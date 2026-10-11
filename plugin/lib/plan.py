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
  crew rail [--label L]                      what waits on the user: open proposals, review batches, verify reports
                                             and bolts to land, each with when it began to wait, what answers it and
                                             its card key, with whether a card is open for it; then the open cards
                                             whose row is gone
  crew card session|wait|end <key> [<unit>]  a plannotator session on what the rail row with that card key asks the
                                             user to read, started on this host with no browser and its link printed,
                                             a batch card's one per unit on that unit's team's host; the user's decision
                                             in it, waited for; and its end, which a card's close brings too
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
                                             construct runs again at once on its team's host, its conductor told
  crew unit order <unit> --before <unit>|--first|--last
  crew unit after <unit> <unit>...|--none
  crew unit move <unit> <bolt>|queue [--unblocks <bolt>]
  crew unit drop <unit> "<reason>"
  crew plan propose <file> [--replaces <n>]  the planner's proposal: a Case and the plan commands it would run (Do)
  crew plan proposed [<n>] [--json] [--open] the open proposals, or one as the user reads it; --open writes that to a
                                             file on this host and opens it in plannotator
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
import argparse, contextlib, datetime, fcntl, json, os, pathlib, re, shlex, subprocess, sys, time
# getpass, hashlib, shutil, tempfile and urllib.parse are imported where they are used: every crew command starts this
# module afresh, and those five (OpenSSL, the compression modules) were a third of its start.
from signal import SIGTERM

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
        if not any(os.access(os.path.join(d, c), os.X_OK) for d in os.environ.get("PATH", "").split(os.pathsep) if d):
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
    """recfix --check on a plan or moves file, read from its standard input; the message names what was checked."""
    r = subprocess.run(["recfix", "--check"], input=text, capture_output=True, text=True)
    if r.returncode:
        said = (r.stderr or r.stdout).strip()
        fail(f"{what} fails recfix --check: " + re.sub(r"(?m)^stdin:", pathlib.Path(what).name + ":", said))


def checked(files):
    """recfix --check on every file a commit holds, {path: text}: a .rec file whole, and a signal's or a capture's
    markdown by its frontmatter, which is one record. A comment stands in for the opening ---, so recfix's line
    numbers are the file's."""
    for path, text in files.items():
        if path.endswith(".md"):
            m = re.match(r"^---\n(.*?\n)---\n", text, re.S)
            m or fail(f"{path} has no frontmatter")
            recfix("#\n" + m.group(1), path)
        else:
            recfix(text, path)


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


class Reading:
    """What one command has read on this host, kept for its later steps, so the command fetches each branch and reads
    each kit once however many steps it has (plan.12): the tip of each branch it fetched or pushed, and each kit's
    answer by host. It lives in the folder CREW_READ names when that folder's host file names this host (bash crew
    makes one for a command of several steps, shares it with the steps it starts on this host, and removes it when
    the command ends), else in this process's memory. Inside fresh() nothing is served from it, so a wait looks again
    each time; what is read there is still kept. A reading is never a service or state: it is gone with its command
    (state.4)."""

    def __init__(self):
        self.memory, self.bypass, self.dir = {}, 0, False

    def folder(self):
        if self.dir is False:
            d = os.environ.get("CREW_READ")
            try:
                mine = bool(d) and pathlib.Path(d, "host").read_text().strip() == crew.this_host()
            except OSError:
                mine = False
            self.dir = pathlib.Path(d) if mine else None
        return self.dir

    def held(self, name):
        d = self.folder()
        if d is None:
            return self.memory.get(name)
        try:
            return json.loads((d / name).read_text())
        except (OSError, ValueError):
            return None

    def keep(self, name, value):
        d = self.folder()
        if d is not None:
            try:  # a whole file or none: a step started meanwhile never reads half of one
                tmp = d / f".{name}.{os.getpid()}"
                tmp.write_text(json.dumps(value))
                os.replace(tmp, d / name)
                return
            except OSError:
                self.dir = None
        self.memory[name] = value

    @staticmethod
    def tip_name(repo, ref):
        return "tip-" + re.sub(r"[^A-Za-z0-9.-]", lambda m: f"_{ord(m.group()):x}_", f"{repo} {ref}")

    def tip(self, repo, ref):
        return None if self.bypass else self.held(self.tip_name(repo, ref))

    def keep_tip(self, repo, ref, sha):
        self.keep(self.tip_name(repo, ref), sha)

    def kits(self, host):
        return {} if self.bypass else self.held(f"kits-{host}.json") or {}

    def keep_kits(self, host, answers):
        self.keep(f"kits-{host}.json", dict(self.held(f"kits-{host}.json") or {}, **answers))

    def drop_kit(self, host, main):
        """A step that made or removed a worktree in a kit, or committed in one: the next step reads that kit again."""
        kits = self.held(f"kits-{host}.json") or {}
        if main in kits:
            del kits[main]
            self.keep(f"kits-{host}.json", kits)

    @contextlib.contextmanager
    def fresh(self):
        self.bypass += 1
        try:
            yield
        finally:
            self.bypass -= 1


READ = Reading()


def fetch(repo, ref, fresh=False):
    """The tip of a branch of the repo: the one this command already holds, else fetched now over https and kept; or
    None when the repo has no such branch, which is not kept, so a later step looks again. fresh fetches even when a
    tip is held: after a refused push, and after any push that is not a write's own."""
    held = None if fresh else READ.tip(repo, ref)
    if held:
        return held
    r = git(repo, "fetch", "--quiet", "--no-tags", url(repo), f"+refs/heads/{ref}:refs/crew/{ref}", check=False)
    if r.returncode:
        if "couldn't find remote ref" in r.stderr:
            return None
        fail(f"could not fetch {ref} of {repo} over https: {r.stderr.strip()}")
    tip = git(repo, "rev-parse", f"refs/crew/{ref}")
    READ.keep_tip(repo, ref, tip)
    return tip


def show(repo, tip, path):
    r = git(repo, "show", f"{tip}:{path}", check=False)
    return r.stdout if r.returncode == 0 else None


def commit(repo, parent, files, message):
    """A commit of files' new text ({path: text}) on top of parent, made through a temporary index: no working tree
    is touched, and no other path changes."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        idx = {"GIT_INDEX_FILE": str(pathlib.Path(d) / "index")}
        git(repo, "read-tree", *([parent] if parent else ["--empty"]), env=idx)
        # Every file's blob in one hash-object, and every path into the index in one update-index.
        paths, texts = list(files), []
        for i, path in enumerate(paths):
            texts.append(pathlib.Path(d) / f"blob-{i}")
            texts[-1].write_text(files[path])
        blobs = git(repo, "hash-object", "-w", "--stdin-paths", input="".join(f"{t}\n" for t in texts)).split("\n")
        git(repo, "update-index", "--add", "--index-info", input="".join(f"100644 {b}\t{p}\n" for b, p in zip(blobs, paths)), env=idx)
        tree = git(repo, "write-tree", env=idx)
    return git(repo, "commit-tree", tree, *(["-p", parent] if parent else []), "-F", "-", input=message)


def land(repo, ref, path, make):
    """make(tip) gives a file's new text (or, with path None, {path: text}) and the commit message, or refuses. Every
    file the commit holds is checked first, the carried run record among them. The first attempt starts from the tip
    the command holds; the commit is pushed without force, and when the push is refused because the branch moved, the
    branch is fetched afresh and make runs again on the new tip, up to five times (plan.1, state.1). The command then
    holds the commit it pushed, so its later steps see its own write."""
    tip = fetch(repo, ref)
    for _ in range(1 + REPLAYS):
        text, message = make(tip)
        files = text if path is None else {path: text}
        checked(files)
        sha = commit(repo, tip, files, message)
        r = git(repo, "push", "--quiet", url(repo), f"{sha}:refs/heads/{ref}", check=False)
        if r.returncode == 0:
            git(repo, "update-ref", f"refs/crew/{ref}", sha)
            READ.keep_tip(repo, ref, sha)
            return sha
        moved = fetch(repo, ref, fresh=True)
        if moved == tip:
            fail(f"the push of {ref} to {repo} failed: {r.stderr.strip()}")
        tip = moved
    fail(f"{ref} of {repo} kept moving: the write was applied {1 + REPLAYS} times and each push was refused")


def agent():
    """Who is writing: the agent crew started (CREW_AGENT), else the user at this host."""
    import getpass
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
    with crew's, commit every file it changed with the host's uncarried run record, each file checked first, and push,
    replaying on a refused push. change returns the bolts it touched; each one's conductor is told the subject, unless it wrote it.
    The commit names its run-record entry; with act, that entry is written once pushed, naming on and frm and whatever
    the change added to them. Returns the commit."""
    repo, ref = state_of(fleet, label)
    seen = {"eid": record.new_id()}
    CONTEXT.update(label=label, eid=seen["eid"])

    def make(tip):
        tip or fail(f"{repo} has no {ref} yet: crew state init {label}")
        w = Write(repo, label, tip, read(repo, ref, tip))
        in_step(w.plan)
        before, held = w.plan.teams(), holdings(w.plan)
        touched = change(w) or []
        check(w.plan)
        files = {"plan.rec": w.plan.text(), **w.files}
        seen.update(before=before, after=w.plan.teams(), lost=lost_rows(held, holdings(w.plan)), touched=touched, quiet=w.quiet, label=label,
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


def close_card(row):
    """What the owner of a row is told, or shown, when a change ends the row: to close its card."""
    return f"Close your Pending You card for {row}, if one is open, with what was done."


def either(rows):
    return rows[0] if len(rows) == 1 else ", ".join(rows[:-1]) + " or " + rows[-1]


def holdings(plan):
    """Which team holds each held bolt, and each unit of one: the bolts and units whose rail rows its conductor owns."""
    teams = {b.name(): b.get("Team") for b in plan.bolts() if b.get("Team")}
    return teams, {u.name(): teams[u.get("Bolt")] for u in plan.units() if teams.get(u.get("Bolt"))}


def lost_rows(before, after):
    """The rail rows each team lost in a write, {team: rows}: verify/<unit> for each unit no longer in a bolt it holds,
    and land/<bolt> for each bolt it no longer holds. A landing, a drop and a move all lose rows."""
    (bolts0, units0), (bolts1, units1) = before, after
    out = {}
    for u, t in units0.items():
        if units1.get(u) != t:
            out.setdefault(t, []).append(f"verify/{u}")
    for b, t in bolts0.items():
        if bolts1.get(b) != t:
            out.setdefault(t, []).append(f"land/{b}")
    return out


def notify(fleet, seen, subject):
    """Tell the conductor of each team holding a bolt the write touched, unless that conductor wrote it, or the
    write's own command greets it instead; a team that lost rows of the rail is told to close any card it has open for
    them, or, when its conductor wrote it, that is printed. Tell the partition's dispatchers that are up of a bolt
    added, or of one landed or dropped that frees a team, so a free team gets its next bolt, unless one of them wrote
    it."""
    before, after, touched, lost = seen["before"], seen["after"], seen["touched"], seen.get("lost", {})
    teams = {before.get(b) for b in touched} | {after.get(b) for b in touched} | set(lost)
    for t in sorted(x for x in teams if x and x not in seen["quiet"]):
        if t not in fleet["teams"]:
            continue
        close = f"Close any Pending You card you have open for {either(lost[t])}." if lost.get(t) else ""
        if f"{t}-conductor" != agent():
            crew.tell(fleet, f"{t}-conductor", f"{subject}. {close}" if close else subject)
        elif close:
            print(close)
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
            tip = fetch(repo, ref, fresh=True)
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
        return files, message(f"{subject} ({agent()})", "", eid)
    sha = land(repo, ref, None, make)
    record.emit(label, "state.init", [f"plan/{label}"], commit=[f"{repo}@{sha}"], why=subject, eid=eid)
    return sha


# ------------------------------------------------------------------------------------------ the kits, per host

GATHER = (LIB / "gather.py").read_text()
LATER = ("code", "verify", "merged", "landed")


def gathered(fleet, host, req):
    """gather.py's answer to a request on a host, and None; or None and the last line of why it failed. On this host
    it is read in this process, as the same JSON, sparing a Python start each read; on another it is piped to that
    host's python3, since its crew may be older (code.1)."""
    if host == crew.this_host():
        if os.environ.get("CREW_TEST_READS"):  # crew's tests count a command's reads of the kits, a piped one by its python3
            with open(os.environ["CREW_TEST_READS"], "a") as f:
                f.write(f"{host} gather\n")
        try:
            running = gather.routes() if req.get("sites") else None
            return json.loads(json.dumps({k["main"]: gather.kit(k, req.get("sites"), running, req.get("board")) for k in req["kits"]})), None
        except Exception as e:
            import traceback
            return None, traceback.format_exception_only(e)[-1].strip()
    r = crew.on_machine(fleet, host, ["python3", "-", json.dumps(req)], input=GATHER)
    if r.returncode:
        return None, ((r.stderr or "").strip().splitlines() or [f"exit {r.returncode}"])[-1]
    return json.loads(r.stdout), None


def survey(fleet, held, sites=False, board=False):
    """Read the kits of every host holding active bolts, one call per host. held is [(team, bolt)]. The answer is
    per host: its kits by main checkout, or why it did not answer. With sites, each worktree's devurl names and
    the host's running portless routes too; board implies sites and adds each team's slots and the explorations on
    each kit's main, for the board. Each kit is asked for the verify reports, and with board the slots, of every team
    that builds it on that host. A kit the command has already read is not asked again, and what a host answers is
    kept for the command's later steps; a sites survey is neither served nor kept."""
    sites = sites or board
    hosts = {}
    for team, bolt in held:
        t = fleet["teams"].get(team)
        if not t:
            continue
        mates = sorted(o["name"] for o in fleet["teams"].values() if o["machine"] == t["machine"] and o["kit"]["main"] == t["kit"]["main"])
        k = hosts.setdefault(t["machine"], {}).setdefault(t["kit"]["main"], {"main": t["kit"]["main"], "dir": t["kit"]["dir"], "bolts": [],
            "reports": [f"~/.local/state/{o}-team/reports" for o in mates],
            **({"slots": {o: f"~/.local/state/{o}-team/slots" for o in mates}} if board else {})})
        if bolt and bolt not in k["bolts"]:
            k["bolts"].append(bolt)
    out = {}
    for host, kits in sorted(hosts.items()):
        have = {} if sites else {m: k for m, k in READ.kits(host).items() if m in kits}
        ask = [k for m, k in kits.items() if m not in have]
        if ask:
            req = {"kits": ask, "sites": sites, **({"board": True} if board else {})}
            got, error = gathered(fleet, host, req)
            if error:
                out[host] = {"ok": False, "error": error}
                continue
            if not sites:
                READ.keep_kits(host, {m: k for m, k in got.items() if k.get("ok")})
            have.update(got)
        out[host] = {"ok": True, "kits": have}
    return out


def amended(mark):
    """Whether a unit's Amended mark waits for construct to be run again: proposal/<n> or intent. Any other mark is
    the head of unit/<unit> when construct started again."""
    return mark == "intent" or (mark or "").startswith("proposal/")


def place_stage(pl, mark=None):
    """The stage of a unit that has neither landed nor merged, from its place and its Amended mark. A marked unit is
    amended until construct runs again, and in construct while its head is still where construct started; once that
    construct has committed the mark stops counting (plan.6). Otherwise: verify, code, planned or construct, from its
    tasks and its planning."""
    if mark and (amended(mark) or not pl or pl.get("head") == mark):
        return "amended" if amended(mark) else "construct"
    done, total = pl["tasks"] or (0, 0)
    return "verify" if total and done == total else "code" if done else "planned" if pl["planning"] else "construct"


# The stages at which a unit has finished construct: its change is committed, and a unit after it may be constructed.
CONSTRUCTED = ("planned", "code", "verify", "merged", "landed")


class Stages:
    """Each unit's stage, read from its kit on its team's host. The first rule that holds is the stage:
    landed, merged, then amended or construct for a unit the plan marks amended whose construct has not committed again,
    then verify, code, planned, construct, then ready or waiting by whether its After units have finished construct
    (plan.13); a unit with no bolt is queued, and one whose host does not answer is unknown."""

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
            res["worktree"], res["head"], res["place"] = (pl["path"], pl.get("head"), pl) if pl else (None, None, None)
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
        res["stage"] = "unknown" if "unknown" in deps else ("ready" if all(d in CONSTRUCTED for d in deps) else "waiting")
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
    """A worktree at a fixed path, made with git itself on the team's host and prepared as the kit says. The command's
    next step reads the kit again."""
    host_run(fleet, t["machine"], PLACE, t["kit"]["main"], path, branch, base, "track" if track else "")
    READ.drop_kit(t["machine"], t["kit"]["main"])


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
    READ.drop_kit(t["machine"], t["kit"]["main"])
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
    outside = [u for u, *_ in due_changes(plan, partition_entries(fleet, label)) if u in units]
    not outside or fail(f"bolt {a.bolt} lands only once every unit's latest change has been in a batch, and {either(outside)} "
                        + ("has" if len(outside) == 1 else "have") + f" not: a batch is due for them (crew review {label})")
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
    amended, proposal/<n> inside an approval and intent when the user runs it, and once the write has landed the
    amendment runs its construct again on its team's host, in the name of whoever applied it, and tells its conductor
    what started or why nothing did (plan.15). Merged work is not amended."""
    label, plan = ctx.locate("Unit", a.unit)
    s = unit_stage(ctx.fleet, plan, a.unit)
    s["stage"] not in ("merged", "landed") or fail(
        f"unit {a.unit} has " + ("merged into its bolt" if s["stage"] == "merged" else "landed on main")
        + ", so it is not amended: a defect in it is a fix, and new work is a new unit")
    s["stage"] != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    bolt = plan.unit(a.unit).get("Bolt")
    team = ctx.fleet["teams"].get(plan.bolt(bolt).get("Team")) if bolt else None
    mark = (f"proposal/{ctx.n}" if not ctx.direct else "intent") if s["worktree"] else None
    # The verify row the unit held before the amendment: its card is named when the construct cannot start.
    row = f"verify/{a.unit}" if s["stage"] == "verify" else None

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
        conductor = f"{team['name']}-conductor"
        r = crew.on_machine(ctx.fleet, team["machine"], crew.crew_argv(ctx.fleet, team["machine"], "unit", "run", a.unit, "construct"))
        said = (r.stdout + r.stderr).strip()
        if said:
            print(said)
        if r.returncode == 0:
            m = re.search(rf"^(\S+) has {re.escape(a.unit)}: construct, in ", r.stdout, re.M)
            slot = m.group(1) if m else f"a slot of {team['name']}"
            text = (f"Unit {a.unit}'s intent was amended by {by}, and construct runs again on it in {slot}: wait for it "
                    f"(crew unit wait {a.unit}); once it has committed, the unit goes on from its tasks.")
            unsaid = f"construct runs again on unit {a.unit} in {slot}"
        else:
            why = (crew.unanswered(team["machine"], r)
                   or ((r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1].rstrip("."))
            print(f"construct did not start on unit {a.unit}: {why}")
            text = (f"Unit {a.unit}'s intent was amended by {by}, and construct did not start: {why}. Run it once it can "
                    f"(crew unit run {a.unit} construct); once it has committed, the unit goes on from its tasks."
                    + (f" {close_card(row)}" if row else ""))
            unsaid = f"unit {a.unit} waits, amended, for construct to be run again"
        if not crew.tell(ctx.fleet, conductor, text):
            print(f"{conductor} is not up: {unsaid}")
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
            READ.drop_kit(ft["machine"], ft["kit"]["main"])
            r.returncode != 3 or fail(f"rebasing {a.unit} onto bolt/{to} conflicts: the move is abandoned and the plan is unchanged")
            r.returncode == 0 or fail(f"rebasing {a.unit} on {ft['machine']} failed: {r.stderr.strip()}")
            orig = r.stdout.strip()

            def undo():
                crew.on_machine(ctx.fleet, ft["machine"], ["bash", "-c", UNREBASE, "crew", s["worktree"], orig, src, a.unit])
                READ.drop_kit(ft["machine"], ft["kit"]["main"])
            return undo

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


def refuse(said, recorded):
    """A refusal that quotes typed text: said whole, and in the run record as crew's own words without it (record.3)."""
    e = Refusal(said)
    e.recorded = recorded
    raise e


def do_named(a):
    """A proposal's command as the run record holds it: the command and what it acts on, never its intent or reason."""
    return f"{a.cmd} {a.sub} {a.bolt if a.cmd == 'bolt' else a.unit}"


def do_args(label, do):
    """A proposal's Do as crew's parser reads it: one of the ten plan commands, in the proposal's partition."""
    try:
        argv = shlex.split(do)
    except ValueError as e:
        refuse(f"`{do}`: {e}", f"a Do line does not parse: {e}")
    argv = argv[1:] if argv[:1] == ["crew"] else argv
    held = "a proposal holds only the plan's commands (" + ", ".join(" ".join(k) for k in PROPOSABLE) + ")"
    tuple(argv[:2]) in PROPOSABLE or refuse(f"{held}, not `{do}`", held)
    try:
        a = parser(Strict).parse_args(argv)
    except Refusal as e:
        refuse(f"`{do}`: {e}", f"`{' '.join(argv[:2])}` does not parse as crew's parser reads it")
    getattr(a, "label", None) in (None, label) or refuse(f"`{do}` names partition {a.label}, and the proposal is {label}'s",
                                                         f"`{do_named(a)}` names partition {a.label}, and the proposal is {label}'s")
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
            refuse(f"`{a.do}`: {e}", f"`{do_named(a)}`: {getattr(e, 'recorded', None) or e}")
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
            refuse(f"`{a.do}`: {e}", f"`{do_named(a)}`: {getattr(e, 'recorded', None) or e}")
    try:
        check(scratch.plan)
        checked({"plan.rec": scratch.plan.text(), **scratch.files})
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
            seen["old_by"] = old.get("By")
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
    planner = f"{label}-planner"
    replaced = f"Close your Pending You card for proposal/{a.replaces}, if one is open: proposal {n} replaces it."
    if kind == "planner":
        if a.replaces:
            print(replaced)
        print(f"Post your Pending You card for proposal/{n}.")
    elif a.replaces and seen.get("old_by") == planner:
        tell_planner(fleet, label, f"Proposal {a.replaces} was replaced by proposal {n}, by {agent()}. {replaced}")


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
    carded = p0.get("By") == f"{label}-planner"

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
    tell_planner(fleet, label, f"{', '.join(seen['new'])} agree{'s' if len(seen['new']) == 1 else ''} to proposal {a.n}."
                 + (f" Update your Pending You card for proposal/{a.n}: it no longer waits on "
                    + either([f"{t}-conductor" for t in seen["new"]]) + "." if carded else ""))


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
        state = f"proposal {a.n} is {p.get('State')}"
        p.get("State") == "open" or refuse(state + (f": {p.get('Reason')}" if p.get("Reason") else ""), state)
    opened(p0)
    agreed(w0, p0)
    carded = p0.get("By") == f"{label}-planner"
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
    if carded and agent() == f"{label}-planner":
        print(close_card(f"proposal/{a.n}"))
    elif carded:
        tell_planner(fleet, label, f"Proposal {a.n} was approved by {agent()}. {close_card(f'proposal/{a.n}')}")


def plan_drop(fleet, a):
    """crew plan drop <n> "<reason>": an open proposal closed unapplied, with the reason; the planner is told when
    someone else dropped it."""
    label = proposal_label(fleet, a, a.n)
    CONTEXT["label"] = label

    def change(w):
        pl = proposals(w)
        p = proposal(pl, a.n, label)
        p.get("State") == "open" or fail(f"proposal {a.n} is {p.get('State')}, so it can't be dropped")
        seen["by"] = p.get("By")
        argvs = [do_args(label, d) for d in p.all("Do")]
        p.set("State", "dropped")
        p.set("Closed", datetime.date.today().isoformat(), after="By")
        p.set("Reason", a.reason, after="Closed")
        w.replace("proposals.rec", pl.text())
        w.subject = f"plan(proposal {a.n}): drop"
        w.on += [f"proposal/{a.n}"] + objects(argvs)
        return []
    seen = {}
    write(fleet, label, change, "plan: drop", a.reason, act="plan.drop")
    carded = seen["by"] == f"{label}-planner"
    if carded and agent() == f"{label}-planner":
        print(close_card(f"proposal/{a.n}"))
    said = f"Proposal {a.n} was dropped by {agent()}: {a.reason.strip()}"
    tell_planner(fleet, label, said + (("" if said[-1:] in ".!?" else ".") + f" {close_card(f'proposal/{a.n}')}" if carded else ""))


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
           f", now in {st}" if st in ("construct", "planned", "code", "verify") else f", now {st}")
    return [f"**Amend unit `{a.unit}`** in {where}{now}", f"Intent, as it stands: {u.get('Intent')}", f"Intent, as proposed:  {a.intent}",
            f"On approval: construct runs again at once in {team}'s slot, and once that has committed the unit goes on from "
            "its tasks with no approval asked, its revised change due for the next batch." if s["worktree"] and team else
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


def code_span(text):
    """text as a markdown code span: fenced one backtick longer than its longest run of backticks, with a space inside
    each end when it starts or ends with one (CommonMark's rule)."""
    fence = "`" * (max((len(r) for r in re.findall(r"`+", text)), default=0) + 1)
    pad = " " if text[:1] == "`" or text[-1:] == "`" else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def page(d, label):
    """The markdown of one proposal: each change in plain words with the command approval runs for it, and, while it is
    open, who it waits on, in words."""
    out = [f"# Proposal {d['proposal']} — {d['state']}, by {d['by']}, {d['opened']}", ""]
    if d["replaces"]:
        out += [f"Replaces proposal {d['replaces']}.", ""]
    out += [d["case"], "", "## Changes", ""]
    for i, c in enumerate(d["changes"], 1):
        first, *rest = c["lines"]
        out.append(f"{i}. {first}")
        out += [f"   {l}" for l in rest]
        out.append(f"   Runs: {code_span(c['do'] if c['do'].startswith('crew ') else 'crew ' + c['do'])}")
        out.append("")
    if d["state"] != "open":
        out += [f"Closed {d['closed']}" + (f": {d['reason']}" if d["reason"] else "") + "."]
        return "\n".join(out).rstrip() + "\n"
    out += ["## Waiting on", ""]
    out += [f"- {t}-conductor, to agree, or tell {label}-planner why not" for t in d["waiting"]]
    if d["agreed"]:
        out.append("- agreed: " + ", ".join(d["agreed"]))
    out.append("- the user, to approve it or say what to change")
    return "\n".join(out) + "\n"


def open_proposals(fleet, labels, found=None):
    """Each open proposal of the labels' flywheels, as describe() gives it, with its label. found, when given, is the
    plans already read, as plans() gives them: their tips are used, and a label it lacks is skipped."""
    rows = []
    for l in labels:
        repo, ref = state_of(fleet, l)
        if found is None:
            tip, plan = fetch(repo, ref), None
        else:
            tip, plan = next(((t, p) for x, _, t, p in found if x == l), (None, None))
        text = show(repo, tip, "proposals.rec") if tip else None
        if not text:
            continue
        plan = plan or read(repo, ref, tip)
        for p in Plan(text).recs("Proposal"):
            if p.get("State") == "open":
                rows.append(dict(describe(fleet, l, plan, p), label=l))
    return rows


def plan_proposed(fleet, a):
    """crew plan proposed [<n>] [--label L] [--json] [--open]: the open proposals, or one as the user would read it.
    Reads the flywheels' branches only, so any host can answer. With --open, one proposal's page is written to
    ~/.local/state/crew/proposals/<label>-<n>.md on this host, replacing any earlier copy, and opened in plannotator:
    beside the caller in herdr, inline in the terminal otherwise. The file is a copy for reading; nothing reads it back."""
    if a.open and a.n is None:
        fail("--open needs a proposal's number: crew plan proposed <n> --open")
    if a.open and a.json:
        fail("--open shows the proposal in plannotator and --json prints it: use one")
    label = default_label(fleet, a)
    if a.n is not None:
        label = label or proposal_label(fleet, a, a.n)
        w, _, p, _ = at_tip(fleet, label, a.n)
        d = describe(fleet, label, w.plan, p)
        if a.open:
            f = pathlib.Path.home() / ".local/state/crew/proposals" / f"{label}-{a.n}.md"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(page(d, label))
            argv = ["plannotator-tui", "herdr", "open", str(f)] if os.environ.get("HERDR_ENV") == "1" else ["plannotator-tui", str(f)]
            try:
                sys.exit(subprocess.run(argv).returncode)
            except FileNotFoundError:
                fail(f"plannotator-tui is not on this host's path; the proposal is written to {f}")
        print(json.dumps(d, indent=1) if a.json else page(d, label), end="" if not a.json else "\n")
        return
    rows = [dict(d, waits=[f"{t}-conductor" for t in d["waiting"]] + ["the user"])
            for d in open_proposals(fleet, [label] if label else list(fleet["partitions"]))]
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
    import hashlib
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
        v, sid = check_excerpt(fleet, name, a, excerpt, host)
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
        import getpass
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


def check_excerpt(fleet, name, a, excerpt, host):
    """The agent's excerpt checked against its own Claude session's transcript, which is on this host: crew signal
    is never run on another. The session is the one a forwarded command carries, else herdr's for the agent. A slot's
    agent runs its team's stages, whose own prompts are its conductor's. Returns the verdict and the session id."""
    sess = record.session()
    shost, sid = sess.split(":", 1) if sess and ":" in sess else (host, sess)
    if sid and shost != host:
        return transcript.unverified(f"session {sid} is on {shost}, not {host}"), sid
    skip = [a.excerpt_file, str(pathlib.Path(a.excerpt_file).resolve())] if a.excerpt_file else []
    kind, of = role(fleet, name)
    slot = kind == "team" and re.fullmatch(rf"{re.escape(of)}-unit-[1-9][0-9]*", name)
    return transcript.check(sid, excerpt, skip, f"{of}-conductor" if slot else None), sid


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


def in_bolt(fleet, a):
    """Whether a unit is in a bolt the team holds: said and exit 0 when it is, exit 3 when it is not, and refused when
    the team's plan could not be read, since then nobody can tell."""
    t = crew.team_of(fleet, a.team)
    errors = {}
    found = plans(fleet, [t["label"]], errors)
    not errors or fail(f"can't tell whether unit {a.unit} is still in {t['name']}'s bolt: "
                       + "; ".join(f"{k} could not be read: {v}" for k, v in errors.items()))
    plan = found[0][3]
    u = plan.unit(a.unit) if plan else None
    if u and u.get("Bolt") in {b.name() for b in held_by(plan, t["name"])}:
        print(f"unit {a.unit} is in bolt {u.get('Bolt')}, which {t['name']} holds")
        return
    sys.exit(3)


HEAD = r"""cd "$1" && git rev-parse HEAD"""
# A dependent's place takes the head of each unmerged After unit, as it stands, while it holds nothing of its own beyond
# the bolt and their work: printed as "<unit> <head>" for each it holds. A merge that conflicts is undone, the place put
# back where it was, and printed as "conflict <unit> <paths...>", exit 3. Never a push, never a write to their branches.
TAKE = r"""cd "$1" || exit 1
unit=$2 bolt=$3; shift 3
start=$(git rev-parse HEAD)
refs=(); for a; do refs+=("refs/heads/unit/$a"); done
[ -z "$(git rev-list -n1 HEAD --not "refs/heads/bolt/$bolt" "${refs[@]}")" ] || exit 0
for a; do
  if ! git merge-base --is-ancestor "unit/$a" HEAD; then
    if ! git merge -q --no-edit -m "chore($unit): build on $a as it stands" "unit/$a" >/dev/null 2>&1; then
      paths=$(git diff --name-only --diff-filter=U | tr '\n' ' ')
      git merge --abort >/dev/null 2>&1; git reset -q --keep "$start"
      echo "conflict $a $paths"; exit 3
    fi
  fi
  echo "$a $(git rev-parse --short=7 "unit/$a")"
done
"""


def mark_amended(fleet, label, unit, bolt, head):
    """The plan marks a unit amended at the head construct starts again from, so its code, verify and merge wait until
    what construct writes is committed (plan.6). Returns the write's commit. What the write says goes to standard
    error: bash crew reads standard output as the stage's variables."""
    def change(w):
        u = w.unit(unit)
        u.get("Bolt") == bolt or fail(f"unit {unit} moved to {u.get('Bolt') or 'the queue'} meanwhile")
        u.set("Amended", head)
        return [bolt]
    with contextlib.redirect_stdout(sys.stderr):
        return write(fleet, label, change, f"plan({bolt}): {unit} amended, construct runs again")


def local_entries(label, days=30):
    """This host's run record of the label, from days back, oldest first."""
    runs = record.ROOT / label / "runs" / crew.this_host()
    since = (datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=days)).isoformat()
    out = []
    for f in sorted(runs.glob("*.rec")) if runs.is_dir() else []:
        if f.stem >= since:
            out += record.parse(f.read_text())
    return sorted(out, key=lambda e: (e["At"], e["Id"]))


def verified(label, unit, entries=None):
    """Whether a unit has delivered its verify since it was last constructed or coded, from the run record of the host
    its stages run on: a delivered verify end later than every construct or code start of it."""
    done = None
    for e in entries if entries is not None else local_entries(label):
        if e.get("Refused"):
            continue
        if e.get("Act") == "stage.start" and any(o in e["On"] for o in (f"stage/{unit}/construct", f"stage/{unit}/code")):
            done = False
        elif e.get("Act") == "stage.end" and f"stage/{unit}/verify" in e["On"] and e.get("Ended") == "delivered":
            done = True
    return bool(done)


# ------------------------------------------------------------------------------------------------- Touches

WILD = re.compile(r"[*?]")


def matches(entry, path):
    """Whether a Touches entry, a path or glob relative to the kit's root, matches a path: * and ? within one part of
    the path, ** across parts; a path with no wildcard matches itself and anything under it."""
    entry = entry.strip()
    entry = entry[2:] if entry.startswith("./") else entry
    if not WILD.search(entry):
        e = entry.rstrip("/")
        return path == e or path.startswith(e + "/")
    rx = "".join(".*" if part == "**" else "[^/]*" if part == "*" else "[^/]" if part == "?" else re.escape(part)
                 for part in re.split(r"(\*\*|\*|\?)", entry))
    return re.fullmatch(rx, path) is not None


def overlaps(a, b):
    """Whether two Touches entries overlap: one matches the other, or both are globs whose literal parts up to their
    first wildcard are one the start of the other."""
    if matches(a, b) or matches(b, a):
        return True
    if WILD.search(a) and WILD.search(b):
        pa, pb = WILD.split(a, 1)[0], WILD.split(b, 1)[0]
        return pa.startswith(pb) or pb.startswith(pa)
    return False


def declared(k, unit, why):
    """A unit's Touches entries from its place as read, refused naming what is missing (read.1)."""
    got = (k["places"].get(unit) or {}).get("touches") or {"missing": "crew could not read its proposal"}
    "entries" in got or fail(f"unit {unit}'s {why} is refused: its change must declare what it touches, and {got['missing']}; "
                             f"construct ends proposal.md with `## Touches` and a fenced list of paths or globs")
    return got["entries"]


def overlapping(plan, st_all, k, unit, mine):
    """What a unit's Touches overlap among the unmerged units ahead of it in its bolt that have a place: the prompt's
    words for each, naming the entries and the other unit's change."""
    out = []
    for o in plan.units_of(plan.unit(unit).get("Bolt")):
        if o.name() == unit:
            break
        pl = k["places"].get(o.name())
        if not pl or st_all.of(o.name())["stage"] in ("merged", "landed") or "entries" not in (pl.get("touches") or {}):
            continue
        pairs = [(m, t) for m in mine for t in pl["touches"]["entries"] if overlaps(m, t)]
        if pairs:
            on = "; ".join(m if m == t else f"{m} against {t}" for m, t in pairs)
            out.append(f"Its Touches overlap those of {o.name()}, ahead of it in the bolt and not merged, on {on}; "
                       f"{o.name()}'s change is {pl['path']}/openspec/changes/{o.name()}/.")
    return out


def undeclared(fleet, t, bolt, unit, entries, deps=()):
    """The paths a unit changed against its bolt that no Touches entry matches, its own change's folder aside. A
    dependent's place holds its After units' work as it stood: a path only their commits changed is theirs, not the
    dependent's."""
    main = t["kit"]["main"]
    _, out = kit_git(fleet, t, main, "diff", "--name-only", f"bolt/{bolt}...unit/{unit}")
    paths = [p for p in out.splitlines() if p]
    held = [f"refs/heads/unit/{d}" for d in deps if head_of(fleet, t, main, f"unit/{d}")]
    if held:
        _, mine = kit_git(fleet, t, main, "log", "--format=", "--name-only", "--no-merges", f"unit/{unit}", "--not", f"refs/heads/bolt/{bolt}", *held)
        paths = [p for p in paths if p in set(mine.splitlines())]
    own = f"openspec/changes/{unit}/"
    return [p for p in paths if not p.startswith(own) and not any(matches(e, p) for e in entries)]


def take(fleet, t, place, unit, bolt, deps):
    """A dependent's place takes the head of each unmerged After unit with a branch, as it stands, while it holds
    nothing of its own (TAKE): the heads it holds, as "<unit>@<head>" words for its construct's start. Refused, with the
    place as it was, when two of them conflict."""
    if not deps:
        return ""
    r = crew.on_machine(fleet, t["machine"], ["bash", "-c", TAKE, "crew", place, unit, bolt, *deps])
    READ.drop_kit(t["machine"], t["kit"]["main"])
    if r.returncode == 3:
        _, other, *paths = r.stdout.strip().splitlines()[-1].split()
        fail(f"unit {unit}'s place can't take {other}'s work with the rest it comes after: they conflict on {', '.join(paths)}; "
             "order the units it comes after with crew unit after, then run construct again")
    r.returncode == 0 or fail(f"on {t['machine']}: " + ((r.stderr or r.stdout).strip() or f"exit {r.returncode}"))
    return " ".join(f"{a}@{h}" for a, h in (l.split() for l in r.stdout.strip().splitlines() if l))


def merge_command(t, k, bolt):
    """How a unit or fix merges into its bolt (teams.5): `wt submit bolt/<bolt>` where the kit opts into sluice, its
    pre-merge hooks the submit gate and sluice's verdict the merge gate; else `wt merge bolt/<bolt> --no-squash
    --no-remove`, one merge at a time. Refused when the kit's flag can't be read (read.1)."""
    k or fail(f"can't tell how {t['kit']['name']} merges: its checkout on {t['machine']} was not read")
    k.get("sluice") is not None or fail(f"can't tell whether {t['kit']['name']} merges through sluice: {k.get('sluice_error')}")
    return f"wt submit bolt/{bolt}" if k["sluice"] else f"wt merge bolt/{bolt} --no-squash --no-remove"


def merging(fleet, a):
    """crew _merging <team> <bolt>: the command a fix of the team merges into its bolt with, as a shell assignment
    (MERGE) for bash crew."""
    t = crew.team_of(fleet, a.team)
    k = survey(fleet, [(t["name"], a.bolt)]).get(t["machine"], {})
    kit = k.get("kits", {}).get(t["kit"]["main"]) if k.get("ok") else None
    print(sh(MERGE=merge_command(t, kit if kit and kit.get("ok") else None, a.bolt)))


def run_check(fleet, a):
    """Whether a unit's stage may start, its place (made for construct), and the prompt the stage is sent. Construct
    starts once each After unit has finished construct, never waiting on a merge (plan.13), and is run again at any
    stage before merge; on a unit whose change is committed, or one already amended, it first marks the unit amended in
    the plan at its head. Where that write is what marks the unit, only the conductor of the team holding its bolt, or
    the user, makes it; on a unit whose intent was amended, which the user approved, anyone starts its construct, and
    the prompt carries the amendment's words, read from the mark. Code starts once the change is committed, with no
    review between; code, verify, settle and merge wait while the mark stands (plan.6). Merge waits until each After
    unit has merged (teams.5); settle runs only for a unit that has delivered its verify."""
    label, repo, tip, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))
    u = plan.unit(a.unit)
    bolt = u.get("Bolt") or fail(f"unit {a.unit} is queued: move it into a bolt first")
    t = fleet["teams"][plan.bolt(bolt).get("Team")]
    st_all = Stages(fleet, plan, survey(fleet, [(t["name"], bolt)]))
    s = st_all.of(a.unit)
    st, place, mark = s["stage"], f"{t['kit']['dir']}/places/{a.unit}", u.get("Amended")
    st != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    words = f" {a.words}" if a.words else ""
    amended_at = entry = ""
    if a.stage == "construct":
        if st == "waiting":
            deps = [d for d in u.all("After") if st_all.of(d)["stage"] not in CONSTRUCTED]
            fail(f"unit {a.unit} is waiting: it comes after " + ", ".join(deps) + ", whose change is not committed yet")
        st not in ("merged", "landed") or fail(f"unit {a.unit} has " + ("merged into its bolt" if st == "merged" else "landed on main")
                                               + ": a defect in it is a fix (crew fix), and a new need is a new unit")
        marking = bool(mark) or st in ("planned", "code", "verify")
        if marking and not amended(mark):
            kind, team = role(fleet, os.environ.get("CREW_AGENT"))
            kind == "user" or (kind, team) == ("conductor", t["name"]) or fail(
                f"unit {a.unit} is in {st}, so construct run again marks it amended: a plan write only {t['name']}-conductor "
                "or the user makes")
        # The amendment's words, from the mark, so whoever starts the construct sends the same prompt.
        again = ""
        if mark == "intent":
            again = " This unit's intent was amended by the user; revise the existing change to it."
        elif amended(mark):
            n = mark.split("/", 1)[1]
            case = proposal(Plan(show(repo, tip, "proposals.rec") or PROPOSALS), n, label).get("Case")
            again = (f" This unit's intent was amended by proposal {n}; revise the existing change to it. The planner's case, "
                     f"as the user approved it: {' '.join(case.split())}")
        make_place(fleet, t, place, f"unit/{a.unit}", f"bolt/{bolt}", track=True)
        took = take(fleet, t, place, a.unit, bolt, [d for d in u.all("After") if st_all.of(d)["stage"] not in ("merged", "landed")
                                                   and (st_all.kit(plan.bolt(bolt))[0] or {"places": {}})["places"].get(d)])
        if marking:
            head = s.get("head") or host_run(fleet, t["machine"], HEAD, place)
            if head != mark:
                amended_at, entry = f"{repo}@{mark_amended(fleet, label, a.unit, bolt, head)}", CONTEXT["eid"]
        sources = u.all("Source")
        prompt = f"/opsx:propose {a.unit} {u.get('Intent')}" + (" Sources: " + "; ".join(sources) + "." if sources else "") + again + words
    elif st in ("amended", "construct") and mark:
        fail(f"unit {a.unit} was amended and " + (f"construct has not been run again (crew unit run {a.unit} construct)" if st == "amended"
                                                  else "its change is being written again, and has not been committed"))
    elif a.stage == "code":
        st in ("planned", "code", "verify") or fail(f"unit {a.unit} is in {st}: " + (
            "code waits until its change is committed" if st == "construct" else "it has no change to code yet"))
        k, _ = st_all.kit(plan.bolt(bolt))
        told = overlapping(plan, st_all, k, a.unit, declared(k, a.unit, "code"))
        prompt = f"/opsx:apply {a.unit}{words}" + "".join(" " + x for x in told)
    elif a.stage == "verify":
        if st == "code":
            n = len(s["open"])
            refuse(f"unit {a.unit} is in code, with these tasks still open: " + "; ".join(s["open"]),
                   f"unit {a.unit} is in code, with {n} task{'' if n == 1 else 's'} still open")  # titles are typed text
        st == "verify" or fail(f"unit {a.unit} is in {st}: verify waits until every task is ticked")
        k, _ = st_all.kit(plan.bolt(bolt))
        got = (k["places"].get(a.unit) or {}).get("touches") or {}
        loose = undeclared(fleet, t, bolt, a.unit, got.get("entries", []), u.all("After"))
        prompt = f"/opsx:verify {a.unit}{words}" + (
            (" Changed and not declared in its Touches: " + ", ".join(loose) + "."
             + ("" if "entries" in got else f" Its change declares no Touches: {got.get('missing')}.")) if loose else "")
    elif a.stage == "settle":
        st == "verify" and verified(label, a.unit) or fail(
            f"unit {a.unit} is in {st}" + (", and has not delivered its verify" if st == "verify" else "")
            + ": settle runs only for a unit that has delivered its verify and waits to merge")
        a.words or fail(f"settle {a.unit} with what reached it: crew unit run {a.unit} settle \"<the forecast or the amendment>\"")
        prompt = f"Settle {a.unit}:{words}"
    else:
        st == "verify" or fail(f"unit {a.unit} is in {st}: it merges once every task is ticked and verify has run")
        ahead = [d for d in u.all("After") if st_all.of(d)["stage"] not in ("merged", "landed")]
        not ahead or fail(f"unit {a.unit} merges after " + ", ".join(ahead) + ", not yet merged into bolt/" + bolt)
        prompt = f"Merge {a.unit} into bolt/{bolt}: {merge_command(t, st_all.kit(plan.bolt(bolt))[0], bolt)}{words}"
    # What reached the unit while no stage of it ran: forecasts, carried in this stage's prompt and named on its start.
    ids, said = carried_forecasts(fleet, t, plan, st_all, bolt, a.unit)
    prompt += "".join(" " + x for x in said)
    # The rail row the stage ends, whose card the conductor closes: a verify report acted on; for a unit whose intent
    # was amended, the verify row its place reads without the mark, which the amendment ended. Bash crew names the card
    # once the stage has started (stage_ended_row), since starting it can still be refused.
    if a.stage == "construct" and amended(mark):
        was = place_stage(s["place"]) if s.get("place") else None
        ends = f"verify/{a.unit}" if was == "verify" else ""
    else:
        ends = f"verify/{a.unit}" if a.stage in ("construct", "code", "merge") and st == "verify" else ""
    # A construct that marked the unit amended: the plan's commit, and the entry it names, which the stage's start is.
    print(sh(PLACE=place, BOLT=bolt, PROMPT=prompt, AMENDED=amended_at, ENDS=ends, ENTRY=entry, FORECAST=" ".join(ids),
             TOOK=took if a.stage == "construct" else ""))


def stage_ended_row(fleet, a):
    """A started stage that ended a rail row names the row's card to the conductor that owns it: shown to the
    conductor when it ran the stage, told to it otherwise."""
    conductor = f"{crew.team_of(fleet, a.team)['name']}-conductor"
    if agent() == conductor:
        print(close_card(a.row))
    else:
        crew.tell(fleet, conductor, f"{agent()} ran {a.stage} on unit {a.unit}. {close_card(a.row)}")


def amended_units(fleet, a):
    """The line a team's conductor is greeted with, or sent on crew resume, naming each unit of its bolt whose stage is
    amended, which no construct has run on since: nothing when there is none. When the plan or the bolt's kit cannot
    be read it says so, rather than name no unit (read.1), and still exits 0, so the greeting goes out."""
    t = crew.team_of(fleet, a.team)
    CONTEXT["label"] = t["label"]
    errors, names, unread = {}, [], []
    found = plans(fleet, [t["label"]], errors)
    unread += [f"{k} could not be read: {v}" for k, v in errors.items()]
    plan = found[0][3] if found else None
    held = held_by(plan, t["name"]) if plan else []
    if held:
        st = stages_for(fleet, plan, held)  # one survey of the team's host (plan.12)
        for b in held:
            for u in plan.units_of(b.name()):
                s = st.of(u.name())
                if s["stage"] == "amended":
                    names.append(u.name())
                elif s["stage"] == "unknown" and s.get("why") and s["why"] not in unread:
                    unread.append(s["why"])
    said = []
    if len(names) == 1:
        said.append(f"Unit {names[0]} was amended and no construct runs on it: run construct on it now "
                    f"(crew unit run {names[0]} construct).")
    elif names:
        said.append(f"Units {', '.join(names)} were amended and no construct runs on them: run construct on each now "
                    "(crew unit run <unit> construct).")
    if unread:
        why = " ".join("; ".join(unread).split())  # one line, though git's own words may span several
        said.append(f"crew could not read whether a unit of your bolt waits amended ({why}): read crew bolts.")
    if said:
        print(" ".join(said))


def bolt_of_team(fleet, a):
    t = crew.team_of(fleet, a.team)
    repo, ref = state_of(fleet, t["label"])
    tip = fetch(repo, ref) or fail(f"{repo} has no {ref} yet: crew state init {t['label']}")
    held = held_by(read(repo, ref, tip), t["name"])
    held or fail(f"{t['name']} holds no bolt: crew bolt give {t['name']}")
    print(sh(BOLT=held[0].name()))


def place_cmd(fleet, a):
    make_place(fleet, crew.team_of(fleet, a.team), a.path, a.branch, a.base, track=True)


def not_the_bolts(bolt, fix):
    """Why a fix's commits beyond main are not the bolt's replayed in order, or None when they are: as many, and in each
    place the bolt's commit's message and author. Commits are matched by those, each used once, oldest first, and the
    reason names each commit of either side left without a match by short sha and subject."""
    if len(bolt) == len(fix) and all(b["who"] == f["who"] for b, f in zip(bolt, fix)):
        return None
    left, lone = list(fix), []
    for b in bolt:
        i = next((i for i, f in enumerate(left) if f["who"] == b["who"]), None)
        if i is None:
            lone.append(b)
        else:
            del left[i]
    named = lambda cs: ", ".join(f"{c['short']} ({c['subject']})" for c in cs)
    why = []
    if lone:
        why.append(f"the bolt's commit{'s' if len(lone) > 1 else ''} {named(lone)} {'are' if len(lone) > 1 else 'is'} not in it")
    if left:
        why.append(f"its commit{'s' if len(left) > 1 else ''} {named(left)} {'are' if len(left) > 1 else 'is'} none of the bolt's")
    return "; ".join(why) or "its commits are the bolt's in another order"


def kit_git(fleet, t, where, *args, ok=(0,)):
    """git in a checkout of the team's kit, on the team's host: (exit status, output); refused in git's words when it
    exits with a status outside ok."""
    r = crew.on_machine(fleet, t["machine"], ["git", "-C", where, *args])
    r.returncode in ok or fail(f"git {args[0]} in {where} on {t['machine']} failed: "
                               + ((r.stderr or r.stdout).strip() or f"exit {r.returncode}"))
    return r.returncode, r.stdout.strip()


def head_of(fleet, t, where, ref):
    """The commit a branch of the kit is at, or None when there is no such branch."""
    rc, out = kit_git(fleet, t, where, "rev-parse", "--verify", "-q", f"refs/heads/{ref}^{{commit}}", ok=(0, 1))
    return out if rc == 0 and out else None


def commits_beyond(fleet, t, where, base, head):
    """The commits from base to head, oldest first, each with its sha, short sha, subject, and what makes it that commit
    (who): its author's name and email and its whole message as git stores it. One git log, each commit ended by NUL,
    which no message holds, and its fields by newlines, which no sha, subject, name or email holds."""
    out = kit_git(fleet, t, where, "log", "--reverse", "--topo-order", "--no-show-signature", "-z", "--abbrev=7",
                  "--format=%H%n%h%n%s%n%an%n%ae%n%B", f"{base}..{head}")[1]
    commits = []
    for rec in out.split("\0")[:-1]:
        f = rec.split("\n", 5)
        len(f) == 6 or fail(f"git log of {base[:7]}..{head[:7]} in {where} printed a commit crew cannot read: {rec[:80]!r}")
        commits.append({"sha": f[0], "short": f[1], "subject": f[2], "who": (f[3], f[4], f[5])})
    return commits


def patch_ids(fleet, t, where, base, *heads):
    """Each commit's patch id from base to each head, by sha: git patch-id --stable over git log -p, on the team's host.
    A commit whose patch is empty has none."""
    text = "".join(kit_git(fleet, t, where, "log", "-p", "--no-color", "--no-ext-diff", "--format=commit %H", f"{base}..{h}")[1]
                   + "\n" for h in heads)
    r = crew.on_machine(fleet, t["machine"], ["git", "-C", where, "patch-id", "--stable"], input=text)
    r.returncode == 0 or fail(f"git patch-id in {where} on {t['machine']} failed: " + ((r.stderr or r.stdout).strip() or f"exit {r.returncode}"))
    ids = {}
    for line in r.stdout.splitlines():
        m = re.fullmatch(r"([0-9a-f]+) ([0-9a-f]+)", line)
        m or fail(f"git patch-id in {where} printed a line crew cannot read: {line!r}")
        ids[m.group(2)] = m.group(1)
    return ids


def range_reading(fleet, t, where, base, old, new, bolt, fix):
    """git range-diff of the bolt's commits beyond main and the fix's, on standard error as git printed it: the reading
    the conductor can look at, which decides nothing and which crew does not parse (plan.8). When range-diff fails, as
    it does on a side with no commits beyond main, it is named in git's words, up to the usage git prints after them."""
    ranges = f"main..bolt/{bolt} main..{fix}"
    r = crew.on_machine(fleet, t["machine"], ["git", "-C", where, "range-diff", "--no-color", "--no-patch", f"{base}..{old}", f"{base}..{new}"])
    if r.returncode:
        words = (r.stderr or r.stdout).strip().split("\n\n")[0]
        print(f"git range-diff {ranges} could not be read: " + (words or f"exit {r.returncode}"), file=sys.stderr)
        return
    print(f"git range-diff {ranges}, the reading, which judges nothing: crew judges by each commit's message and author, in order", file=sys.stderr)
    if r.stdout.strip():
        print(r.stdout.rstrip("\n"), file=sys.stderr)


# What keeps a worktree from moving, by the file its git dir holds while it is in progress.
IN_PROGRESS = (("rebase-merge", "a rebase"), ("rebase-apply", "a rebase"), ("MERGE_HEAD", "a merge"), ("CHERRY_PICK_HEAD", "a cherry-pick"))


def carry_move(fleet, t, fix, bolt, old, new):
    """The bolt's branch moved to the fix's head, in the bolt's worktree, by git reset --keep, which discards nothing
    (code.6): only while that worktree is on bolt/<bolt> with nothing uncommitted and nothing in progress, and both
    heads are still where the judgment read them."""
    wt, main, name = f"{t['kit']['dir']}/bolts/{bolt}", t["kit"]["main"], fix.rsplit("/", 1)[-1]
    again = f"then run crew fix {t['name']} {name} --merge again"
    rc, _ = kit_git(fleet, t, wt, "rev-parse", "--git-dir", ok=(0, 128))
    rc == 0 or fail(f"bolt/{bolt} is not moved: its worktree {wt} is not there")
    for path, what in IN_PROGRESS:
        _, at = kit_git(fleet, t, wt, "rev-parse", "--path-format=absolute", "--git-path", path)
        crew.on_machine(fleet, t["machine"], ["test", "-e", at]).returncode != 0 or fail(
            f"bolt/{bolt} is not moved: its worktree {wt} has {what} in progress; finish or abort it, {again}")
    _, on = kit_git(fleet, t, wt, "branch", "--show-current")
    on == f"bolt/{bolt}" or fail(f"bolt/{bolt} is not moved: its worktree {wt} is on {on or 'no branch'}, not bolt/{bolt}")
    _, status = kit_git(fleet, t, wt, "status", "--porcelain")
    if status:
        paths = [l.split(None, 1)[-1] for l in status.splitlines()]
        fail(f"bolt/{bolt} is not moved: its worktree {wt} has uncommitted changes (" + ", ".join(paths[:5])
             + (f" and {len(paths) - 5} more" if len(paths) > 5 else "") + f"); commit or remove them, {again}")
    for ref, was in ((f"bolt/{bolt}", old), (fix, new)):
        now = head_of(fleet, t, main, ref)
        now == was or fail(f"bolt/{bolt} is not moved: {ref} moved from {was[:7]} to {(now or 'nothing')[:7]} since crew read it; {again}")
    kit_git(fleet, t, wt, "reset", "-q", "--keep", new)
    READ.drop_kit(t["machine"], main)


def carry_cmd(fleet, a):
    """Whether a fix carries its bolt onto main, as shell assignments for bash crew (teams.9): CARRIES=yes with the
    bolt's head (OLD), the fix's (NEW), how many of the bolt's commits it carries (COMMITS) and how many the
    resolution changed (CHANGED); or CARRIES=no and why not (WHY). It carries when the bolt's head is not in the fix,
    and the fix holds as many commits beyond the kit's main as the bolt, in order each the bolt's commit in the same
    place replayed: the same message and author, its patch the same or changed, by patch id (plan.8). Whenever the fix
    does not hold the bolt's head, git range-diff of the two is printed on standard error as the reading, before and
    whatever the judgment, deciding nothing. With --move, the bolt's branch is moved to the fix's head."""
    t = crew.team_of(fleet, a.team)
    main = t["kit"]["main"]
    if a.move:
        return carry_move(fleet, t, a.fix, a.bolt, *a.move)
    heads = {ref: head_of(fleet, t, main, ref) for ref in (f"bolt/{a.bolt}", a.fix, "main")}
    missing = [ref for ref, sha in heads.items() if not sha]
    not missing or fail(f"can't tell whether {a.fix} carries bolt/{a.bolt} onto main: {main} has no " + " and no ".join(missing))
    old, new, base = heads[f"bolt/{a.bolt}"], heads[a.fix], heads["main"]
    no = lambda why: print(sh(CARRIES="no", WHY=why))
    rc, _ = kit_git(fleet, t, main, "merge-base", "--is-ancestor", old, new, ok=(0, 1))
    if rc == 0:
        return no("it holds the bolt's head")
    range_reading(fleet, t, main, base, old, new, a.bolt, a.fix)
    bolt = commits_beyond(fleet, t, main, base, old)
    if not bolt:
        return no(f"bolt/{a.bolt} has no commits beyond main")
    fix = commits_beyond(fleet, t, main, base, new)
    if not fix:
        return no("it has no commits beyond main")
    why = not_the_bolts(bolt, fix)
    if why:
        return no(why)
    ids = patch_ids(fleet, t, main, base, old, new)
    changed = sum(ids.get(b["sha"]) != ids.get(f["sha"]) for b, f in zip(bolt, fix))
    print(sh(CARRIES="yes", OLD=old, NEW=new, COMMITS=len(bolt), CHANGED=changed))


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
    merged is dropped when the plan was read and has no such unit, or no bolt the fix's branch tracks; a unit the plan
    has outside every bolt the team holds, queued again or moved to another bolt, has left."""
    path = pathlib.Path.home() / f".local/state/{t['name']}-team/slots"
    held = [l.split() for l in (path.read_text().splitlines() if path.exists() else []) if l.strip()]
    if not held:
        return []
    k = survey(fleet, [(t["name"], None)]).get(t["machine"], {})
    kit = k.get("kits", {}).get(t["kit"]["main"], {}) if k.get("ok") else {}
    plan = plan_of(fleet, t["label"])
    marks = {u.name(): u.get("Amended") for u in plan.units() if u.get("Amended")} if plan else {}
    bolts = {b.name() for b in held_by(plan, t["name"])} if plan else set()
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
            elif plan and plan.unit(name).get("Bolt") not in bolts:
                stage = "left"
            elif pl:
                stage = place_stage(pl, marks.get(name))
                counts = "{}/{}".format(*pl["tasks"]) if pl["tasks"] else None
            else:
                stage = "none"
        out.append(dict(slot=slot, kind=kind, name=name, stage=stage, counts=counts, place=place))
    return out


@contextlib.contextmanager
def silenced():
    """Standing for a step bash ran with its output thrown away and its failure ignored (`>/dev/null 2>&1 || true`): what
    it and the processes it starts write goes nowhere, and a refusal or error in it is dropped."""
    sys.stdout.flush(), sys.stderr.flush()
    saved = os.dup(1), os.dup(2)
    null = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(null, 1), os.dup2(null, 2)
        yield
    except Exception:
        pass
    finally:
        sys.stdout.flush(), sys.stderr.flush()
        os.dup2(saved[0], 1), os.dup2(saved[1], 2)
        for fd in (null, *saved):
            os.close(fd)


def slots_cmd(fleet, a):
    """Each slot of the team on this host: what it holds and that work's stage, read from the kit and the plan's marks.
    With --ends, the ends the team's stages file owes are recorded first, as `_ends <team>` records them, its output and
    any failure dropped: one process for a team's read where there were two."""
    t = crew.team_of(fleet, a.team)
    if a.ends and (team_state(t) / "stages").exists() and (team_state(t) / "stages").stat().st_size:
        with silenced():
            stage_ends(fleet, argparse.Namespace(team=a.team, slot=None, ending=False))
    for s in slot_stages(fleet, t):
        tasks = s["counts"] if s["counts"] and s["stage"] in ("code", "verify") else "-"
        print(s["slot"], s["kind"], s["name"], s["stage"], tasks, s["place"])


def tidy(fleet, a):
    """Each worktree crew made in the team's kit checkout, on this host, whose work is over and that no slot holds:
    removed with its branch, saying the commit the branch was at; or kept and named, with its branch, while it is
    locked or has uncommitted changes. The removal goes through the kit's own `wt remove`, run from the kit's main
    checkout and leaving the branch to crew, so the kit's remove hooks run; one wt refuses, a hook having failed or
    waiting for the user's approval on this host, one wt leaves standing, or with no wt on this host's path, is kept
    and named with its branch, and the next read tries it again; when crew can't read from wt that it left the branch
    alone, the branch is kept and said. crew made it when it is directly in <kit>/bolts/ on bolt/<its folder>, or
    directly in <kit>/places/ on unit/<its folder> or a fix/ branch; nothing else is touched. The worktrees are listed
    before the slots and plans are read: a plan has a bolt, a unit or a fix's bolt, and a slot is taken, before crew
    makes the worktree, so whatever is listed was planned or held by then. Nothing is removed when a plan the kit's
    work goes in can't be read. Once a worktree is removed, the command's next step reads the kit again."""
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
        kept = f"{path} is kept, and {branch} with it: {over}, and "
        try:  # the clean check above is the guard, so --force; the branch is crew's, so --no-delete-branch
            r = subprocess.run(["wt", "-C", main, "remove", path, "--foreground", "--no-delete-branch", "--force", "--format", "json"],
                               capture_output=True, text=True, stdin=subprocess.DEVNULL,
                               env={k: v for k, v in gitenv().items() if not k.startswith("WORKTRUNK_")})
        except FileNotFoundError:
            print(kept + f"wt, the kit's worktree tool, is not on {crew.this_host()}'s path")
            continue
        if r.returncode:
            said = [l.strip() for l in r.stderr.splitlines() if l.strip() and not l.strip().startswith("↳")]  # ↳ advises --no-hooks or --yes
            if any("Cannot prompt for approval" in l for l in said):
                print(kept + f"the kit's remove hooks wait for the user's approval on {crew.this_host()}: wt config approvals add, in {main}")
            else:
                print(kept + "the kit's wt remove refused it: " + "; ".join(
                    [l[1:].strip() for l in said if l.startswith("✗")] or said[-1:] or [f"wt remove exited {r.returncode}"]))
            continue
        READ.drop_kit(t["machine"], t["kit"]["main"])  # the command's next step reads the kit again
        if os.path.isdir(path):
            print(kept + "the kit's wt remove exited 0 and left it there")
            continue
        try:
            told = json.loads(r.stdout)
            left = (len(told) == 1 and os.path.realpath(told[0]["path"]) == os.path.realpath(path)
                    and told[0]["branch_outcome"] == "not_attempted")
        except (ValueError, TypeError, KeyError, IndexError):
            left = False
        if not left:
            print(f"{path} is removed, and {branch} is kept: crew could not read what wt remove said of the branch")
            continue
        r = subprocess.run(["git", "-C", main, "branch", "-q", "-D", branch], capture_output=True, text=True, env=gitenv())
        print(f"{path} and {branch} are removed; the branch was at {sha}" if r.returncode == 0 else
              f"{path} is removed, and {branch} is kept: {r.stderr.strip()}")


# ------------------------------------------------------------------------------------------ a stage's end

def team_state(t):
    """The team's state folder on its host: its slots, panes, stages, reports, waits and stop-shorts."""
    return pathlib.Path.home() / f".local/state/{t['name']}-team"


def started(eid):
    """When a stage began: the UTC second at the front of its start entry's id, or None when the id holds none."""
    try:
        return datetime.datetime.strptime(eid[:16], "%Y%m%dT%H%M%SZ").replace(tzinfo=datetime.timezone.utc)
    except (TypeError, ValueError):
        return None


class Owed:
    """A stage crew owes an end, from its line in the team's stages file: <slot> <unit, fix branch or bolt> <stage>
    <start entry id> <object>. A unit's stages are construct, code, verify, settle and merge; a fix's, fix and merge, its name
    its branch and its object fix/<bolt>/<name>; ops's proof of a bolt is proof, in the slot ops."""

    def __init__(self, t, fields):
        self.t, self.fields = t, list(fields)
        self.slot, self.name, self.stage, self.eid, self.obj = (self.fields + [""] * 5)[:5]
        self.agent = f"{t['name']}-{self.slot}"
        self.start = started(self.eid)
        self.proof = self.stage == "proof"
        self.fix = not self.proof and self.name.startswith("fix/")

    def branch(self):
        """The branch whose head an end names: the unit's, the fix's, or the proven bolt's."""
        return self.name if self.fix else f"bolt/{self.name}" if self.proof else f"unit/{self.name}"

    def phrase(self):
        """The stage as the wait names it."""
        if self.proof:
            return f"the proof of {self.name}"
        if self.fix:
            return f"fix {self.obj or self.name}" if self.stage == "fix" else f"{self.stage} of {self.obj or self.name}"
        return f"{self.stage} on {self.name}"

    def on(self):
        if self.proof:
            return [f"stage/{self.name}/proof", f"bolt/{self.name}", f"agent/{self.agent}"]
        if self.fix:
            return [self.obj or self.name, f"agent/{self.agent}"]
        return [f"stage/{self.name}/{self.stage}", f"unit/{self.name}", f"agent/{self.agent}"]

    def why(self, ended):
        how = "stopped short" if ended == "short" else "ended"
        if self.proof:
            return f"bolt({self.name}): proof {how}"
        if self.fix:
            return f"fix({self.name.rsplit('/', 1)[-1]}): {self.stage} {how}"
        return f"unit({self.name}): {self.stage} {how}"


def short_head(main, ref):
    return (gather.run(["git", "rev-parse", "--short", "--verify", "-q", ref], main) or "").strip()


def committed_at(main, ref):
    """When a branch's head was committed, in UTC, or None."""
    at = gather.head_at(main, ref)
    try:
        return datetime.datetime.fromisoformat(at).astimezone(datetime.timezone.utc) if at else None
    except ValueError:
        return None


def ticks(main, branch, unit):
    """A unit's tasks at its branch's head, done and total, read from the commit and not the working tree, by the
    reading every other reader of a unit's tasks uses (gather.tasks_of)."""
    tasks = gather.tasks_of(gather.run(["git", "show", f"{branch}:openspec/changes/{unit}/tasks.md"], main) or "")
    return sum(done for done, _ in tasks), len(tasks)


def newest_saved(t, pattern, name, since):
    """The newest file in the team's reports folder that the pattern names for name, modified at or after since."""
    best = None
    folder = team_state(t) / "reports"
    for f in (folder.iterdir() if folder.is_dir() else []):
        m = pattern.match(f.name)
        try:
            at = f.stat().st_mtime if m and m.group(1) == name else None
        except OSError:
            continue
        if at is not None and at >= since.timestamp() and (best is None or at > best[0]):
            best = (at, f)
    return best[1] if best else None


def bolt_of_unit(fleet, t, main, unit):
    """The bolt a unit's branch was made from and merges into, from its upstream; else the bolt the team holds."""
    up = gather.upstreams(main).get(f"unit/{unit}", "")
    if up.startswith("bolt/"):
        return up[5:]
    plan = plan_of(fleet, t["label"])
    held = held_by(plan, t["name"]) if plan else []
    return held[0].name() if held else None


def deliverable(fleet, t, o, place=None):
    """What an owed stage has delivered since it began, read on the team's host: (its object, what the wait says of
    it), or (None, what is missing). construct: a commit on the unit's branch since the start, with its planning
    complete; code: a commit since the start, every task ticked at the head; verify: a report for the unit saved since
    the start; settle: a commit on the unit's branch since the start (teams.14); merge: the bolt holding the unit's
    change, or the fix's commits; a fix: a commit on its branch since the start; the proof: a proof file for the bolt
    saved since the start. A start crew can't read delivers nothing."""
    main = t["kit"]["main"]
    if o.start is None:
        return None, f"no start crew can read in its entry {o.eid}"
    if o.proof:
        f = newest_saved(t, gather.PROOF, o.name, o.start)
        return (f"proof/{f.name}", str(f)) if f else (None, "no proof file saved")
    if o.stage == "verify":
        f = newest_saved(t, gather.REPORT, o.name, o.start)
        return (f"report/{f.name}", f"the report is {f}") if f else (None, "no report saved")
    if o.stage == "merge":
        bolt = o.obj.split("/")[1] if o.fix and o.obj.count("/") == 2 else None if o.fix else bolt_of_unit(fleet, t, main, o.name)
        if not bolt:
            return None, "no bolt crew can read for it"
        holds = gather.fix_merged(main, o.name, bolt) if o.fix else o.name in gather.changes(main, f"bolt/{bolt}")
        head = short_head(main, f"refs/heads/bolt/{bolt}")
        return (f"bolt/{bolt}@{head}", f"bolt/{bolt} holds it at {head}") if holds and head else (None, f"bolt/{bolt} not yet holding it")
    head, at = short_head(main, f"refs/heads/{o.branch()}"), committed_at(main, f"refs/heads/{o.branch()}")
    fresh = bool(head) and at is not None and at >= o.start
    if o.fix:
        return (f"{o.obj or o.name}@{head}", f"its branch is at {head}") if fresh else (None, "nothing committed since it began")
    if o.stage == "settle":
        return (f"unit/{o.name}@{head}", f"its branch is at {head}, ready to merge") if fresh else (None, "nothing committed since it began")
    if o.stage == "code":
        done, total = ticks(main, o.branch(), o.name)
        if fresh and total and done == total:
            return f"unit/{o.name}@{head}", f"every task is ticked ({done}/{total}) at {head}"
        return None, (f"{done} of {total} tasks ticked at its head" if total and done < total else
                      "no commit since it began" if total else "no task list at its head")
    if not fresh:
        return None, "nothing committed"
    place = place or f"{t['kit']['dir']}/places/{o.name}"
    planned = gather.planned(f"{place}/openspec/changes/{o.name}", place)
    if planned is None:
        status = gather.run(["openspec", "status", "--change", o.name, "--json"], place)
        try:
            planned = bool(json.loads(status).get("isPlanningComplete")) if status else False
        except (ValueError, AttributeError):
            planned = False
    return (f"unit/{o.name}@{head}", f"its change is committed at {head}") if planned else (None, "its planning not complete")


@contextlib.contextmanager
def stages_file(t, shared=False):
    """The team's stages file under its lock (teams.9), as its lines split into fields. Under the exclusive lock the
    caller may change the list, and what it leaves is written back."""
    path = team_state(t) / "stages"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    with open(path, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_SH if shared else fcntl.LOCK_EX)
        lines = [l.split() for l in f.read().splitlines() if l.strip()]
        before = [list(l) for l in lines]
        yield lines
        if not shared and lines != before:
            f.seek(0)
            f.truncate()
            f.write("".join(" ".join(l) + "\n" for l in lines))


def record_end(fleet, t, o, ended, delivered=None, late=False, now=None):
    """One owed stage's stage.end: how it ended (delivered, short or stopped), what it delivered, and the stage, tasks
    and head crew then reads from the kit. now is slot_stages' answer when the caller has it."""
    main = t["kit"]["main"]
    if o.proof:
        result = tasks = None
    else:
        s = (now if now is not None else {x["slot"]: x for x in slot_stages(fleet, t)}).get(o.slot, {})
        result, tasks = s.get("stage", "unknown"), s.get("counts")
    record.emit(t["label"], "stage.end", o.on(), why=o.why(ended), Result=result, Tasks=tasks,
                Head=short_head(main, f"refs/heads/{o.branch()}"), Ended=ended, Delivered=delivered,
                Observed="late" if late else None)


def unmark(fleet, t, o):
    """Once an amended unit's construct has delivered, its mark stops counting, and crew removes it from the plan in a
    write that carries the construct's end (plan.6). A mark that still waits for construct, one set again meanwhile, or
    a write that fails is said on standard error and changes nothing else: the mark no longer counts either way."""
    if o.proof or o.fix or o.stage != "construct":
        return
    plan = plan_of(fleet, t["label"])
    u = plan.unit(o.name) if plan else None
    mark = u.get("Amended") if u else None
    if not mark or amended(mark):
        return

    def change(w):
        v = w.unit(o.name)
        v.get("Amended") == mark or fail(f"unit {o.name} was marked again since its construct ended")
        v.drop("Amended")
        w.quiet.add(t["name"])  # its conductor learns the end from its wait, not from this write
        return [v.get("Bolt")] if v.get("Bolt") else []
    try:
        with contextlib.redirect_stdout(sys.stderr):
            write(fleet, t["label"], change, f"plan({u.get('Bolt')}): {o.name} constructed again, its mark cleared")
    except Refusal as e:
        print(f"unit {o.name}'s Amended mark is left in the plan, and no longer counts: {e}", file=sys.stderr)


def end_owed(fleet, t, o, ended, delivered=None, then=None):
    """Record an owed stage's end and remove its line, under the stages file's lock, unless another command recorded
    it first. then(lines) runs under the same lock once the end is recorded. Returns whether this call recorded it."""
    with stages_file(t) as lines:
        i = next((i for i, l in enumerate(lines) if l[3:4] == [o.eid]), None)
        if i is None:
            return False
        record_end(fleet, t, o, ended, delivered)
        del lines[i]
        if then:
            then(lines)
    return True


def stage_ends(fleet, a):
    """Record the end of each stage the team's stages file owes, once each, under its lock. With --ending, the slot's
    or ops's stage whose agent is about to be ended: delivered when its deliverable exists, else stopped. Otherwise each
    one whose deliverable exists and whose agent is not working, observed late by the command that reads the team; a
    quiet stage that has delivered nothing stays owed. A slot's line whose slot no longer holds its unit or fix is
    dropped without an entry, and so is a proof's line once the team no longer holds its bolt."""
    t = crew.team_of(fleet, a.team)
    held = {l.split()[0]: l.split() for l in (team_state(t) / "slots").read_text().splitlines() if l.strip()} \
        if (team_state(t) / "slots").exists() else {}
    with stages_file(t) as lines:
        keep, ended = [], []
        bolts = None
        for l in lines:
            o = Owed(t, l)
            if a.slot and o.slot != a.slot:
                keep.append(l)
                continue
            if o.proof:
                if bolts is None:
                    plan = plan_of(fleet, t["label"])
                    bolts = {b.name() for b in held_by(plan, t["name"])} if plan else False
                if bolts is not False and o.name not in bolts and not a.ending:
                    continue
            elif o.slot not in held or held[o.slot][2] != o.name:
                continue
            if a.ending:
                got, _ = deliverable(fleet, t, o, held.get(o.slot, [None] * 4)[3])
                ended.append((o, "delivered" if got else "stopped", got))
            elif crew.agent_status(fleet, o.agent) != "working":
                got, _ = deliverable(fleet, t, o, held.get(o.slot, [None] * 4)[3])
                (ended.append((o, "delivered", got)) if got else keep.append(l))
            else:
                keep.append(l)
        now = {s["slot"]: s for s in slot_stages(fleet, t)} if any(not o.proof for o, *_ in ended) else {}
        for o, how, got in ended:
            record_end(fleet, t, o, how, got, late=how == "delivered", now=now)
        lines[:] = keep
    for o, how, _ in ended:
        if how == "delivered":
            unmark(fleet, t, o)


# ----------------------------------------------------------------------------------- what reaches a unit

def merge_tree(main, ours, theirs):
    """The paths git merge-tree forecasts in conflict when theirs is merged into ours, [] for a clean merge, or None when
    git can't tell. It writes objects and no ref."""
    r = subprocess.run(["git", "-C", main, "merge-tree", "--write-tree", "--name-only", "--no-messages", ours, theirs],
                       capture_output=True, text=True, env=gitenv())
    if r.returncode == 0:
        return []
    if r.returncode != 1:
        return None
    paths = []
    for line in r.stdout.split("\n")[1:]:
        if not line:
            break
        if line not in paths:
            paths.append(line)
    return paths


def case_of(text):
    """A proposal's Why, and the lead sentence of each of its What Changes items, in its own words."""
    sections, cur = {}, None
    for line in (text or "").splitlines():
        m = re.match(r"^##\s+(.*?)\s*$", line)
        if m:
            cur = sections.setdefault(m.group(1).lower(), [])
        elif cur is not None:
            cur.append(line)
    why = " ".join(l.strip() for l in sections.get("why", []) if l.strip())
    items = [re.split(r"(?<=[.!?])\s", m.group(1).strip(), maxsplit=1)[0]
             for m in (re.match(r"^\s*[-*]\s+(.*)$", l) for l in sections.get("what changes", [])) if m]
    return why, items


def change_words(main, kdir, k, bolt, unit):
    """Where another unit's change is, and its Why and What Changes as its proposal words them: read in its place while
    it has one, else on the bolt."""
    pl = k["places"].get(unit)
    if pl:
        path = f"{pl['path']}/openspec/changes/{unit}/"
        try:
            text = pathlib.Path(path, "proposal.md").read_text()
        except OSError:
            text = None
    else:
        path = f"{kdir}/bolts/{bolt}/openspec/changes/{unit}/"
        text = gather.run(["git", "show", f"bolt/{bolt}:openspec/changes/{unit}/proposal.md"], main)
    why, items = case_of(text)
    return (f"{unit}'s change is {path}." + (f" Its Why: {why}" if why else "")
            + (" What it changes: " + " ".join(items) if items else ""))


def forecast_words(t, k, bolt, unit, other, paths):
    """What a forecast says to the later unit: the conflicting paths, how to resolve them keeping both intents, and the
    other unit's change, or, for a conflict with the bolt, the change of each unit merged since the unit's place was
    made (teams.13)."""
    main, kdir, on = t["kit"]["main"], t["kit"]["dir"], ", ".join(paths)
    if other == f"bolt/{bolt}":
        base = gather.run(["git", "merge-base", f"bolt/{bolt}", f"unit/{unit}"], main)
        since = [c for c in gather.changes(main, f"bolt/{bolt}") if c not in (gather.changes(main, base.strip()) if base else [])]
        return (f"Your branch is forecast to conflict with bolt/{bolt} on {on}. Rebase your place onto the bolt "
                f"(git rebase bolt/{bolt}), resolve each conflict keeping both changes' intents, run the tests those paths "
                "affect, and commit." + "".join(" Merged since your place was made: " + change_words(main, kdir, k, bolt, c)
                                                  for c in since))
    return (f"Your merge after {other}, ahead of you in the bolt and not merged, is forecast to conflict on {on}. You merge "
            f"after it: take its work into your place (git merge unit/{other}), resolve each conflict keeping both changes' "
            f"intents, run the tests those paths affect, and commit. " + change_words(main, kdir, k, bolt, other))


def amendment_words(t, k, bolt, after):
    """What an amended After unit says to its dependent: that it was constructed again, and its revised change."""
    return (f"{after}, which you come after, was constructed again, and you are not held for it: build on its revised "
            "change, keeping yours true to it. Your place holds its work as it stood when your place was made, and is "
            f"rebased onto the bolt once it merges. " + change_words(t["kit"]["main"], t["kit"]["dir"], k, bolt, after))


def owed_by_unit(t):
    """The stages the team's stages file owes, by the unit or fix each is of."""
    with stages_file(t, shared=True) as lines:
        return {Owed(t, l).name: Owed(t, l) for l in lines if not Owed(t, l).proof}


def deliver(fleet, t, entries, unit, stage, words):
    """How a forecast or an amendment reaches a unit, once (teams.12): told, while a stage of it is owed and its agent is
    up and not working; as a settle stage, when it has delivered its verify and waits to merge; else carried in its next
    stage's prompt. None while its stage's agent is working, or when telling it or starting its settle failed, so the
    next wait tries again."""
    o = owed_by_unit(t).get(unit)
    status = crew.agent_status(fleet, o.agent) if o else None
    if o and status == "working":
        return None
    if o and status:
        return "told" if crew.tell(fleet, o.agent, words) else None
    if stage == "verify" and verified(t["label"], unit, entries):
        r = crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], "unit", "run", unit, "settle", words))
        if r.returncode:
            print(f"crew could not start {unit}'s settle stage: " + ((r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1],
                  file=sys.stderr)
            return None
        return "settle"
    return "prompt"


# A dependent's place rebased onto its bolt: printed "rebased" when it moved, nothing when it was already there; a
# rebase that conflicts is aborted, the place as it was, and printed "conflict <paths...>", exit 3.
ONTO = r"""cd "$1" || exit 1
bolt=$2
git merge-base --is-ancestor "refs/heads/bolt/$bolt" HEAD && exit 0
if git rebase -q "refs/heads/bolt/$bolt" >/dev/null 2>&1; then echo rebased; exit 0; fi
paths=$(git diff --name-only --diff-filter=U | tr '\n' ' ')
git rebase --abort >/dev/null 2>&1
echo "conflict $paths"; exit 3
"""


def landed_at(main, bolt, unit):
    """The commit on a bolt that brought a unit's change there, the first that holds its folder; None when it holds none."""
    out = gather.run(["git", "log", "--format=%H", "--reverse", f"refs/heads/bolt/{bolt}", "--", f"openspec/changes/{unit}"], main)
    return (out or "").split("\n")[0].strip() or None


def clean(path):
    """Whether a worktree has nothing uncommitted and nothing in progress, as plan.9 reads a worktree crew may move."""
    st = subprocess.run(["git", "-C", path, "status", "--porcelain"], capture_output=True, text=True, env=gitenv())
    if st.returncode or st.stdout.strip():
        return False
    for f, _ in IN_PROGRESS:
        at = subprocess.run(["git", "-C", path, "rev-parse", "--path-format=absolute", "--git-path", f], capture_output=True,
                            text=True, env=gitenv()).stdout.strip()
        if at and os.path.exists(at):
            return False
    return True


def rebase_dependents(fleet, t, plan, st, say):
    """Each unmerged unit of the team's bolt with a place, one of whose After units has merged since its place last
    met the bolt, is rebased onto the bolt, only while its agent is not working and its place is clean (teams.2, plan.9):
    the bolt's commits drop out of it. A rebase that conflicts is aborted, the place as it was, and returned to reach
    the dependent as a conflict does: [(bolt, unit, paths)]. say(text) reports what was done or left."""
    main, out = t["kit"]["main"], []
    owed = owed_by_unit(t)
    for b in held_by(plan, t["name"]):
        k, _ = st.kit(b)
        if not k:
            continue
        for u in plan.units_of(b.name()):
            pl = k["places"].get(u.name())
            if not pl or st.of(u.name())["stage"] in ("merged", "landed", "unknown"):
                continue
            merged = [a for a in u.all("After") if st.of(a)["stage"] in ("merged", "landed")]
            due = [a for a in merged if (lambda c: c and subprocess.run(["git", "-C", main, "merge-base", "--is-ancestor", c, f"refs/heads/unit/{u.name()}"],
                                                                       env=gitenv()).returncode != 0)(landed_at(main, b.name(), a))]
            if not due:
                continue
            o = owed.get(u.name())
            if o and crew.agent_status(fleet, o.agent) == "working":
                say(f"{u.name()} waits to be rebased onto bolt/{b.name()}, now that {', '.join(due)} merged: its agent is working")
                continue
            if not clean(pl["path"]):
                say(f"{u.name()} waits to be rebased onto bolt/{b.name()}, now that {', '.join(due)} merged: {pl['path']} has "
                    "uncommitted changes or work in progress")
                continue
            r = subprocess.run(["bash", "-c", ONTO, "crew", pl["path"], b.name()], capture_output=True, text=True, env=gitenv())
            READ.drop_kit(t["machine"], main)
            if r.returncode == 3:
                out.append((b.name(), u.name(), r.stdout.strip().split()[1:], due))
                say(f"rebasing {u.name()} onto bolt/{b.name()} conflicts: its place is as it was, and it is told")
            elif r.returncode:
                say(f"{u.name()} was not rebased onto bolt/{b.name()}: " + ((r.stderr or r.stdout).strip() or f"exit {r.returncode}"))
            elif r.stdout.strip() == "rebased":
                record.emit(t["label"], "unit.rebase", [f"unit/{u.name()}", f"bolt/{b.name()}"], frm=[f"unit/{a}" for a in due],
                            why=f"unit({u.name()}): rebase onto bolt/{b.name()}, now that {', '.join(due)} merged")
                say(f"{u.name()} is rebased onto bolt/{b.name()}, now that {', '.join(due)} merged")
    return out


def rebase_cmd(fleet, a):
    """crew _rebase <team> [--tidy]: the team's read rebases each dependent whose After unit has merged
    (rebase_dependents); a conflict waits for the conductor's next wait, which tells the dependent. With --tidy, the
    team's tidy runs after it, as `_tidy <team>` would, whether or not the rebase was refused: one process where there
    were two."""
    t = crew.team_of(fleet, a.team)
    try:
        plan = plan_of(fleet, t["label"])
        if plan:
            rebase_dependents(fleet, t, plan, stages_for(fleet, plan, held_by(plan, t["name"])), print)
    except Refusal as e:
        if not a.tidy:
            raise
        sys.stdout.flush()
        print(e, file=sys.stderr)
    if a.tidy:
        sys.stdout.flush(), sys.stderr.flush()
        tidy(fleet, a)


def amendments(t, plan, st, entries):
    """For each dependent with a place, each After unit constructed again since the dependent's construct took its
    head: [(bolt, dependent, after unit, its new head)], read from this host's run record. A construct whose head the
    dependent already holds, such as one recorded late, is no amendment."""
    out = []
    for b in held_by(plan, t["name"]):
        for u in plan.units_of(b.name()):
            if st.of(u.name())["stage"] in ("merged", "landed", "unknown") or not u.all("After"):
                continue
            starts = [e for e in entries if e.get("Act") == "stage.start" and f"stage/{u.name()}/construct" in e["On"] and not e.get("Refused")]
            if not starts:
                continue
            since = (starts[0]["At"], starts[0]["Id"])
            took = dict(w.split("@", 1) for e in starts for w in (e.get("Took") or "").split() if "@" in w)
            for a in u.all("After"):
                ends = [e for e in entries if e.get("Act") == "stage.end" and f"stage/{a}/construct" in e["On"]
                        and e.get("Ended") == "delivered" and (e["At"], e["Id"]) > since]
                head = (ends[-1].get("Delivered") or "").rpartition("@")[2] if ends else ""
                held = took.get(a)
                if head and head != held and not (held and subprocess.run(
                        ["git", "-C", t["kit"]["main"], "merge-base", "--is-ancestor", head, held], env=gitenv()).returncode == 0):
                    out.append((b.name(), u.name(), a, head))
    return out


def reach(fleet, t):
    """On each of the conductor's waits, before it waits: for each unmerged unit of the team's bolt with a place, git
    merge-tree on the team's host forecasts its merge with the bolt and with each unmerged unit ahead of it in the file's
    order, writing no ref; a unit that conflicts with the bolt resolves that first, and is forecast against the units
    ahead of it once it is clean with the bolt. A conflict is a forecast for the later unit, recorded once for a pair of
    heads (`forecast`, with both heads, the paths and how it reached the unit) and reaching it once (deliver). The
    earlier unit is told nothing. A forecast between two unmerged units gives the later After on the earlier, in a write that is the waiting
    conductor's own (plan.13, roles.1). What crew can't read or write here is said on standard error, and the wait
    goes on (teams.12)."""
    label, main = t["label"], t["kit"]["main"]
    plan = plan_of(fleet, label)
    if plan is None:
        print(f"no forecast: {label}'s plan could not be read", file=sys.stderr)
        return
    bolts = held_by(plan, t["name"])
    with READ.fresh():
        st = stages_for(fleet, plan, bolts)
    say = lambda text: print(text, file=sys.stderr)
    met = rebase_dependents(fleet, t, plan, st, say)
    if met:
        with READ.fresh():
            st = stages_for(fleet, plan, bolts)
    entries = local_entries(label)
    done = {e.get("Heads") for e in entries if e.get("Act") in ("forecast", "amendment") and e.get("Heads")}
    for bolt, name, paths, due in met:
        k, _ = st.kit(plan.bolt(bolt))
        pl = (k or {"places": {}})["places"].get(name)
        bhead = (k or {"bolts": {}})["bolts"].get(bolt, {}).get("head")
        heads = f"{name}@{(pl or {}).get('head', '')[:7]} bolt/{bolt}@{(bhead or '')[:7]}"
        if not pl or not bhead or heads in done:
            continue
        way = deliver(fleet, t, entries, name, st.of(name)["stage"], forecast_words(t, k, bolt, name, f"bolt/{bolt}", paths))
        if way:
            record.emit(label, "forecast", [f"unit/{name}", f"bolt/{bolt}"], why=f"unit({name}): rebase onto bolt/{bolt} conflicts",
                        Heads=heads, Paths=" ".join(paths), Reached=way)
            done.add(heads)
    for bolt, name, a, ahead in amendments(t, plan, st, entries):
        heads = f"{name} {a}@{ahead}"
        if heads in done:
            continue
        k, _ = st.kit(plan.bolt(bolt))
        if not k:
            continue
        way = deliver(fleet, t, entries, name, st.of(name)["stage"], amendment_words(t, k, bolt, a))
        if way:
            record.emit(label, "amendment", [f"unit/{name}", f"unit/{a}"], why=f"unit({name}): {a} was constructed again",
                        Heads=heads, Reached=way)
            done.add(heads)
    for b in bolts:
        k, why = st.kit(b)
        if not k:
            print(f"no forecast for {b.name()}: {why}", file=sys.stderr)
            continue
        live = [u for u in plan.units_of(b.name()) if k["places"].get(u.name()) and k["places"][u.name()].get("head")
                and st.of(u.name())["stage"] not in ("merged", "landed", "unknown")]
        bolt_head = k["bolts"].get(b.name(), {}).get("head")
        for i, u in enumerate(live):
            name, head = u.name(), k["places"][u.name()]["head"]
            others = ([(f"bolt/{b.name()}", bolt_head)] if bolt_head else []) + [(o.name(), k["places"][o.name()]["head"]) for o in live[:i]]
            for other, ohead in others:
                heads = f"{name}@{head[:7]} {other}@{ohead[:7]}"
                paths = merge_tree(main, ohead, head)
                if paths is None:
                    print(f"no forecast of {name} against {other}: git merge-tree could not read them", file=sys.stderr)
                    continue
                if not paths:
                    continue
                if heads in done:
                    if other.startswith("bolt/"):
                        break  # it meets the bolt first: the units ahead are forecast once it is clean with the bolt
                    continue
                if not other.startswith("bolt/") and other not in u.all("After"):
                    def change(w, name=name, other=other):
                        v = w.unit(name)
                        w.unit(other)
                        if other not in v.all("After"):
                            v.add("After", other, after="Intent")
                        return [b.name()]
                    try:
                        with contextlib.redirect_stdout(sys.stderr):
                            write(fleet, label, change, f"plan({b.name()}): {name} after {other}, forecast to conflict",
                                  act="unit.after", on=[f"unit/{name}", f"bolt/{b.name()}"])
                    except Refusal as e:
                        print(f"{name} is not put after {other}: {e}", file=sys.stderr)
                way = deliver(fleet, t, entries, name, st.of(name)["stage"], forecast_words(t, k, b.name(), name, other, paths))
                if way:
                    record.emit(label, "forecast", [f"unit/{name}", other if other.startswith("bolt/") else f"unit/{other}"],
                                why=f"unit({name}): forecast to conflict with {other}", Heads=heads, Paths=" ".join(paths), Reached=way)
                    done.add(heads)
                if other.startswith("bolt/"):
                    break


def carried_forecasts(fleet, t, plan, st_all, bolt, unit):
    """The forecasts and amendments waiting to reach a unit in its next stage's prompt: this host's entries for it that
    reached it by prompt and that no stage start of it has carried since. Returns their ids and their words."""
    entries = local_entries(t["label"])
    taken = {i for e in entries if e.get("Act") == "stage.start" and f"unit/{unit}" in e["On"] for i in (e.get("Forecast") or "").split()}
    waiting = [e for e in entries if e.get("Act") in ("forecast", "amendment") and e.get("Reached") == "prompt"
               and e["On"][:1] == [f"unit/{unit}"] and e["Id"] not in taken]
    if not waiting:
        return [], []
    k, _ = st_all.kit(plan.bolt(bolt))
    other = lambda e: e["On"][1][5:] if e["On"][1].startswith("unit/") else e["On"][1]
    return [e["Id"] for e in waiting], [amendment_words(t, k, bolt, other(e)) if e["Act"] == "amendment" else
                                        forecast_words(t, k, bolt, unit, other(e), (e.get("Paths") or "").split()) for e in waiting]


# ------------------------------------------------------------------------------------------------- the wait

POLL = 10  # seconds between a wait's reads


def handed(t, slot, eid):
    """The words a stop-short of this stage handed to its wait (needs/<slot>, its first line the stage's start entry
    id), taken: the file goes once read. None when there are none for this stage."""
    f = team_state(t) / "needs" / slot
    try:
        first, _, words = f.read_text().partition("\n")
    except OSError:
        return None
    if first.strip() != eid:
        return None
    f.unlink(missing_ok=True)
    return words


def background(info):
    """What an agent's own session says it still waits on: (the background tasks it started and has not been told are
    over, when its transcript last wrote, None), or (None, None, what crew could not read)."""
    sess = info.get("agent_session")
    sid = sess.get("value") if isinstance(sess, dict) else None
    if not isinstance(sid, str) or not sid:
        return None, None, "herdr names no session for it"
    path = transcript.find(sid)
    if path is None:
        return None, None, f"no transcript for its session {sid}"
    pending = transcript.pending(path)
    if pending is None:
        return None, None, f"its transcript {path} can't be read"
    return pending, transcript.last_at(path), None


def minutes(td):
    m = max(0, int(td.total_seconds() // 60))
    return f"{m} minute{'' if m == 1 else 's'}"


def last_end(t, agent):
    """The newest stage.end this host recorded for an agent, or None."""
    runs = record.ROOT / t["label"] / "runs" / crew.this_host()
    found = []
    for f in sorted(runs.glob("*.rec"))[-3:] if runs.is_dir() else []:
        found += [e for e in record.parse(f.read_text()) if e.get("Act") == "stage.end" and not e.get("Refused")
                  and f"agent/{agent}" in e["On"]]
    return max(found, key=lambda e: (e["At"], e["Id"])) if found else None


def ended_said(t, agent):
    """What a wait says of a stage whose end was recorded by something other than itself, from the run record."""
    e = last_end(t, agent)
    if not e:
        return f"{agent} owes no stage's end, and none is recorded for it on this host"
    stage = next((o.split("/") for o in e["On"] if o.startswith("stage/")), None)
    fix = next((o for o in e["On"] if o.startswith("fix/")), None)
    m = re.match(r"^[a-z]+\([^)]*\): (\S+) ", e.get("Why") or "")
    what = (f"the proof of {stage[1]}" if stage and stage[2:] == ["proof"] else f"{stage[2]} on {stage[1]}" if stage and len(stage) > 2 else
            (f"fix {fix}" if not m or m.group(1) == "fix" else f"{m.group(1)} of {fix}") if fix else "its stage")
    how = {"delivered": f"{agent} delivered {e.get('Delivered')}" + (" (observed late)" if e.get("Observed") == "late" else ""),
           "short": f"{agent} stopped short, and {t['name']}-conductor was told what it needs",
           "stopped": f"crew ended {agent} before it delivered"}.get(e.get("Ended"), f"{agent} reached {e.get('Result', 'unknown')}")
    return f"{what} has ended: {how}"


def stage_wait(fleet, a):
    """Wait on the stage a slot's agent, or ops, owes, until it ends at its deliverable, stops short, is stuck, its agent
    is gone, or the timeout passes, and print the one line that says which. A delivered end is recorded here; nothing
    else is. The wait holds waits/<slot>.lock for its life, so crew needs knows a wait is there to hand its words to."""
    t = crew.team_of(fleet, a.team)
    agent = f"{t['name']}-{a.slot}"
    (team_state(t) / "waits").mkdir(parents=True, exist_ok=True)
    lock = open(team_state(t) / "waits" / f"{a.slot}.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fail(f"a wait on {agent}'s stage is already running: its answer is the one to read")
    try:
        reach(fleet, t)
    except Refusal as e:
        print(f"no forecast: {e}", file=sys.stderr)
    try:
        batch_check(fleet, t)
    except Refusal as e:
        print(f"no batch reckoned: {e}", file=sys.stderr)
    held = {l.split()[0]: l.split() for l in (team_state(t) / "slots").read_text().splitlines() if l.strip()} \
        if (team_state(t) / "slots").exists() else {}
    with stages_file(t, shared=True) as lines:
        o = next((Owed(t, l) for l in lines if l[0] == a.slot), None)
    if o is None:
        print(ended_said(t, agent))
        return
    o.start or fail(f"crew can't tell when {o.phrase()} began: its start entry's id, {o.eid}, holds no time it reads")
    place = held.get(a.slot, [None] * 4)[3] if not o.proof else None
    deadline = time.monotonic() + a.timeout / 1000
    stuck = datetime.timedelta(milliseconds=a.stuck)
    seen_quiet = seen_working = None
    with READ.fresh():  # each look reads the plan and the kit afresh
        while True:
            with stages_file(t, shared=True) as lines:
                words = handed(t, a.slot, o.eid)
                owed = any(l[3:4] == [o.eid] for l in lines)
            if words is not None:
                print(f"{agent} stopped short in {o.phrase()}. It needs: {words}")
                return
            if not owed:
                print(ended_said(t, agent))
                return
            info = crew.agent_get(fleet, agent)
            status = info.get("agent_status") if info else None
            got, missing = deliverable(fleet, t, o, place) if status != "working" else (None, None)
            if got:
                if end_owed(fleet, t, o, "delivered", got):
                    unmark(fleet, t, o)
                    if o.stage == "construct" and not o.fix and not o.proof:
                        try:  # the change it delivered is due, and may make a batch due now
                            batch_check(fleet, t)
                        except Refusal as e:
                            print(f"no batch reckoned: {e}", file=sys.stderr)
                    print(f"{agent} delivered {o.phrase()}: {missing}")
                    return
                continue
            if info is None:
                print(f"{agent} is no longer running: {o.phrase()} delivered nothing and said nothing it needs")
                return
            now = datetime.datetime.now(datetime.timezone.utc)
            if status == "working":
                seen_working, doing = now, "is working"
            else:
                seen_quiet = seen_quiet or now
                pending, last, unread = background(info)
                if pending:
                    doing = f"is waiting on {len(pending)} background task{'' if len(pending) == 1 else 's'} of its own"
                else:
                    # The clock starts at the transcript's last record, or when this wait first saw the agent quiet when
                    # that can't be read, and never before this wait last saw it working.
                    quiet = now - max(x for x in ((seen_quiet if unread or not last else last), seen_working) if x)
                    if quiet >= stuck:
                        print(f"{agent} is stuck in {o.phrase()}: quiet for {minutes(quiet)}, with {missing} and nothing it needs said"
                              + (f"; crew could not read whether it waits on work of its own ({unread})" if unread else ""))
                        return
                    doing = f"has been quiet for {minutes(quiet)}, under the limit of {minutes(stuck)}"
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                print(f"{o.phrase()} is still running after the wait's {a.timeout} ms: {agent} {doing}; nothing is recorded yet")
                return
            time.sleep(min(POLL, remaining))


def stage_needs(fleet, a):
    """crew needs: the caller's stage ends short, recorded with Ended short and never the words (record.3), and the
    words go to the conductor: to the wait running on the stage when there is one, through needs/<slot>, else in a
    tell marked as from the agent (roles.4). Only the agent of a stage crew owes an end may say it."""
    t = crew.team_of(fleet, a.team)
    agent, conductor = f"{t['name']}-{a.slot}", f"{t['name']}-conductor"
    a.words.strip() or fail('say what you need: crew needs "<what you tried and what you need>"')
    held = {l.split()[0]: l.split() for l in (team_state(t) / "slots").read_text().splitlines() if l.strip()} \
        if (team_state(t) / "slots").exists() else {}
    needs = team_state(t) / "needs" / a.slot
    owed = []

    def hand(lines):
        needs.parent.mkdir(parents=True, exist_ok=True)
        tmp = needs.with_name(f".{a.slot}.new")
        tmp.write_text(f"{owed[0].eid}\n{a.words}")
        tmp.replace(needs)

    with stages_file(t, shared=True) as lines:
        owed += [Owed(t, l) for l in lines if l[0] == a.slot and (a.slot == "ops" or held.get(a.slot, [None] * 3)[2] == l[1])]
    owed or fail(f"{agent} runs no stage crew is waiting on")
    o = owed[0]
    end_owed(fleet, t, o, "short", then=hand) or fail(f"{agent} runs no stage crew is waiting on")
    # The words are the wait's once it takes the file; when no wait holds its lock, or the one there ends without
    # taking them, they are told. A wait takes the file only while it holds the lock, so a free lock with the file
    # still there means nobody will.
    told = f"{agent} stopped short in {o.phrase()}. It needs: {a.words}"
    give_up, waits = time.monotonic() + 6 * POLL, team_state(t) / "waits" / f"{a.slot}.lock"
    while needs.exists():
        waits.parent.mkdir(parents=True, exist_ok=True)
        with open(waits, "a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                free = True
            except OSError:
                free = False
            if (free or time.monotonic() > give_up) and needs.exists():
                needs.unlink(missing_ok=True)
                if crew.tell(fleet, conductor, told, sender=agent):
                    print(f"{o.phrase()} is ended, stopped short: {conductor} is told what you need")
                else:
                    print(f"{o.phrase()} is ended, stopped short, and {conductor} could not be told what you need: "
                          "say it in your last message", file=sys.stderr)
                return
        time.sleep(1)
    print(f"{o.phrase()} is ended, stopped short: {conductor}'s wait has what you need")


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


# ------------------------------------------------------------------------------------------------- batches

BATCH_DAYS = 60  # how far back the run record is read for constructs and batches
CARD_UNITS = 5  # Pending You's limit on a choice's options: a batch card holds at most five units
UNIT_AT = re.compile(r"^([a-z0-9][a-z0-9-]*):([a-z0-9][a-z0-9-]*)@([0-9a-f]{4,40})$")


def reviews(label):
    """The partition's reviews folder on its main level's host, where each batch's summary is written."""
    return pathlib.Path.home() / f".local/state/crew/{label}-main/reports"


def batch_file(label, n):
    return reviews(label) / f"batch-{label}-{n}.md"


def units_of_batch(e):
    """A review entry's units, in order, as (unit, team, commit)."""
    return [m.groups() for m in (UNIT_AT.match(w) for w in (e.get("Units") or "").split()) if m]


def partition_entries(fleet, label, days=BATCH_DAYS):
    """The partition's run record from days back, from its branch and every host it runs on, refused naming what did not
    answer (read.1): what is due can't be told from part of it."""
    since = (datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=days)).isoformat()
    entries, missing = record.gather(fleet, [label], since)
    not missing or fail("crew can't tell which changes have been in a batch: " + "; ".join(f"{k} did not answer ({v})" for k, v in missing.items()))
    return entries


def batches(entries):
    """The partition's review batches, oldest first: (number, when, [(unit, team, commit)])."""
    return [(int(e["Batch"]), e["At"], units_of_batch(e)) for e in entries
            if e.get("Act") == "review.batch" and not e.get("Refused") and (e.get("Batch") or "").isdigit()]


def due_changes(plan, entries):
    """Each change due for the user's review, in the plan's order: a unit of a bolt a team holds whose last delivered
    construct left a commit no batch has held it at, as (unit, team, commit, when it was constructed)."""
    latest = {}
    for e in entries:
        if e.get("Act") != "stage.end" or e.get("Ended") != "delivered" or e.get("Refused"):
            continue
        st = next((o for o in e["On"] if o.startswith("stage/") and o.endswith("/construct")), None)
        unit = st.split("/")[1] if st else None
        got = e.get("Delivered") or ""
        if unit and got.startswith(f"unit/{unit}@"):
            latest[unit] = (got.rpartition("@")[2], e["At"])
    held = {(u, sha) for _, _, us in batches(entries) for u, _, sha in us}
    out = []
    for u in plan.units():
        b = plan.bolt(u.get("Bolt")) if u.get("Bolt") else None
        if b and b.get("Team") and u.name() in latest and (u.name(), latest[u.name()][0]) not in held:
            out.append((u.name(), b.get("Team"), *latest[u.name()]))
    return out


def batch_check(fleet, t):
    """On each wait of a conductor of the partition: the changes due across the partition, counted from the run
    record, make a batch due at the partition's setting, `every` of them or `hours` since its last batch with at least
    one due, or at once when the team's bolt has every unit merged and some unit's latest change has been in no batch.
    crew then tells the partition's planner once, `batch.due` in the run record, until the next batch is delivered
    (briefs.12). What crew can't read is said on standard error, and the wait goes on."""
    label = t["label"]
    setting = fleet["partitions"][label]["review"]
    plan = plan_of(fleet, label)
    if plan is None:
        return
    entries = partition_entries(fleet, label)
    due = due_changes(plan, entries)
    if not due:
        return
    done = [e["At"] for e in entries if e.get("Act") == "review.batch"]
    last = max(done) if done else None
    if any(e.get("Act") == "batch.due" and (last is None or e["At"] > last) for e in entries):
        return
    now = datetime.datetime.now(datetime.timezone.utc)
    clock = utc(last) if last else min(utc(at) for *_, at in due)
    why = []
    if len(due) >= setting["every"]:
        why.append(f"{len(due)} changes are due, and a batch is every {setting['every']}")
    if now - clock >= datetime.timedelta(hours=setting["hours"]):
        why.append(f"{setting['hours']} hours have passed since " + ("the last batch" if last else "the first of them was constructed"))
    held = held_by(plan, t["name"])
    if held:
        st = stages_for(fleet, plan, held)
        for b in held:
            units = plan.units_of(b.name())
            waiting = [u for u, *_ in due if plan.unit(u).get("Bolt") == b.name()]
            if units and waiting and all(st.of(u.name())["stage"] in ("merged", "landed") for u in units):
                why.append(f"bolt {b.name()} has every unit merged, and lands only once {either(waiting)} "
                           + ("has" if len(waiting) == 1 else "have") + " been in a batch")
    if not why:
        return
    planner = f"{label}-planner"
    text = (f"A batch of {label}'s changes is due: " + ", ".join(f"{u} ({team})" for u, team, *_ in due) + f"; " + "; ".join(why)
            + f". Start its reviewer with crew review {label}, wait for the summary with crew review {label} --wait, then post its cards.")
    if crew.tell(fleet, planner, text):
        record.emit(label, "batch.due", [f"agent/{planner}"] + [f"unit/{u}" for u, *_ in due], why=f"batch: due, {len(due)} changes",
                    Count=len(due))


def reading_command(fleet, label, team, sha, unit):
    """How the reviewer, on the main level's host, reads a unit's change at a commit in its kit on the team's host."""
    t, here = fleet["teams"][team], fleet["partitions"][label]["machine"]
    pre = "" if t["machine"] == here else f"ssh -o BatchMode=yes {t['ssh']} "
    return (f"list its files with `{pre}git -C {t['kit']['main']} ls-tree -r --name-only {sha} openspec/changes/{unit}/` and read "
            f"each with `{pre}git -C {t['kit']['main']} show {sha}:<path>`")


def review_start(fleet, a):
    """crew _review <label>: the batch the partition's reviewer is started for, as shell assignments for bash crew: its
    number (N), the file it writes (FILE), its units as <unit>:<team>@<commit> (UNITS) and by name (NAMES), and its
    prompt (PROMPT), naming each change, its team, its kit and host, and how to read it at its commit. Refused when no
    change is due."""
    p = crew.partition_of(fleet, a.label)
    label = p["label"]
    CONTEXT["label"] = label
    repo, ref = state_of(fleet, label)
    tip = fetch(repo, ref) or fail(f"{repo} has no {ref} yet: crew state init {label}")
    plan = read(repo, ref, tip)
    entries = partition_entries(fleet, label)
    due = due_changes(plan, entries)
    due or fail(f"no change of {label} is due for a batch: every unit's latest change has been in one")
    n = 1 + max([int(e["Batch"]) for e in entries if e.get("Act") in ("review.start", "review.batch") and (e.get("Batch") or "").isdigit()] or [0])
    f = batch_file(label, n)
    prompt = (f"Review batch {n} of {label}, {len(due)} change{'' if len(due) == 1 else 's'}, and write its summary to {f}. "
              + " ".join(f"{u} ({team}, {fleet['teams'][team]['kit']['name']} on {fleet['teams'][team]['machine']}, at {sha}): "
                         f"{reading_command(fleet, label, team, sha, u)}." for u, team, sha, _ in due))
    print(sh(N=n, FILE=f, UNITS=" ".join(f"{u}:{team}@{sha}" for u, team, sha, _ in due), NAMES=" ".join(u for u, *_ in due),
             PROMPT=prompt))


def review_wait(fleet, a):
    """crew _review-wait <label>: wait, on the main level's host, for the summary of the batch the reviewer was last
    started for, written since it started: once it is, the batch is recorded (`review.batch`, its number and each unit
    at the commit its change was read at) and the file's path printed. A batch already recorded is printed at once.
    Exit 3 when the timeout passes first, 1 when the reviewer is gone with no summary written."""
    label = crew.partition_of(fleet, a.label)["label"]
    CONTEXT["label"] = label
    entries = local_entries(label, BATCH_DAYS)
    starts = [e for e in entries if e.get("Act") == "review.start" and not e.get("Refused") and (e.get("Batch") or "").isdigit()]
    starts or fail(f"no batch of {label} has been started: crew review {label} starts one")
    s = starts[-1]
    n, f = int(s["Batch"]), batch_file(label, s["Batch"])
    if any(e.get("Act") == "review.batch" and e.get("Batch") == s["Batch"] for e in entries):
        print(f)
        return
    begun, deadline = utc(s["At"]), time.monotonic() + a.timeout / 1000
    while True:
        try:
            written = f.stat().st_mtime >= begun.timestamp()
        except OSError:
            written = False
        if written:
            record.emit(label, "review.batch", [f"batch/{n}"] + [f"unit/{u}" for u, *_ in units_of_batch(s)],
                        why=f"batch({n}): reviewed", Batch=n, Units=s.get("Units"))
            print(f)
            return
        if crew.agent_status(fleet, f"{label}-reviewer") is None:
            fail(f"{label}-reviewer is no longer running, and batch {n}'s summary {f} was not written")
        if time.monotonic() >= deadline:
            print(f"batch {n}'s review is still running after the wait's {a.timeout} ms: nothing is recorded yet", file=sys.stderr)
            sys.exit(3)
        time.sleep(POLL)


# ------------------------------------------------------------------------------------------------ crew rail

RAIL = ("proposals", "batches", "verify", "land", "deploys")


def utc(iso):
    """An ISO 8601 time, as git and the run record write it, as an aware datetime."""
    return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")) if iso else None


def age(at, now):
    """How long ago, in its two largest units: <1m, 14m, 3h 05m, 2d 04h."""
    m = int((now - at).total_seconds()) // 60
    if m < 1:
        return "<1m"
    if m < 60:
        return f"{m}m"
    h, m = divmod(m, 60)
    if h < 24:
        return f"{h}h {m:02d}m"
    d, h = divmod(h, 24)
    return f"{d}d {h:02d}h"


def opener(fleet, host, here, path):
    """The command that opens a file or folder on a host in plannotator: beside the rail when the host is the one it
    runs on, else inline over ssh, quoted again for the shell on the other end."""
    if host == here:
        return f"plannotator-tui herdr open {shlex.quote(path)}"
    return f"ssh -t {fleet['hosts'][host]['ssh']} plannotator-tui {shlex.quote(shlex.quote(path))}"


# How far back the rail reads the run record for the cards still open.
CARD_DAYS = 14


def rail_record(fleet, found, props):
    """What the rail reads of the run record, in one read of each partition whose plan was read: from 60 days back, for
    the batches and the constructs they hold, or from the day before its oldest open proposal's Opened when that is
    earlier, since Opened is the writing host's date and the record's files are named by the UTC day. Returns when each
    open proposal was proposed, {(label, proposal/<n>): time}, from the earliest plan.propose entry naming it (a
    proposal whose entry isn't found is left out); the cards open, each {label, card, key, on, by, host, at}, from each
    card.post of the last 14 days with a Card that no later card.close of that Card closes; the hosts whose record did
    not answer, {label: {host: why}}; the landings, each {label, bolt, units, at, by, host}, from each bolt.land entry
    not refused, oldest first; the team each bolt was given to, {(label, bolt): team}, from the newest bolt.give entry
    naming it that was not refused; and what the batches hold, {label: {"batches": [(n, at, units)], "closed": card
    keys closed, "due": units whose latest change no batch has held}}, the last None for a partition whose record did
    not all answer, since then it can't be told."""
    times, cards, unread, landings, gives, held, deploys = {}, [], {}, [], {}, {}, []
    today = datetime.datetime.now(datetime.timezone.utc).date()
    fresh = utc(f"{today - datetime.timedelta(days=CARD_DAYS)}T00:00:00Z")
    for l, _, _, plan in [f for f in found if f[3]]:
        since = today - datetime.timedelta(days=BATCH_DAYS)
        opened = [d["opened"] for d in props if d["label"] == l]
        if opened:
            since = min(since, datetime.date.fromisoformat(min(opened)) - datetime.timedelta(days=1))
        entries, missing = record.gather(fleet, [l], since.isoformat())
        unread[l] = missing
        posted, closed = {}, set()
        for e in entries:
            act = e.get("Act")
            if act == "plan.propose" and not e.get("Refused"):
                for o in e["On"]:
                    if o.startswith("proposal/"):
                        times.setdefault((l, o), utc(e["At"]))
            elif act == "card.post" and e.get("Card") and utc(e["At"]) >= fresh:
                posted.setdefault(e["Card"], dict(label=l, card=e["Card"], key=e.get("Key"), on=(e["On"] or [None])[0],
                                                  by=e.get("By"), host=e.get("Host"), at=utc(e["At"])))
            elif act == "card.close" and e.get("Card"):
                posted.pop(e["Card"], None)
                if e.get("Key"):
                    closed.add(e["Key"])
            elif act == "bolt.land" and not e.get("Refused"):
                bolt = next((o[5:] for o in e["On"] if o.startswith("bolt/")), None)
                if bolt:
                    landings.append(dict(label=l, bolt=bolt, units=[o[5:] for o in e["On"] if o.startswith("unit/")], at=utc(e["At"]),
                                         by=e.get("By"), host=e.get("Host")))
            elif act == "bolt.give" and not e.get("Refused"):
                bolt = next((o[5:] for o in e["On"] if o.startswith("bolt/")), None)
                team = next((o[5:] for o in e["On"] if o.startswith("team/")), None)
                if bolt and team:
                    gives[(l, bolt)] = team
        cards += posted.values()
        held[l] = dict(batches=batches(entries), closed=closed, due=None if missing else {u for u, *_ in due_changes(plan, entries)})
        import deploy  # deploy.py imports nothing of this module
        deploys += [dict(r, at=utc(r["at"]), doc=None) for r in deploy.rows(fleet, l, [e for e in entries if (e.get("Act") or "").startswith("deploy.")
                                                                                       and e.get("Host") == fleet["partitions"][l]["machine"]])]
    return times, cards, unread, landings, gives, held, deploys


def rail_rows(fleet, found, sv, props, times, held=None):
    """What waits on the user in the plans read, from the open proposals and when each was proposed, the batches the
    run record holds (held, as rail_record reads it), and the kits as surveyed: each row's group, its partition, its
    card key, the time it began to wait (shown as a date alone when that is all that is known), what it is, its
    commands, and the document its card asks the user to read: ("page", label, n) for a proposal, ("batch", label, n)
    for a batch card, whose units each have a session of their own, (host, path) for a verify report, None for a
    landing. A batch of more than five units is a row for each five, keyed batch/<n>-<k>, until its card closes. A bolt
    with every unit merged is a landing row, offered for landing only once every unit's latest change has been in a
    batch: until then the row names the units that have not, and offers nothing (briefs.12)."""
    rows, here, held = [], crew.this_host(), held or {}
    for d in props:
        l, n = d["label"], d["proposal"]
        what = [f"proposal {n} ({l}), by {d['by']}: {d['case'].splitlines()[0][:70]}"]
        if d["waiting"]:
            what.append("still needs the agreement of " + ", ".join(f"{t}-conductor" for t in d["waiting"]))
        at = times.get((l, f"proposal/{n}"))
        rows.append(dict(group="proposals", label=l, key=f"proposal/{n}", at=at or utc(f"{d['opened']}T00:00:00Z"),
                         date=None if at else d["opened"], what=what, doc=("page", l, n),
                         cmds=[("read", f"crew plan proposed {n} --label {l}"), ("open", f"crew plan proposed {n} --label {l} --open"),
                               ("answer", f"crew plan approve {n} --label {l}")]))
    for l, h in held.items():
        main = fleet["partitions"][l]["machine"]
        for n, at, units in h["batches"]:
            cards_ = [units[i:i + CARD_UNITS] for i in range(0, len(units), CARD_UNITS)]
            for k, part in enumerate(cards_, 1):
                key = f"batch/{n}-{k}"
                if key in h["closed"]:
                    continue
                home = fleet["hosts"].get(main, {}).get("home")
                f = str(batch_file(l, n)) if main == here else f"{home}/.local/state/crew/{l}-main/reports/batch-{l}-{n}.md" if home else None
                rows.append(dict(group="batches", label=l, key=key, at=utc(at), doc=("batch", l, n),
                                 units=[u for u, *_ in part], teams={u: team for u, team, _ in part},
                                 what=[f"batch {n} ({l}), card {k} of {len(cards_)}: " + ", ".join(f"{u} ({team})" for u, team, _ in part)],
                                 cmds=([("open", opener(fleet, main, here, f))] if f else [])
                                 + [("answer", f'crew tell {l}-planner "On batch {n}, these need notes: "')]))
    for l, _, _, plan in found:
        if not plan:
            continue
        st = Stages(fleet, plan, sv)
        for b in plan.bolts():
            if not b.get("Team"):
                continue
            k, _ = st.kit(b)
            if not k:
                continue
            team, host = k["team"]["name"], k["host"]
            units = plan.units_of(b.name())
            for u in units:
                s, pl = st.of(u.name())["stage"], k["places"].get(u.name())
                if not pl:
                    continue
                report = k.get("reports", {}).get(u.name())
                if s == "verify" and report and pl.get("head_at") and utc(report["at"]) > utc(pl["head_at"]):
                    stamp = re.fullmatch(r"verify-.+-(\d{8}-\d{4})\.md", os.path.basename(report["path"]))
                    rows.append(dict(group="verify", label=l, key=f"verify/{u.name()}/{stamp.group(1) if stamp else ''}", at=utc(report["at"]),
                                     what=[f"unit {u.name()} ({l}), {team} on {host}: report {shlex.quote(report['path'])}"],
                                     doc=(host, report["path"]),
                                     cmds=[("open", opener(fleet, host, here, report["path"])),
                                           ("answer", f'crew tell {team}-conductor "On {u.name()}\'s verify report: "')]))
            stages = [st.of(u.name())["stage"] for u in units]
            at, head = k["bolts"].get(b.name(), {}).get("head_at"), k["bolts"].get(b.name(), {}).get("head")
            if stages and at and head and all(x in ("merged", "landed") for x in stages) and not all(x == "landed" for x in stages):
                due = held.get(l, {}).get("due")
                outside = [u.name() for u in units if due is not None and u.name() in due]
                what = [f"bolt {b.name()} ({l}), {team} on {host}: every unit merged; {l}-ops lands it"]
                cmds = [("answer", f'crew tell {l}-ops "Land bolt {b.name()}."')]
                if due is None and l in held:
                    what, cmds = what + ["whether every unit's latest change has been in a batch can't be told: a host did not answer"], []
                elif outside:
                    what = what + [f"lands once {either(outside)} " + ("has" if len(outside) == 1 else "have")
                                   + " been in a batch, which is due for them"]
                    cmds = []
                rows.append(dict(group="land", label=l, key=f"land/{b.name()}/{head[:7]}", at=utc(at), doc=None, what=what, cmds=cmds))
    return rows


def stray_cards(fleet, found, sv, rows, cards, unread):
    """The open cards that match no row, oldest first. A card is left out when whether it has a row can't be known: its
    own host's record did not answer, so its close may not have been read, or it is a verify or land card of a unit or
    bolt whose team's host did not answer."""
    plans_, rowed, out = {l: p for l, _, _, p in found if p}, {(r["label"], r["key"]) for r in rows}, []
    for c in cards:
        if (c["label"], c["key"]) in rowed:
            continue
        down = {h for h, v in sv.items() if not v["ok"]} | set(unread.get(c["label"], {}))
        if c["host"] in down:
            continue
        m = re.match(r"(verify|land)/([a-z0-9][a-z0-9-]*)", c["key"] or "")
        if m:
            plan, kind, name = plans_[c["label"]], m.group(1), m.group(2)
            u = plan.unit(name) if kind != "land" else None
            b = plan.bolt(name if kind == "land" else u.get("Bolt") if u else None)
            t = fleet["teams"].get(b.get("Team")) if b else None
            if t and t["machine"] in down:
                continue
        out.append(c)
    return sorted(out, key=lambda c: (c["at"], c["card"]))


def rail_read(fleet, labels, board=False):
    """Everything the rail is made from, in one read of the labels' plans, proposals, kits and run record: the plans
    found and the errors of those that could not be read, the survey, the open proposals, the cards, the hosts whose
    record did not answer, the landings and gives, and the rows. The survey is of each host holding a bolt; with board,
    of every team of the labels, with the bolt it holds or none, and its dev servers, slots and explorations too, for
    the board (board.py), from which the rail's text is made as well. Nothing is written."""
    errors = {}
    found = plans(fleet, labels, errors)
    held = [(b.get("Team"), b.name()) for _, _, _, p in found if p for b in p.bolts() if b.get("Team")]
    if board:
        held += [(t, None) for l in labels for t in crew.partition_of(fleet, l)["teams"]]
    sv = survey(fleet, held, board=board)
    props = open_proposals(fleet, [l for l, _, _, p in found if p], found)
    times, cards, unread, landings, gives, batched, deploys = rail_record(fleet, found, props)
    return dict(found=found, errors=errors, sv=sv, props=props, times=times, cards=cards, unread=unread, landings=landings,
                gives=gives, rows=rail_rows(fleet, found, sv, props, times, batched) + deploys)


def rail_text(fleet, labels, read, now):
    """The rail as crew rail prints it, from a read rail_read made: its groups in order, each row with when it began to
    wait, how long ago that was, the commands that answer it, and its card key with whether a card is open for it and
    whose, oldest first; then any open card whose row is gone, with the tell that asks its owner to close it. A host
    is named as not answering only when it holds a bolt of the plans read, so a read that surveyed more (the board's)
    gives the same text."""
    found, rows, cards = read["found"], read["rows"], read["cards"]
    holding = {fleet["teams"][b.get("Team")]["machine"] for _, _, _, p in found if p for b in p.bolts() if b.get("Team") in fleet["teams"]}
    sv = {h: v for h, v in read["sv"].items() if h in holding}
    lines = [f"What waits on you ({', '.join(labels)}), as of {now.astimezone():%H:%M:%S}"]
    for g in RAIL:
        lines += ["", g]
        mine = sorted((r for r in rows if r["group"] == g), key=lambda r: (r["at"] is None, r["at"] or now, r["what"][0]))
        if not mine:
            lines.append("  none")
        for r in mine:
            when = r.get("date") or (f"{r['at'].astimezone():%Y-%m-%d %H:%M}" if r["at"] else "-")
            first, *rest = r["what"]
            lines.append(f"  {when:<16}  {age(r['at'], now) if r['at'] else '-':<7}  {first}")
            lines += [" " * 29 + w for w in rest]
            lines += [f"    {c + ':':<8}{cmd}" for c, cmd in r["cmds"]]
            lines += [f"    {'card:':<8}{r['key']}, open, asked by {c['by']}" for c in cards
                      if (c["label"], c["key"]) == (r["label"], r["key"])] or [f"    {'card:':<8}{r['key']}, none open"]
    stray = stray_cards(fleet, found, sv, rows, cards, read["unread"])
    if stray:
        lines += ["", "open cards with no row:"]
    for c in stray:
        lines.append(f"  {c['at'].astimezone():%Y-%m-%d %H:%M}  {age(c['at'], now):<7}  {c['key'] or 'an unkeyed card'} ({c['label']}), "
                     f"asked by {c['by']} on {c['host']}")
        say = f"Close your Pending You card {c['key'] or c['card']}: its row is gone."
        lines.append(f"    {'answer:':<8}crew tell {shlex.quote(c['by'])} " + (f'"{say}"' if re.fullmatch(r"[\w/:. -]+", say) else shlex.quote(say)))
    for h, v in sv.items():
        if not v["ok"]:
            lines.append(f"\n{h} did not answer ({v['error']}): its units and bolts may also wait on you")
    return "\n".join(lines)


def rail_view(fleet, a):
    """crew rail [--label L]: what waits on the user, as rail_text gives it, read from the plans, the proposals, the
    kits and the run record; nothing is written. It prints everything it could read, then exits non-zero naming each
    plan it could not."""
    label = default_label(fleet, a)
    labels = [label] if label else list(fleet["partitions"])
    read = rail_read(fleet, labels)
    print(rail_text(fleet, labels, read, datetime.datetime.now(datetime.timezone.utc)))
    if read["errors"]:
        sys.exit("\n".join(read["errors"].values()))


# ------------------------------------------------------------------------------------------------ crew card

# A card's plannotator session, by its card key, in ~/.local/state/crew/cards/<label>/<key>/ on the owner's host, the
# key's slashes as folders: session.json (pid, document, url, started), and plannotator's result.json once the user
# decides.
CARDS = pathlib.Path.home() / ".local/state/crew/cards"
# The rail's card keys, as crew's card hook reads them.
CARD_KEYS = (r"proposal/\d+", r"batch/\d+-\d+", r"verify/[a-z0-9][a-z0-9-]*/\d{8}-\d{4}", r"land/[a-z0-9][a-z0-9-]*/[0-9a-f]{7}",
             r"deploy/[a-z0-9][a-z0-9-]*/[0-9a-f]{7}", r"deploy-step/[a-z0-9][a-z0-9-]*/[0-9a-f]{7}/\d+")
CARD_START = 10  # seconds a start waits for plannotator to list its session
CARD_POLL = 5  # seconds between a wait's reads


def batch_keys(fleet, label):
    """The keys of the partition's batch cards whose row is open, as the rail reads them: batch/<n>-<k> for each card,
    of at most five units, of each batch the run record holds, but those a card's close has named. Refused naming what
    did not answer (read.1), since a close it did not read may be on it."""
    entries = partition_entries(fleet, label)
    closed = {e["Key"] for e in entries if e.get("Act") == "card.close" and e.get("Card") and e.get("Key")}
    keys = [f"batch/{n}-{k}" for n, _, units in batches(entries) for k in range(1, (len(units) + CARD_UNITS - 1) // CARD_UNITS + 1)]
    return [k for k in keys if k not in closed]


def card_refusal(fleet, name, label, tool, key):
    """Whether the agent crew started may post a Pending You card (post_request) or make an area (create_area) under an
    idempotency key: None to let the call through, else the refusal's words, naming the key to use (briefs.11). A card's
    key must be a rail row's of the agent's own: the planner's proposal/<n> for an open proposal of its partition, read
    from proposals.rec, or batch/<n>-<k> for a card of one of its batches whose row is open, read from the run record; a
    conductor's land/<bolt>/<head> for the bolt its team holds, or verify/<unit>/<stamp> for a unit of it, read from the
    plan. Every other agent owns no key. An area's key is create-area:<owner>/<kit> for a kit the agent's team builds
    or, for the main level, a kit of any team of its partition, read from the teams file. The state branch is fetched
    once (plan.12), and only for the planner's or a conductor's card; what can't be read is a Refusal naming it
    (read.1). The user's own name is never checked."""
    kind, of = role(fleet, name)
    if kind == "user":
        return None
    what = "an area" if tool == "create_area" else "a card"
    if not isinstance(key, str) or not key:
        return f"crew refuses {what} with no idempotencyKey."
    said, cmd = f"crew refuses {what} under {key}", f"{crew.HOME}/plugin/bin/crew"
    if tool == "create_area":
        teams = [of] if kind in ("conductor", "team") else [] if kind == "other" else crew.partition_of(fleet, label)["teams"]
        mine = sorted({f"create-area:{fleet['teams'][t]['kit']['repo']}" for t in teams})
        if key in mine:
            return None
        return f"{said}: " + (f"{name} makes a kit's area only under {either(mine)}." if mine else f"no kit's area is {name}'s to make.")
    rail = f"from the `card:` line under its row in `{cmd} rail --label {label}`"
    if kind == "planner":
        repo, ref = state_of(fleet, label)
        tip = fetch(repo, ref)
        text = show(repo, tip, "proposals.rec") if tip else None
        mine = [f"proposal/{p.get('Proposal')}" for p in Plan(text).recs("Proposal") if p.get("State") == "open"] if text else []
        if key in mine:
            return None
        mine += batch_keys(fleet, label)
        if key in mine:
            return None
        return (f"{said}: {name} posts a card only under proposal/<n> for a proposal of {label} open now, or batch/<n>-<k> "
                f"for a card of one of its batches open now, " + (f"{either(mine)}, {rail}." if mine else "and none is open."))
    if kind == "conductor":
        plan = plans(fleet, [label])[0][3]
        bolts = sorted(b for b, t in holdings(plan)[0].items() if t == of) if plan else []
        units = [u.name() for b in bolts for u in plan.units_of(b)]
        row, _, rest = key.partition("/")
        if any(re.fullmatch(k, key) for k in CARD_KEYS) and (
                (row == "land" and rest.split("/")[0] in bolts) or (row == "verify" and rest.split("/")[0] in units)):
            return None
        if not bolts:
            return f"{said}: {name} posts a card only under a rail row's key of its own, and {of} holds no bolt, so none is."
        mine = [f"land/{b}/<head>" for b in bolts] + (
            [f"verify/<unit>/<stamp> for unit {either(units)}"] if units else [])
        return (f"{said}: {name} posts a card only under a rail row's key of its own: {either(mine)}, "
                f"the head{' or stamp' if units else ''} {rail}.")
    if kind == "main-ops":
        import deploy  # the partition's deploy rows, read where its main level runs
        p = crew.partition_of(fleet, label)
        if p["machine"] != crew.this_host():
            return f"{said}: {name} posts its deploys' cards on {p['machine']}, where {label}'s deploys are kept."
        mine = deploy.open_keys(label)
        if key in mine:
            return None
        return (f"{said}: {name} posts a card only under a deploy row's key of {label} open now, "
                + (f"{either(mine)}, {rail}." if mine else "and none is open."))
    if kind == "team":
        left = ("Write what a proof leaves that only the user can do or check in your proof file, under Left for the user: "
                "the conductor asks it on the bolt's landing card." if name == f"{of}-ops"
                else f"Say what you need with `{cmd} needs`, and the conductor gets it.")
        return f"{said}: {name} owns no card key, since a team's cards are its conductor's. {left}"
    return (f"{said}: {name} owns no card key, since only the planner, the conductors and main-level ops post cards. Tell the partition's "
            "operator agents what you wait on, as your brief says.")


def card_of(fleet, a, unit_needed=True):
    """The partition a card command runs as and the key's folder, a batch card's per unit: refused with no partition, a
    key that is not one of the rail's, a batch card's key with no unit where one is needed, and a unit with any other
    key."""
    label = default_label(fleet, a) or fail("crew card runs as the card's partition: run it as a crew agent, or add --label")
    any(re.fullmatch(k, a.key) for k in CARD_KEYS) or fail(
        f"{a.key} is not a card key: proposal/<n>, batch/<n>-<k>, verify/<unit>/<stamp> or land/<bolt>/<head>")
    batch = a.key.startswith("batch/")
    if batch:
        a.unit or not unit_needed or fail(f"a batch card has a session for each of its units: crew card {a.sub} {a.key} <unit>")
    else:
        not a.unit or fail(f"only a batch card's key takes a unit, and {a.key} is not one")
    if a.unit:
        crew.NAME.match(a.unit) or fail(f"a unit's name is lowercase words with dashes, not {a.unit}")
    return label, CARDS / label / a.key / a.unit if batch and a.unit else CARDS / label / a.key


def plannotator_sessions():
    """The plannotator sessions running on this host, ({pid: session}, None), as `plannotator sessions --json` lists
    them, each with the pid, target and url it lists; (None, why) when the list can't be read."""
    try:
        r = subprocess.run(["plannotator", "sessions", "--json"], capture_output=True, text=True, timeout=8)
    except FileNotFoundError:
        return None, "plannotator is not on this host's path"
    except subprocess.TimeoutExpired:
        return None, "plannotator sessions did not answer in 8 seconds"
    if r.returncode:
        return None, "plannotator sessions: " + ((r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1]
    try:
        got = json.loads(r.stdout)
    except ValueError:
        got = None
    if not isinstance(got, list):
        return None, "plannotator sessions --json printed no list"
    return {s["pid"]: s for s in got if isinstance(s, dict) and isinstance(s.get("pid"), int) and isinstance(s.get("target"), str)
            and isinstance(s.get("url"), str)}, None


def card_recorded(d):
    """The session crew started for a key, as session.json records it, or None when none is recorded. A record crew
    can't read is refused, so nothing is done to a process it names."""
    f = d / "session.json"
    try:
        s = json.loads(f.read_text())
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        fail(f"crew can't read {f}: {e}")
    ok = (isinstance(s, dict) and isinstance(s.get("pid"), int) and s["pid"] > 1
          and all(isinstance(s.get(k), str) for k in ("document", "url", "started")))
    return s if ok else fail(f"{f} is not a session crew recorded: it lacks a pid, document, url or started")


def serving(listed, s):
    """Whether plannotator lists the recorded session's pid as serving its document: a folder's target is listed
    without its last slash."""
    got = listed.get(s["pid"])
    return bool(got) and os.path.realpath(got["target"]) == s["document"]


def card_result(d):
    """The user's decision in a key's session, as plannotator wrote it to result.json: (decision, feedback), feedback
    None when it gave none; None while there is no result."""
    f = d / "result.json"
    try:
        r = json.loads(f.read_text())
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        fail(f"crew can't read plannotator's result {f}: {e}")
    if not isinstance(r, dict) or r.get("decision") not in ("approved", "annotated", "dismissed"):
        fail(f"plannotator's result {f} holds no decision crew knows: approved, annotated or dismissed")
    fb = r.get("feedback")
    return r["decision"], fb if isinstance(fb, str) and fb.strip() else None


def card_row(fleet, label, key):
    """The rail row of one partition with that card key, read as crew rail reads its rows: only the proposals for a
    proposal's key, only the run record's batches for a batch card's, only the host of the unit's team for a verify
    report's."""
    found = plans(fleet, [label])
    plan = found[0][3]
    kind, name = key.split("/")[:2]
    held = []
    if kind not in ("proposal", "batch") and plan and plan.unit(name):
        b = plan.bolt(plan.unit(name).get("Bolt"))
        held = [(b.get("Team"), b.name())] if b and b.get("Team") else []
    sv = survey(fleet, held)
    props = open_proposals(fleet, [label], found) if kind == "proposal" and plan else []
    batched = {}
    if kind == "batch" and plan:
        _, _, unread, _, _, batched, _ = rail_record(fleet, found, [])
        not unread.get(label) or fail(f"crew can't tell whether {key}'s card is still open: "
                                      + "; ".join(f"{h} did not answer" for h in sorted(unread[label])))
    row = next((r for r in rail_rows(fleet, found, sv, props, {}, batched) if r["key"] == key), None)
    if row:
        return row, props
    down = [f"{h} did not answer ({v['error']})" for h, v in sv.items() if not v["ok"]]
    fail(f"no row of {label}'s rail has the card key {key}"
         + (", and whether one would can't be known: " + "; ".join(down) if down else ": its row is gone, so its card has nothing to read"))


def card_stop(proc):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def card_session(fleet, a):
    """crew card session <key> [<unit>] [--label L]: a plannotator session on the document the rail row with that card
    key asks the user to read, started on this host with an Approve button and no browser, and its link printed; for a
    batch card, one session for each unit it holds, on that unit's whole change, started on the host the teams file
    names for the unit's team (code.3) and refused for a unit the card does not hold. While the
    session crew started for the key still runs, its link is printed again and nothing is started. One the user
    approved or annotated before it ended is kept for crew card wait, its link printed again with a line saying so; one
    that ended with no decision is forgotten, and one the user closed undecided is moved aside, so a new one starts.
    Refused for a landing's key, a key with no row, a document on another host, and a link that would open only on this
    host."""
    label, d = card_of(fleet, a)
    a.key.startswith("land/") and fail("a landing card has no document to read, so it has no session")
    row, props = card_row(fleet, label, a.key)
    here = crew.this_host()
    if row["doc"][0] == "batch":
        a.unit in row["units"] or fail(f"{a.key} holds {either(row['units'])}, not {a.unit}: its sessions are its units'")
        t = fleet["teams"].get(row["teams"][a.unit]) or fail(f"{a.unit}'s team {row['teams'][a.unit]} is not in the teams file")
        if t["machine"] != here:
            return forward_card(fleet, t, a, label)
        where, doc, name = here, (change_folder(fleet, t, a.unit),), f"{a.key}'s session of {a.unit}"
    else:
        where, doc, name = row["doc"][0], row["doc"][1:], f"{a.key}'s session"
    where in ("page", here) or fail(f"{a.key}'s document is on {where}, not {here}: its session starts there, from its owner")
    d.mkdir(parents=True, exist_ok=True)
    with open(d / ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        s = card_recorded(d)
        if s:
            listed, why = plannotator_sessions()
            listed is not None or fail(f"crew can't tell whether {name} still runs: {why}")
            if serving(listed, s):
                print(s["url"])
                return
            decided = card_result(d)
            if decided and decided[0] != "dismissed":
                print(s["url"])
                print(f"the user decided in {name} before it ended: crew card wait {a.key}{' ' + a.unit if a.unit else ''} gives "
                      "the decision", file=sys.stderr)
                return
            if decided:
                (d / "result.json").rename(d / f"result.{re.sub(r'[-:]', '', s['started'])}.json")
            (d / "session.json").unlink()
        import shutil
        shutil.which("plannotator") or fail("plannotator is not on this host's path, and a card's session is a plannotator session")
        if where == "page":
            _, n = doc
            p = next(x for x in props if x["proposal"] == n)
            f = d / f"proposal-{n}.md"
            f.write_text(page(p, label))
            doc = str(f)
        else:
            doc = doc[0]
        doc = os.path.realpath(doc)
        os.path.exists(doc) or fail(f"{a.key}'s document {doc} is not on {here}")
        given = doc + "/" if os.path.isdir(doc) else doc  # a folder, as plannotator's usage gives it
        started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        env = dict(os.environ, PLANNOTATOR_SKIP_BROWSER_OPEN="1", PLANNOTATOR_REMOTE="1")
        with open(d / "out", "w") as out, open(d / "err", "w") as err:
            proc = subprocess.Popen(["plannotator", "annotate", given, "--gate", "--json", "--result-file", str(d / "result.json")],
                                    stdin=subprocess.DEVNULL, stdout=out, stderr=err, env=env, start_new_session=True)
        deadline = time.monotonic() + CARD_START
        while True:
            listed, why = plannotator_sessions()
            got = (listed or {}).get(proc.pid)
            if got:
                break
            if proc.poll() is not None:
                said = (d / "err").read_text().strip().splitlines()
                fail(f"plannotator ended before {name} was ready" + (f": {said[-1]}" if said else f", exit {proc.returncode}"))
            if time.monotonic() > deadline:
                card_stop(proc)
                fail(f"plannotator did not list {name} within {CARD_START} seconds" + (f" ({why})" if why else "")
                     + ", so crew ended it")
            time.sleep(0.2)
        import urllib.parse
        host = urllib.parse.urlsplit(got["url"]).hostname or ""
        if host in ("localhost", "::1") or host.startswith("127."):
            card_stop(proc)
            fail(f"plannotator gave {name} the link {got['url']}, which would open only on {here}, so crew ended it: "
                 "a card's session needs PLANNOTATOR_URL_HOST naming the host on the tailnet (swancloud sets it to auto)")
        tmp = d / ".session.json"
        tmp.write_text(json.dumps({"pid": proc.pid, "document": doc, "url": got["url"], "started": started}) + "\n")
        tmp.replace(d / "session.json")
    print(got["url"])


def change_folder(fleet, t, unit):
    """A unit's whole change on its team's host, this one: in its place while it has one, else on its bolt's worktree,
    else on the kit's main, open or archived."""
    k = survey(fleet, [(t["name"], None)]).get(t["machine"], {})
    kit = k.get("kits", {}).get(t["kit"]["main"], {}) if k.get("ok") else {}
    kit.get("ok") or fail(f"{t['kit']['main']} on {t['machine']} could not be read: {kit.get('error') or k.get('error')}")
    pl = kit["places"].get(unit)
    where = [f"{pl['path']}/openspec/changes/{unit}"] if pl else []
    where += [f"{w}/openspec/changes/{unit}" for w in (b["worktree"] for b in kit["bolts"].values()) if w]
    where += [f"{t['kit']['main']}/openspec/changes/{unit}"]
    where += sorted(str(x) for x in pathlib.Path(t["kit"]["main"], "openspec/changes/archive").glob(f"????-??-??-{unit}"))
    return next((w for w in where if os.path.isdir(w)), None) or fail(f"unit {unit}'s change is in no checkout of {t['kit']['name']} on {t['machine']}")


def forward_card(fleet, t, a, label):
    """A batch card's command for one of its units, run on the host the teams file names for that unit's team (code.3),
    as the one asking here; its output passed on, and its failure this command's."""
    r = crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], "card", a.sub, a.key, a.unit, "--label", label))
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode:
        sys.exit(r.returncode)


def batch_team(fleet, label, key, unit):
    """The team of a unit a batch card holds, from the batch in the run record, whether or not the card is still open."""
    n, k = (int(x) for x in key.split("/")[1].split("-"))
    entries = partition_entries(fleet, label)
    for m, _, units in batches(entries):
        if m == n:
            part = units[(k - 1) * CARD_UNITS:k * CARD_UNITS]
            names = [u for u, *_ in part]
            names or fail(f"batch {n} of {label} has no card {k}")
            team = next((tm for u, tm, _ in part if u == unit), None) or fail(f"{key} holds {either(names)}, not {unit}")
            return fleet["teams"].get(team) or fail(f"{unit}'s team {team} is not in the teams file")
    fail(f"{label}'s run record holds no batch {n}")


def card_wait(fleet, a):
    """crew card wait <key> [--label L]: wait, with no timeout, until the user decides in the session crew started for
    the key, or it ends without a decision, and print which: approved or annotated with the user's words after it as
    they are, closed in plannotator with no decision, or ended with no decision; a decision made before the wait began
    is printed at once. A session crew ended, its card closed, is said so. Refused for a key with no session started."""
    label, d = card_of(fleet, a)
    if a.unit:
        t = batch_team(fleet, label, a.key, a.unit)
        if t["machine"] != crew.this_host():
            return forward_card(fleet, t, a, label)
    name = f"{a.key} {a.unit}" if a.unit else a.key
    card_recorded(d) or fail(f"no session was started for card {name}: crew card session {name} starts one")
    said = {"approved": "approved", "annotated": "annotated", "dismissed": "closed in plannotator with no decision"}
    while True:
        decided = card_result(d)
        if decided:
            print(f"{name}: {said[decided[0]]}")
            if decided[1]:
                print(decided[1], end="" if decided[1].endswith("\n") else "\n")
            return
        s = card_recorded(d)
        if s is None:
            print(f"{name}: crew ended its session, as its card closed or crew card end was run")
            return
        listed, _ = plannotator_sessions()  # a list that can't be read says nothing: the wait goes on
        if listed is not None and not serving(listed, s) and not card_result(d) and card_recorded(d) == s:
            print(f"{name}: the session ended with no decision")
            return
        time.sleep(CARD_POLL)


def end_session(label, key, unit=None):
    """End the plannotator session crew started for a card key on this host, a batch card's for one of its units, and
    forget it: its folder goes first, so a wait on it hears crew ended it, then the recorded pid is sent SIGTERM only
    while plannotator lists it as serving the recorded document (read.4). Returns what it did, in words. crew's card
    hook runs it when a crew agent closes or withdraws a keyed card."""
    any(re.fullmatch(k, key) for k in CARD_KEYS) or fail(f"{key} is not a card key")
    d = CARDS / label / key / unit if unit else CARDS / label / key
    key = f"{key} {unit}" if unit else key
    if not d.is_dir():
        return f"no session was running for {key}"
    try:
        s = card_recorded(d)
    except Refusal:
        s = None
    listed, why = plannotator_sessions() if s else (None, None)
    import shutil
    shutil.rmtree(d)
    for p in d.parents:
        if p == CARDS / label or not p.is_dir() or any(p.iterdir()):
            break
        p.rmdir()
    if not s:
        return f"no session was recorded for {key}; its folder is removed"
    if listed is None:
        return f"crew can't read plannotator's sessions ({why}): it ended nothing, and {key} is forgotten"
    if not serving(listed, s):
        return f"plannotator lists no session of pid {s['pid']} on {s['document']}: crew ended nothing, and {key} is forgotten"
    try:
        os.kill(s["pid"], SIGTERM)
    except ProcessLookupError:
        return f"{key}'s session had already ended, and {key} is forgotten"
    return f"ended {key}'s session, plannotator pid {s['pid']}"


def card_end(fleet, a):
    """crew card end <key> [<unit>] [--label L]: end the session crew started for a card key, and forget the key; a batch
    card's for one of its units on that unit's team's host, or with no unit for each of its units, as its close does."""
    label, _ = card_of(fleet, a, unit_needed=False)
    if not a.key.startswith("batch/"):
        print(end_session(label, a.key))
        return
    names = [a.unit] if a.unit else card_units(fleet, label, a.key)
    for u in names:
        t = batch_team(fleet, label, a.key, u)
        if t["machine"] != crew.this_host():
            forward_card(fleet, t, argparse.Namespace(**dict(vars(a), unit=u)), label)
        else:
            print(end_session(label, a.key, u))


def card_units(fleet, label, key):
    """The units a batch card holds, from the batch in the run record."""
    n, k = (int(x) for x in key.split("/")[1].split("-"))
    for m, _, units in batches(partition_entries(fleet, label)):
        if m == n:
            return [u for u, *_ in units[(k - 1) * CARD_UNITS:k * CARD_UNITS]]
    fail(f"{label}'s run record holds no batch {n}")


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
    v = sub.add_parser("rail")
    v.add_argument("--label")
    ca = sub.add_parser("card").add_subparsers(dest="sub", required=True)
    for c in ("session", "wait", "end"):
        x = ca.add_parser(c)
        x.add_argument("key")
        x.add_argument("unit", nargs="?")
        x.add_argument("--label")

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

    pp = sub.add_parser("plan").add_subparsers(dest="sub", required=True)
    x = pp.add_parser("propose")
    x.add_argument("file")
    x.add_argument("--replaces", type=int)
    x.add_argument("--label")
    x = pp.add_parser("proposed")
    x.add_argument("n", nargs="?", type=int)
    x.add_argument("--label")
    x.add_argument("--json", action="store_true")
    x.add_argument("--open", action="store_true")
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
    x.add_argument("stage", choices=("construct", "code", "verify", "settle", "merge"))
    x.add_argument("words", nargs="?", default="")
    x.add_argument("--label")
    x = sub.add_parser("_ended")
    x.add_argument("team")
    x.add_argument("unit")
    x.add_argument("stage")
    x.add_argument("row")
    x = sub.add_parser("_bolt-of")
    x.add_argument("team")
    x = sub.add_parser("_amended")
    x.add_argument("team")
    x = sub.add_parser("_place")
    x.add_argument("team")
    x.add_argument("path")
    x.add_argument("branch")
    x.add_argument("base")
    x = sub.add_parser("_carry")
    x.add_argument("team")
    x.add_argument("fix")
    x.add_argument("bolt")
    x.add_argument("--move", nargs=2, metavar=("OLD", "NEW"))
    x = sub.add_parser("_slots")
    x.add_argument("team")
    x.add_argument("--ends", action="store_true")
    x = sub.add_parser("_tidy")
    x.add_argument("team")
    x = sub.add_parser("_rebase")
    x.add_argument("team")
    x.add_argument("--tidy", action="store_true")
    x = sub.add_parser("_merging")
    x.add_argument("team")
    x.add_argument("bolt")
    x = sub.add_parser("_review")
    x.add_argument("label")
    x = sub.add_parser("_review-wait")
    x.add_argument("label")
    x.add_argument("--timeout", type=int, default=3600000)
    x = sub.add_parser("_in-bolt")
    x.add_argument("unit")
    x.add_argument("team")
    x = sub.add_parser("_ends")
    x.add_argument("team")
    x.add_argument("--slot")
    x.add_argument("--ending", action="store_true")
    x = sub.add_parser("_needs")
    x.add_argument("team")
    x.add_argument("--slot", required=True)
    x.add_argument("words")
    x = sub.add_parser("_wait")
    x.add_argument("team")
    x.add_argument("--slot", required=True)
    x.add_argument("--timeout", type=int, default=3600000)
    x.add_argument("--stuck", type=int, default=900000)
    return ap


COMMANDS = {
    ("state", "init"): state_init, ("bolts", None): bolts_view, ("rail", None): rail_view,
    ("card", "session"): card_session, ("card", "wait"): card_wait, ("card", "end"): card_end,
    ("bolt", "new"): direct(("bolt", "new")), ("bolt", "give"): bolt_give, ("bolt", "order"): direct(("bolt", "order")), ("bolt", "drop"): direct(("bolt", "drop")),
    ("bolt", "land"): bolt_land,
    ("unit", "add"): direct(("unit", "add")), ("unit", "split"): direct(("unit", "split")), ("unit", "amend"): direct(("unit", "amend")),
    ("unit", "order"): direct(("unit", "order")), ("unit", "after"): direct(("unit", "after")),
    ("unit", "move"): direct(("unit", "move")), ("unit", "drop"): direct(("unit", "drop")),
    ("_team-of", None): team_of_unit, ("_run", None): run_check, ("_ended", None): stage_ended_row, ("_bolt-of", None): bolt_of_team, ("_amended", None): amended_units,
    ("_place", None): place_cmd,
    ("_carry", None): carry_cmd, ("_slots", None): slots_cmd, ("_tidy", None): tidy, ("_rebase", None): rebase_cmd, ("_merging", None): merging, ("_review", None): review_start, ("_review-wait", None): review_wait, ("_in-bolt", None): in_bolt, ("signal", None): signal, ("signal-move", None): signal_move,
    ("signal-show", None): signal_show,
    ("_ends", None): stage_ends, ("_wait", None): stage_wait, ("_needs", None): stage_needs,
    ("plan", "propose"): plan_propose, ("plan", "proposed"): plan_proposed, ("plan", "agree"): plan_agree,
    ("plan", "approve"): plan_approve, ("plan", "drop"): plan_drop,
}
# The act a command that moves work records, done or refused. A command that only reads records nothing.
ACTS = {
    ("state", "init"): "state.init", ("bolt", "new"): "bolt.new", ("bolt", "give"): "bolt.give", ("bolt", "order"): "bolt.order",
    ("bolt", "drop"): "bolt.drop", ("bolt", "land"): "bolt.land", ("unit", "add"): "unit.add", ("unit", "split"): "unit.split",
    ("unit", "amend"): "unit.amend",
    ("unit", "order"): "unit.order", ("unit", "after"): "unit.after", ("unit", "move"): "unit.move", ("unit", "drop"): "unit.drop",
    ("signal", None): "capture", ("signal-move", None): "signal.move",
    ("_run", None): "stage.start", ("_needs", None): "stage.end",
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
    if a.cmd == "_needs":
        out.append(f"agent/{a.team}-{a.slot}")
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
