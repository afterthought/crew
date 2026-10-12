#!/usr/bin/env python3
"""gather.py: read a host's kits for the bolt plan, in one run per host.

  python3 gather.py '<request>'      or, sent over ssh:  python3 - '<request>' < gather.py

The request is JSON: {"kits": [{"main": <kit's main checkout>, "dir": <the kit's folder>, "bolts": [<bolt>, ...],
"reports": [<a team's verify reports folder, ~ allowed>, ...], "slots": {<team>: <its slots file, ~ allowed>}}],
"sites": <true to also read each worktree's dev server names with devurl, and the host's running portless routes>,
"board": <true to also read each team's slots file and the explorations on the kit's main>}.
The answer, on stdout, is JSON keyed by each kit's main checkout: the changes main holds (open or archived) and the
chores its history holds (each `Chore:` trailer's name), and for each local bolt/* branch, and each bolt asked for,
whether bolt/<bolt> exists, the changes and chores it holds, its worktree, its head and the head's time; each place under
<dir>/places with its branch, its head and the head's time, its change's tasks, whether its planning is complete and the
paths its proposal declares it touches; each chore's place, <dir>/places/chore-<name> on chore/<name>, with its bolt,
head, head's time and how many commits of its own it holds beyond the bolt; each fix branched from a bolt;
each unit's newest verify report in the reports folders, with its path and time; and whether the kit merges through
sluice, by the flag in its main checkout's .config/crew.toml. With sites, each worktree's devurl names and the host's
portless routes; with board, each team's slots, one {slot, kind, name, place} per line of its slots file, and each
folder under openspec/explorations/ on main with the first line of its first .md file. It reads with git, the file
system, devurl and portless and, for a change whose workflow it does not read itself, openspec, and changes nothing.
It needs nothing but python3's standard library, since it is sent to hosts whose crew may be older."""
import datetime, json, os, re, subprocess, sys


def run(args, cwd):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return r.stdout if r.returncode == 0 else None


def changes(main, ref):
    """The OpenSpec changes a branch holds, open or archived (an archived one loses its YYYY-MM-DD- prefix)."""
    out = run(["git", "ls-tree", "-d", "--name-only", ref, "openspec/changes/", "openspec/changes/archive/"], main) or ""
    names = set()
    for line in out.splitlines():
        rest = line[len("openspec/changes/"):]
        if rest == "archive":
            continue
        if rest.startswith("archive/"):
            rest = rest[len("archive/"):]
            if len(rest) > 11 and rest[4] == "-" and rest[7] == "-" and rest[10] == "-":
                rest = rest[11:]
        names.add(rest)
    return sorted(names)


# A chore's name, as a commit's `Chore:` trailer gives it (plan.11).
CHORE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def chores(main, ref):
    """The chores a branch's history holds: the name each commit's `Chore:` trailer gives, as git parses trailers, of
    the commits whose message has a line starting `Chore: `. [] for a branch that is not there."""
    out = run(["git", "log", "--grep=^Chore: ", "--format=%(trailers:key=Chore,valueonly,separator=%x0a)", ref, "--"], main) or ""
    return sorted({l.strip() for l in out.splitlines() if CHORE.match(l.strip())})


def chore_place(path, bolt):
    """A chore's place: its head and the head's time, and how many commits of its own it holds beyond its bolt (ahead):
    its first-parent line with no merges, so the work it took of what it comes after is not counted; None when it
    tracks no bolt or git can't count them."""
    ahead = (run(["git", "rev-list", "--count", "--first-parent", "--no-merges", f"refs/heads/bolt/{bolt}..HEAD"], path) or "").strip() if bolt else ""
    return {"path": path, "head": (run(["git", "rev-parse", "HEAD"], path) or "").strip() or None, "head_at": head_at(path, "HEAD"),
            "ahead": int(ahead) if ahead.isdigit() else None}


def worktrees(main):
    """The checkout's worktrees: each one's path, its branch when it is on one, and whether it is locked."""
    out, cur = [], {}
    for line in (run(["git", "worktree", "list", "--porcelain"], main) or "").splitlines() + [""]:
        if not line:
            if cur:
                out.append(cur)
            cur = {}
        elif line.startswith("worktree "):
            cur["path"] = os.path.realpath(line[9:])
        elif line.startswith("branch refs/heads/"):
            cur["branch"] = line[18:]
        elif line == "locked" or line.startswith("locked "):
            cur["locked"] = True
    return out


def upstreams(main):
    out = {}
    for line in (run(["git", "for-each-ref", "--format=%(refname:short) %(upstream:short)", "refs/heads/unit/", "refs/heads/fix/",
                      "refs/heads/chore/"], main) or "").splitlines():
        b, _, up = line.partition(" ")
        out[b] = up
    return out


def fix_merged(main, branch, bolt):
    """Whether a fix has merged into its bolt: the bolt holds the fix's tip, and the fix has moved since it was made
    (its reflog's first entry)."""
    if not bolt:
        return False
    born = (run(["git", "reflog", "show", "--format=%H", branch], main) or "").split()
    tip = (run(["git", "rev-parse", branch], main) or "").strip()
    return bool(born) and tip != born[-1] and subprocess.run(
        ["git", "merge-base", "--is-ancestor", branch, f"bolt/{bolt}"], cwd=main).returncode == 0


def sluice(main):
    """Whether a kit opts into sluice, by `sluice = true` in its main checkout's .config/crew.toml: (True or False,
    None), False when it has no such file; or (None, why) when crew can't read it."""
    path = os.path.join(main, ".config", "crew.toml")
    if not os.path.exists(path):
        return False, None
    try:
        import tomllib
    except ImportError:
        return None, f"python3 on this host has no tomllib to read {path}"
    try:
        with open(path, "rb") as f:
            v = tomllib.load(f).get("sluice", False)
    except (OSError, ValueError) as e:
        return None, f"{path} can't be read: {e}"
    if not isinstance(v, bool):
        return None, f"{path}: 'sluice' is true or false, not {json.dumps(v)}"
    return v, None


def own_head(cwd, branch, bolt):
    """The newest commit of a chore's own on its branch beyond its bolt, its first-parent line with no merges, as
    (short sha, committer time in ISO 8601); (None, None) when it has none."""
    out = (run(["git", "log", "-1", "--first-parent", "--no-merges", "--format=%h %cI", f"refs/heads/bolt/{bolt}..refs/heads/{branch}"], cwd)
           or "").split()
    return (out[0], out[1]) if len(out) == 2 else (None, None)


def head_at(cwd, ref):
    """The committer time of a ref, as ISO 8601, or None."""
    return (run(["git", "log", "-1", "--format=%cI", ref], cwd) or "").strip() or None


REPORT = re.compile(r"^verify-(.+)-(\d{8}-\d{4})\.md$")
# Ops's proof of a bolt, saved once, whole, in the same folder.
PROOF = re.compile(r"^proof-(.+)-(\d{8}-\d{4})\.md$")


def reports(folders):
    """Each unit's newest verify report across the folders: {unit: {"path": its absolute path, "at": its file's
    time, in UTC}}. A folder that isn't there gives nothing."""
    out = {}
    for d in folders:
        d = os.path.abspath(os.path.expanduser(d))
        try:
            names = os.listdir(d)
        except OSError:
            continue
        for n in names:
            m = REPORT.match(n)
            if not m:
                continue
            f = os.path.join(d, n)
            try:
                t = os.path.getmtime(f)
            except OSError:
                continue
            if m.group(1) not in out or t > out[m.group(1)][0]:
                out[m.group(1)] = (t, f)
    return {u: {"path": f, "at": datetime.datetime.fromtimestamp(t, datetime.timezone.utc).isoformat()} for u, (t, f) in out.items()}


# A change's tasks and whether its planning is complete, read from its files by openspec 1.14.1's own rules for its
# spec-driven schema (dist/utils/task-progress.js, dist/core/artifact-graph, dist/utils/change-metadata.js), so
# neither needs openspec started. tests/t-stage-facts.sh holds this reading to openspec's on the same worktrees.
# JavaScript's \s, written out, since Python's differs; JavaScript's `.` stops at a line or paragraph separator.
SPACE = "\t\n\v\f\r \u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"
WS = f"[{SPACE}]"
# openspec's TASK_LINE_PATTERN: a list item (-, *, + or 1. / 1)) holding a checkbox of at most one marker; only x or X
# is done. Not anchored at the end, so a CRLF line still matches.
TASK = re.compile(rf"^{WS}*(?:[-*+]|[0-9]{{1,9}}[.)]){WS}*\[(?:{WS}*([^\]{SPACE}]?){WS}*\](?![(\[])|{WS}+\]){WS}*([^\n\r\u2028\u2029]*)")
# The spec-driven schema's outputs: an artifact is complete when a file it generates exists.
PLANNED = ("proposal.md", "design.md", "tasks.md")


def tasks_of(text):
    """Each task of a tasks file, in order, as (done, description), as openspec parses them."""
    out = []
    for line in text.split("\n"):
        m = TASK.match(line)
        if m:
            out.append(((m.group(1) or "").lower() == "x", re.sub(rf"^{WS}+|{WS}+$", "", m.group(2))))
    return out


def yaml_lines(path):
    """A small YAML file's top-level lines as [(key, value, indented lines under it)], or None when crew does not read
    it: a line that is not a plain `key: value` at the left edge or a key's indented continuation, or a key twice.
    [] when the file is not there."""
    try:
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
    except FileNotFoundError:
        return []
    except (OSError, UnicodeDecodeError):
        return None
    out = []
    for line in text.split("\n"):
        line = line[:-1] if line.endswith("\r") else line
        if not line.strip() or line.startswith("#"):
            continue
        if line.startswith(" ") and out:
            out[-1][2].append(line)
            continue
        m = re.match(r"^([a-z_]+):(?:[ ]+(\S.*?))?[ ]*$", line)
        if not m or any(k == m.group(1) for k, _, _ in out):
            return None
        out.append((m.group(1), m.group(2) or "", []))
    return out


def data_dir():
    """openspec's global data folder: $XDG_DATA_HOME/openspec when that is set, else ~/.local/share/openspec
    (getGlobalDataDir, on every system but Windows)."""
    base = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "openspec")


def planned(change, root):
    """Whether a change's planning is complete, as `openspec status` would say it in the project at root: True or
    False when the change uses openspec's own spec-driven schema and crew reads all its metadata, else None, meaning
    read it through openspec. The schema is the change's .openspec.yaml's, else the project's openspec/config.yaml's
    (config.yml's when there is no .yaml), else spec-driven; a spec-driven of the project's or the user's own, any
    other schema, or a line crew does not read hands the change to openspec. .openspec.yaml is read when it holds
    only schema, created and skip_specs; config.yaml when its schema is plain and its other keys are context, rules
    and operations, which openspec reads for its instructions only."""
    if os.path.islink(change):
        return None
    metadata = os.path.join(change, ".openspec.yaml")
    meta = yaml_lines(metadata)
    config = os.path.join(root, "openspec", "config.yaml")
    conf = yaml_lines(config if os.path.exists(config) else os.path.join(root, "openspec", "config.yml"))
    if meta is None or conf is None:
        return None
    if os.path.lexists(metadata) and not any(k == "schema" for k, _, _ in meta):
        return None  # openspec refuses metadata with no schema
    for k, v, more in meta:
        if more or not (k == "schema" and v == "spec-driven" or k == "created" and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v)
                        or k == "skip_specs" and v in ("true", "false")):
            return None
    for k, v, more in conf:
        if k == "schema" and (more or v != "spec-driven") or k not in ("schema", "context", "rules", "operations"):
            return None
    if any(os.path.exists(os.path.join(d, "spec-driven")) for d in (os.path.join(root, "openspec", "schemas"), os.path.join(data_dir(), "schemas"))):
        return None
    if not os.path.isdir(change):
        return False
    if not all(os.path.isfile(os.path.join(change, f)) for f in PLANNED):
        return False
    return ("skip_specs", "true", []) in meta or specs_written(os.path.join(change, "specs"))


def specs_written(specs):
    """Whether specs/**/*.md matches a file, as openspec's glob does: a regular file, symbolic links followed, no
    part of its path below specs/ starting with a dot."""
    for d, dirs, files in os.walk(specs, followlinks=True):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        if any(f.endswith(".md") and not f.startswith(".") and os.path.isfile(os.path.join(d, f)) for f in files):
            return True
    return False


def change_tasks(change):
    """A change's tasks, as tasks_of reads its tasks.md; [] when there is none to read."""
    try:
        with open(os.path.join(change, "tasks.md"), encoding="utf-8", errors="replace", newline="") as f:
            return tasks_of(f.read())
    except OSError:
        return []


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def touches(text):
    """What a proposal declares it touches: the lines of the one fenced block under its `## Touches` heading, each a
    path or glob relative to the kit's root ({"entries": [...]}), or what is missing ({"missing": ...}): the heading,
    the block before the next heading, or any line in it."""
    if text is None:
        return {"missing": "it has no proposal.md"}
    lines = text.split("\n")
    at = next((i for i, l in enumerate(lines) if re.fullmatch(r"##[ \t]+Touches[ \t]*\r?", l)), None)
    if at is None:
        return {"missing": "its proposal.md has no `## Touches` heading"}
    for i in range(at + 1, len(lines)):
        if re.match(r"^#{1,2}[ \t]", lines[i]):
            break
        m = FENCE.match(lines[i])
        if m:
            entries = []
            for l in lines[i + 1:]:
                if l.strip().startswith(m.group(1)) and not l.strip().strip(m.group(1)[0]):
                    break
                if l.strip():
                    entries.append(l.strip())
            return {"entries": entries} if entries else {"missing": "the block under its `## Touches` heading is empty"}
    return {"missing": "its `## Touches` heading holds no fenced block"}


def place(path, unit):
    """A unit's place: its head and the head's time, its change's tasks, whether its planning is complete, the open
    tasks, and what its proposal declares it touches. The tasks and the planning are read from the change's files, or
    through openspec when planned() hands the change to it."""
    info = {"path": path, "head": (run(["git", "rev-parse", "HEAD"], path) or "").strip() or None,
            "head_at": head_at(path, "HEAD"), "tasks": None, "planning": False, "open": []}
    change = os.path.join(path, "openspec", "changes", unit)
    try:
        with open(os.path.join(change, "proposal.md"), encoding="utf-8", errors="replace", newline="") as f:
            info["touches"] = touches(f.read())
    except OSError:
        info["touches"] = touches(None)
    tasks = change_tasks(change)
    info["open"] = [d for done, d in tasks if not done]
    planning = planned(change, path)
    if planning is not None:
        info["planning"] = planning
        if os.path.isdir(change):  # openspec lists a change folder, not a link to one
            info["tasks"] = [sum(done for done, _ in tasks), len(tasks)]
    else:
        listed = run(["openspec", "list", "--json"], path)
        if listed:
            for c in json.loads(listed).get("changes", []):
                if c.get("name") == unit:
                    info["tasks"] = [c.get("completedTasks", 0), c.get("totalTasks", 0)]
        status = run(["openspec", "status", "--change", unit, "--json"], path)
        if status:
            info["planning"] = bool(json.loads(status).get("isPlanningComplete"))
    return info


def devurl(path):
    """The worktree's names as swancloud's devurl gives them: here (this host's local name) and tailnet (its
    dev.swancloud.net name, None when the host does not publish)."""
    out = run(["devurl"], path)
    if out is None:
        return {"here": None, "tailnet": None, "error": "devurl did not answer"}
    names = {}
    for line in out.splitlines():
        key, _, rest = line.strip().partition(" ")
        rest = rest.strip()
        names[key] = rest if rest.startswith("https://") else None
    return {"here": names.get("here"), "tailnet": names.get("tailnet")}


def routes():
    """The host's running dev servers, from portless's active routes: each URL and the name it serves."""
    out, found = run(["portless", "list"], None), []
    for line in (out or "").splitlines():
        m = re.match(r"\s*(https?://(\S+?))(:\d+)?\s+->\s+", line)
        if m:
            host = m.group(2)
            name = host.rsplit(".", 1)[0] if host.rsplit(".", 1)[-1] in ("local", "localhost") else host
            found.append({"url": m.group(1) + (m.group(3) or ""), "name": name})
    return found if out is not None else None


def slots(files):
    """Each team's slots, from its slots file: {team: [{slot, kind, name, place}]}, one per non-blank line of four
    fields; a file that isn't there gives [], and a line of another shape is skipped."""
    out = {}
    for team, path in files.items():
        try:
            with open(os.path.expanduser(path), encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except OSError:
            lines = []
        out[team] = [dict(zip(("slot", "kind", "name", "place"), l.split())) for l in lines if len(l.split()) == 4]
    return out


def explorations(main):
    """Each folder under openspec/explorations/ on main, in name order, with the first non-blank line of its first .md
    file, its leading "> " dropped; None when it has no .md file or that line can't be read."""
    out = []
    for path in (run(["git", "ls-tree", "-d", "--name-only", "main", "openspec/explorations/"], main) or "").splitlines():
        name = path.rstrip("/").rsplit("/", 1)[-1]
        files = (run(["git", "ls-tree", "--name-only", "main", f"openspec/explorations/{name}/"], main) or "").splitlines()
        md = next((f for f in files if f.endswith(".md")), None)
        text = run(["git", "show", f"main:{md}"], main) if md else None
        first = next((l.strip() for l in (text or "").splitlines() if l.strip()), None)
        out.append({"name": name, "first": first[2:] if first and first.startswith("> ") else first})
    return out


def kit(req, sites=False, running=None, board=False):
    main, kdir = req["main"], os.path.realpath(req["dir"])
    if not os.path.isdir(main):
        return {"ok": False, "error": f"no checkout at {main}"}
    trees = worktrees(main)
    at = {t["path"]: t.get("branch") for t in trees}
    ups = upstreams(main)
    out = {"ok": True, "main": changes(main, "main"), "chores": chores(main, "refs/heads/main"), "bolts": {}, "places": {},
           "chore_places": {}, "fixes": [], "reports": reports(req.get("reports", []))}
    out["sluice"], out["sluice_error"] = sluice(main)
    # Every local bolt branch, so one answer serves every step of a command, whichever bolt it asks about; a bolt
    # asked for, or tracked by a place, that has no branch is marked missing.
    have = [r[len("refs/heads/bolt/"):] for r in (run(["git", "for-each-ref", "--format=%(refname)", "refs/heads/bolt/"], main) or "").split()]
    tracked = [u[5:] for u in ups.values() if u.startswith("bolt/")]
    for b in sorted(set(have + req.get("bolts", []) + tracked)):
        exists = b in have
        wt = os.path.join(kdir, "bolts", b)
        out["bolts"][b] = {"exists": exists, "changes": changes(main, f"bolt/{b}") if exists else [],
                           "chores": chores(main, f"refs/heads/bolt/{b}") if exists else [],
                           "worktree": wt if at.get(wt) == f"bolt/{b}" else None,
                           "head": (run(["git", "rev-parse", "--verify", "-q", f"refs/heads/bolt/{b}^{{commit}}"], main) or "").strip() or None if exists else None,
                           "head_at": head_at(main, f"refs/heads/bolt/{b}") if exists else None}
    places = os.path.join(kdir, "places")
    for path, branch in at.items():
        if os.path.dirname(path) != places or not branch:
            continue
        if branch.startswith("unit/"):
            unit = branch[5:]
            bolt = ups.get(branch, "")[5:] if ups.get(branch, "").startswith("bolt/") else None
            out["places"][unit] = dict(place(path, unit), branch=branch, bolt=bolt)
        elif branch.startswith("chore/") and os.path.basename(path) == f"chore-{branch[6:]}":
            bolt = ups.get(branch, "")[5:] if ups.get(branch, "").startswith("bolt/") else None
            out["chore_places"][branch[6:]] = dict(chore_place(path, bolt), branch=branch, bolt=bolt)
        elif branch.startswith("fix/"):
            bolt = ups.get(branch, "")[5:] if ups.get(branch, "").startswith("bolt/") else None
            out["fixes"].append({"fix": branch, "path": path, "bolt": bolt, "merged": fix_merged(main, branch, bolt)})
    if sites:
        out["sites"] = {path: devurl(path) for path, branch in at.items()
                        if os.path.dirname(path) in (places, os.path.join(kdir, "bolts")) and branch}
        out["routes"] = running
    if board:
        out["slots"] = slots(req.get("slots", {}))
        out["explorations"] = explorations(main)
    return out


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    running = routes() if request.get("sites") else None
    print(json.dumps({k["main"]: kit(k, request.get("sites"), running, request.get("board")) for k in request["kits"]}))
