#!/usr/bin/env python3
"""plan.py: the bolt plan, one recutils plan.rec per flywheel, on the flywheel's branch of its state repository.

A flywheel is a partition's loop, named by its label. Its state is the files on the branch <label>/main of the
state repository the teams file names for it (`state`): plan.rec, moves.rec, proposals.rec, the signals agents record
under signals/, and the run record under runs/<host>/.
The plan holds only intent: Bolt and Unit records. Every stage is read from the kits. The planner changes it only
by a proposal (proposals.rec) the user approves; who else writes it directly is may_write's table. A write fetches the branch
over https, applies itself to the tip, checks each file it changed with recfix (the plan with crew's own rules
too), commits through a temporary index in crew's own bare cache of the repo (no working tree is touched), and
pushes without force. A push that is refused because someone wrote first is applied again to the new tip, up to
five times. A write that changes several files is one commit, and it carries the host's uncarried run record.

  crew state init <label>                    create <label>/main in the state repository, adopting plan/<label> and
                                             the moves where the partition's blueprints repos have them
  crew bolts [<bolt>] [--label L] [--json]   every bolt and unit of the plans, each unit's stage read from its kit
  crew bolt new <bolt> "<goal>" --repo <kit> [--source S]... [--before <bolt>]
  crew bolt give <team> [<bolt>]             the team takes the bolt (default: the first planned in its kit)
  crew bolt order <bolt> --before <bolt>|--first|--last
  crew bolt drop <bolt> "<reason>" [--requeue]
                                             the bolt and its units out of the plan, or with --requeue its units
                                             queued, refused while one has a worktree; its worktrees then go from its
                                             team's host
  crew bolt land <bolt>                      once every unit has landed on main; its worktree then goes from its
                                             team's host, unless it has uncommitted changes
  crew unit add <unit> "<intent>" --bolt <bolt>|--repo <kit> [--source S]... [--after U]... [--before U] [--signal ID]
                                             [--unblocks <bolt>]
  crew unit split <unit> "<narrowed intent>" --into <unit> "<intent>" [--into ...]
  crew unit amend <unit> "<new intent>"      a unit's intent replaced; one with a worktree is marked amended, and its
                                             conductor runs construct again
  crew unit order <unit> --before <unit>|--first|--last
  crew unit after <unit> <unit>...|--none
  crew unit move <unit> <bolt>|queue [--unblocks <bolt>]
  crew unit drop <unit> "<reason>"
  crew unit approve <unit>                   the user's review, an empty Reviewed-by: commit on unit/<unit>
  crew plan propose <file> [--replaces <n>]  the planner's proposal: a Case and the plan commands it would run (Do)
  crew plan proposed [<n>] [--json]          the open proposals, or one as the user reads it
  crew plan agree <n> [--team <team>]        a conductor's agreement to a proposal that touches its bolt
  crew plan approve <n>                      the proposal applied, exactly as read, in one commit
  crew plan drop <n> "<reason>"              the proposal closed unapplied
  crew signal <slug> "<what it asserts>" --excerpt "<the words, verbatim>"|--excerpt-file <path> [--kind K] [--subject a,b]
                                             a finding, as a capture and its signal on the flywheel's branch: an
                                             agent's excerpt checked against its own Claude transcript and graded, the
                                             user's note at a shell its own excerpt
  crew signal show <id>                      a signal with its capture's provenance and its move, from either home
  crew signal move <id> attach|challenge|new-territory|answered|drop [--target T] [--reason R]
                                             curation's move for a signal, in moves.rec on the flywheel's branch

A signal recorded through crew is on the flywheel's branch, under signals/; one the daily pass read from a meeting or
a channel is in the partition's first blueprints repo. An id is looked up in that order.

A command that names no partition reads them all, or the agent's own (CREW_LABEL); --label names one.
"""
import argparse, contextlib, datetime, fcntl, getpass, hashlib, json, os, pathlib, re, shlex, subprocess, sys, tempfile

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew  # noqa: E402
import gather  # noqa: E402
import record  # noqa: E402
import transcript  # noqa: E402
from crew import Refusal, fail  # noqa: E402

REPLAYS = 5
# What a command found out before it wrote or was refused: the partition whose run record its entry goes in.
CONTEXT = {}
CACHE = pathlib.Path.home() / ".cache/crew/git"
HEADER = """\
# The partition's bolts and their units: what is to be built, in which bolt,
# in what order. Nothing here says how far anything has got: `crew bolts`
# reads that from the kits. Written only by `crew bolt` and `crew unit`.
# A Source is a path in the flywheel's first blueprints repo, or
# <owner>/<name>:<path> in another.

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
%allowed: Unit Repo Bolt Intent After Source Amended
%unique: Repo Bolt Intent
"""
MOVES = """\
# The flywheel's curation moves: one per signal, appended through crew and
# never merged. A Signal is a signal's id: signals/<id>.md on this branch, or
# in the flywheel's first blueprints repo.

%rec: Move
%doc: A curation move over one signal, stored with its inputs.
%key: Signal
%mandatory: Signal Move Date By
%allowed: Signal Move Target Reason Date By
%type: Move enum attach challenge new-territory answered drop route
%type: Date date
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


def declares(p):
    """The record set a paragraph of the plan declares, or None for a record or a comment."""
    return None if isinstance(p, Rec) else next((l[5:].split()[0] for l in p if l.startswith("%rec:")), None)


def in_step(plan):
    """Bring each record descriptor of a plan in step with crew's own (HEADER), so a branch started before a field was
    allowed takes it on its next write. Returns whether any changed."""
    want = {declares(p): p for p in Plan(HEADER).paras if declares(p)}
    changed = False
    for i, p in enumerate(plan.paras):
        k = declares(p)
        if k in want and p != want[k]:
            plan.paras[i], changed = list(want[k]), True
    return changed


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


def commit(repo, parent, files, message):
    """A commit of files' new text ({path: text}) on top of parent, made through a temporary index: no working tree
    is touched, and no other path changes."""
    with tempfile.TemporaryDirectory() as d:
        idx = {"GIT_INDEX_FILE": str(pathlib.Path(d) / "index")}
        git(repo, "read-tree", *([parent] if parent else ["--empty"]), env=idx)
        for path, text in files.items():
            blob = git(repo, "hash-object", "-w", "--stdin", input=text)
            git(repo, "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env=idx)
        tree = git(repo, "write-tree", env=idx)
    return git(repo, "commit-tree", tree, *(["-p", parent] if parent else []), "-F", "-", input=message)


def land(repo, ref, path, make):
    """make(tip) gives a file's new text (or, with path None, {path: text}) and the commit message, or refuses. The
    commit is pushed without force; when the push is refused because the branch moved, make runs again on the new
    tip, up to five times."""
    for _ in range(1 + REPLAYS):
        tip = fetch(repo, ref)
        text, message = make(tip)
        sha = commit(repo, tip, text if path is None else {path: text}, message)
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

def state_of(fleet, label):
    """A flywheel's state repository and its branch there: <owner>/<name> and <label>/main."""
    return crew.partition_of(fleet, label)["state"], f"{label}/main"


def read(repo, ref, tip):
    """plan.rec at a commit of a branch, refused when it fails its schema, naming the commit."""
    text = show(repo, tip, "plan.rec")
    text is not None or fail(f"{ref} of {repo} at {tip[:7]} has no plan.rec")
    try:
        recfix(text, "plan.rec")
    except Refusal as e:
        fail(f"{ref} of {repo} at {tip[:7]}: {e}")
    return Plan(text)


def removed_by(repo, tip, kind, name):
    """The commit that removed a record, for a write whose subject is gone."""
    out = git(repo, "log", "-1", "--format=%h %s", "-G", f"^{kind}: {re.escape(name)}$", tip, "--", "plan.rec")
    return out or None


class Write:
    """What a change sees: the flywheel's state at the tip it is applied to (the plan, and any other file it reads or
    replaces), and how to refuse with the commit that removed something."""

    def __init__(self, repo, label, tip, plan):
        self.repo, self.label, self.tip, self.plan, self.subject = repo, label, tip, plan, None
        self.files = {}  # every other file the change replaced, {path: text}, committed with the plan
        self.quiet = set()  # teams the write's own command greets, so notify leaves them be
        self.on, self.frm = [], []  # objects only the change can name, for the write's run-record entry

    def text(self, path):
        """A file of the branch as the change has left it: replaced, else at the tip, else None."""
        return self.files[path] if path in self.files else show(self.repo, self.tip, path)

    def replace(self, path, text):
        self.files[path] = text

    def bolt(self, name):
        return self.plan.bolt(name) or self.gone("Bolt", name)

    def unit(self, name):
        return self.plan.unit(name) or self.gone("Unit", name)

    def gone(self, kind, name):
        by = removed_by(self.repo, self.tip, kind, name)
        fail(f"no {kind.lower()} {name} in {self.label}/main of {self.repo}" + (f": {by} removed it" if by else ""))


def message(subject, body, eid):
    """A commit message: the subject, the body where there is one, and the Crew-Entry trailer naming the run-record
    entry that describes the commit."""
    return subject + (f"\n\n{body}" if body else "") + (f"\n\nCrew-Entry: {eid}" if eid else "") + "\n"


def carried(label, repo, tip, files):
    """Add the host's uncarried run record of the label to a commit's files; the newest id it carries."""
    runs, newest = record.carry(label, lambda path: show(repo, tip, path))
    files.update(runs)
    return newest


def write(fleet, label, change, subject, body="", act=None, on=(), frm=()):
    """Apply change(Write) to the tip of the flywheel's branch, its plan's record descriptors first brought in step
    with crew's, check every file it changed, commit them with the host's uncarried run record, and push, replaying on
    a refused push. change returns the bolts it touched; each one's conductor is told the subject, unless it wrote it.
    The commit names its run-record entry; with act, that entry is written once pushed, naming on and frm and whatever
    the change added to them. Returns the commit."""
    repo, ref = state_of(fleet, label)
    seen = {"eid": record.new_id()}
    CONTEXT.update(label=label, eid=seen["eid"])

    def make(tip):
        tip or fail(f"{repo} has no {ref} yet: crew state init {label}")
        w = Write(repo, label, tip, read(repo, ref, tip))
        in_step(w.plan)
        before = w.plan.teams()
        touched = change(w) or []
        check(w.plan)
        text = w.plan.text()
        recfix(text, "plan.rec")
        files = {"plan.rec": text}
        for path, t in w.files.items():
            if path.endswith(".rec"):
                recfix(t, path)
            files[path] = t
        seen.update(before=before, after=w.plan.teams(), touched=touched, quiet=w.quiet, label=label,
                    subject=f"{w.subject or subject} ({agent()})", on=list(on) + w.on, frm=list(frm) + w.frm)
        seen["newest"] = carried(label, repo, tip, files)
        return files, message(seen["subject"], body, seen["eid"])
    sha = land(repo, ref, None, make)
    record.mark_carried(label, seen["newest"])
    print(f"{ref} {sha[:7]}: {seen['subject']}")
    if act:
        record.emit(label, act, seen["on"], seen["frm"], [f"{repo}@{sha}"], record.subject(seen["subject"]), eid=seen["eid"])
    notify(fleet, seen, seen["subject"])
    return sha


def notify(fleet, seen, subject):
    """Tell the conductor of each team holding a bolt the write touched, unless that conductor wrote it, or the
    write's own command greets it instead. Tell the partition's dispatchers that are up of a bolt added, or of one
    landed or dropped that frees a team, so a free team gets its next bolt, unless one of them wrote it."""
    before, after, touched = seen["before"], seen["after"], seen["touched"]
    teams = {before.get(b) for b in touched} | {after.get(b) for b in touched}
    for t in sorted(x for x in teams if x and x not in seen["quiet"]):
        if f"{t}-conductor" != agent() and t in fleet["teams"]:
            crew.tell(fleet, f"{t}-conductor", subject)
    added = [b for b in touched if b not in before and b in after]
    freed = [b for b in touched if b not in after and before.get(b)]
    if added or freed:
        label = seen["label"]
        for host in crew.partition_hosts(fleet, label):
            d = f"{label}-dispatch-{host}"
            if d != agent() and crew.agent_status(fleet, d):
                crew.tell(fleet, d, f"{subject}. Give a free team its next bolt.")


def carry_now(fleet, label):
    """crew events --push: the host's uncarried run record of the label, carried to its branch in a commit of its
    own; nothing at all when there is nothing to carry. Such a commit records no act, so it names no entry: an entry
    of its own would be left uncarried by every push."""
    repo, ref = state_of(fleet, label)
    tip = fetch(repo, ref) or fail(f"{repo} has no {ref} yet: crew state init {label}")
    if not record.carry(label, lambda path: show(repo, tip, path))[0]:
        print(f"{ref}: nothing of {crew.this_host()}'s run record left to carry")
        return
    seen = {}

    def make(tip):
        files = {}
        seen["newest"] = carried(label, repo, tip, files)
        return files, message(f"runs({crew.this_host()}): carry the run record ({agent()})", "", None)
    sha = land(repo, ref, None, make)
    record.mark_carried(label, seen["newest"])
    print(f"{ref} {sha[:7]}: carried {crew.this_host()}'s run record")


# --------------------------------------------------------------------------------------------- crew state init

def state_init(fleet, a):
    """Create the flywheel's branch, adopting what the partition had: the first blueprints repo's plan/<label> is
    pushed as the branch, so the plan's history is the branch's, else the branch starts with an empty plan; each other
    blueprints repo's plan/<label> is joined in one commit naming where it came from; the plan's record descriptors are
    brought in step with crew's; then moves.rec, with the first blueprints repo's moves. Every step is its own push and first checks whether the branch already shows it, so a
    run that stopped partway is finished by running it again, and a finished branch is only reported."""
    p = crew.partition_of(fleet, a.label)
    label = p["label"]
    repo, ref = state_of(fleet, label)
    CONTEXT["label"] = label
    # What the partition had, read whole before anything is pushed.
    old = []
    for bp in p["blueprints"]:
        t = fetch(bp, f"plan/{label}")
        if t:
            old.append((bp, t, read(bp, f"plan/{label}", t)))
    owner = {}
    for bp, _, plan in old:
        for r in plan.bolts() + plan.units():
            other = owner.setdefault((r.kind, r.name()), bp)
            other == bp or fail(f"plan/{label} of {other} and plan/{label} of {bp} both hold {r.kind.lower()} {r.name()}: "
                                "rename one in its plan first; nothing was written")
    first = old[0] if old and old[0][0] == p["blueprints"][0] else None
    joins = [o for o in old if o is not first]
    did = []
    tip = fetch(repo, ref)
    if tip is None:
        if first:
            bp, t, _ = first
            r = git(bp, "push", "--quiet", url(repo), f"{t}:refs/heads/{ref}", check=False)
            r.returncode == 0 or fail(f"could not push plan/{label} of {bp} to {repo} as {ref}: {r.stderr.strip()}")
            tip = fetch(repo, ref)
            did.append(f"adopted plan/{label} of {bp} at {t[:7]}, with its history")
            record.emit(label, "state.init", [f"plan/{label}"], commit=[f"{repo}@{tip}"], why=f"state({label}): adopt plan/{label} of {bp}")
        else:
            tip = init_step(repo, ref, label, f"state({label}): start the flywheel's plan",
                            lambda w_tip, files: files.update({"plan.rec": HEADER}) if w_tip is None else fail(f"{repo} has {ref} since {w_tip[:7]}"))
            did.append("started an empty plan")
    for bp, t, plan in joins:
        mark = f"join plan/{label} of {bp} at {t[:7]}"
        if git(repo, "log", "--format=%h", "-F", f"--grep={mark}", tip):
            continue

        def join(w_tip, files, bp=bp, plan=plan):
            have = read(repo, ref, w_tip)
            for r in plan.bolts() + plan.units():
                (have.bolt if r.kind == "Bolt" else have.unit)(r.name()) is None or fail(
                    f"{ref} of {repo} already holds {r.kind.lower()} {r.name()}, which plan/{label} of {bp} also holds; nothing was joined")
                fields = [(n, v if n != "Source" or ":" in v else f"{bp}:{v}") for n, v in r.fields]
                have.insert(Rec(r.kind, fields))
            check(have)
            files["plan.rec"] = have.text()
        tip = init_step(repo, ref, label, f"state({label}): {mark}", join)
        did.append(f"joined plan/{label} of {bp} at {t[:7]}")
    if in_step(read(repo, ref, tip)):
        def step(w_tip, files):
            have = read(repo, ref, w_tip)
            in_step(have)
            files["plan.rec"] = have.text()
        tip = init_step(repo, ref, label, f"state({label}): the plan's record descriptors in step with crew's", step)
        did.append("brought the plan's record descriptors in step with crew's")
    if show(repo, tip, "moves.rec") is None:
        src = p["blueprints"][0]
        st = fetch(src, "main")
        moves = show(src, st, "signals/moves.rec") if st else None
        recs = Plan(moves).recs("Move") if moves else []
        at = f" at {st[:7]}" if moves else ""

        def start_moves(w_tip, files):
            show(repo, w_tip, "moves.rec") is None or fail(f"{ref} of {repo} has moves.rec since {w_tip[:7]}")
            files["moves.rec"] = MOVES + "".join("\n" + "\n".join(r.lines()) + "\n" for r in recs)
            if show(repo, w_tip, "proposals.rec") is None:
                files["proposals.rec"] = PROPOSALS
        tip = init_step(repo, ref, label, f"state({label}): moves.rec, with the {len(recs)} moves of {src}'s signals/moves.rec{at}", start_moves)
        did.append(f"added moves.rec with {len(recs)} moves of {src}{at}")
    if did:
        print(f"{ref} of {repo} {tip[:7]}: " + "; ".join(did))
    else:
        print(f"{ref} of {repo} exists, at {tip[:7]}: nothing to do")


def init_step(repo, ref, label, subject, make_files):
    """One step of crew state init: make_files(tip, files) fills the commit's files at the tip (None when the branch
    is not there yet), pushed without force and replayed on a moved tip. The step's entry names its commit."""
    eid = record.new_id()

    def make(tip):
        files = {}
        make_files(tip, files)
        for path, text in files.items():
            recfix(text, path)
        return files, message(f"{subject} ({agent()})", "", eid)
    sha = land(repo, ref, None, make)
    record.emit(label, "state.init", [f"plan/{label}"], commit=[f"{repo}@{sha}"], why=subject, eid=eid)
    return sha


# ------------------------------------------------------------------------------------------ the kits, per host

GATHER = (LIB / "gather.py").read_text()
LATER = ("code", "verify", "merged", "landed")


def survey(fleet, held, sites=False):
    """Read the kits of every host holding active bolts, one call per host. held is [(team, bolt)]. The answer is
    per host: its kits by main checkout, or why it did not answer. With sites, each worktree's devurl names and
    the host's running portless routes too."""
    hosts = {}
    for team, bolt in held:
        t = fleet["teams"].get(team)
        if not t:
            continue
        k = hosts.setdefault(t["machine"], {}).setdefault(t["kit"]["main"], {"main": t["kit"]["main"], "dir": t["kit"]["dir"], "bolts": []})
        if bolt and bolt not in k["bolts"]:
            k["bolts"].append(bolt)
    out = {}
    for host, kits in sorted(hosts.items()):
        r = crew.on_machine(fleet, host, ["python3", "-", json.dumps({"kits": list(kits.values()), "sites": sites})], input=GATHER)
        if r.returncode == 0:
            out[host] = {"ok": True, "kits": json.loads(r.stdout)}
        else:
            out[host] = {"ok": False, "error": ((r.stderr or "").strip().splitlines() or [f"exit {r.returncode}"])[-1]}
    return out


def amended(mark):
    """Whether a unit's Amended mark waits for construct to be run again: proposal/<n> or intent. Any other mark is
    the head of unit/<unit> when construct started again."""
    return mark == "intent" or (mark or "").startswith("proposal/")


def place_stage(pl, mark=None):
    """The stage of a unit that has neither landed nor merged, from its place and its Amended mark. A marked unit is
    amended until construct runs again, in construct while its head is still where construct started, and in review
    once it has moved, whatever its tasks say. Otherwise: verify, code, approved, review or construct, from its tasks,
    its planning and its review."""
    if mark:
        return "amended" if amended(mark) else "construct" if not pl or pl.get("head") == mark else "review"
    done, total = pl["tasks"] or (0, 0)
    return ("verify" if total and done == total else "code" if done else
            "approved" if pl["planning"] and pl["reviewed"] else "review" if pl["planning"] else "construct")


class Stages:
    """Each unit's stage, read from its kit on its team's host. The first rule that holds is the stage:
    landed, merged, then amended, construct or review for a unit the plan marks amended, then verify, code, approved,
    review, construct, then ready or waiting by its After units; a unit with no bolt is queued, and one whose host
    does not answer is unknown."""

    def __init__(self, fleet, plan, survey):
        self.fleet, self.plan, self.survey, self.memo = fleet, plan, survey, {}

    def kit(self, b):
        """The bolt's team, host and kit as read, or why they can't be."""
        t = self.fleet["teams"].get(b.get("Team"))
        if not t:
            return None, f"team {b.get('Team')} is not in the teams file"
        h = self.survey.get(t["machine"])
        if not h or not h["ok"]:
            return None, f"{t['machine']} did not answer" + (f" ({h['error']})" if h else "")
        k = h["kits"].get(t["kit"]["main"])
        if not k or not k.get("ok"):
            return None, f"{t['machine']}: " + (k.get("error") if k else "the kit was not read")
        return dict(k, team=t, host=t["machine"]), None

    def of(self, name):
        if name in self.memo:
            return self.memo[name]
        u = self.plan.unit(name)
        self.memo[name] = res = {"stage": "unknown", "tasks": None, "worktree": None, "open": []}
        b = u.get("Bolt")
        if not b:
            res["stage"] = "queued"
            return res
        bolt = self.plan.bolt(b)
        if bolt.get("Team"):
            k, why = self.kit(bolt)
            if not k:
                res["why"] = why
                return res
            pl = k["places"].get(name)
            res["worktree"], res["head"] = (pl["path"], pl.get("head")) if pl else (None, None)
            if name in k["main"]:
                res["stage"] = "landed"
                return res
            if name in k["bolts"].get(b, {}).get("changes", []):
                res["stage"] = "merged"
                return res
            if pl or u.get("Amended"):
                if pl:
                    res.update(tasks=pl["tasks"], open=pl["open"])
                res["stage"] = place_stage(pl, u.get("Amended"))
                return res
        deps = [self.of(a)["stage"] for a in u.all("After")]
        res["stage"] = "unknown" if "unknown" in deps else ("ready" if all(d in ("merged", "landed") for d in deps) else "waiting")
        return res

    def bolt_state(self, b):
        if not b.get("Team"):
            return "planned"
        k, _ = self.kit(b)
        if not k:
            return "unknown"
        units = self.plan.units_of(b.name())
        return "landed" if units and all(self.of(u.name())["stage"] == "landed" for u in units) else "active"


def stages_for(fleet, plan, bolts):
    """Stages for the units of the given bolts, reading only the hosts that hold them."""
    held = [(b.get("Team"), b.name()) for b in bolts if b.get("Team")]
    return Stages(fleet, plan, survey(fleet, held))


# ------------------------------------------------------------------------------------------- finding the plans

def default_label(fleet, a):
    """The partition a command means: --label, else the agent's own (CREW_LABEL), else none."""
    label = getattr(a, "label", None) or os.environ.get("CREW_LABEL")
    if label:
        crew.partition_of(fleet, label)
        CONTEXT.setdefault("label", label)
    return label


def plans(fleet, labels, errors=None):
    """(label, repo, tip, plan) for each flywheel's one plan, on its branch of its state repository, with tip and
    plan None where the branch is not started. A plan that can't be read is left out and its reason put in errors
    when that is given, else refused."""
    out = []
    for l in labels:
        repo = None
        try:
            repo, ref = state_of(fleet, l)
            tip = fetch(repo, ref)
            out.append((l, repo, tip, read(repo, ref, tip) if tip else None))
        except Refusal as e:
            if errors is None:
                raise
            errors[f"{ref} of {repo}" if repo else f"the plan of {l}"] = str(e)
    return out


def locate(fleet, kind, name, label):
    labels, errors = [label] if label else list(fleet["partitions"]), {}
    hits = [h for h in plans(fleet, labels, errors) if h[3] and (h[3].bolt(name) if kind == "Bolt" else h[3].unit(name))]
    hits or fail(f"no {kind.lower()} {name} in the plans of " + ", ".join(labels)
                 + "".join(f"; {k} could not be read: {v}" for k, v in errors.items()))
    len(hits) == 1 or fail(f"{kind.lower()} {name} is in more than one plan: " + ", ".join(f"{h[0]}/main of {h[1]}" for h in hits) + "; add --label")
    CONTEXT["label"] = hits[0][0]
    return hits[0]


def kit_teams(fleet, kit, label=None):
    return [t for n, t in sorted(fleet["teams"].items()) if t["kit"]["name"] == kit and label in (None, t["label"])]


def plan_for(fleet, kit, label):
    """The plan a kit's work goes in, (label, state repository): the flywheel of the teams that build it."""
    labels = sorted({t["label"] for t in kit_teams(fleet, kit, label)})
    labels or fail(f"no team" + (f" of {label}" if label else "") + f" builds {kit}, so no plan holds its work")
    len(labels) == 1 or fail(f"{kit}'s work could go in the plan of " + ", ".join(labels) + "; add --label")
    CONTEXT["label"] = labels[0]
    return labels[0], state_of(fleet, labels[0])[0]


def name_free(fleet, label, kit, names):
    """A unit's name is its OpenSpec change's: refused when the kit's main already has that change, open or archived."""
    t = kit_teams(fleet, kit, label)[0]
    sv = survey(fleet, [(t["name"], None)])[t["machine"]]
    sv["ok"] or fail(f"cannot check {kit}'s changes: {t['machine']} did not answer ({sv['error']})")
    k = sv["kits"][t["kit"]["main"]]
    k.get("ok") or fail(f"cannot check {kit}'s changes on {t['machine']}: {k.get('error')}")
    for n in names:
        crew.NAME.match(n) or fail(f"a unit's name is lowercase words with dashes, not {n}")
        n not in k["main"] or fail(f"{kit}'s main already has a change named {n}, open or archived; pick another name")


def host_run(fleet, host, script, *args):
    """Run a bash script on a host, with its arguments; refused with its own words when it fails."""
    r = crew.on_machine(fleet, host, ["bash", "-c", script, "crew", *args])
    r.returncode == 0 or fail(f"on {host}: " + ((r.stderr or r.stdout).strip() or f"exit {r.returncode}"))
    return r.stdout.strip()


PLACE = r"""set -e
main=$1 path=$2 branch=$3 base=$4 track=$5
cd "$main"
[ -d "$path" ] && exit 0
if git rev-parse --verify -q "refs/heads/$branch" >/dev/null; then git worktree add -q "$path" "$branch"
elif [ "$track" = track ]; then git worktree add -q --track -b "$branch" "$path" "$base"
else git worktree add -q -b "$branch" "$path" "$base"; fi
# A kit that needs a new worktree prepared (its dependencies installed) gives its devenv a crew-prepare script,
# run from the main checkout's profile, since a worktree has no devenv of its own.
p="$main/.devenv/profile/bin"
if [ -x "$p/crew-prepare" ]; then cd "$path" && KIT="$main" PATH="$p:$PATH" crew-prepare >/dev/null; fi
"""


def make_place(fleet, t, path, branch, base, track=False):
    """A worktree at a fixed path, made with git itself on the team's host and prepared as the kit says."""
    host_run(fleet, t["machine"], PLACE, t["kit"]["main"], path, branch, base, "track" if track else "")


# A host clones a kit once and never pulls it, so its main can lag GitHub's by hundreds of commits. Prints the ref a
# bolt is cut from: GitHub's main, fetched now, with the checkout's main fast-forwarded to it when that is safe; or the
# checkout's own main when it already holds all of GitHub's. A main with commits of its own that also lacks some of
# GitHub's is refused, since a bolt cut from either side would lose the other. A kit with no origin keeps its main.
FRESH = r"""main=$1
n() { if [ "$1" = 1 ]; then echo "1 commit"; else echo "$1 commits"; fi; }
cd "$main" || exit 1
git remote get-url origin >/dev/null 2>&1 || { echo main; exit 0; }
err=$(git fetch -q origin 2>&1) || { echo "cannot fetch $(basename "$(dirname "$main")") from GitHub, so a bolt can't be cut from its main: $err" >&2; exit 1; }
git rev-parse --verify -q origin/main >/dev/null || { echo main; exit 0; }
ahead=$(git rev-list --count origin/main..main) behind=$(git rev-list --count main..origin/main)
if [ "$ahead" -gt 0 ] && [ "$behind" -gt 0 ]; then
  echo "main on this host has $(n $ahead) of its own and lacks $(n $behind) of GitHub's: rebase it onto origin/main first, and never push it with force" >&2; exit 1
elif [ "$behind" -gt 0 ]; then
  if [ "$(git branch --show-current)" = main ] && [ -z "$(git status --porcelain)" ]; then
    git merge -q --ff-only origin/main && echo "main fast-forwarded $(n $behind) to GitHub's" >&2
  else
    echo "main is $(n $behind) behind GitHub's and was left as it is (another branch is checked out there, or it has uncommitted changes)" >&2
  fi
  echo origin/main
else
  [ "$ahead" -gt 0 ] && echo "main holds $(n $ahead) GitHub's main does not yet have; the bolt is cut from them" >&2
  echo main
fi
"""


def fresh_base(fleet, t):
    """The ref a team's next bolt is cut from, on its host, after fetching the kit from GitHub."""
    r = crew.on_machine(fleet, t["machine"], ["bash", "-c", FRESH, "crew", t["kit"]["main"]])
    r.returncode == 0 or fail(f"on {t['machine']}: " + ((r.stderr or r.stdout).strip() or f"exit {r.returncode}"))
    if r.stderr.strip():
        print(r.stderr.strip())
    return r.stdout.strip() or "main"


# How far a kit's main on its host is from GitHub's, after fetching: "<ahead> <behind>", or nothing for a kit with no
# origin or a GitHub repo with no main yet.
BEHIND = r"""main=$1
cd "$main" || exit 1
git remote get-url origin >/dev/null 2>&1 || exit 0
err=$(git fetch -q origin 2>&1) || { echo "cannot fetch $(basename "$(dirname "$main")") from GitHub, so cannot tell whether its main is behind GitHub's: $err" >&2; exit 1; }
git rev-parse --verify -q origin/main >/dev/null || exit 0
echo "$(git rev-list --count origin/main..main) $(git rev-list --count main..origin/main)"
"""


def tidy_after(fleet, t, what):
    """crew _tidy on the team's host, after a plan write that ends work there: the slots of work the plan no longer
    has are freed and the worktrees whose work is over removed, as the team's next read would, saying what it did. A
    host that does not answer leaves that to the team's next read, and the write stands."""
    r = crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], "_tidy", t["name"]))
    if r.returncode:
        why = "did not answer" if r.returncode == 255 else "failed (" + ((r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1] + ")"
        print(f"{t['name']}'s host {why}, so its worktrees for {what} are not removed yet: the team's next read removes them")
    elif (r.stdout + r.stderr).strip():
        print((r.stdout + r.stderr).strip())


# --------------------------------------------------------------------------------------------------- bolts

def held_by(plan, team):
    return [b for b in plan.bolts() if b.get("Team") == team]


def bolt_give(fleet, a):
    t = crew.team_of(fleet, a.team)
    label, kit = t["label"], t["kit"]["name"]
    repo, ref = state_of(fleet, label)
    CONTEXT["label"] = label
    tip = fetch(repo, ref)
    tip or fail(f"{repo} has no {ref} yet: crew state init {label}")
    plan = read(repo, ref, tip)
    held = held_by(plan, t["name"])
    if held:
        st = stages_for(fleet, plan, held)
        for b in held:
            open_ = [(u.name(), st.of(u.name())["stage"]) for u in plan.units_of(b.name()) if st.of(u.name())["stage"] != "landed"]
            if open_:
                fail(f"{t['name']} holds bolt {b.name()}, whose unit {open_[0][0]} has not landed ({open_[0][1]})")
            if not plan.units_of(b.name()):
                fail(f"{t['name']} holds bolt {b.name()}, which has no units yet")
            fail(f"{t['name']} holds bolt {b.name()}, landed but still in the plan: crew bolt land {b.name()}")
    base = fresh_base(fleet, t)

    def change(w):
        again = held_by(w.plan, t["name"])
        not again or fail(f"{t['name']} holds bolt {again[0].name()} since {tip[:7]}")
        if a.bolt:
            b = w.bolt(a.bolt)
            b.get("Repo") == kit or fail(f"bolt {a.bolt} is in {b.get('Repo')}, and {t['name']} builds {kit}")
            not b.get("Team") or fail(f"bolt {a.bolt} is held by {b.get('Team')}")
        else:
            free = [b for b in w.plan.bolts() if b.get("Repo") == kit and not b.get("Team")]
            free or fail(f"{label}/main has no planned bolt in {kit} for {t['name']}")
            b = free[0]
        b.set("Team", t["name"])
        w.subject = f"plan({b.name()}): give to {t['name']}"
        w.quiet = {t["name"]}  # greeted below, once its bolt's worktree exists
        seen["bolt"] = b.name()
        return [b.name()]
    seen = {}
    sha = write(fleet, label, change, "plan: give a bolt")
    b = seen["bolt"]
    path = f"{t['kit']['dir']}/bolts/{b}"
    make_place(fleet, t, path, f"bolt/{b}", base)
    print(f"{t['name']} holds {b}: bolt/{b} at {path} on {t['machine']}")
    record.emit(label, "bolt.give", [f"bolt/{b}", f"team/{t['name']}"], commit=[f"{repo}@{sha}"], why=f"plan({b}): give to {t['name']}",
                eid=CONTEXT["eid"])
    # A team takes a bolt only once its last one has landed or been dropped, so nothing is in flight: a conductor
    # or ops that is up starts again in the new bolt's worktree, with fresh context, before the conductor is greeted.
    up = [r for r in ("conductor", "ops") if crew.agent_status(fleet, f"{t['name']}-{r}")]
    if up:
        r = crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], "restart", t["name"], *up, "--no-greet"))
        said = (r.stdout + r.stderr).strip()
        if said:
            print(said)
    crew.greet(fleet, t["name"], first=f"Your team now holds the bolt {b}. ", wait=90 if "conductor" in up else 0)


def bolt_land(fleet, a):
    label, repo, tip, plan = locate(fleet, "Bolt", a.bolt, default_label(fleet, a))
    b = plan.bolt(a.bolt)
    t = fleet["teams"].get(b.get("Team")) or fail(f"bolt {a.bolt} is held by no team, so it has not been built")
    st = stages_for(fleet, plan, [b])
    units = [u.name() for u in plan.units_of(a.bolt)]
    for u in units:
        s = st.of(u)
        s["stage"] != "unknown" or fail(f"cannot tell whether unit {u} has landed: {s.get('why')}")
        s["stage"] == "landed" or fail(f"unit {u} has not landed on main: it is {s['stage']}")
    # A bolt landed on a main that lags GitHub's can't be pushed without force, and force would erase what it lacks.
    gap = host_run(fleet, t["machine"], BEHIND, t["kit"]["main"]).split()
    if gap and int(gap[1]):
        commits = lambda k: f"{k} commit" + ("" if k == "1" else "s")
        fail(f"{t['kit']['name']}'s main on {t['machine']} is {commits(gap[1])} behind GitHub's (with {gap[0]} of its own): "
             f"rebase it onto origin/main, check it again, then land; never push it with force")

    def change(w):
        w.bolt(a.bolt)
        late = [u.name() for u in w.plan.units_of(a.bolt) if u.name() not in units]
        not late or fail(f"unit {late[0]} was added to {a.bolt} since it was checked; it has not landed")
        for u in w.plan.units_of(a.bolt):
            w.plan.remove(u)
            w.on.append(f"unit/{u.name()}")
        w.plan.remove(w.plan.bolt(a.bolt))
        return [a.bolt]
    write(fleet, label, change, f"plan({a.bolt}): land the bolt", act="bolt.land", on=[f"bolt/{a.bolt}"])
    print(f"{a.bolt} has landed and {t['name']} holds no bolt")
    tidy_after(fleet, t, f"bolt {a.bolt}")


# ---------------------------------------------------------------------------------------------------- units

def group_of(u):
    """Where a unit is, as an object: its bolt, or its kit's queue."""
    return f"bolt/{u.get('Bolt')}" if u.get("Bolt") else f"queue/{u.get('Repo')}"


def unit_stage(fleet, plan, name):
    u = plan.unit(name)
    b = plan.bolt(u.get("Bolt")) if u.get("Bolt") else None
    return (stages_for(fleet, plan, [b]) if b else Stages(fleet, plan, {})).of(name)


REBASE = r"""cd "$1" || exit 1
orig=$(git rev-parse HEAD)
if git rebase -q --onto "bolt/$3" "bolt/$2" "unit/$4" >/dev/null 2>&1; then
  git branch -q --set-upstream-to="bolt/$3" "unit/$4"; echo "$orig"
else
  git rebase --abort >/dev/null 2>&1; exit 3
fi
"""
UNREBASE = r"""cd "$1" && git reset -q --hard "$2" && git branch -q --set-upstream-to="bolt/$3" "unit/$4" """


# The approval commit, printed as "made <sha>"; or, given the head an amended unit's construct started from, the
# approval already made since then, as "found <sha>", so an approval whose plan write failed only clears the mark.
APPROVE = r"""cd "$1" || exit 1
if [ -n "$3" ]; then
  had=$(git log --format='%H %(trailers:key=Reviewed-by,valueonly,separator=%x2C)' "$3..HEAD" 2>/dev/null | awk 'NF > 1 {print $1; exit}')
  if [ -n "$had" ]; then echo "found $had"; exit 0; fi
fi
git commit -q --allow-empty -m "review($2): approved" --trailer "Reviewed-by: $(git config user.name) <$(git config user.email)>"
echo "made $(git rev-parse HEAD)"
"""


def unit_approve(fleet, a):
    """crew unit approve <unit>: the user's review, an empty Reviewed-by commit on unit/<unit>. A unit marked amended
    has its mark cleared in the plan as well, after which its stage is read from its tasks again."""
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))
    s = unit_stage(fleet, plan, a.unit)
    u = plan.unit(a.unit)
    mark, bolt = u.get("Amended"), u.get("Bolt")
    if s["stage"] == "approved":
        print(f"unit {a.unit} is already approved")
        return
    s["stage"] == "review" or fail(f"unit {a.unit} is in {s['stage']}: " + (
        "construct has not been run again since it was amended" if s["stage"] == "amended" else
        "its change is being written again, and has not been committed" if s["stage"] == "construct" and mark else
        "its change's planning is not complete" if s["stage"] == "construct" else
        "it has no change to review yet" if s["stage"] in ("ready", "waiting", "queued") else
        s.get("why", "it is past review")))
    t = fleet["teams"][plan.bolt(bolt).get("Team")]
    made, sha = host_run(fleet, t["machine"], APPROVE, s["worktree"], a.unit, mark or "").split()
    print(f"unit {a.unit} approved: {sha[:7]} on unit/{a.unit}" if made == "made" else
          f"unit {a.unit} was approved at {sha[:7]} on unit/{a.unit}, after construct ran again")
    commits, eid = [f"{t['kit']['repo']}@{sha}"], None
    if mark:
        def change(w):
            u = w.unit(a.unit)
            u.get("Amended") == mark or fail(f"unit {a.unit} was sent back to construct again since it was read: approve it "
                                             "once its change is in review")
            u.drop("Amended")
            return [bolt]
        commits.append(f"{repo}@{write(fleet, label, change, f'plan({bolt}): {a.unit} approved after amendment')}")
        eid = CONTEXT["eid"]
    record.emit(label, "unit.approve", [f"unit/{a.unit}"], commit=commits, why=f"review({a.unit}): approved", eid=eid)


# ------------------------------------------------------------------------------------------ who writes what

# The commands that write the plan directly, and the one role each agent crew started may use them in.
PLAN_WRITES = {("bolt", "new"), ("bolt", "give"), ("bolt", "order"), ("bolt", "drop"), ("bolt", "land"), ("unit", "add"),
               ("unit", "split"), ("unit", "amend"), ("unit", "order"), ("unit", "after"), ("unit", "move"), ("unit", "drop")}


def role(fleet, name):
    """What an agent crew started is, from its name alone: (kind, its partition's label or its team), or ("user", None)
    for no agent at all, or for the user's <user>@<host>, which a command run again on a team's host carries."""
    if not name or "@" in name:
        return "user", None
    for label in fleet["partitions"]:
        for kind, n in (("planner", f"{label}-planner"), ("design", f"{label}-design"), ("main-ops", f"{label}-ops")):
            if name == n:
                return kind, label
        if name.startswith(f"{label}-dispatch-"):
            return "dispatcher", label
        if name.startswith(f"{label}-operator-"):
            return "operator", label
    for t in fleet["teams"]:
        if name == f"{t}-conductor":
            return "conductor", t
        if name == f"{t}-ops" or re.fullmatch(rf"{re.escape(t)}-unit-[1-9][0-9]*", name):
            return "team", t
    return "other", None


def planner_of(fleet, kind, of):
    label = fleet["teams"][of]["label"] if kind in ("conductor", "team") else of
    return f"{label}-planner" if label in fleet["partitions"] else "the partition's planner"


def may_write(fleet, key, a):
    """Who writes the plan directly. The user writes everything. The planner changes it only by a proposal; a
    conductor narrows, orders and sets dependencies within the bolt its team holds (checked once its unit is found),
    and marks a unit of it amended by running construct again (run_check); the design agent queues; a dispatcher
    gives bolts; the main level's ops lands them. Any other plan write by an agent crew started is refused, naming
    the planner."""
    name = os.environ.get("CREW_AGENT")
    if key not in PLAN_WRITES or not name:
        return
    kind, of = role(fleet, name)
    cmd = " ".join(key)
    if kind == "planner":
        fail(f"the planner changes the plan through a proposal: crew plan propose, not crew {cmd}")
    if ((kind == "conductor" and key in (("unit", "split"), ("unit", "order"), ("unit", "after")))
            or (kind == "design" and key == ("unit", "add") and not a.bolt)
            or (kind == "dispatcher" and key == ("bolt", "give")) or (kind == "main-ops" and key == ("bolt", "land"))):
        return
    fail(f"{name} does not write the plan with crew {cmd}" + (" --bolt" if key == ("unit", "add") and a.bolt else "")
         + f": tell {planner_of(fleet, kind, of)}, who proposes it")


# ----------------------------------------------------------------------------------- plan commands, as ops

class Op:
    """One plan command, split so a proposal can check it without writing and an approval can apply several in one
    commit. It is built against a plan, and building it runs its checks, those that read the kits included. It holds
    its change to a Write (which checks again on each replay and returns the bolts whose conductors hear the write),
    the subject and run-record entry of its write, what to prepare before the push with its undo (a unit's rebase),
    and what follows the push."""

    def __init__(self, label, change, subject, act, on=(), frm=(), body="", prepare=None, after=None):
        self.label, self.change, self.subject, self.act, self.body = label, change, subject, act, body
        self.on, self.frm = list(on), list(frm)
        self.prepare, self.after = prepare, after
        self.added_on, self.added_frm = [], []


class Direct:
    """What a command run directly sees: the plans of every partition, or of --label (or the agent's own)."""
    direct = True

    def __init__(self, fleet, a):
        self.fleet, self.label = fleet, default_label(fleet, a)

    def locate(self, kind, name):
        label, _, _, plan = locate(self.fleet, kind, name, self.label)
        return label, plan

    def kit(self, kit):
        return plan_for(self.fleet, kit, self.label)[0]


class Proposed:
    """What a command inside a proposal sees: the proposal's partition and number, in the plan as the commands before
    it in the proposal have left it."""
    direct = False

    def __init__(self, fleet, label, w, n):
        self.fleet, self.label, self.w, self.n = fleet, label, w, n

    def locate(self, kind, name):
        (self.w.plan.bolt(name) if kind == "Bolt" else self.w.plan.unit(name)) or self.w.gone(kind, name)
        return self.label, self.w.plan

    def kit(self, kit):
        return plan_for(self.fleet, kit, self.label)[0]


def first_open(fleet, plan, bolt):
    """The first unit of a held bolt that has not merged into it: where work the bolt needs to land goes, ahead of
    what waits on it. None when every unit has merged, or the bolt has none."""
    b = plan.bolt(bolt)
    st = stages_for(fleet, plan, [b])
    return next((u.name() for u in plan.units_of(bolt) if st.of(u.name())["stage"] not in ("merged", "landed")), None)


def unblocking(ctx, plan, label, a, into):
    """--unblocks <bolt>: the unit is work a bolt a team holds needs before it can be proven or land. It goes into that
    bolt, ahead of what waits on it, never into the queue or another bolt. Returns the unit it goes ahead of."""
    into == a.unblocks or fail(f"{a.unit} unblocks bolt {a.unblocks}, so it goes into that bolt, ahead of what waits on it, "
                               f"not into {f'bolt {into}' if into else 'the queue'}")
    plan.bolt(a.unblocks).get("Team") or fail(f"{a.unit} unblocks bolt {a.unblocks}, which no team holds, so nothing waits on "
                                              "it: --unblocks names a bolt in flight")
    return first_open(ctx.fleet, plan, a.unblocks)


def op_bolt_new(ctx, a):
    label = ctx.kit(a.repo)
    crew.NAME.match(a.bolt) or fail(f"a bolt's name is lowercase words with dashes, not {a.bolt}")

    def change(w):
        w.plan.bolt(a.bolt) is None or fail(f"{label}/main already has bolt {a.bolt}")
        r = Rec("Bolt", [("Bolt", a.bolt), ("Repo", a.repo), ("Goal", a.goal)] + [("Source", x) for x in a.source])
        w.plan.insert(r, before=w.bolt(a.before) if a.before else None)
        return [a.bolt]
    return Op(label, change, f"plan({a.bolt}): add the bolt", "bolt.new", on=[f"bolt/{a.bolt}"])


def op_bolt_order(ctx, a):
    label, _ = ctx.locate("Bolt", a.bolt)

    def change(w):
        b, bolts = w.bolt(a.bolt), w.plan.bolts()
        if a.first:
            w.plan.insert(b, before=bolts[0]) if bolts[0] is not b else None
        elif a.last:
            w.plan.insert(b, after=bolts[-1]) if bolts[-1] is not b else None
        else:
            o = w.bolt(a.before)
            o is not b or fail("a bolt can't go before itself")
            w.plan.insert(b, before=o)
        return [a.bolt]
    where = "first" if a.first else "last" if a.last else f"before {a.before}"
    return Op(label, change, f"plan({a.bolt}): order the bolt {where}", "bolt.order", on=[f"bolt/{a.bolt}"])


def op_bolt_drop(ctx, a):
    label, plan = ctx.locate("Bolt", a.bolt)
    team = ctx.fleet["teams"].get(plan.bolt(a.bolt).get("Team"))
    if a.requeue and team:  # a queued unit has no worktree
        st = stages_for(ctx.fleet, plan, [plan.bolt(a.bolt)])
        for u in plan.units_of(a.bolt):
            s = st.of(u.name())
            s["stage"] != "unknown" or fail(f"cannot tell unit {u.name()}'s stage: {s.get('why')}")
            not s["worktree"] or fail(f"unit {u.name()} has a worktree at {s['worktree']}, and a queued unit has none")

    def change(w):
        b = w.bolt(a.bolt)
        for u in w.plan.units_of(a.bolt):
            if a.requeue:
                u.drop("Bolt")
                u.drop("After")
                w.plan.place_last(u)
            else:
                w.plan.remove(u)
                w.on.append(f"unit/{u.name()}")
        w.plan.remove(b)
        return [a.bolt]

    def after(repo, sha):
        if team:
            tidy_after(ctx.fleet, team, f"bolt {a.bolt}")
    return Op(label, change, f"plan({a.bolt}): drop the bolt" + (", its units queued" if a.requeue else ""), "bolt.drop",
              on=[f"bolt/{a.bolt}"], body=a.reason, after=after)


def op_unit_add(ctx, a):
    label = ctx.label
    if a.bolt:
        label, plan = ctx.locate("Bolt", a.bolt)
        kit = plan.bolt(a.bolt).get("Repo")
        a.repo in (None, kit) or fail(f"bolt {a.bolt} is in {kit}, not {a.repo}")
    else:
        a.repo or fail("a unit goes in a bolt (--bolt) or in a repo's queue (--repo)")
        label, kit, plan = ctx.kit(a.repo), a.repo, None
    ahead = unblocking(ctx, plan, label, a, a.bolt) if getattr(a, "unblocks", None) else None
    name_free(ctx.fleet, label, kit, [a.unit])
    sources = list(a.source)
    if a.signal:
        sources.insert(0, f"signals/{a.signal}")

    def change(w):
        w.plan.unit(a.unit) is None or fail(f"{label}/main already has unit {a.unit}")
        if a.bolt:
            w.bolt(a.bolt)
        if a.signal:  # its one move, route, in the same commit, checked again on each replay
            move(ctx.fleet, label, w, a.signal, route_move(a.signal, a.unit))
        r = Rec("Unit", [("Unit", a.unit), ("Repo", kit)] + ([("Bolt", a.bolt)] if a.bolt else []) + [("Intent", a.intent)]
                + [("After", x) for x in a.after] + [("Source", x) for x in sources])
        before = a.before or ahead
        o = w.plan.unit(before) if before else None
        if a.before:
            o = w.unit(a.before)
            o.get("Bolt") == a.bolt and o.get("Repo") == kit or fail(f"unit {a.before} is not in {a.bolt or 'the queue of ' + kit}")
        if o is not None:
            w.plan.insert(r, before=o)
        else:
            w.plan.place_last(r)
        return [a.bolt] if a.bolt else []

    def after(repo, sha):
        if a.signal:
            print(f"signal {a.signal} routed to unit/{a.unit}, in the same commit")
            record.emit(label, "signal.move", [f"signals/{a.signal}", f"unit/{a.unit}"], commit=[f"{repo}@{sha}"],
                        why=f"signals({a.signal}): route to unit/{a.unit}")
    return Op(label, change, f"plan({a.bolt or 'queue'}): add {a.unit}", "unit.add",
              on=[f"unit/{a.unit}", f"bolt/{a.bolt}" if a.bolt else f"queue/{kit}"], frm=[f"signals/{a.signal}"] if a.signal else [], after=after)


def conductor_scope(ctx, plan, a):
    """A conductor narrows, orders and sets dependencies only within the bolt its team holds."""
    kind, team = role(ctx.fleet, os.environ.get("CREW_AGENT"))
    if ctx.direct and kind == "conductor":
        b = plan.unit(a.unit).get("Bolt")
        b and plan.bolt(b).get("Team") == team or fail(
            f"{team}-conductor writes only units of the bolt {team} holds, and {a.unit} is in {f'bolt {b}' if b else 'the queue'}: "
            f"tell {ctx.fleet['teams'][team]['label']}-planner")


def op_unit_split(ctx, a):
    label, plan = ctx.locate("Unit", a.unit)
    conductor_scope(ctx, plan, a)
    s = unit_stage(ctx.fleet, plan, a.unit)
    s["stage"] not in LATER or fail(f"unit {a.unit} is in {s['stage']}, so it is no longer split; add the remainder as a new unit instead (crew unit add)")
    s["stage"] != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    name_free(ctx.fleet, label, plan.unit(a.unit).get("Repo"), [n for n, _ in a.into])
    bolt = plan.unit(a.unit).get("Bolt")

    def change(w):
        u = w.unit(a.unit)
        u.set("Intent", a.intent)
        prev = u
        for n, intent in a.into:
            w.plan.unit(n) is None or fail(f"{label}/main already has unit {n}")
            r = Rec("Unit", [("Unit", n), ("Repo", u.get("Repo"))] + ([("Bolt", u.get("Bolt"))] if u.get("Bolt") else [])
                    + [("Intent", intent)] + [("Source", x) for x in u.all("Source")])
            w.plan.insert(r, after=prev)
            prev = r
        return [u.get("Bolt")] if u.get("Bolt") else []
    return Op(label, change, f"plan({bolt or 'queue'}): split {a.unit} into " + ", ".join(n for n, _ in a.into), "unit.split",
              on=[f"unit/{a.unit}"] + [f"unit/{n}" for n, _ in a.into], frm=[f"unit/{a.unit}"])


def op_unit_amend(ctx, a):
    """A unit's intent replaced. One that has a worktree has a change written for the old intent, so it is marked
    amended, proposal/<n> inside an approval and intent when the user runs it, and its conductor is told to run
    construct again. Merged work is not amended."""
    label, plan = ctx.locate("Unit", a.unit)
    s = unit_stage(ctx.fleet, plan, a.unit)
    s["stage"] not in ("merged", "landed") or fail(
        f"unit {a.unit} has " + ("merged into its bolt" if s["stage"] == "merged" else "landed on main")
        + ", so it is not amended: a defect in it is a fix, and new work is a new unit")
    s["stage"] != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    bolt = plan.unit(a.unit).get("Bolt")
    team = ctx.fleet["teams"].get(plan.bolt(bolt).get("Team")) if bolt else None
    mark = (f"proposal/{ctx.n}" if not ctx.direct else "intent") if s["worktree"] else None

    def change(w):
        u = w.unit(a.unit)
        u.set("Intent", a.intent)
        if mark:
            u.set("Amended", mark)
            if team:
                w.quiet.add(team["name"])  # told below what to do, rather than the write's subject
        return [bolt] if bolt else []

    def after(repo, sha):
        if not (mark and team):
            return
        by = f"proposal {ctx.n}" if not ctx.direct else "the user"
        if not crew.tell(ctx.fleet, f"{team['name']}-conductor", f"Unit {a.unit}'s intent was amended by {by}. Run construct again "
                         f"(crew unit run {a.unit} construct); it returns to the user's review."):
            print(f"{team['name']}-conductor is not up: unit {a.unit} waits, amended, for construct to be run again")
    return Op(label, change, f"plan({bolt or 'queue'}): amend {a.unit}", "unit.amend", on=[f"unit/{a.unit}"], after=after)


def op_unit_order(ctx, a):
    label, plan = ctx.locate("Unit", a.unit)
    conductor_scope(ctx, plan, a)
    u0 = plan.unit(a.unit)

    def change(w):
        u = w.unit(a.unit)
        g = w.plan.group(u)
        if a.first:
            w.plan.insert(u, before=g[0]) if g[0] is not u else None
        elif a.last:
            w.plan.insert(u, after=g[-1]) if g[-1] is not u else None
        else:
            o = w.unit(a.before)
            o is not u or fail("a unit can't go before itself")
            o in g or fail(f"unit {a.before} is not in {u.get('Bolt') or 'the queue'} with {a.unit}")
            w.plan.insert(u, before=o)
        return [u.get("Bolt")] if u.get("Bolt") else []
    where = "first" if a.first else "last" if a.last else f"before {a.before}"
    return Op(label, change, f"plan({u0.get('Bolt') or 'queue'}): order {a.unit} {where}", "unit.order",
              on=[f"unit/{a.unit}", group_of(u0)])


def op_unit_after(ctx, a):
    label, plan = ctx.locate("Unit", a.unit)
    conductor_scope(ctx, plan, a)
    a.none or a.deps or fail("name the units it comes after, or --none")
    u0 = plan.unit(a.unit)

    def change(w):
        u = w.unit(a.unit)
        if a.none:
            u.drop("After")
        for d in a.deps:
            w.unit(d)
            d != a.unit or fail("a unit can't come after itself")
            if d not in u.all("After"):
                u.add("After", d, after="Intent")
        return [u.get("Bolt")] if u.get("Bolt") else []
    what = "after nothing" if a.none else "after " + ", ".join(a.deps)
    return Op(label, change, f"plan({u0.get('Bolt') or 'queue'}): {a.unit} {what}", "unit.after",
              on=[f"unit/{a.unit}", group_of(u0)])


def op_unit_move(ctx, a):
    label, plan = ctx.locate("Unit", a.unit)
    u = plan.unit(a.unit)
    src, to = u.get("Bolt"), None if a.bolt == "queue" else a.bolt
    to != src or fail(f"unit {a.unit} is already in {src or 'the queue'}")
    if to:
        tb = plan.bolt(to) or fail(f"no bolt {to} in {label}/main of {state_of(ctx.fleet, label)[0]}")
        tb.get("Repo") == u.get("Repo") or fail(f"bolt {to} is in {tb.get('Repo')}; a unit moves only between bolts of its own repo, {u.get('Repo')}")
    ahead = unblocking(ctx, plan, label, a, to) if getattr(a, "unblocks", None) else None
    s = unit_stage(ctx.fleet, plan, a.unit)
    s["stage"] not in ("merged", "landed") or fail(f"unit {a.unit} has merged into {src}, so it can't move")
    s["stage"] != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    prepare = None
    if s["worktree"]:
        to or fail(f"unit {a.unit} has a worktree at {s['worktree']}, and a queued unit has none")
        ft, tt = ctx.fleet["teams"][plan.bolt(src).get("Team")], ctx.fleet["teams"].get(plan.bolt(to).get("Team"))
        tt or fail(f"bolt {to} is held by no team, so it has no branch to rebase {a.unit} onto")
        (ft["machine"], ft["kit"]["main"]) == (tt["machine"], tt["kit"]["main"]) or fail(
            f"bolt {to} is built in {tt['kit']['main']} on {tt['machine']}, not in {a.unit}'s checkout; a unit with a worktree moves only within it")

        def prepare():
            r = crew.on_machine(ctx.fleet, ft["machine"], ["bash", "-c", REBASE, "crew", s["worktree"], src, to, a.unit])
            r.returncode != 3 or fail(f"rebasing {a.unit} onto bolt/{to} conflicts: the move is abandoned and the plan is unchanged")
            r.returncode == 0 or fail(f"rebasing {a.unit} on {ft['machine']} failed: {r.stderr.strip()}")
            orig = r.stdout.strip()
            return lambda: crew.on_machine(ctx.fleet, ft["machine"], ["bash", "-c", UNREBASE, "crew", s["worktree"], orig, src, a.unit])

    def change(w):
        u = w.unit(a.unit)
        u.get("Bolt") == src or fail(f"unit {a.unit} moved to {u.get('Bolt') or 'the queue'} meanwhile")
        u.drop("After")
        if to:
            w.bolt(to)
            u.set("Bolt", to, after="Repo")
        else:
            u.drop("Bolt")
        o = w.plan.unit(ahead) if ahead else None
        if o is not None and o is not u and o.get("Bolt") == to:
            w.plan.insert(u, before=o)
        else:
            w.plan.place_last(u)
        return [b for b in (src, to) if b]
    kit = u.get("Repo")
    return Op(label, change, f"plan({to or 'queue'}): move {a.unit} from {src or 'the queue'}", "unit.move",
              on=[f"unit/{a.unit}", f"bolt/{to}" if to else f"queue/{kit}"], frm=[f"bolt/{src}" if src else f"queue/{kit}"], prepare=prepare)


def op_unit_drop(ctx, a):
    label, plan = ctx.locate("Unit", a.unit)
    s = unit_stage(ctx.fleet, plan, a.unit)
    s["stage"] not in ("merged", "landed") or fail(f"unit {a.unit} has merged into its bolt, so it can't be dropped")
    s["stage"] != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    u0 = plan.unit(a.unit)
    bolt = u0.get("Bolt")
    team = ctx.fleet["teams"].get(plan.bolt(bolt).get("Team")) if bolt else None

    def change(w):
        u = w.unit(a.unit)
        for o in w.plan.group(u):
            if a.unit in o.all("After"):
                o.fields = [(n, v) for n, v in o.fields if not (n == "After" and v == a.unit)]
        w.plan.remove(u)
        return [bolt] if bolt else []

    def after(repo, sha):
        if team:
            tidy_after(ctx.fleet, team, f"unit {a.unit}")
        elif s["worktree"]:
            print(f"its worktree stays at {s['worktree']}, on unit/{a.unit}")
    return Op(label, change, f"plan({bolt or 'queue'}): drop {a.unit}", "unit.drop", on=[f"unit/{a.unit}", group_of(u0)],
              body=a.reason, after=after)


# The ten commands a proposal may hold, each built the same way whether run directly or inside a proposal.
OPS = {
    ("bolt", "new"): op_bolt_new, ("bolt", "order"): op_bolt_order, ("bolt", "drop"): op_bolt_drop,
    ("unit", "add"): op_unit_add, ("unit", "split"): op_unit_split, ("unit", "amend"): op_unit_amend, ("unit", "order"): op_unit_order,
    ("unit", "after"): op_unit_after, ("unit", "move"): op_unit_move, ("unit", "drop"): op_unit_drop,
}


def direct(key):
    """A plan command run directly: built (its checks), prepared, written, and what follows done, as one write."""
    def run(fleet, a):
        op = OPS[key](Direct(fleet, a), a)
        undo = op.prepare() if op.prepare else None
        try:
            sha = write(fleet, op.label, op.change, op.subject, op.body, act=op.act, on=op.on, frm=op.frm)
        except Refusal:
            if undo:
                undo()
            raise
        if op.after:
            op.after(state_of(fleet, op.label)[0], sha)
    return run


# --------------------------------------------------------------------------------------------- proposals

PROPOSALS = """\
# The planner's proposals: each change it would make to the plan, waiting for the user's approval. Written only
# through crew plan. A proposal is never removed, its commands never change, and its number is never reused.

%rec: Proposal
%doc: A case, and the plan commands it would run in order (Do), as typed without the leading crew.
%key: Proposal
%type: Proposal,Replaces int
%type: State enum open approved dropped
%type: Opened,Closed date
%mandatory: Proposal Case Do State Opened By
%allowed: Proposal Case Do Agreed State Opened By Closed Reason Replaces
"""
# The commands a proposal may hold.
PROPOSABLE = tuple(OPS)


class Strict(argparse.ArgumentParser):
    """crew's own parser, refusing instead of exiting: a proposal's Do is read by the same grammar as the command line."""

    def error(self, message):
        fail(message)


def do_args(label, do):
    """A proposal's Do as crew's parser reads it: one of the ten plan commands, in the proposal's partition."""
    try:
        argv = shlex.split(do)
    except ValueError as e:
        fail(f"`{do}`: {e}")
    argv = argv[1:] if argv[:1] == ["crew"] else argv
    tuple(argv[:2]) in PROPOSABLE or fail(f"a proposal holds only the plan's commands ("
                                          + ", ".join(" ".join(k) for k in PROPOSABLE) + f"), not `{do}`")
    try:
        a = parser(Strict).parse_args(argv)
    except Refusal as e:
        fail(f"`{do}`: {e}")
    getattr(a, "label", None) in (None, label) or fail(f"`{do}` names partition {a.label}, and the proposal is {label}'s")
    a.label, a.do = label, do
    return a


def proposals(w):
    """proposals.rec of the flywheel as the write has it, or a new one when the branch has none yet."""
    text = w.text("proposals.rec")
    return Plan(text if text is not None else PROPOSALS)


def proposal(pl, n, label):
    return next((p for p in pl.recs("Proposal") if p.get("Proposal") == str(n)), None) or fail(
        f"no proposal {n} in {label}/main")


def objects(argvs):
    """Every bolt and unit a proposal's commands name, as run-record objects, in order and once each."""
    out = []
    for a in argvs:
        key = (a.cmd, a.sub)
        if a.cmd == "bolt":
            out.append(f"bolt/{a.bolt}")
        else:
            out.append(f"unit/{a.unit}")
            out += [f"unit/{n}" for n, _ in getattr(a, "into", None) or []]
            if key == ("unit", "add") and a.bolt:
                out.append(f"bolt/{a.bolt}")
            if key == ("unit", "move") and a.bolt != "queue":
                out.append(f"bolt/{a.bolt}")
    return list(dict.fromkeys(out))


def summary(argvs):
    """A proposal's changes in a few words that name things and quote nothing anyone typed, for its subjects."""
    words = {("bolt", "new"): lambda a: f"new bolt {a.bolt}", ("bolt", "order"): lambda a: f"order bolt {a.bolt}",
             ("bolt", "drop"): lambda a: f"drop bolt {a.bolt}",
             ("unit", "add"): lambda a: f"add {a.unit} to " + (a.bolt or f"the {a.repo} queue"),
             ("unit", "split"): lambda a: f"split {a.unit}", ("unit", "amend"): lambda a: f"amend {a.unit}",
             ("unit", "order"): lambda a: f"order {a.unit}",
             ("unit", "after"): lambda a: f"set what {a.unit} comes after",
             ("unit", "move"): lambda a: f"move {a.unit} to " + ("the queue" if a.bolt == "queue" else a.bolt),
             ("unit", "drop"): lambda a: f"drop {a.unit}"}
    return ", ".join(words[(a.cmd, a.sub)](a) for a in argvs)


def touched_by(plan, argvs):
    """The bolts each of a proposal's commands touches, read from the plan and the commands alone (no kit is read): a
    unit add's bolt; the bolt a unit leaves and the one it joins; the bolt of a unit split, ordered, given what it
    comes after, amended or dropped; the bolt of a bolt order or drop. A bolt new touches none."""
    where = {u.name(): u.get("Bolt") for u in plan.units()}
    out = []
    for a in argvs:
        key, t = (a.cmd, a.sub), []
        if key in (("bolt", "order"), ("bolt", "drop")):
            t = [a.bolt]
            for u in [u for u, b in where.items() if b == a.bolt]:
                if a.sub == "drop":
                    where[u] = None
        elif key == ("unit", "add"):
            t, where[a.unit] = [a.bolt], a.bolt
        elif key == ("unit", "move"):
            to = None if a.bolt == "queue" else a.bolt
            t, where[a.unit] = [where.get(a.unit), to], to
        elif key[0] == "unit":
            t = [where.get(a.unit)]
            for n, _ in getattr(a, "into", None) or []:
                where[n] = where.get(a.unit)
            if a.sub == "drop":
                where.pop(a.unit, None)
        out.append([b for b in t if b])
    return out


def held_teams(plan, bolts):
    """The teams holding, in a plan, any of the given bolts: their conductors agree to a proposal that touches them."""
    return sorted({plan.bolt(b).get("Team") for b in bolts if plan.bolt(b) and plan.bolt(b).get("Team")})


def flat(lists):
    return list(dict.fromkeys(x for l in lists for x in l))


def apply_all(fleet, label, w, argvs, n):
    """Proposal n's commands built and applied in order to the write's plan, each checked against the plan as the ones
    before it left it. Returns the ops, each with the objects its change added, and the bolts whose conductors hear
    the write."""
    ctx, ops, told = Proposed(fleet, label, w, n), [], []
    for a in argvs:
        try:
            op = OPS[(a.cmd, a.sub)](ctx, a)
            n_on, n_frm = len(w.on), len(w.frm)
            told += op.change(w) or []
        except Refusal as e:
            fail(f"`{a.do}`: {e}")
        op.added_on, op.added_frm = w.on[n_on:], w.frm[n_frm:]
        ops.append(op)
    return ops, list(dict.fromkeys(told))


def check_ops(fleet, label, w, argvs, n):
    """Proposal n's commands applied in order to a copy of the plan and of the files they change, then thrown away:
    every refusal and rule each has when run directly, the schema's and crew's own rules included."""
    scratch = Write(w.repo, label, w.tip, Plan(w.plan.text()))
    scratch.files = dict(w.files)
    for a in argvs:
        try:
            OPS[(a.cmd, a.sub)](Proposed(fleet, label, scratch, n), a).change(scratch)
        except Refusal as e:
            fail(f"`{a.do}`: {e}")
    try:
        check(scratch.plan)
        recfix(scratch.plan.text(), "plan.rec")
        for path, text in scratch.files.items():
            recfix(text, path)
    except Refusal as e:
        fail(f"the proposal as a whole: {e}")


def read_proposal_file(path):
    """The planner's proposal file: one record of a Case and its Do lines, and nothing else."""
    try:
        text = pathlib.Path(path).read_text()
    except OSError as e:
        fail(f"cannot read {path}: {e.strerror}")
    recs = [p for p in Plan(text).paras if isinstance(p, Rec)]
    len(recs) == 1 or fail(f"{path} holds {len(recs)} records: a proposal file is one record of a Case and its Do lines")
    r = recs[0]
    other = sorted({n for n, _ in r.fields if n not in ("Case", "Do", "#")})
    not other or fail(f"{path} has fields a proposal file doesn't: " + ", ".join(other) + "; only Case and Do")
    len(r.all("Case")) == 1 and r.get("Case").strip() or fail(f"{path} needs one Case: why these changes")
    r.all("Do") or fail(f"{path} has no Do: the plan commands the proposal would run, in order")
    return r.get("Case").strip(), r.all("Do")


def proposal_label(fleet, a, n=None):
    """The partition a proposal command means: --label, the agent's own, the only partition, or, for a numbered
    proposal, the one partition whose branch has that number."""
    label = default_label(fleet, a)
    if label:
        return label
    if len(fleet["partitions"]) == 1:
        return next(iter(fleet["partitions"]))
    n is not None or fail("which partition's proposals? add --label " + "|".join(fleet["partitions"]))
    hits = []
    for l in fleet["partitions"]:
        repo, ref = state_of(fleet, l)
        tip = fetch(repo, ref)
        text = show(repo, tip, "proposals.rec") if tip else None
        if text and any(p.get("Proposal") == str(n) for p in Plan(text).recs("Proposal")):
            hits.append(l)
    len(hits) == 1 or fail(f"proposal {n} is in " + (", ".join(hits) or "no partition's proposals") + ": add --label")
    CONTEXT["label"] = hits[0]
    return hits[0]


def at_tip(fleet, label, n):
    """The flywheel's branch at its tip, with proposal n: (repo, tip, plan, proposals, the proposal, its commands)."""
    repo, ref = state_of(fleet, label)
    tip = fetch(repo, ref) or fail(f"{repo} has no {ref} yet: crew state init {label}")
    w = Write(repo, label, tip, read(repo, ref, tip))
    pl = proposals(w)
    p = proposal(pl, n, label)
    return w, pl, p, [do_args(label, d) for d in p.all("Do")]


def tell_planner(fleet, label, text):
    planner = f"{label}-planner"
    if agent() != planner:
        crew.tell(fleet, planner, text)


def plan_propose(fleet, a):
    """crew plan propose <file> [--replaces <n>]: the planner's proposal, checked against the plan at the tip, written
    open with the next number; the conductor of each bolt in flight it touches is told."""
    kind, of = role(fleet, os.environ.get("CREW_AGENT"))
    kind in ("planner", "user") or fail(f"{os.environ.get('CREW_AGENT')} does not write proposals: tell "
                                        f"{planner_of(fleet, kind, of)}, who proposes changes to the plan")
    label = of if kind == "planner" else proposal_label(fleet, a)
    a.label in (None, label) or fail(f"{label}-planner proposes for {label}, not {a.label}")
    CONTEXT["label"] = label
    case, dos = read_proposal_file(a.file)
    argvs = [do_args(label, d) for d in dos]
    seen = {}

    def change(w):
        pl = proposals(w)
        n = 1 + max([int(p.get("Proposal")) for p in pl.recs("Proposal")] or [0])
        check_ops(fleet, label, w, argvs, n)
        per = touched_by(w.plan, argvs)
        today = datetime.date.today().isoformat()
        if a.replaces:
            old = proposal(pl, a.replaces, label)
            old.get("State") == "open" or fail(f"proposal {a.replaces} is {old.get('State')}, so nothing replaces it")
            old.set("State", "dropped")
            old.set("Closed", today, after="By")
            old.set("Reason", f"replaced by proposal {n}", after="Closed")
        pl.insert(Rec("Proposal", [("Proposal", str(n)), ("Case", case)] + [("Do", d) for d in dos]
                      + [("State", "open"), ("Opened", today), ("By", agent())]
                      + ([("Replaces", str(a.replaces))] if a.replaces else [])))
        w.replace("proposals.rec", pl.text())
        w.subject = f"plan(proposal {n}): propose: {summary(argvs)}"
        w.on += [f"proposal/{n}"] + objects(argvs) + ([f"proposal/{a.replaces}"] if a.replaces else [])
        seen.update(n=n, per=per, held={b: w.plan.bolt(b).get("Team") for b in flat(per) if w.plan.bolt(b) and w.plan.bolt(b).get("Team")})
        return []
    write(fleet, label, change, "plan: propose", act="plan.propose")
    n, held = seen["n"], seen["held"]
    if a.replaces:
        print(f"proposal {a.replaces} is dropped, replaced by proposal {n}")
    teams = sorted(set(held.values()))
    for team in teams:
        cmds = "; ".join(d for d, t in zip(dos, seen["per"]) if any(held.get(b) == team for b in t))
        if not crew.tell(fleet, f"{team}-conductor", f"Proposal {n} would change your bolt: {cmds}. Read it with "
                         f"crew plan proposed {n} --label {label}. Agree with crew plan agree {n} --label {label}, "
                         f"or tell {label}-planner why not."):
            print(f"{team}-conductor is not up: proposal {n} is written and waits for its agreement")
    waits = [f"{t}-conductor" for t in teams] + ["the user"]
    print(f"proposal {n} is open, waiting on " + ", then ".join(waits) + f": crew plan proposed {n} --label {label}")


def plan_agree(fleet, a):
    """crew plan agree <n> [--team <team>]: the conductor's recorded agreement to a proposal that touches the bolt its
    team holds; the user may agree for any team the proposal touches."""
    label = proposal_label(fleet, a, a.n)
    CONTEXT["label"] = label
    name = os.environ.get("CREW_AGENT")
    kind, of = role(fleet, name)
    kind in ("conductor", "user") or fail(f"{name} does not agree to proposals: the conductor of a bolt a proposal "
                                          "touches agrees to it")
    w0, _, p0, argvs = at_tip(fleet, label, a.n)
    p0.get("State") == "open" or fail(f"proposal {a.n} is {p0.get('State')}, so there is nothing to agree to")

    def wanted(w, p):
        held = held_teams(w.plan, flat(touched_by(w.plan, argvs)))
        if kind == "conductor":
            of in held or fail(f"proposal {a.n} touches no bolt {of} holds" + (f": it touches the bolts of {', '.join(held)}" if held else ""))
            want = [of]
        else:
            a.team is None or a.team in held or fail(f"proposal {a.n} touches no bolt {a.team} holds")
            want = [a.team] if a.team else held
        return [t for t in want if t not in p.all("Agreed")]
    if not wanted(w0, p0):
        print(f"proposal {a.n} already has the agreement" + (f" of {of}" if kind == "conductor" else " of every team it touches"))
        return
    seen = {}

    def change(w):
        pl = proposals(w)
        p = proposal(pl, a.n, label)
        p.get("State") == "open" or fail(f"proposal {a.n} is {p.get('State')}, so there is nothing to agree to")
        new = wanted(w, p)
        for t in new:
            p.add("Agreed", t, after="Do")
        w.replace("proposals.rec", pl.text())
        w.subject = f"plan(proposal {a.n}): " + ", ".join(new) + " agree" + ("s" if len(new) == 1 else "")
        w.on += [f"proposal/{a.n}"] + [f"team/{t}" for t in new]
        seen["new"] = new
        return []
    write(fleet, label, change, "plan: agree", act="plan.agree")
    tell_planner(fleet, label, f"{', '.join(seen['new'])} agree{'s' if len(seen['new']) == 1 else ''} to proposal {a.n}.")


def plan_approve(fleet, a):
    """crew plan approve <n>: the proposal's commands applied in order to the plan at the tip, and the proposal closed
    as approved, in one commit; refused, with nothing changed, when a command no longer applies or a conductor whose
    bolt it touches has not agreed. A rebase it prepares is undone if the approval is refused."""
    label = proposal_label(fleet, a, a.n)
    CONTEXT["label"] = label
    w0, _, p0, argvs = at_tip(fleet, label, a.n)
    repo = w0.repo

    def agreed(w, p):
        missing = [t for t in held_teams(w.plan, flat(touched_by(w.plan, argvs))) if t not in p.all("Agreed")]
        not missing or fail(f"proposal {a.n} waits on the agreement of " + ", ".join(f"{t}-conductor" for t in missing)
                            + f": crew plan agree {a.n}")

    def opened(p):
        p.get("State") == "open" or fail(f"proposal {a.n} is {p.get('State')}" + (f": {p.get('Reason')}" if p.get("Reason") else ""))
    opened(p0)
    agreed(w0, p0)
    ops0 = apply_all(fleet, label, w0, argvs, a.n)[0]  # checked at the tip, to know what to prepare
    undos, seen = [], {}
    try:
        for op in ops0:
            if op.prepare:
                undos.append(op.prepare())

        def change(w):
            pl = proposals(w)
            p = proposal(pl, a.n, label)
            opened(p)
            agreed(w, p)
            ops, told = apply_all(fleet, label, w, argvs, a.n)
            p.set("State", "approved")
            p.set("Closed", datetime.date.today().isoformat(), after="By")
            w.replace("proposals.rec", pl.text())
            w.subject = f"plan(proposal {a.n}): approve: {summary(argvs)}"
            w.on += [f"proposal/{a.n}"] + objects(argvs)
            seen["ops"] = ops
            return told
        sha = write(fleet, label, change, "plan: approve", act="plan.approve")
    except Refusal:
        for undo in reversed([u for u in undos if u]):
            undo()
        raise
    for op in seen["ops"]:
        record.emit(label, op.act, op.on + op.added_on, op.frm + op.added_frm + [f"proposal/{a.n}"], [f"{repo}@{sha}"],
                    record.subject(op.subject))
        if op.after:
            op.after(repo, sha)
    print(f"proposal {a.n} is approved and applied")


def plan_drop(fleet, a):
    """crew plan drop <n> "<reason>": an open proposal closed unapplied, with the reason; the planner is told when
    someone else dropped it."""
    label = proposal_label(fleet, a, a.n)
    CONTEXT["label"] = label

    def change(w):
        pl = proposals(w)
        p = proposal(pl, a.n, label)
        p.get("State") == "open" or fail(f"proposal {a.n} is {p.get('State')}, so it can't be dropped")
        argvs = [do_args(label, d) for d in p.all("Do")]
        p.set("State", "dropped")
        p.set("Closed", datetime.date.today().isoformat(), after="By")
        p.set("Reason", a.reason, after="Closed")
        w.replace("proposals.rec", pl.text())
        w.subject = f"plan(proposal {a.n}): drop"
        w.on += [f"proposal/{a.n}"] + objects(argvs)
        return []
    write(fleet, label, change, "plan: drop", a.reason, act="plan.drop")
    tell_planner(fleet, label, f"Proposal {a.n} was dropped by {agent()}: {a.reason}")


def signal_text(fleet, label, sig):
    """A signal's assertion, its excerpt and the excerpt's grade where its capture has one, from whichever home holds
    it, for a proposal's page."""
    try:
        hit = signal_at(fleet, label, sig)
    except Refusal:
        return None, None, None
    if not hit:
        return None, None, None
    _, repo, tip, text = hit
    body = text.split("---", 2)[2] if text.startswith("---") and text.count("---") >= 2 else text
    paras = [p.strip() for p in body.strip().split("\n\n") if p.strip()]
    excerpt = next((p for p in paras if p.startswith(">")), None)
    assertion = next((p for p in paras if not p.startswith(">")), None)
    return assertion, excerpt, field(show(repo, tip, capture_of(sig)) or "", "excerpt")


def amendment(fleet, plan, a):
    """A unit amend as the user reads it: the unit's bolt, team and stage, its intent as it stands and as it would be,
    and what approval sets in motion. The stage is read from the unit's kit."""
    u = plan.unit(a.unit)
    if u is None:
        return [f"**Amend unit `{a.unit}`**, new in this proposal", f"Intent, as proposed:  {a.intent}"]
    s, b = unit_stage(fleet, plan, a.unit), u.get("Bolt")
    team = plan.bolt(b).get("Team") if b else None
    where = (f"bolt `{b}`" + (f" ({team})" if team else "")) if b else f"the queue of {u.get('Repo')}"
    st = s["stage"]
    now = ("" if st == "queued" else f", its stage unknown ({s.get('why')})" if st == "unknown" else
           f", now in {st}" if st in ("construct", "review", "code", "verify") else f", now {st}")
    return [f"**Amend unit `{a.unit}`** in {where}{now}", f"Intent, as it stands: {u.get('Intent')}", f"Intent, as proposed:  {a.intent}",
            f"On approval: {team}'s conductor runs construct again, and the unit returns to your review." if s["worktree"] and team else
            "On approval: its intent is replaced; it has no change written yet, so nothing else changes."]


def describe(fleet, label, plan, p):
    """A proposal as the user reads it: each change in plain words, with what the user is comparing beside it (a unit's
    intent and sources, the goal and team of the bolt it would join, an amended unit's intent before and after), and
    who has yet to agree."""
    argvs = [do_args(label, d) for d in p.all("Do")]
    per = touched_by(plan, argvs)
    new_bolts, changes = {}, []

    def bolt_line(b):
        if b in new_bolts:
            return f"bolt `{b}` (new in this proposal)"
        r = plan.bolt(b)
        return f"bolt `{b}`" + (f", held by {r.get('Team')}" if r and r.get("Team") else "")

    def goal_of(b):
        return new_bolts.get(b) or (plan.bolt(b).get("Goal") if plan.bolt(b) else None)

    def intent_of(u):
        r = plan.unit(u)
        return r.get("Intent") if r else None
    for i, a in enumerate(argvs):
        key, lines = (a.cmd, a.sub), []
        if key == ("bolt", "new"):
            new_bolts[a.bolt] = a.goal
            lines = [f"**New bolt `{a.bolt}`** in {a.repo}", f"Goal: {a.goal}"] + [f"Source: {s}" for s in a.source]
        elif key == ("bolt", "order"):
            where = "first" if a.first else "last" if a.last else f"before `{a.before}`"
            lines = [f"**Order bolt `{a.bolt}`** {where}", f"Goal: {goal_of(a.bolt)}"]
        elif key == ("bolt", "drop"):
            lines = [f"**Drop bolt `{a.bolt}`**" + (", its units back to the queue" if a.requeue else ", with its units"),
                     f"Goal: {goal_of(a.bolt)}", f"Reason: {a.reason}"]
        elif key == ("unit", "add"):
            where = bolt_line(a.bolt) if a.bolt else f"the queue of {a.repo}"
            lines = [f"**New unit `{a.unit}`** in {where}", f"Intent: {a.intent}"]
            if a.bolt and goal_of(a.bolt):
                lines.append(f"Bolt's goal: {goal_of(a.bolt)}")
            if getattr(a, "unblocks", None):
                lines.append(f"Unblocks: bolt `{a.unblocks}`, which can't be proven or land without it")
            if a.signal:
                assertion, excerpt, grade = signal_text(fleet, label, a.signal)
                lines.append(f"From: signals/{a.signal}" + (f": \"{assertion}\"" if assertion else ""))
                if excerpt:
                    lines.append(f"Excerpt" + (f" ({grade})" if grade else "") + f": {excerpt}")
            lines += [f"Source: {s}" for s in a.source]
        elif key == ("unit", "move"):
            src = next((b for b in per[i] if b != a.bolt), None)
            to = None if a.bolt == "queue" else a.bolt
            lines = [f"**Move unit `{a.unit}`** from {bolt_line(src) if src else 'the queue'} to {bolt_line(to) if to else 'the queue'}",
                     f"Intent: {intent_of(a.unit)}"]
            if to and goal_of(to):
                lines.append(f"Bolt's goal: {goal_of(to)}")
            if getattr(a, "unblocks", None):
                lines.append(f"Unblocks: bolt `{a.unblocks}`, which can't be proven or land without it")
        elif key == ("unit", "split"):
            lines = [f"**Split unit `{a.unit}`**", f"Narrowed intent: {a.intent}"] + [f"New unit `{n}`: {i}" for n, i in a.into]
        elif key == ("unit", "amend"):
            lines = amendment(fleet, plan, a)
        elif key == ("unit", "order"):
            where = "first" if a.first else "last" if a.last else f"before `{a.before}`"
            lines = [f"**Order unit `{a.unit}`** {where}", f"Intent: {intent_of(a.unit)}"]
        elif key == ("unit", "after"):
            lines = [f"**Unit `{a.unit}` comes after** " + ("nothing" if a.none else ", ".join(f"`{d}`" for d in a.deps))]
        elif key == ("unit", "drop"):
            lines = [f"**Drop unit `{a.unit}`**", f"Intent: {intent_of(a.unit)}", f"Reason: {a.reason}"]
        changes.append({"do": a.do, "lines": lines, "bolts": per[i]})
    held = held_teams(plan, flat(per))
    agreed = p.all("Agreed")
    return {"proposal": int(p.get("Proposal")), "state": p.get("State"), "by": p.get("By"), "opened": p.get("Opened"),
            "closed": p.get("Closed"), "reason": p.get("Reason"), "replaces": p.get("Replaces"), "case": p.get("Case"),
            "changes": changes, "agreed": agreed, "waiting": [t for t in held if t not in agreed]}


def page(d, label):
    """The markdown of one proposal, so the planner can show it in its pane or beside it in plannotator."""
    out = [f"# Proposal {d['proposal']} — {d['state']}, by {d['by']}, {d['opened']}", ""]
    if d["replaces"]:
        out += [f"Replaces proposal {d['replaces']}.", ""]
    out += [d["case"], "", "## Changes", ""]
    for i, c in enumerate(d["changes"], 1):
        first, *rest = c["lines"]
        out.append(f"{i}. {first}")
        out += [f"   {l}" for l in rest]
        out.append("")
    if d["state"] != "open":
        out += [f"Closed {d['closed']}" + (f": {d['reason']}" if d["reason"] else "") + "."]
        return "\n".join(out).rstrip() + "\n"
    out += ["## Waiting on", ""]
    out += [f"- {t}-conductor: `crew plan agree {d['proposal']} --label {label}`, or tell {label}-planner why not" for t in d["waiting"]]
    if d["agreed"]:
        out.append("- agreed: " + ", ".join(d["agreed"]))
    out.append(f"- the user: `crew plan approve {d['proposal']} --label {label}`, or `crew plan drop {d['proposal']} \"<reason>\" --label {label}`")
    return "\n".join(out) + "\n"


def plan_proposed(fleet, a):
    """crew plan proposed [<n>] [--label L] [--json]: the open proposals, or one as the user would read it. Reads the
    flywheels' branches only, so any host can answer."""
    label = default_label(fleet, a)
    if a.n is not None:
        label = label or proposal_label(fleet, a, a.n)
        w, _, p, _ = at_tip(fleet, label, a.n)
        d = describe(fleet, label, w.plan, p)
        print(json.dumps(d, indent=1) if a.json else page(d, label), end="" if not a.json else "\n")
        return
    rows = []
    for l in ([label] if label else list(fleet["partitions"])):
        repo, ref = state_of(fleet, l)
        tip = fetch(repo, ref)
        text = show(repo, tip, "proposals.rec") if tip else None
        if not text:
            continue
        plan = read(repo, ref, tip)
        for p in Plan(text).recs("Proposal"):
            if p.get("State") == "open":
                d = describe(fleet, l, plan, p)
                rows.append(dict(d, label=l, waits=[f"{t}-conductor" for t in d["waiting"]] + ["the user"]))
    if a.json:
        print(json.dumps(rows, indent=1))
        return
    if not rows:
        print("no proposal is open" + (f" in {label}" if label else ""))
        return
    for r in rows:
        print(f"{r['label']} {r['proposal']:<3} {r['by']:<24} {r['opened']}  {r['case'].splitlines()[0][:70]}  waiting on "
              + ", then ".join(r["waits"]))


# -------------------------------------------------------------------------------------------------- signals

def signal_at(fleet, label, sig, w=None):
    """Where a signal is: signals/<id>.md on the flywheel's branch (as the write w has it, else at the branch's tip),
    else on main of the partition's first blueprints repo, where the daily pass writes meetings' and channels'.
    (where, repo, tip, the signal's text), or None when it is in neither."""
    path = f"signals/{sig}.md"
    if w is not None:
        repo, ref, tip = w.repo, f"{label}/main", w.tip
        text = w.text(path)
    else:
        repo, ref = state_of(fleet, label)
        tip = fetch(repo, ref)
        text = show(repo, tip, path) if tip else None
    if text is not None:
        return ref, repo, tip, text
    srepo = crew.partition_of(fleet, label)["blueprints"][0]
    tip = fetch(srepo, "main")
    text = show(srepo, tip, path) if tip else None
    return ("main", srepo, tip, text) if text is not None else None


def no_signal(fleet, label, sig):
    fail(f"no signal {sig} on {label}/main of {state_of(fleet, label)[0]} or on main of "
         f"{crew.partition_of(fleet, label)['blueprints'][0]}: signals/{sig}.md is in neither")


def frontmatter(text):
    """The fields of a markdown file's frontmatter, [(name, value)] in order; none when it has none."""
    m = re.match(r"^---\n(.*?)\n---\n", text or "", re.S)
    return [tuple(l.split(": ", 1)) if ": " in l else (l.rstrip(":"), "") for l in m.group(1).splitlines() if l.strip()] if m else []


def field(text, name):
    return next((v for k, v in frontmatter(text) if k == name), None)


def capture_of(sig):
    """A signal's capture, signals/<capture>/capture.md, from its id <capture>/<NN>-<slug>."""
    return f"signals/{sig.rsplit('/', 1)[0]}/capture.md"


def move(fleet, label, w, sig, rec):
    """A signal's one move, appended to the flywheel's moves.rec in the write w: refused when the signal is in
    neither of its homes, or already has its move. recfix checks the file before the commit, so a move the file's
    schema refuses writes nothing."""
    signal_at(fleet, label, sig, w) or no_signal(fleet, label, sig)
    moves = w.text("moves.rec")
    moves is not None or fail(f"{label}/main of {w.repo} has no moves.rec: crew state init {label}")
    unmoved(moves, sig)
    w.replace("moves.rec", moves.rstrip("\n") + "\n\n" + "\n".join(rec.lines()) + "\n")


def unmoved(text, sig):
    moved = [m for m in Plan(text).recs("Move") if m.get("Signal") == sig]
    not moved or fail(f"signal {sig} already has its move: {moved[0].get('Move')}")


def route_move(sig, unit):
    return Rec("Move", [("Signal", sig), ("Move", "route"), ("Target", f"unit/{unit}"),
                        ("Date", datetime.date.today().isoformat()), ("By", agent())])


CURATION = ("attach", "challenge", "new-territory", "answered", "drop")
KINDS = ("constraint", "ask", "question", "commitment", "reaction")


def signal_move(fleet, a):
    """Curation's five moves, each written through crew the way the route is: one move per signal, appended to
    moves.rec on the flywheel's branch of its state repository, never merged."""
    label = default_label(fleet, a) or fail("which partition's signals? add --label " + "|".join(fleet["partitions"]))
    a.move not in ("attach", "challenge", "answered") or a.target or fail(
        f"a {a.move} move names its target (--target): the intent, claim or record it " + {"attach": "lands on", "challenge": "argues with", "answered": "was settled by"}[a.move])
    a.move != "drop" or a.reason or fail("a drop gives its reason (--reason)")
    rec = Rec("Move", [("Signal", a.signal), ("Move", a.move)] + ([("Target", a.target)] if a.target else [])
              + ([("Reason", a.reason)] if a.reason else []) + [("Date", datetime.date.today().isoformat()), ("By", agent())])
    # A target is a pointer, a typed name such as unit/<unit> or a path; anything else could be typed text.
    target = [a.target] if a.target and re.fullmatch(r"[a-z]+/[^\s]+", a.target) else []
    write(fleet, label, lambda w: move(fleet, label, w, a.signal, rec), f"signals({a.signal}): {a.move}",
          act="signal.move", on=[f"signals/{a.signal}"] + target)


class Already(Exception):
    """The signal is recorded already, in its capture: nothing is written, and its id is said."""


def dashed(s):
    """A name as a directory's part: lowercase, any other characters a dash."""
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def sha16(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def quoted(excerpt, position):
    """The excerpt as a signal quotes it: a blockquote of the words, verbatim, then its position."""
    return "\n".join(f"> {l}" if l else ">" for l in f'"{excerpt}" — {position}'.split("\n"))


def where_of(fleet, name, plan):
    """Where an agent was working, read without asking it: its team, the bolt the team holds and, for a slot's stage,
    the unit or fix its slot holds; the main level, or the operator session; None for an agent crew has no role for."""
    kind, of = role(fleet, name)
    if kind in ("planner", "design", "main-ops", "dispatcher"):
        return "main level"
    if kind == "operator":
        return "operator session"
    if kind not in ("conductor", "team"):
        return None
    out = [f"team {of}"] + [f"bolt {b.name()}" for b in held_by(plan, of)[:1]]
    slot = re.fullmatch(rf"{re.escape(of)}-(unit-[1-9][0-9]*)", name)
    if slot:
        try:
            held = crew.slot_of(fleet["teams"][of], slot.group(1))
            out.append(f"fix {held['name'].rsplit('/', 1)[-1]}" if held["kind"] == "fix" else f"unit {held['name']}")
        except Refusal:
            pass
    return ", ".join(out)


def bank(path, line):
    """The source record appended to the host's raw file for its capture, outside git, unless it is there already."""
    try:
        if path.exists() and line in path.read_bytes().split(b"\n"):
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "ab") as f:
            f.write(line + b"\n")
    except OSError as e:
        fail(f"the source record could not be banked at {path}: {e.strerror or e}")


def signal(fleet, a):
    """A finding, as a capture and its signal under signals/ on the flywheel's branch, in the shape the blueprints'
    signals/README.md gives. An agent quotes the words that show it, which are looked for in its own Claude transcript
    and graded (transcript.py), and a paraphrase is refused. Its capture is the one record that holds the excerpt,
    copied to this host's raw/ outside git; a second signal from that record joins the capture, and the same signal
    again writes nothing. The user's note at a shell is its own excerpt. One write, one commit."""
    label = default_label(fleet, a) or fail("which partition's signals? add --label " + "|".join(fleet["partitions"]))
    crew.NAME.match(a.slug) or fail(f"a signal's slug is lowercase words with dashes, not {a.slug}")
    a.slug not in ("move", "show") or fail(f"a signal's slug can't be '{a.slug}'")
    a.asserts.strip() or fail("a signal says what it asserts, in a sentence")
    name, host = os.environ.get("CREW_AGENT"), crew.this_host()
    now = datetime.datetime.now(datetime.timezone.utc)
    excerpt = a.excerpt
    if a.excerpt_file:
        try:
            excerpt = pathlib.Path(a.excerpt_file).read_text()
        except (OSError, UnicodeDecodeError) as e:
            fail(f"cannot read the excerpt from {a.excerpt_file}: {getattr(e, 'strerror', None) or e}")
    if name:
        excerpt = (excerpt or "").strip()
        excerpt or fail('a signal quotes the words that show it: add --excerpt "<the exact words the user said or the '
                        'tool printed>", or --excerpt-file <path>')
        v, sid = check_excerpt(a, excerpt, host)
        v.grade != "refused" or fail("the excerpt is not in your session's transcript: quote the words as you received "
                                     "them, from the user or from a tool's output")
        # The capture's key and name, by grade: a received record by its uuid, any other line by its hash, and an
        # unchecked excerpt by its own; dated by the record's time where it has one.
        when = transcript.stamp(v.at) if v.grade == "verified" else None
        date = (transcript.stamp(v.at) or now).date().isoformat()
        rid = re.sub(r"[^a-z0-9]", "", (v.uuid or "").lower()) if v.grade == "verified" else ""
        if v.grade == "unverified":
            h = sha16(excerpt)
            key, part = f"unverified/{name}/{h}", h[:8]
        elif rid:
            key, part = f"session/{sid}/{v.uuid}", rid[:8]
        else:
            h = v.line_hash()[:16]
            key, part = f"session/{sid}/line-{h}", h[:8]
        cap = f"{date}-{dashed(name)}-{part}"
        who = {"user": "user", "crew": "crew"}.get(v.asserted_by) or (v.asserted_by[6:] if v.asserted_by.startswith("agent:") else name)
        position = "unverified" if v.grade == "unverified" else when.strftime("%H:%M:%SZ") if when else f"line {v.n}"
        kind = a.kind or "constraint"
    else:
        excerpt = (excerpt or a.asserts).strip()
        h = sha16(excerpt)
        v = sid = when = None
        date, key = now.date().isoformat(), f"operator/{agent()}/{h}"
        cap, who, position, kind = f"{date}-{dashed(getpass.getuser())}-{dashed(host)}-{h[:8]}", "user", now.strftime("%H:%M:%SZ"), a.kind or "ask"
    # An id is unique across both homes, so it is looked up in either without asking which.
    srepo = crew.partition_of(fleet, label)["blueprints"][0]
    btip = fetch(srepo, "main")
    not (btip and git(srepo, "ls-tree", "--name-only", btip, f"signals/{cap}")) or fail(
        f"{srepo} has signals/{cap} already, so a capture can't take that name")
    raw = None
    if v and v.grade != "unverified":
        bank(record.ROOT / label / "raw" / f"{cap}.jsonl", v.raw)
        raw = f"{host}:~/.local/state/crew/{label}/raw/{cap}.jsonl"
    quote = quoted(excerpt, position)
    subject = "[" + ", ".join(x.strip() for x in a.subject.split(",") if x.strip()) + "]" if a.subject else None
    seen = {}

    def change(w):
        cpath = f"signals/{cap}/capture.md"
        have = w.text(cpath)
        names = []
        if have is not None:
            field(have, "key") == key or fail(f"signals/{cap} on {label}/main is another capture ({field(have, 'key')}), not {key}")
            listed = git(w.repo, "ls-tree", "--name-only", f"{w.tip}:signals/{cap}", check=False)
            names = [n for n in (listed.stdout.split() if listed.returncode == 0 else []) if re.match(r"^[0-9]{2}-.*\.md$", n)]
            for n in names:
                if n[3:-3] == a.slug and quote in (w.text(f"signals/{cap}/{n}") or ""):
                    raise Already(f"{cap}/{n[:-3]}")
        nn = 1 + max([int(n[:2]) for n in names] or [0])
        sig = f"{cap}/{nn:02d}-{a.slug}"
        if have is None:
            have = capture_text(fleet, name, host, v, sid, key, cap, date, now, raw, w.plan)
        w.replace(cpath, re.sub(r"(?m)^signals: [0-9]+$", f"signals: {len(names) + 1}", have, count=1))
        w.replace(f"signals/{sig}.md", "---\n" + f"signal: {sig}\nkind: {kind}\nwho: {who}\n" + (f"subject: {subject}\n" if subject else "")
                  + "---\n\n" + a.asserts.strip() + "\n\n" + quote + "\n")
        w.subject = f"signals({sig}): {a.slug}"
        w.on.append(f"signals/{sig}")
        seen["id"] = sig
        return []
    try:
        write(fleet, label, change, f"signals: {a.slug}", act="capture")
    except Already as e:
        print(f"signal {e} is recorded already; nothing was written")
        return
    grade = "own" if v is None else v.grade
    print(f"signal {seen['id']}: excerpt {grade}" + (f", asserted by {v.asserted_by}" if v and v.grade == "verified" else "")
          + (f" ({v.reason})" if v and v.grade == "unverified" else ""))


def check_excerpt(a, excerpt, host):
    """The agent's excerpt checked against its own Claude session's transcript, which is on this host: crew signal
    is never run on another. The session is the one a forwarded command carries, else herdr's for the agent. Returns
    the verdict and the session id."""
    sess = record.session()
    shost, sid = sess.split(":", 1) if sess and ":" in sess else (host, sess)
    if sid and shost != host:
        return transcript.unverified(f"session {sid} is on {shost}, not {host}"), sid
    skip = [a.excerpt_file, str(pathlib.Path(a.excerpt_file).resolve())] if a.excerpt_file else []
    return transcript.check(sid, excerpt, skip), sid


def capture_text(fleet, name, host, v, sid, key, cap, date, now, raw, plan):
    """A new capture.md: where its excerpt came from and how well crew could check it, with the count of its signals,
    which each signal that joins it rewrites."""
    today = now.date().isoformat()
    if v is None:
        fields = [("capture", cap), ("source", "operator"), ("key", key), ("captured_by", agent()), ("host", host),
                  ("excerpt", "own"), ("asserted_by", "user")]
        title, body = f"{agent()}, {date}", "The user's own note, recorded with crew signal at a shell."
    else:
        when = transcript.stamp(v.at) if v.grade != "unverified" else None
        record_name = None if v.grade == "unverified" else v.uuid or f"line {v.n}"
        fields = [("capture", cap), ("source", "crew-session"), ("key", key), ("captured_by", name), ("host", host),
                  ("session", sid), ("record", record_name), ("at", when.strftime("%Y-%m-%dT%H:%M:%SZ") if when else None),
                  ("excerpt", v.grade), ("unverified", v.reason), ("asserted_by", v.asserted_by),
                  ("where", where_of(fleet, name, plan)), ("raw", raw)]
        title = f"{name}, {date}" + (f" {when.strftime('%H:%M')}Z" if when else "")
        body = (f"Words {name} quoted, captured with crew signal; crew could not check them against its session."
                if v.grade == "unverified" else f"One record of {name}'s session, captured with crew signal.")
    fields += [("event_date", date), ("imported", today), ("status", "read"), ("signals", "1")]
    return "---\n" + "".join(f"{k}: {x}\n" for k, x in fields if x not in (None, "")) + f"---\n\n# {title}\n\n{body}\n"


def signal_show(fleet, a):
    """crew signal show <id>: the signal, its capture's provenance in plain lines (the excerpt's grade among them), and
    its move in each flywheel that reads it. Reads only the branches, so any host can answer."""
    label = default_label(fleet, a)
    labels, errors, hit = [label] if label else list(fleet["partitions"]), {}, None
    for l in labels:
        try:
            h = signal_at(fleet, l, a.signal)
        except Refusal as e:
            if label:
                raise
            errors[l] = str(e)  # with no partition named, one that can't be read is passed over, and named below
            continue
        if h:
            hit = (l, h)
            break
    hit or fail(f"no signal {a.signal} on the branches of " + ", ".join(f"{l}/main" for l in labels)
                + " or on main of their first blueprints repos" + "".join(f"; {l} could not be read: {e}" for l, e in errors.items()))
    found_in, (where, repo, tip, text) = hit
    out = [f"signals/{a.signal}, on {where} of {repo}", "", text.rstrip(), ""]
    cap = show(repo, tip, capture_of(a.signal))
    if cap is None:
        out.append(f"No capture.md beside it in {repo}.")
    else:
        out.append(f"Its capture, {capture_of(a.signal)}:")
        out += [f"  {k}: {x}" for k, x in frontmatter(cap)]
    # A signal in the state is its flywheel's alone; one in a blueprints repo is read by each flywheel it is first for.
    readers = [found_in] if where != "main" else [l for l in labels if crew.partition_of(fleet, l)["blueprints"][0] == repo]
    out.append("")
    for l in readers:
        srepo, ref = state_of(fleet, l)
        stip = fetch(srepo, ref)
        moves = show(srepo, stip, "moves.rec") if stip else None
        m = next((m for m in Plan(moves).recs("Move") if m.get("Signal") == a.signal), None) if moves else None
        out.append(f"No move yet in {l}." if not m else f"Its move in {l}: {m.get('Move')}" + (f" {m.get('Target')}" if m.get("Target") else "")
                   + f", by {m.get('By')} on {m.get('Date')}" + (f": {m.get('Reason')}" if m.get("Reason") else ""))
    print("\n".join(out))


# ------------------------------------------------------------------------------------- what bash crew asks

def sh(**pairs):
    return "\n".join(f"{k}={__import__('shlex').quote(str(v))}" for k, v in pairs.items())


def team_of_unit(fleet, a):
    """The team whose bolt holds a unit: crew unit run goes to that team's host."""
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))
    u = plan.unit(a.unit)
    u.get("Bolt") or fail(f"unit {a.unit} is queued: move it into a bolt first (crew unit move {a.unit} <bolt>)")
    team = plan.bolt(u.get("Bolt")).get("Team") or fail(f"bolt {u.get('Bolt')} is held by no team yet: crew bolt give <team> {u.get('Bolt')}")
    print(sh(TEAM=team))


def in_plan(fleet, a):
    """Whether a partition's plan has a unit (every partition's, without --label): said and exit 0 when one does, exit
    3 when none does, and refused when a plan could not be read, since then nobody can tell."""
    errors = {}
    labels = [a.label] if a.label else list(fleet["partitions"])
    hits = [h for h in plans(fleet, labels, errors) if h[3] and h[3].unit(a.unit)]
    if hits:
        print(f"unit {a.unit} is in {hits[0][0]}/main of {hits[0][1]}")
        return
    not errors or fail(f"can't tell whether unit {a.unit} is still planned: "
                       + "; ".join(f"{k} could not be read: {v}" for k, v in errors.items()))
    sys.exit(3)


HEAD = r"""cd "$1" && git rev-parse HEAD"""


def mark_amended(fleet, label, unit, bolt, head):
    """The plan marks a unit amended at the head construct starts again from, so its code, verify and merge wait for
    the user's review of what construct writes. Returns the write's commit. What the write says goes to standard
    error: bash crew reads standard output as the stage's variables."""
    def change(w):
        u = w.unit(unit)
        u.get("Bolt") == bolt or fail(f"unit {unit} moved to {u.get('Bolt') or 'the queue'} meanwhile")
        u.set("Amended", head)
        return [bolt]
    with contextlib.redirect_stdout(sys.stderr):
        return write(fleet, label, change, f"plan({bolt}): {unit} amended, construct runs again")


def run_check(fleet, a):
    """Whether a unit's stage may start, its place (made for construct), and the prompt the stage is sent. Construct
    is run again at any stage before merge, and on a unit with an approved change, or one already amended, it first
    marks the unit amended in the plan: a write the conductor of the team holding its bolt, or the user, makes. Code,
    verify and merge wait while the mark stands."""
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))
    u = plan.unit(a.unit)
    bolt = u.get("Bolt") or fail(f"unit {a.unit} is queued: move it into a bolt first")
    t = fleet["teams"][plan.bolt(bolt).get("Team")]
    s = Stages(fleet, plan, survey(fleet, [(t["name"], bolt)])).of(a.unit)
    st, place, mark = s["stage"], f"{t['kit']['dir']}/places/{a.unit}", u.get("Amended")
    st != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    words = f" {a.words}" if a.words else ""
    amended_at = entry = ""
    if a.stage == "construct":
        if st == "waiting":
            deps = [d for d in u.all("After") if Stages(fleet, plan, survey(fleet, [(t["name"], bolt)])).of(d)["stage"] not in ("merged", "landed")]
            fail(f"unit {a.unit} is waiting: it comes after " + ", ".join(deps) + ", not yet merged into its bolt")
        st not in ("merged", "landed") or fail(f"unit {a.unit} has " + ("merged into its bolt" if st == "merged" else "landed on main")
                                               + ": a defect in it is a fix (crew fix), and a new need is a new unit")
        marking = bool(mark) or st in ("approved", "code", "verify")
        if marking:
            kind, team = role(fleet, os.environ.get("CREW_AGENT"))
            kind == "user" or (kind, team) == ("conductor", t["name"]) or fail(
                f"unit {a.unit} is in {st}, so construct run again marks it amended: a plan write only {t['name']}-conductor "
                "or the user makes")
        make_place(fleet, t, place, f"unit/{a.unit}", f"bolt/{bolt}", track=True)
        if marking:
            head = s.get("head") or host_run(fleet, t["machine"], HEAD, place)
            if head != mark:
                amended_at, entry = f"{repo}@{mark_amended(fleet, label, a.unit, bolt, head)}", CONTEXT["eid"]
        sources = u.all("Source")
        again = " This unit's intent was amended; revise the existing change to it." if amended(mark) else ""
        prompt = f"/opsx:propose {a.unit} {u.get('Intent')}" + (" Sources: " + "; ".join(sources) + "." if sources else "") + again + words
    elif mark:
        fail(f"unit {a.unit} was amended and " + (f"construct has not been run again (crew unit run {a.unit} construct)" if st == "amended"
                                                  else f"waits for the user's review (crew unit approve {a.unit})"))
    elif a.stage == "code":
        st != "review" or fail(f"unit {a.unit} is in review: code waits until the user approves it (crew unit approve {a.unit})")
        st in ("approved", "code", "verify") or fail(f"unit {a.unit} is in {st}, with no approved change to code yet")
        prompt = f"/opsx:apply {a.unit}{words}"
    elif a.stage == "verify":
        if st == "code":
            e = Refusal(f"unit {a.unit} is in code, with these tasks still open: " + "; ".join(s["open"]))
            n = len(s["open"])
            e.recorded = f"unit {a.unit} is in code, with {n} task{'' if n == 1 else 's'} still open"  # titles are typed text
            raise e
        st == "verify" or fail(f"unit {a.unit} is in {st}: verify waits until every task is ticked")
        prompt = f"/opsx:verify {a.unit}{words}"
    else:
        st == "verify" or fail(f"unit {a.unit} is in {st}: it merges once every task is ticked and verify has run")
        prompt = f"Merge {a.unit} into bolt/{bolt}: wt merge bolt/{bolt} --no-squash --no-remove{words}"
    # A construct that marked the unit amended: the plan's commit, and the entry it names, which the stage's start is.
    print(sh(PLACE=place, BOLT=bolt, PROMPT=prompt, AMENDED=amended_at, ENTRY=entry))


def bolt_of_team(fleet, a):
    t = crew.team_of(fleet, a.team)
    repo, ref = state_of(fleet, t["label"])
    tip = fetch(repo, ref) or fail(f"{repo} has no {ref} yet: crew state init {t['label']}")
    held = held_by(read(repo, ref, tip), t["name"])
    held or fail(f"{t['name']} holds no bolt: crew bolt give {t['name']}")
    print(sh(BOLT=held[0].name()))


def place_cmd(fleet, a):
    make_place(fleet, crew.team_of(fleet, a.team), a.path, a.branch, a.base, track=True)


def plan_of(fleet, label):
    """The label's plan, or None when it can't be read, so a team's slots are still read from the kit."""
    try:
        repo, ref = state_of(fleet, label)
        tip = fetch(repo, ref)
        return read(repo, ref, tip) if tip else None
    except Refusal:
        return None


def slot_stages(fleet, t):
    """Each slot of the team on this host that holds a unit or fix: what it holds and that work's stage, read from the
    kit and the plan, with its tasks done and total where its change has a task list. Work that has neither landed nor
    merged is dropped when the plan was read and has no such unit, or no bolt the fix's branch tracks."""
    path = pathlib.Path.home() / f".local/state/{t['name']}-team/slots"
    held = [l.split() for l in (path.read_text().splitlines() if path.exists() else []) if l.strip()]
    if not held:
        return []
    k = survey(fleet, [(t["name"], None)]).get(t["machine"], {})
    kit = k.get("kits", {}).get(t["kit"]["main"], {}) if k.get("ok") else {}
    plan = plan_of(fleet, t["label"])
    marks = {u.name(): u.get("Amended") for u in plan.units() if u.get("Amended")} if plan else {}
    out = []
    for slot, kind, name, place in held:
        stage, counts = "unknown", None
        if kit.get("ok") and kind == "fix":
            f = next((f for f in kit["fixes"] if f["fix"] == name), None)
            stage = ("merged" if f["merged"] else "dropped" if plan and f["bolt"] and not plan.bolt(f["bolt"]) else "fix") if f else "none"
        elif kit.get("ok"):
            pl = kit["places"].get(name)
            if name in kit["main"]:
                stage = "landed"
            elif pl and pl["bolt"] and name in kit["bolts"].get(pl["bolt"], {}).get("changes", []):
                stage = "merged"
            elif plan and not plan.unit(name):
                stage = "dropped"
            elif pl:
                stage = place_stage(pl, marks.get(name))
                counts = "{}/{}".format(*pl["tasks"]) if pl["tasks"] else None
            else:
                stage = "none"
        out.append(dict(slot=slot, kind=kind, name=name, stage=stage, counts=counts, place=place))
    return out


def slots_cmd(fleet, a):
    """Each slot of the team on this host: what it holds and that work's stage, read from the kit and the plan's marks."""
    for s in slot_stages(fleet, crew.team_of(fleet, a.team)):
        tasks = s["counts"] if s["counts"] and s["stage"] in ("code", "verify") else "-"
        print(s["slot"], s["kind"], s["name"], s["stage"], tasks, s["place"])


def tidy(fleet, a):
    """Each worktree crew made in the team's kit checkout, on this host, whose work is over and that no slot holds:
    removed with its branch, saying the commit the branch was at; or kept and named, with its branch, while it is
    locked or has uncommitted changes. crew made it when it is directly in <kit>/bolts/ on bolt/<its folder>, or
    directly in <kit>/places/ on unit/<its folder> or a fix/ branch; nothing else is touched. The worktrees are listed
    before the slots and plans are read: a plan has a bolt, a unit or a fix's bolt, and a slot is taken, before crew
    makes the worktree, so whatever is listed was planned or held by then. Nothing is removed when a plan the kit's
    work goes in can't be read."""
    t = crew.team_of(fleet, a.team)
    main, kdir, kit = os.path.realpath(t["kit"]["main"]), os.path.realpath(t["kit"]["dir"]), t["kit"]["name"]
    trees = gather.worktrees(main)
    held = set()  # each slot's name and place, of every team of this host building in this checkout
    for o in fleet["teams"].values():
        if o["machine"] == crew.this_host() and os.path.realpath(o["kit"]["main"]) == main:
            f = pathlib.Path.home() / f".local/state/{o['name']}-team/slots"
            for slot, kind, name, place in (l.split()[:4] for l in (f.read_text().splitlines() if f.exists() else []) if len(l.split()) >= 4):
                held |= {name, os.path.realpath(place)}
    errors = {}
    found = plans(fleet, sorted({o["label"] for o in kit_teams(fleet, kit)}), errors)
    errors.update({f"{l}/main of {repo}": f"{repo} has no {l}/main yet" for l, repo, tip, _ in found if not tip})
    if errors:
        print("no worktree was removed: " + "; ".join(f"{k} could not be read: " + " ".join(v.split()) for k, v in errors.items()))
        return
    bolts = {b.name() for *_, p in found for b in p.bolts() if b.get("Repo") == kit}
    units = {u.name() for *_, p in found for u in p.units() if u.get("Repo") == kit}
    ups, on_main = gather.upstreams(main), set(gather.changes(main, "main"))
    for w in trees:
        path, branch = w["path"], w.get("branch") or ""
        folder, up = os.path.basename(path), ups.get(branch, "")
        bolt = up[5:] if up.startswith("bolt/") else None
        if os.path.dirname(path) == os.path.join(kdir, "bolts") and branch == f"bolt/{folder}":
            name, over = None, None if folder in bolts else f"bolt {folder} is in no plan"
        elif os.path.dirname(path) == os.path.join(kdir, "places") and branch == f"unit/{folder}":
            name, over = folder, (f"unit {folder} has landed on main" if folder in on_main else
                                  f"unit {folder} has merged into bolt/{bolt}" if bolt and folder in gather.changes(main, f"bolt/{bolt}") else
                                  None if folder in units else f"unit {folder} is in no plan")
        elif os.path.dirname(path) == os.path.join(kdir, "places") and branch.startswith("fix/") and bolt:
            name, over = branch, (f"{branch} has merged into bolt/{bolt}" if gather.fix_merged(main, branch, bolt) else
                                  None if bolt in bolts else f"bolt {bolt}, which {branch} was made from, is in no plan")
        else:
            continue
        if not over or name in held or path in held or not os.path.isdir(path):
            continue
        if w.get("locked"):
            print(f"{path} is kept, and {branch} with it: it is locked")
            continue
        st = subprocess.run(["git", "-C", path, "status", "--porcelain"], capture_output=True, text=True, env=gitenv())
        if st.returncode or st.stdout.strip():
            print(f"{path} is kept, and {branch} with it: " + (f"git cannot read its status: {st.stderr.strip()}" if st.returncode else
                  f"{over}, and it has uncommitted changes, which are the user's to keep or discard"))
            continue
        sha = subprocess.run(["git", "-C", main, "rev-parse", "--short", "--verify", "-q", f"refs/heads/{branch}"],
                             capture_output=True, text=True, env=gitenv()).stdout.strip()
        r = subprocess.run(["git", "-C", main, "worktree", "remove", "--force", path], capture_output=True, text=True, env=gitenv())
        if r.returncode:
            print(f"{path} was not removed: {r.stderr.strip()}")
            continue
        r = subprocess.run(["git", "-C", main, "branch", "-q", "-D", branch], capture_output=True, text=True, env=gitenv())
        print(f"{path} and {branch} are removed; the branch was at {sha}" if r.returncode == 0 else
              f"{path} is removed, and {branch} is kept: {r.stderr.strip()}")


def stage_ends(fleet, a):
    """Record the end of each stage the team's stages file holds a start for, once each, under its lock: with --waited,
    the slot the conductor's wait returned for, as seen at once; with --ending, the slot whose agent is about to be
    ended, whatever it is doing; otherwise each one whose agent is no longer working, observed late by the command
    that reads the team. A line whose slot no longer holds its unit or fix is dropped without an entry."""
    t = crew.team_of(fleet, a.team)
    state = pathlib.Path.home() / f".local/state/{t['name']}-team"
    path = state / "stages"
    slots = state / "slots"
    held = {l.split()[0]: l.split() for l in (slots.read_text().splitlines() if slots.exists() else []) if l.strip()}
    now = {}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    with open(path, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        keep, ended = [], []
        for l in (l.split() for l in f.read().splitlines() if l.strip()):
            slot, name = l[0], l[1]
            if a.slot and slot != a.slot:
                keep.append(l)
            elif slot not in held or held[slot][2] != name:
                continue
            elif a.ending or crew.agent_status(fleet, f"{t['name']}-{slot}") != "working":
                ended.append(l)
            else:
                keep.append(l)
        now = {s["slot"]: s for s in slot_stages(fleet, t)} if ended else now
        for slot, name, stage, *rest in ended:
            s, fix = now.get(slot, {}), name.startswith("fix/")
            branch = name if fix else f"unit/{name}"
            head = subprocess.run(["git", "-C", t["kit"]["main"], "rev-parse", "--short", "--verify", "-q", f"refs/heads/{branch}"],
                                  capture_output=True, text=True).stdout.strip()
            on = ([rest[1]] if fix and len(rest) > 1 else [f"stage/{name}/{stage}", f"unit/{name}"]) + [f"agent/{t['name']}-{slot}"]
            why = f"fix({name.rsplit('/', 1)[-1]}): {stage} ended" if fix else f"unit({name}): {stage} ended"
            record.emit(t["label"], "stage.end", on, why=why,
                        Result=s.get("stage", "unknown"), Tasks=s.get("counts"), Head=head,
                        Observed=None if a.waited and not a.ending else "late")
        f.seek(0)
        f.truncate()
        f.write("".join(" ".join(l) + "\n" for l in keep))
    if a.waited and a.slot in held:
        now = now or {s["slot"]: s for s in slot_stages(fleet, t)}
        s = now.get(a.slot, {})
        print(f"{t['name']}-{a.slot} settled: {held[a.slot][2]} is in {s.get('stage', 'unknown')}"
              + (f", {s['counts']} tasks" if s.get("counts") else ""))


# ----------------------------------------------------------------------------------------------- crew bolts

def bolts_view(fleet, a):
    label = default_label(fleet, a)
    labels = [label] if label else list(fleet["partitions"])
    errors = {}
    found = plans(fleet, labels, errors)
    held = [(b.get("Team"), b.name()) for _, _, _, p in found if p for b in p.bolts() if b.get("Team") and a.bolt in (None, b.name())]
    sv = survey(fleet, held)
    data = {"partitions": [], "unreachable": {h: v["error"] for h, v in sv.items() if not v["ok"]}, "unread": errors}
    for l in labels:
        part = {"label": l, "plans": []}
        for pl, repo, tip, plan in found:
            if pl != l:
                continue
            if not plan:
                part["plans"].append({"repo": repo, "plan": None, "bolts": [], "queue": []})
                continue
            st = Stages(fleet, plan, sv)
            bolts = []
            for b in plan.bolts():
                if a.bolt not in (None, b.name()):
                    continue
                t = fleet["teams"].get(b.get("Team"))
                k, _ = st.kit(b) if t else (None, None)
                units = [dict(unit=u.name(), after=u.all("After"), sources=u.all("Source"), **{
                    x: st.of(u.name())[x] for x in ("stage", "tasks", "worktree")}) for u in plan.units_of(b.name())]
                fixes = [dict(fix=f["fix"], worktree=f["path"], merged=f["merged"]) for f in (k["fixes"] if k else []) if f["bolt"] == b.name()]
                bolts.append(dict(bolt=b.name(), repo=b.get("Repo"), goal=b.get("Goal"), sources=b.all("Source"), team=b.get("Team"),
                                  host=t["machine"] if t else None, state=st.bolt_state(b), units=units, fixes=fixes))
            queue = [] if a.bolt else [dict(unit=u.name(), repo=u.get("Repo"), stage="queued", sources=u.all("Source")) for u in plan.queue()]
            part["plans"].append({"repo": repo, "plan": tip, "bolts": bolts, "queue": queue})
        data["partitions"].append(part)
    if a.bolt and not any(b for p in data["partitions"] for pl in p["plans"] for b in pl["bolts"]):
        fail(f"no bolt {a.bolt} in the plans of " + ", ".join(labels))
    if a.json:
        print(json.dumps(data, indent=1))
        sys.exit(1 if errors else 0)
    lines = []
    for p in data["partitions"]:
        for pl in p["plans"]:
            if not pl["plan"]:
                lines.append(f"{p['label']}/main  {pl['repo']}  not started: crew state init {p['label']}")
                continue
            lines.append(f"{p['label']}/main {pl['plan'][:7]}  {pl['repo']}")
            for b in pl["bolts"]:
                who = f"{b['team']} @ {b['host']}" if b["team"] else "no team"
                lines.append(f"{b['bolt']}  {b['repo']}  {who}  {b['state']}")
                for u in b["units"]:
                    stage = u["stage"] + (f" {u['tasks'][0]}/{u['tasks'][1]}" if u["stage"] in ("code", "verify") and u["tasks"] else "")
                    where = "places/" + os.path.basename(u["worktree"]) if u["worktree"] else ""
                    lines.append(f"  {u['unit']:<40} {stage:<12} {where}".rstrip())
                for f in b["fixes"]:
                    lines.append(f"  {f['fix']:<40} {'fix merged' if f['merged'] else 'fix':<12} places/{os.path.basename(f['worktree'])}")
            repos = sorted({u["repo"] for u in pl["queue"]})
            for r in repos:
                lines.append(f"queue  {r}")
                for u in (x for x in pl["queue"] if x["repo"] == r):
                    lines.append(f"  {u['unit']:<40} {'queued':<12} {', '.join(u['sources'])}".rstrip())
    for h, why in data["unreachable"].items():
        lines.append(f"{h} did not answer ({why}): the stages of its bolts are unknown")
    print("\n".join(lines))
    if errors:
        sys.exit("\n".join(errors.values()))


# ----------------------------------------------------------------------------------------------------- the CLI

def parser(cls=argparse.ArgumentParser):
    ap = cls(prog="crew", add_help=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    st = sub.add_parser("state").add_subparsers(dest="sub", required=True)
    i = st.add_parser("init")
    i.add_argument("label")

    v = sub.add_parser("bolts")
    v.add_argument("bolt", nargs="?")
    v.add_argument("--label")
    v.add_argument("--json", action="store_true")

    bo = sub.add_parser("bolt").add_subparsers(dest="sub", required=True)
    x = bo.add_parser("new")
    x.add_argument("bolt")
    x.add_argument("goal")
    x.add_argument("--repo", required=True)
    x.add_argument("--source", action="append", default=[])
    x.add_argument("--before")
    x.add_argument("--label")
    x = bo.add_parser("give")
    x.add_argument("team")
    x.add_argument("bolt", nargs="?")
    x = bo.add_parser("order")
    x.add_argument("bolt")
    g = x.add_mutually_exclusive_group(required=True)
    g.add_argument("--before")
    g.add_argument("--first", action="store_true")
    g.add_argument("--last", action="store_true")
    x.add_argument("--label")
    x = bo.add_parser("drop")
    x.add_argument("bolt")
    x.add_argument("reason")
    x.add_argument("--requeue", action="store_true")
    x.add_argument("--label")
    x = bo.add_parser("land")
    x.add_argument("bolt")
    x.add_argument("--label")

    un = sub.add_parser("unit").add_subparsers(dest="sub", required=True)
    x = un.add_parser("add")
    x.add_argument("unit")
    x.add_argument("intent")
    x.add_argument("--bolt")
    x.add_argument("--repo")
    x.add_argument("--source", action="append", default=[])
    x.add_argument("--after", action="append", default=[])
    x.add_argument("--before")
    x.add_argument("--signal")
    x.add_argument("--unblocks", metavar="BOLT")
    x.add_argument("--label")
    x = un.add_parser("split")
    x.add_argument("unit")
    x.add_argument("intent")
    x.add_argument("--into", nargs=2, action="append", required=True, metavar=("UNIT", "INTENT"))
    x.add_argument("--label")
    x = un.add_parser("amend")
    x.add_argument("unit")
    x.add_argument("intent")
    x.add_argument("--label")
    x = un.add_parser("order")
    x.add_argument("unit")
    g = x.add_mutually_exclusive_group(required=True)
    g.add_argument("--before")
    g.add_argument("--first", action="store_true")
    g.add_argument("--last", action="store_true")
    x.add_argument("--label")
    x = un.add_parser("after")
    x.add_argument("unit")
    x.add_argument("deps", nargs="*")
    x.add_argument("--none", action="store_true")
    x.add_argument("--label")
    x = un.add_parser("move")
    x.add_argument("unit")
    x.add_argument("bolt", metavar="bolt|queue")
    x.add_argument("--unblocks", metavar="BOLT")
    x.add_argument("--label")
    x = un.add_parser("drop")
    x.add_argument("unit")
    x.add_argument("reason")
    x.add_argument("--label")
    x = un.add_parser("approve")
    x.add_argument("unit")
    x.add_argument("--label")

    pp = sub.add_parser("plan").add_subparsers(dest="sub", required=True)
    x = pp.add_parser("propose")
    x.add_argument("file")
    x.add_argument("--replaces", type=int)
    x.add_argument("--label")
    x = pp.add_parser("proposed")
    x.add_argument("n", nargs="?", type=int)
    x.add_argument("--label")
    x.add_argument("--json", action="store_true")
    x = pp.add_parser("agree")
    x.add_argument("n", type=int)
    x.add_argument("--team")
    x.add_argument("--label")
    x = pp.add_parser("approve")
    x.add_argument("n", type=int)
    x.add_argument("--label")
    x = pp.add_parser("drop")
    x.add_argument("n", type=int)
    x.add_argument("reason")
    x.add_argument("--label")

    x = sub.add_parser("signal-move", prog="crew signal move")
    x.add_argument("signal", metavar="id")
    x.add_argument("move", choices=CURATION)
    x.add_argument("--target")
    x.add_argument("--reason")
    x.add_argument("--label")
    x = sub.add_parser("signal-show", prog="crew signal show")
    x.add_argument("signal", metavar="id")
    x.add_argument("--label")
    x = sub.add_parser("signal")
    x.add_argument("slug")
    x.add_argument("asserts")
    x.add_argument("--kind", choices=KINDS, help="constraint for an agent, ask for the user, unless given")
    x.add_argument("--subject", help="tags, separated by commas")
    g = x.add_mutually_exclusive_group()
    g.add_argument("--excerpt", help="the words that show it, verbatim, as the session received them")
    g.add_argument("--excerpt-file", help="a file holding them, for words the shell would mangle")
    x.add_argument("--label")

    # What bash crew asks, on the host it has forwarded to.
    x = sub.add_parser("_team-of")
    x.add_argument("unit")
    x.add_argument("--label")
    x = sub.add_parser("_run")
    x.add_argument("unit")
    x.add_argument("stage", choices=("construct", "code", "verify", "merge"))
    x.add_argument("words", nargs="?", default="")
    x.add_argument("--label")
    x = sub.add_parser("_bolt-of")
    x.add_argument("team")
    x = sub.add_parser("_place")
    x.add_argument("team")
    x.add_argument("path")
    x.add_argument("branch")
    x.add_argument("base")
    x = sub.add_parser("_slots")
    x.add_argument("team")
    x = sub.add_parser("_tidy")
    x.add_argument("team")
    x = sub.add_parser("_in-plan")
    x.add_argument("unit")
    x.add_argument("--label")
    x = sub.add_parser("_ends")
    x.add_argument("team")
    x.add_argument("--slot")
    x.add_argument("--waited", action="store_true")
    x.add_argument("--ending", action="store_true")
    return ap


COMMANDS = {
    ("state", "init"): state_init, ("bolts", None): bolts_view,
    ("bolt", "new"): direct(("bolt", "new")), ("bolt", "give"): bolt_give, ("bolt", "order"): direct(("bolt", "order")), ("bolt", "drop"): direct(("bolt", "drop")),
    ("bolt", "land"): bolt_land,
    ("unit", "add"): direct(("unit", "add")), ("unit", "split"): direct(("unit", "split")), ("unit", "amend"): direct(("unit", "amend")),
    ("unit", "order"): direct(("unit", "order")), ("unit", "after"): direct(("unit", "after")),
    ("unit", "move"): direct(("unit", "move")), ("unit", "drop"): direct(("unit", "drop")), ("unit", "approve"): unit_approve,
    ("_team-of", None): team_of_unit, ("_run", None): run_check, ("_bolt-of", None): bolt_of_team, ("_place", None): place_cmd,
    ("_slots", None): slots_cmd, ("_tidy", None): tidy, ("_in-plan", None): in_plan, ("signal", None): signal, ("signal-move", None): signal_move,
    ("signal-show", None): signal_show,
    ("_ends", None): stage_ends,
    ("plan", "propose"): plan_propose, ("plan", "proposed"): plan_proposed, ("plan", "agree"): plan_agree,
    ("plan", "approve"): plan_approve, ("plan", "drop"): plan_drop,
}
# The act a command that moves work records, done or refused. A command that only reads records nothing.
ACTS = {
    ("state", "init"): "state.init", ("bolt", "new"): "bolt.new", ("bolt", "give"): "bolt.give", ("bolt", "order"): "bolt.order",
    ("bolt", "drop"): "bolt.drop", ("bolt", "land"): "bolt.land", ("unit", "add"): "unit.add", ("unit", "split"): "unit.split",
    ("unit", "amend"): "unit.amend",
    ("unit", "order"): "unit.order", ("unit", "after"): "unit.after", ("unit", "move"): "unit.move", ("unit", "drop"): "unit.drop",
    ("unit", "approve"): "unit.approve", ("signal", None): "capture", ("signal-move", None): "signal.move",
    ("_run", None): "stage.start",
    ("plan", "propose"): "plan.propose", ("plan", "agree"): "plan.agree", ("plan", "approve"): "plan.approve",
    ("plan", "drop"): "plan.drop",
}


def named(a):
    """The objects a command names on its command line: a refusal's entry names those."""
    out = [f"unit/{a.unit}"] if getattr(a, "unit", None) else []
    if getattr(a, "unit", None) and getattr(a, "stage", None):
        out.append(f"stage/{a.unit}/{a.stage}")
    if getattr(a, "bolt", None) and a.bolt != "queue":
        out.append(f"bolt/{a.bolt}")
    if getattr(a, "team", None):
        out.append(f"team/{a.team}")
    if a.cmd == "signal-move":
        out.append(f"signals/{a.signal}")
    if a.cmd == "state":
        out.append(f"plan/{a.label}")
    if a.cmd == "plan" and getattr(a, "n", None) is not None:
        out.append(f"proposal/{a.n}")
    return out


def refused(fleet, a, key, e):
    """A refused command that would have moved work, in its partition's run record, with crew's reason."""
    label = CONTEXT.get("label") or getattr(a, "label", None) or os.environ.get("CREW_LABEL")
    if not label and getattr(a, "team", None) in fleet["teams"]:
        label = fleet["teams"][a.team]["label"]
    if label in fleet["partitions"]:
        record.emit(label, ACTS[key], named(a), refused=getattr(e, "recorded", None) or str(e))


def main(argv):
    need_recutils()
    if argv[:2] in (["signal", "move"], ["signal", "show"]):  # crew signal move|show <id>, beside crew signal <slug> "<asserts>"
        argv = [f"signal-{argv[1]}"] + argv[2:]
    args = parser().parse_args(argv)
    fleet = crew.load()
    key = (args.cmd, getattr(args, "sub", None))
    try:
        may_write(fleet, key, args)
        COMMANDS[key](fleet, args)
    except Refusal as e:
        if key in ACTS:
            refused(fleet, args, key, e)
        raise


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
