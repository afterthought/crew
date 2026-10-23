#!/usr/bin/env python3
"""gather.py: read a host's kits for the bolt plan, in one run per host.

  python3 gather.py '<request>'      or, sent over ssh:  python3 - '<request>' < gather.py

The request is JSON: {"kits": [{"main": <kit's main checkout>, "dir": <the kit's folder>, "bolts": [<bolt>, ...],
"slots": {<team>: <its slots file, ~ allowed>}}],
"sites": <true to also read each worktree's dev server names with devurl, and the host's running portless routes>,
"board": <true to also read each team's slots file and the explorations on the kit's main>,
"fetch": <true to fetch each kit's GitHub, its origin, before reading it>}.
The answer, on stdout, is JSON keyed by each kit's main checkout: the changes main holds (open or archived) and the
chores its history holds (each `Chore:` trailer's name), and for each local bolt/* branch, and each bolt asked for,
read where the bolt lives (bolt_read, at: GitHub's origin/bolt/<bolt> for a bolt on GitHub, else the host's bolt/<bolt>),
whether it exists, the changes and chores it holds, those it holds archived, the tasks of each it holds open
that main does not hold, its worktree, its head and the head's time; each place under
<dir>/places with its branch, its head and the head's time, its change's tasks, whether its planning is complete and the
paths its proposal declares it touches, read from the change archived there once its merge has archived it; each chore's place, <dir>/places/chore-<name> on chore/<name>, with its bolt,
head, head's time and how many commits of its own it holds beyond the bolt; each fix's place with its branch's facts
(fix_facts), and, as fix_branches, the same facts of each fix branch no worktree holds, its place gone; the kit's
policy, its main's .config/sluice.toml as text; and each bolt's verdict, the Sluice-Result trailer on its head when
sluice landed it. With sites, each worktree's devurl names and the host's
portless routes; with board, each team's slots, one {slot, kind, name, place} per line of its slots file, and each
folder under openspec/explorations/ on main with the first line of its first .md file. It reads with git, the file
system, devurl and portless and, for a change whose workflow it does not read itself, openspec, and changes nothing.
It needs nothing but python3's standard library, since it is sent to hosts whose crew may be older."""
import fnmatch, json, os, re, subprocess, sys, tomllib


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


# The prefix openspec archive gives a change's folder: the day it was archived.
DATED = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}-")


def archived(main, ref):
    """The OpenSpec changes a branch holds archived, by name, without the archive's YYYY-MM-DD- prefix: what a unit's
    merge has delivered once the bolt holds its change so (teams.17)."""
    out = run(["git", "ls-tree", "-d", "--name-only", ref, "openspec/changes/archive/"], main) or ""
    return sorted({n[11:] for n in (l[len("openspec/changes/archive/"):] for l in out.splitlines())
                   if len(n) > 11 and DATED.fullmatch(n[:11])})


def opened(main, ref):
    """The OpenSpec changes a branch holds open, by name: each folder directly under openspec/changes/ but the archive."""
    out = run(["git", "ls-tree", "-d", "--name-only", ref, "openspec/changes/"], main) or ""
    return sorted(n for n in (l[len("openspec/changes/"):] for l in out.splitlines()) if n and n != "archive")


def carried(main, ref, held):
    """The tasks, [done, total], of each change a bolt holds open that main does not hold (held, main's changes): a
    unit's change carried there open inside another unit's merge, since a unit's own merge archives it (teams.17)."""
    out = {}
    for name in opened(main, ref):
        if name not in held:
            tasks = tasks_of(run(["git", "show", f"{ref}:openspec/changes/{name}/tasks.md"], main) or "")
            out[name] = [sum(done for done, _ in tasks), len(tasks)]
    return out


# A chore's name, as a commit's `Chore:` trailer gives it (plan.11).
CHORE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def chores(main, ref):
    """The chores a branch's history holds: the name each commit's `Chore:` trailer gives, as git parses trailers, of
    the commits whose message has a line starting `Chore: `. [] for a branch that is not there."""
    out = run(["git", "log", "--grep=^Chore: ", "--format=%(trailers:key=Chore,valueonly,separator=%x0a)", ref, "--"], main) or ""
    return sorted({l.strip() for l in out.splitlines() if CHORE.match(l.strip())})


def chore_place(path, bolt, ref):
    """A chore's place: its head and the head's time, and how many commits of its own it holds beyond its bolt (ahead),
    read at the ref the bolt is read at (ref, bolt_at): its first-parent line with no merges, so the work it took of
    what it comes after is not counted; None when it tracks no bolt crew can read or git can't count them."""
    ahead = (run(["git", "rev-list", "--count", "--first-parent", "--no-merges", f"{ref}..HEAD"], path) or "").strip() if bolt and ref else ""
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


def fixes_dropped(main):
    """The fix branches of a kit checkout their conductor dropped, by the mark crew fix --drop sets in the kit's git
    config, branch.<fix>.crew dropped (record 0028)."""
    out = run(["git", "config", "--get-regexp", r"^branch\.fix/.*\.crew$"], main) or ""
    return {k[len("branch."):-len(".crew")] for k, _, v in (l.partition(" ") for l in out.splitlines()) if v == "dropped"}


def bolt_ref(up):
    """The bolt a branch's upstream names, and the ref it names, from its short form as for-each-ref's
    %(upstream:short) prints it, which still names an upstream that is gone: (bolt, ref) for bolt/<bolt>, the host's
    refs/heads/bolt/<bolt>, or for origin/bolt/<bolt>, GitHub's refs/remotes/origin/bolt/<bolt> as this host last
    fetched it (plan.19); (None, None) for any other."""
    for short, ref in (("bolt/", "refs/heads/bolt/"), ("origin/bolt/", "refs/remotes/origin/bolt/")):
        if up.startswith(short) and up[len(short):]:
            return up[len(short):], ref + up[len(short):]
    return None, None


def bolt_of(up):
    """The bolt a place's branch was cut from, from its upstream (plan.19, bolt_ref): bolt/<bolt>, a bolt made before
    gives went through sluice, or origin/bolt/<bolt>, a bolt on GitHub; None for any other upstream, or none."""
    return bolt_ref(up or "")[0]


# A kit's policy, where sluice reads how each branch is gated and routed (kit.DECLARATION).
POLICY = ".config/sluice.toml"


def branch_table(branches, branch):
    """The [branches."<pattern>"] table of a policy's branches whose pattern matches the branch, the most specific
    first, as sluice matches it; None when none does."""
    matching = sorted((p for p in (branches if isinstance(branches, dict) else {}) if fnmatch.fnmatchcase(branch, p)),
                      key=lambda p: (p.count("*"), -len(p)))
    return branches[matching[0]] if matching and isinstance(branches[matching[0]], dict) else None


def policy_remote(text, branch):
    """The remote a policy's text names for a branch, as sluice routes it (plan.19): the `remote` of the matching
    [branches."<pattern>"] table (branch_table) when it is a non-empty string; None for no policy (text None), no
    matching table or no remote, which sluice reads as a branch kept in the host's own refs. Raises ValueError
    (tomllib's TOMLDecodeError) on text that is not TOML."""
    if text is None:
        return None
    table = branch_table(tomllib.loads(text).get("branches", {}), branch)
    remote = table.get("remote") if table else None
    return remote if isinstance(remote, str) and remote else None


def bolt_at(bolt, tracked, local, remote_at_tracked):
    """The ref a bolt is read at (plan.19): GitHub's copy, refs/remotes/origin/bolt/<bolt> as this host last fetched
    it, when the host holds it (tracked) and the policy in it names a remote for the bolt's branch (remote_at_tracked);
    else the host's own refs/heads/bolt/<bolt> when it is there (local), the bolt itself for a bolt kept on its host or
    one this host has not fetched; None when the host has neither, the bolt missing. The host's copy of a bolt on
    GitHub is sluice's, and nothing of the bolt is read from it."""
    if tracked and remote_at_tracked is not None:
        return f"refs/remotes/origin/bolt/{bolt}"
    return f"refs/heads/bolt/{bolt}" if local else None


def bolt_read(main, bolt, tracked=None, local=None):
    """Where a bolt is read in a kit's main checkout (bolt_at), from what the host holds of it, asked of git unless the
    caller has listed it (tracked, local): (ref, None), (None, None) when the host has no copy of it, or (None, why)
    when the policy at GitHub's copy is not TOML, which reads nothing from the host's copy (read.1)."""
    def there(ref):
        return run(["git", "rev-parse", "--verify", "-q", f"{ref}^{{commit}}"], main) is not None
    github = f"refs/remotes/origin/bolt/{bolt}"
    tracked = there(github) if tracked is None else tracked
    remote = None
    if tracked:
        try:
            remote = policy_remote(run(["git", "show", f"{github}:{POLICY}"], main), f"bolt/{bolt}")
        except ValueError as e:
            return None, f"{POLICY} at origin/bolt/{bolt} is not TOML, so crew can't read bolt {bolt}: {e}"
    return bolt_at(bolt, tracked, there(f"refs/heads/bolt/{bolt}") if local is None else local, remote), None


def short(ref):
    """A ref's short form, as git takes it and a person reads it: origin/bolt/<bolt> or bolt/<bolt>; None for None."""
    for long in ("refs/remotes/", "refs/heads/"):
        if ref and ref.startswith(long):
            return ref[len(long):]
    return ref


def holds(main, ref, branch):
    """Whether ref holds a branch's tip."""
    return subprocess.run(["git", "merge-base", "--is-ancestor", f"refs/heads/{branch}", ref], cwd=main, capture_output=True).returncode == 0


def moved(main, branch):
    """Whether a branch has moved since it was made: its tip is not its reflog's first entry. False when its reflog is
    gone."""
    born = (run(["git", "reflog", "show", "--format=%H", f"refs/heads/{branch}"], main) or "").split()
    tip = (run(["git", "rev-parse", f"refs/heads/{branch}"], main) or "").strip()
    return bool(born) and tip != born[-1]


def fix_merged(main, branch, bolt, ref=None):
    """Whether a fix has merged into its bolt: the bolt, at the ref it is read at (ref, else bolt_read), holds the fix's
    tip, and the fix has moved since it was made (its reflog's first entry)."""
    ref = ref or (bolt_read(main, bolt)[0] if bolt else None)
    return bool(ref) and holds(main, ref, branch) and moved(main, branch)


def fix_facts(main, branches, ups, now, at=None):
    """What a fix's stage is read from, of each fix branch named (branches), by branch, with its upstream from ups
    (upstreams): its bolt (bolt_ref), whether it has merged into it (merged, as fix_merged reads it), at the ref its
    bolt is read at when at names it ({bolt: ref}, bolt_at; None for a bolt crew can't read), else at the ref it tracks, whether the kit's main now (now, now_ref) holds its tip (on_main), and whether it has moved since it was made
    (moved; None when neither main nor its bolt holds its tip, so it decides nothing). Read with as few processes as
    git allows: one listing of the fix branches main holds and one of the bolt refs; a branch's bolt is asked only when
    its ref exists, and its reflog only when main or its bolt holds its tip."""
    if not branches:
        return {}
    landed = {r[len("refs/heads/"):] for r in (run(["git", "for-each-ref", f"--merged={now}", "--format=%(refname)", "refs/heads/fix/"], main) or "").split()}
    refs = set((run(["git", "for-each-ref", "--format=%(refname)", "refs/heads/bolt/", "refs/remotes/origin/bolt/"], main) or "").split())
    out = {}
    for b in branches:
        bolt, ref = bolt_ref(ups.get(b, ""))
        ref = at[bolt] if at is not None and bolt in at else ref
        in_bolt = ref in refs and holds(main, ref, b)
        went = moved(main, b) if in_bolt or b in landed else None
        out[b] = {"bolt": bolt, "merged": in_bolt and went, "on_main": b in landed, "moved": went}
    return out


def own_head(cwd, branch, bolt):
    """The newest commit of a chore's own on its branch beyond its bolt, read at the ref the bolt is read at
    (bolt_read), its first-parent line with no merges, as (short sha, committer time in ISO 8601); (None, None) when it
    has none or the bolt can't be read."""
    ref = bolt_read(cwd, bolt)[0]
    out = (run(["git", "log", "-1", "--first-parent", "--no-merges", "--format=%h %cI", f"{ref}..refs/heads/{branch}"], cwd)
           or "").split() if ref else []
    return (out[0], out[1]) if len(out) == 2 else (None, None)


def head_at(cwd, ref):
    """The committer time of a ref, as ISO 8601, or None."""
    return (run(["git", "log", "-1", "--format=%cI", ref], cwd) or "").strip() or None


REPORT = re.compile(r"^verify-(.+)-(\d{8}-\d{4})\.md$")


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
    through openspec when planned() hands the change to it. A change its merge archived in the place, as a unit's merge
    stage does first (teams.17), is read from the archive, its planning complete, and the place says it is archived."""
    info = {"path": path, "head": (run(["git", "rev-parse", "HEAD"], path) or "").strip() or None,
            "head_at": head_at(path, "HEAD"), "tasks": None, "planning": False, "open": [], "archived": False}
    change, archive = os.path.join(path, "openspec", "changes", unit), os.path.join(path, "openspec", "changes", "archive")
    if not os.path.isdir(change) and os.path.isdir(archive):
        gone = sorted(d for d in os.listdir(archive) if d[11:] == unit and DATED.fullmatch(d[:11]))
        if gone:
            change, info["archived"] = os.path.join(archive, gone[-1]), True
    try:
        with open(os.path.join(change, "proposal.md"), encoding="utf-8", errors="replace", newline="") as f:
            info["touches"] = touches(f.read())
    except OSError:
        info["touches"] = touches(None)
    tasks = change_tasks(change)
    info["open"] = [d for done, d in tasks if not done]
    if info["archived"]:
        info["tasks"], info["planning"] = [sum(done for done, _ in tasks), len(tasks)], True
        return info
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


def has_origin(main):
    """Whether a kit's main checkout has an origin remote, its GitHub."""
    return run(["git", "remote", "get-url", "origin"], main) is not None


def ran(args, cwd):
    """A command's exit and what it said, (exit, stdout, stderr); (None, "", why) when it can't be started."""
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    except (FileNotFoundError, NotADirectoryError) as e:
        return None, "", str(e)
    return r.returncode, r.stdout, r.stderr


def fetched(main):
    """A kit's GitHub fetched into its main checkout, as a read a decision of the moment rests on fetches it (plan.18,
    plan.19), `git fetch -q origin`: None once it fetched, or for a kit with no origin remote, which has no GitHub;
    git's words when the fetch failed."""
    if not has_origin(main):
        return None
    code, out, err = ran(["git", "fetch", "-q", "origin"], main)
    return None if code == 0 else (err or out).strip() or f"git fetch exited {code}"


def now_ref(origin):
    """The ref a kit's main is read at now (plan.18), from whether it has an origin remote: GitHub's,
    refs/remotes/origin/main as this host last fetched it, for a kit with one, since sluice lands there and the host's
    own main lags it on every host that did not land; its own main for a kit with none, which has no GitHub to lag. A
    read of every kit fetches nothing: sluice's push moves origin/main on the host that landed, and the fleet's timer
    fetches on every other within minutes; a command that must have GitHub's main at once fetches it (plan.MAINS)."""
    return "refs/remotes/origin/main" if origin else "refs/heads/main"


def explorations(main, ref="main"):
    """Each folder under openspec/explorations/ on main (ref), in name order, with the first non-blank line of its first
    .md file, its leading "> " dropped; None when it has no .md file or that line can't be read."""
    out = []
    for path in (run(["git", "ls-tree", "-d", "--name-only", ref, "openspec/explorations/"], main) or "").splitlines():
        name = path.rstrip("/").rsplit("/", 1)[-1]
        files = (run(["git", "ls-tree", "--name-only", ref, f"openspec/explorations/{name}/"], main) or "").splitlines()
        md = next((f for f in files if f.endswith(".md")), None)
        text = run(["git", "show", f"{ref}:{md}"], main) if md else None
        first = next((l.strip() for l in (text or "").splitlines() if l.strip()), None)
        out.append({"name": name, "first": first[2:] if first and first.startswith("> ") else first})
    return out


def kit(req, sites=False, running=None, board=False, fetch=False):
    main, kdir = req["main"], os.path.realpath(req["dir"])
    if not os.path.isdir(main):
        return {"ok": False, "error": f"no checkout at {main}"}
    # A read a decision of the moment rests on fetches GitHub first (fetch, fetched); every other reads it as this host
    # last fetched it.
    why = fetched(main) if fetch else None
    if why:
        return {"ok": False, "error": f"cannot fetch {main} from GitHub: {why}"}
    trees = worktrees(main)
    at = {t["path"]: t.get("branch") for t in trees}
    ups = upstreams(main)
    # The kit's main now (now_ref): which changes and chores have landed, and the explorations, are read there.
    now = now_ref(has_origin(main))
    if run(["git", "rev-parse", "--verify", "-q", f"{now}^{{commit}}"], main) is None:
        return {"ok": False, "error": f"{main} has no {now[len('refs/remotes/'):] if now.startswith('refs/remotes/') else 'branch main'} to read"}
    out = {"ok": True, "main": changes(main, now), "chores": chores(main, now), "bolts": {}, "places": {},
           "chore_places": {}, "fixes": []}
    # The kit's policy, as its main holds it: what gates its bolt branches, which crew reads before it gives a bolt.
    out["policy"] = run(["git", "show", f"{now}:.config/sluice.toml"], main)
    # Every local bolt branch, so one answer serves every step of a command, whichever bolt it asks about; a bolt
    # asked for, or tracked by a place, that has no branch is marked missing. Each is read where it lives (bolt_read):
    # GitHub's copy as this host last fetched it for a bolt on GitHub, never the host's copy, which is sluice's.
    refs = (run(["git", "for-each-ref", "--format=%(refname)", "refs/heads/bolt/", "refs/remotes/origin/bolt/"], main) or "").split()
    have = [r[len("refs/heads/bolt/"):] for r in refs if r.startswith("refs/heads/bolt/")]
    github = {r[len("refs/remotes/origin/bolt/"):] for r in refs if r.startswith("refs/remotes/origin/bolt/")}
    tracked = [b for b in map(bolt_of, ups.values()) if b]
    reads = {}
    for b in sorted(set(have + req.get("bolts", []) + tracked)):
        ref, why = bolt_read(main, b, b in github, b in have)
        reads[b] = ref
        wt = os.path.join(kdir, "bolts", b)
        out["bolts"][b] = {"exists": ref is not None, "at": short(ref), "changes": changes(main, ref) if ref else [],
                           "archived": archived(main, ref) if ref else [],
                           "open": carried(main, ref, out["main"]) if ref else {},
                           "chores": chores(main, ref) if ref else [],
                           "worktree": wt if at.get(wt) == f"bolt/{b}" else None,
                           "head": (run(["git", "rev-parse", "--verify", "-q", f"{ref}^{{commit}}"], main) or "").strip() or None if ref else None,
                           "head_at": head_at(main, ref) if ref else None,
                           # sluice's verdict on the bolt's last landing: its head's trailer, empty when it is no landing.
                           "verdict": (run(["git", "log", "-1", "--format=%(trailers:key=Sluice-Result,valueonly)",
                                            ref], main) or "").strip() if ref else None,
                           **({"error": why} if why else {})}
    places, dropped = os.path.join(kdir, "places"), None
    for path, branch in at.items():
        if os.path.dirname(path) != places or not branch:
            continue
        if branch.startswith("unit/"):
            unit = branch[5:]
            bolt = bolt_of(ups.get(branch))
            out["places"][unit] = dict(place(path, unit), branch=branch, bolt=bolt)
        elif branch.startswith("chore/") and os.path.basename(path) == f"chore-{branch[6:]}":
            bolt = bolt_of(ups.get(branch))
            out["chore_places"][branch[6:]] = dict(chore_place(path, bolt, reads.get(bolt)), branch=branch, bolt=bolt)
        elif branch.startswith("fix/"):
            dropped = fixes_dropped(main) if dropped is None else dropped  # read once, and only for a kit with a fix's place
            out["fixes"].append(dict(fix=branch, path=path, dropped=branch in dropped))
    # Each fix branch's facts, read together: a fix's place's, and, as fix_branches, those of each fix branch no
    # worktree holds, whose place is gone, so a slot holding one and the tidy still read it (teams.1, teams.3).
    worked = {b for b in at.values() if b}
    facts = fix_facts(main, sorted({b for b in ups if b.startswith("fix/") and b not in worked} | {f["fix"] for f in out["fixes"]}), ups, now, reads)
    for f in out["fixes"]:
        f.update(facts[f["fix"]])
    out["fix_branches"] = {b: f for b, f in facts.items() if b not in worked}
    if sites:
        out["sites"] = {path: devurl(path) for path, branch in at.items()
                        if os.path.dirname(path) in (places, os.path.join(kdir, "bolts")) and branch}
        out["routes"] = running
    if board:
        out["slots"] = slots(req.get("slots", {}))
        out["explorations"] = explorations(main, now)
    return out


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    running = routes() if request.get("sites") else None
    print(json.dumps({k["main"]: kit(k, request.get("sites"), running, request.get("board"), request.get("fetch")) for k in request["kits"]}))
