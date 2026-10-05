#!/usr/bin/env python3
"""gather.py: read a host's kits for the bolt plan, in one run per host.

  python3 gather.py '<request>'      or, sent over ssh:  python3 - '<request>' < gather.py

The request is JSON: {"kits": [{"main": <kit's main checkout>, "dir": <the kit's folder>, "bolts": [<bolt>, ...]}],
"sites": <true to also read each worktree's dev server names with devurl, and the host's running portless routes>}.
The answer, on stdout, is JSON keyed by each kit's main checkout: the changes main holds (open or archived), and
for each bolt whether bolt/<bolt> exists, the changes it holds and its worktree; each place under <dir>/places
with its branch and head, its change's tasks, whether its planning is complete and whether it has a review since
the bolt; and each fix branched from a bolt. It reads with git and openspec only, and changes nothing. It needs
nothing but python3's standard library, since it is sent to hosts whose crew may be older."""
import json, os, re, subprocess, sys


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


def worktrees(main):
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
    return out


def upstreams(main):
    out = {}
    for line in (run(["git", "for-each-ref", "--format=%(refname:short) %(upstream:short)", "refs/heads/unit/", "refs/heads/fix/"], main) or "").splitlines():
        b, _, up = line.partition(" ")
        out[b] = up
    return out


def place(path, unit, bolt):
    """A unit's place: its head, its change's tasks, whether its planning is complete, the open tasks, and its review."""
    info = {"path": path, "head": (run(["git", "rev-parse", "HEAD"], path) or "").strip() or None, "tasks": None,
            "planning": False, "reviewed": False, "open": []}
    listed = run(["openspec", "list", "--json"], path)
    if listed:
        for c in json.loads(listed).get("changes", []):
            if c.get("name") == unit:
                info["tasks"] = [c.get("completedTasks", 0), c.get("totalTasks", 0)]
    status = run(["openspec", "status", "--change", unit, "--json"], path)
    if status:
        info["planning"] = bool(json.loads(status).get("isPlanningComplete"))
    tasks = os.path.join(path, "openspec", "changes", unit, "tasks.md")
    if os.path.exists(tasks):
        info["open"] = [l.strip()[6:] for l in open(tasks) if l.strip().startswith("- [ ]")]
    if bolt:
        log = run(["git", "log", "--format=%(trailers:key=Reviewed-by,valueonly)", f"bolt/{bolt}..unit/{unit}"], path) or ""
        info["reviewed"] = bool(log.strip())
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


def kit(req, sites=False, running=None):
    main, kdir = req["main"], os.path.realpath(req["dir"])
    if not os.path.isdir(main):
        return {"ok": False, "error": f"no checkout at {main}"}
    trees = worktrees(main)
    at = {t["path"]: t.get("branch") for t in trees}
    ups = upstreams(main)
    out = {"ok": True, "main": changes(main, "main"), "bolts": {}, "places": {}, "fixes": []}
    tracked = [u[5:] for u in ups.values() if u.startswith("bolt/")]
    for b in list(dict.fromkeys(req.get("bolts", []) + tracked)):
        exists = run(["git", "rev-parse", "--verify", "-q", f"refs/heads/bolt/{b}"], main) is not None
        wt = os.path.join(kdir, "bolts", b)
        out["bolts"][b] = {"exists": exists, "changes": changes(main, f"bolt/{b}") if exists else [],
                           "worktree": wt if at.get(wt) == f"bolt/{b}" else None}
    places = os.path.join(kdir, "places")
    for path, branch in at.items():
        if os.path.dirname(path) != places or not branch:
            continue
        if branch.startswith("unit/"):
            unit = branch[5:]
            bolt = ups.get(branch, "")[5:] if ups.get(branch, "").startswith("bolt/") else None
            out["places"][unit] = dict(place(path, unit, bolt), branch=branch, bolt=bolt)
        elif branch.startswith("fix/"):
            bolt = ups.get(branch, "")[5:] if ups.get(branch, "").startswith("bolt/") else None
            # Merged: the bolt holds the fix's tip, and the fix has moved since it was made (its reflog's first entry).
            born = (run(["git", "reflog", "show", "--format=%H", branch], main) or "").split()
            tip = (run(["git", "rev-parse", branch], main) or "").strip()
            merged = bool(bolt) and bool(born) and tip != born[-1] and subprocess.run(
                ["git", "merge-base", "--is-ancestor", branch, f"bolt/{bolt}"], cwd=main).returncode == 0
            out["fixes"].append({"fix": branch, "path": path, "bolt": bolt, "merged": merged})
    if sites:
        out["sites"] = {path: devurl(path) for path, branch in at.items()
                        if os.path.dirname(path) in (places, os.path.join(kdir, "bolts")) and branch}
        out["routes"] = running
    return out


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    running = routes() if request.get("sites") else None
    print(json.dumps({k["main"]: kit(k, request.get("sites"), running) for k in request["kits"]}))
