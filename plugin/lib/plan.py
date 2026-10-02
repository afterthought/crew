#!/usr/bin/env python3
"""plan.py: the bolt plan, one recutils plan.rec per partition and blueprints repo, alone on its plan/<label> branch.

The plan holds only intent: Bolt and Unit records. Every stage is read from the kits. A write fetches the branch
over https, applies itself to the tip, checks the result with recfix and crew's own rules, commits through a
temporary index in crew's own bare cache of the repo (no working tree is touched), and pushes without force. A push
that is refused because someone wrote first is applied again to the new tip, up to five times.

  crew plan init <blueprints> <label>        create plan/<label> in a blueprints repo with the schema and no records
"""
import argparse, datetime, getpass, json, os, pathlib, re, subprocess, sys, tempfile

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew  # noqa: E402
from crew import Refusal, fail  # noqa: E402

REPLAYS = 5
CACHE = pathlib.Path.home() / ".cache/crew/git"
HEADER = """\
# The partition's bolts and their units: what is to be built, in which bolt,
# in what order. Nothing here says how far anything has got: `crew bolts`
# reads that from the kits. Written only by `crew bolt` and `crew unit`.
# A Source is a path in this repository, or <repo>:<path> in another.

%rec: Bolt
%doc: Work on branch bolt/<Bolt> of Repo, deployed and tested from <Repo>/bolts/<Bolt>.
%key: Bolt
%type: Bolt regexp /^[a-z0-9][a-z0-9-]*$/
%mandatory: Repo Goal
%allowed: Bolt Repo Goal Team Source
%unique: Repo Goal Team

%rec: Unit
%doc: One OpenSpec change named Unit, built on unit/<Unit> at <Repo>/places/<Unit>.
%key: Unit
%type: Unit regexp /^[a-z0-9][a-z0-9-]*$/
%type: Bolt rec Bolt
%mandatory: Repo Intent
%allowed: Unit Repo Bolt Intent After Source
%unique: Repo Bolt Intent
"""


def need_recutils():
    """Every plan command checks for recutils before anything else."""
    for c in ("recsel", "recfix"):
        if not __import__("shutil").which(c):
            sys.exit(f"crew's plan needs recutils, and {c} is not on PATH: install the recutils package "
                     "(crew's devenv.nix declares it; on a host, swancloud's packages)")


# ---------------------------------------------------------------------------------------------------- records

FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9_]*):(.*)$")


class Rec:
    """One record: its record set and its fields in order. A comment line inside a record is kept as field '#'."""

    def __init__(self, kind, fields):
        self.kind, self.fields = kind, fields

    def get(self, f):
        return next((v for n, v in self.fields if n == f), None)

    def all(self, f):
        return [v for n, v in self.fields if n == f]

    def drop(self, f):
        self.fields = [(n, v) for n, v in self.fields if n != f]

    def add(self, f, v, after=None):
        """Add a field, after the last field named `after` when there is one, else after the last of its own name."""
        at = None
        for i, (n, _) in enumerate(self.fields):
            if n == f or (after and n == after):
                at = i
        self.fields.insert(len(self.fields) if at is None else at + 1, (f, v))

    def set(self, f, v, after=None):
        if self.get(f) is None:
            self.add(f, v, after)
        else:
            first = next(i for i, (n, _) in enumerate(self.fields) if n == f)
            self.fields = [(n, w) for i, (n, w) in enumerate(self.fields) if n != f or i == first]
            self.fields[first] = (f, v)

    def name(self):
        return self.get(self.kind)

    def lines(self):
        out = []
        for n, v in self.fields:
            if n == "#":
                out.append(v)
                continue
            first, *rest = v.split("\n")
            out.append(f"{n}: {first}" if first else f"{n}:")
            out += [f"+ {l}" if l else "+" for l in rest]
        return out


class Plan:
    """plan.rec as paragraphs: the comments and record descriptors kept as written, and the records in file order."""

    def __init__(self, text):
        self.paras, kind, cur = [], None, []
        for line in text.split("\n") + [""]:
            if line.strip():
                cur.append(line)
                continue
            if not cur:
                continue
            if any(FIELD.match(l) for l in cur):
                fields = []
                for l in cur:
                    m = FIELD.match(l)
                    if l.startswith("#"):
                        fields.append(("#", l))
                    elif l.startswith("+"):
                        n, v = fields[-1]
                        fields[-1] = (n, v + "\n" + (l[2:] if l.startswith("+ ") else l[1:]))
                    elif m:
                        v = m.group(2)
                        fields.append((m.group(1), v[1:] if v.startswith(" ") else v))
                self.paras.append(Rec(kind, fields))
            else:
                for l in cur:
                    if l.startswith("%rec:"):
                        kind = l[5:].strip().split()[0]
                self.paras.append(cur)
            cur = []

    def text(self):
        return "\n\n".join("\n".join(p.lines() if isinstance(p, Rec) else p) for p in self.paras) + "\n"

    def recs(self, kind):
        return [p for p in self.paras if isinstance(p, Rec) and p.kind == kind]

    def bolts(self):
        return self.recs("Bolt")

    def units(self):
        return self.recs("Unit")

    def bolt(self, name):
        return next((b for b in self.bolts() if b.name() == name), None)

    def unit(self, name):
        return next((u for u in self.units() if u.name() == name), None)

    def units_of(self, bolt):
        return [u for u in self.units() if u.get("Bolt") == bolt]

    def queue(self, repo=None):
        return [u for u in self.units() if not u.get("Bolt") and repo in (None, u.get("Repo"))]

    def group(self, u):
        """The units built in order with this one: its bolt's, or its repo's queue."""
        return self.units_of(u.get("Bolt")) if u.get("Bolt") else self.queue(u.get("Repo"))

    def teams(self):
        return {b.name(): b.get("Team") for b in self.bolts()}

    def remove(self, rec):
        self.paras.remove(rec)

    def end_of(self, kind):
        """Where a new record of a set goes: after its last record, or after its descriptor when it has none."""
        recs = self.recs(kind)
        if recs:
            return self.paras.index(recs[-1]) + 1
        for i, p in enumerate(self.paras):
            if not isinstance(p, Rec) and any(l.startswith("%rec:") and l[5:].split()[0] == kind for l in p):
                return i + 1
        fail(f"the plan declares no %rec: {kind}")

    def insert(self, rec, before=None, after=None):
        if rec in self.paras:
            self.paras.remove(rec)
        if before is not None:
            at = self.paras.index(before)
        elif after is not None:
            at = self.paras.index(after) + 1
        else:
            at = self.end_of(rec.kind)
        self.paras.insert(at, rec)

    def place_last(self, u):
        """Put a unit at the end of its group: after the last unit of its bolt, or of its repo's queue."""
        others = [o for o in self.group(u) if o is not u]
        self.insert(u, after=others[-1] if others else None)


def recfix(text, what):
    """recfix --check on a plan or moves file; the message names what was checked."""
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / pathlib.Path(what).name
        f.write_text(text)
        r = subprocess.run(["recfix", "--check", str(f)], capture_output=True, text=True)
        if r.returncode:
            fail(f"{what} fails recfix --check: " + (r.stderr or r.stdout).strip().replace(str(f), pathlib.Path(what).name))


def check(plan):
    """crew's own rules, which recfix cannot check: a unit's bolt exists in the same repo, and its After names
    units of the same bolt, with no cycle."""
    bolts = {b.name(): b for b in plan.bolts()}
    units = {u.name(): u for u in plan.units()}
    for u in plan.units():
        b = u.get("Bolt")
        if b:
            b in bolts or fail(f"unit {u.name()} names bolt {b}, which the plan does not hold")
            bolts[b].get("Repo") == u.get("Repo") or fail(f"unit {u.name()} is in {u.get('Repo')} and its bolt {b} in {bolts[b].get('Repo')}")
        for a in u.all("After"):
            a in units or fail(f"unit {u.name()} comes after {a}, which the plan does not hold")
            b or fail(f"unit {u.name()} is queued, so it can come after nothing; dependencies are within a bolt")
            units[a].get("Bolt") == b or fail(f"unit {u.name()} comes after {a}, which is in {units[a].get('Bolt') or 'the queue'}, not {b}")
    seen, done = set(), set()

    def visit(n, path):
        if n in done:
            return
        n not in seen or fail("units would come after each other in a cycle: " + " -> ".join(path + [n]))
        seen.add(n)
        for a in units[n].all("After"):
            visit(a, path + [n])
        done.add(n)
    for n in units:
        visit(n, [])


# -------------------------------------------------------------------------------------------------- transport

def url(repo):
    """Every plan read and write goes over https: gh's credential helper on a Mac, the token helper on a box.
    Never ssh, which on a Mac waits on 1Password."""
    return f"https://github.com/{repo}.git"


def gitenv(extra=None):
    env = {k: v for k, v in os.environ.items() if k not in (
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_QUARANTINE_PATH")}
    env["GIT_TERMINAL_PROMPT"] = "0"
    return dict(env, **(extra or {}))


def cache(repo):
    """crew's bare cache of a repo, which holds the objects a write commits and has no working tree."""
    c = CACHE / f"{repo}.git"
    if not (c / "HEAD").exists():
        c.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q", "--bare", str(c)], check=True, env=gitenv())
    return c


def git(repo, *args, input=None, env=None, check=True):
    r = subprocess.run(["git", "-C", str(cache(repo)), *args], input=input, capture_output=True, text=True, env=gitenv(env))
    if check and r.returncode:
        fail(f"git {args[0]} in crew's cache of {repo} failed: {r.stderr.strip()}")
    return r if not check else r.stdout.strip()


def fetch(repo, ref):
    """The tip of a branch of the repo, fetched now over https, or None when the repo has no such branch."""
    r = git(repo, "fetch", "--quiet", "--no-tags", url(repo), f"+refs/heads/{ref}:refs/crew/{ref}", check=False)
    if r.returncode:
        if "couldn't find remote ref" in r.stderr:
            return None
        fail(f"could not fetch {ref} of {repo} over https: {r.stderr.strip()}")
    return git(repo, "rev-parse", f"refs/crew/{ref}")


def show(repo, tip, path):
    r = git(repo, "show", f"{tip}:{path}", check=False)
    return r.stdout if r.returncode == 0 else None


def commit(repo, parent, path, text, message):
    """A commit of one file's new text on top of parent, made through a temporary index: no working tree is touched."""
    blob = git(repo, "hash-object", "-w", "--stdin", input=text)
    with tempfile.TemporaryDirectory() as d:
        idx = {"GIT_INDEX_FILE": str(pathlib.Path(d) / "index")}
        git(repo, "read-tree", *([parent] if parent else ["--empty"]), env=idx)
        git(repo, "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env=idx)
        tree = git(repo, "write-tree", env=idx)
    return git(repo, "commit-tree", tree, *(["-p", parent] if parent else []), "-F", "-", input=message)


def land(repo, ref, path, make):
    """make(tip) gives a file's new text and the commit message, or refuses. The commit is pushed without force;
    when the push is refused because the branch moved, make runs again on the new tip, up to five times."""
    for _ in range(1 + REPLAYS):
        tip = fetch(repo, ref)
        text, message = make(tip)
        sha = commit(repo, tip, path, text, message)
        r = git(repo, "push", "--quiet", url(repo), f"{sha}:refs/heads/{ref}", check=False)
        if r.returncode == 0:
            git(repo, "update-ref", f"refs/crew/{ref}", sha)
            return sha
        if fetch(repo, ref) == tip:
            fail(f"the push of {ref} to {repo} failed: {r.stderr.strip()}")
    fail(f"{ref} of {repo} kept moving: the write was applied {1 + REPLAYS} times and each push was refused")


def agent():
    """Who is writing: the agent crew started (CREW_AGENT), else the user at this host."""
    return os.environ.get("CREW_AGENT") or f"{getpass.getuser()}@{crew.this_host()}"


# ---------------------------------------------------------------------------------------------------- the plan

def read(repo, label, tip):
    """plan.rec at a commit of plan/<label>, refused when it fails its schema, naming the commit."""
    text = show(repo, tip, "plan.rec")
    text is not None or fail(f"plan/{label} of {repo} at {tip[:7]} has no plan.rec")
    try:
        recfix(text, "plan.rec")
    except Refusal as e:
        fail(f"plan/{label} of {repo} at {tip[:7]}: {e}")
    return Plan(text)


def removed_by(repo, tip, kind, name):
    """The commit that removed a record, for a write whose subject is gone."""
    out = git(repo, "log", "-1", "--format=%h %s", "-G", f"^{kind}: {re.escape(name)}$", tip, "--", "plan.rec")
    return out or None


class Write:
    """What a change sees: the plan at the tip it is applied to, and how to refuse with the commit that removed something."""

    def __init__(self, repo, label, tip, plan):
        self.repo, self.label, self.tip, self.plan = repo, label, tip, plan

    def bolt(self, name):
        return self.plan.bolt(name) or self.gone("Bolt", name)

    def unit(self, name):
        return self.plan.unit(name) or self.gone("Unit", name)

    def gone(self, kind, name):
        by = removed_by(self.repo, self.tip, kind, name)
        fail(f"no {kind.lower()} {name} in plan/{self.label} of {self.repo}" + (f": {by} removed it" if by else ""))


def write(fleet, label, repo, change, subject, body=""):
    """Apply change(Write) to the tip of plan/<label>, check, commit and push it, replaying on a refused push.
    change returns the bolts it touched; each one's conductor is told the subject, unless it wrote it."""
    ref, seen = f"plan/{label}", {}
    message = f"{subject} ({agent()})" + (f"\n\n{body}" if body else "") + "\n"

    def make(tip):
        tip or fail(f"{repo} has no plan/{label} yet: crew plan init {repo} {label}")
        w = Write(repo, label, tip, read(repo, label, tip))
        before = w.plan.teams()
        touched = change(w) or []
        check(w.plan)
        text = w.plan.text()
        recfix(text, "plan.rec")
        seen.update(before=before, after=w.plan.teams(), touched=touched)
        return text, message
    sha = land(repo, ref, "plan.rec", make)
    print(f"plan/{label} {sha[:7]}: {message.splitlines()[0]}")
    notify(fleet, seen, message.splitlines()[0])
    return sha


def notify(fleet, seen, subject):
    """Tell the conductor of each team holding a bolt the write touched, unless that conductor wrote it."""
    teams = {seen["before"].get(b) for b in seen["touched"]} | {seen["after"].get(b) for b in seen["touched"]}
    for t in sorted(x for x in teams if x):
        if f"{t}-conductor" != agent() and t in fleet["teams"]:
            crew.tell(fleet, f"{t}-conductor", subject)


def init(fleet, args):
    p = crew.partition_of(fleet, args.label)
    repo = blueprints_of(p, args.blueprints)

    def make(tip):
        tip is None or fail(f"{repo} already has plan/{p['label']} (at {tip[:7]})")
        recfix(HEADER, "plan.rec")
        return HEADER, f"plan: start plan/{p['label']} ({agent()})\n"
    sha = land(repo, f"plan/{p['label']}", "plan.rec", lambda tip: make(tip))
    print(f"plan/{p['label']} {sha[:7]}: created in {repo}")


def blueprints_of(p, name):
    """One of a partition's blueprints repos, named as owner/name or by its name."""
    found = [b for b in p["blueprints"] if b == name or b.split("/")[-1] == name]
    len(found) == 1 or fail(f"{name} is not one of {p['label']}'s blueprints repos: " + " ".join(p["blueprints"]))
    return found[0]


# ----------------------------------------------------------------------------------------------------- the CLI

def parser():
    ap = argparse.ArgumentParser(prog="crew", add_help=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("plan").add_subparsers(dest="sub", required=True)
    i = pl.add_parser("init")
    i.add_argument("blueprints")
    i.add_argument("label")
    return ap


def main(argv):
    need_recutils()
    args = parser().parse_args(argv)
    fleet = crew.load()
    {("plan", "init"): init}[(args.cmd, getattr(args, "sub", None))](fleet, args)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
