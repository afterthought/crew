#!/usr/bin/env python3
"""plan.py: the bolt plan, one recutils plan.rec per flywheel, on the flywheel's branch of its state repository.

A flywheel is a partition's loop, named by its label. Its state is the files on the branch <label>/main of the
state repository the teams file names for it (`state`): plan.rec, moves.rec, proposals.rec, the signals agents record
under signals/, and the run record under runs/<host>/.
The plan holds only intent: Bolt and Unit records, a Unit record marked Kind: chore being a chore (plan.11). Every
stage is read from the kits. The planner changes it only
by a proposal (proposals.rec) the user approves; who else writes it directly is may_write's table. A write fetches the branch
over https, applies itself to the tip, checks each file it changed with recfix (the plan with crew's own rules
too), commits through a temporary index in crew's own bare cache of the repo (no working tree is touched), and
pushes without force. A push that is refused because someone wrote first is applied again to the new tip, up to
five times. A write that changes several files is one commit; its run-record entry follows it as a commit of its own.

  crew state init <label>                    create <label>/main in the state repository, adopting plan/<label> and
                                             the moves where the partition's blueprints repos have them
  crew bolts [<bolt>] [--label L] [--json]   every bolt, unit and chore of the plans, each one's stage read from its kit
  crew rail [--label L]                      what waits on the user: open proposals, review batches and bolts to
                                             land, each with when it began to wait, what answers it and
                                             its card key, with whether a card is open for it; then the open cards
                                             whose row is gone; its sweep posts again, on its owner's host, each row's
                                             card and still-proposed record's another host holds or its owner lost,
                                             saying the older copy is dead, and tries again the reading of a batch's, a
                                             long proposal's or a kit's landings card that stands without it, ten
                                             minutes on, a landings card's rows' each on its team's host
  crew record <kit> <number> --proposed|--accepted|--rejected [--settled-in-pane --excerpt "<words>"] [--alternatives <file>]
                                             the design agent's record at each turn of its status, read on the kit's
                                             main, raising its card unless settled in the pane, the user's yes read in
                                             the design agent's transcript as theirs, a choice when a rule decided,
                                             saying an older copy is dead when another host holds one, changing it on
                                             a revision and closing it on accepted or rejected
  crew card session|wait|end <key> [<unit>]  a plannotator session on what the rail row with that card key asks the
                                             user to read, started on this host with no browser and its link printed,
                                             a batch card's one per unit on that unit's team's host; the user's decision
                                             in it, waited for, a bolt's reading started first when none runs while
                                             it is a row of its kit's landings card, a batch's while the planner holds
                                             its card, waiting on the card alone when it will not open; a reading
                                             started anew, or given again to a card standing without it, changing its
                                             open card to carry the link, each try recorded; and its end, which a
                                             card's close brings too
  crew card answer batch/<n> --excerpt "<words>"
                                             the user's answer to a batch in their own words in the planner's or the
                                             operator's pane, recorded once crew reads the words in that agent's own
                                             transcript as the user's, no words in the run record: the batch's card
                                             closed with them, the planner's wait on it ended, and the planner told
                                             them when the operator ran it
  crew bolt new <bolt> "<goal>" --repo <kit> [--source S]... [--before <bolt>]
  crew bolt give <team> [<bolt>]             the team takes the bolt (default: the first planned in its kit)
  crew bolt order <bolt> --before <bolt>|--first|--last
  crew bolt drop <bolt> "<reason>" [--requeue]
                                             the bolt and its units out of the plan, or with --requeue its units
                                             queued, refused while one has a worktree; its worktrees then go from its
                                             team's host
  crew bolt land <bolt>                      once every unit has landed on main, recording the commit main then
                                             holds; its worktree then goes from its team's host, unless it has
                                             uncommitted changes; a bolt no team holds lands once each unit's change
                                             is on its kit's main
  crew bolt submit <bolt>... [--excerpt "<the user's words>"] [--label L]
                                             main-level ops's landing of one kit's bolts through sluice, in order; with
                                             --excerpt, on the user's words in ops's pane, submitted only once crew
                                             reads them in ops's own transcript as the user's, no words in the run
                                             record, and the landing cards closed with them at crew bolt land. One
                                             that did not land for its own content, a conflict or a check that ran
                                             and failed, is held on its row; one sluice or its host stopped keeps its
                                             box and the user's word, and is submitted again once that is cleared
  crew unit add <unit> "<intent>" --bolt <bolt>|--repo <kit> [--source S]... [--after U]... [--before U] [--signal ID]
                                             [--unblocks <bolt>]
  crew unit split <unit> "<narrowed intent>" --into <unit> "<intent>" [--into ...]
  crew unit amend <unit> "<new intent>"      a unit's intent replaced; one with a worktree is marked amended, and its
                                             construct runs again at once on its team's host, its conductor told
  crew unit order <unit> --before <unit>|--first|--last
  crew unit after <unit> <unit>...|--none
  crew unit move <unit> <bolt>|queue [--unblocks <bolt>]
  crew unit drop <unit> "<reason>"
  crew chore add <chore> "<words>" --bolt <bolt>|--repo <kit> [--source S]... [--after U]... [--before U] [--signal ID]
                                             [--unblocks <bolt>]
  crew chore order|after|move|drop ...       as a unit's, of a chore: planned maintenance that changes nothing a spec
                                             says must be true, built in its bolt by code, verify and merge
  crew plan propose <file> [--replaces <n>]  the planner's proposal: a Case and the plan commands it would run (Do);
                                             crew raises its card in the planner's name, or changes the card of the
                                             one it replaces
  crew plan proposed [<n>] [--json] [--open] the open proposals, or one as the user reads it; --open writes that to a
                                             file on this host and opens it in plannotator
  crew plan agree <n> [--team <team>]        a conductor's agreement to a proposal that touches its bolt
  crew plan card <n>                         the proposal's Pending You card as JSON, from the branch alone, and its
                                             picture, a PNG crew draws, written on this host
  crew plan approve <n> [--clear <unit>...]  the proposal applied as read, in one commit, but for the new units the
                                             user left out
  crew plan answer <n> <question> <answer>... [--note "<text>"]
                                             one answer of the proposal's card, kept on this host; the change is
                                             applied with its boxes as they stand once every question is answered
  crew plan drop <n> "<reason>"              the proposal closed unapplied
  crew signal <slug> "<what it asserts>" --excerpt "<the words, verbatim>"|--excerpt-file <path> [--kind K] [--subject a,b]
                                             a finding, as a capture and its signal on the flywheel's branch: an
                                             agent's excerpt checked against its own Claude transcript and graded, the
                                             user's note at a shell its own excerpt
  crew signal show <id>                      a signal with its capture's provenance and its move, from either home
  crew signal move <id> attach|challenge|new-territory|answered|drop [--target T] [--reason R]
                                             curation's move for a signal, in moves.rec on the flywheel's branch

A signal recorded through crew is on the flywheel's branch, under signals/; one the daily pass read from a meeting or
a channel is in the partition's first blueprints repo. An id is looked up in that order. Every command that takes a
signal's id takes its full id, <capture>/<NN>-<slug>, or its short one, <capture>/<NN>, such as
2026-10-20-swancloud-planner-72efd8ec/01: the one signal of that capture numbered NN, written by its full id.

A command that names no partition reads them all, or the agent's own (CREW_LABEL); --label names one.
"""
import argparse, base64, contextlib, datetime, fcntl, io, json, os, pathlib, re, shlex, subprocess, sys, time
# getpass, hashlib, shutil, tempfile and urllib.parse are imported where they are used: every crew command starts this
# module afresh, and those five (OpenSSL, the compression modules) were a third of its start.
from signal import SIGTERM
# Run as the command, this module is the plan the modules it imports import, so the command holds one reading of the
# branch, its entries' pushes among its steps, and fetches it once (plan.12), rather than a second copy fetching anew.
if __name__ == "__main__":
    sys.modules.setdefault("plan", sys.modules[__name__])

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew  # noqa: E402
import gather  # noqa: E402
import kit  # noqa: E402
import record  # noqa: E402
import transcript  # noqa: E402
import cards  # noqa: E402
from cards import joined, new_units  # noqa: E402
from crew import Refusal, Stopped, fail  # noqa: E402
from picture import cut  # noqa: E402

REPLAYS = 5
# How many times a fetch is made again when another command on this host moved crew's cache's ref of the branch while it
# fetched, which git refuses as a ref that is at another commit than it read: every act pushes its entry (read.5), so
# commands on one host fetch and push side by side.
LOCK_TRIES = 5
# What a command found out before it wrote or was refused: the partition whose run record its entry goes in.
CONTEXT = {}
CACHE = pathlib.Path.home() / ".cache/crew/git"
HEADER = """\
# The partition's bolts and their units and chores: what is to be built, in
# which bolt, in what order. Nothing here says how far anything has got: `crew
# bolts` reads that from the kits. Written only by `crew bolt`, `crew unit` and
# `crew chore`.
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
%doc: One OpenSpec change named Unit, built on unit/<Unit> at <Repo>/places/<Unit>; or, marked Kind: chore, a chore: planned maintenance with no change, its Intent its words, built on chore/<Unit> at <Repo>/places/chore-<Unit>.
%key: Unit
%type: Unit regexp /^[a-z0-9][a-z0-9-]*$/
%type: Bolt rec Bolt
%type: Kind enum chore
%mandatory: Repo Intent
%allowed: Unit Repo Bolt Kind Intent After Source Amended
%unique: Repo Bolt Kind Intent
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


def is_chore(u):
    """Whether a record of the plan's Unit set is a chore, marked Kind: chore (plan.11), rather than a unit."""
    return u.get("Kind") == "chore"


def kind_of(u):
    """A Unit record's kind as crew names it: chore or unit, which is also its command and its run-record object."""
    return "chore" if is_chore(u) else "unit"


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

    def work(self):
        """Every record of the Unit set, units and chores, in file order: the work built in bolts (plan.11)."""
        return self.recs("Unit")

    def units(self):
        return [u for u in self.work() if not is_chore(u)]

    def chores(self):
        return [u for u in self.work() if is_chore(u)]

    def bolt(self, name):
        return next((b for b in self.bolts() if b.name() == name), None)

    def item(self, name):
        """The unit or chore by that name: one key holds both."""
        return next((u for u in self.work() if u.name() == name), None)

    def unit(self, name):
        u = self.item(name)
        return u if u is not None and not is_chore(u) else None

    def chore(self, name):
        u = self.item(name)
        return u if u is not None and is_chore(u) else None

    def work_of(self, bolt):
        return [u for u in self.work() if u.get("Bolt") == bolt]

    def units_of(self, bolt):
        return [u for u in self.units() if u.get("Bolt") == bolt]

    def queue(self, repo=None):
        """The queued work of a repo, or of every repo: units and chores with no bolt, in order."""
        return [u for u in self.work() if not u.get("Bolt") and repo in (None, u.get("Repo"))]

    def group(self, u):
        """The work built in order with this unit or chore: its bolt's, or its repo's queue."""
        return self.work_of(u.get("Bolt")) if u.get("Bolt") else self.queue(u.get("Repo"))

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


def in_step(plan, header=HEADER):
    """Bring each record descriptor of a plan, or of another of crew's files with its header, in step with crew's own
    (HEADER), so a branch started before a field was allowed takes it on its next write. Returns whether any changed."""
    want = {declares(p): p for p in Plan(header).paras if declares(p)}
    changed = False
    for i, p in enumerate(plan.paras):
        k = declares(p)
        if k in want and p != want[k]:
            plan.paras[i], changed = list(want[k]), True
    return changed


def check(plan):
    """crew's own rules, which recfix cannot check: a unit's or chore's bolt exists in the same repo, and its After
    names units or chores of the same bolt, with no cycle; a chore is never marked amended (plan.11)."""
    bolts = {b.name(): b for b in plan.bolts()}
    units = {u.name(): u for u in plan.work()}
    for u in plan.work():
        b, k = u.get("Bolt"), kind_of(u)
        if b:
            b in bolts or fail(f"{k} {u.name()} names bolt {b}, which the plan does not hold")
            bolts[b].get("Repo") == u.get("Repo") or fail(f"{k} {u.name()} is in {u.get('Repo')} and its bolt {b} in {bolts[b].get('Repo')}")
        not (is_chore(u) and u.get("Amended")) or fail(f"chore {u.name()} is marked amended, and a chore has no amendment: "
                                                      "its words change by a drop and an add")
        for a in u.all("After"):
            a in units or fail(f"{k} {u.name()} comes after {a}, which the plan does not hold")
            b or fail(f"{k} {u.name()} is queued, so it can come after nothing; dependencies are within a bolt")
            units[a].get("Bolt") == b or fail(f"{k} {u.name()} comes after {a}, which is in {units[a].get('Bolt') or 'the queue'}, not {b}")
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
    answer by host, in this process's memory, every crew command being one process. Inside fresh() nothing is served
    from it, so a wait looks again each time; what is read there is still kept. A reading is never a service or state:
    it is gone with its command (state.4)."""

    def __init__(self):
        self.memory, self.bypass = {}, 0

    def held(self, name):
        return self.memory.get(name)

    def keep(self, name, value):
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

    @staticmethod
    def sweep():
        """A reading folder that a killed command of an older crew left, when its steps were processes of their own,
        goes once it is a day old."""
        root = pathlib.Path.home() / ".cache/crew/reads"
        try:
            old = [d for d in root.iterdir() if re.fullmatch(r".{8}", d.name) and d.is_dir() and time.time() - d.stat().st_mtime >= 86400]
        except OSError:
            return
        if old:
            import shutil
            for d in old:
                shutil.rmtree(d, ignore_errors=True)

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
    for n in range(LOCK_TRIES):
        r = git(repo, "fetch", "--quiet", "--no-tags", url(repo), f"+refs/heads/{ref}:refs/crew/{ref}", check=False)
        if not (r.returncode and "cannot lock ref" in r.stderr):
            break
        time.sleep(0.1 * (n + 1))
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
    """make(tip) gives a file's new text (or, with path None, {path: text}) and the commit message, or refuses; or a
    chain of them, a list, each committed on the one before, as the run record's entries are, one commit each. Every
    file a commit holds is checked first. The first attempt starts from the tip the command holds; the last commit is
    pushed without force, and when the push is refused because the branch moved, the branch is fetched afresh and make
    runs again on the new tip, the whole chain made again, up to five times (plan.1, state.1). The command then holds
    the commit it pushed, so its later steps see its own write."""
    tip = fetch(repo, ref)
    for _ in range(1 + REPLAYS):
        made = make(tip)
        sha = tip
        for text, message in made if isinstance(made, list) else [made]:
            files = text if path is None else {path: text}
            checked(files)
            sha = commit(repo, sha, files, message)
        r = git(repo, "push", "--quiet", url(repo), f"{sha}:refs/heads/{ref}", check=False)
        if r.returncode == 0:
            # The cache's own mark of the tip: another command on this host moving it at the same moment refuses
            # nothing the push made, and the next fetch sets it.
            git(repo, "update-ref", f"refs/crew/{ref}", sha, check=False)
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

    def item(self, name):
        """The unit or chore by that name, which a command's After or --before may name either way round."""
        return self.plan.item(name) or self.gone("Unit", name, "unit or chore")

    def of(self, a):
        """The unit or chore a unit or chore command names (a.unit), refused when it is of the other kind (plan.11)."""
        u = self.plan.item(a.unit) or self.gone("Unit", a.unit, a.cmd)
        why = kind_refusal(kind_of(u), a.cmd, a.sub, a.unit)
        return u if not why else fail(why)

    def gone(self, kind, name, word=None):
        by = removed_by(self.repo, self.tip, kind, name)
        fail(f"no {word or kind.lower()} {name} in {self.label}/main of {self.repo}" + (f": {by} removed it" if by else ""))


def message(subject, body, eid):
    """A commit message: the subject, the body where there is one, and the Crew-Entry trailer naming the run-record
    entry that describes the commit."""
    return subject + (f"\n\n{body}" if body else "") + (f"\n\nCrew-Entry: {eid}" if eid else "") + "\n"


def write(fleet, label, change, subject, body="", act=None, on=(), frm=(), fields=None):
    """Apply change(Write) to the tip of the flywheel's branch, its plan's record descriptors first brought in step
    with crew's, commit every file it changed, each checked first, and push, replaying on a refused push. change returns the bolts it touched; each one's conductor is told the subject, unless it wrote it.
    The commit names its run-record entry; with act, that entry is written once pushed, naming on and frm and whatever
    the change added to them, with the act's own fields, and reaches the branch as the commit after it (read.5).
    Returns the commit."""
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
        files = {"plan.rec": w.plan.text(), **w.files}
        seen.update(before=before, after=w.plan.teams(), touched=touched, quiet=w.quiet, label=label,
                    subject=f"{w.subject or subject} ({agent()})", on=list(on) + w.on, frm=list(frm) + w.frm)
        return files, message(seen["subject"], body, seen["eid"])
    sha = land(repo, ref, None, make)
    print(f"{ref} {sha[:7]}: {seen['subject']}")
    if act:
        record.emit(label, act, seen["on"], seen["frm"], [f"{repo}@{sha}"], record.subject(seen["subject"]), eid=seen["eid"], **(fields or {}))
    notify(fleet, seen, seen["subject"])
    return sha


def either(rows):
    return rows[0] if len(rows) == 1 else ", ".join(rows[:-1]) + " or " + rows[-1]


def notify(fleet, seen, subject):
    """Tell the conductor of each team holding a bolt the write touched, before or after, unless that conductor wrote it,
    or the write's own command greets it instead; crew closes a row's card itself at the event that ends it, so no
    write names a card to close. Tell the partition's dispatchers that are up of a bolt
    added, or of one landed or dropped that frees a team, so a free team gets its next bolt, unless one of them wrote
    it."""
    tells, shown, dispatch = notices(fleet["teams"], seen, agent(), subject)
    for to, text in tells:
        crew.tell(fleet, to, text)
    for line in shown:
        print(line)
    if dispatch:
        tell_dispatchers(fleet, seen["label"], f"{subject}. Give a free team its next bolt.")


def tell_dispatchers(fleet, label, text):
    """Each of the partition's dispatchers that is up told the text, unless it is the one asking."""
    for host in crew.partition_hosts(fleet, label):
        d = f"{label}-dispatch-{host}"
        if d != agent() and crew.agent_status(fleet, d):
            crew.tell(fleet, d, text)


def notices(teams, seen, me, subject):
    """Who a write tells, as facts (teams.7): each conductor of a team holding a bolt the write touched, before or after
    it, unless it wrote it (me) or the write's own command greets it (seen["quiet"]), sent the subject, nothing more,
    since crew closes a row's card itself; and whether the dispatchers hear of it, a bolt added or one a team held
    landed or dropped. Returns ([(conductor, text)], [lines shown], whether the dispatchers are told)."""
    before, after, touched = seen["before"], seen["after"], seen["touched"]
    tells, shown = [], []
    for t in sorted(x for x in {before.get(b) for b in touched} | {after.get(b) for b in touched}
                    if x and x not in seen["quiet"] and x in teams):
        if f"{t}-conductor" != me:
            tells.append((f"{t}-conductor", subject))
    added = [b for b in touched if b not in before and b in after]
    freed = [b for b in touched if b not in after and before.get(b)]
    return tells, shown, bool(added or freed)


def push_now(fleet, label):
    """crew events --push: each entry of the host's run record of the label that its branch lacks, which a push that
    was refused left in the host's file, pushed now, each as its own commit (record.reach); said when there is none."""
    ref, host = state_of(fleet, label)[1], crew.this_host()
    n = record.reach(label)
    print(f"{ref}: pushed {n} of {host}'s entries" if n else f"{ref}: nothing of {host}'s run record left to push")


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
    shared = shared_name(label, [(bp, plan) for bp, _, plan in old])
    shared is None or fail(shared)
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
            joined_into(have, plan, bp, f"{ref} of {repo}", label)
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
            files["moves.rec"] = moves_file(recs)
            if show(repo, w_tip, "proposals.rec") is None:
                files["proposals.rec"] = PROPOSALS
        tip = init_step(repo, ref, label, f"state({label}): moves.rec, with the {len(recs)} moves of {src}'s signals/moves.rec{at}", start_moves)
        did.append(f"added moves.rec with {len(recs)} moves of {src}{at}")
    if did:
        print(f"{ref} of {repo} {tip[:7]}: " + "; ".join(did))
    else:
        print(f"{ref} of {repo} exists, at {tip[:7]}: nothing to do")


def shared_name(label, plans):
    """Why the partition's plans can't be adopted together, or None: two of them, [(blueprints repo, plan)], hold a
    bolt, or a unit or chore, by the same name."""
    owner = {}
    for bp, plan in plans:
        for r in plan.bolts() + plan.work():
            other = owner.setdefault((r.kind, r.name()), bp)
            if other != bp:
                return (f"plan/{label} of {other} and plan/{label} of {bp} both hold {r.kind.lower()} {r.name()}: "
                        "rename one in its plan first; nothing was written")
    return None


def joined_into(have, plan, bp, where, label):
    """Another blueprints repo's plan joined into the branch's (have): each bolt and unit added, a Source naming no repo
    made to name bp, refused when the branch (where) already holds one by that name; then crew's own rules checked."""
    for r in plan.bolts() + plan.work():
        (have.bolt if r.kind == "Bolt" else have.item)(r.name()) is None or fail(
            f"{where} already holds {r.kind.lower()} {r.name()}, which plan/{label} of {bp} also holds; nothing was joined")
        have.insert(Rec(r.kind, [(n, v if n != "Source" or ":" in v else f"{bp}:{v}") for n, v in r.fields]))
    check(have)


def moves_file(recs):
    """A new moves.rec: crew's descriptor, then each move it starts with."""
    return MOVES + "".join("\n" + "\n".join(r.lines()) + "\n" for r in recs)


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
            return json.loads(json.dumps({k["main"]: gather.kit(k, req.get("sites"), running, req.get("board"), req.get("fetch"))
                                          for k in req["kits"]})), None
        except Exception as e:
            import traceback
            return None, traceback.format_exception_only(e)[-1].strip()
    r = crew.on_machine(fleet, host, ["python3", "-", json.dumps(req)], input=GATHER)
    if r.returncode:
        return None, ((r.stderr or "").strip().splitlines() or [f"exit {r.returncode}"])[-1]
    return json.loads(r.stdout), None


def survey(fleet, held, sites=False, board=False, fetch=False):
    """Read the kits of every host holding active bolts, one call per host. held is [(team, bolt)] or [(team, bolt, kit)], the kit the bolt's
    as the plan's Repo names it. The answer is
    per host: its kits by main checkout, or why it did not answer. With sites, each worktree's devurl names and
    the host's running portless routes too; board implies sites and adds each team's slots and the explorations on
    each kit's main, for the board. With board, each kit is asked for the slots of every team that builds it on that
    host. With fetch, each kit's GitHub is fetched on its host before it is read, for a read a decision of the moment
    rests on (plan.18, plan.19), and a fetch that fails reads that kit unread with git's words. A kit the command has
    already read is not asked again, but by a survey that fetches, which must read after its own fetch; what a host
    answers is kept for the command's later steps; a sites survey is neither served nor kept."""
    sites = sites or board
    hosts = {}
    for team, bolt, *repo in held:
        t = fleet["teams"].get(team)
        if not t:
            continue
        # A team with a bolt reads that bolt's kit; one asked of with none, every kit it holds (record 0035).
        try:
            kits = [crew.with_kit(t, repo[0])["kit"]] if repo and repo[0] else [t["kit"]] if bolt else crew.kits_of(t)
        except Refusal:
            continue
        for kt in kits:
            mates = sorted(o["name"] for o in fleet["teams"].values() if o["machine"] == t["machine"]
                           and any(x["main"] == kt["main"] for x in crew.kits_of(o)))
            k = hosts.setdefault(t["machine"], {}).setdefault(kt["main"], {"main": kt["main"], "dir": kt["dir"], "bolts": [],
                **({"slots": {o: f"~/.local/state/{o}-team/slots" for o in mates}} if board else {})})
            if bolt and bolt not in k["bolts"]:
                k["bolts"].append(bolt)
    out = {}
    for host, kits in sorted(hosts.items()):
        have = {} if sites or fetch else {m: k for m, k in READ.kits(host).items() if m in kits}
        ask = [k for m, k in kits.items() if m not in have]
        if ask:
            req = {"kits": ask, "sites": sites, **({"board": True} if board else {}), **({"fetch": True} if fetch else {})}
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


def carried_place(tasks):
    """A place read from a unit's change its bolt holds open, carried there inside another unit's merge, for a unit
    whose own place is gone: its tasks as the bolt holds them, its planning complete (teams.17)."""
    return {"tasks": tasks, "planning": True, "open": [], "head": None}


# The stages at which a unit has finished construct: its change is committed, and a unit after it may be constructed.
CONSTRUCTED = ("planned", "code", "verify", "merged", "landed")


# The stages at which a chore has something committed to build on: its code has delivered its commits (plan.11).
CODED = ("verify", "merged", "landed")


def built_on(kind, stage):
    """Whether a unit or chore it comes after has something committed for the dependent to build on (plan.13): a unit
    its change, once construct has finished; a chore its code, once its commits are in its place."""
    return stage in (CODED if kind == "chore" else CONSTRUCTED)


def after_met(deps):
    """Whether a unit's or chore's After is met, from each one it names as (its kind, its stage): each has something
    committed to build on (built_on), never waiting on a merge (plan.13), whichever kind the dependent is. None while
    one's stage is unknown (read.1)."""
    if any(s == "unknown" for _, s in deps):
        return None
    return all(built_on(k, s) for k, s in deps)


def chore_stage(name, bolt, k, pl):
    """A chore's stage in a bolt its team holds, read from the kit as gathered (k) and its place (pl, None when it has
    none), or None when it has no place and its stage is ready or waiting (state.2, plan.11): landed once main's history
    holds its trailer, merged once the bolt's does; verify once its place holds a commit beyond the bolt, code while it
    holds none; unknown when its place tracks no bolt crew can read. Returns (stage, why)."""
    if name in k.get("chores", []):
        return "landed", None
    if name in k["bolts"].get(bolt, {}).get("chores", []):
        return "merged", None
    if not pl:
        return None, None
    if pl.get("ahead") is None:
        return "unknown", f"chore {name}'s place {pl['path']} tracks no bolt crew can read"
    return ("verify" if pl["ahead"] else "code"), None


class Stages:
    """Each unit's and chore's stage, read from its kit on its team's host. The first rule that holds is a unit's stage:
    landed, merged once its bolt holds its change archived (teams.17), then amended or construct for a unit the plan
    marks amended whose construct has not committed again, then verify, code, planned, construct, then ready or waiting
    by whether its After is met (after_met); a chore's is chore_stage's, then ready or waiting the same way. A unit
    whose change its bolt holds open, carried there inside another unit's merge, is marked carried and reads its stage
    from its place, or with none from the change on the bolt, its merge owed (carried_place). A place at its path that
    tracks another bolt, one it has left, kept from a drop or a move, is not its place: its stage is read as having none,
    and that place is marked left, which the tidy removes and no stage starts over (left_refusal). Work with no bolt is
    queued, and work whose host does not answer, or whose bolt crew can't tell where to read, is unknown, unless main
    holds it landed."""

    def __init__(self, fleet, plan, survey):
        self.fleet, self.plan, self.survey, self.memo = fleet, plan, survey, {}

    def kit(self, b):
        """The bolt's team, host and kit as read, or why they can't be."""
        try:
            t = bolt_team(self.fleet, b)
        except Refusal as e:
            return None, str(e)
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
        u = self.plan.item(name)
        self.memo[name] = res = {"stage": "unknown", "tasks": None, "worktree": None, "open": [], "kind": kind_of(u)}
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
            pl = k.get("chore_places", {}).get(name) if is_chore(u) else k["places"].get(name)
            if pl and pl.get("bolt") and pl["bolt"] != b:  # a place of a bolt it has left is not its place (left_refusal)
                res["left"], pl = pl, None
            res["worktree"], res["head"], res["place"] = (pl["path"], pl.get("head"), pl) if pl else (None, None, None)
            unread = k["bolts"].get(b, {}).get("error")  # a bolt crew can't tell where to read (gather.bolt_read)
            if unread and name not in (k.get("chores", []) if is_chore(u) else k["main"]):
                res["why"] = unread
                return res
            if is_chore(u):
                stage, why = chore_stage(name, b, k, pl)
                if stage:  # unknown only for its place, so a drop or a move is not refused for it (place_unread)
                    res.update(stage=stage, **({"why": why, "place_unread": True} if why else {}))
                    return res
            elif name in k["main"]:
                res["stage"] = "landed"
                return res
            elif name in k["bolts"].get(b, {}).get("archived", []):
                res["stage"] = "merged"
                return res
            elif pl or u.get("Amended") or name in k["bolts"].get(b, {}).get("open", {}):
                if name in k["bolts"].get(b, {}).get("open", {}):
                    res["carried"] = True
                    pl = pl or carried_place(k["bolts"][b]["open"][name])
                if pl:
                    res.update(tasks=pl["tasks"], open=pl["open"])
                res["stage"] = place_stage(pl, u.get("Amended"))
                return res
        met = after_met([(self.of(a)["kind"], self.of(a)["stage"]) for a in u.all("After")])
        res["stage"] = "unknown" if met is None else "ready" if met else "waiting"
        return res

    def bolt_state(self, b):
        """A bolt's state: planned while no team holds it; unknown when its kit can't be read; landed once every unit
        and chore has landed; else unknown when crew can't tell where the bolt is read (gather.bolt_read); waits, to
        land, once every one has merged and sluice is green at its head (teams.16); else active."""
        if not b.get("Team"):
            return "planned"
        k, _ = self.kit(b)
        if not k:
            return "unknown"
        units = self.plan.work_of(b.name())
        stages = [self.of(u.name())["stage"] for u in units]
        if units and all(x == "landed" for x in stages):
            return "landed"
        facts = k["bolts"].get(b.name(), {})
        if facts.get("error"):
            return "unknown"
        if units and all(x in ("merged", "landed") for x in stages) and kit.verification(facts.get("head"), facts.get("verdict"))[0] == "green":
            return "waits"
        return "active"


def stages_for(fleet, plan, bolts, fetch=False):
    """Stages for the units of the given bolts, reading only the hosts that hold them, each kit's GitHub fetched first
    with fetch (survey)."""
    held = [(b.get("Team"), b.name(), b.get("Repo")) for b in bolts if b.get("Team")]
    return Stages(fleet, plan, survey(fleet, held, fetch=fetch))


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


def locate(fleet, kind, name, label, word=None):
    """The one plan holding a bolt, or a record of the Unit set, a unit or a chore (said as word), by name."""
    labels, errors, word = [label] if label else list(fleet["partitions"]), {}, word or kind.lower()
    hits = [h for h in plans(fleet, labels, errors) if h[3] and (h[3].bolt(name) if kind == "Bolt" else h[3].item(name))]
    hits or fail(f"no {word} {name} in the plans of " + ", ".join(labels)
                 + "".join(f"; {k} could not be read: {v}" for k, v in errors.items()))
    len(hits) == 1 or fail(f"{word} {name} is in more than one plan: " + ", ".join(f"{h[0]}/main of {h[1]}" for h in hits) + "; add --label")
    CONTEXT["label"] = hits[0][0]
    return hits[0]


def kit_teams(fleet, kit, label=None):
    return [crew.with_kit(t, kit) for n, t in sorted(fleet["teams"].items()) if crew.builds(t, kit) and label in (None, t["label"])]


def plan_for(fleet, kit, label):
    """The plan a kit's work goes in, (label, state repository): the flywheel of the teams that build it."""
    labels = sorted({t["label"] for t in kit_teams(fleet, kit, label)})
    labels or fail(f"no team" + (f" of {label}" if label else "") + f" builds {kit}, so no plan holds its work")
    len(labels) == 1 or fail(f"{kit}'s work could go in the plan of " + ", ".join(labels) + "; add --label")
    CONTEXT["label"] = labels[0]
    return labels[0], state_of(fleet, labels[0])[0]


def name_free(fleet, label, kit, names):
    """A unit's name is its OpenSpec change's, and a name is taken once in a kit, by a unit or a chore (plan.7, plan.11):
    refused when the kit's main already has that change, open or archived, or holds a chore by it."""
    t = kit_teams(fleet, kit, label)[0]
    sv = survey(fleet, [(t["name"], None)])[t["machine"]]
    sv["ok"] or fail(f"cannot check {kit}'s changes: {t['machine']} did not answer ({sv['error']})")
    k = sv["kits"][t["kit"]["main"]]
    k.get("ok") or fail(f"cannot check {kit}'s changes on {t['machine']}: {k.get('error')}")
    for n in names:
        why = name_taken(kit, n, k["main"], k.get("chores"))
        not why or fail(why)


def name_taken(kit, name, changes, chores):
    """Why a new unit's or chore's name is not free in its kit, or None: not a name crew mints, the name of a change the
    kit's main holds (changes), or of a chore main's history holds (chores, None when the kit was read by a crew that
    reads none, so nothing is refused for it)."""
    if not crew.NAME.match(name):
        return f"a unit's or chore's name is lowercase words with dashes, not {name}"
    if name in changes:
        return f"{kit}'s main already has a change named {name}, open or archived; pick another name"
    if name in (chores or ()):
        return f"{kit}'s main already holds a chore named {name}; pick another name"
    return None


def host_run(fleet, host, script, *args):
    """Run a bash script on a host, with its arguments; refused with its own words when it fails."""
    r = crew.on_machine(fleet, host, ["bash", "-c", script, "crew", *args])
    r.returncode == 0 or fail(f"on {host}: " + ((r.stderr or r.stdout).strip() or f"exit {r.returncode}"))
    return r.stdout.strip()


# Where a bolt's branch lives, for kit.bolt_lives (plan.19), read in a checkout of its kit with $bolt and $file set:
# LOCAL and TRACKED, the commit of the host's own bolt/<bolt> and of origin's tracking ref of it, as this host last
# fetched it, or -; AT_LOCAL and AT_TRACKED, the policy ($file) at each, base64, or - when it holds none, read from the
# commit as sluice reads a branch's policy. Its two reads, ref and pol, are REFS, which LAND_COPIES reads with too.
REFS = r"""ref() { git rev-parse --verify -q "$1^{commit}" || echo -; }
pol() { if [ "$1" != - ] && text=$(git show "$1:$file" 2>/dev/null); then printf '%s\n' "$text" | base64 | tr -d '\n'; else printf -; fi; }
"""
BOLT_AT = REFS + r"""l=$(ref "refs/heads/bolt/$bolt") o=$(ref "refs/remotes/origin/bolt/$bolt")
echo "LOCAL=$l"; echo "TRACKED=$o"; echo "AT_LOCAL=$(pol "$l")"; echo "AT_TRACKED=$(pol "$o")"
"""

# A place: a worktree at a fixed path, on its branch, made on the team's host, its branch tracking its bolt where the
# bolt lives (plan.19, kit.place_base): given no base, PLACE says where the bolt lives (BOLT_AT) and makes nothing;
# given origin/bolt/<bolt>, it fetches the bolt from GitHub first, and says FETCHED with git's words, making nothing,
# when the fetch fails. A new branch is cut from base; a branch already there with no worktree, one a drop kept
# (plan.10, record 0003), is taken as it stands, then tracks base, and the commit it is at is printed as KEPT.
PLACE = r"""main=$1 path=$2 branch=$3 bolt=$4 base=$5 file=$6
cd "$main" || exit 1
if [ ! -d "$path" ]; then
  if [ -z "$base" ]; then
""" + BOLT_AT + r"""    exit 0
  fi
  if [ "$base" = "origin/bolt/$bolt" ] && ! err=$(git fetch -q origin "+refs/heads/bolt/$bolt:refs/remotes/origin/bolt/$bolt" 2>&1); then
    echo "FETCHED=$(printf '%s' "$err" | tr '\n' ' ')"; exit 0
  fi
  if git rev-parse --verify -q "refs/heads/$branch" >/dev/null; then
    git worktree add -q "$path" "$branch" || exit 1
    git branch -q --set-upstream-to="$base" "$branch" || exit 1
    echo "KEPT=$(git rev-parse --short "refs/heads/$branch")"
  else git worktree add -q --track -b "$branch" "$path" "$base" || exit 1; fi
fi
# Where the worktree keeps what crew runs for it, and what its kit declares of its toolchain and tests (kit.py).
echo "GITDIR=$(git -C "$path" rev-parse --absolute-git-dir)"
if [ -f "$path/$file" ]; then echo "DECLARATION=$(base64 < "$path/$file" | tr -d '\n')"; else echo "DECLARATION=-"; fi
"""

# A step of a worktree's readying, run in it with only the variables kit.KEEP names and every LC_* the host has, and
# stdin closed; with an output file, its stdout kept there.
IN_PLACE = r"""path=$1 out=$2 keep=$3; shift 3
cd "$path" || exit 2
env=()
for v in $keep $(compgen -e | grep '^LC_'); do if val=$(printenv "$v"); then env+=("$v=$val"); fi; done
if [ -n "$out" ]; then mkdir -p "$(dirname "$out")" || exit 2; exec env -i "${env[@]}" "$@" </dev/null >"$out"; fi
exec env -i "${env[@]}" "$@" </dev/null
"""


def make_place(fleet, t, path, branch, bolt, unready=False):
    """A worktree at a fixed path on its branch, made with git itself on the team's host, its branch tracking the bolt
    where it lives, origin/bolt/<bolt> after a fetch for a bolt on GitHub (plan.19, PLACE), a new branch cut from it,
    then made ready through its kit's declaration (plan.17), whether it is new or was already there: the declared
    toolchain, its output kept in the worktree's git directory, and the runner's setup inside it. A step that fails
    refuses the command with the worktree made; with unready, as a fix's place is made (teams.3, record 0028), it stops
    the readying instead, and what failed is returned, None once the worktree is ready; with the commit a kept branch
    the new worktree was made on is at (PLACE's KEPT), else None. The command's next step reads the kit again."""
    main, host = t["kit"]["main"], t["machine"]
    said = host_run(fleet, host, PLACE, main, path, branch, bolt, "", kit.DECLARATION)
    if "GITDIR=" not in said:
        said = host_run(fleet, host, PLACE, main, path, branch, bolt, kit.place_base(said, bolt), kit.DECLARATION)
    gitdir, text = kit.place_said(said, bolt)
    kept = next((l[len("KEPT="):] for l in said.splitlines() if l.startswith("KEPT=")), None)
    why = None
    for what, argv, out in kit.readying(kit.declared(text, f"{path}/{kit.DECLARATION}"), f"{gitdir}/crew/toolchain.sh"):
        r = crew.on_machine(fleet, t["machine"], ["bash", "-c", IN_PLACE, "crew", path, out or "", " ".join(kit.KEEP), *argv])
        if r.returncode:
            why = kit.step_failed(path, what, r.returncode, r.stderr + r.stdout)
        elif what == "moon --version" and kit.moon_said(r.stdout):
            why = f"{path} is made but not ready: {kit.moon_said(r.stdout)}"
        if why:
            unready or fail(why)
            break
    READ.drop_kit(t["machine"], t["kit"]["main"])
    return why, kept


# What a kit's main checkout holds of its mains, on its host, for kit.main_now to decide which is main now (plan.18,
# code.7): ORIGIN, whether it has an origin remote, which it then fetches, once for the command, and FETCHED, ok or the
# fetch's error; GITHUB and OWN, the commits origin/main and its own main are at, or -.
MAINS = r"""if git remote get-url origin >/dev/null 2>&1; then
  echo ORIGIN=yes
  if err=$(git fetch -q origin 2>&1); then echo FETCHED=ok; else echo "FETCHED=$(printf '%s' "$err" | tr '\n' ' ')"; fi
else echo ORIGIN=no; fi
echo "GITHUB=$(git rev-parse --verify -q 'refs/remotes/origin/main^{commit}' || echo -)"
echo "OWN=$(git rev-parse --verify -q 'refs/heads/main^{commit}' || echo -)"
"""

# What a kit's main holds of its policy, on its host: its mains (MAINS), and the policy file at each, AT_GITHUB and
# AT_OWN, base64 or - when that main has none, read from main's commit, not the main checkout's files, as sluice reads
# a branch's policy; kit.policy_said takes the one at main now (kit.bolt_checks).
POLICY = r"""main=$1 file=$2
cd "$main" || exit 1
""" + MAINS + r"""at() { if text=$(git show "$1:$file" 2>/dev/null); then printf '%s\n' "$text" | base64 | tr -d '\n'; else printf -; fi; }
echo "AT_GITHUB=$(at refs/remotes/origin/main)"
echo "AT_OWN=$(at refs/heads/main)"
"""

# What a give reads on the team's host before sluice makes the bolt's branch (plan.19): the kit's policy at its main now
# (POLICY), and SLUICE, what the host's `sluice --version` said, on one line, for kit.sluice_refusal.
GIVE_READ = POLICY + r"""echo "SLUICE=$(sluice --version 2>&1 | tr '\n' ' ')"
"""

# A bolt's branch made by sluice from main, where the policy at main keeps it, on GitHub for a kit whose policy names
# origin for its bolts (plan.19), run in the kit's main checkout on the team's host, with no worktree (record 0026):
# sluice's document on standard output and its exit (kit.branch_said). Once sluice made it, which sets the host's own
# branch too, crew marks that branch in the kit's git config, branch.bolt/<bolt>.crew, so the tidy knows it as crew's
# (read.4), and fetches GitHub's copy, origin/bolt/<bolt>, where the bolt is read from then (gather.bolt_read), before
# the give's plan write; a mark git refused, or a fetch that failed, is said on standard error, and the give goes on,
# since the branch is made and the team's next read fetches it again.
BOLT_CREATE = r"""cd "$1" || exit 3
sluice branch create "bolt/$2" --from main --json; rc=$?
if [ "$rc" = 0 ]; then
  git config "branch.bolt/$2.crew" given || echo "git could not mark bolt/$2 as crew's" >&2
  git fetch -q origin "+refs/heads/bolt/$2:refs/remotes/origin/bolt/$2" >&2 \
    || echo "git could not fetch bolt/$2 from GitHub; the team's next read fetches it again" >&2
fi
exit $rc
"""

# What a give reads of a bolt's branch sluice refused to make (plan.19, made_said), in the kit's main checkout on the
# team's host: OWN, the commit of the host's own bolt/<bolt>, or -; then THERE and MAIN, the commits of bolt/<bolt> and
# of main on the bolt's remote, by one ls-remote, each - when the remote lacks it, or READ, git's words on one line,
# when the remote could not be asked (kit.bolt_found).
BOLT_FOUND = r"""cd "$1" || exit 1
bolt=$2 remote=$3
echo "OWN=$(git rev-parse --verify -q "refs/heads/bolt/$bolt^{commit}" || echo -)"
if ! heads=$(git ls-remote "$remote" "refs/heads/bolt/$bolt" refs/heads/main 2>&1); then
  echo "READ=$(printf '%s' "$heads" | tr '\n' ' ')"; exit 0
fi
at() { printf '%s\n' "$heads" | awk -v r="$1" '$2 == r {s = $1} END {print (s != "" ? s : "-")}'; }
echo "THERE=$(at "refs/heads/bolt/$bolt")"; echo "MAIN=$(at refs/heads/main)"
"""

# A bolt's branch deleted by sluice wherever the policy at its tip keeps it (plan.19), once its tip is in main, run in
# the kit's main checkout: where it lives first (BOLT_AT), then RC, sluice's exit, and SAID, its document, base64.
BOLT_DELETE = r"""main=$1 bolt=$2 file=$3
cd "$main" || exit 3
""" + BOLT_AT + r"""out=$(sluice branch delete "bolt/$bolt" --into main --json 2>/dev/null); rc=$?
echo "RC=$rc"; echo "SAID=$(printf '%s' "$out" | base64 | tr -d '\n')"
"""


# What a kit's main checkout holds of its mains, on its host (MAINS), for the commit its main is at now, which a
# landing records (plan.14), and the number of sluice's submission each main's head landed, SUBMISSION_GITHUB and
# SUBMISSION_OWN, its Sluice-Submission trailer, empty for a head sluice did not make.
MAIN = r"""main=$1
cd "$main" || exit 1
""" + MAINS + r"""n() { git log -1 --format='%(trailers:key=Sluice-Submission,valueonly,separator=%x20)' "$1" 2>/dev/null; }
echo "SUBMISSION_GITHUB=$(n refs/remotes/origin/main)"
echo "SUBMISSION_OWN=$(n refs/heads/main)"
"""


def main_held(name, machine, said):
    """The commit a kit's main holds now, from what MAIN read on its host (kit.main_now): (sha, None), or (None, why).
    A host's own main lagging GitHub's refuses nothing: sluice forms every landing on GitHub's main and pushes it with a
    lease (plan.8), and main now is GitHub's for a kit with an origin."""
    _, sha, why = kit.main_now(said, name, machine)
    return sha, why


def tidy_after(fleet, t, what, landed=None, dropped=None):
    """crew _tidy on the team's host, after a plan write that ends work there: the slots of work the plan no longer
    has are freed and the worktrees whose work is over removed, as the team's next read would, saying what it did; and,
    after a landing, the bolt's landing card closed there with the words, where its conductor holds it
    (landing_cards_closed), and the bolt's branch deleted by sluice once the landing's place is gone (land_delete,
    plan.19), landed being (bolt, the outcome recorded, what Pending You is sent in its place or None, whether the user
    answered it in a conversation); after a drop (dropped, the bolt), its branch asked of sluice by the tidy's judgment
    of it (bolt_branch_asked). A host that does not answer leaves that to the team's next read, the delete named with
    its command, and the write stands."""
    bolt, outcome, said, here = landed or (None, None, None, False)
    more = (["--landed", bolt, "--outcome", outcome] + (["--said", said] if said else []) + (["--here"] if here else [])) if landed else []
    r = crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], "_tidy", t["name"], *more))
    READ.drop_kit(t["machine"], t["kit"]["main"])
    said = tidied(t["name"], what, r.returncode, r.stdout, r.stderr)
    if said:
        print(said)
    if landed and r.returncode == 255:  # nothing ran there, the land's delete among it
        print(deleted_said(landed[0], t["machine"], r.returncode, r.stdout, r.stderr))
    if dropped and r.returncode == 255:  # the team's next read asks it, the bolt's branch marked given and in no plan
        print(dropped_said(dropped, t["machine"], r.returncode, r.stdout, r.stderr))


def tidied(team, what, code, out, err):
    """What a plan write that ended work says of the tidy it asked of the team's host: what the tidy said, or, when the
    host did not answer (ssh's 255) or the tidy failed, that the team's next read removes what is over; the write
    stands either way."""
    if code:
        why = "did not answer" if code == 255 else "failed (" + ((err or out).strip().splitlines() or [f"exit {code}"])[-1] + ")"
        return f"{team}'s host {why}, so its worktrees for {what} are not removed yet: the team's next read removes them"
    return (out + err).strip()


# --------------------------------------------------------------------------------------------------- bolts

def held_by(plan, team):
    return [b for b in plan.bolts() if b.get("Team") == team]


def building(team, held, gives):
    """The bolt a team builds (teams.16): of the bolts it holds (held, by name), the one given last, the other waiting to
    land. One held is that one, with no record read; none is None; of two, the one whose newest give is later in gives,
    the bolts given to the team as the run record's gives name them, oldest first (given_to). Refused when the record
    holds a give of neither, rather than guess (read.1)."""
    if len(held) < 2:
        return held[0] if held else None
    last = {b: i for i, b in enumerate(gives)}
    known = [b for b in held if b in last]
    known or fail(f"can't tell which bolt {team} builds: the run record holds no give of {either(held)}")
    return max(known, key=last.get)


def given_to(entries, team):
    """The bolts the run record's gives handed a team, oldest first: each unrefused bolt.give on team/<team>."""
    return [o[len("bolt/"):] for e in entries if e.get("Act") == "bolt.give" and not e.get("Refused")
            and f"team/{team}" in (e.get("On") or []) for o in e["On"] if o.startswith("bolt/")]


def team_building(fleet, plan, t):
    """The bolt a team builds, by name, from its plan (building): the run record read, from the partition's branch
    (read.5), only when it holds two."""
    held = [b.name() for b in held_by(plan, t["name"])]
    gives = given_to(partition_entries(fleet, t["label"]), t["name"]) if len(held) > 1 else []
    return building(t["name"], held, gives)


def waiting_bolt(plan, team, built):
    """The bolt a team holds beside the one it builds (built), which waits to land, or None."""
    return next((b.name() for b in held_by(plan, team) if b.name() != built), None)


def bolt_give(fleet, a):
    """crew bolt give <team> [<bolt>]: bolt/<bolt> made by sluice on GitHub from the kit's main, run on the team's host,
    and no worktree (plan.19, record 0026), then the bolt given to the team in the plan; the conductor and ops start in
    the kit's main checkout. Refused, with the plan unchanged and no branch made, while a bolt the team holds is not
    proven or it holds two (teams.16, give_refusal), or its host is held (teams.19), since a give starts the team's
    agents again: at once for a team that held no bolt, and at their next stop beside a bolt that waits to land
    (team_handed); when the kit's policy at its main now names no checks or no remote for its bolt branches, since a
    bolt merges and lands only through sluice and lives on GitHub (teams.5, give_check); when the host's sluice has no
    `branch create`; and in sluice's words when it makes no branch, but for a branch already on its remote at main's
    tip with no commit of its own, as a give that failed after sluice made it leaves it, which the give takes and goes
    on with (made_said). A plan write refused after sluice made the branch, or the give took it, has sluice delete it
    again (ungiven_said)."""
    t = crew.team_of(fleet, a.team)
    label, kits = t["label"], [k["name"] for k in crew.kits_of(t)]
    CONTEXT["label"] = label
    h = crew.held_on(fleet, t["machine"])
    not h or fail(crew.held_said(t["machine"], h))
    repo, ref = state_of(fleet, label)
    CONTEXT["label"] = label
    tip = fetch(repo, ref)
    tip or fail(f"{repo} has no {ref} yet: crew state init {label}")
    plan = read(repo, ref, tip)
    # The bolts the team holds, oldest first, read once on its host (plan.12): a give waits only for their proof.
    held = held_by(plan, t["name"])
    if len(held) > 1:
        built = team_building(fleet, plan, t)
        held = sorted(held, key=lambda b: b.name() == built)
    if held:
        # Read after a fetch, since a merge sluice landed on GitHub may be what proves the bolt (plan.19).
        why = give_refusal(t["name"], proven_facts(stages_for(fleet, plan, held, fetch=True), plan, held))
        not why or fail(why)
    checked = {b.name() for b in held}
    # The bolt's kit, one of the team's (record 0035), decides the policy read and the branch made; the write gives
    # the same bolt, read again at the tip it replays on.
    named = (plan.bolt(a.bolt) or fail(f"{label}/main has no bolt {a.bolt}")) if a.bolt else None
    chosen = to_give(plan, named, t["name"], kits, label).name()
    t = crew.with_kit(t, plan.bolt(chosen).get("Repo"))
    kit_name, main, host = t["kit"]["name"], t["kit"]["main"], t["machine"]
    text, ref, _, version = kit_policy(fleet, t)
    remote = give_check(kit_name, f"{main}/{kit.DECLARATION}", ref, text, chosen, version, host)
    r = crew.on_machine(fleet, host, ["bash", "-c", BOLT_CREATE, "crew", main, chosen])
    READ.drop_kit(host, main)
    if r.stderr.strip():
        print(r.stderr.strip(), file=sys.stderr)
    found = None
    if r.returncode == 2:
        # sluice refused: a branch a give that did not finish left at main is taken as it stands (made_said).
        try:
            found = kit.bolt_found(host_run(fleet, host, BOLT_FOUND, main, chosen, remote), chosen)
        except Refusal as e:
            found = {"read": str(e)}
    made, adopted = made_said(chosen, kit_name, host, r.stdout, r.returncode, found, remote)
    if adopted and found["own"]:
        m = crew.on_machine(fleet, host, ["git", "-C", main, "config", f"branch.bolt/{chosen}.crew", "given"])
        m.returncode == 0 or print(f"git could not mark bolt/{chosen} as crew's", file=sys.stderr)

    def change(w):
        # The kit's proof was read only for the bolts held then.
        again = [b.name() for b in held_by(w.plan, t["name"])]
        new = [b for b in again if b not in checked]
        not new or fail(f"{t['name']} was given {new[0]} since {tip[:7]}")
        len(again) < 2 or fail(f"{t['name']} holds {again[0]} and {again[1]}")
        b = to_give(w.plan, w.bolt(chosen), t["name"], [kit_name], label)
        b.set("Team", t["name"])
        w.subject = f"plan({b.name()}): give to {t['name']}"
        w.quiet = {t["name"]}  # greeted below once its bolt's branch exists, or at its restart beside a waiting bolt
        seen["bolt"] = b.name()
        return [b.name()]
    seen = {}
    try:
        sha = write(fleet, label, change, "plan: give a bolt")
    except Refusal as e:
        r = crew.on_machine(fleet, host, ["bash", "-c", BOLT_DELETE, "crew", main, chosen, kit.DECLARATION])
        READ.drop_kit(host, main)
        fail(ungiven_said(chosen, str(e), r.stdout, r.returncode))
    b = seen["bolt"]
    print(given_said(t["name"], b, kit_name, remote, made, host, adopted))
    record.emit(label, "bolt.give", [f"bolt/{b}", f"team/{t['name']}"], commit=[f"{repo}@{sha}"], why=f"plan({b}): give to {t['name']}",
                eid=CONTEXT["eid"])
    up = [r for r in ("conductor", "ops") if crew.agent_status(fleet, f"{t['name']}-{r}")]
    if checked:
        # The team still holds a proven bolt, its landing card and any carrying fix the conductor waits on, so neither
        # role is cut off: the team's host tells their panes the bolt they now work for and hands each whose session
        # carries the old branch its restart at its next stop, once idle (teams.16, teams.20), greeted there with both
        # bolts (greet_team).
        print(given_beside(t["name"], b, up, *team_handed(fleet, t)))
        return
    # The team held no bolt, so nothing is in flight: a conductor or ops that is up starts again, with fresh context,
    # and each is greeted here, told the bolt (teams.7).
    if up:
        r = crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], "restart", t["name"], *up, "--no-greet"))
        said = (r.stdout + r.stderr).strip()
        if said:
            print(said)
    if "conductor" not in up:
        print(f"{t['name']}-conductor is not up: crew up {t['name']} starts and greets it", file=sys.stderr)
    greeted(greet_team(fleet, t, crew.greeted_roles("give", up, up), bolt=b))


def give_check(kit_name, where, ref, text, bolt, version, host):
    """What a give checks before sluice makes the bolt's branch, so that any refusal leaves the plan as it was and no
    branch made (plan.19, teams.5, read.1): the kit's policy at its main now (text, read at ref) names checks for the
    bolt's branch and a remote to make it on, and the team's host runs a sluice with `branch create` (version, what its
    `sluice --version` said). The remote, else refused naming the file and what it lacks, or the version needed and
    the host's words."""
    kit.bolt_checks(text, kit_name, where, f"bolt/{bolt}", ref=ref)
    remote = kit.give_remote(text, kit_name, where, f"bolt/{bolt}", ref=ref)
    why = kit.sluice_refusal(version, host)
    not why or fail(why)
    return remote


def made_said(bolt, kit_name, host, out, code, found=None, remote="origin"):
    """The commit a give's bolt/<bolt> stands at, and whether crew took it as it found it rather than sluice made it
    (plan.19), from what BOLT_CREATE printed (out, code; kit.branch_said) and, when sluice refused, what BOLT_FOUND read
    of the branch (found, kit.bolt_found; None when crew read nothing): (the commit sluice made it at, False); or (the
    commit, True) for a branch on its remote at its main's tip with no commit of its own, the host's own copy at that
    commit or none, as a give that failed after sluice made the branch leaves it, so the give run again goes on: such
    a branch is what sluice's create would make now and holds nothing for crew to take over (read.4). Else refused in
    sluice's words, the plan unchanged, naming the branch and where it stands when it is not such a branch."""
    made, why = kit.branch_said(out, code)
    if made:
        return made, False
    said = f"sluice did not make bolt/{bolt} for {kit_name} on {host}: {why}"
    f = found or {}
    not f.get("read") or fail(f"{said}; and crew could not read bolt/{bolt} on {remote}: {f['read']}")
    there, main, own = f.get("there"), f.get("main"), f.get("own")
    if there and there == main and own in (None, there):
        return there, True
    if there and there != main:
        fail(f"{said}; bolt/{bolt} on {remote} is at {there[:7]} and {remote}'s main at {main[:7] if main else 'nothing'}, "
             "so it is no branch a give left empty at main, and crew gives no bolt onto it")
    if there:
        fail(f"{said}; {host}'s own bolt/{bolt} is at {own[:7]}, not at {remote}'s {there[:7]}, and crew gives no bolt "
             "onto it")
    if own:
        fail(f"{said}; {host}'s own bolt/{bolt} is at {own[:7]} and {remote} has none, and crew gives no bolt onto it")
    fail(said)


def given_said(team, bolt, kit_name, remote, made, host, adopted=False):
    """What a give says once the plan gives the bolt (plan.19): where sluice made its branch, on GitHub by the kit's
    remote, from main at the commit it made it at, or that crew took the branch an earlier give left there at main
    (adopted, made_said), and the team's host that builds it."""
    how = (f"crew took bolt/{bolt}, which sluice made on GitHub ({remote}) for a give that did not finish, at "
           f"{kit_name}'s main {made[:7]}" if adopted else
           f"sluice made bolt/{bolt} on GitHub ({remote}) from {kit_name}'s main at {made[:7]}")
    return f"{team} holds {bolt}: {how}, built on {host} and merged into only through sluice"


def ungiven_said(bolt, why, out, code):
    """What a give refused at its plan write says, once crew had sluice delete the bolt's branch it made just before
    (plan.19): the write's refusal, and that the branch is deleted again, or why it stands, in sluice's words, so
    nobody gives the bolt again onto a branch left behind. out and code are what BOLT_DELETE printed and its exit."""
    try:
        code == 0 or fail(f"its delete exited {code}: {(out or '').strip()[-200:] or 'nothing was said'}")
        gone, words = kit.branch_said(*kit.delete_ran(out))
    except Refusal as e:
        gone, words = None, str(e)
    if gone:
        return f"{why}; sluice deleted bolt/{bolt} again, so nothing of the give is left"
    return f"{why}; and bolt/{bolt}, which sluice made for the give, still stands, since sluice did not delete it: {words}"


def deleted_said(bolt, host, code, out, err, held=None):
    """What a land says of sluice's delete of the bolt's branch (plan.19), from what BOLT_DELETE printed on the team's
    host (out, err, its exit code): deleted, from GitHub for a bolt its tip's policy keeps there, else from the host,
    at the commit it was at; gone already, as sluice says when it finds no branch, which refuses nothing; kept where it
    lives, in sluice's words, when sluice refused, as while a submission is queued on it; and, when the host did not
    answer or crew can't read what sluice said, that the branch may still stand. A branch a worktree still holds (held,
    its path) is not asked of sluice, whose delete would leave that worktree on no branch. The bolt has left the plan
    either way."""
    if held:
        return (f"bolt/{bolt} is kept: {held} holds it, so sluice was not asked to delete it: sluice branch delete "
                f"bolt/{bolt} --into main on {host}, once that worktree is gone")
    if code:
        return unasked(bolt, host, code, out, err)
    h = delete_heard(bolt, host, out)
    on, frm = (f" on {h['where']}", f" from {h['where']}") if h["where"] else ("", "")
    if h["rc"] is None:
        return f"bolt/{bolt} may still stand{on}: {h['words']}"
    if h["gone"]:
        return f"sluice deleted bolt/{bolt}{frm} at {h['gone'][:7]}"
    if h["rc"] == 1:
        return f"bolt/{bolt} is gone already: {h['words']}"
    return f"bolt/{bolt} is kept{on}: sluice did not delete it: {h['words']}"


def dropped_said(bolt, host, code, out, err, again=False):
    """What a drop says of sluice's delete of the bolt's branch (plan.19, record 0003), asked by the tidy on the team's
    host once no plan has the bolt and its worktrees are gone, from what BOLT_DELETE printed there (out, err, its exit
    code), read as deleted_said reads it (delete_heard): deleted, from GitHub or, for a bolt made before, from the host;
    gone already, which refuses nothing; kept where it lives, at its tip, in sluice's words when sluice refused, as it
    does while main lacks the tip or a submission is queued on it, named as the drop's unmerged work, the user's; and,
    when the host did not answer, crew can't read what sluice said or sluice failed, the command, which the team's next
    read asks again. Asked again (again), once main holds a kept branch's tip: removed, or still kept in sluice's
    words."""
    if code:
        return unasked(bolt, host, code, out, err) + "; the team's next read asks it"
    h = delete_heard(bolt, host, out)
    on, frm = (f" on {h['where']}", f" from {h['where']}") if h["where"] else ("", "")
    if h["rc"] not in (0, 1, 2):
        return f"bolt/{bolt} may still stand{on}: {h['words']}; the team's next read asks sluice again"
    if h["gone"]:
        return (f"bolt/{bolt} is removed: main now holds bolt {bolt}'s tip, and sluice deleted it{frm} at {h['gone'][:7]}" if again
                else f"sluice deleted bolt/{bolt}{frm} at {h['gone'][:7]}")
    if h["rc"] == 1:
        return f"bolt/{bolt} is gone already: {h['words']}"
    if again:
        return f"bolt/{bolt} is still kept: {h['words']}"
    at = f" at {h['tip']}" if h["tip"] else ""
    return (f"bolt/{bolt} is kept{on}{at}: bolt {bolt} was dropped, and sluice did not delete it: {h['words']}; it is the "
            "drop's unmerged work, the user's to keep or delete, and crew asks sluice again once main holds its tip")


def unasked(bolt, host, code, out, err):
    """That sluice was not asked to delete the bolt's branch, the host not answering (ssh's 255) or the script failing,
    with the command to ask it."""
    why = "did not answer" if code == 255 else "failed (" + ((err or out).strip().splitlines() or [f"exit {code}"])[-1] + ")"
    return f"{host} {why}, so sluice was not asked to delete bolt/{bolt}: sluice branch delete bolt/{bolt} --into main there"


def delete_heard(bolt, host, out):
    """What BOLT_DELETE printed on host of sluice's delete of bolt/<bolt>, read by facts checked against sluice 0.36.4
    (read.2): where the branch lives, GitHub, or the host for one its tip's policy keeps there, None when crew can't
    tell (where); the commit it was at, short, the host's own branch first, or None (tip); the commit sluice deleted it
    at, or None (gone); sluice's exit, None when crew can't read what it said (rc); and sluice's message, or crew's
    refusal to read it (words)."""
    f = kit.said_of(out)
    tip = next((f[k][:7] for k in ("LOCAL", "TRACKED") if f.get(k, "-") != "-"), None)
    try:
        where = "GitHub" if kit.bolt_lives(out, bolt) else host
    except Refusal:
        where = None
    try:
        doc, rc = kit.delete_ran(out)
        gone, words = kit.branch_said(doc, rc)
    except Refusal as e:
        return dict(where=where, tip=tip, gone=None, rc=None, words=str(e))
    return dict(where=where, tip=tip, gone=gone, rc=rc, words=words)


def team_handed(fleet, t):
    """crew _tidy on the team's host after a give beside a bolt the team still holds: its read, its standing panes told
    the bolt they now work for and each due handed its restart at its next stop (team_tidy). (code, what it said)."""
    r = crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], "_tidy", t["name"]))
    READ.drop_kit(t["machine"], t["kit"]["main"])
    return r.returncode, (r.stdout + r.stderr).strip()


def given_beside(team, bolt, up, code, said):
    """What a give to a team that still holds a proven bolt says of its conductor and ops (teams.16): what the team's
    host said, then that each that is up starts again on the new bolt at its next stop, or, when the host did not
    answer or its tidy failed, that they start again on it only at their next start."""
    lines = [said] if said else []
    roles = " and ".join(f"{team}-{r}" for r in up)
    if code:
        why = "did not answer" if code == 255 else "could not hand them their restart"
        lines.append(f"{team}'s host {why}: {roles or 'its conductor and ops'} carry bolt/{bolt} once next started")
    elif up:
        lines.append(f"{roles} start{'s' if len(up) == 1 else ''} again on bolt/{bolt} at {'its' if len(up) == 1 else 'their'} next stop")
    else:
        lines.append(f"{team}-conductor is not up: crew up {team} starts and greets it")
    return "\n".join(lines)


def kit_policy(fleet, t):
    """The team's kit's policy as its main holds it now and what its host's sluice says of its version, read on the
    team's host in one go, origin/main after a fetch for a kit with an origin (GIVE_READ, kit.main_now, plan.18): (the
    policy's text, or None; the ref and the commit it was read at; sluice's words)."""
    said = host_run(fleet, t["machine"], GIVE_READ, t["kit"]["main"], kit.DECLARATION)
    text, ref, sha = kit.policy_said(said, t["kit"]["name"], t["machine"])
    return text, ref, sha, kit.said_of(said).get("SLUICE", "")


def proven_facts(st, plan, bolts):
    """What give_refusal reads of each of the bolts, in the order given, from one read of their kits (st, stages_for):
    (name, work, head, verdict, unread)."""
    out = []
    for b in bolts:
        k, why = st.kit(b)
        facts = k["bolts"].get(b.name(), {}) if k else {}
        work = [(u.name(), kind_of(u), st.of(u.name())["stage"]) for u in plan.work_of(b.name())]
        out.append((b.name(), work, facts.get("head"), facts.get("verdict"), why))
    return out


def give_refusal(team, held):
    """Why a team is given no bolt now, or None (teams.16, record 0020): a team builds one bolt and holds at most one
    more, proven and waiting to land, so a give is refused while it holds two, and while a bolt it holds is not proven:
    its kit could not be read (read.1), it holds no unit or chore yet, one of them has not merged, or sluice's verdict
    at its head is not green (kit.verification). held is each bolt the team holds, oldest first, as (name, work, head,
    verdict, unread): work its units and chores as (name, kind, stage), unread why its kit could not be read or None.
    A fix in flight refuses nothing, since a carrying fix is what the proven bolt keeps of the team; a bolt every unit
    of which has landed passes, only crew bolt land being left of it."""
    if len(held) >= 2:
        return f"{team} holds {held[0][0]} and {held[1][0]}; {held[0][0]} waits to land, and its landing frees {team}"
    for name, work, head, verdict, unread in held:
        if unread:
            return f"can't tell whether bolt {name} is proven: {unread}"
        if not work:
            return f"bolt {name} holds no units or chores yet"
        for n, kind, stage in work:
            if stage not in ("merged", "landed"):
                return f"bolt {name}'s {kind} {n} has not merged ({stage})"
        if all(stage == "landed" for *_, stage in work):
            continue
        state, said = kit.verification(head, verdict)
        if state != "green":
            return f"bolt {name}'s verification is not green: {said}"
    return None


def to_give(plan, b, team, kits, label):
    """The bolt a give hands a team: the one named (b), refused when it is in a kit the team does not hold or another
    team holds it; else the first bolt in the plan's order of any kit the team holds (kits, by name) that no team holds
    (record 0035)."""
    built = " and ".join(kits)
    if b is not None:
        b.get("Repo") in kits or fail(f"bolt {b.name()} is in {b.get('Repo')}, and {team} builds {built}")
        not b.get("Team") or fail(f"bolt {b.name()} is held by {b.get('Team')}")
        return b
    free = [x for x in plan.bolts() if x.get("Repo") in kits and not x.get("Team")]
    return free[0] if free else fail(f"{label}/main has no planned bolt in {built} for {team}")


def land_refusal(bolt, units, stage_of, outside, label):
    """Why a bolt does not land, or None (plan.16): a unit or chore (units, by name) crew cannot read, or one that has
    not landed on main, or units whose latest change no batch has held yet (outside); a chore is in no batch."""
    for u in units:
        s = stage_of(u)
        k = s.get("kind", "unit")
        if s["stage"] == "unknown":
            return f"cannot tell whether {k} {u} has landed: {s.get('why')}"
        if s["stage"] != "landed":
            return f"{k} {u} has not landed on main: it is {s['stage']}"
    if outside:
        return (f"bolt {bolt} lands only once every unit's latest change has been in a batch, and {either(outside)} "
                + ("has" if len(outside) == 1 else "have") + f" not: a batch is due for them (crew review {label})")
    return None


def builder(fleet, label, kit):
    """The team of the partition building a kit, the first by name, on whose host and main checkout a bolt no team
    holds is read and landed; None when no team of the partition builds it."""
    return next((crew.with_kit(fleet["teams"][t], kit) for t in sorted(crew.partition_of(fleet, label)["teams"]) if crew.builds(fleet["teams"][t], kit)), None)


def partition_kits(fleet, label):
    """The names of the kits the partition's teams build, from the teams file alone (code.5), sorted."""
    return sorted({k["name"] for t in crew.partition_of(fleet, label)["teams"] for k in crew.kits_of(fleet["teams"][t])})


def land_key(key, kits):
    """What a land/ card key names (rail-cards, record 0031 as amended 2026-10-23), from the names of the kits the
    partition's teams build (kits): ("kit", <kit>) for land/<kit>, the kit's landings card, main-level ops's; ("bolt",
    <bolt>) for any other land/<x>, a bolt's reading and preview on its team's host, and an old landing card of the
    bolt's own, land/<bolt> or land/<bolt>/<head> as a conductor posted one before; None for a key that is no
    landing's."""
    m = re.fullmatch(r"land/([a-z0-9][a-z0-9-]*)(/[0-9a-f]{7})?", key or "")
    if not m:
        return None
    return ("kit", m.group(1)) if m.group(1) in kits and not m.group(2) else ("bolt", m.group(1))


def kit_named(bolt, kits, label):
    """Why a bolt may not be added under its name, or None (rail-cards "A bolt's own landing card gives way to its
    kit's"): it is the name of a kit the partition's teams build (kits), whose landings card is land/<kit>, so land/
    <bolt> would name the kit's card and not the bolt."""
    if bolt in kits:
        return (f"a bolt of {label} may not be named {bolt}: that is the name of a kit {label}'s teams build, whose "
                f"landings card is land/{bolt}")
    return None


def unheld_stages(k, why, other, chores=()):
    """Each unit's and chore's stage for the landing of a bolt no team holds: landed when main holds it on its kit as
    read there (k), a unit's change open or archived and a chore's trailer (chores, the bolt's chores' names), unknown
    with why when the kit could not be read, else its stage in the plan (other(name))."""
    def of(name):
        kind = "chore" if name in chores else "unit"
        if k is None:
            return {"stage": "unknown", "why": why, "kind": kind}
        return {"stage": "landed", "kind": kind} if name in (k.get("chores", []) if kind == "chore" else k["main"]) else dict(other(name), kind=kind)
    return of


def unheld_refusal(bolt, units, kit, t, label):
    """Why a bolt no team holds can't land, or None: it holds units or chores, since a bolt with none has nothing on
    main, and a team of the partition builds its kit, whose main checkout is read."""
    if not units:
        return f"bolt {bolt} is held by no team and holds no units or chores, so nothing of it has landed"
    if t is None:
        return f"bolt {bolt} is held by no team, and no team of {label} builds {kit}, so crew can't read its main"
    return None


def landed_line(bolt, kit_name, head, team, still):
    """What crew bolt land says of a bolt its team held (teams.16): where it landed, and the bolt the team still builds
    (still, the bolts it holds once the landing is written), or that it holds none; when the plan could not be read
    after the write (still None), only where it landed."""
    said = f"{bolt} has landed at {kit_name}'s {head[:7]}"
    if still is None:
        return f"{said}; {team}'s plan could not be read again to say what it holds"
    return f"{said}; {team} builds {still[0]}" if still else f"{said} and {team} holds no bolt"


def landed_words(head, submission):
    """What a bolt's landing card closes with at crew bolt land (plan.16, record 0032 §3): where GitHub's main holds the
    landing, with sluice's submission number when its head carries one, and that every host's folder follows by the
    fleet's timer, since nothing waits on a host."""
    n = f" (#{submission.strip()})" if re.fullmatch(r"\d+", (submission or "").strip()) else ""
    return f"landed on GitHub's main at {head[:7]}{n}; every host's folder follows by swancloud's timer within minutes"


def pane_word_of(entries, bolt):
    """The user's word to land the bolt given in a pane (plan.16, crew bolt submit --excerpt), from the run record's
    entries, oldest first: (who submitted it, when, the transcript record its words were read from, the host it ran
    on) for the last bolt.submit on bolt/<bolt> not refused, when it names a session's record (From session/<sid>/
    <record>); None for a landing on the card's approval, or when no submission of the bolt landed."""
    done = [e for e in entries if e.get("Act") == "bolt.submit" and not e.get("Refused") and f"bolt/{bolt}" in (e.get("On") or [])]
    frm = [f for f in (done[-1].get("From") or []) if f.startswith("session/")] if done else []
    return (done[-1].get("By"), done[-1].get("At"), frm[0], done[-1].get("Host")) if frm else None


def pane_landed(landed, by, at, words):
    """What a landing on the user's word in by's pane closes its card with (plan.16), landed the landed_words: (the
    outcome the run record keeps, naming the pane and none of the words, record.3; what Pending You is sent, the word
    and the user's words first, since the close is cut to Pending You's length from its end, or, with no words read
    back, the time the word was given, at, as HH:MMZ)."""
    pane = f"Landed on the user's word in {by}'s pane"
    said = f'{pane}, "{words}"; {landed}' if words else f"{pane} at {(at or '')[11:16]}Z; {landed}"
    return f"{pane}; {landed}", said


def landing_card_keys(entries, bolt, owner):
    """The keys under which the bolt's conductor (owner) holds an open landing card, from its host's run record:
    land/<bolt>, as crew raises it (record 0031), and land/<bolt>/<head>, as a conductor posted one before."""
    keys = sorted({e.get("Key") for e in entries if e.get("Act") == "card.post" and e.get("By") == owner
                   and re.fullmatch(rf"land/{re.escape(bolt)}(/[0-9a-f]{{7}})?", e.get("Key") or "")})
    return [k for k in keys if cards.card_under(entries, k, owner)]


def landing_act(event, head=None, words=None):
    """Which act a bolt's landing card takes at its event (record 0031 §1, plan.16), from facts alone: ("change", note)
    once the bolt reads proven, at the merge's end or the rail's read, which row_card_change posts when no card is held,
    changes in place, its head moved, while the user has not answered it, and once they have leaves as it is, or
    follows with a new card when the head moved since their answer;
    ("close", None, reason) when a fix starts on the bolt, withdrawn as held for the fix, in its words; ("close",
    outcome, None) when it lands, the outcome landed_words'."""
    if event == "proven":
        return ("change", f"Its head is now {head[:7]}")
    if event == "fix":
        return ("close", None, f"held for a fix: {words}")
    if event == "preview":
        return ("change", words)
    return ("close", words, None)


# A preview of a bolt's head as sluice lists it (sluice record 0021, read in sluice 0.29.3): its states, the first while
# it waits for room on the host.
PREVIEW_STATES = ("waiting", "starting", "up", "failed")


def preview_step(declared, recorded, head, listed, alive):
    """What crew does with the bolt's preview as its landing card is raised (rail-cards, record 0031 §3), from facts
    alone: declared, whether the kit's policy at the head declares [preview] (kit.previewed); recorded, the head crew's
    record of its ask names, or None when none stands; listed, whether sluice lists the recorded preview; alive, whether
    the process crew handed the ask to still runs. "none" with nothing declared or recorded; "release" when one is
    recorded and the head's policy declares none; "replace" when the recorded one is another head's, released before
    one is asked at this; "keep" when it is this head's and listed or still being asked, read again and nothing asked;
    "ask" otherwise, sluice's one preview of a revision the second guard against asking twice."""
    if recorded is None:
        return "ask" if declared else "none"
    if not declared:
        return "release"
    if recorded != head:
        return "replace"
    return "keep" if listed or alive else "ask"


def preview_change(shown, outcome, head):
    """The change note a preview's end puts on its landing card while it waits on the user, or None (rail-cards "A
    preview that fails is said on the card"): shown, what the card was raised with, "addresses" or "reason"; outcome,
    how sluice's preview of head ended, "up" or "failed", a refusal among the failures. Addresses shown and the preview
    failed: the card says it did not come up; a reason shown and the preview up: the card lists its addresses; anything
    else changes nothing the card says."""
    if shown == "addresses" and outcome != "up":
        return f"Its preview of {head[:7]} did not come up"
    if shown == "reason" and outcome == "up":
        return f"Its preview of {head[:7]} is up"
    return None


def preview_listed(doc, branch, head):
    """The preview of head on branch as `sluice previews --json` lists it (doc), its fields checked as sluice 0.29.3
    gives them (read.2): {head, name, addresses, state}, with sluice's output when it failed; None when none is listed.
    Refused when the document is no list of objects, or the entry's fields are not sluice's."""
    isinstance(doc, list) or fail(f"sluice's previews are no list crew reads: {cut(json.dumps(doc), 200)}")
    for e in doc:
        isinstance(e, dict) or fail(f"sluice lists a preview crew can't read: {cut(json.dumps(e), 200)}")
        rev = e.get("revision")
        if not (e.get("branch") == branch and isinstance(rev, str) and len(rev) >= 7 and (head.startswith(rev) or rev.startswith(head))):
            continue
        name, addresses, state = e.get("name"), e.get("addresses"), e.get("state")
        (isinstance(name, str) and name.startswith("preview/") and isinstance(addresses, dict)
         and all(isinstance(k, str) and k and isinstance(v, str) and v for k, v in addresses.items())
         and state in PREVIEW_STATES) or fail(f"sluice lists a preview of {branch} at {head[:7]} crew can't read: {cut(json.dumps(e), 200)}")
        out = dict(head=head, name=name, addresses=dict(addresses), state=state)
        if state == "failed":
            out["output"] = e["output"] if isinstance(e.get("output"), str) else ""
        return out
    return None


def fixes_in_flight(fixes, bolt):
    """The fixes of the bolt in flight, by name, from the fixes a kit read found (gather.kit): each whose place stands,
    that has not merged into the bolt and that its conductor did not drop (record 0028); a fix in flight holds the
    bolt's landing (landing_unready)."""
    return sorted(f["fix"] for f in fixes if f.get("bolt") == bolt and not f.get("merged") and not f.get("dropped"))


def landing_unready(work, head, verdict, fixes):
    """Why a bolt does not yet read proven, from its kit alone (record 0031 §1, record 0025), or None: work is each of
    its units and chores as (name, kind, stage); head and verdict, its branch's head and sluice's Sluice-Result there;
    fixes, the fixes of the bolt in flight. It reads proven once every unit and chore has merged, not every one has
    landed, sluice's verdict at its head is green, and no fix is in flight on it, since a fix started on the bolt holds
    its landing until the fix merges or is dropped."""
    if not work:
        return "it holds no units or chores"
    for name, kind, stage in work:
        if stage not in ("merged", "landed"):
            return f"{kind} {name} has not merged: it is {stage}"
    if all(stage == "landed" for *_, stage in work):
        return "every unit and chore of it has landed"
    state, said = kit.verification(head, verdict)
    if state != "green":
        return f"its verification is not green: {said}"
    return f"{either(sorted(fixes))} is in flight on it" if fixes else None


def landing_facts(bolt, kit_name, work, head, at, due, unanswered, read_in, moved, pr, frees=None):
    """The landing card's facts as cards.landing_card takes them, once the bolt reads proven by its kit (landing_unready):
    the bolt, its kit, its units and chores, the batch each unit was last read in (read_in), its head and when sluice
    landed it there (at), how many landings main has had since the bolt last met it (moved), sluice's pull request
    at the head (pr) or None, and, when its team holds another bolt that is proven too, what a yes frees it for (frees,
    {team, next}, yes_frees) or None. None while a unit's latest change waits for a batch (due), or has been in one whose
    card the user has not answered (unanswered, awaiting_answer), since a bolt lands only once each has been in a batch
    the user has answered (briefs.12); a chore is in no batch."""
    units = [n for n, kind, _ in work if kind == "unit"]
    if any(u in due or u in unanswered for u in units):
        return None
    return dict(bolt=bolt, kit=kit_name, units=units, chores=[n for n, kind, _ in work if kind == "chore"],
                batches={u: read_in[u] for u in units if u in read_in}, head=head, at=at, moved=moved, pr=pr, frees=frees)


def pull_of(sluice_from, repo):
    """sluice's pull request for the submission at a head, from its Sluice-From trailer, `<agent> (pull/<n>)` when the
    submission went through one: {number, url} on the kit's GitHub, or None for a submission from a branch."""
    m = re.search(r"\(pull/(\d+)\)\s*$", sluice_from or "")
    return dict(number=int(m.group(1)), url=f"https://github.com/{repo}/pull/{m.group(1)}") if m else None


def last_submits(entries):
    """Each bolt's last bolt.submit entry, from the run record's entries, oldest first: {bolt: entry}."""
    last = {}
    for e in entries:
        if e.get("Act") != "bolt.submit":
            continue
        for o in e.get("On") or []:
            if o.startswith("bolt/"):
                last[o[5:]] = e
    return last


def refusals(entries):
    """Each bolt whose last landing sluice refused for the bolt's own content (landing_end), from the run record's
    entries, oldest first: {bolt: (head, words)}, the head that was submitted (its bolt.submit's Head) and the words it
    was refused with, sluice's verdict when it gave one (landing_said, recorded), from each bolt's last bolt.submit
    entry when it was refused; a bolt whose last one landed or was stopped, or that has none, is not in it."""
    return {b: (e.get("Head") or "", e["Refused"]) for b, e in last_submits(entries).items() if e.get("Refused")}


def stops(entries):
    """Each bolt whose last landing sluice or its host stopped, nothing of the bolt's (rail-cards "A landing sluice or
    its host stopped keeps its box", landing_end), from the run record's entries, oldest first: {bolt: (head, words)},
    the head that was submitted and the words for what stopped it, from each bolt's last bolt.submit entry when it is
    marked Outcome stopped and names its Head; a bolt whose last one landed or was refused, or that has none, is not in
    it, nor one whose stop names no head, which nothing of the bolt was submitted at."""
    return {b: (e["Head"], e.get("Why") or "") for b, e in last_submits(entries).items()
            if e.get("Outcome") == "stopped" and e.get("Head") and not e.get("Refused")}


def stopped_at(stopped, bolt, head):
    """What stopped the bolt's last landing, in the words it was recorded with, when it was stopped at head, from the
    stops already read ({bolt: (head, words)}, stops), or None: one stopped at another head says nothing, the bolt's
    head having moved since, as a refusal at another head holds nothing (held_at)."""
    return held_at(stopped, bolt, head)


def refused_at(entries, bolt, head):
    """sluice's refusal of the bolt's landing at head, in the words it was recorded with, or None (rail-cards "A
    refused landing is held on its row"): its last bolt.submit was refused with head submitted; one refused at another
    head, the bolt's head moved since by its team's fix, holds nothing."""
    return held_at(refusals(entries), bolt, head)


def held_at(refused, bolt, head):
    """refused_at from the refusals already read ({bolt: (head, words)}, refusals)."""
    at, words = refused.get(bolt, (None, None))
    return words if at and head and (at.startswith(head) or head.startswith(at)) else None


def send_stands(sent, head, work):
    """Whether the user's send on a kit's landings card still stands for a bolt they ticked at sent, now at head
    (rail-cards "A ticked bolt's approval stands while its own work is unchanged", record 0031 as amended 2026-10-24):
    the heads one by prefix, or the bolt's own work, its non-merge commits main lacks, read between them (work,
    bolt_work's {head, gained, lost, why}) with nothing gained and nothing lost. Work not read, or read with why, holds
    no send at another head (read.1). A decision of facts alone (code.7)."""
    if sent and head and (head.startswith(sent) or sent.startswith(head)):
        return True
    return bool(work) and not work.get("why") and not work.get("gained") and not work.get("lost")


SAID_COMMITS = 5  # the subjects a bolt asked again names of each list, before how many more


def work_said(bolt, sent, head, work):
    """The words for a bolt the user ticked at sent and asked for again at head, whose send does not stand
    (send_stands, rail-cards "A ticked bolt whose own work changed is asked again, saying what changed"): its head now,
    then the subjects of its own commits it gained since the send and those it no longer holds, SAID_COMMITS of each
    at most and how many more; or why crew could not tell, in git's words (read.1)."""
    work, now = work or {"why": "crew read none of its work"}, f"{bolt}'s head is now {head[:7]}" if head else None

    def listed(commits):
        more = len(commits) - SAID_COMMITS
        return "; ".join([s for _, s in commits[:SAID_COMMITS]] + ([f"and {more} more"] if more > 0 else []))
    if work.get("why"):
        return ", but ".join(([now] if now else []) + [
            f"crew could not tell whether {bolt}'s own work changed since your send at {sent[:7]}: {work['why']}"])
    gained, lost = list(work.get("gained") or []), list(work.get("lost") or [])
    said = [now or f"{bolt}'s head has moved"]
    if gained:
        said.append(f"with work of its own since your send at {sent[:7]}: {listed(gained)}")
    if lost:
        said.append(f"and no longer holding: {listed(lost)}" if gained else
                    f"no longer holding work of its own your send at {sent[:7]} held: {listed(lost)}")
    return ", ".join(said)


# The words a take-main fix starts with (bolt_forecast's, and main-level ops's for a landing that conflicts): a fix in
# flight with them holds its bolt's row as taking main first (rail-cards "A take-main fix holds its row as taking main
# first").
TAKE_MAIN = "Take main into the bolt"


def landing_rows(order, rows, held, stopped=None, takes_main=None, left=()):
    """The rows of a kit's landings card (rail-cards, record 0031 as amended 2026-10-23), from facts alone: order, the
    plan's bolts of the kit by name, in its order; rows, {bolt: facts} for each that reads proven as a fix in flight on
    it leaves it (land_row), its facts carrying its head and its fixes in flight, {fix: the words it started with or
    None}; held, each bolt's last landing sluice refused for its own content, {bolt: (head, words)} (refusals);
    stopped, each bolt's last landing sluice or its host stopped, nothing of the bolt's, the same (stops); takes_main,
    each bolt forecast to conflict with what main holds at its present head, {bolt: (main's short sha, [paths])}, by
    the card's forecast or the run record's (main_conflict). In the plan's order, each {bolt, box: True, facts}, a row
    the user ticks, its facts carrying stopped, (head, words), when its last landing was stopped at its present head
    (stopped_at), which holds nothing (rail-cards "A landing sluice or its host stopped keeps its box"); or {bolt, box:
    False, why, facts}, held with no box: for a fix in flight on it, in the fix's words, or for sluice's refusal of its
    landing at its present head, until its team's fix moves the head; or, marked takes_main, taking main first,
    forecast to conflict with main, or with only take-main fixes in flight (TAKE_MAIN), each named with its words; but a
    bolt the user left (left, left_now) marked takes_main keeps its box, its facts marked would_main, (main's short
    sha, [paths]), for its row to say it would take main first once ticked (rail-cards "A row the user left says
    whether it would take main first"). A bolt not in rows is no row."""
    out, stopped, takes_main = [], stopped or {}, takes_main or {}
    for b in [b for b in order if b in rows]:
        f = rows[b]
        fixes = f.get("fixes") or {}
        at, words = held.get(b, (None, None))
        main_first = bool(fixes) and all((note or "").startswith(TAKE_MAIN) for note in fixes.values())
        if fixes:
            why = "; ".join(f'takes main first: {fix.rsplit("/", 1)[-1]} taking main in: "{note}"' if (note or "").startswith(TAKE_MAIN)
                            else f"held for a fix: {note} ({fix})" if note else f"held for {fix} until it merges or is dropped"
                            for fix, note in sorted(fixes.items()))
        elif at and (at.startswith(f["head"]) or f["head"].startswith(at)):
            why = f"held: sluice refused its landing at {f['head'][:7]}, and it waits for its team's fix: {words}"
        elif b in takes_main and b not in left:
            main, paths = takes_main[b]
            why, main_first = (f"takes main first: forecast to conflict with main on {joined(list(paths))} at {main[:7]}; "
                               f"{f.get('conductor') or 'its team'} takes main in by a fix"), True
        else:
            stop = stopped_at(stopped, b, f["head"])
            marks = dict(**({"stopped": (stopped[b][0], stop)} if stop else {}),
                         **({"would_main": (takes_main[b][0][:7], list(takes_main[b][1]))} if b in takes_main else {}))
            out.append(dict(bolt=b, box=True, facts=dict(f, **marks) if marks else f))
            continue
        out.append(dict(bolt=b, box=False, why=why, facts=f, **({"takes_main": True} if main_first else {})))
    return out


def card_heads(text):
    """A kit's landings card's rows as its post or change recorded them (built_fields): [(bolt, head, left)] in the
    card's order, left whether the user cleared it on their last send; [] for none recorded."""
    out = []
    for w in (text or "").split():
        m = re.fullmatch(r"([a-z0-9][a-z0-9-]*)@([0-9a-f]{7,40})(:left)?", w)
        if m:
            out.append((m.group(1), m.group(2), bool(m.group(3))))
    return out


def at_head(head, now):
    """Whether a head recorded short or whole (head) is the bolt's head now (now), either a prefix of the other."""
    return bool(head and now) and (now.startswith(head) or head.startswith(now))


def left_marks(entries, key):
    """What the run record holds of the bolts the user left on a kit's landings card (rail-cards "A bolt the user left
    stays left until they tick it"), from the entries, oldest first: the last set a raise of the card under key recorded
    (a landing.left not refused with that Key, its Heads <bolt>@<head7> each), {bolt: head7}, and each stop main-level
    ops recorded after it on the user's words in its pane (bolt.leave, its Head), [(bolt, head)]; less any bolt landed
    on the user's words in ops's pane since (a bolt.submit not refused naming the transcript record they were read
    from). The bolts of every kit are among the stops, which the kit's heads sort out (left_now, left_of)."""
    recorded, stops = {}, []
    for e in entries:
        act = e.get("Act")
        if e.get("Refused") or act not in ("landing.left", "bolt.leave", "bolt.submit"):
            continue
        bolt = next((o[5:] for o in e.get("On") or [] if o.startswith("bolt/")), None)
        if act == "landing.left" and e.get("Key") == key:
            recorded, stops = {b: h for b, h, _ in card_heads(e.get("Heads"))}, []
        elif act == "bolt.leave" and bolt and e.get("Head"):
            stops.append((bolt, e["Head"]))
        elif act == "bolt.submit" and bolt and e.get("From"):
            recorded.pop(bolt, None)
            stops = [(b, h) for b, h in stops if b != bolt]
    return recorded, stops


def left_now(card, ticked, heads, recorded, stops):
    """The bolts of a kit's landings card the user left, at a raise of it (rail-cards "A bolt the user left stays left
    until they tick it", "A bolt stopped in ops's pane is shown as left"), from facts alone (code.7): card, the card ops
    holds as kit_card_state reads it, {status, heads}, or None; ticked, the bolts the user ticked on it once answered;
    heads, {bolt: its head now} of each row of the kit read now; recorded and stops, as left_marks gives them. A bolt at
    its head now is left when it is marked left on the card held while it waits, the card held is answered and the user
    did not tick its row, or the record names it left or stopped and the card held has not ticked it; one the user
    ticked, one at another head and one that is no row are not. {bolt: head7}."""
    status = (card or {}).get("status")
    ticks = set(ticked or []) if status == "answered" else set()
    out = {}
    for b, h, marked in (card or {}).get("heads") or []:
        if at_head(h, heads.get(b)) and (marked if status == "waiting" else status == "answered" and b not in ticks):
            out[b] = heads[b][:7]
    for b, h in list(recorded.items()) + list(stops):
        if b not in ticks and at_head(h, heads.get(b)):
            out.setdefault(b, heads[b][:7])
    return out


def left_of(entries, key, heads):
    """The bolts of a kit's landings card the user left, as the run record holds them (left_marks): the last set its
    raise recorded and each stop recorded since, kept only at the bolt's head now (heads, {bolt: head}); a tick on a
    send, read by the raise that recorded the set, a moved head or a landing on the user's words ending one. Which a
    conductor's wait and the rail read, neither seeing the card. {bolt: head7}."""
    recorded, stops = left_marks(entries, key)
    return {b: heads[b][:7] for b, h in list(recorded.items()) + stops if at_head(h, heads.get(b))}


def landings_sent(entries, key, owner):
    """The bolts the user's send on a kit's landings card still landed when a new card followed it (landings_step's
    follow), from the run record's entries, oldest first: {bolt: the head they ticked}, from the Heads of each close of
    a card under key in owner's name that carries them, the last for each bolt; {} for none."""
    out = {}
    for e in entries:
        if e.get("Act") == "card.close" and not e.get("Refused") and e.get("Key") == key and e.get("By") == owner:
            out.update({b: h for b, h, _ in card_heads(e.get("Heads"))})
    return out


def rows_unsent(rows, sent, work=None):
    """A kit's landings card's rows (landing_rows) less each that can land on an earlier send that still stands for it
    (landings_sent, send_stands), at the head sent or at a head whose own work is the same (work, bolt_work's for each
    bolt whose head moved), which is no row of a card that follows that send's, nor of any after it; those bolts; and
    each that can land whose send does not stand, a row again, with the words that say what changed (work_said):
    (rows, [bolt], [(bolt, words)]). A decision of facts alone (code.7)."""
    work, out, landing, asked = work or {}, [], [], []
    for r in rows:
        b, head = r["bolt"], r["facts"]["head"]
        at = sent.get(b)
        if r["box"] and at and send_stands(at, head, work.get(b)):
            landing.append(b)
            continue
        out.append(r)
        if r["box"] and at:
            asked.append((b, work_said(b, at, head, work.get(b))))
    return out, landing, asked


def sent_left(sent, now, in_plan, refused, work=None):
    """The bolts an earlier send on a kit's landings card still lands (landings_sent's sent, {bolt: the head they
    ticked}), in the order sent, which crew card read land/<kit> prints with or without a card open, so the send is read
    though its card closed before ops read it: each the plan still holds (in_plan) whose head now is read (now, {bolt:
    its head or None}), whose send stands there (send_stands, work bolt_work's between the two), and that sluice did not
    refuse at its head now (refused, refusals), a refusal at the head sent holding nothing once its team's fix moved it;
    and beside them each it can't tell of, its head now unread or its work not compared, with why (read.1): (bolts,
    [(bolt, why)]). A decision of facts alone (code.7)."""
    work, out, unknown = work or {}, [], []
    for b, h in sent.items():
        if b not in in_plan:
            continue
        w = work.get(b) or {}
        if not now.get(b):
            unknown.append((b, w.get("why") or f"crew read no head of bolt/{b}"))
        elif send_stands(h, now[b], work.get(b)):
            if not held_at(refused, b, now[b]):
                out.append(b)
        elif w.get("why"):
            unknown.append((b, w["why"]))
    return out, unknown


def ticked_of(got, heads):
    """The bolts the user ticked on a kit's landings card, in the card's order (heads, card_heads), from get_request's
    answer on their turn: the one row of an approval they approved, none of one they declined; each box of a list,
    land:<bolt>, from its choiceIds, or each question's of lists. None while they have not answered."""
    answer = got.get("answer") if isinstance(got, dict) and got.get("status") == "answered" else None
    if not isinstance(answer, dict):
        return None
    if isinstance(answer.get("approved"), bool):
        return [heads[0][0]] if answer["approved"] and heads else []
    picked = [c for c in answer.get("choiceIds") or [] if isinstance(c, str)]
    for a in (answer.get("answers") or {}).values() if isinstance(answer.get("answers"), dict) else []:
        picked += [c for c in (a.get("choiceIds") or [] if isinstance(a, dict) else []) if isinstance(c, str)]
    return [b for b, _, _ in heads if f"land:{b}" in picked]


def landings_step(rows, card, ticked, in_plan, landed=None, note=None, here=False, work=None):
    """What the raise of a kit's landings card does with it (rail-cards, record 0031 as amended 2026-10-23), from facts
    alone (code.7): rows, its rows as landing_rows gives them; card, None when ops holds none, else {status, heads},
    status "waiting" or "answered" and heads its rows as its last post or change recorded them (card_heads); ticked,
    the bolts the user ticked on it once answered (ticked_of); in_plan, the kit's bolts the plan still holds; landed,
    {bolt: the commit GitHub's main holds} for each that landed (the bolt.land entries); note, the event's own change
    note; here, that the event is a landing on the user's word in ops's pane (pane_landed), a word that answers the
    card; work, each ticked bolt's own work between the head the card showed and its head now, for those whose head
    moved (bolt_work), by which the user's send still stands for a bolt that only took main in (send_stands, record
    0031 as amended 2026-10-24). Each act with the bolts the user cleared on their last send (left), which its card
    shows unticked:
    ("none",) when no row can land and no card is held;
    ("withdraw", why) when no row can land and a waiting card is held, each row held or none proven; ("answered", why)
    then for a landing on the user's word in ops's pane (here), closed as answered there;
    ("post", left) when rows can land and no card is held, following the kit's last card only when that one was
    answered and closed with rows left (cards.follows_of);
    ("change", note, kind_changed, left) when a waiting card is held and its rows, their heads or the event changed
    it, its form changed or not (cards.landings_form), followed then rather than changed; ("leave",) when nothing did;
    ("leave",) when an answered card is held while any bolt the user ticked is still to land on their send, in the
    plan, not held, or held only taking main first (landing_rows' takes_main), and its send standing at its head now,
    which stands while it takes main in, one landed and not yet closed among them, and no row reads proven since but at
    a head their send still stands at;
    ("follow", outcome, left, landing) when one does, a bolt on no row of the card or at a head the card did not show
    whose send does not stand, which is never added to the card they answered: it is closed saying what landed, what
    their send still lands, each whose last landing at its head sluice or its host stopped with what stopped it (its
    row's stopped, landing_rows), which holds nothing, what takes main in first, what was held and what was left, and
    what changed of a ticked bolt asked again (work_said), and a new card follows it with every row that can land but
    those their send still lands (landing, each (bolt, the head they ticked), a held one whose send stands among them);
    ("close", outcome, then, standing) once none is still to land, the outcome saying what landed and where GitHub's
    main holds it, what was held and why, what was left and what reads proven since, then the bolts left when rows can
    land, for a new card that follows it, else None, then each ticked bolt held whose send still stands, (bolt, the
    head they ticked), which the close keeps, saying so, for it to land on that send once its team's fix has only
    taken main in; a send ticking none closes it at once, landing nothing. A bolt left on the last send is shown
    unticked on the card that follows only while its head stands."""
    boxed = [r for r in rows if r["box"]]
    now = [(r["bolt"], r["facts"]["head"][:7]) for r in boxed]
    held = {r["bolt"]: r["why"] for r in rows if not r["box"]}
    if card is None:
        return ("post", []) if boxed else ("none",)
    heads = card.get("heads") or []
    if card["status"] != "answered":
        if not boxed:
            return ("answered" if here else "withdraw", "every bolt waiting to land is held: "
                    + "; ".join(f"{b}, {w}" for b, w in held.items()) if held else "no bolt waits to land on its main")
        was = {b: (h, left) for b, h, left in heads}
        left = [b for b, h in now if b in was and was[b][1] and was[b][0] == h]
        said = [f"{b} reads proven and joins the card" for b, _ in now if b not in was]
        said += [f"{b}'s head is now {h}" for b, h in now if b in was and was[b][0] != h]
        said += [(f"{b} {held[b]}" if held[b].startswith("takes main first") else f"{b} is {held[b]}") if b in held
                 else f"{b} no longer waits to land" for b, _, _ in heads if b not in dict(now)]
        said = ([note] if note else []) + said
        if not said:
            return ("leave",)
        return ("change", "; ".join(said), cards.landings_form(len(heads)) != cards.landings_form(len(now)), left)
    ticked, work = list(ticked or []), work or {}
    was = {b: h for b, h, _ in heads}
    at = {r["bolt"]: r["facts"]["head"] for r in rows}

    def stands(b):  # the user's send still stands for a bolt they ticked, at its head now
        return b in ticked and b in was and send_stands(was[b], at[b], work.get(b))
    # proven since the send: on no row of the card, or at a new head their send does not stand at
    anew = [(b, h) for b, h in now if was.get(b) != h and not stands(b)]
    moved = {b for b, _ in anew}
    main_first = {r["bolt"] for r in rows if not r["box"] and r.get("takes_main")}  # its send stands while it takes main in
    landing = [b for b in ticked if b in in_plan and (b not in held or b in main_first and stands(b)) and b not in moved]  # in flight or not yet submitted
    standing = [b for b in ticked if b in in_plan and b in held and b not in landing and stands(b)]
    if landing and not anew:
        return ("leave",)
    on = [b for b, _, _ in heads]
    gone = [b for b in ticked if b not in in_plan]
    said = ([f"Landed on GitHub's main: " + joined([f"{b} at {landed[b][:7]}" if b in (landed or {}) else b for b in gone])
             + "; every host's folder follows by swancloud's timer within minutes."]
            if gone and all(b in (landed or {}) for b in gone) else
            [f"Landed or left the plan: {joined(gone)}."] if gone else [])
    lands = [b for b in landing if b not in main_first]
    said += [f"Landing as you ticked: {joined(lands)}."] if lands else []
    stopped = {r["bolt"]: r["facts"]["stopped"] for r in boxed if r["facts"].get("stopped")}
    said += [f"{b}'s last landing at {stopped[b][0][:7]} was stopped, nothing of the bolt's: {stopped[b][1].rstrip('.')}; it "
             "lands on your send once that is cleared." for b in lands if b in stopped]
    said += [f"Taking main in first, your send standing for it: {joined([b for b in landing if b in main_first])}."] if len(lands) < len(landing) else []
    said += [f"Held: {b}, {held[b]}; your send stands for it: it lands once its team's fix has only taken main in and "
             "sluice has proven it, with nothing asked." if b in standing else
             f"Held: {b}, {held[b]}; {work_said(b, was[b], at[b], work.get(b))}, so a card asks for it again once it reads "
             "proven." for b in ticked if b in held and b not in landing]
    cleared = [b for b in on if b not in ticked]
    said += [f"Left: {joined(cleared)}."] if cleared else []
    said += ["Since your send, " + "; ".join(work_said(b, was[b], at[b], work.get(b)) if b in was and b in ticked else
                                             f"{b}'s head is now {h}" if b in was else f"{b} reads proven" for b, h in anew)
             + f", and the card that follows asks for {'it' if len(anew) == 1 else 'them'}."] if anew else []
    if not ticked:
        said = ["Sent with no bolt ticked, so nothing lands."] + said
    left = [b for b in cleared if b in dict(now) and b not in moved]
    if landing:
        return ("follow", " ".join(said), left, [(b, was[b]) for b in ticked if b in landing or b in standing])
    return ("close", " ".join(said), left if boxed else None, [(b, was[b]) for b in standing])


def landings_since(earlier, rows):
    """What changed since the user's send on a kit's last landings card, which a new card raised after it, following it
    (cards.follows_of), says first (rail-cards "A card that follows one the user answered says so first"), from facts
    alone (code.7): earlier, that card's rows as its last post or change recorded them (card_heads); rows, the rows
    that can land now (landing_rows, with a box). Each bolt that joins the card, each head that moved, and each bolt
    still waiting at the head the card showed, which the user's send left; sentences."""
    was = {b: h for b, h, _ in earlier}
    joins = [r["bolt"] for r in rows if r["bolt"] not in was]
    moved = [(r["bolt"], r["facts"]["head"][:7]) for r in rows if r["bolt"] in was
             and not (r["facts"]["head"].startswith(was[r["bolt"]]) or was[r["bolt"]].startswith(r["facts"]["head"]))]
    waits = [r["bolt"] for r in rows if r["bolt"] in was and r["bolt"] not in dict(moved)]
    return ([f"{joined(joins)} {'reads' if len(joins) == 1 else 'read'} proven and {'joins' if len(joins) == 1 else 'join'} the card."]
            if joins else []) + [f"{b}'s head is now {h}." for b, h in moved] + (left_waits(waits) if waits else [])


def left_waits(left):
    """The sentence a kit's landings card that follows the user's send says of the bolts that send left, shown again."""
    return [f"{joined(left)}, which you left, {'waits' if len(left) == 1 else 'wait'} on this card."]


def row_forecasts(order, pairs, held=()):
    """Each row's forecast conflicts (rail-cards "The landings card forecasts each row's conflicts"), from facts alone
    (code.7): order, the bolts of the card's rows that can land, in its order; pairs(ours, theirs), the paths git
    forecasts in conflict when the bolt ours is merged onto theirs, "main" or a bolt above it on the card, from their
    merge base: [] for none, None when git can't tell; held, the bolts the run record holds taking main first
    (main_conflict). {bolt: [(with, paths)]}, main first, then each bolt above it in the card's order, a pair with no
    conflict left out and one git could not tell kept with paths None, a forecast not made, which holds nothing; an
    empty list, no conflict forecast. Every bolt is forecast against main first, and one forecast to conflict with it,
    or held, takes main first (landing_rows), so it is forecast against main alone and no row is forecast against it:
    the rest are forecast among themselves, pairwise, as units are (teams.12)."""
    mains = {b: pairs(b, "main") for b in order}
    rest = [b for b in order if not mains[b] and b not in held]
    return {b: [(w, p) for w, p in [("main", mains[b])] + ([(w, pairs(b, w)) for w in rest[:rest.index(b)]] if b in rest else [])
                if p is None or p] for b in order}


def tree_paths(rc, out):
    """The paths `git merge-tree --write-tree --name-only --no-messages` names in conflict, from its exit and output:
    [] for a clean merge (0), the paths after the tree's id (1), each once; None for any other exit."""
    if rc == 0:
        return []
    if rc != 1:
        return None
    return list(dict.fromkeys(l for l in out.split("\n")[1:] if l))


def forecast_rows(fleet, label, kit, bolts, held=()):
    """The forecasts of a kit's landings card's rows (row_forecasts, held the bolts it is handed as taking main first by
    the run record), made where the kit's first building team
    (builder) has its main checkout: GitHub's main fetched there, a kit with no origin reading its own; each bolt read
    where it lives (gather.bolt_at, plan.19), GitHub's copy when the policy in it names a remote for the bolt, else the
    host's, a bolt made before gives went through sluice; and git merge-tree of each onto main and onto each bolt above
    it. Returns ({bolt: [(with, paths)]}, {bolt: why}, at),
    why for each bolt whose forecast crew could not make, or that has one not made against another it could not read:
    a branch on no ref it can read, a fetch or a git that failed, or no team building the kit, said and holding nothing
    (read.1); at, the revision of main forecast against, {"main": <sha>}, the commit origin/main names after the fetch or
    main for a kit with no origin, or None when the fetch or the read of it failed."""
    t = builder(fleet, label, kit)
    if not t:
        return ({b: [("main", None)] for b in bolts}, {b: f"no team of {label} builds {kit}, so crew reads no checkout of it" for b in bolts},
                None)
    main, host = t["kit"]["main"], t["machine"]
    try:
        origin = origin_fetched(fleet, t, main)
        name = "refs/remotes/origin/main" if origin else "refs/heads/main"
        rc, sha = kit_git(fleet, t, main, "rev-parse", "--verify", "-q", f"{name}^{{commit}}", ok=(0, 1))
        rc == 0 and sha or fail(f"{main} on {host} has no {'origin/main' if origin else 'branch main'} to forecast against")
    except Refusal as e:
        return {b: [("main", None)] for b in bolts}, {b: str(e) for b in bolts}, None
    at, why = bolts_where(fleet, t, main, origin, bolts)
    refs = {"main": sha, **at}

    def pairs(ours, theirs):
        if ours in why or theirs in why:
            return None
        try:
            return tree_paths(*kit_git(fleet, t, main, "merge-tree", "--write-tree", "--name-only", "--no-messages",
                                       refs[theirs], refs[ours], ok=(0, 1)))
        except Refusal:
            return None
    got = row_forecasts(bolts, pairs, held)
    for b, fs in got.items():
        for w, paths in fs:
            if paths is None and b not in why:
                why[b] = why.get(w) or f"git merge-tree could not tell in {main} on {host}"
    return got, why, {"main": sha}


def origin_fetched(fleet, t, main):
    """Whether the kit's main checkout on the team's host (t) has an origin, GitHub, fetched there when it has; refused
    in git's words when the fetch fails (plan.18)."""
    origin = kit_git(fleet, t, main, "remote", "get-url", "origin", ok=(0, 2))[0] == 0
    if origin:
        kit_git(fleet, t, main, "fetch", "-q", "origin")
    return origin


def bolts_where(fleet, t, main, origin, bolts):
    """Each bolt's head where it lives (gather.bolt_at, plan.19), read in the kit's main checkout on the team's host (t)
    once fetched (origin_fetched): GitHub's copy when the policy in it names a remote for the bolt, else the host's.
    Returns ({bolt: commit}, {bolt: why}), why for each on no ref crew can read there, or whose policy or git failed."""
    host, refs, why = t["machine"], {}, {}
    for b in bolts:
        github, own, at = f"refs/remotes/origin/bolt/{b}", f"refs/heads/bolt/{b}", {}
        try:
            for ref in ([github] if origin else []) + [own]:
                rc, out = kit_git(fleet, t, main, "rev-parse", "--verify", "-q", f"{ref}^{{commit}}", ok=(0, 1))
                if rc == 0 and out:
                    at[ref] = out
            rc, text = kit_git(fleet, t, main, "show", f"{github}:{gather.POLICY}", ok=(0, 128)) if github in at else (1, None)
            ref = gather.bolt_at(b, github in at, own in at, gather.policy_remote(text if rc == 0 else None, f"bolt/{b}"))
        except Refusal as e:
            why[b] = str(e)
            continue
        except ValueError as e:
            why[b] = f"{gather.POLICY} at origin/bolt/{b} is not TOML, so crew can't read bolt {b}: {e}"
            continue
        if ref:
            refs[b] = at[ref]
        else:
            why[b] = f"bolt/{b} is on no branch crew can read in {main} on {host}, GitHub's or the host's"
    return refs, why


def commits_listed(out):
    """git log --format='%h %s''s lines as [(sha, subject)], newest first."""
    return [tuple(l.split(" ", 1)) if " " in l else (l, "") for l in out.splitlines() if l.strip()]


def bolt_work(fleet, label, kit, moves):
    """Each bolt's own work between the head the user sent and its head now (rail-cards "A ticked bolt's approval
    stands while its own work is unchanged", Decision 1), read where the kit's forecasts are made (forecast_rows), in
    the kit's first building team's main checkout, GitHub's main fetched there once: a bolt's own work at a head being
    its non-merge commits main lacks, what it gained is `git log --no-merges <now> ^<sent> ^<main>` and what it lost
    `<sent> ^<now> ^<main>`, main GitHub's, or a kit's own with no origin. moves, {bolt: (sent, head)}, head None for
    one read where the bolt lives (bolts_where). Returns {bolt: {head, gained, lost, why}}, gained and lost
    [(sha, subject)], why set when crew could not tell, the fetch, the head sent or now, or git having failed, or no
    team building the kit (read.1)."""
    def told(head, why):
        return dict(head=head, gained=[], lost=[], why=why)
    t = builder(fleet, label, kit)
    if not t:
        return {b: told(h, f"no team of {label} builds {kit}, so crew reads no checkout of it") for b, (_, h) in moves.items()}
    main, host = t["kit"]["main"], t["machine"]
    try:
        origin = origin_fetched(fleet, t, main)
    except Refusal as e:
        return {b: told(h, str(e)) for b, (_, h) in moves.items()}
    mains = "refs/remotes/origin/main" if origin else "refs/heads/main"
    at, unread = bolts_where(fleet, t, main, origin, [b for b, (_, h) in moves.items() if not h])
    out = {}
    for b, (sent, head) in moves.items():
        head = head or at.get(b)
        if not head:
            out[b] = told(None, unread.get(b) or f"bolt/{b} is on no branch crew can read in {main} on {host}")
            continue
        try:
            for what, rev in (("your send's head", sent), ("its head now", head)):
                rc, _ = kit_git(fleet, t, main, "rev-parse", "--verify", "-q", f"{rev}^{{commit}}", ok=(0, 1, 128))
                rc == 0 or fail(f"{what}, {rev[:7]}, names no one commit in {main} on {host}")
            gained = commits_listed(kit_git(fleet, t, main, "log", "--no-merges", "--format=%h %s", head, f"^{sent}", f"^{mains}")[1])
            lost = commits_listed(kit_git(fleet, t, main, "log", "--no-merges", "--format=%h %s", sent, f"^{head}", f"^{mains}")[1])
        except Refusal as e:
            out[b] = told(head, str(e))
            continue
        out[b] = dict(head=head, gained=gained, lost=lost, why=None)
    return out


def batch_waits(units, due, unanswered):
    """Why a bolt that otherwise reads proven has no landing card yet (briefs.12), as landing_facts holds it: the units
    whose latest change no batch has held (due), then the batches holding a unit's latest change whose card the user
    has not answered (unanswered, {unit: batch}); None when neither holds it."""
    late = [u for u in units if u in due]
    held = sorted({unanswered[u] for u in units if u in unanswered and u not in due})
    said = ([f"{either(late)} {'has' if len(late) == 1 else 'have'} not been in a batch, which is due"] if late else []) + (
        [f"the user has not answered batch{'' if len(held) == 1 else 'es'} {joined([str(n) for n in held])}"] if held else [])
    return "; ".join(said) or None


def land_held(fleet, label, bolt):
    """The partition's plan, the bolt and the team holding it, as a landing reads them: the bolt None when the plan
    holds none by that name, the team None when no team holds it. Refused when the plan can't be read (read.1)."""
    plan = plan_of(fleet, label) or fail(f"{label}/main could not be read, so whether bolt {bolt} reads proven can't be told")
    b = plan.bolt(bolt)
    return plan, b, bolt_team(fleet, b) if b else None


def land_facts(fleet, label, plan, b, t, fixes_hold=True):
    """A held bolt's landing facts, read on the host of its team (t), so its row on its kit's landings card (land_row)
    and its reading (crew card session) read the same bolt: (facts, None) once it reads proven (landing_unready,
    landing_facts), the row's facts as cards.landings_card takes them with what the reading's writer needs beside them,
    the team, its conductor, its host and where the bolt last met main (base); (None, why) while it does not. With
    fixes_hold False, a fix in flight on it does not keep it from reading proven, and the facts hold each such fix with
    the words it started with ({fix: words or None}, fix_words), the bolt's last landing sluice refused ((head, words),
    refusals) or None, for landing_rows to hold its row by, and its last one sluice or its host stopped ((head, words),
    stops) or None, for its row to say. Refused when its kit can't be read (read.1)."""
    bolt = b.name()
    st = stages_for(fleet, plan, held_by(plan, t["name"]) or [b])
    k, why = st.kit(b)
    not why or fail(f"bolt {bolt}'s kit could not be read: {why}")
    of = {u.name(): st.of(u.name()) for u in plan.work_of(bolt)}
    work = [(n, s.get("kind", "unit"), s["stage"]) for n, s in of.items()]
    facts = k["bolts"].get(bolt, {})
    fixes = fixes_in_flight(k.get("fixes", []), bolt)
    why = landing_unready(work, facts.get("head"), facts.get("verdict"), fixes if fixes_hold else [])
    if why:
        return None, why
    entries = partition_entries(fleet, label)
    read_in = {}
    for n, _, us in batches(entries):
        for u, _, _ in us:
            read_in[u] = n
    main, head = t["kit"]["main"], facts["head"]
    now = gather.now_ref(gather.has_origin(main))  # the kit's main now, as its stages read it (plan.18)
    _, base = kit_git(fleet, t, main, "merge-base", facts["at"], now)  # the bolt where it is read (gather.bolt_read)
    _, moved = kit_git(fleet, t, main, "rev-list", "--count", "--first-parent", f"{base}..{now}")
    _, came = kit_git(fleet, t, main, "log", "-1", "--format=%(trailers:key=Sluice-From,valueonly)", head)
    due, unanswered = {u for u, *_ in due_changes(plan, entries)}, awaiting_answer(entries)
    frees = frees_of(st, plan, t, bolt)
    card = landing_facts(bolt, t["kit"]["name"], work, head, facts.get("head_at"), due, unanswered, read_in, int(moved),
                         pull_of(came.strip(), t["kit"]["repo"]),
                         dict(team=t["name"], next=frees[1]) if frees and frees[0] == "frees" else None)
    if not card:
        return None, batch_waits([n for n, kind, _ in work if kind == "unit"], due, unanswered)
    held = {} if fixes_hold else dict(fixes={f: fix_words(t, f) for f in fixes}, refusal=refusals(entries).get(bolt),
                                      stop=stops(entries).get(bolt))
    return dict(card, team=t["name"], conductor=f"{t['name']}-conductor", host=t["machine"], base=base, **held), None


def fix_said(t, fix, words):
    """The words a fix started with (crew fix's), kept on the team's host beside its stages file, never in the run
    record (record.3), for its bolt's row on its kit's landings card to say while it holds it (land_facts); what can't
    be written is said, and the fix stands."""
    f = team_state(t) / "fix-words" / fix.replace("/", "--")
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(words)
    except OSError as e:
        print(f"crew could not keep {fix}'s words for its bolt's landings row: {e.strerror or e}", file=sys.stderr)


def fix_words(t, fix):
    """The words a fix started with as fix_said kept them on the team's host, or None when none are kept."""
    try:
        return (team_state(t) / "fix-words" / fix.replace("/", "--")).read_text().strip() or None
    except OSError:
        return None


def landing_retry(why, fresh, fresh_why):
    """What follows a first refusal of a landing's reading at a raise (card-sessions "A landing's raise tries its
    reading again before raising without it"), from that refusal (why), the landing read afresh once the kit's main was
    fetched, as land_facts gives it (fresh, (facts, why it does not read proven)), or why that read was refused
    (fresh_why, fresh None): ("again", facts) to open the reading once more with the fresh facts, the card's from then;
    ("none", None) when the bolt no longer reads proven, so the raise posts and changes nothing; ("stand", why) when
    the fresh read was refused, the first facts and the first reason standing (read.1)."""
    if fresh_why:
        return "stand", why
    facts, unproven = fresh
    return ("none", None) if unproven else ("again", facts)


def landing_opened(fleet, label, plan, b, t, card, acts):
    """A landings row's facts with its reading opened by its read (land_row), before the card is built: its link,
    or on a refusal one more try as crew card session land/<bolt> makes it, the kit's main fetched on the team's host,
    this one, a fetch that failed said and the try going on (plan.18), the landing read afresh (land_facts) and its
    reading opened again with those facts (landing_retry). The facts the card is built from, carrying the reading's
    link or why it could not be opened (unread, the second try's reason, or the first's when the fresh read was
    refused); None when, read afresh, the bolt no longer reads proven, so the raise posts and changes nothing."""
    key, main = f"land/{card['bolt']}", t["kit"]["main"]
    try:
        return dict(card, link=acts.reading(label, key, card)[0])
    except Refusal as e:
        why = str(e)
    print(f"card {key}: its reading could not be opened on the tailnet: {why}; crew fetches {t['kit']['name']}'s main "
          "and tries once more", file=sys.stderr)
    try:
        if gather.has_origin(main):
            kit_git(fleet, t, main, "fetch", "-q", "origin")
    except Refusal as e:
        print(f"card {key}: {e}; the reading is tried again all the same", file=sys.stderr)
    fresh, fresh_why = None, None
    try:
        with READ.fresh():
            fresh = land_facts(fleet, label, plan, b, t)
    except Refusal as e:
        fresh_why = str(e)
    step, got = landing_retry(why, fresh, fresh_why)
    if step == "none":
        return None
    if step == "stand":
        why = got
    else:
        try:
            return dict(got, link=acts.reading(label, key, got)[0])
        except Refusal as e:
            card, why = got, str(e)
    print(f"card {key}: its reading could not be opened on the tailnet: {why}; crew card session {key} starts it", file=sys.stderr)
    return dict(card, unread=why)


def land_read(fleet, label, plan, b, t):
    """A held bolt's row on its kit's landings card, read on its team's host (t) as land_facts reads it, a fix in flight
    on it holding its row rather than keeping it off the card: (row, None), the row as landing_rows gives it, a box,
    or held for a fix or for sluice's refusal of its landing at its present head (rail-cards, Decision 7), a box saying
    what stopped its last landing at that head; (None, why) while it is no row. Refused when its kit can't be read
    (read.1)."""
    facts, why = land_facts(fleet, label, plan, b, t, fixes_hold=False)
    if why:
        return None, why
    return landing_rows([b.name()], {b.name(): facts}, {b.name(): facts["refusal"]} if facts.get("refusal") else {},
                        {b.name(): facts["stop"]} if facts.get("stop") else {})[0], None


def land_row(fleet, label, bolt, acts=None):
    """crew _land-row <label> <bolt>: a bolt's row on its kit's landings card, on the host of the team holding it, where
    its reading and its preview run (Decision 2): read as land_read reads it; a row that can land with its reading
    opened, or given again while it serves, twice if it must be, the second time on the landing read afresh
    (landing_opened), and the preview of its head asked, kept or replaced (landing_preview); a held row, and a bolt that
    is no row, with its reading ended and its preview released, as a card's close ends them (row_card_close). Returns
    the row, {bolt, box, why, facts}, its facts carrying its reading's link or why it could not be opened and its
    preview; or {bolt, why} while it is no row. Refused on any host but the team's, naming it, and when what it reads
    can't be read (read.1)."""
    acts = acts or CardActs(fleet)
    plan, b, t = land_held(fleet, label, bolt)
    if not b:
        return dict(bolt=bolt, why=f"{label}'s plan holds no bolt {bolt}")
    if not t:
        return dict(bolt=bolt, why=f"no team holds bolt {bolt}")
    t["machine"] == acts.host() or fail(f"bolt {bolt}'s row is read on {t['machine']}, where {t['name']}, which holds it, runs")
    row, why = land_read(fleet, label, plan, b, t)
    if row and row["box"]:
        facts = landing_opened(fleet, label, plan, b, t, row["facts"], acts)
        if facts:
            facts["preview"] = landing_preview(fleet, t, label, bolt, facts, acts)
            return dict(row, facts=facts)
        row, why = None, "read afresh, it no longer reads proven"
    for said in (acts.end(label, f"land/{bolt}"), acts.release_preview(label, f"land/{bolt}")):
        if said:
            print(said)
    return row or dict(bolt=bolt, why=why)


def land_row_cmd(fleet, a):
    """crew _land-row <label> <bolt> [--json]: land_row, what it does said on standard error, and the row printed, as
    JSON with --json, the one line on standard output, which the raise of the kit's card reads (CardActs.land_row)."""
    with contextlib.redirect_stdout(sys.stderr):
        row = land_row(fleet, a.label, a.bolt)
    print(json.dumps(row) if a.json else f"{a.bolt}: " + ("can land" if row.get("box") else row["why"]))


def kit_card_state(acts, label, key, owner, card, entries):
    """The kit's landings card ops holds (card), as landings_step reads it, with the bolts the user ticked on it: ({status,
    heads}, ticked), status "answered" once the user answered it, else "waiting", heads its rows as its last post or
    change recorded them (card_heads); (None, why) when Pending You could not be read or no longer finds it, so the
    raise changes nothing (read.1), but a lost card, recorded lost, reads as none held, for a new one to be posted."""
    try:
        with acts.bridge(owner, "Its landings card is not changed.") as py:
            got, words = py.answer("get_request", {"requestId": card, "name": owner})
    except Refusal as e:
        return None, str(e)
    if words is not None:
        if cards.lost(words):
            card_lost(acts, label, owner, key, card, words)
            return {"status": None}, None
        return None, f"Pending You refused get_request: {words}"
    recorded = next((e.get("Heads") for e in reversed(entries) if e.get("Card") == card and not e.get("Refused")
                     and e.get("Act") in ("card.post", "card.update") and e.get("Heads")), None)
    heads = card_heads(recorded)
    return {"status": "answered" if got.get("status") == "answered" else "waiting", "heads": heads, "ticked": ticked_of(got, heads)}, None


def main_told(acts, label, plan, rows, found, at, entries):
    """Each bolt the landings card's forecast found newly in conflict with main told to its conductor (bolt-teams "A
    waiting bolt's conflict with main tells its conductor the take-main fix"): rows, {bolt: facts} of each whose
    forecast against main names files (found, {bolt: paths}), at main's revision (at); told the take-main fix in the
    words a conductor's wait gives (bolt_forecast), with --bolt while its team holds two bolts (teams.16), once for the
    same bolt head and revision of main, whichever forecast recorded it first, read from the partition's run record and
    this host's (entries); recorded as the wait's forecast is, on bolt/<bolt> with its Heads and Paths, only once the tell
    went through, so a tell that fails records nothing and the next raise tells it again (roles.4, read.1)."""
    done = {e.get("Heads") for e in entries if e.get("Act") == "forecast" and not e.get("Refused") and e.get("Heads")}
    for b, f in rows.items():
        team = f["team"]
        told = bolt_forecast(team, label, b, {"conflict": {"paths": found[b], "with": []}, "head": f["head"], "onto": at["main"]},
                             done, len(held_by(plan, team)) > 1)
        if not told:
            continue
        heads, paths, words = told
        if not acts.tell(f"{team}-conductor", words):
            print(f"card land/{f.get('kit', '')}: {team}-conductor was not told {b} takes main first, so it is told at the next raise",
                  file=sys.stderr)
            continue
        acts.emit(label, "forecast", [f"bolt/{b}"], why=f"bolt({b}): forecast to conflict with main", Heads=heads,
                  Paths=" ".join(paths), Reached="told")
        done.add(heads)


def raise_landings(fleet, label, kit, acts=None, note=None, dead=False, pane=None):
    """crew _land-card <label> <kit>: a kit's landings card raised, changed, followed or closed (rail-cards, record 0031
    as amended 2026-10-23, Decisions 2 and 8), on the partition's main machine in main-level ops's name, refused
    elsewhere naming it: each of the plan's bolts of the kit a team holds asked for its row on its team's host
    (acts.land_row, land_row), a host that does not answer named and its rows left off, the rest raised (read.3); the
    card ops holds read first, its state in Pending You and the bolts the user ticked on it; the rows in the plan's
    order, but each that an earlier send still lands (landings_sent, rows_unsent), at the head sent or at one whose own
    work is the same (record 0031 as amended 2026-10-24), read once for every bolt sent or ticked whose head moved
    (acts.work, bolt_work), one whose work changed a row again; each that can land forecast against main and the rows
    above it (acts.forecast, forecast_rows); then what the card makes of them (landings_step): posted, changed in place
    with what changed, or the event's note first, followed when its form changed, left, withdrawn saying why, or closed
    with what landed, was held and was left, with how many rows can still land, a new card following it while any can,
    each card that asks for a bolt again saying first what changed of its work (work_said): in its opening when it
    follows the user's send (below), else ahead of its summary (built_saying); an answered
    card whose send still lands bolts while another reads proven since is closed saying so, the bolts it still lands
    kept as its close's Heads, and a new card follows it with the rest; one closed with a ticked bolt held whose send
    stands keeps it as its Heads, for it to land on that send. With pane, the outcome the run record
    keeps of a landing on the user's word in ops's pane (pane_landed), note then being what Pending You is sent, their
    words among them: a waiting card no row of which can land is closed as answered there, rather than withdrawn. A
    card that follows the user's send says first what they sent and what changed since: what landed, was held and was
    left, the outcome, and that each bolt they left waits on it; or, posted after the kit's last card, what changed of
    each bolt asked again and the bolts that joined, moved or still wait since (landings_since). With
    dead, an older copy this host's sign-in can't reach standing, as the rail's sweep hands it, the card is posted
    saying first that it was lost (built_again). The card's id, or None."""
    acts = acts or CardActs(fleet)
    machine = crew.partition_of(fleet, label)["machine"]
    machine == acts.host() or fail(f"{kit}'s landings card is raised on {machine}, where {label}-ops's cards are")
    plan = plan_of(fleet, label) or fail(f"{label}/main could not be read, so {kit}'s landings card is not raised")
    owner, key = f"{label}-ops", f"land/{kit}"
    got, unread = {}, set()
    for b in plan.bolts():
        t = bolt_team(fleet, b) if b.get("Repo") == kit else None
        if not t:
            continue
        row, why = acts.land_row(label, b.name(), t["machine"])
        if row is None:
            print(f"card {key}: {t['machine']} did not answer for bolt {b.name()} ({why}), so its row is left off", file=sys.stderr)
            unread.add(b.name())
        elif "box" in row:
            got[b.name()] = row
    entries, whole = acts.entries(label), acts.partition(label)
    card = cards.card_under(entries, key, owner)
    state, ticked = None, None
    if card:
        state, why = kit_card_state(acts, label, key, owner, card, entries)
        if state is None:
            print(f"card {key}: {card} is not changed, since where it stands can't be read: {why}", file=sys.stderr)
            return None
        if state["status"] is None:  # lost to its owner and recorded so: posted again
            card, state = None, None
        else:
            ticked = state.pop("ticked")
    rows = [got[b.name()] for b in plan.bolts() if b.name() in got]
    shown = (state or {}).get("heads") or []
    # a bolt on a row of the card held is that card's to ask for; the rest an earlier send ticked are judged by it
    sent = {b: h for b, h in landings_sent(entries, key, owner).items() if b not in {s for s, _, _ in shown}}
    ticked_at = {b: h for b, h, _ in shown if b in (ticked or [])}
    at = {r["bolt"]: r["facts"]["head"] for r in rows}
    # The bolts the user left (left_now), recorded when they change: a row whose host did not answer is left as recorded
    # (read.1). This host's entries the branch does not hold yet come after the branch's.
    ids = {e["Id"] for e in whole if e.get("Id")}
    recorded, stops = left_marks(whole + [e for e in entries if not e.get("Id") or e["Id"] not in ids], key)
    left = dict(left_now(state, ticked, at, recorded, stops), **{b: h for b, h in recorded.items() if b in unread})
    if left != recorded:
        acts.emit(label, "landing.left", [cards.row_object(key, acts.kits(label))], by=owner, Key=key,
                  Heads=" ".join(f"{b.name()}@{left[b.name()]}" for b in plan.bolts() if b.name() in left))
    moves = {b: (h, at[b]) for b, h in list(sent.items()) + list(ticked_at.items())
             if b in at and not (at[b].startswith(h) or h.startswith(at[b]))}
    work = acts.work(label, kit, moves) if moves else {}
    rows, landing, asked = rows_unsent(rows, sent, work)
    for b in landing:
        print(f"card {key}: {b} lands on the user's send of an earlier card, so it is no row of this one")
    for b, words in asked:
        print(f"card {key}: {words}; the user's send of an earlier card does not stand for it, so it is a row again")
    # Every row that can land is forecast against main first, and each forecast to conflict with it, by this forecast or
    # the run record's at its present head, takes main first; the rest are forecast among themselves (row_forecasts).
    recorded = {r["bolt"]: c for r in rows if r["box"] for c in [main_conflict(whole, r["bolt"], r["facts"]["head"])] if c}
    boxed = [r["bolt"] for r in rows if r["box"]]
    forecast, unmade, onto = acts.forecast(label, kit, boxed, list(recorded)) if boxed else ({}, {}, None)
    if onto:
        acts.keep_main(label, kit, onto["main"])
    found = {b: p for b, fs in forecast.items() for w, p in fs if w == "main" and p}
    takes = dict(recorded, **{b: (onto["main"][:7], p) for b, p in found.items()})
    rows = [landing_rows([r["bolt"]], {r["bolt"]: r["facts"]}, {}, takes_main=takes, left=left)[0] if r["box"] else r for r in rows]
    main_told(acts, label, plan, {r["bolt"]: r["facts"] for r in rows if r["bolt"] in found}, found, onto, whole + entries)
    boxed = [r["bolt"] for r in rows if r["box"]]
    for r in rows:
        if r["box"]:
            r["facts"] = dict(r["facts"], forecast=forecast.get(r["bolt"], []), forecast_why=unmade.get(r["bolt"]))
    landed = {next((o[5:] for o in e.get("On") or [] if o.startswith("bolt/")), None): e.get("Head") or ""
              for e in whole if e.get("Act") == "bolt.land" and not e.get("Refused")}
    in_plan = {b.name() for b in plan.bolts() if b.get("Repo") == kit}
    step = landings_step(rows, state, ticked, in_plan, landed, note, bool(pane), work)
    t = builder(fleet, label, kit)
    where = card_where(t["kit"] if t else {"main": str(pathlib.Path.home()), "repo": kit})
    facts = dict(kit=kit, rows=[r["facts"] for r in rows if r["box"]], held=[dict(bolt=r["bolt"], why=r["why"]) for r in rows if not r["box"]],
                 ops=owner)
    offered = [f"land:{b}" for b, _, _ in (state or {}).get("heads") or []]  # the rows its answer ticked or left

    def unticked(cleared):  # the rows a card shows unticked: those the step names cleared, and every bolt the user left
        return [r["bolt"] for r in rows if r["box"] and (r["bolt"] in cleared or r["bolt"] in left)]
    said = [w for _, w in asked]  # what changed of each bolt an earlier send ticked that is a row again, said first
    if step[0] == "none":
        return None
    if step[0] == "leave":
        print(f"card {key}: {card} is left as it is" + (", the user having answered it" if state and state["status"] == "answered" else ""))
        return card
    if step[0] == "withdraw":
        return row_card_close(fleet, label, owner, key, reason=step[1], acts=acts, Rows="0")
    if step[0] == "answered":
        return row_card_close(fleet, label, owner, key, outcome=f"{pane}; {step[1]}", acts=acts, said=f"{note}; {step[1]}",
                              here=True, Rows="0")
    if step[0] == "post":
        facts.update(left=unticked(step[1]), follows=cards.follows_of("land", {"kit": kit}, entries, owner))
        earlier = card_heads(next((e.get("Heads") for e in reversed(entries) if e.get("Card") == facts["follows"] and not e.get("Refused")
                                   and e.get("Act") in ("card.post", "card.update") and e.get("Heads")), None)) if facts["follows"] else []
        # following the user's send, what changed of a bolt asked again opens the card with the rest (card_posted)
        build = cards.landings_card if facts["follows"] else built_saying(cards.landings_card, said)
        since = [f"{w}." for w in said] + landings_since(earlier, [r for r in rows if r["box"] and r["bolt"] not in dict(asked)])
        return row_card_change(fleet, label, owner, built_again(build) if dead else build, facts,
                               "; ".join(said + [note or "Raised as the bolts stand"]), where, acts,
                               since=since if facts["follows"] else None)
    if step[0] == "change":
        _, change, kind_changed, cleared = step
        return row_card_change(fleet, label, owner, cards.landings_card, dict(facts, left=unticked(cleared)),
                               "; ".join(said + [change]), where, acts, kind_changed)
    outcome = " ".join([f"{w}." for w in said] + [step[1]])
    if step[0] == "follow":  # closed with the bolts the send still lands as its Heads (landings_sent), the rest following
        _, _, cleared, landing = step
        rest, waits = [r["facts"] for r in rows if r["box"] and r["bolt"] not in dict(landing)], unticked(cleared)
        closed = row_card_close(fleet, label, owner, key, outcome=outcome, acts=acts, offered=offered, Rows=str(len(rest)),
                                Heads=" ".join(f"{b}@{h}" for b, h in landing))
        # the outcome, what changed of each bolt asked again among it (landings_step), opens the card that follows
        return closed and row_card_change(fleet, label, owner, cards.landings_card, dict(facts, rows=rest, left=waits,
                                                                                         follows=closed), outcome, where, acts,
                                          since=[outcome] + (left_waits(waits) if waits else []))
    _, _, then, standing = step  # the bolts held whose send stands kept as its close's Heads (landings_sent)
    closed = row_card_close(fleet, label, owner, key, outcome=outcome, acts=acts, offered=offered, Rows=str(len(boxed)),
                            **({"Heads": " ".join(f"{b}@{h}" for b, h in standing)} if standing else {}))
    if then is None or not boxed or not closed:  # a close refused leaves the card open, and nothing follows it yet
        return closed
    waits = unticked(then)
    return row_card_change(fleet, label, owner, cards.landings_card, dict(facts, left=waits, follows=closed), outcome, where, acts,
                           since=[outcome] + (left_waits(waits) if waits else []))


def raise_landings_row(fleet, row, acts=None):
    """The rail's raise of a kit's landing row, land/<kit>, whose card is missing or lost (sweep_cards), or whose card
    this host's sign-in can't reach, handed that older copy as the row's dead: raise_landings of its kit; a row of a
    bolt's key, the form before a kit's card, is raised by none."""
    kind = land_key(row.get("key"), partition_kits(fleet, row["label"]))
    return raise_landings(fleet, row["label"], kind[1], acts, dead=bool(row.get("dead"))) if kind and kind[0] == "kit" else None


def land_hand(fleet, label, kit, note=None, pane=None):
    """The raise of a kit's landings card handed to the partition's main machine, where main-level ops's cards are
    (Decision 2, code.3): raise_landings there, as crew _land-card <label> <kit>, through crew.on_machine as the one
    asking, or in this process when this is that machine, with pane, the outcome of a landing on the user's word in
    ops's pane, note then what Pending You is sent; what it said passed on, and its failure said, refusing nothing of
    the event that handed it."""
    machine = crew.partition_of(fleet, label)["machine"]
    if machine == crew.this_host():
        try:
            raise_landings(fleet, label, kit, note=note, pane=pane)
        except Refusal as e:
            print(f"{kit}'s landings card is not raised: {e}", file=sys.stderr)
        return
    r = crew.on_machine(fleet, machine, crew.crew_argv(fleet, machine, "_land-card", label, kit, *(["--note", note] if note else []),
                                                       *(["--pane", pane] if pane else [])))
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode:
        said = ((r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1]
        print(f"{kit}'s landings card is not raised on {machine}: {said}", file=sys.stderr)


def land_card_cmd(fleet, a):
    """crew _land-card <label> <kit> [--note <words>] [--pane <outcome>]: raise_landings on the partition's main
    machine, handed there by the event that changed a bolt's row (land_hand)."""
    raise_landings(fleet, a.label, a.kit, note=a.note, pane=a.pane)


def head_previewed(fleet, t, head):
    """Whether the kit's policy as the bolt's head holds it declares a preview (kit.previewed), as sluice reads it from
    the previewed revision, read with git in the kit's main checkout on the team's host: (declared, None), or (None,
    why) when it can't be read (read.1)."""
    main = t["kit"]["main"]
    try:
        _, held = kit_git(fleet, t, main, "ls-tree", "--name-only", head, "--", kit.DECLARATION)
        text = kit_git(fleet, t, main, "show", f"{head}:{kit.DECLARATION}")[1] if held else None
        return kit.previewed(text, f"{kit.DECLARATION} at {head[:7]}"), None
    except Refusal as e:
        return None, str(e)


def landing_preview(fleet, t, label, bolt, card, acts):
    """The preview a landing card is raised with (rail-cards, record 0031 §3), as cards.landing_card takes it: asked,
    kept, replaced or released through acts.preview (preview_ask) once the kit's policy at the head declares one
    (head_previewed) or crew recorded one for the bolt; {head, why} when that policy can't be read, crew's record left
    as it is (read.1); None with neither."""
    declared, why = head_previewed(fleet, t, card["head"])
    if why:
        return {"head": card["head"], "why": why}
    if not declared and not preview_path(label, bolt).exists():
        return None
    return acts.preview(label, f"land/{bolt}", dict(card, previewed=declared))


def land_end(fleet, label, bolt):
    """A bolt's reading and its preview ended on this, its team's, host, with its row on its kit's landings card, held or
    gone, which no close of a card of the bolt's own ends (row_card_close): what each said, printed."""
    acts = CardActs(fleet)
    for said in (acts.end(label, f"land/{bolt}"), acts.release_preview(label, f"land/{bolt}")):
        if said:
            print(said)


def landing_held(fleet, t, bolt, words):
    """A fix started on the bolt holds its row on its kit's landings card (rail-cards "A fix in flight holds the card"):
    its landing pull request drafted first, so no merge into the bolt lands it meanwhile (pull_hold, bolt-teams), what
    crew could not read or mark said on standard error and the fix going on, since the fix is how the bolt is repaired
    and its merge drafts it before it starts (merge_holds); then, on this, the team's host, any landing card of the
    bolt's own its conductor still holds withdrawn with "held for a fix: <the fix's words>", the row's reading ended and
    its preview released (land_end); then the kit's card changed on the partition's main machine, the row held with no
    box, its note naming the fix's words (land_hand). The row has its box again once the bolt reads proven again."""
    try:
        said = pull_said(bolt, *pull_hold(fleet, t, bolt, "held"), True, t["kit"]["repo"])
        if said:
            print(said)
    except Refusal as e:
        print(f"{str(e).rstrip('.')}; the fix goes on, and its merge drafts it before it starts", file=sys.stderr)
    owner, (_, outcome, reason) = f"{t['name']}-conductor", landing_act("fix", words=words)
    for key in landing_card_keys(cards.host_entries(record, t["label"], crew.this_host()), bolt, owner):
        row_card_close(fleet, t["label"], owner, key, outcome=outcome, reason=reason)
    land_end(fleet, t["label"], bolt)
    land_hand(fleet, t["label"], t["kit"]["name"], f"{bolt} is held for a fix: {words}")


def merge_holds(fleet, t, bolt, what):
    """A merge into the bolt, a unit's, a chore's or a fix's (what, its name for the words), holds the bolt's landing
    pull request before it starts (bolt-teams): a ready one drafted (pull_hold, "held") and said, so the merge's move of
    bolt/<bolt> submits nothing to main; when crew can't read or mark it, the merge does not start, naming the pull
    request, or the repository it could not list, in gh's words (read.1)."""
    try:
        pull, act = pull_hold(fleet, t, bolt, "held")
    except Refusal as e:
        fail(f"{what} does not start: {e}")
    said = pull_said(bolt, pull, act, True, t["kit"]["repo"])
    if said:
        print(said)


def landing_after_merge(fleet, t, bolt):
    """The merge's end, on the team's host: what it frees of the team (team_freed); then the raise of the kit's landings
    card handed to the partition's main machine (land_hand), which puts the bolt on it once it reads proven, or changes
    its row, its head moved, with what a yes now frees as its note. What crew can't read is said, and the merge
    stands."""
    plan = plan_of(fleet, t["label"])
    if not plan or not plan.bolt(bolt) or plan.bolt(bolt).get("Team") != t["name"]:
        return
    note = None
    try:
        note = team_freed(fleet, t, plan, bolt)
    except Refusal as e:
        print(f"whether {t['name']} is free for its next bolt can't be told: {e}", file=sys.stderr)
    land_hand(fleet, t["label"], plan.bolt(bolt).get("Repo") or t["kit"]["name"], note)


def team_freed(fleet, t, plan, bolt):
    """What a merge into a bolt frees of its team (teams.16), from one read of its kits: once the bolt reads proven for
    a give and the team holds another that is proven too, the note the kit's landings card changes with, what a yes
    now frees (frees_note), returned, else None; and once the team may take its next bolt and one is planned for it
    (free_now), the partition's dispatchers that are up told so, as a landing tells them."""
    held = held_by(plan, t["name"])
    facts = proven_facts(stages_for(fleet, plan, held), plan, held)
    proven = {f[0]: give_refusal(t["name"], [f]) is None for f in facts}
    planned = next_planned(plan, t)
    if free_now(give_refusal(t["name"], facts), planned):
        tell_dispatchers(fleet, t["label"], f"{t['name']} can take its next bolt: bolt {bolt} reads proven. Give a free team its next bolt.")
    if proven.get(bolt) and any(proven[b] for b in proven if b != bolt):
        return frees_note(t["name"], planned)
    return None


def next_planned(plan, t):
    """The bolt a give would hand the team now (to_give), by name, or None when none is planned for it."""
    try:
        return to_give(plan, None, t["name"], [k["name"] for k in crew.kits_of(t)], t["label"]).name()
    except Refusal:
        return None


def free_now(refusal, planned):
    """Whether a merge's end tells the dispatchers a team can take its next bolt (teams.16): the give would not be
    refused (give_refusal) and a bolt is planned for the team (planned, its name or None)."""
    return refusal is None and planned is not None


def yes_frees(this, others, planned):
    """What a yes to a bolt's landing frees of its team (teams.16), the one fact its rail row and its card share:
    others, each bolt the team holds as (name, proven), this one left out; planned, the bolt a give would hand the team
    (next_planned) or None. None when the team holds no other bolt, being free already; ("builds", it) while the other
    is not proven, the team building it meanwhile; ("frees", planned) once it is, planned None saying nothing is
    planned for the team."""
    others = [(n, proven) for n, proven in others if n != this]
    if not others:
        return None
    name, proven = others[0]
    return ("frees", planned) if proven else ("builds", name)


def frees_of(st, plan, t, bolt):
    """yes_frees for a bolt of the team t, its other bolt read proven from the kits as read (st), as a give reads it."""
    others = [x for x in held_by(plan, t["name"]) if x.name() != bolt]
    return yes_frees(bolt, [(x.name(), give_refusal(t["name"], proven_facts(st, plan, [x])) is None) for x in others],
                     next_planned(plan, t) if others else None)


def frees_said(team, frees):
    """The landing row's line for what a yes frees (yes_frees), or None."""
    if not frees:
        return None
    kind, other = frees
    if kind == "builds":
        return f"{team} builds {other} meanwhile"
    return f"a yes frees {team} for {other}" if other else f"a yes frees {team}, and nothing is planned for it"


def frees_note(team, planned):
    """The change note on a landing card whose yes now frees its team, its other bolt read proven (teams.16)."""
    return f"A yes now frees {team} for {planned}" if planned else f"A yes now frees {team}, and nothing is planned for it"


def landing_cards_closed(fleet, t, bolt, outcome, said=None, here=False):
    """At crew bolt land, on the team's host, once the partition's plan no longer holds the bolt (plan.16): any landing
    card of the bolt's own its conductor still holds closed with outcome, its reading ended and its preview released
    (land_end); then the kit's landings card raised on the partition's main machine (land_hand), which closes it once
    every bolt the user ticked has landed or been held, naming where GitHub's main holds each. A landing on the user's
    word in ops's pane sends said in place of the outcome, and closes a card still waiting as answered there (here,
    pane_landed): the bolt's own card, and the kit's once no row of it can land. A plan that can't be read closes none,
    saying so (read.1)."""
    pl = plan_of(fleet, t["label"])
    if pl is None or pl.bolt(bolt):
        print(f"no landing card of bolt {bolt} is closed: " + (f"{t['label']}/main could not be read" if pl is None else
                                                                f"{t['label']}/main still holds the bolt"))
        return
    owner, (_, outcome, reason) = f"{t['name']}-conductor", landing_act("landed", words=outcome)
    for key in landing_card_keys(cards.host_entries(record, t["label"], crew.this_host()), bolt, owner):
        row_card_close(fleet, t["label"], owner, key, outcome=outcome, reason=reason, said=said, here=here)
    land_end(fleet, t["label"], bolt)
    land_hand(fleet, t["label"], t["kit"]["name"], said if here else None, outcome if here else None)


def bolt_land(fleet, a):
    """A bolt whose units and chores have all landed on its kit's main, out of the plan, the landing recording the
    commit main holds (plan.14, plan.16), then, by the tidy on its team's host once the landing's place is gone, its
    branch deleted by sluice wherever the policy at its tip keeps it, on GitHub for a bolt given since gives went
    through sluice, a delete sluice refuses named in its words with the bolt out of the plan all the same (plan.19,
    land_delete), and its landing card closed there with where GitHub's main holds it (landed_words), after, for a landing
    on the user's word in ops's pane (pane_word_of), that word and their words kept on this host (landing_word_read),
    as answered there (pane_landed); the words kept are removed once the landing is written. A bolt no team holds,
    built outside a team, is read on the host and main checkout of a team of the partition building its kit, and lands
    the same way once main holds each of its units' changes and chores, on the user's word (roles.2)."""
    label, repo, tip, plan = locate(fleet, "Bolt", a.bolt, default_label(fleet, a))
    b = plan.bolt(a.bolt)
    t = held = bolt_team(fleet, b)
    units = [u.name() for u in plan.work_of(a.bolt)]
    if not held:
        t = builder(fleet, label, b.get("Repo"))
        why = unheld_refusal(a.bolt, units, b.get("Repo"), t, label)
        not why or fail(why)
    # What main holds now, GitHub's after the command's one fetch (plan.18), read before which units landed, so a bolt
    # sluice has just landed reads landed with no wait for the fleet's timer; the landing records it (plan.14).
    said = host_run(fleet, t["machine"], MAIN, t["kit"]["main"])
    ref, head, why = kit.main_now(said, t["kit"]["name"], t["machine"])
    not why or fail(why)
    if held:
        stage_of = stages_for(fleet, plan, [b]).of
    else:
        h = survey(fleet, [(t["name"], None)]).get(t["machine"]) or {"ok": False, "error": "it was not asked"}
        k = h["kits"].get(t["kit"]["main"]) if h["ok"] else None
        k = k if k and k.get("ok") else None
        stage_of = unheld_stages(k, h.get("error") or f"{t['machine']} did not read {t['kit']['main']}", Stages(fleet, plan, {}).of,
                                 [u.name() for u in plan.work_of(a.bolt) if is_chore(u)])
    landed = all(stage_of(u)["stage"] == "landed" for u in units)
    entries = partition_entries(fleet, label) if landed else []
    outside = [u for u, *_ in due_changes(plan, entries) if u in units] if landed else []
    why = land_refusal(a.bolt, units, stage_of, outside, label)
    not why or fail(why)
    # The user's word to land, when it was given in ops's pane, and their words, kept where it was submitted (plan.16).
    pane = pane_word_of(entries, a.bolt) if b.get("Team") else None
    kept = landing_word_read(label, a.bolt, pane[2]) if pane else None
    landed = landed_words(head, kit.said_of(said).get("SUBMISSION_GITHUB" if ref == "origin/main" else "SUBMISSION_OWN"))
    outcome, sent = pane_landed(landed, pane[0], pane[1], kept) if pane else (landed, None)

    def change(w):
        w.bolt(a.bolt)
        late = [u for u in w.plan.work_of(a.bolt) if u.name() not in units]
        not late or fail(f"{kind_of(late[0])} {late[0].name()} was added to {a.bolt} since it was checked; it has not landed")
        for u in w.plan.work_of(a.bolt):
            w.plan.remove(u)
            w.on.append(f"{kind_of(u)}/{u.name()}")
        w.plan.remove(w.plan.bolt(a.bolt))
        return [a.bolt]
    write(fleet, label, change, f"plan({a.bolt}): land the bolt", act="bolt.land", on=[f"bolt/{a.bolt}"],
          fields=dict(Repo=t["kit"]["name"], Head=head))
    if b.get("Team"):
        after = plan_of(fleet, label)
        print(landed_line(a.bolt, t["kit"]["name"], head, t["name"], [x.name() for x in held_by(after, t["name"])] if after else None))
        if pane and kept is None:
            here = crew.this_host()
            where = f"are kept on {pane[3]}, where it was submitted, not on {here}" if pane[3] != here else f"are not kept on {here}"
            print(f"the user's words to land {a.bolt} {where}: its landing card closes naming {pane[0]}'s pane and the time, without them")
        tidy_after(fleet, t, f"bolt {a.bolt}", (a.bolt, outcome, sent, bool(pane)))
        if pane:
            landing_word_drop(label, a.bolt)
    else:
        print(f"{a.bolt} has landed at {t['kit']['name']}'s {head[:7]}; no team held it")


# A landing's submission (plan.16, record 0026), on the team's host, refused there when sluice's wt-submit, which
# worktrunk runs as `wt submit`, is not on its path: a short-lived worktree on the bolt's branch, the one place sluice
# takes a submission from, nothing moving the branch there, and cut with no write to the host's bolt/<bolt>: `git
# worktree add --no-checkout` writes the worktree's HEAD alone and `read-tree -m -u HEAD` its files, where a plain add's
# checkout writes the branch to the value it holds, a transaction sluice's guard judges against the branch's copy on
# GitHub and refuses while the two differ, so sluice's push for the pull request is the one writer of both (plan.19,
# sluice clause 124); `wt submit main --no-wait --json` from it, in the name of whoever asked for it, which answers once
# sluice has queued it, what sluice said on standard error passed through. To a main that takes pull requests sluice
# answers with the pull request it opened, `{"branch":"main","pull_request":<n>,"state":...}`, its submission made from
# the place `pull/<n>` (sluice 0.36.4 lib.rs submit_pull, pulls.rs place), and to any other main with the submission.
# While sluice has it the worktree's git dir holds, in crew-landing, the process id of a `sluice wait` on it kept
# running on the host until its outcome is in, then emptied, which no stage starts on the bolt beside (landing_now): a
# wait on the submission, or, for a pull request, `sluice wait main` from the place, which follows the pull request to
# its submission's outcome; an answer naming neither empties it at once. It decides nothing (code.7): it prints, as
# shell assignments, RC, the submission's exit; TIP, the bolt's tip that was submitted; OLD, the host's own main before,
# empty when it has none; ID, the submission's number from sluice's JSON, and PULL, the pull request's, each empty when
# it gave none; ANSWER, what sluice printed on standard output, base64, for crew to name an answer it can't read, and
# its verdict when it refused the submission at once, its error document (verdict_printed); SAID, what it said on
# standard error, base64, which crew says beside that verdict and never as it (beside_of); and LEVEL, the value the
# host's bolt/<bolt> had when it levelled it, - for none, or empty when it wrote nothing. The fifth word is
# the head to submit (landing_head), empty for the host's copy as it stands, and the sixth the copy's value as
# LAND_COPIES read it, - for none: given a head the copy is not at, it first sets the host's bolt/<bolt> to it with `git
# update-ref` guarded by that value, before anything is cut (plan.19), the one write sluice's guard lets through, its
# value the branch as sluice's route reads it on GitHub; git refuses it when the copy moved since the read, and the
# guard when GitHub's branch did, either way in their words with nothing cut or submitted. A landing's worktree that
# stands from an earlier attempt is brought along with `read-tree -m -u`, which writes no ref, git's words when it
# cannot; and a worktree whose HEAD is not the head given submits nothing. Given a submission (the seventh word) and the
# tip it submitted (the eighth), the head and value empty, it levels nothing and waits on that submission again in
# place of submitting: the place made again, the `sluice wait` on it holding crew-landing as for one sluice queued, ID
# that submission and TIP that tip, as landing_ended asks once sluice itself failed and its record has the submission
# standing (submission_of).
SUBMIT = r"""main=$1 path=$2 bolt=$3 head=$5 from=$6
export SLUICE_AGENT=$4
cd "$main" || exit 2
command -v wt-submit >/dev/null || { echo "wt submit needs sluice's wt-submit, which is not on $(hostname -s)'s path" >&2; exit 2; }
old=$(git rev-parse --verify -q refs/heads/main) || old=
now=$(git rev-parse --verify -q "refs/heads/bolt/$bolt") || now=
level=
if [ -n "$head" ] && [ "$head" != "$now" ]; then
  was=$from; [ "$was" != - ] || was=$(printf '%0*d' ${#head} 0)
  err=$(git update-ref -m "crew: level to GitHub's bolt/$bolt for its landing" "refs/heads/bolt/$bolt" "$head" "$was" 2>&1) || {
    echo "$(hostname -s)'s copy of bolt/$bolt was not levelled to GitHub's ${head:0:7}: $(printf '%s' "$err" | tr '\n' ' ')" >&2; exit 2; }
  level=$from
fi
git rev-parse --verify -q "refs/heads/bolt/$bolt" >/dev/null || { echo "$main has no branch bolt/$bolt" >&2; exit 2; }
if [ ! -d "$path" ]; then
  { git worktree add -q --no-checkout "$path" "bolt/$bolt" >&2 && git -C "$path" read-tree -m -u HEAD >&2; } || exit 2
elif [ -n "$level" ] && [ "$level" != - ]; then
  err=$(git -C "$path" read-tree -m -u "$level" HEAD 2>&1) || {
    echo "the landing's worktree $path could not be brought to ${head:0:7}: $(printf '%s' "$err" | tr '\n' ' ')" >&2; exit 2; }
fi
tip=$(git -C "$path" rev-parse HEAD) || exit 2
[ -z "$head" ] || [ "$tip" = "$head" ] || { echo "the landing's worktree $path is at ${tip:0:7}, not bolt/$bolt's head ${head:0:7}, so nothing was submitted" >&2; exit 2; }
[ -z "$8" ] || tip=$8
mark=$(git -C "$path" rev-parse --absolute-git-dir)/crew-landing && echo $$ > "$mark" || exit 2
out=$(mktemp) || exit 2
if [ -n "$7" ]; then printf '{"id":%s}\n' "$7" >"$out"; : >"$out.err"; rc=0
else (cd "$path" && wt submit main --no-wait --json --no-remove) >"$out" 2>"$out.err" </dev/null; rc=$?; fi
cat "$out.err" >&2
id=; [[ $(cat "$out") =~ \"id\":[[:space:]]*([0-9]+) ]] && id=${BASH_REMATCH[1]}
pull=; [[ $(cat "$out") =~ \"pull_request\":[[:space:]]*([0-9]+) ]] && pull=${BASH_REMATCH[1]}
answer=$(base64 < "$out" | tr -d '\n')
said=$(base64 < "$out.err" | tr -d '\n')
rm -f "$out" "$out.err"
if [ "$rc" = 0 ] && [ -n "$id" ]; then
  nohup bash -c 'sluice wait "$1" --timeout 24h --json >/dev/null 2>&1; : > "$2"' crew "$id" "$mark" >/dev/null 2>&1 </dev/null &
  echo $! > "$mark"
elif [ "$rc" = 0 ] && [ -n "$pull" ]; then
  nohup bash -c 'cd "$1" && sluice wait main --timeout 24h --json >/dev/null 2>&1; : > "$2"' crew "$path" "$mark" >/dev/null 2>&1 </dev/null &
  echo $! > "$mark"
else
  : > "$mark"
fi
printf 'RC=%s TIP=%s OLD=%s ID=%s PULL=%s ANSWER=%s SAID=%s LEVEL=%s\n' "$rc" "$tip" "$old" "$id" "$pull" "$answer" "$said" "$level"
"""

# sluice's outcome of a landing's submission, waited on in the kit's main checkout on the team's host, a call at a time
# (code.9): `sluice wait <n> --timeout 9m --json`, exiting 5 while it is still undecided, and printing the
# submission's record, whose state is its outcome (wait_outcome).
WAIT = r"""cd "$1" && exec sluice wait "$2" --timeout 9m --json"""

# A landing's end, on the team's host, once sluice's outcome of its submission is in (SUBMIT, WAIT): the landing's
# worktree removed; and, when the host's own main moved, the kit's main checkout brought level with it while it is on
# branch main, since sluice moves the branch and not that checkout's files, and left as it is when it is detached, the
# anchor the fleet's timer moves (plan.18). It decides nothing (code.7): it prints the kit's mains after a fresh fetch
# (MAINS), whether each holds the bolt's tip that was submitted, HELD_GITHUB and HELD_OWN, "yes", "no", or - when that
# main is absent, for landing_said to judge by main now; then, as shell assignments: RC, the submission's outcome as
# sluice's exit gives it (0 landed, 1 its checks failed, 2 a conflict or a refusal, 3 sluice itself failed, 4
# withdrawn, 64 a bad command line, 130 stopped); TIP, the bolt's tip that was submitted; OLD, the host's own main
# before, empty when it has none; KEPT, the worktree when git could not remove it, and WHY, git's words for it, which
# the tidy at the bolt's landing sweeps or names (tidy_over); LEVEL, "yes", "detached", why it was not tried, or empty
# when the host's own main did not move; SAID, sluice's verdict on the submission (verdict_printed), base64, as crew
# hands it, since bash's %q garbles what is not ASCII in the C locale.
LANDED = r"""main=$1 path=$2 bolt=$3 tip=$4 old=$5 rc=$6 said=$7
cd "$main" || exit 2
kept= why=; why=$(git worktree remove "$path" 2>&1 >/dev/null) || kept=$path
new=$(git rev-parse --verify -q refs/heads/main) || new=
level=
if [ -n "$old" ] && [ -n "$new" ] && [ "$new" != "$old" ]; then
  if ! on=$(git symbolic-ref -q --short HEAD); then level=detached
  elif [ "$on" != main ]; then level="its main checkout is not on main"
  elif git read-tree -m -u "$old" main >&2; then level=yes
  else level="git read-tree could not bring it level"; fi
fi
[ -n "$kept" ] || why=
""" + MAINS + r"""held() { if ! git rev-parse --verify -q "$1^{commit}" >/dev/null; then echo -; elif git merge-base --is-ancestor "$tip" "$1"; then echo yes; else echo no; fi; }
echo "HELD_GITHUB=$(held refs/remotes/origin/main)"
echo "HELD_OWN=$(held refs/heads/main)"
printf 'RC=%s TIP=%s OLD=%s KEPT=%q WHY=%q LEVEL=%q SAID=%s\n' "$rc" "$tip" "$old" "$kept" "$why" "$level" "$said"
"""

# The bolt's branch marked landed in the kit's git config, branch.bolt/<bolt>.crew, when it carries crew's mark, so
# every later read of the team judges the bolt's work against main (record 0003, read.4), run on the team's host once
# landing_said has read that the bolt landed (code.7): MARKED, "yes", "no" when the branch carries no mark of crew's,
# or why git could not set it.
LANDED_MARK = r"""main=$1 bolt=$2
cd "$main" || exit 2
if ! git config --get "branch.bolt/$bolt.crew" >/dev/null; then marked=no
elif git config "branch.bolt/$bolt.crew" landed; then marked=yes
else marked="git config could not set it"; fi
printf 'MARKED=%q\n' "$marked"
"""


# sluice's own record of main's submissions, read in the kit's main checkout on the team's host before a landing's
# pull request is readied, so crew can tell the submission sluice makes for the landing from any made before it
# (landing_submitted), and after, for that submission, when sluice answered with a pull request or an earlier
# submission, or sluice itself failed with the bolt's tip not on main now (submission_of): every submission sluice
# keeps of main, the decided among them.
SUBMISSIONS = r"""cd "$1" || exit 2
exec sluice status main --all --json
"""

# A submission's states in sluice 0.36.4 (sluice-core records.rs, State): those it stands in, in the queue or a chain
# under test, as crew says them, and those it is out in, where sluice's wait ends.
STANDING = {"queued": "queued", "waiting": "waiting on a submission it comes after", "testing": "under test",
            "passed": "passed, to land next", "landing": "landing"}
OUT = {"failed": "blamed for a check that failed", "conflict": "in conflict", "withdrawn": "withdrawn", "landed": "landed"}
AGAIN = 3  # the times a landing waits again on a submission sluice's record has standing, sluice failing each time


def landing_report(said):
    """LANDED's report (said) as facts: its last line's assignments, sluice's last words decoded from SAID, and the
    KEY=value lines before it, MAINS's and HELD_GITHUB and HELD_OWN; None when crew can't read them (read.2)."""
    try:
        f = dict(w.split("=", 1) for w in shlex.split(said.strip().splitlines()[-1] if said.strip() else ""))
        words = " ".join(base64.b64decode(f.get("SAID", ""), validate=True).decode(errors="replace").split())
    except ValueError:
        return None
    held = kit.said_of(said)
    if not {"RC", "TIP", "OLD", "SAID"} <= set(f) or not all(held.get(k) in ("yes", "no", "-") for k in ("HELD_GITHUB", "HELD_OWN")):
        return None
    return f, words, held


def sluice_failed(said, before):
    """The tip a landing submitted when sluice itself failed, its submission or its wait exiting 3, and main now, read
    after it, does not hold that tip: whether the bolt lands is then sluice's own record's to say (submission_of,
    plan.16). None when sluice exited anything else, the bolt landed, or crew can't read the report or main now, which
    landing_said says as they are."""
    r = landing_report(said)
    if r is None or r[0]["RC"] != "3":
        return None
    f, _, held = r
    ref, now, why = kit.main_now(said, "", "")
    return None if why or (now != before and held["HELD_GITHUB" if ref == "origin/main" else "HELD_OWN"] == "yes") else f["TIP"]


def submissions_listed(code, out, err):
    """main's submissions as SUBMISSIONS printed them on the team's host, read by facts checked against sluice 0.36.4's
    `sluice status main --all --json` (read.2, tests/py/sluice-0.36.4/status-all.json): its submissions[], each a
    sluice/submission@1 with its id and head; or the words why crew has none: sluice did not answer, or printed what
    crew can't read."""
    try:
        doc = json.loads(out)
    except ValueError:
        doc = None
    if code != 0:  # sluice says why as {"error": {"message": ...}} under --json; ssh and bash on standard error
        said = doc.get("error") if isinstance(doc, dict) else None
        said = said.get("message") if isinstance(said, dict) else None
        said = said if isinstance(said, str) and said else next((l.strip() for l in (err or "").splitlines() if l.strip()), "")
        return f"sluice status main --all exited {code}" + (f": {said}" if said else "")
    subs = doc.get("submissions") if isinstance(doc, dict) else None
    if not isinstance(subs, list) or not all(isinstance(s, dict) and s.get("schema") == SUBMISSION and type(s.get("id")) is int
                                             and isinstance(s.get("head"), str) for s in subs):
        return f"sluice status main --all printed no listing of submissions crew reads: {cut((out or '').strip(), 200) or 'nothing'}"
    return subs


def submission_of(tip, code, out, err, pull=None, after=0):
    """sluice's own record of a landing's submission, from what SUBMISSIONS printed on the team's host
    (submissions_listed): the last of main's submissions whose head is the tip that was submitted, made after the last
    sluice had recorded before the landing (after, landing_submitted), so that no submission made before it is ever
    read as its own; with pull, the pull request sluice answered the landing's submission with (SUBMIT's PULL), the
    last of those sluice made from its place, `pull/<n>` in the record's from.worktree, as sluice's own wait on a pull
    request finds it (lib.rs submit_pull, pulls.rs follow). Returns {"id", "state"}, with the record's failed, result
    and conflict beside them where it holds them, for landing_blame to judge it by; or the words why crew has none:
    sluice records no such submission, holds it in a state crew does not read, did not answer, or printed what crew
    can't read."""
    subs = submissions_listed(code, out, err)
    if isinstance(subs, str):
        return subs
    made = lambda s: pull is None or isinstance(s.get("from"), dict) and s["from"].get("worktree") == f"pull/{pull}"
    mine = [s for s in subs if s["head"] == tip and s["id"] > after and made(s)]
    if not mine:
        return (f"sluice records no submission of {tip[:7]} to main" + (f" from pull request #{pull}" if pull is not None else "")
                + (f" newer than #{after}" if after else ""))
    s = max(mine, key=lambda s: s["id"])
    if s.get("state") not in STANDING and s.get("state") not in OUT:
        return f"sluice records #{s['id']} in a state crew does not read: {cut(json.dumps(s.get('state')), 60)}"
    return dict({"id": s["id"], "state": s["state"]}, **{k: s[k] for k in ("failed", "result", "conflict") if k in s})


def wait_again(sub, again):
    """The submission a landing waits on again (plan.16): sluice's record of it, read once sluice itself failed with
    the bolt's tip not on main now (submission_of), while it stands queued or under test, as long as crew has waited on
    it again fewer than AGAIN times; else None."""
    return sub["id"] if isinstance(sub, dict) and sub["state"] in STANDING and again < AGAIN else None


# sluice's exit for a submission out in each state (sluice 0.36.4 lib.rs exit_for), which landing_said reads.
EXITS = {"landed": "0", "failed": "1", "conflict": "2", "withdrawn": "4"}


def wait_outcome(n, code, out):
    """A landing's outcome from sluice's wait on its submission, #n (WAIT), read from the submission's state: sluice
    0.36.4's `sluice wait <n> --json` prints the submission's record, decided or not (lib.rs await_submission), and
    the state it is out in is its outcome, as sluice's exit for it (EXITS); a wait that printed no record of #n out in
    a state crew reads, as when sluice itself failed and printed its error, is its exit (read.2). (the outcome, the
    record of #n the wait printed, which landing_blame judges, or None when it printed none)."""
    try:
        doc = json.loads(out)
    except ValueError:
        doc = None
    doc = doc if isinstance(doc, dict) and doc.get("schema") == SUBMISSION and doc.get("id") == n else None
    return (EXITS[doc["state"]] if doc and doc.get("state") in EXITS else str(code)), doc


def answer_record(f):
    """sluice's record of the submission it made for a landing, as its answer to SUBMIT printed it (f, SUBMIT's
    assignments, ANSWER base64), when that answer is the record of the submission it names (ID): what sluice refused at
    once is judged by (landing_blame); None for an answer that is no such record, sluice's error among them."""
    try:
        doc = json.loads(base64.b64decode(f.get("ANSWER") or "").decode(errors="replace"))
    except ValueError:
        return None
    ok = isinstance(doc, dict) and doc.get("schema") == SUBMISSION and f.get("ID") and doc.get("id") == int(f["ID"])
    return doc if ok else None


def landing_blame(doc):
    """Whether a landing that did not land was the bolt's (plan.16 as read 2026-10-24, rail-cards "A refused landing is
    held on its row"), from sluice's own record of its submission alone (doc, a sluice/submission@1 as sluice 0.36.4
    writes it, records.rs Submission and FailedTask; tests/py/sluice-0.36.4/wait-failed-*.json), never from sluice's
    exit or words (read.2): ("bolt", None) when the record has it in conflict, or failed with a check that ran (its
    `hash` kept) or a run its time limit ended (`result` "timed out"), which its team's fix answers; else ("stop",
    words), nothing of the bolt's: every failed check left without a result, named with why each could not run as
    sluice words it (words.rs could_not_run) or, with none given, said so; a submission withdrawn, landed with main not
    holding it, or still standing; or a record crew can't read, said so. A decision of facts alone (code.7)."""
    state = doc.get("state") if isinstance(doc, dict) else None
    if not isinstance(state, str):
        return "stop", "crew can't read sluice's record of the submission"
    n = f"#{doc['id']}" if type(doc.get("id")) is int else "the submission"
    if state == "conflict":
        return "bolt", None
    if state == "failed":
        failed, result = doc.get("failed", []), doc.get("result")
        if not (isinstance(failed, list) and all(isinstance(t, dict) and isinstance(t.get("task"), str)
                                                 and all(isinstance(t.get(k, ""), str) for k in ("hash", "not_run"))
                                                 for t in failed) and isinstance(result, (str, type(None)))):
            return "stop", f"crew can't read the checks sluice's record of {n} blames: {cut(json.dumps(failed), 120)}"
        if result == "timed out" or any(t.get("hash") for t in failed):
            return "bolt", None
        why = [f"{t['task']} could not run: {' '.join(t['not_run'].split())}" for t in failed if t.get("not_run")]
        return "stop", "; ".join(why) or "every required check was left without a result"
    if state == "withdrawn":
        return "stop", f"sluice's record has {n} withdrawn"
    if state == "landed":
        return "stop", f"sluice's record has {n} landed"
    if state in STANDING:
        return "stop", f"sluice's record still has {n} {STANDING[state]}"
    return "stop", f"sluice's record has {n} in a state crew does not read: {cut(json.dumps(state), 60)}"


def verdict_of(doc):
    """sluice's verdict on a submission, from its record (doc, a sluice/submission@1 as sluice 0.36.4 prints and lists
    it, out in its state), in the words sluice's own report gives it (lib.rs report, detail): `#<n> conflict: <paths>`,
    with each submission it conflicts with; `#<n> failed: <checks> on <combination>`, timed out or not run; `#<n>
    withdrawn by <who> at <when>`; or `#<n> landed as <commit>`; or, from sluice's error document, its message
    (told.rs).
    It is never what sluice says on standard error, which under --json is only what its rounds did beside, a place it
    released or could not release among them (exec.rs tell_abandoned), and its own warnings and failure (main.rs).
    "" when doc is neither, or holds a submission not out; an absent field is left out (read.2)."""
    if not isinstance(doc, dict):
        return ""
    err = doc.get("error")
    if isinstance(err, dict):
        return " ".join(err["message"].split()) if isinstance(err.get("message"), str) else ""
    if doc.get("schema") != SUBMISSION or type(doc.get("id")) is not int or doc.get("state") not in OUT:
        return ""
    n, state = doc["id"], doc["state"]
    field = lambda d, k, of=str: d.get(k) if isinstance(d, dict) and isinstance(d.get(k), of) else None
    if state == "conflict":
        c = doc.get("conflict")
        paths = [p for p in field(c, "paths", list) or [] if isinstance(p, str)]
        withs = [w for w in field(c, "with", list) or [] if type(field(w, "id", int)) is int]
        said = f"#{n} conflict" + (f": {', '.join(paths)}" if paths else "")
        for w in withs:
            who = [x for x in (field(w.get("from"), "agent"), field(w.get("from"), "worktree")) if x]
            said += f"; conflicts with #{w['id']}" + (f" ({', '.join(who)})" if who else "")
        return said
    if state == "failed":
        tasks = [t for t in field(doc, "failed", list) or [] if field(t, "task")]
        named = lambda t: t["task"] + (f" ({t['system']})" if field(t, "system") else "") + (
            " (flaky)" if t.get("flaky") else " (could not run)" if t.get("not_run") else "")
        ran, unrun = [named(t) for t in tasks if field(t, "hash")], [t["task"] for t in tasks if not field(t, "hash")]
        parts = (["timed out"] if field(doc, "result") == "timed out" else []) + (
            [f"failed: {', '.join(ran)}"] if ran else []) + ([f"not run: {', '.join(unrun)}"] if unrun else [])
        on = field(doc.get("tested"), "combination")
        return f"#{n} " + ("; ".join(parts) or field(doc, "result") or "failed") + (f" on {on[:7]}" if on else "")
    if state == "withdrawn":
        w = doc.get("withdrawn")
        return f"#{n} withdrawn" + (f" by {field(w, 'by')}" if field(w, "by") else "") + (f" at {field(w, 'at')}" if field(w, "at") else "")
    return f"#{n} landed" + (f" as {field(doc, 'landed_as')[:7]}" if field(doc, "landed_as") else "")


def verdict_printed(out, n=None):
    """sluice's verdict (verdict_of) from what it printed on standard output under --json: the record of submission #n,
    as its wait prints it (WAIT), or as main's listing holds it (SUBMISSIONS); the record of any submission when n is
    None, as SUBMIT's answer holds one; or sluice's error document. "" when it printed none of them crew reads
    (read.2)."""
    try:
        doc = json.loads(out)
    except ValueError:
        return ""
    if isinstance(doc, dict) and isinstance(doc.get("submissions"), list):
        doc = next((s for s in doc["submissions"] if isinstance(s, dict) and s.get("id") == n), None) if n is not None else None
    elif n is not None and isinstance(doc, dict) and "error" not in doc and doc.get("id") != n:
        return ""
    return verdict_of(doc)


def beside_of(err, verdict=""):
    """What sluice said on standard error beside its verdict on a submission (verdict_of), its lines joined: under
    --json, what its rounds did beside, as a place it could not release, and its own warnings, which crew says beside
    the verdict and never as why a landing did not land; a line that is the verdict itself, as sluice's failure is said
    on both (main.rs), is left out."""
    lines = [" ".join(l.split()) for l in (err or "").splitlines() if l.strip()]
    return "; ".join(l for l in lines if not verdict or l not in (verdict, f"sluice: {verdict}"))


def answered_before(f, after):
    """The submission sluice answered a landing's submission with (f, SUBMIT's assignments) when sluice had recorded it
    before the landing, its id no newer than the last sluice had recorded then (after): sluice 0.36.4 answers a pull
    request sent back on the head submitted, and not marked ready for review since as its intake reads it, with that
    earlier submission's record and its exit, queueing nothing (lib.rs submit_pull, Reached::Before; pulls.rs
    consider), which is no outcome of this landing's. {"id", "state", "pull"}, its state and the pull request it was
    made from, `pull/<n>` in its record's from.worktree, each None when the answer does not say; None when the answer
    names no submission, or one made since."""
    if not f["ID"] or int(f["ID"]) > after:
        return None
    try:
        doc = json.loads(base64.b64decode(f["ANSWER"]).decode(errors="replace"))
    except ValueError:
        doc = None
    doc = doc if isinstance(doc, dict) and doc.get("schema") == SUBMISSION and doc.get("id") == int(f["ID"]) else {}
    place = re.fullmatch(r"pull/(\d+)", str((doc.get("from") if isinstance(doc.get("from"), dict) else {}).get("worktree")))
    state = doc.get("state") if doc.get("state") in STANDING or doc.get("state") in OUT else None
    return {"id": int(f["ID"]), "state": state, "pull": place.group(1) if place else None}


def submitted_line(bolt, name, f, was=None):
    """What crew says once a landing's submission has answered (f, SUBMIT's assignments, its ID that of the submission
    sluice made for it once crew has found it, landing_submitted): sluice's number for the submission, and the pull
    request it came from; with none, the pull request alone, the earlier submission sluice answered with (was,
    answered_before), sluice refusing it at once, or an answer naming no submission crew reads."""
    if f["ID"]:
        return f"bolt/{bolt} submitted to {name}'s main, sluice's #{f['ID']}" + (f" from pull request #{f['PULL']}" if f["PULL"] else "")
    if f["PULL"]:
        return f"bolt/{bolt} submitted to {name}'s main as pull request #{f['PULL']}"
    if was:
        return f"bolt/{bolt} submitted to {name}'s main, sluice answering with #{was['id']}, an earlier one"
    return f"bolt/{bolt} submitted to {name}'s main, " + ("sluice queueing nothing" if f["RC"] != "0" else
                                                           "sluice's answer naming no submission crew reads")


def left_standing(bolt, name, path, f, why=None, was=None):
    """The words for a landing whose submission sluice answered with nothing crew can wait on (f, SUBMIT's
    assignments, its RC 0 and its ID empty): an earlier submission (was, answered_before), named with the pull request
    it was made from and the state it is in, whose landing's own crew did not find in sluice's record (why,
    submission_of's words), and, when it was sent back, how sluice takes its pull request again (pulls.rs comment); a
    pull request, f's PULL, whose submission crew did not find there, named with the state sluice's answer gave it; or
    an answer crew can't read, named as sluice printed it (ANSWER). Whatever sluice queued is left standing: crew
    drafts and withdraws nothing on its reading of its own output, and records no refusal to hold the bolt's row for a
    fix (landing_ended)."""
    answer = base64.b64decode(f["ANSWER"]).decode(errors="replace").strip()
    if was:
        held = OUT.get(was["state"]) or STANDING.get(was["state"])
        said = (f"crew can't tell whether bolt/{bolt} will land on {name}'s main: sluice answered its submission with "
                f"#{was['id']}, an earlier one" + (f" from pull request #{was['pull']}" if was["pull"] else "")
                + (f", {held}" if held else "") + f", and {why}. crew withdraws nothing: ")
        if not was["pull"]:
            return said + f"what sluice queued stands, its place {path} kept, and sluice status main says where it is."
        again = (", which sluice takes again on that head only once it is marked a draft and then ready for review"
                 if was["state"] in ("failed", "conflict") else "")
        return said + f"the pull request stands as sluice has it{again}, and sluice wait main from {path} follows it."
    if f["PULL"]:
        try:
            state = json.loads(answer).get("state")
        except (ValueError, AttributeError):
            state = None
        held = f" ({state})" if isinstance(state, str) and state else ""
        return (f"crew can't tell whether bolt/{bolt} will land on {name}'s main: sluice holds it as pull request "
                f"#{f['PULL']}{held}, and {why}. crew withdraws nothing: the pull request stands as sluice has it, and "
                f"sluice wait main from {path} follows it.")
    return (f"crew can't tell whether bolt/{bolt} will land on {name}'s main: sluice answered its submission with what "
            f"crew can't read, {cut(' '.join(answer.split()), 200) or 'nothing'}. crew withdraws nothing: what sluice "
            f"queued stands, its place {path} kept, and sluice status main says where it is.")


def landing_said(bolt, name, host, said, before, marked="", sub=None, again=0, recorded=False, doc=None, beside=""):
    """What a landing's submission came to, as landing_end judges it: (landed, the words crew says to ops), or with
    recorded, (landed, the words its bolt.submit is recorded with)."""
    landed, words, kept_as, _ = landing_end(bolt, name, host, said, before, marked, sub, again, doc, beside)
    return landed, kept_as if recorded else words


def submit_again(bolt):
    """What crew tells ops of a landing nothing of the bolt's stopped (bolt-teams, main-level, Decision 4)."""
    return (f" Its row keeps its box and the user's word stands: report what stopped it, and once it is cleared crew bolt "
            f"submit {bolt} submits it again, with no new word.")


def landing_end(bolt, name, host, said, before, marked="", sub=None, again=0, doc=None, beside=""):
    """What a landing's submission came to, from LANDED's report on the team's host and the commit main now was at
    before it (code.7): (landed, the words crew says to ops, the words its bolt.submit is recorded with, stopped).
    Main now is GitHub's after the landing's fetch for a kit with an origin, its own main for one with none
    (kit.main_now, plan.18). Landed when main now moved and holds the bolt's tip that was submitted, whatever sluice
    exited, sluice having pushed it, so what comes next is crew bolt land and no push (plan.16); a non-zero exit is
    named with sluice's last words as what came after its push, sluice's to report apart; a main checkout not brought
    level is named with the command that levels it, and a detached one, which the fleet's timer moves, is said nothing
    of (plan.18); a mark of landed crew could not set on the bolt's branch is named (marked, mark_said), and lands it
    all the same. Not landed when main now did not move, "main is where it was", or moved without the bolt's tip, named
    where it is. It is the bolt's, refused, only when sluice's record of the submission says so (landing_blame): the
    record the wait printed or sluice answered with at once (doc, wait_outcome, answer_record), or, when sluice itself
    failed, exiting 3, with the bolt's tip not on main now, its record in sluice's listing (sub, submission_of; again,
    the times crew has waited on it again): a conflict or a check that ran is the team's to resolve by taking main into
    the bolt by a submission to the bolt (plan.8), and ops tells the bolt's conductor why in sluice's verdict, SAID, or
    its record's once sluice itself failed (sub's verdict), which is recorded, a conflict's paths among it (rail-cards
    "A refused landing is held on its row"), else crew's words for why it did not land and where main is. Anything
    else is stopped, nothing of the bolt's (rail-cards "A landing sluice or its host stopped keeps its box"): recorded
    with what stopped it, the record's words for it (landing_blame), sluice's verdict when it gave no record crew reads,
    or crew's for what it can't tell, and ops told to report it and submit the bolt again once it is cleared, with no
    new word (submit_again, main-level). While sluice's record has a submission sluice itself failed on standing queued
    or under test, crew says so and waits on it again (wait_again); crew can't tell when the record has it landed, has
    none, or can't be read, or when it still stands after AGAIN waits, each stopped. A main now crew can't read after
    the submission says it can't tell, naming why and sluice's exit, and words crew can't read land nothing, each
    stopped (read.1, read.2). What sluice said beside its verdict (beside, beside_of), as a place its rounds could not
    release, is said to ops apart, as not why it did not land, and never recorded. A worktree git could not remove is
    named with git's words to ops, and goes with the bolt at crew bolt land or is named there (tidy_over). The recorded
    words are what its row on its kit's landings card, its line on the rail and the card's close say (refused_at,
    stopped_at), never what crew tells ops, which is for ops's terminal."""
    r = landing_report(said)
    if r is None:
        why = f"crew can't read what the submission of bolt/{bolt} to {name}'s main came to: {said.strip()[-200:] or 'nothing'}"
        return False, why + "." + submit_again(bolt), why, True
    f, words, held = r
    kept = (f" Its worktree {f['KEPT']} is kept, git refusing to remove it: {' '.join(f.get('WHY', '').split()) or 'git said nothing'}. "
            "crew bolt land removes it with the bolt, or names it with why it stays." if f.get("KEPT") else "")
    ref, now, why = kit.main_now(said, name, host)
    if why:
        why = f"crew can't tell whether bolt/{bolt} landed on {name}'s main: {why}; the submission exited {f['RC']}"
        return False, f"{why}.{submit_again(bolt)}{kept}", why + ".", True
    if now != before and held["HELD_GITHUB" if ref == "origin/main" else "HELD_OWN"] == "yes":
        after = ("" if f["RC"] == "0" else
                 f" sluice exited {f['RC']} after its push: {words or 'sluice said nothing'}. That is sluice's to report, apart from the landing.")
        level = ("" if f.get("LEVEL") in ("", "yes", "detached") else
                 f" {name}'s main checkout was not brought level ({f['LEVEL']}): git read-tree -m -u {f['OLD'][:7]} main there.")
        why = "its branch carries no mark of crew's" if marked == "no" else marked
        mark = f" crew could not mark bolt/{bolt} landed: {why}." if why and why != "yes" else ""
        said_ = f"bolt/{bolt} landed on {name}'s main at {now[:7]}: now crew bolt land {bolt}.{after}{level}{mark}{kept}"
        return True, said_, said_, False
    where = ", and main is where it was" if now == before else f"; {name}'s main moved to {now[:7]} without it"
    if f["RC"] == "3":  # sluice itself failed, the bolt not on main now: sluice's record says what comes next
        failed = f"sluice itself failed ({words or 'it said nothing'})"
        tip = f"{name}'s main now, {now[:7]}, does not hold bolt/{bolt}'s tip {f['TIP'][:7]}"
        if not isinstance(sub, dict):
            unread = sub or "crew has not read sluice's record of the submission"
            return (False, f"crew can't tell whether bolt/{bolt} will land on {name}'s main: {failed}, {tip}, and {unread}."
                    f"{submit_again(bolt)}{kept}", f"{failed}, and {unread}", True)
        n, state = sub["id"], sub["state"]
        if wait_again(sub, again) is not None:
            return False, (f"{failed}, but its record has bolt/{bolt}'s submission, #{n}, {STANDING[state]} on {name}'s main, "
                           f"which does not hold it yet: crew waits on it again (sluice wait {n}).{kept}"), None, False
        if state in STANDING:
            return False, (f"crew can't tell whether bolt/{bolt} will land on {name}'s main: sluice itself failed again each of the "
                           f"{again} times crew waited on #{n}, which its record still has {STANDING[state]}, and {tip}."
                           f"{submit_again(bolt)}{kept}"), (f"sluice itself failed ({words or 'it said nothing'}) each of the "
                                                            f"{again} times crew waited on #{n}, which its record still has "
                                                            f"{STANDING[state]}"), True
        if state == "landed":
            why = f"{failed}, its record has #{n} landed, and {tip}"
            return False, f"crew can't tell whether bolt/{bolt} landed: {why}.{submit_again(bolt)}{kept}", why, True
        blame, cause = landing_blame(sub)
        why, cause = f"sluice itself failed, and its record has #{n} {OUT[state]}", cause and f"{failed}, and {cause}"
        verdict = sub.get("verdict") or ""
    else:
        blame, cause = landing_blame(doc) if doc is not None else ("stop", None)
        why = {"1": "main's checks failed on it", "2": "sluice refused it or found a conflict", "4": "it was withdrawn while it waited",
               "64": "sluice could not read its command line", "130": "the submission was stopped"}.get(f["RC"], f"the submission exited {f['RC']}")
        verdict = words if f["RC"] != "0" else ""
    also = f" Beside its verdict, and not why it did not land, sluice said: {beside}." if beside else ""
    if blame == "bolt":
        told = f" sluice's verdict: {verdict}." if verdict else ""
        return False, (f"bolt/{bolt} did not land: {why}{where}.{told} Tell the bolt's conductor why: a conflict is the bolt's, "
                       f"and the team takes main into it by a submission to the bolt, then you submit again.{also}{kept}"), (
            verdict or f"bolt/{bolt} did not land: {why}{where}."), False
    if cause:  # sluice's record says what stopped it
        told, kept_as = f"{cause.rstrip('.')}{where}", cause
    else:  # sluice gave no record crew reads: in its verdict, else crew's words
        crews = {"0": "the submission exited 0", "64": "sluice could not read its command line", "130": "the submission was stopped"
                 }.get(f["RC"], f"the submission exited {f['RC']}, and sluice gave no record of it crew reads")
        told, kept_as = f"{(verdict or crews).rstrip('.')}{where}", verdict or f"{crews}{where}"
    return (False, f"bolt/{bolt} did not land, and nothing of the bolt's stopped it: {told}.{submit_again(bolt)}{also}{kept}",
            kept_as, True)


def mark_said(code, out, err):
    """What LANDED_MARK said of the landed bolt's branch, for landing_said: MARKED's value, "yes", "no" or why git could
    not set it, or the host's own words when it did not run there (read.2)."""
    try:
        f = dict(w.split("=", 1) for w in shlex.split(out.strip()))
    except ValueError:
        f = {}
    if code == 0 and "MARKED" in f:
        return f["MARKED"]
    return ((err or out).strip().splitlines() or [f"exit {code}"])[-1].strip() or f"exit {code}"


# A bolt's open pull requests into main on GitHub, on the team's host, listed by gh as sluice's landing opens them,
# from the bolt's branch: RC, gh's exit, on the first line, then what gh printed; its errors on standard error. It
# decides nothing (code.7): kit.pull_said reads it.
PULL = r"""repo=$1 bolt=$2
out=$(gh pr list -R "$repo" --head "bolt/$bolt" --base main --state open --json number,isDraft,headRefOid,url </dev/null); rc=$?
echo "RC=$rc"
printf '%s\n' "$out"
"""

# A pull request marked a draft (act "draft", gh's --undo) or ready for review (act "ready"), on the team's host: RC,
# gh's exit, and SAID, gh's last line, base64, as LANDED passes sluice's (kit.pull_marked).
PULL_MARK = r"""repo=$1 n=$2 act=$3
undo=(); [ "$act" = draft ] && undo=(--undo)
out=$(gh pr ready "$n" -R "$repo" "${undo[@]}" 2>&1 </dev/null); rc=$?
echo "RC=$rc"
echo "SAID=$(printf '%s\n' "$out" | grep -v '^[[:space:]]*$' | tail -n 1 | base64 | tr -d '\n')"
"""


def pull_act(pull, want):
    """What crew does to a bolt's landing pull request (pull, kit.pull_said's, or None) for whether the user's word to
    land stands for its head (want "live") or not (want "held"): "draft" for a ready one held, "ready" for a draft one
    live, None when there is none or it is already as wanted. A draft is the one state sluice's intake never submits
    to main, however the branch moves (bolt-teams)."""
    if not pull:
        return None
    if want == "held":
        return None if pull["draft"] else "draft"
    return "ready" if pull["draft"] else None


def pull_said(bolt, pull, act, done, repo):
    """The words crew says of what it did to a bolt's landing pull request (pull_act): nothing when it marked nothing;
    for one drafted, that no merge into the bolt lands it and the next crew bolt submit on the user's word makes it live
    again; for one readied, that sluice takes it at the head the bolt has now; and, when gh did not mark it (done, gh's
    words, in place of True), why, with the command that drafts it, since the next merge would land it, or that nothing
    is submitted."""
    if not act:
        return ""
    url, n = pull["url"], pull["number"]
    if done is True:
        if act == "draft":
            return (f"Its pull request {url} is a draft, so no merge into bolt/{bolt} lands it; the next crew bolt submit "
                    f"{bolt}, on the user's word, makes it live again.")
        return f"Its pull request {url} is ready for review again, so sluice takes it at the head bolt/{bolt} has now."
    if act == "draft":
        return (f"crew could not make bolt/{bolt}'s pull request {url} a draft: {done}; until it is one, the next merge "
                f"into bolt/{bolt} lands it: gh pr ready {n} -R {repo} --undo makes it one.")
    return (f"crew could not make bolt/{bolt}'s pull request {url} ready for review: {done}; sluice takes no draft into "
            "main's queue, so nothing is submitted.")


def pull_unread(bolt, repo, want, why):
    """A refusal for a bolt's landing pull request gh could not list (kit.pull_said's, why): with, when it is to be held,
    the command that drafts it by its branch, since crew can't tell whether the next merge would land it."""
    if want == "held":
        return (f"{why}; until bolt/{bolt}'s pull request into main is a draft, the next merge into bolt/{bolt} may land "
                f"it: gh pr ready bolt/{bolt} -R {repo} --undo makes it one")
    return f"{why}; nothing is submitted"


def pull_hold(fleet, t, bolt, want):
    """A bolt's landing pull request made to follow the user's word (bolt-teams, plan.16), on the team's host: in a kit
    whose policy at main now, origin/main after a fetch (POLICY, kit.policy_said, plan.18), takes pull requests
    (kit.takes_pulls), the bolt's open pull request into main listed (PULL, kit.pull_said), what to do decided
    (pull_act) and done (PULL_MARK); a kit that takes none, or has no origin, is asked nothing of GitHub. (the pull
    request or None, the act done or None); refused, marking nothing, when the policy or the pull requests can't be
    read (pull_unread), and when gh does not mark it (pull_said, read.1)."""
    name, host, main, repo = t["kit"]["name"], t["machine"], t["kit"]["main"], t["kit"]["repo"]
    text, ref, _ = kit.policy_said(host_run(fleet, host, POLICY, main, kit.DECLARATION), name, host)
    if ref != "origin/main" or not kit.takes_pulls(text, f"{name}'s {kit.DECLARATION} on {ref}"):
        return None, None
    r = crew.on_machine(fleet, host, ["bash", "-c", PULL, "crew", repo, bolt])
    first, _, out = r.stdout.partition("\n")
    m = re.fullmatch(r"RC=(\d+)", first.strip())
    if r.returncode or not m:
        said = ((r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1].strip()
        fail(pull_unread(bolt, repo, want, f"crew can't list {repo}'s pull requests on {host}: {said}"))
    try:
        pull = kit.pull_said(int(m.group(1)), out, r.stderr, repo, bolt)
    except Refusal as e:
        fail(pull_unread(bolt, repo, want, str(e)))
    act = pull_act(pull, want)
    if act:
        r = crew.on_machine(fleet, host, ["bash", "-c", PULL_MARK, "crew", repo, str(pull["number"]), act])
        code, said = kit.pull_marked(r.returncode, r.stdout, r.stderr)
        code == 0 or fail(pull_said(bolt, pull, act, said or f"gh exited {code}", repo))
    return pull, act


def landing_unheld(fleet, t, bolt, *words):
    """The refusal of a landing that did not land, in each of words (landing_said's, for ops's terminal and for the
    record), once its pull request is drafted (pull_hold, "held"), so no merge into the bolt lands it with no word of
    the user's: each, then what was drafted; or, when crew could not draft it, why first, naming the pull request and
    the command that drafts it (bolt-teams)."""
    try:
        pull, act = pull_hold(fleet, t, bolt, "held")
    except Refusal as e:
        return [f"{str(e).rstrip('.')}. {w}" for w in words]
    said = pull_said(bolt, pull, act, True, t["kit"]["repo"])
    return [f"{w.rstrip('.')}. {said}" if said else w for w in words]


def submit_word_refusal(bolt, v):
    """Why crew bolt submit --excerpt submits nothing of the bolt (plan.16, briefs.12), or None: the verdict v on the
    words in the caller's own transcript (transcript.check, want="user") does not read them as the user's (signals.5),
    naming who said them (words_refusal), and holding none of the words (record.3). A decision of facts alone
    (code.7)."""
    return words_refusal(f"crew submits nothing of bolt {bolt}", v, "land a bolt",
                         "the user lands a bolt on its landing card or in main-level ops's pane")


def submit_refusal(bolts, kits, teams):
    """Why crew bolt submit submits nothing (rail-cards, Decision 6), or None, from facts alone: bolts, in the order
    given; kits, {bolt: its kit}; teams, {bolt: the team holding it, or None}. A bolt named twice; bolts of two kits,
    since one command lands one kit's bolts; a bolt no team holds, which has no branch to submit."""
    twice = sorted({b for i, b in enumerate(bolts) if b in bolts[:i]})
    if twice:
        return f"crew bolt submit names {either(twice)} twice: each bolt lands once, in the order given"
    if len({kits[b] for b in bolts}) > 1:
        return ("crew bolt submit lands one kit's bolts at a time, and " + joined([f"{b} is {kits[b]}'s" for b in bolts])
                + ": submit each kit's in a command of its own")
    none = [b for b in bolts if not teams.get(b)]
    return f"bolt {none[0]} is held by no team, so it has no branch to submit" if none else None


def submit_order(bolts, hosts):
    """When each bolt of crew bolt submit is submitted (Decision 6), from facts alone: bolts, in the order given;
    hosts, {bolt: the host of the team holding it}. [(bolt, when)]: the first at once; each after it "queued", as soon
    as sluice has queued the one before, when both are on one host, whose sluice keeps one queue and lands them in the
    order submitted; "ended", only once the one before has its outcome, when it is on another, since each host's sluice
    keeps its own queue."""
    return [(b, "first" if i == 0 else "queued" if hosts[b] == hosts[bolts[i - 1]] else "ended") for i, b in enumerate(bolts)]


def landing_submitted(fleet, t, bolt):
    """A bolt's landing submitted on its team's host (SUBMIT), after main now was read there (MAIN, main_held), the
    bolt's two copies read there after one fetch (LAND_COPIES, kit.land_copies) and the head it submits decided
    (landing_head, plan.19), and its landing pull request, a draft, readied, since the submission is the user's word
    (pull_hold, bolt-teams). SUBMIT is given that head and the host's copy's value as read, and levels the copy to it
    first; what the decision says of the copy is printed once SUBMIT has run, a level only when SUBMIT made it: {bolt, t,
    before, path, RC, TIP, OLD, ID, PULL, ANSWER, SAID, LEVEL, standing, last}, said as it is queued (submitted_line),
    sluice's verdict when it refused it at once in its answer, ANSWER, and what it said beside on standard error, SAID.
    Its ID is only ever a submission sluice made for this landing, newer than last, the last of main's submissions
    sluice had recorded before its pull request was readied (SUBMISSIONS, submissions_listed). Queued as a pull request, sluice
    answering with its number and no submission, or answered with an earlier submission (answered_before), whose exit
    is that one's and refuses nothing of this one, its ID is the submission sluice made for it, found in sluice's
    record on the team's host (SUBMISSIONS, submission_of with the pull request and last), and waited on as any other;
    standing, when crew finds none to wait on, its words (left_standing). Or {bolt, t, refused}, nothing submitted,
    when main now, the bolt's copies or sluice's record of main could not be read, the bolt's two copies have diverged,
    the pull request could not be readied, or the submission could not be made, in crew's, sluice's, gh's, git's or the
    host's words; refused before its submission ran, its pull request is left as it was."""
    name, host, main = t["kit"]["name"], t["machine"], t["kit"]["main"]
    try:
        before, why = main_held(name, host, host_run(fleet, host, MAIN, main))
        not why or fail(why)
        r = crew.on_machine(fleet, host, ["bash", "-c", LAND_COPIES, "crew", main, bolt, kit.DECLARATION])
        r.returncode == 0 or fail(f"crew can't read bolt/{bolt}'s copies on {host}: "
                                  + ((r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1])
        copies = kit.land_copies(r.stdout, bolt)
    except Refusal as e:
        return dict(bolt=bolt, t=t, refused=f"bolt/{bolt} was not submitted: {e}")
    decided = landing_head(bolt, host, copies)
    if isinstance(decided, str):  # the copy on GitHub unread, or the two diverged: nothing levelled or submitted
        return dict(bolt=bolt, t=t, refused=decided)
    head, own = (decided["head"], copies["own"]) if decided["head"] else ("", "")
    s = crew.on_machine(fleet, host, ["bash", "-c", SUBMISSIONS, "crew", main])
    subs = submissions_listed(s.returncode, s.stdout, s.stderr)
    if isinstance(subs, str):  # read.1: no submission sluice answers with could be told from one made before it
        return dict(bolt=bolt, t=t, refused=f"bolt/{bolt} was not submitted: crew can't read sluice's record of {name}'s main "
                                            f"on {host}, so could not tell its submission from any made before it: {subs}")
    last = max((x["id"] for x in subs), default=0)
    try:  # its pull request live on the user's word, which this is (bolt-teams)
        said = pull_said(bolt, *pull_hold(fleet, t, bolt, "live"), True, t["kit"]["repo"])
    except Refusal as e:
        return dict(bolt=bolt, t=t, refused=f"bolt/{bolt} was not submitted: {e}")
    if said:
        print(said)
    path = f"{t['kit']['dir']}/places/land-{bolt}"
    f, told = submit_ran(fleet, host, main, path, bolt, head, own)
    if f is None:
        return dict(bolt=bolt, t=t, refused=f"bolt/{bolt} was not submitted on {host}: {told}", attempted=True)
    if decided["said"] and (f["LEVEL"] or not decided["level"]):
        print(decided["said"])
    standing, was = None, answered_before(f, last)
    if was:  # an earlier submission's record and exit: this landing's own is looked for as a pull request's is
        f = dict(f, RC="0", ID="", PULL=was["pull"] or "")
    if f["RC"] == "0" and not f["ID"]:
        why = None
        if f["PULL"] or was:  # the submission sluice made for it since, from its place pull/<n> for a pull request
            s = crew.on_machine(fleet, host, ["bash", "-c", SUBMISSIONS, "crew", main])
            sub = submission_of(f["TIP"], s.returncode, s.stdout, s.stderr, int(f["PULL"]) if f["PULL"] else None, last)
            f["ID"], why = (str(sub["id"]), None) if isinstance(sub, dict) else ("", sub)
        standing = None if f["ID"] else left_standing(bolt, name, path, f, why, was)
    print(submitted_line(bolt, name, f, was))
    return dict(bolt=bolt, t=t, before=before, path=path, **f, standing=standing, last=last)


def submit_ran(fleet, host, main, path, bolt, head="", own="", *again):
    """SUBMIT run on the team's host, a landing's submission of head (landing_head), empty for the host's copy as it
    stands, the copy levelled to it first from own, its value as read (LAND_COPIES); or, given a submission and the tip
    it submitted (again), head and own empty, a wait on it again: (its assignments, RC, TIP, OLD, ID, PULL, ANSWER, SAID
    and LEVEL, None), or (None, the host's last words) when they can't be read."""
    r = crew.on_machine(fleet, host, ["bash", "-c", SUBMIT, "crew", main, path, bolt, record.who(), head, own, *again])
    READ.drop_kit(host, main)
    if r.stderr.strip():
        print(r.stderr.rstrip(), file=sys.stderr)
    try:
        f = dict(w.split("=", 1) for w in shlex.split(r.stdout.strip().splitlines()[-1])) if r.returncode == 0 else {}
        base64.b64decode(f.get("SAID", ""), validate=True)
        base64.b64decode(f.get("ANSWER", ""), validate=True)
    except (ValueError, IndexError):
        f = {}
    if not {"RC", "TIP", "OLD", "ID", "PULL", "ANSWER", "SAID", "LEVEL"} <= set(f):
        return None, ((r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1]
    return f, None


def landing_ended(fleet, label, p, a):
    """A submitted landing's end (Decision 6): sluice's outcome waited on a call at a time (WAIT) while it exits 5, read
    from the state of the submission's record the wait printed (wait_outcome), what sluice said passed through; a
    landing whose submission sluice answered with nothing crew can wait on (standing, left_standing) said so, recorded
    with the head submitted and no refusal, so no row is held for a fix, and nothing drafted, its place kept, since what
    sluice queued stands; the landing's worktree removed and the mains read (LANDED), and what it came to judged
    (landing_said). A landed bolt marked landed on its branch (LANDED_MARK), recorded (bolt.submit, with the head
    submitted) and closed at once by crew bolt land's own code (bolt_land), as its caller may close it (may_write), a
    close refused named with why and crew bolt land as the act that closes it; a bolt that did not land has its landing
    pull request drafted first, so no merge into the bolt lands it (landing_unheld), and is recorded so with the head
    that was submitted, and the kit's card raised so (land_hand): refused, when sluice's record of the submission has it
    for the bolt's own content (landing_end), in sluice's verdict on the submission when it gave one, from the record
    its wait printed or from SUBMIT's answer when it refused the submission at once (verdict_printed), which holds its
    row on its kit's landings card (refused_at); else stopped, with what stopped it as Why, Outcome stopped and no
    refusal, so its row keeps its box and says so (stopped_at), as is one whose submission ran and failed, with no head
    when it never named its tip (attempted); what sluice said beside its verdict on standard error said to ops apart
    and never recorded (beside_of). When sluice itself failed with the bolt's tip not on main now, sluice's own record
    of the submission is read on the team's host (SUBMISSIONS, submission_of, among those made since the landing began,
    newer than its last), its verdict with it, and while it has the submission standing crew says so and waits on it
    again (wait_again), SUBMIT given the submission's id and the tip it submitted, then its outcome waited on and its
    end read as before. A landing on the user's words in the caller's pane (p's frm, the transcript record bolt_submit
    read them from, a's excerpt) is recorded naming that record and the words' length, and the words kept on this host
    (landing_word_keep) before it is closed. Its words printed, standard error for one that did not land. Returns
    (bolt, landed)."""
    bolt, t = p["bolt"], p["t"]
    if p.get("refused") and p.get("attempted"):  # its submission ran and failed: drafted, and stopped, nothing of the bolt's
        words, why = landing_unheld(fleet, t, bolt, p["refused"] + "." + submit_again(bolt), p["refused"])
        record.emit(label, "bolt.submit", [f"bolt/{bolt}"], why=why, Outcome="stopped", Head=p.get("TIP"))
        print(words, file=sys.stderr)
        return bolt, False
    if p.get("refused"):  # crew's own refusal before anything was submitted: no head, holding no row
        record.emit(label, "bolt.submit", [f"bolt/{bolt}"], refused=p["refused"])
        print(p["refused"], file=sys.stderr)
        return bolt, False
    if p.get("standing"):  # nothing crew can wait on: what sluice queued stands, drafted by nothing of crew's
        record.emit(label, "bolt.submit", [f"bolt/{bolt}"], why=p["standing"], Head=p["TIP"])
        print(p["standing"], file=sys.stderr)
        return bolt, False
    name, host, main = t["kit"]["name"], t["machine"], t["kit"]["main"]
    again = 0
    while True:
        # sluice's verdict, from what it printed on standard output, its answer to SUBMIT when it refused at once; what
        # it said on standard error said beside it (verdict_printed, beside_of)
        rc, said = p["RC"], verdict_printed(base64.b64decode(p["ANSWER"]).decode(errors="replace"))
        beside = beside_of(base64.b64decode(p["SAID"]).decode(errors="replace"), said)
        doc = answer_record(p) if rc != "0" else None  # what sluice refused at once is judged by its answer's record
        if rc == "0":
            while True:
                w = crew.on_machine(fleet, host, ["bash", "-c", WAIT, "crew", main, p["ID"]])
                if w.returncode != 5:
                    break
            if w.stderr.strip():
                print(w.stderr.rstrip(), file=sys.stderr)
            rc, doc = wait_outcome(int(p["ID"]), w.returncode, w.stdout)
            said = verdict_printed(w.stdout, int(p["ID"]))
            beside = beside_of(w.stderr, said)
        r = crew.on_machine(fleet, host, ["bash", "-c", LANDED, "crew", main, p["path"], bolt, p["TIP"], p["OLD"], rc,
                                          base64.b64encode(said.encode()).decode()])
        READ.drop_kit(host, main)
        if r.stderr.strip():
            print(r.stderr.rstrip(), file=sys.stderr)
        if r.returncode:
            refused = f"crew can't tell whether bolt/{bolt} landed on {name}'s main: on {host}: " + (
                (r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1]
            landed, words, stopped = False, refused.rstrip(".") + "." + submit_again(bolt), True
            break
        tip, sub = sluice_failed(r.stdout, p["before"]), None
        if tip:  # sluice itself failed, the bolt not on main now: its record of the submission says what comes next
            s = crew.on_machine(fleet, host, ["bash", "-c", SUBMISSIONS, "crew", main])
            sub = submission_of(tip, s.returncode, s.stdout, s.stderr, after=p["last"])
            if isinstance(sub, dict):  # its verdict, from its record in the listing, where it is out
                sub = dict(sub, verdict=verdict_printed(s.stdout, sub["id"]))
        landed, words, refused, stopped = landing_end(bolt, name, host, r.stdout, p["before"], sub=sub, again=again, doc=doc,
                                                      beside=beside)
        n = wait_again(sub, again) if tip else None
        if n is None:
            break
        print(words, flush=True)
        f, told = submit_ran(fleet, host, main, p["path"], bolt, "", "", str(n), tip)
        if f is None:
            refused = (f"crew can't tell whether bolt/{bolt} will land on {name}'s main: crew could not wait on #{n} "
                       f"again on {host}: {told}")
            words, stopped = refused + "." + submit_again(bolt), True
            break
        p, again = dict(p, **f), again + 1
    if not landed:
        # its pull request a draft, so no merge into the bolt lands it
        words, refused = landing_unheld(fleet, t, bolt, words, refused)
        if stopped:  # nothing of the bolt's: its row keeps its box, saying what stopped it (stopped_at)
            record.emit(label, "bolt.submit", [f"bolt/{bolt}"], why=refused, Outcome="stopped", Head=p["TIP"])
        else:
            record.emit(label, "bolt.submit", [f"bolt/{bolt}"], refused=refused, Head=p["TIP"])
        print(words, file=sys.stderr)
        land_hand(fleet, label, name)  # its row held on its kit's landings card at the head submitted (refused_at), or not
        return bolt, False
    m = crew.on_machine(fleet, host, ["bash", "-c", LANDED_MARK, "crew", main, bolt])
    _, words = landing_said(bolt, name, host, r.stdout, p["before"], mark_said(m.returncode, m.stdout, m.stderr))
    now, _ = main_held(name, host, r.stdout)
    frm, excerpt = p.get("frm") or [], getattr(a, "excerpt", None)
    record.emit(label, "bolt.submit", [f"bolt/{bolt}"], why=f"bolt({bolt}): landed on main at {now[:7]}", Head=p["TIP"],
                **(dict(frm=frm, Chars=len(excerpt)) if frm else {}))
    if frm:  # the user's words kept on this host, for crew bolt land to close its card with (landing_word_keep)
        at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        landing_word_keep(label, bolt, excerpt, record.who(), at, frm[0])
        print(f"bolt {bolt} landed on the user's word in {record.who()}'s pane; crew bolt land closes its card with their words")
    print(words)
    closing = argparse.Namespace(cmd="bolt", sub="land", bolt=bolt, label=label)
    try:
        may_write(fleet, ("bolt", "land"), closing)
        bolt_land(fleet, closing)
    except Refusal as e:
        print(f"bolt/{bolt} landed and was not closed: {e}; crew bolt land {bolt} closes it", file=sys.stderr)
    return bolt, True


def bolt_submit(fleet, a):
    """crew bolt submit <bolt>... [--excerpt "<the user's words>"] [--label L]: main-level ops's landing of one kit's
    bolts, in the order given (plan.16, record 0026, Decision 6): refused before anything is submitted when they are of
    two kits, one is named twice, or one is held by no team (submit_refusal). With --excerpt, the word to land is the
    user's own words in the caller's pane: read first in the caller's own session transcript on this host, and nothing
    submitted unless crew reads them as the user's (submit_word_refusal); each landed bolt's bolt.submit then names the
    transcript record they were read from and their length, never the words (record.3), and this host keeps the words
    for crew bolt land to close the landing card with (landing_word_keep). Without it, the word is the landing card's
    send. Each bolt's branch submitted to its kit's main through sluice from
    a short-lived worktree on its team's host (landing_submitted), the next as soon as sluice has queued it when both
    are on one host, else once it has ended (submit_order); each then waited on in order, whether it landed read from
    main now, GitHub's after a fetch for a kit with an origin (landing_said, plan.18), and a landed bolt closed as it
    lands (landing_ended). Nothing is refused for a host's own main lagging GitHub's: sluice forms the landing on
    GitHub's main and pushes it with a lease (plan.8). Each bolt's landing pull request is live only on the user's word,
    which this command is (bolt-teams): a draft one is readied before its submission, nothing of that bolt submitted
    when it can't be, and one a landing leaves open is drafted before the command says the bolt did not land
    (landing_unheld). A bolt that did not land is said in sluice's words, and the rest go on; it exits non-zero naming
    each that did not land. It moves no branch itself, and is run in the background and waited on to its end
    (code.9)."""
    bolts = list(a.bolt) if isinstance(a.bolt, list) else [a.bolt]
    label, _, _, plan = locate(fleet, "Bolt", bolts[0], default_label(fleet, a))
    CONTEXT["label"] = label
    held = {b: plan.bolt(b) or fail(f"{label}'s plan holds no bolt {b}: crew bolt submit lands one partition's bolts") for b in bolts}
    teams = {b: bolt_team(fleet, held[b]) for b in bolts}
    why = submit_refusal(bolts, {b: held[b].get("Repo") for b in bolts}, {b: t["name"] if t else None for b, t in teams.items()})
    not why or fail(why)
    words, frm = getattr(a, "excerpt", None), []
    if words is not None:
        words.strip() or fail("crew bolt submit needs the user's words: --excerpt \"<their words, as they wrote them>\"")
        v, sid = CardActs(fleet).heard(words)
        why = submit_word_refusal(", ".join(bolts), v)
        not why or fail(why)
        frm = [f"session/{sid}/{v.uuid or f'line-{v.line_hash()[:16]}'}"]
    outcomes, pending = [], []
    for b, when in submit_order(bolts, {b: teams[b]["machine"] for b in bolts}):
        if when == "ended":
            outcomes += [landing_ended(fleet, label, p, a) for p in pending]
            pending = []
        pending.append(dict(landing_submitted(fleet, teams[b], b), frm=frm))
    outcomes += [landing_ended(fleet, label, p, a) for p in pending]
    missed = [b for b, landed in outcomes if not landed]
    if missed:
        print(f"{joined(missed)} did not land, as said above; " + (f"{joined([b for b, landed in outcomes if landed])} landed"
                                                                    if len(missed) < len(outcomes) else "none landed"), file=sys.stderr)
        raise Stopped(1)

# ---------------------------------------------------------------------------------------------------- units

def group_of(u):
    """Where a unit is, as an object: its bolt, or its kit's queue."""
    return f"bolt/{u.get('Bolt')}" if u.get("Bolt") else f"queue/{u.get('Repo')}"


def unit_stage(fleet, plan, name):
    u = plan.item(name)
    b = plan.bolt(u.get("Bolt")) if u.get("Bolt") else None
    return (stages_for(fleet, plan, [b]) if b else Stages(fleet, plan, {})).of(name)


# A moved unit's place, or a chore's (its kind the fifth word), rebased onto the bolt it moves to, its branch then
# tracking that bolt where it lives (the sixth word, bolt_upstream); UNREBASE puts it back, tracking the bolt it left.
REBASE = r"""cd "$1" || exit 1
branch="$5/$4"
orig=$(git rev-parse HEAD)
if git rebase -q --onto "bolt/$3" "bolt/$2" "$branch" >/dev/null 2>&1; then
  git branch -q --set-upstream-to="$6" "$branch"; echo "$orig"
else
  git rebase --abort >/dev/null 2>&1; exit 3
fi
"""
UNREBASE = r"""cd "$1" && git reset -q --hard "$2" && git branch -q --set-upstream-to="$6" "$5/$4" """

# Where a bolt lives, read in its kit's main checkout (BOLT_AT), for bolt_upstream.
BOLT_LIVES = r"""cd "$1" || exit 1
bolt=$2 file=$3
""" + BOLT_AT

# Whether a bolt's branch on the remote its host's tip names holds that tip (plan.19), read in its kit's main checkout
# with one fetch of it (plan.18), for kit.bolt_split: THERE=- when the remote has no bolt/<bolt>, READ with git's words
# when it can't be asked or fetched, else LOCAL and THERE, the host's commit and the remote's, HELD, yes when the
# host's tip is an ancestor of the remote's, and MERGES, the merges the host holds beyond it; and given the ref of the
# work to merge ($4), CARRIED, yes when the host's tip is an ancestor of it.
BOLT_SPLIT = r"""cd "$1" || exit 1
bolt=$2 remote=$3 work=${4:-}
l=$(git rev-parse --verify -q "refs/heads/bolt/$bolt^{commit}")
err=$(git ls-remote --exit-code "$remote" "refs/heads/bolt/$bolt" 2>&1); rc=$?
if [ $rc = 2 ]; then echo "THERE=-"; exit 0; fi
if [ $rc != 0 ]; then echo "READ=$(printf '%s' "$err" | tr '\n' ' ')"; exit 0; fi
if ! err=$(git fetch -q "$remote" "+refs/heads/bolt/$bolt:refs/remotes/$remote/bolt/$bolt" 2>&1); then
  echo "READ=$(printf '%s' "$err" | tr '\n' ' ')"; exit 0
fi
there=$(git rev-parse --verify -q "refs/remotes/$remote/bolt/$bolt^{commit}")
echo "LOCAL=$l"; echo "THERE=$there"
git merge-base --is-ancestor "$l" "$there" 2>/dev/null; case $? in 0) echo "HELD=yes" ;; 1) echo "HELD=no" ;; esac
echo "MERGES=$(git rev-list --count --merges "$there..$l" 2>/dev/null)"
[ -n "$work" ] || exit 0
git merge-base --is-ancestor "$l" "$work" 2>/dev/null; case $? in 0) echo "CARRIED=yes" ;; 1) echo "CARRIED=no" ;; esac
"""

# The bolt's two copies a landing reads (plan.19), in its kit's main checkout with $file the policy, with one fetch of
# the bolt from origin (plan.18), for kit.land_copies: THERE=- when the kit has no origin or origin has no
# bolt/<bolt>, fetching nothing; READ with git's words when origin can't be asked or fetched; else OWN, the host's own
# bolt/<bolt>, or - when it has none; THERE, origin's after the fetch; AT_THERE, the policy at it, base64, or - when it
# holds none, read as BOLT_AT reads one; HELD, yes when the host's copy is an ancestor of origin's or there is none;
# AHEAD, yes when origin's is an ancestor of the host's; LACKS, the merges the host's copy holds beyond origin's, and
# BEYOND, the merges origin's holds beyond the host's; AHEAD, LACKS and BEYOND each - when the host has no copy.
LAND_COPIES = r"""cd "$1" || exit 1
bolt=$2 file=$3
git remote get-url origin >/dev/null 2>&1 || { echo "THERE=-"; exit 0; }
err=$(git ls-remote --exit-code origin "refs/heads/bolt/$bolt" 2>&1); rc=$?
if [ $rc = 2 ]; then echo "THERE=-"; exit 0; fi
if [ $rc != 0 ]; then echo "READ=$(printf '%s' "$err" | tr '\n' ' ')"; exit 0; fi
if ! err=$(git fetch -q origin "+refs/heads/bolt/$bolt:refs/remotes/origin/bolt/$bolt" 2>&1); then
  echo "READ=$(printf '%s' "$err" | tr '\n' ' ')"; exit 0
fi
""" + REFS + r"""own=$(ref "refs/heads/bolt/$bolt") there=$(ref "refs/remotes/origin/bolt/$bolt")
echo "OWN=$own"; echo "THERE=$there"; echo "AT_THERE=$(pol "$there")"
if [ "$own" = - ]; then printf 'HELD=yes\nAHEAD=-\nLACKS=-\nBEYOND=-\n'; exit 0; fi
git merge-base --is-ancestor "$own" "$there" 2>/dev/null; case $? in 0) echo "HELD=yes" ;; 1) echo "HELD=no" ;; esac
git merge-base --is-ancestor "$there" "$own" 2>/dev/null; case $? in 0) echo "AHEAD=yes" ;; 1) echo "AHEAD=no" ;; esac
echo "LACKS=$(git rev-list --count --merges "$there..$own" 2>/dev/null)"
echo "BEYOND=$(git rev-list --count --merges "$own..$there" 2>/dev/null)"
"""


# Where a bolt lives (BOLT_LIVES), and AT_MAIN, the policy at the kit's main now as this host last fetched it, with no
# fetch (plan.18): origin/main for a kit with an origin, else its own main, base64, or - when it holds none.
BOLT_HOME = BOLT_LIVES + r"""now=refs/heads/main; if git remote get-url origin >/dev/null 2>&1; then now=refs/remotes/origin/main; fi
echo "AT_MAIN=$(pol "$(ref "$now")")"
"""


def bolt_local_said(bolt, lives, main_remote):
    """What a team's read says, once, of a bolt the team holds (plan.19, record 0032's amendment): that it is local
    until it lands, when it lives on its host only (lives None, kit.bolt_lives) while the policy at the kit's main now
    names a remote for its bolt branches (main_remote); else None, a bolt on GitHub, or every bolt local while main's
    policy names none. Nothing is run for it: sluice has no command that puts a local branch's tip on GitHub, and its
    landing's pull request puts it there."""
    if lives is None and main_remote:
        return (f"bolt/{bolt} is local until it lands: it was made before bolts were on GitHub, so its places are cut "
                "from the local branch, and its landing puts it on GitHub")
    return None


def bolts_local_said(fleet, t, plan):
    """The line a team's read says of each bolt the team holds that is local until it lands (bolt_local_said), read on
    the team's host in each bolt's kit (BOLT_HOME); a bolt whose home crew can't read says nothing."""
    out = []
    for b in held_by(plan, t["name"]):
        k = crew.with_kit(t, b.get("Repo"))
        r = crew.on_machine(fleet, k["machine"], ["bash", "-c", BOLT_HOME, "crew", k["kit"]["main"], b.name(), kit.DECLARATION])
        try:
            lives, main_remote = kit.bolt_home(r.stdout, b.name()) if r.returncode == 0 else (None, None)
        except Refusal:
            continue
        said = bolt_local_said(b.name(), lives, main_remote)
        if said:
            out.append(said)
    return out


def bolt_split_check(fleet, t, bolt, work=None):
    """What a merge into the bolt reads of a split (plan.19), on the team's host in the kit's main checkout: where the
    bolt lives (BOLT_LIVES), and when the host's own tip names a remote for it (kit.split_remote), that remote's copy
    after one fetch (BOLT_SPLIT), and given the ref of the work to merge, whether it holds the host's tip; (remote,
    kit.bolt_split's facts), or None when there is nothing to read, so a bolt whose tip names no remote fetches
    nothing."""
    remote = kit.split_remote(host_run(fleet, t["machine"], BOLT_LIVES, t["kit"]["main"], bolt, kit.DECLARATION), bolt)
    if not remote:
        return None
    return remote, kit.bolt_split(host_run(fleet, t["machine"], BOLT_SPLIT, t["kit"]["main"], bolt, remote,
                                           *([work] if work else [])), bolt)


def bolt_upstream(fleet, t, bolt):
    """The ref a place of the bolt tracks, read on the team's host where the bolt lives (kit.place_base, plan.19):
    origin/bolt/<bolt> for a bolt on GitHub, bolt/<bolt> for one made before gives went through sluice."""
    return kit.place_base(host_run(fleet, t["machine"], BOLT_LIVES, t["kit"]["main"], bolt, kit.DECLARATION), bolt)


# ------------------------------------------------------------------------------------------ who writes what

# The commands that write the plan directly, and the one role each agent crew started may use them in.
PLAN_WRITES = {("bolt", "new"), ("bolt", "give"), ("bolt", "order"), ("bolt", "drop"), ("bolt", "land"), ("unit", "add"),
               ("unit", "split"), ("unit", "amend"), ("unit", "order"), ("unit", "after"), ("unit", "move"), ("unit", "drop"),
               ("chore", "add"), ("chore", "order"), ("chore", "after"), ("chore", "move"), ("chore", "drop")}


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
        if name == f"{label}-operator" or name.startswith(f"{label}-operator-"):  # the latter, a host's before record 0035
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
    gives bolts; the main level's ops lands them. A chore's commands are written by the same hands as the unit's of the
    same name (plan.11). Any other plan write by an agent crew started is refused, naming the planner."""
    name = os.environ.get("CREW_AGENT")
    kind, of = role(fleet, name)
    if key not in PLAN_WRITES or kind == "user":
        return
    cmd, as_unit = " ".join(key), ("unit", key[1]) if key[0] == "chore" else key
    if kind == "planner":
        fail(f"the planner changes the plan through a proposal: crew plan propose, not crew {cmd}")
    if ((kind == "conductor" and as_unit in (("unit", "split"), ("unit", "order"), ("unit", "after")))
            or (kind == "design" and as_unit == ("unit", "add") and not a.bolt)
            or (kind == "dispatcher" and key == ("bolt", "give")) or (kind == "main-ops" and key == ("bolt", "land"))):
        return
    fail(f"{name} does not write the plan with crew {cmd}" + (" --bolt" if as_unit == ("unit", "add") and a.bolt else "")
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


class Reads:
    """How a plan command reads the kits: its units' stages, whether a change's name is free on a kit's main, and the
    first unit of a held bolt not yet merged. A command run directly or inside a proposal reads them; a proposal's
    card reads none (Drawn)."""
    w = None  # the write a command inside a proposal is applied to; a command run directly reads the branch's tip

    def stages(self, plan, bolts):
        return stages_for(self.fleet, plan, bolts)

    def stage(self, plan, name):
        return unit_stage(self.fleet, plan, name)

    def free(self, label, kit, names):
        name_free(self.fleet, label, kit, names)

    def first_open(self, plan, bolt):
        return first_open(self.fleet, plan, bolt)


class Direct(Reads):
    """What a command run directly sees: the plans of every partition, or of --label (or the agent's own)."""
    direct = True

    def __init__(self, fleet, a):
        self.fleet, self.label = fleet, default_label(fleet, a)

    def locate(self, kind, name, word=None):
        label, _, _, plan = locate(self.fleet, kind, name, self.label, word)
        return label, plan

    def kit(self, kit):
        return plan_for(self.fleet, kit, self.label)[0]


class Proposed(Reads):
    """What a command inside a proposal sees: the proposal's partition and number, in the plan as the commands before
    it in the proposal have left it."""
    direct = False

    def __init__(self, fleet, label, w, n):
        self.fleet, self.label, self.w, self.n = fleet, label, w, n

    def locate(self, kind, name, word=None):
        (self.w.plan.bolt(name) if kind == "Bolt" else self.w.plan.item(name)) or self.w.gone(kind, name, word)
        return self.label, self.w.plan

    def kit(self, kit):
        return plan_for(self.fleet, kit, self.label)[0]


class Drawn(Proposed):
    """What a command inside a proposal sees when the proposal's card is drawn: the plan as the commands before it have
    left it, and no kit (plan.12). No stage is known, so nothing is refused for one; a change's name is checked only
    for its form; and work a held bolt needs goes ahead of the bolt's first unit, merged or not. The approval reads the
    kits and checks them all."""
    UNREAD = {"stage": "unread", "worktree": None}

    def stages(self, plan, bolts):
        return self

    def of(self, name):
        return dict(self.UNREAD)

    def stage(self, plan, name):
        return dict(self.UNREAD)

    def free(self, label, kit, names):
        for n in names:
            crew.NAME.match(n) or fail(f"a unit's or chore's name is lowercase words with dashes, not {n}")

    def first_open(self, plan, bolt):
        return next((u.name() for u in plan.work_of(bolt)), None)


def first_open(fleet, plan, bolt):
    """The first unit or chore of a held bolt that has not merged into it: where work the bolt needs to land goes, ahead
    of what waits on it. None when every one has merged, or the bolt has none."""
    b = plan.bolt(bolt)
    st = stages_for(fleet, plan, [b])
    return next((u.name() for u in plan.work_of(bolt) if st.of(u.name())["stage"] not in ("merged", "landed")), None)


def unblocking(ctx, plan, label, a, into):
    """--unblocks <bolt>: the unit or chore is work a bolt a team holds needs before it can be proven or land. It goes
    into that bolt, ahead of what waits on it, never into the queue or another bolt. Returns what it goes ahead of."""
    into == a.unblocks or fail(f"{a.unit} unblocks bolt {a.unblocks}, so it goes into that bolt, ahead of what waits on it, "
                               f"not into {f'bolt {into}' if into else 'the queue'}")
    plan.bolt(a.unblocks).get("Team") or fail(f"{a.unit} unblocks bolt {a.unblocks}, which no team holds, so nothing waits on "
                                              "it: --unblocks names a bolt in flight")
    return ctx.first_open(plan, a.unblocks)


def kind_refusal(kind, cmd, sub, name):
    """Why a unit or chore command may not act on a record of the plan's Unit set (plan.11), or None: a unit command
    names a chore, or a chore command a unit, said with its kind and the command that takes it; and a chore is never
    split or amended, its words changing by a proposal that drops it and adds it again."""
    if kind == cmd:
        return None
    if kind == "chore" and sub in ("split", "amend"):
        return (f"{name} is a chore, which is never " + ("split" if sub == "split" else "amended")
                + ": a chore's words change by a proposal that drops it and adds it again (crew chore drop, crew chore add)")
    return f"{name} is a {kind}, not a {cmd}: crew {kind} {sub} acts on it"


def the_work(ctx, a):
    """The plan holding the unit or chore a command names (a.unit), as (label, plan), refused when it is of the other
    kind than the command (kind_refusal)."""
    label, plan = ctx.locate("Unit", a.unit, a.cmd)
    why = kind_refusal(kind_of(plan.item(a.unit)), a.cmd, a.sub, a.unit)
    not why or fail(why)
    return label, plan


def called(a):
    """How a write's subject names the unit or chore a command acts on: a unit by its name, a chore as `chore <name>`."""
    return f"chore {a.unit}" if a.cmd == "chore" else a.unit


def op_bolt_new(ctx, a):
    label = ctx.kit(a.repo)
    crew.NAME.match(a.bolt) or fail(f"a bolt's name is lowercase words with dashes, not {a.bolt}")
    why = kit_named(a.bolt, partition_kits(ctx.fleet, label), label)
    not why or fail(why)

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
    team = bolt_team(ctx.fleet, plan.bolt(a.bolt))
    if a.requeue and team:  # queued work has no worktree
        st = ctx.stages(plan, [plan.bolt(a.bolt)])
        for u in plan.work_of(a.bolt):
            s, k = st.of(u.name()), kind_of(u)
            s["stage"] != "unknown" or fail(f"cannot tell {k} {u.name()}'s stage: {s.get('why')}")
            not s["worktree"] or fail(f"{k} {u.name()} has a worktree at {s['worktree']}, and a queued {k} has none")

    def change(w):
        b = w.bolt(a.bolt)
        for u in w.plan.work_of(a.bolt):
            if a.requeue:
                u.drop("Bolt")
                u.drop("After")
                w.plan.place_last(u)
            else:
                w.plan.remove(u)
                w.on.append(f"{kind_of(u)}/{u.name()}")
        w.plan.remove(b)
        return [a.bolt]

    def after(repo, sha):  # the bolt's branch asked of sluice there, after its worktrees (plan.19, bolt_branch_asked)
        if team:
            tidy_after(ctx.fleet, team, f"bolt {a.bolt}", dropped=a.bolt)
    return Op(label, change, f"plan({a.bolt}): drop the bolt" + (", its units queued" if a.requeue else ""), "bolt.drop",
              on=[f"bolt/{a.bolt}"], body=a.reason, after=after)


def op_unit_add(ctx, a):
    """crew unit add, and crew chore add (a.cmd), whose record is marked Kind: chore (plan.11): the same flags, the same
    refusals and the same hands."""
    k = a.cmd
    label = ctx.label
    if a.bolt:
        label, plan = ctx.locate("Bolt", a.bolt)
        kit = plan.bolt(a.bolt).get("Repo")
        a.repo in (None, kit) or fail(f"bolt {a.bolt} is in {kit}, not {a.repo}")
    else:
        a.repo or fail(f"a {k} goes in a bolt (--bolt) or in a repo's queue (--repo)")
        label, kit, plan = ctx.kit(a.repo), a.repo, None
    ahead = unblocking(ctx, plan, label, a, a.bolt) if getattr(a, "unblocks", None) else None
    ctx.free(label, kit, [a.unit])
    sources = list(a.source)
    if a.signal:
        a.signal = signal_id(ctx.fleet, label, a.signal, ctx.w)  # a short id is routed, and sourced, by its full one
        sources.insert(0, f"signals/{a.signal}")

    def change(w):
        had = w.plan.item(a.unit)
        had is None or fail(f"{label}/main already has {kind_of(had)} {a.unit}")
        if a.bolt:
            w.bolt(a.bolt)
        if a.signal:  # its one move, route, in the same commit, checked again on each replay
            move(ctx.fleet, label, w, a.signal, route_move(a.signal, f"{k}/{a.unit}"))
        r = Rec("Unit", [("Unit", a.unit), ("Repo", kit)] + ([("Bolt", a.bolt)] if a.bolt else []) + ([("Kind", "chore")] if k == "chore" else [])
                + [("Intent", a.intent)] + [("After", x) for x in a.after] + [("Source", x) for x in sources])
        before = a.before or ahead
        o = w.plan.item(before) if before else None
        if a.before:
            o = w.item(a.before)
            o.get("Bolt") == a.bolt and o.get("Repo") == kit or fail(f"{kind_of(o)} {a.before} is not in {a.bolt or 'the queue of ' + kit}")
        if o is not None:
            w.plan.insert(r, before=o)
        else:
            w.plan.place_last(r)
        return [a.bolt] if a.bolt else []

    def after(repo, sha):
        if a.signal:
            print(f"signal {a.signal} routed to {k}/{a.unit}, in the same commit")
            record.emit(label, "signal.move", [f"signals/{a.signal}", f"{k}/{a.unit}"], commit=[f"{repo}@{sha}"],
                        why=f"signals({a.signal}): route to {k}/{a.unit}")
    return Op(label, change, f"plan({a.bolt or 'queue'}): add {called(a)}", f"{k}.add",
              on=[f"{k}/{a.unit}", f"bolt/{a.bolt}" if a.bolt else f"queue/{kit}"], frm=[f"signals/{a.signal}"] if a.signal else [], after=after)


def conductor_scope(ctx, plan, a):
    """A conductor narrows, orders and sets dependencies only within the bolt its team holds, of units and chores alike."""
    kind, team = role(ctx.fleet, os.environ.get("CREW_AGENT"))
    if ctx.direct and kind == "conductor":
        b = plan.item(a.unit).get("Bolt")
        b and plan.bolt(b).get("Team") == team or fail(
            f"{team}-conductor writes only units and chores of the bolt {team} holds, and {a.unit} is in {f'bolt {b}' if b else 'the queue'}: "
            f"tell {ctx.fleet['teams'][team]['label']}-planner")


def op_unit_split(ctx, a):
    label, plan = the_work(ctx, a)
    conductor_scope(ctx, plan, a)
    s = ctx.stage(plan, a.unit)
    s["stage"] not in LATER or fail(f"unit {a.unit} is in {s['stage']}, so it is no longer split; add the remainder as a new unit instead (crew unit add)")
    s["stage"] != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    ctx.free(label, plan.unit(a.unit).get("Repo"), [n for n, _ in a.into])
    bolt = plan.unit(a.unit).get("Bolt")

    def change(w):
        u = w.of(a)
        u.set("Intent", a.intent)
        prev = u
        for n, intent in a.into:
            had = w.plan.item(n)
            had is None or fail(f"{label}/main already has {kind_of(had)} {n}")
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
    amendment hands its construct to its team's host, in the name of whoever applied it (construct_hand): the command
    answers once the host has it, and the host starts construct again, ending the unit's agent when it is past
    construct, and tells the conductor what started or why nothing did (plan.15, code.9). A host that does not answer
    is told to the conductor from here. Merged work is not amended, and a chore never is (plan.11)."""
    label, plan = the_work(ctx, a)
    s = ctx.stage(plan, a.unit)
    s["stage"] not in ("merged", "landed") or fail(
        f"unit {a.unit} has " + ("merged into its bolt" if s["stage"] == "merged" else "landed on main")
        + ", so it is not amended: a defect in it is a fix, and new work is a new unit")
    s["stage"] != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    bolt = plan.unit(a.unit).get("Bolt")
    team = bolt_team(ctx.fleet, plan.bolt(bolt)) if bolt else None
    mark = (f"proposal/{ctx.n}" if not ctx.direct else "intent") if s["worktree"] else None

    def change(w):
        u = w.of(a)
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
        r = crew.on_machine(ctx.fleet, team["machine"],
                            crew.crew_argv(ctx.fleet, team["machine"], *construct_again(team["name"], a.unit, s["stage"], by)))
        said = (r.stdout + r.stderr).strip()
        if said:
            print(said)
        if r.returncode:
            why = (crew.unanswered(team["machine"], r)
                   or ((r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1].rstrip("."))
            print(f"construct did not start on unit {a.unit}: {why}")
            amend_tell(ctx.fleet, team["name"], *amend_told(a.unit, by, None, why))
    return Op(label, change, f"plan({bolt or 'queue'}): amend {a.unit}", "unit.amend", on=[f"unit/{a.unit}"], after=after)


def construct_again(team, unit, stage, by):
    """The crew command an amendment runs on its team's host (plan.15, code.9): construct on the unit handed to that
    host (construct_hand), in the name of what amended it (by), ending its agent where it stands when the unit is past
    construct, since that agent works to the old intent; a construct still writing the change is not ended, and the
    unit's corrections wait until it settles (briefs.5)."""
    return ["_construct-again", team, unit, "--by", by] + (["--force"] if stage != "construct" else [])


def amend_tell(fleet, team, text, unsaid):
    """An amendment's word to its team's conductor (amend_told), or what crew says when the conductor is not up."""
    conductor = f"{team}-conductor"
    if not crew.tell(fleet, conductor, text):
        print(f"{conductor} is not up: {unsaid}")


# How long a handed construct's process has to name itself in its marker before crew takes it as never started.
HAND_NAMED = 60


def handed_state(unit, marker, alive, now):
    """Where a construct an amendment handed to the team's host stands (plan.15), from its marker (None when nothing
    was handed, or once it started), whether the process it names is alive, and the time now: (None, None) when nothing
    is handed; ("failed", why) when it could not start; ("starting", what) while it starts, or for HAND_NAMED seconds
    from the hand-off before its process has named itself; ("gone", what) when its process ended, or never named
    itself, without saying either."""
    if marker is None:
        return None, None
    if marker.get("failed"):
        return "failed", f"construct did not start on unit {unit}: {marker['failed']}"
    if alive or ("pid" not in marker and now - marker.get("at", 0) < HAND_NAMED):
        return "starting", f"construct on unit {unit} is starting on this host, handed there by {marker.get('by', 'an amendment')}"
    return "gone", (f"construct handed to this host for unit {unit} ended before it said whether it started (its words are in "
                    f"{marker.get('log', 'its log')}): crew unit run {unit} construct runs it")


def amend_told(unit, by, slot, why=None):
    """What an amendment tells the conductor of the unit's team, and what crew says when the conductor is not up
    (plan.15): construct runs again in the slot that started it, or did not start, and why."""
    if slot:
        return (f"Unit {unit}'s intent was amended by {by}, and construct runs again on it in {slot}: wait for it "
                f"(crew unit wait {unit}); once it has committed, the unit goes on from its tasks.",
                f"construct runs again on unit {unit} in {slot}")
    return (f"Unit {unit}'s intent was amended by {by}, and construct did not start: {why}. Run it once it can "
            f"(crew unit run {unit} construct); once it has committed, the unit goes on from its tasks.",
            f"unit {unit} waits, amended, for construct to be run again")


def op_unit_order(ctx, a):
    label, plan = the_work(ctx, a)
    conductor_scope(ctx, plan, a)
    u0, k = plan.item(a.unit), a.cmd

    def change(w):
        u = w.of(a)
        g = w.plan.group(u)
        if a.first:
            w.plan.insert(u, before=g[0]) if g[0] is not u else None
        elif a.last:
            w.plan.insert(u, after=g[-1]) if g[-1] is not u else None
        else:
            o = w.item(a.before)
            o is not u or fail(f"a {k} can't go before itself")
            o in g or fail(f"{kind_of(o)} {a.before} is not in {u.get('Bolt') or 'the queue'} with {a.unit}")
            w.plan.insert(u, before=o)
        return [u.get("Bolt")] if u.get("Bolt") else []
    where = "first" if a.first else "last" if a.last else f"before {a.before}"
    return Op(label, change, f"plan({u0.get('Bolt') or 'queue'}): order {called(a)} {where}", f"{k}.order",
              on=[f"{k}/{a.unit}", group_of(u0)])


def op_unit_after(ctx, a):
    label, plan = the_work(ctx, a)
    conductor_scope(ctx, plan, a)
    a.none or a.deps or fail("name the units or chores it comes after, or --none")
    u0, k = plan.item(a.unit), a.cmd

    def change(w):
        u = w.of(a)
        if a.none:
            u.drop("After")
        for d in a.deps:
            w.item(d)
            d != a.unit or fail(f"a {k} can't come after itself")
            if d not in u.all("After"):
                u.add("After", d, after="Intent")
        return [u.get("Bolt")] if u.get("Bolt") else []
    what = "after nothing" if a.none else "after " + ", ".join(a.deps)
    return Op(label, change, f"plan({u0.get('Bolt') or 'queue'}): {called(a)} {what}", f"{k}.after",
              on=[f"{k}/{a.unit}", group_of(u0)])


def op_unit_move(ctx, a):
    label, plan = the_work(ctx, a)
    u, k = plan.item(a.unit), a.cmd
    src, to = u.get("Bolt"), None if a.bolt == "queue" else a.bolt
    to != src or fail(f"{k} {a.unit} is already in {src or 'the queue'}")
    if to:
        tb = plan.bolt(to) or fail(f"no bolt {to} in {label}/main of {state_of(ctx.fleet, label)[0]}")
        tb.get("Repo") == u.get("Repo") or fail(f"bolt {to} is in {tb.get('Repo')}; a {k} moves only between bolts of its own repo, {u.get('Repo')}")
    ahead = unblocking(ctx, plan, label, a, to) if getattr(a, "unblocks", None) else None
    s = ctx.stage(plan, a.unit)
    s["stage"] not in ("merged", "landed") or fail(f"{k} {a.unit} has merged into {src}, so it can't move")
    s["stage"] != "unknown" or s.get("place_unread") or fail(f"cannot tell {k} {a.unit}'s stage: {s.get('why')}")
    prepare = None
    # A place that tracks a bolt crew cannot read is not rebased: it is left on the bolt it tracks, which the work has
    # then left, so the tidy removes it and its next stage cuts its place from bolt/<to> (left_refusal).
    if s["worktree"] and not s.get("place_unread"):
        to or fail(f"{k} {a.unit} has a worktree at {s['worktree']}, and a queued {k} has none")
        ft, tt = bolt_team(ctx.fleet, plan.bolt(src)), bolt_team(ctx.fleet, plan.bolt(to))
        tt or fail(f"bolt {to} is held by no team, so it has no branch to rebase {a.unit} onto")
        (ft["machine"], ft["kit"]["main"]) == (tt["machine"], tt["kit"]["main"]) or fail(
            f"bolt {to} is built in {tt['kit']['main']} on {tt['machine']}, not in {a.unit}'s checkout; a {k} with a worktree moves only within it")

        def prepare():
            ups = {b: bolt_upstream(ctx.fleet, ft, b) for b in (src, to)}
            r = crew.on_machine(ctx.fleet, ft["machine"], ["bash", "-c", REBASE, "crew", s["worktree"], src, to, a.unit, k, ups[to]])
            READ.drop_kit(ft["machine"], ft["kit"]["main"])
            r.returncode != 3 or fail(f"rebasing {a.unit} onto bolt/{to} conflicts: the move is abandoned and the plan is unchanged")
            r.returncode == 0 or fail(f"rebasing {a.unit} on {ft['machine']} failed: {r.stderr.strip()}")
            orig = r.stdout.strip()

            def undo():
                crew.on_machine(ctx.fleet, ft["machine"], ["bash", "-c", UNREBASE, "crew", s["worktree"], orig, src, a.unit, k, ups[src]])
                READ.drop_kit(ft["machine"], ft["kit"]["main"])
            return undo

    def change(w):
        u = w.of(a)
        u.get("Bolt") == src or fail(f"{k} {a.unit} moved to {u.get('Bolt') or 'the queue'} meanwhile")
        u.drop("After")
        if to:
            w.bolt(to)
            u.set("Bolt", to, after="Repo")
        else:
            u.drop("Bolt")
        o = w.plan.item(ahead) if ahead else None
        if o is not None and o is not u and o.get("Bolt") == to:
            w.plan.insert(u, before=o)
        else:
            w.plan.place_last(u)
        return [b for b in (src, to) if b]
    kit = u.get("Repo")
    return Op(label, change, f"plan({to or 'queue'}): move {called(a)} from {src or 'the queue'}", f"{k}.move",
              on=[f"{k}/{a.unit}", f"bolt/{to}" if to else f"queue/{kit}"], frm=[f"bolt/{src}" if src else f"queue/{kit}"], prepare=prepare)


def op_unit_drop(ctx, a):
    label, plan = the_work(ctx, a)
    k = a.cmd
    s = ctx.stage(plan, a.unit)
    s["stage"] not in ("merged", "landed") or fail(f"{k} {a.unit} has merged into its bolt, so it can't be dropped")
    # A stage unknown only for its place is not merged: the drop goes, and the tidy after it removes that place.
    s["stage"] != "unknown" or s.get("place_unread") or fail(f"cannot tell {k} {a.unit}'s stage: {s.get('why')}")
    u0 = plan.item(a.unit)
    bolt = u0.get("Bolt")
    team = bolt_team(ctx.fleet, plan.bolt(bolt)) if bolt else None

    def change(w):
        u = w.of(a)
        for o in w.plan.group(u):
            if a.unit in o.all("After"):
                o.fields = [(n, v) for n, v in o.fields if not (n == "After" and v == a.unit)]
        w.plan.remove(u)
        return [bolt] if bolt else []

    def after(repo, sha):
        if team:
            tidy_after(ctx.fleet, team, f"{k} {a.unit}")
        elif s["worktree"]:
            print(f"its worktree stays at {s['worktree']}, on {k}/{a.unit}")
    return Op(label, change, f"plan({bolt or 'queue'}): drop {called(a)}", f"{k}.drop", on=[f"{k}/{a.unit}", group_of(u0)],
              body=a.reason, after=after)


# The fifteen commands a proposal may hold, each built the same way whether run directly or inside a proposal. A chore's
# five are a unit's, the kind read from the command (plan.11).
OPS = {
    ("bolt", "new"): op_bolt_new, ("bolt", "order"): op_bolt_order, ("bolt", "drop"): op_bolt_drop,
    ("unit", "add"): op_unit_add, ("unit", "split"): op_unit_split, ("unit", "amend"): op_unit_amend, ("unit", "order"): op_unit_order,
    ("unit", "after"): op_unit_after, ("unit", "move"): op_unit_move, ("unit", "drop"): op_unit_drop,
    ("chore", "add"): op_unit_add, ("chore", "order"): op_unit_order, ("chore", "after"): op_unit_after, ("chore", "move"): op_unit_move,
    ("chore", "drop"): op_unit_drop,
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
%allowed: Proposal Case Do Agreed State Opened By Closed Reason Replaces Cleared
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
    """Every bolt, unit and chore a proposal's commands name, as run-record objects, in order and once each."""
    out = []
    for a in argvs:
        if a.cmd == "bolt":
            out.append(f"bolt/{a.bolt}")
        else:
            out.append(f"{a.cmd}/{a.unit}")
            out += [f"unit/{n}" for n, _ in getattr(a, "into", None) or []]
            if a.sub == "add" and a.bolt:
                out.append(f"bolt/{a.bolt}")
            if a.sub == "move" and a.bolt != "queue":
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
    # A chore's command is said as the unit's, its name as `chore <name>`.
    return ", ".join(words[("unit", a.sub)](argparse.Namespace(**dict(vars(a), unit=called(a)))) if a.cmd == "chore"
                     else words[(a.cmd, a.sub)](a) for a in argvs)


def touched_by(plan, argvs):
    """The bolts each of a proposal's commands touches, read from the plan and the commands alone (no kit is read): a
    unit's or chore's add's bolt; the bolt a unit or chore leaves and the one it joins; the bolt of a unit split, or of
    a unit or chore ordered, given what it comes after, amended or dropped; the bolt of a bolt order or drop. A bolt new
    touches none."""
    where = {u.name(): u.get("Bolt") for u in plan.work()}
    out = []
    for a in argvs:
        key, t = ("unit" if a.cmd == "chore" else a.cmd, a.sub), []
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
            refuse(*command_refused(a, e))
        op.added_on, op.added_frm = w.on[n_on:], w.frm[n_frm:]
        ops.append(op)
    return ops, list(dict.fromkeys(told))


def command_refused(a, e):
    """A proposal's command refused, as said, its line as typed, and as recorded, its command and the names it acts on
    with no intent or reason typed in it (record.3)."""
    return f"`{a.do}`: {e}", f"`{do_named(a)}`: {getattr(e, 'recorded', None) or e}"


def check_ops(fleet, label, w, argvs, n, seen=Proposed):
    """Proposal n's commands applied in order to a copy of the plan and of the files they change: every refusal and
    rule each has when run directly, the schema's and crew's own rules included. Returns the copy, which a proposal's
    card draws (seen=Drawn, which reads no kit) and nothing writes."""
    scratch = Write(w.repo, label, w.tip, Plan(w.plan.text()))
    scratch.files = dict(w.files)
    for a in argvs:
        try:
            OPS[(a.cmd, a.sub)](seen(fleet, label, scratch, n), a).change(scratch)
        except Refusal as e:
            refuse(*command_refused(a, e))
    try:
        check(scratch.plan)
        checked({"plan.rec": scratch.plan.text(), **scratch.files})
    except Refusal as e:
        fail(f"the proposal as a whole: {e}")
    return scratch


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


# A decision record a source names by its path (plan-proposals): docs/adr/ and its four digits, the repository's when
# <owner>/<name> and a colon or a space come right before it. The lookbehinds keep a path's tail from reading as a
# repository, and other/docs/adr/ from reading as a record.
RECORD_REF = re.compile(r"(?:(?<![\w./-])([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)[:\s])?(?<![\w./-])docs/adr/(\d{4})(?!\d)")
UNACCEPTED = "crew refuses the proposal: it rests on records the user has not accepted."
UNACCEPTED_AFTER = "Propose it once each record is accepted on its kit's main."


def record_refs(source, kit_repo):
    """The decision records a source names, [(repo, number)] in the order they appear and each once: each by its path
    (RECORD_REF), of the repository written before it, else of kit_repo, the repository of the kit whose work names it.
    A record named only in words ("record 0026") is no record here, since nothing in the words says whose it is."""
    return list(dict.fromkeys((m.group(1) or kit_repo, int(m.group(2))) for m in RECORD_REF.finditer(source)))


def record_items(fleet, label, plan, argvs):
    """The records a proposal's new work names (plan-proposals, briefs.15): for each bolt its `bolt new`s create, then
    each unit or chore it makes new to a bolt or the queue (new_units), as the plan its commands leave holds them, each
    record its sources name (record_refs), as (kind, name, kit, repo, number): kit the record's kit as a refusal names
    it, the work's kit by its name, or <owner>/<name> when the record is another repository's, and repo the repository
    it is read in, from the teams file (code.5). Work whose sources name a record and whose kit no team of the partition
    builds is refused, since crew can't tell whose records they are (read.1)."""
    work = [("bolt", a.bolt, plan.bolt(a.bolt)) for a in argvs if (a.cmd, a.sub) == ("bolt", "new")]
    work += [(kind_of(plan.item(u)) if plan.item(u) else "unit", u, plan.item(u)) for u in new_units(argvs)]
    out = []
    for kind, name, r in work:
        sources = [s for s in (r.all("Source") if r else []) if RECORD_REF.search(s)]
        if not sources:
            continue
        kit = r.get("Repo")
        teams = kit_teams(fleet, kit, label)
        teams or fail(f"{kind} {name} names a decision record, and no team of {label} builds {kit}, so crew can't tell whose it is")
        k = next(k for k in crew.kits_of(teams[0]) if kit in (k.get("name"), k.get("repo")))
        for s in sources:
            out += [(kind, name, k["name"] if repo == k["repo"] else repo, repo, n) for repo, n in record_refs(s, k["repo"])]
    return list(dict.fromkeys(out))


def unaccepted(items, held):
    """Why a proposal can't be written because its new work rests on records the user has not accepted, or None when
    every one is (plan-proposals, roles.3 on briefs.15): one line for each item, (kind, name, kit, repo, number) as
    record_items gives them, whose record its main does not hold accepted, saying what it holds, read from held, which
    maps (repo, number) to the files main holds by that number with the one file's status and whether an amendment is
    marked proposed ({"files", "status", "marked"}), or to why it could not be read ({"why"}, read.1)."""
    lines = []
    for kind, name, kit, repo, number in items:
        h, n = held[(repo, number)], f"{number:04d}"
        if "why" in h:
            says = h["why"]
        elif not h["files"]:
            says = f"{kit}'s main holds no record {n} in docs/adr/"
        elif len(h["files"]) > 1:
            says = f"{kit}'s main holds {len(h['files'])} records numbered {n}: {', '.join(h['files'])}"
        elif record_accepted(h["status"], h["marked"]):
            continue
        else:
            says = f"{kit}'s main holds it " + ("" if h["status"] else "with ") + record_says(h["status"], h["marked"])
        lines.append(f"  {kind} {name} names record {n} of {kit}: {says}")
    return "\n".join([UNACCEPTED, *lines, UNACCEPTED_AFTER]) if lines else None


def proposal_records(fleet, label, scratch, argvs):
    """The records a proposal's new work names, read on each repository's main as GitHub holds it now (plan.18): the
    items record_items finds in the plan its commands leave (scratch), and what each repository's main holds by each
    number, for unaccepted. Each repository is fetched once into crew's cache, held for the command (plan.12), its
    docs/adr/ listed at that tip and the one file by a number read; a main that can't be fetched, or a file that can't
    be read as text, gives why, naming it (read.1, read.2). Returns (items, held)."""
    items, held = record_items(fleet, label, scratch.plan, argvs), {}
    for repo in dict.fromkeys(i[3] for i in items):
        numbers = sorted({i[4] for i in items if i[3] == repo})
        try:
            tip = fetch(repo, "main")
            listed = git(repo, "ls-tree", "--name-only", tip, "docs/adr/").splitlines() if tip else []
        except Refusal as e:
            held.update({(repo, n): {"why": str(e)} for n in numbers})
            continue
        for n in numbers:
            if not tip:
                held[(repo, n)] = {"why": f"{repo} has no main on GitHub"}
                continue
            files = [f for f in listed if re.fullmatch(rf"docs/adr/{n:04d}-[^/]*\.md", f)]
            held[(repo, n)] = {"files": files, "status": "", "marked": False}
            if len(files) != 1:
                continue
            try:
                text = show(repo, tip, files[0])
            except UnicodeDecodeError:
                text = None
            if text is None:
                held[(repo, n)] = {"why": f"crew can't read {files[0]} on {repo}'s main at {tip[:7]} as text"}
                continue
            status, marked = record_status_held(text)
            held[(repo, n)].update(status=status, marked=bool(marked))
    return items, held


def plan_propose(fleet, a):
    """crew plan propose <file> [--replaces <n>]: the planner's proposal, checked against the plan at the tip, written
    open with the next number; the conductor of each bolt in flight it touches is told. Refused, with nothing written,
    when a bolt it creates, or a unit or chore it adds or moves into a bolt, names a decision record its main on GitHub
    does not hold accepted (proposal_records, unaccepted). Once it is written, crew raises its card in the planner's
    name, or, for a rewrite, changes its chain's card in place (raise_proposal_at)."""
    kind, of = role(fleet, os.environ.get("CREW_AGENT"))
    kind in ("planner", "user") or fail(proposer_refusal(fleet, os.environ.get("CREW_AGENT"), kind, of))
    label = of if kind == "planner" else proposal_label(fleet, a)
    a.label in (None, label) or fail(f"{label}-planner proposes for {label}, not {a.label}")
    CONTEXT["label"] = label
    case, dos = read_proposal_file(a.file)
    argvs = [do_args(label, d) for d in dos]
    seen = {}

    def change(w):
        pl = proposals(w)
        n = next_proposal(pl)
        scratch = check_ops(fleet, label, w, argvs, n)
        said = unaccepted(*proposal_records(fleet, label, scratch, argvs))
        not said or fail(said)
        per = touched_by(w.plan, argvs)
        seen["old_by"] = open_proposal(pl, n, case, dos, agent(), datetime.date.today().isoformat(), a.replaces, label)
        w.replace("proposals.rec", pl.text())
        w.subject = f"plan(proposal {n}): propose: {summary(argvs)}"
        w.on += [f"proposal/{n}"] + objects(argvs) + ([f"proposal/{a.replaces}"] if a.replaces else [])
        seen.update(n=n, per=per, w=w, held={b: w.plan.bolt(b).get("Team") for b in flat(per) if w.plan.bolt(b) and w.plan.bolt(b).get("Team")})
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
    if kind != "planner" and a.replaces and seen.get("old_by") == f"{label}-planner":
        tell_planner(fleet, label, f"Proposal {a.replaces} was replaced by proposal {n}, by {agent()}.")
    raise_proposal_at(fleet, label, seen["w"], n, "replace" if a.replaces else "propose")


def proposer_refusal(fleet, name, kind, of):
    """Why an agent may not propose (roles.1): only the planner and the user write proposals."""
    return f"{name} does not write proposals: tell {planner_of(fleet, kind, of)}, who proposes changes to the plan"


def next_proposal(pl):
    """The number a new proposal takes: one past the highest, never reused (plan.4)."""
    return 1 + max([int(p.get("Proposal")) for p in pl.recs("Proposal")] or [0])


def open_proposal(pl, n, case, dos, by, today, replaces=None, label=None):
    """Proposal n written open in proposals.rec (pl), its case and commands as given (plan.4); one it replaces, which
    must be open, is dropped with the reason that it was replaced, and agreements stay with it. Returns who wrote the
    one replaced."""
    old_by = None
    if replaces:
        old = proposal(pl, replaces, label)
        old.get("State") == "open" or fail(f"proposal {replaces} is {old.get('State')}, so nothing replaces it")
        old_by = old.get("By")
        old.set("State", "dropped")
        old.set("Closed", today, after="By")
        old.set("Reason", f"replaced by proposal {n}", after="Closed")
    pl.insert(Rec("Proposal", [("Proposal", str(n)), ("Case", case)] + [("Do", d) for d in dos]
                  + [("State", "open"), ("Opened", today), ("By", by)] + ([("Replaces", str(replaces))] if replaces else [])))
    return old_by


def proposal_chain(pl, n):
    """Proposal n's chain in proposals.rec (pl), its first to n: each proposal it replaces, followed back by Replaces.
    The chain is one card, keyed by its first, proposal/<first> (record 0031 §1)."""
    out = [n]
    while True:
        p = next((p for p in pl.recs("Proposal") if p.get("Proposal") == str(out[0])), None)
        back = int(p.get("Replaces")) if p is not None and (p.get("Replaces") or "").isdigit() else None
        if back is None or back in out:
            return out
        out.insert(0, back)


def agreements_wanted(plan, argvs, p, n, kind, of, team=None, name=None):
    """The teams whose agreement this caller records on proposal n, those it touches that have not agreed (plan.4): a
    conductor's own team, which must hold a bolt the proposal touches; the user's, any team named, or every team the
    proposal touches. Only a conductor or the user agrees."""
    kind in ("conductor", "user") or fail(f"{name} does not agree to proposals: the conductor of a bolt a proposal touches agrees to it")
    held = held_teams(plan, flat(touched_by(plan, argvs)))
    if kind == "conductor":
        of in held or fail(f"proposal {n} touches no bolt {of} holds" + (f": it touches the bolts of {', '.join(held)}" if held else ""))
        want = [of]
    else:
        team is None or team in held or fail(f"proposal {n} touches no bolt {team} holds")
        want = [team] if team else held
    return [t for t in want if t not in p.all("Agreed")]


def agreement_missing(plan, argvs, p, n):
    """Why proposal n can't be approved yet, or None: the conductor of a bolt it touches, held now, has not agreed."""
    missing = [t for t in held_teams(plan, flat(touched_by(plan, argvs))) if t not in p.all("Agreed")]
    return (f"proposal {n} waits on the agreement of " + ", ".join(f"{t}-conductor" for t in missing) + f": crew plan agree {n}"
            if missing else None)


def closed_refusal(p, n):
    """Why proposal n can't be approved because it is closed, said with its reason and recorded without it (record.3),
    or None while it is open."""
    if p.get("State") == "open":
        return None
    state = f"proposal {n} is {p.get('State')}"
    return state + (f": {p.get('Reason')}" if p.get("Reason") else ""), state


def agree_closed(p, n):
    """What crew answers an agreement to proposal n with when the plan as it stands once the agreement is written
    shows the proposal (p) closed: that it is closed and how, approved or dropped with its reason, and that crew raises
    no card for it and changes none, since the agreement's write still showed it open and a card raised from that
    would reach the user in the planner's name for a closed proposal (wldn's proposal 553 on 2026-10-24: swb-1 agreed
    at 35d07471, the planner dropped it at bc2c3b1 four seconds on, and the agreement then posted its card again until
    the rail's sweep withdrew it; signal 2026-10-24-swancloud-planner-04891322/01). None while it is open."""
    why = closed_refusal(p, n)
    if why is None:
        return None
    return why[0] + ("" if why[0][-1:] in ".!?" else ".") + " It is closed, so crew raises no card for it and changes none."


def close(p, state, today, reason=None, cleared=()):
    """A proposal closed: approved, with each new unit the user left out of the change as Cleared, or dropped with its
    reason; one that is not open is refused, saying what it is (plan.4)."""
    p.get("State") == "open" or fail(f"proposal {p.get('Proposal')} is {p.get('State')}, so it can't be " + (
        "dropped" if state == "dropped" else "approved"))
    p.set("State", state)
    p.set("Closed", today, after="By")
    if reason:
        p.set("Reason", reason, after="Closed")
    for u in cleared:
        p.add("Cleared", u, after="Closed")


def plan_agree(fleet, a):
    """crew plan agree <n> [--team <team>]: the conductor's recorded agreement to a proposal that touches the bolt its
    team holds; the user may agree for any team the proposal touches."""
    label = proposal_label(fleet, a, a.n)
    CONTEXT["label"] = label
    name = os.environ.get("CREW_AGENT")
    kind, of = role(fleet, name)
    w0, _, p0, argvs = at_tip(fleet, label, a.n)
    p0.get("State") == "open" or fail(f"proposal {a.n} is {p0.get('State')}, so there is nothing to agree to")
    wanted = lambda w, p: agreements_wanted(w.plan, argvs, p, a.n, kind, of, a.team, name)
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
        seen.update(new=new, w=w)
        return []
    write(fleet, label, change, "plan: agree", act="plan.agree")
    tell_planner(fleet, label, f"{', '.join(seen['new'])} agree{'s' if len(seen['new']) == 1 else ''} to proposal {a.n}.")
    raise_agreed(fleet, label, a.n, seen["new"])


def raise_agreed(fleet, label, n, agreed, acts=None):
    """Proposal n's card once the agreements of the teams agreed are written (raise_proposal_at, agree), raised on the
    plan as it stands, the branch's tip fetched anew: an approval or a drop can land between the agreement's write and
    its raise, so a proposal the tip shows closed raises no card and changes none, and the agreement answers that it is
    closed and how (agree_closed). The fetch is the one past the command's first (plan.12), as the sweep's raise makes
    (raise_proposal). The card's id, or None."""
    w = tip_write(fleet, label, fresh=True)
    closed = agree_closed(proposal(proposals(w), n, label), n)
    if closed:
        print(closed)
        return None
    return raise_proposal_at(fleet, label, w, n, "agree", acts, agreed=agreed)


def plan_approve(fleet, a):
    """crew plan approve <n> [--clear <unit>...]: the proposal's commands applied in order to the plan at the tip, and
    the proposal closed as approved, in one commit; refused, with nothing changed, when a command no longer applies or
    a conductor whose bolt it touches has not agreed. A rebase it prepares is undone if the approval is refused. With
    --clear, the commands that concern only the units the user left out are not applied, a command left in that names
    one refuses the whole, and the proposal records each as Cleared (plan.3). Then crew closes the proposal's card with
    what was applied, and the planner is told it when someone else approved (raise_proposal_at)."""
    label = proposal_label(fleet, a, a.n)
    CONTEXT["label"] = label
    w0, _, p0, argvs = at_tip(fleet, label, a.n)
    repo = w0.repo
    cleared = list(dict.fromkeys(getattr(a, "clear", None) or []))

    def agreed(w, p):
        why = agreement_missing(w.plan, argvs, p, a.n)
        not why or fail(why)

    def opened(p):
        why = closed_refusal(p, a.n)
        not why or refuse(*why)
    opened(p0)
    agreed(w0, p0)
    applied = kept(argvs, cleared, a.n)
    ops0 = apply_all(fleet, label, w0, applied, a.n)[0]  # checked at the tip, to know what to prepare
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
            ops, told = apply_all(fleet, label, w, applied, a.n)
            if cleared:  # a branch's proposals.rec keeps the descriptor it was made with, from before Cleared
                in_step(pl, PROPOSALS)
            close(p, "approved", datetime.date.today().isoformat(), cleared=cleared)
            w.replace("proposals.rec", pl.text())
            w.subject = f"plan(proposal {a.n}): approve: {summary(applied) or 'nothing applied'}"
            w.on += [f"proposal/{a.n}"] + objects(argvs)
            seen.update(ops=ops, w=w)
            return told
        body = f"Left out: {', '.join(cleared)}" if cleared else ""
        sha = write(fleet, label, change, "plan: approve", body, act="plan.approve")
    except Refusal:
        for undo in reversed([u for u in undos if u]):
            undo()
        raise
    for op in seen["ops"]:
        record.emit(label, op.act, op.on + op.added_on, op.frm + op.added_frm + [f"proposal/{a.n}"], [f"{repo}@{sha}"],
                    record.subject(op.subject))
        if op.after:
            op.after(repo, sha)
    print(f"proposal {a.n} is approved and applied" + (f", without {joined(cleared)}" if cleared else ""))
    words = approved_words(applied, cleared)
    if p0.get("By") == f"{label}-planner":
        tell_planner(fleet, label, f"Proposal {a.n} was approved by {agent()}. {words}")
    raise_proposal_at(fleet, label, seen["w"], a.n, "approve", outcome=words)


def plan_drop(fleet, a):
    """crew plan drop <n> "<reason>": an open proposal closed unapplied, with the reason kept whole on its record; the
    planner is told when someone else dropped it, and crew withdraws its card with the reason, or acks it, once the
    user answered it, as dropped on their note (raise_proposal_at, DROPPED)."""
    label = proposal_label(fleet, a, a.n)
    CONTEXT["label"] = label

    def change(w):
        pl = proposals(w)
        p = proposal(pl, a.n, label)
        argvs = [do_args(label, d) for d in p.all("Do")]
        close(p, "dropped", datetime.date.today().isoformat(), a.reason)
        w.replace("proposals.rec", pl.text())
        w.subject = f"plan(proposal {a.n}): drop"
        w.on += [f"proposal/{a.n}"] + objects(argvs)
        seen["w"] = w
        return []
    seen = {}
    write(fleet, label, change, "plan: drop", a.reason, act="plan.drop")
    said = f"Proposal {a.n} was dropped by {agent()}: {a.reason.strip()}"
    tell_planner(fleet, label, said + ("" if said[-1:] in ".!?" else "."))
    raise_proposal_at(fleet, label, seen["w"], a.n, "drop", reason=a.reason.strip())


def signal_text(fleet, label, sig):
    """A signal's assertion, its excerpt and the excerpt's grade where its capture has one, from whichever home holds
    it, for a proposal's page."""
    try:
        hit = signal_at(fleet, label, sig)
    except Refusal:
        return None, None, None
    if not hit:
        return None, None, None
    _, repo, tip, text, sig = hit
    return (*asserted(text), field(show(repo, tip, capture_of(sig)) or "", "excerpt"))


def asserted(text):
    """A signal's assertion and its quoted excerpt, the first paragraph of its body that is not a quote and the first
    that is, or None for either it lacks."""
    body = text.split("---", 2)[2] if text.startswith("---") and text.count("---") >= 2 else text
    paras = [p.strip() for p in body.strip().split("\n\n") if p.strip()]
    return next((p for p in paras if not p.startswith(">")), None), next((p for p in paras if p.startswith(">")), None)


def amendment(fleet, plan, a, alone=False):
    """A unit amend as the user reads it: the unit's bolt, team and stage, its intent as it stands and as it would be,
    and what approval sets in motion. The stage is read from the unit's kit; alone, nothing is read but the plan, and
    only its first line is said."""
    return amendment_lines(plan, a, None if alone or plan.unit(a.unit) is None else unit_stage(fleet, plan, a.unit))


def amendment_lines(plan, a, s):
    """What a proposal's page says of a unit amend: the unit's bolt and team, and, given its stage (s, None when the page
    is drawn alone), its intent as it stands and as proposed and what approval sets in motion."""
    u = plan.unit(a.unit)
    if u is None:
        return [f"**Amend unit `{a.unit}`**, new in this proposal", f"Intent, as proposed:  {a.intent}"]
    b = u.get("Bolt")
    team = plan.bolt(b).get("Team") if b else None
    where = (f"bolt `{b}`" + (f" ({team})" if team else "")) if b else f"the queue of {u.get('Repo')}"
    if s is None:
        return [f"**Amend unit `{a.unit}`** in {where}"]
    st = s["stage"]
    now = ("" if st == "queued" else f", its stage unknown ({s.get('why')})" if st == "unknown" else
           f", now in {st}" if st in ("construct", "planned", "code", "verify") else f", now {st}")
    return [f"**Amend unit `{a.unit}`** in {where}{now}", f"Intent, as it stands: {u.get('Intent')}", f"Intent, as proposed:  {a.intent}",
            f"On approval: construct runs again at once in {team}'s slot, and once that has committed the unit goes on from "
            "its tasks with no approval asked, its revised change due for the next batch." if s["worktree"] and team else
            "On approval: its intent is replaced; it has no change written yet, so nothing else changes."]


def describe(fleet, label, plan, p, alone=False, signal_of=None):
    """A proposal as the user reads it: each change in plain words, with what the user is comparing beside it (a unit's
    intent and sources, the goal and team of the bolt it would join, an amended unit's intent before and after), and
    who has yet to agree. alone, it reads nothing but the plan and the proposal: no kit for an amended unit's stage and
    no signal, as a proposal's card is drawn (plan.12). signal_of(id) gives a unit's signal as signal_text reads it."""
    signal_of = signal_of or (lambda sig: signal_text(fleet, label, sig))
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
        r = plan.item(u)
        return r.get("Intent") if r else None
    for i, a in enumerate(argvs):
        # A chore's command reads as the unit's of the same name, said of a chore and its words (plan.11).
        key, lines = ("unit" if a.cmd == "chore" else a.cmd, a.sub), []
        noun, says = ("chore", "Chore") if a.cmd == "chore" else ("unit", "Intent")
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
            lines = [f"**New {noun} `{a.unit}`** in {where}", f"{says}: {a.intent}"]
            if a.bolt and goal_of(a.bolt):
                lines.append(f"Bolt's goal: {goal_of(a.bolt)}")
            if getattr(a, "unblocks", None):
                lines.append(f"Unblocks: bolt `{a.unblocks}`, which can't be proven or land without it")
            if a.signal and not alone:
                assertion, excerpt, grade = signal_of(a.signal)
                lines.append(f"From: signals/{a.signal}" + (f": \"{assertion}\"" if assertion else ""))
                if excerpt:
                    lines.append(f"Excerpt" + (f" ({grade})" if grade else "") + f": {excerpt}")
            lines += [f"Source: {s}" for s in a.source]
        elif key == ("unit", "move"):
            src = next((b for b in per[i] if b != a.bolt), None)
            to = None if a.bolt == "queue" else a.bolt
            lines = [f"**Move {noun} `{a.unit}`** from {bolt_line(src) if src else 'the queue'} to {bolt_line(to) if to else 'the queue'}",
                     f"{says}: {intent_of(a.unit)}"]
            if to and goal_of(to):
                lines.append(f"Bolt's goal: {goal_of(to)}")
            if getattr(a, "unblocks", None):
                lines.append(f"Unblocks: bolt `{a.unblocks}`, which can't be proven or land without it")
        elif key == ("unit", "split"):
            lines = [f"**Split unit `{a.unit}`**", f"Narrowed intent: {a.intent}"] + [f"New unit `{n}`: {i}" for n, i in a.into]
        elif key == ("unit", "amend"):
            lines = amendment(fleet, plan, a, alone)
        elif key == ("unit", "order"):
            where = "first" if a.first else "last" if a.last else f"before `{a.before}`"
            lines = [f"**Order {noun} `{a.unit}`** {where}", f"{says}: {intent_of(a.unit)}"]
        elif key == ("unit", "after"):
            lines = [f"**{noun.capitalize()} `{a.unit}` comes after** " + ("nothing" if a.none else ", ".join(f"`{d}`" for d in a.deps))]
        elif key == ("unit", "drop"):
            lines = [f"**Drop {noun} `{a.unit}`**", f"{says}: {intent_of(a.unit)}", f"Reason: {a.reason}"]
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
    """Each open proposal of the labels' flywheels, as describe() gives it, with its label and its chain's first
    (proposal_chain), whose key its card is under. found, when given, is the plans already read, as plans() gives
    them: their tips are used, and a label it lacks is skipped."""
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
        plan, pl = plan or read(repo, ref, tip), Plan(text)
        for p in pl.recs("Proposal"):
            if p.get("State") == "open":
                rows.append(dict(describe(fleet, l, plan, p), label=l, first=proposal_chain(pl, int(p.get("Proposal")))[0]))
    return rows


def plan_proposed(fleet, a):
    """crew plan proposed [<n>] [--label L] [--json] [--open]: the open proposals, or one as the user would read it.
    Reads the flywheels' branches only, so any host can answer. With --open, one proposal's page is written to
    ~/.local/state/crew/proposals/<label>-<n>.md on this host, replacing any earlier copy, and opened in plannotator:
    beside the caller in herdr, inline in the terminal otherwise. The file is a copy for reading; nothing reads it back."""
    why = open_refusal(a.n, a.open, a.json)
    not why or fail(why)
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


def open_refusal(n, open_, as_json):
    """Why crew plan proposed refuses --open: it opens one proposal, by its number, and prints no JSON beside it."""
    if open_ and n is None:
        return "--open needs a proposal's number: crew plan proposed <n> --open"
    if open_ and as_json:
        return "--open shows the proposal in plannotator and --json prints it: use one"
    return None


# ------------------------------------------------------------------------------------------- a proposal's card

def concerns(a):
    """The unit a proposal's command concerns, its subject, or None for a bolt's command."""
    return None if a.cmd == "bolt" else a.unit


def names_units(a):
    """Every unit a proposal's command names: its subject and each unit it refers to."""
    if a.cmd == "bolt":
        return []
    out = [a.unit] + list(getattr(a, "after", None) or []) + ([a.before] if getattr(a, "before", None) else [])
    out += [n for n, _ in getattr(a, "into", None) or []] + list(getattr(a, "deps", None) or [])
    return list(dict.fromkeys(out))


def kept(argvs, cleared, n):
    """Proposal n's commands the user kept, the cleared units left out (plan.3): each cleared unit must be one the
    proposal makes new to a bolt; every command that concerns only a cleared unit is left out; a command left in that
    names one refuses the whole, so the planner writes the proposal again without it."""
    new = new_units(argvs)
    wrong = [u for u in cleared if u not in new]
    not wrong or fail(f"proposal {n} neither adds nor moves into a bolt {either(wrong)}, so the user can't leave "
                      + ("it" if len(wrong) == 1 else "them") + " out: "
                      + (f"the units it may leave out are {either(new)}" if new else "it makes no unit new to a bolt"))
    out = []
    for a in argvs:
        if concerns(a) in cleared:
            continue
        hit = [u for u in names_units(a) if u in cleared]
        if hit:
            refuse(f"`{a.do}` names {either(hit)}, which the user left out: write the proposal again without "
                   + ("it" if len(hit) == 1 else "them"), f"`{do_named(a)}` names {either(hit)}, which the user left out")
        out.append(a)
    return out


def approved_words(applied, cleared):
    """What an approval did, as the proposal's card is closed with it and the planner told (record 0031 §1): what was
    added, dropped and amended, with a count of the rest, then the new units the user left out."""
    def units(subs, xs):
        return [a.unit for a in xs if a.cmd in ("unit", "chore") and a.sub in subs]
    added, dropped, amended = new_units(applied), units(("drop",), applied), units(("amend",), applied)
    rows = [a for a in applied if a.cmd in ("unit", "chore") and (a.sub in ("drop", "amend") or a.sub in ("add", "move") and a.unit in added)]
    rest = len(applied) - len(rows)
    did = ([f"added {joined(added)}"] if added else []) + ([f"dropped {joined(dropped)}"] if dropped else []) \
        + ([f"amended {joined(amended)}"] if amended else []) + ([cards.plural(rest, "other change")] if rest else [])
    said = [("Applied: " + "; ".join(did) + ".") if did else "Nothing applied."]
    said += [f"Left out on your word: {joined(cleared)}."] if cleared else []
    return " ".join(said)


def answers_file(label, n):
    return CARDS / label / "proposal" / str(n) / "answers.json"


def held_answers(f):
    """The answers gathered for a proposal's card, {} when none; refused when crew can't read them (read.1)."""
    try:
        held = json.loads(f.read_text())
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as e:
        fail(f"crew can't read the answers it gathered, {f}: {e}")
    return held if isinstance(held, dict) else fail(f"{f} holds no answers crew gathered")


def plan_answer(fleet, a):
    """crew plan answer <n> <question> <answer>... [--note "<text>"] [--label L]: one question of open proposal n's card
    answered, as the planner reads it from the card: rows-<k> and the ids of the boxes the user left ticked (none when
    every one is cleared; rows-1 for a card of one list, and for a lone new unit the side the user picked), or, for a
    hold-to-approve, plan approve or decline. It is checked against the card crew builds for the proposal now
    (proposal_facts, cards.proposal_card), and kept on this host, the planner's, beside the card's session files: a
    card's working state, never the plan's (state.2). Once it holds every question's answer, the change is applied with
    the boxes as they stand, as crew plan approve applies it, and the answers go: a new unit unticked left out; a note
    beside it is then printed as the user's word for the planner's next proposal. A decline applies nothing, and its
    answers go. Refused for a question the card does not ask, a box its question does not hold, an answer that differs
    from the one held, and a closed proposal, recording nothing."""
    label = proposal_label(fleet, a, a.n)
    CONTEXT["label"] = label
    w, _, p, _ = at_tip(fleet, label, a.n)
    b = cards.proposal_card(proposal_facts(fleet, label, w, a.n))
    asks = card_asks(b["card"])
    answer = card_answer(asks, b["card"].get("kind") == "choice", a.n, a.question, a.answer)
    f = answers_file(label, a.n)
    f.parent.mkdir(parents=True, exist_ok=True)
    with open(f.parent / ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        held = with_answer(held_answers(f), a.n, a.question, answer, a.note)
        tmp = f.parent / ".answers.json"
        tmp.write_text(json.dumps(held, indent=1) + "\n")
        tmp.replace(f)
        note = held.get("note")
        if held.get("plan") == "decline":
            f.unlink()
            print(f"proposal {a.n} is declined: nothing is applied, and the answers crew gathered are gone. The decline"
                  + (f", and the user's note beside it, \"{note}\"," if note else "") + " is the user's word for you to act on: "
                  f"write the proposal again with crew plan propose <file> --replaces {a.n}, or drop it with "
                  f"crew plan drop {a.n} \"<the user's reason>\".")
            return
        waits, cleared = answered(asks, held, b["boxes"])
        if waits:
            print(f"proposal {a.n} waits on {either(waits)}: nothing is applied")
            return
        approval = argparse.Namespace(cmd="plan", sub="approve", n=a.n, label=label, clear=cleared)
        try:
            plan_approve(fleet, approval)
        except Refusal as e:
            refused(fleet, approval, ("plan", "approve"), e)
            raise
        f.unlink()
    if note:
        print(f"The user's note beside the approval of proposal {a.n}: \"{note}\". Propose what it asks as a new proposal.")


def card_asks(card):
    """The questions a proposal's card crew built asks, as crew plan answer takes their answers, each with the ids of
    its boxes: plan, approve or decline, for a hold-to-approve; else rows-<k> for each list of boxes, rows-1 for a card
    of one list or a lone new unit's choice of its two sides."""
    if card.get("kind") == "approve":
        return {"plan": None}
    if card.get("questions"):
        return {q["id"]: [o["id"] for o in q["options"]] for q in card["questions"]}
    return {"rows-1": [o["id"] for o in card["options"]]}


def card_answer(asks, lone, n, question, given):
    """One question of proposal n's card answered, checked against the questions the card asks now (asks, each
    question's box ids): plan, approve or decline; a lone new unit's, the one side the user picked; rows-<k>, the boxes
    the user left ticked of those it holds. Returns the answer as kept."""
    question in asks or fail(f"proposal {n}'s card asks {either(list(asks))}, not {question}")
    given, boxes = list(dict.fromkeys(given)), asks[question]
    if question == "plan":
        len(given) == 1 and given[0] in ("approve", "decline") or fail("plan is answered approve or decline")
        return given[0]
    if lone:
        len(given) == 1 and given[0] in boxes or fail(f"{question} is answered {either(boxes)}")
        return given
    bad = [x for x in given if x not in boxes]
    not bad or fail(f"{question} holds {either(boxes)}, not {either(bad)}")
    return given


def with_answer(held, n, question, answer, note=None):
    """The answers held for proposal n's card with one more: the same answer again is fine, a different one refused,
    and a note joins the notes held, once."""
    if question in held:
        was = held[question]
        same = was == answer if question == "plan" else sorted(was) == sorted(answer)
        words = was if isinstance(was, str) else " ".join(was) or "nothing ticked"
        same or fail(f"crew already holds {question} {words} for proposal {n}: the user answered it once")
    held = dict(held)
    held.setdefault(question, answer)
    if note and note.strip() and note.strip() not in held.get("note", ""):
        held["note"] = (held.get("note", "") + "\n\n" + note.strip()).strip()
    return held


def answered(asks, held, boxes):
    """What the answers held say once a card's questions are read (record 0031 §5): the questions still unanswered,
    and, once none is, the new units the user cleared, each one's box left unticked. A hold-to-approve leaves none out,
    the boxes of one that links its reading session standing as proposed."""
    waits = [q for q in asks if q not in held]
    if waits or "plan" in asks:
        return waits, []
    picked = {x for q in asks for x in held[q]}
    return [], [b["unit"] for b in boxes if b["id"] not in picked]


def proposal_facts(fleet, label, w, n):
    """What proposal n's card is built from (record 0031 §5), as card_model reads it, from the write w as it left the
    branch and no kit (plan.12): the plan at the tip and as the proposal's commands leave it, applied to a copy as
    check_ops applies them; the proposal's number, state, case and commands, parsed; its chain's first, whose key the
    card is under; the teams whose conductor has yet to agree; and no reading session. A closed proposal's facts hold
    no plan after it, and the builder refuses them."""
    pl = proposals(w)
    p = proposal(pl, n, label)
    argvs = [do_args(label, d) for d in p.all("Do")]
    after = check_ops(fleet, label, w, argvs, n, Drawn).plan if p.get("State") == "open" else w.plan
    waiting = [t for t in held_teams(w.plan, flat(touched_by(w.plan, argvs))) if t not in p.all("Agreed")]
    return dict(n=n, first=proposal_chain(pl, n)[0], state=p.get("State"), case=p.get("Case"), before=w.plan,
                after=after, argvs=argvs, waiting=waiting, session=None)


def named_kit(plan, argvs):
    """The kit of the first bolt or unit a proposal's commands name, in whose area its card is filed (briefs.11): a new
    bolt's, or a unit's added to the queue, as the command gives it, else the plan's for the bolt or unit it names; None
    when the plan names none of them."""
    for a in argvs:
        if a.cmd == "bolt":
            b = plan.bolt(a.bolt)
            repo = a.repo if a.sub == "new" else b.get("Repo") if b else None
        elif a.sub == "add":
            repo = a.repo or (plan.bolt(a.bolt).get("Repo") if a.bolt and plan.bolt(a.bolt) else None)
        else:
            repo = plan.item(a.unit).get("Repo") if plan.item(a.unit) else None
        if repo:
            return repo
    return None


def chain_open(pl, first):
    """The open proposal of the chain whose card is keyed proposal/<first>, in proposals.rec (pl): its number, or None
    when the chain has none open, its last one approved or dropped."""
    return next((int(p.get("Proposal")) for p in pl.recs("Proposal") if p.get("State") == "open"
                 and proposal_chain(pl, int(p.get("Proposal")))[0] == first), None)


SWEPT = "Raised again as the plan stands"  # the change note of a proposal's card the rail's sweep raises
# The outcome a dropped proposal's card is acked with once the user answered it: their note, the drop's reason, may ask
# them something, which Pending You refuses as an outcome (proposal 161's drop on 2026-10-19: "Your outcome asks your
# person something; put it on a new card with follows instead."), so the reason stays on the proposal's record.
DROPPED = "Dropped on your note, nothing of it applied"


def proposal_act(event, n, mine, was_mine=False, held=True, home=True, agreed=(), outcome=None, reason=None, by=None):
    """Which act proposal n's card takes at its event (record 0031 §1), from facts alone: ("post",) when it is
    accepted, ("change", note) when it is rewritten (replace), a conductor agrees, the rail's sweep finds its card
    missing or lost (sweep), or its reading opens after the card was raised without it (relink, reading_again),
    ("close", outcome, reason) when it is approved, or dropped, its card acked with DROPPED
    once the user answered it and withdrawn with the reason while it waits, or None when it has no card of
    crew's. mine, whether the planner wrote it, the card's owner, whose proposals alone crew raises a card for;
    was_mine, at a rewrite, whether the planner wrote the one it replaces, whose card a rewrite of anyone else's
    withdraws. A change is made only where its card was posted, held on this host, or on the planner's own (home),
    where it is posted when none is held: elsewhere it is ("skip",), since a card is reached only from the host that
    posted it. The sweep runs only on the planner's host."""
    if event == "replace" and not mine:
        return ("close", None, f"Rewritten by {by} as proposal {n}, which has no card") if was_mine else None
    if not mine:
        return None
    if event == "propose":
        return ("post",)
    if event == "sweep":
        return ("change", SWEPT)
    if event == "relink":
        return ("change", RELINKED)
    if event in ("replace", "agree"):
        if not held and not home:
            return ("skip",)
        return ("change", f"Rewritten as proposal {n} after your note" if event == "replace" else
                "No longer waits on " + either([f"{t}-conductor" for t in agreed]))
    return ("close", outcome, None) if event == "approve" else ("close", DROPPED, reason)


def chain_closed(pl, first):
    """How the chain keyed proposal/<first> stands closed in proposals.rec (pl), in row_gone's words, as its card is
    closed once the plan shows it so (raise_proposal): (outcome, None) when its last proposal was approved, its card
    closed as applied; (None, reason) when it was dropped, its card withdrawn; None while a proposal of it is open, and
    for a chain pl holds no proposal of."""
    chain = [p for p in pl.recs("Proposal") if proposal_chain(pl, int(p.get("Proposal")))[0] == first]
    if not chain or any(p.get("State") == "open" for p in chain):
        return None
    last = max(chain, key=lambda p: int(p.get("Proposal")))
    return ("its proposal was applied", None) if last.get("State") == "approved" else (None, "its proposal was dropped")


def tip_write(fleet, label, fresh=False):
    """The flywheel's branch at its tip, as a write; with fresh, the tip fetched anew, the plan as it stands and not
    as this command first read it (fetch). None when the branch has no tip."""
    repo, ref = state_of(fleet, label)
    tip = fetch(repo, ref, fresh)
    return Write(repo, label, tip, read(repo, ref, tip)) if tip else None


def chain_read(fleet, label, first):
    """The open proposal of the chain keyed proposal/<first>, read at the branch's tip: (w, n), the write as the tip
    holds it and the proposal's number; None when the branch has no tip or the chain has no proposal open."""
    w = tip_write(fleet, label)
    n = chain_open(proposals(w), first) if w else None
    return (w, n) if n is not None else None


def raise_proposal(fleet, row, acts=None, event="sweep"):
    """The rail's sweep's raise of a proposal row's card (record 0031 §1), for a row whose card is missing or lost:
    the open proposal of the chain its key names, read at the branch's tip from the row's label and key, fetched anew
    at the sweep (tip_write), raised through row_card_change, which posts it when none is held and posts it again, its
    summary saying the older copy is dead, when Pending You no longer finds it, and when the sweep hands it the older
    copy this host can't reach as the row's dead; or, with event relink, its card changed to carry its reading's link
    (reading_again). The rail's read of the plan can be older than an approval or a drop its run record already holds
    (wldn's proposal 538 on 2026-10-23, approved at 9b8c8c1 and its card closed, then posted again by the sweep 15 s
    after on the read's tip, signal 2026-10-23-swancloud-planner-727dc1ea/01), so the sweep's raise fetches the tip
    again, the one fetch of the state branch past a command's first (plan.12), made only for a card about to be posted:
    a chain the plan as it stands shows approved or dropped raises none, and a card the planner still holds open under
    its key on this host is closed as one whose row is gone (chain_closed), so the user is not asked what was answered.
    None, raising nothing, when the key is no proposal chain's or the chain has no proposal open. The card's id, or
    None."""
    label, m = row["label"], re.fullmatch(r"proposal/(\d+)", row.get("key") or "")
    w = tip_write(fleet, label, fresh=event == "sweep") if m else None
    pl = proposals(w) if w else None
    n = chain_open(pl, int(m.group(1))) if pl else None
    if n is not None:
        return raise_proposal_at(fleet, label, w, n, event, acts, dead=bool(row.get("dead")))
    closed = chain_closed(pl, int(m.group(1))) if pl and event == "sweep" else None
    if closed:
        acts, owner = acts or CardActs(fleet), f"{label}-planner"
        print(f"card {row['key']} not raised: {closed[0] or closed[1]}, as the plan stands")
        if cards.card_under(acts.entries(label), row["key"], owner):
            row_card_close(fleet, label, owner, row["key"], *closed, acts=acts)
    return None


def raise_proposal_at(fleet, label, w, n, event, acts=None, agreed=(), outcome=None, reason=None, dead=False):
    """Proposal n's card at its event (record 0031 §1, briefs.11), once the event's write is made (code.9), from the
    write w as it left the branch: the act proposal_act decides; the card built by the proposal's builder from
    proposal_facts, and posted, changed or closed by the act in the planner's name under its chain's key,
    proposal/<first>, filed in the area of the kit of the first bolt or unit its commands name. A rewrite whose card
    takes another form than the replaced proposal's (cards.proposal_form: a hold-to-approve, a choice, one list or
    lists), which update_request never changes, has the card followed as a card whose kind changed; a rewrite asks
    anew, and follows a card the user answered, where an agreement or the sweep's raise leaves it as it is, its answer
    going on to the approval (row_card_change); the card that follows says what the rewrite changed against the
    proposal it replaces (cards.proposal_since), and one that changes neither its commands nor its case is withheld,
    the user's answer standing (card_posted). With dead, an older copy this host can't reach standing, the card is
    built saying first that it was lost (built_again). A card crew cannot build, or Pending You refuses, refuses
    nothing of the proposal: it is said, and the rail shows the row with no card. The card's id, or None."""
    acts = acts or CardActs(fleet)
    owner, part = f"{label}-planner", crew.partition_of(fleet, label)
    pl = proposals(w)
    p = proposal(pl, n, label)
    replaced = proposal(pl, int(p.get("Replaces")), label) if (p.get("Replaces") or "").isdigit() else None
    was = replaced.get("By") if replaced else None
    key = f"proposal/{proposal_chain(pl, n)[0]}"
    near = event in ("replace", "agree")
    act = proposal_act(event, n, p.get("By") == owner, was == owner,
                       held=near and cards.card_under(acts.entries(label), key, owner) is not None,
                       home=acts.host() == part["machine"], agreed=agreed, outcome=outcome, reason=reason, by=p.get("By"))
    if act is None:
        return None
    if act[0] == "skip":
        print(f"card {key} not changed here: {owner} holds it on {part['machine']}, and {acts.host()} holds none")
        return None
    try:
        if act[0] == "close":
            return row_card_close(fleet, label, owner, key, outcome=act[1], reason=act[2], acts=acts)
        facts = proposal_facts(fleet, label, w, n)
        team = builder(fleet, label, named_kit(w.plan, facts["argvs"]))
        where = card_where(team["kit"] if team else {"main": part["checkout"], "repo": part["blueprints"][0]})
        build = built_again(cards.proposal_card) if dead else cards.proposal_card
        if act[0] == "post":
            return row_card_post(fleet, label, owner, build, facts, where, acts)
        old = [do_args(label, d) for d in replaced.all("Do")] if event == "replace" and replaced is not None else None
        moved = old is not None and cards.proposal_form(old) != cards.proposal_form(facts["argvs"])
        since = cards.proposal_since(old, replaced.get("Case"), facts["argvs"], facts["case"]) if old is not None else None
        return row_card_change(fleet, label, owner, build, facts, act[1], where, acts, kind_changed=moved,
                               anew={} if event == "replace" else None,
                               since=[f"The planner rewrote it as proposal {n}."] + since if since else since)
    except Refusal as e:
        print(f"card {key} not raised: {e}", file=sys.stderr)
        return None


# -------------------------------------------------------------------------------------------------- signals

SHORT_ID = re.compile(r"^[^/]+/[0-9]{2}$")  # a signal's short id, <capture>/<NN>: its full id without the slug


def signal_at(fleet, label, sig, w=None):
    """Where a signal is: signals/<id>.md on the flywheel's branch (as the write w has it, else at the branch's tip),
    else on main of the partition's first blueprints repo, where the daily pass writes meetings' and channels'. sig is
    its full id, <capture>/<NN>-<slug>, or its short form, <capture>/<NN>, which names the one signal of that capture
    numbered NN. (where, repo, tip, the signal's text, its full id), or None when it is in neither."""
    if w is not None:
        repo, ref, tip = w.repo, f"{label}/main", w.tip
    else:
        repo, ref = state_of(fleet, label)
        tip = fetch(repo, ref)
    hit = signal_in(repo, tip, sig, w) if tip or w is not None else None
    if hit:
        return ref, repo, tip, *hit
    srepo = crew.partition_of(fleet, label)["blueprints"][0]
    tip = fetch(srepo, "main")
    hit = signal_in(srepo, tip, sig) if tip else None
    return ("main", srepo, tip, *hit) if hit else None


def signal_in(repo, tip, sig, w=None):
    """A signal's (text, full id) in the repo at tip, as the write w has it when given; None when it is not there. A
    short id is looked for among the files of its capture's folder."""
    if SHORT_ID.match(sig):
        cap = sig.split("/")[0]
        listed = git(repo, "ls-tree", "--name-only", f"{tip}:signals/{cap}", check=False) if tip else None
        names = (listed.stdout.split() if listed and listed.returncode == 0 else []) + [
            p.rsplit("/", 1)[1] for p in (w.files if w is not None else ()) if p.startswith(f"signals/{cap}/")]
        sig = signal_named(sig, names)
        if sig is None:
            return None
    path = f"signals/{sig}.md"
    text = w.text(path) if w is not None else show(repo, tip, path)
    return (text, sig) if text is not None else None


def signal_named(sig, names):
    """The full id a short id, <capture>/<NN>, names, from the file names in its capture's folder: the one signal
    numbered NN, <capture>/<NN>-<slug>. None when the capture has none; refused when it has more than one, since
    nothing says which (read.1)."""
    cap, n = sig.split("/")
    hits = sorted({f"{cap}/{x[:-3]}" for x in names if SIGNAL_FILE.match(x) and x.startswith(f"{n}-")})
    len(hits) < 2 or fail(f"signal {sig} names {len(hits)} signals: {', '.join(hits)}; give the full id of one")
    return hits[0] if hits else None


def signal_id(fleet, label, sig, w=None):
    """A signal's full id: a full id as it is, a short one as signal_at finds it (in the write w, when given), refused
    when it is in neither home."""
    return sig if not SHORT_ID.match(sig) else (signal_at(fleet, label, sig, w) or no_signal(fleet, label, sig))[4]


def no_signal(fleet, label, sig):
    cap, _, n = sig.rpartition("/")
    fail(f"no signal {sig} on {label}/main of {state_of(fleet, label)[0]} or on main of "
         f"{crew.partition_of(fleet, label)['blueprints'][0]}: "
         + (f"signals/{cap}/ holds no {n}-<slug>.md in either" if SHORT_ID.match(sig) else f"signals/{sig}.md is in neither"))


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


def route_move(sig, target):
    """A signal's route move to the work that takes it, its target that work's object, unit/<unit> or chore/<chore>."""
    return Rec("Move", [("Signal", sig), ("Move", "route"), ("Target", target if "/" in target else f"unit/{target}"),
                        ("Date", datetime.date.today().isoformat()), ("By", agent())])


CURATION = ("attach", "challenge", "new-territory", "answered", "drop")
KINDS = ("constraint", "ask", "question", "commitment", "reaction")


def signal_move(fleet, a):
    """Curation's five moves, each written through crew the way the route is: one move per signal, appended to
    moves.rec on the flywheel's branch of its state repository, never merged. A short id is moved by its full one."""
    label = default_label(fleet, a) or fail("which partition's signals? add --label " + "|".join(fleet["partitions"]))
    a.signal = signal_id(fleet, label, a.signal)
    rec, on = curation_move(a.signal, a.move, a.target, a.reason, datetime.date.today().isoformat(), agent())
    write(fleet, label, lambda w: move(fleet, label, w, a.signal, rec), f"signals({a.signal}): {a.move}", act="signal.move", on=on)


def curation_move(sig, kind, target, reason, today, by):
    """A curation move's record, and the objects its run-record entry names: the signal, and its target when that is a
    pointer, a typed name such as unit/<unit> or a path, never words that could be typed text. Refused when an attach,
    a challenge or an answered names no target, or a drop gives no reason."""
    kind not in ("attach", "challenge", "answered") or target or fail(
        f"a {kind} move names its target (--target): the intent, claim or record it " + {"attach": "lands on", "challenge": "argues with", "answered": "was settled by"}[kind])
    kind != "drop" or reason or fail("a drop gives its reason (--reason)")
    rec = Rec("Move", [("Signal", sig), ("Move", kind)] + ([("Target", target)] if target else [])
              + ([("Reason", reason)] if reason else []) + [("Date", today), ("By", by)])
    return rec, [f"signals/{sig}"] + ([target] if target and re.fullmatch(r"[a-z]+/[^\s]+", target) else [])


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
    """Where an agent was working, read without asking it: its team, each bolt the team holds and, for a slot's stage,
    the unit or fix its slot holds; the main level; None for an agent crew has no role for."""
    kind, of = role(fleet, name)
    if kind in ("planner", "design", "main-ops", "dispatcher", "operator"):
        return "main level"
    if kind not in ("conductor", "team"):
        return None
    out = [f"team {of}"] + [f"bolt {b.name()}" for b in held_by(plan, of)]
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
    signal_refusal(a.slug, a.asserts) and fail(signal_refusal(a.slug, a.asserts))
    name, host = os.environ.get("CREW_AGENT"), crew.this_host()
    now = datetime.datetime.now(datetime.timezone.utc)
    excerpt = a.excerpt
    if a.excerpt_file:
        try:
            excerpt = pathlib.Path(a.excerpt_file).read_text()
        except (OSError, UnicodeDecodeError) as e:
            fail(f"cannot read the excerpt from {a.excerpt_file}: {getattr(e, 'strerror', None) or e}")
    v = sid = user = None
    if name:
        excerpt = (excerpt or "").strip()
        excerpt or fail('a signal quotes the words that show it: add --excerpt "<the exact words the user said or the '
                        'tool printed>", or --excerpt-file <path>')
        v, sid = check_excerpt(fleet, name, a, excerpt, host)
        excerpt_refusal(v) and fail(excerpt_refusal(v))
    else:
        import getpass
        excerpt, user = (excerpt or a.asserts).strip(), getpass.getuser()
    by = agent()
    key, cap, date, who, position, kind = capture_named(name, v, sid, excerpt, now, a.kind, user, host, by)
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
    seen = {}

    def change(w):
        cpath = f"signals/{cap}/capture.md"
        have = w.text(cpath)
        names = []
        if have is not None:
            listed = git(w.repo, "ls-tree", "--name-only", f"{w.tip}:signals/{cap}", check=False)
            names = listed.stdout.split() if listed.returncode == 0 else []
        nn, count = signal_number(have, key, cap, label, names, a.slug, quote, lambda n: w.text(f"signals/{cap}/{n}"))
        sig = f"{cap}/{nn:02d}-{a.slug}"
        if have is None:
            have = capture_text(fleet, name, host, v, sid, key, cap, date, now, raw, w.plan, by)
        w.replace(cpath, re.sub(r"(?m)^signals: [0-9]+$", f"signals: {count}", have, count=1))
        w.replace(f"signals/{sig}.md", signal_md(sig, kind, who, a.subject, a.asserts, quote))
        w.subject = f"signals({sig}): {a.slug}"
        w.on.append(f"signals/{sig}")
        seen["id"] = sig
        return []
    try:
        write(fleet, label, change, f"signals: {a.slug}", act="capture")
    except Already as e:
        print(f"signal {e} is recorded already; nothing was written")
        return
    print(signal_said(seen["id"], v))


def signal_refusal(slug, asserts):
    """Why crew signal refuses a signal before reading anything, or None: its slug is a name and not a subcommand's,
    and it says what it asserts."""
    if not crew.NAME.match(slug):
        return f"a signal's slug is lowercase words with dashes, not {slug}"
    if slug in ("move", "show", "land"):
        return f"a signal's slug can't be '{slug}'"
    if not asserts.strip():
        return "a signal says what it asserts, in a sentence"
    return None


def excerpt_refusal(v):
    """Why crew signal refuses an agent's excerpt on its verdict v, or None: the words are not in the session's
    transcript, reworded or a background task's output the agent has not read yet (signals.2)."""
    if v.grade != "refused":
        return None
    return ("the excerpt is not in your session's transcript: quote the words as you received them, from the user or "
            "from a tool's output. A background task's output reaches your transcript only once you read the output file "
            "its task notification names: read that file, then record the signal again")


def capture_named(name, v, sid, excerpt, now, kind=None, user=None, host=None, by=None):
    """The capture a signal goes in, and how it quotes its excerpt: (key, capture name, date, who asserted it, the
    quote's position, kind). An agent's (name) by the verdict v on its excerpt in session sid: a received record by its
    uuid, any other line by its hash, an unchecked excerpt by its own, dated by the record's time where it has one,
    asserted by whom the verdict says, the agent itself for a tool's output; kind constraint unless given. The user's
    note at a shell (no name), by user, at host, recorded by by: its own excerpt, by its hash, kind ask unless given."""
    if not name:
        h = sha16(excerpt)
        date = now.date().isoformat()
        return f"operator/{by}/{h}", f"{date}-{dashed(user)}-{dashed(host)}-{h[:8]}", date, "user", now.strftime("%H:%M:%SZ"), kind or "ask"
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
    who = {"user": "user", "crew": "crew"}.get(v.asserted_by) or (v.asserted_by[6:] if v.asserted_by.startswith("agent:") else name)
    position = "unverified" if v.grade == "unverified" else when.strftime("%H:%M:%SZ") if when else f"line {v.n}"
    return key, f"{date}-{dashed(name)}-{part}", date, who, position, kind or "constraint"


def signal_number(have, key, cap, label, names, slug, quote, text_of):
    """The number a signal takes in its capture, and how many signals the capture then holds: 1 and 1 in a capture
    not yet written (have is None); else one past the highest of the capture's signals (names, the files in its
    folder), refused when the capture there is another's (its key), and Already when one of them is this signal, by
    its slug and its quote (text_of(name), read only then)."""
    if have is None:
        return 1, 1
    field(have, "key") == key or fail(f"signals/{cap} on {label}/main is another capture ({field(have, 'key')}), not {key}")
    names = [n for n in names if re.match(r"^[0-9]{2}-.*\.md$", n)]
    for n in names:
        if n[3:-3] == slug and quote in (text_of(n) or ""):
            raise Already(f"{cap}/{n[:-3]}")
    return 1 + max([int(n[:2]) for n in names] or [0]), len(names) + 1


def signal_md(sig, kind, who, subject, asserts, quote):
    """A signal's file: its frontmatter, what it asserts, and its quote; subject, as typed, a comma-separated list."""
    subject = "[" + ", ".join(x.strip() for x in subject.split(",") if x.strip()) + "]" if subject else None
    return ("---\n" + f"signal: {sig}\nkind: {kind}\nwho: {who}\n" + (f"subject: {subject}\n" if subject else "")
            + "---\n\n" + asserts.strip() + "\n\n" + quote + "\n")


def signal_said(sig, v):
    """What crew signal says once the signal is written: its id and its excerpt's grade, own for the user's note,
    with who asserted a verified one and why one is unverified."""
    grade = "own" if v is None else v.grade
    return (f"signal {sig}: excerpt {grade}" + (f", asserted by {v.asserted_by}" if v and v.grade == "verified" else "")
            + (f" ({v.reason})" if v and v.grade == "unverified" else ""))


def check_excerpt(fleet, name, a, excerpt, host):
    """The agent's excerpt checked against its own Claude session's transcript, which is on this host: crew signal
    is never run on another. The session is the one a forwarded command carries, else herdr's for the agent. Returns
    the verdict and the session id."""
    sid, elsewhere = session_here(record.session(), host)
    if elsewhere:
        return transcript.unverified(elsewhere), sid
    skip = [a.excerpt_file, str(pathlib.Path(a.excerpt_file).resolve())] if a.excerpt_file else []
    return transcript.check(sid, excerpt, skip, stage_by(fleet, name)), sid


def session_here(sess, host):
    """The session a signal's excerpt is checked in, from the caller's <host>:<id>, and why it can't be read on this
    host, or None: a session on another host is not."""
    shost, sid = sess.split(":", 1) if sess and ":" in sess else (host, sess)
    return sid, (f"session {sid} is on {shost}, not {host}" if sid and shost != host else None)


def stage_by(fleet, name):
    """The conductor whose stages a slot's agent runs, whose own prompts are the conductor's; None for any other."""
    kind, of = role(fleet, name)
    return f"{of}-conductor" if kind == "team" and re.fullmatch(rf"{re.escape(of)}-unit-[1-9][0-9]*", name) else None


def capture_text(fleet, name, host, v, sid, key, cap, date, now, raw, plan, by=None):
    """A new capture.md: where its excerpt came from and how well crew could check it, with the count of its signals,
    which each signal that joins it rewrites. The user's note (v None) is captured by by, the user at this host."""
    today = now.date().isoformat()
    if v is None:
        fields = [("capture", cap), ("source", "operator"), ("key", key), ("captured_by", by), ("host", host),
                  ("excerpt", "own"), ("asserted_by", "user")]
        title, body = f"{by}, {date}", "The user's own note, recorded with crew signal at a shell."
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


SIGNAL_FILE = re.compile(r"^[0-9]{2}-[a-z0-9][a-z0-9-]*\.md$")
SIGNAL_LIMIT = 8 * 1024  # a signal's file larger than this copies its source; a program cuts its excerpt to fit (signals.3)


def raw_of(cap_text):
    """Where a capture's raw record is, from its raw field, <host>:<path>: (host, path), or None when it names none."""
    raw = field(cap_text, "raw")
    return tuple(raw.split(":", 1)) if raw and ":" in raw else None


def capture_refusal(cap, files, here, banked):
    """Why a program's capture does not land on the flywheel's branch (signals.6), or None. cap is its folder's name,
    files the folder's files ({name: text}, None for anything that is not a readable file), here this host and banked
    whether the raw record its capture.md names is there on it. A capture is a name crew takes (code.4) holding
    capture.md and its signals, NN-<slug>.md, and nothing else, since raw material stays on its host (signals.3);
    capture.md names itself, the program as its source, who captured it, its event's date, its raw record banked on
    this host, the host that ran the program, and is read, with as many signals as it holds, at least one; each signal
    names itself in its capture, its kind and who asserted it, says what it asserts, quotes its excerpt and is no
    larger than crew lands. The first refusal found is said, naming the file."""
    if not crew.NAME.match(cap):
        return f"{cap} is no capture's name crew takes: lowercase words, digits and dashes (code.4)"
    if files.get("capture.md") is None:
        return f"{cap} has no capture.md"
    for n in sorted(files):
        if n != "capture.md" and (not SIGNAL_FILE.match(n) or files[n] is None):
            return f"{cap}/{n} is no signal's file, NN-<slug>.md: a capture's raw material stays on its host, outside git (signals.3)"
    c = files["capture.md"]
    sigs = sorted(n for n in files if n != "capture.md")
    if field(c, "capture") != cap:
        return f"{cap}/capture.md names the capture {field(c, 'capture')}, not {cap}"
    for f, what in (("source", "the program that recorded it"), ("captured_by", "who recorded it"), ("event_date", "its event's date")):
        if not field(c, f):
            return f"{cap}/capture.md names no {f}, {what}"
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", field(c, "event_date")):
        return f"{cap}/capture.md: event_date is a date, 2026-10-12, not {field(c, 'event_date')}"
    raw = raw_of(c)
    if not raw:
        return f"{cap}/capture.md names no raw record, <host>:<path>, banked on the host that ran the program (signals.3)"
    if raw[0] != here:
        return f"{cap}/capture.md's raw record is on {raw[0]}, and a program's capture lands from the host that banked it, not {here}"
    if not banked:
        return f"{cap}/capture.md's raw record, {raw[1]}, is not on {here}"
    if field(c, "status") != "read" or not sigs:
        return f"{cap} lands read, with its signals: a program's capture is its own excerpt, and its one signal is made with it (signals.6)"
    if field(c, "signals") != str(len(sigs)):
        return f"{cap}/capture.md counts {field(c, 'signals')} signals, and {cap} holds {len(sigs)}"
    for n in sigs:
        t, what = files[n], f"{cap}/{n}"
        if len(t.encode()) > SIGNAL_LIMIT:
            return f"{what} is larger than {SIGNAL_LIMIT // 1024} KiB, so it copies its source: cut its excerpt and keep the whole in the raw record"
        if field(t, "signal") != f"{cap}/{n[:-3]}":
            return f"{what} names the signal {field(t, 'signal')}, not {cap}/{n[:-3]}"
        if field(t, "kind") not in KINDS:
            return f"{what}: kind is one of {', '.join(KINDS)}, not {field(t, 'kind')}"
        if not field(t, "who"):
            return f"{what} names no who, who asserted it"
        body = [l for l in re.sub(r"^---\n.*?\n---\n", "", t, count=1, flags=re.S).splitlines() if l.strip()]
        if not any(not l.startswith(">") for l in body):
            return f"{what} says nothing it asserts"
        if not any(l.startswith(">") for l in body):
            return f"{what} quotes no excerpt"
    return None


def capture_landing(cap, files, have, label):
    """What a capture's landing writes on the flywheel's branch, {path: text}, from the folder's files and what the
    branch holds at each of their paths (have, {name: text or None}): each file the branch lacks; one it holds the same
    is passed over; one it holds otherwise refuses the landing, since captures and signals are never changed (signals.4).
    Already when there is nothing to write."""
    out = {}
    for n in sorted(files):
        if have.get(n) is None:
            out[f"signals/{cap}/{n}"] = files[n]
        elif have[n] != files[n]:
            fail(f"signals/{cap}/{n} on {label}/main is not the one landed now, and a capture or signal is never changed (signals.4)")
    if not out:
        raise Already(cap)
    return out


def signal_land(fleet, a):
    """crew signal land <capture-dir>: a program's capture, a release adapter's or a deployer's, landed on the
    flywheel's branch of the partition named, as recorded on this host and never forwarded (signals.2, signals.6): the
    folder checked whole (capture_refusal), then its capture and signals written in one commit, the files the branch holds
    already passed over, and nothing written when it holds them all. Its raw record stays where the program banked it."""
    label = default_label(fleet, a) or fail("which partition's flywheel? add --label " + "|".join(fleet["partitions"]))
    d = pathlib.Path(a.dir)
    d.is_dir() or fail(f"{a.dir} is no capture's folder")
    cap = d.resolve().name
    files = {}
    for f in sorted(d.iterdir()):
        try:
            files[f.name] = f.read_text() if f.is_file() and not f.is_symlink() else None
        except (OSError, UnicodeDecodeError):
            files[f.name] = None
    raw = raw_of(files.get("capture.md"))
    why = capture_refusal(cap, files, crew.this_host(), bool(raw) and pathlib.Path(raw[1]).expanduser().exists())
    not why or fail(why)
    srepo = crew.partition_of(fleet, label)["blueprints"][0]
    btip = fetch(srepo, "main")
    not (btip and git(srepo, "ls-tree", "--name-only", btip, f"signals/{cap}")) or fail(
        f"{srepo} has signals/{cap} already, so a capture can't take that name (signals.1)")
    seen = {}

    def change(w):
        out = capture_landing(cap, files, {n: w.text(f"signals/{cap}/{n}") for n in files}, label)
        for path, text in out.items():
            w.replace(path, text)
        seen["ids"] = [p[8:-3] for p in out if not p.endswith("/capture.md")]
        w.on += [f"signals/{i}" for i in seen["ids"]]
        w.subject = f"signals({cap}): land " + (f"{len(seen['ids'])} signal" + ("" if len(seen["ids"]) == 1 else "s") if seen["ids"] else "the capture")
        return []
    try:
        write(fleet, label, change, f"signals({cap}): land", act="capture")
    except Already:
        print(f"{cap} is already landed on {label}/main; nothing was written")
        return
    print(f"landed {cap} on {label}/main: " + (", ".join(seen["ids"]) or "its capture"))


def signal_show(fleet, a):
    """crew signal show <id>: the signal, by its full id or its short one, its capture's provenance in plain lines (the
    excerpt's grade among them), and its move in each flywheel that reads it. Reads only the branches, so any host can
    answer."""
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
    found_in, (where, repo, tip, text, sig) = hit
    # A signal in the state is its flywheel's alone; one in a blueprints repo is read by each flywheel it is first for.
    readers = [found_in] if where != "main" else [l for l in labels if crew.partition_of(fleet, l)["blueprints"][0] == repo]
    moves = []
    for l in readers:
        srepo, ref = state_of(fleet, l)
        stip = fetch(srepo, ref)
        recs = show(srepo, stip, "moves.rec") if stip else None
        moves.append((l, next((m for m in Plan(recs).recs("Move") if m.get("Signal") == sig), None) if recs else None))
    print(shown_signal(sig, where, repo, text, show(repo, tip, capture_of(sig)), moves))


def shown_signal(sig, where, repo, text, cap, moves):
    """crew signal show: where the signal is, its text, its capture's fields in plain lines (cap, its capture.md, None
    when it has none), and its move in each flywheel that reads it (moves, [(label, its Move record or None)])."""
    out = [f"signals/{sig}, on {where} of {repo}", "", text.rstrip(), ""]
    if cap is None:
        out.append(f"No capture.md beside it in {repo}.")
    else:
        out.append(f"Its capture, {capture_of(sig)}:")
        out += [f"  {k}: {x}" for k, x in frontmatter(cap)]
    out.append("")
    for l, m in moves:
        out.append(f"No move yet in {l}." if not m else f"Its move in {l}: {m.get('Move')}" + (f" {m.get('Target')}" if m.get("Target") else "")
                   + f", by {m.get('By')} on {m.get('Date')}" + (f": {m.get('Reason')}" if m.get("Reason") else ""))
    return "\n".join(out)


# ------------------------------------------------------------------------------------- what a unit's stage asks

def sh(**pairs):
    return "\n".join(f"{k}={__import__('shlex').quote(str(v))}" for k, v in pairs.items())


def team_of_unit(fleet, a):
    """The team whose bolt holds a unit or chore, from its plan: crew unit run and wait, and crew chore run and wait, go
    to that team's host."""
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a), "unit or chore")
    t = crew.team_of(fleet, unit_team(plan, a.unit))
    return bolt_team(fleet, plan.bolt(plan.item(a.unit).get("Bolt"))) or t


def unit_team(plan, name):
    """The team whose bolt holds a unit or chore, which runs its stages; refused for queued work or a bolt no team
    holds."""
    u = plan.item(name)
    k = kind_of(u)
    u.get("Bolt") or fail(f"{k} {name} is queued: move it into a bolt first (crew {k} move {name} <bolt>)")
    return plan.bolt(u.get("Bolt")).get("Team") or fail(f"bolt {u.get('Bolt')} is held by no team yet: crew bolt give <team> {u.get('Bolt')}")


def in_bolt(fleet, t, unit):
    """Whether a unit or chore is in a bolt the team holds: what says so when it is, None when it is not, and refused
    when the team's plan could not be read, since then nobody can tell."""
    errors = {}
    found = plans(fleet, [t["label"]], errors)
    not errors or fail(f"can't tell whether {unit} is still in {t['name']}'s bolt: "
                       + "; ".join(f"{k} could not be read: {v}" for k, v in errors.items()))
    plan = found[0][3]
    u = plan.item(unit) if plan else None
    if u and u.get("Bolt") in {b.name() for b in held_by(plan, t["name"])}:
        return f"{kind_of(u)} {unit} is in bolt {u.get('Bolt')}, which {t['name']} holds"
    return None


HEAD = r"""cd "$1" && git rev-parse HEAD"""
# A dependent's place takes the head of each unmerged unit or chore it comes after, each given by its branch (unit/<name>
# or chore/<name>), as it stands, while it holds nothing of its own beyond the bolt, given by the ref it is read at
# (gather.bolt_read), and their work: printed as "<name>
# <head>" for each it holds. A merge that conflicts is undone, the place put back where it was, and printed as "conflict
# <name> <paths...>", exit 3. Each taking is a merge commit of its own, never a fast-forward, so the place's own work is
# its first-parent line with no merges (a chore's, plan.11). Never a push, never a write to their branches.
TAKE = r"""cd "$1" || exit 1
unit=$2 at=$3; shift 3
start=$(git rev-parse HEAD)
refs=(); for b; do refs+=("refs/heads/$b"); done
[ -z "$(git rev-list -n1 --no-merges HEAD --not "$at" "${refs[@]}")" ] || exit 0
for b; do
  a=${b#*/}
  if ! git merge-base --is-ancestor "refs/heads/$b" HEAD; then
    if ! git merge -q --no-ff --no-edit -m "chore($unit): build on $a as it stands" "refs/heads/$b" >/dev/null 2>&1; then
      paths=$(git diff --name-only --diff-filter=U | tr '\n' ' ')
      git merge --abort >/dev/null 2>&1; git reset -q --keep "$start"
      echo "conflict $a $paths"; exit 3
    fi
  fi
  echo "$a $(git rev-parse --short=7 "refs/heads/$b")"
done
"""


def mark_amended(fleet, label, unit, bolt, head):
    """The plan marks a unit amended at the head construct starts again from, so its code, verify and merge wait until
    what construct writes is committed (plan.6). Returns the write's commit. What the write says goes to standard
    error, as a write's does inside another command's work."""
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
    """Whether a unit or chore has delivered its verify since it was last constructed, from the run record of the host
    its stages run on: a delivered verify end later than every construct start of it. Its one round of fixes after the
    verify, a code stage, needs no verify again (teams.17); a chore has no construct, so any verify it delivered
    counts."""
    done = None
    for e in entries if entries is not None else local_entries(label):
        if e.get("Refused"):
            continue
        if e.get("Act") == "stage.start" and f"stage/{unit}/construct" in e["On"]:
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


def comes_after(after_of, a, b):
    """Whether a comes after b through After at any depth (plan.13): after_of is each unit's or chore's After names."""
    seen, todo = set(), list(after_of.get(a, ()))
    while todo:
        x = todo.pop()
        if x == b:
            return True
        if x not in seen:
            seen.add(x)
            todo += after_of.get(x, ())
    return False


def ahead(order, after_of, a, b):
    """Whether a is ahead of b in their bolt's merge order (teams.12, plan.13): b comes after a, at any depth; else,
    unless a comes after b, a is earlier in the plan's order (order, the work's names as the file lists them). A unit's
    dependents are never ahead of it, however the file lists them."""
    if comes_after(after_of, b, a):
        return True
    return not comes_after(after_of, a, b) and order.index(a) < order.index(b)


def bolt_order(plan, bolt):
    """A bolt's work as ahead reads it: its names in the plan's order, and each one's After names."""
    work = plan.work_of(bolt)
    return [w.name() for w in work], {w.name(): w.all("After") for w in work}


def overlapping(plan, st_all, k, unit, mine):
    """What a unit's Touches overlap among the unmerged units ahead of it in its bolt's merge order that have a place
    (ahead): the prompt's words for each, naming the entries and the other unit's change."""
    out, bolt = [], plan.unit(unit).get("Bolt")
    order, after_of = bolt_order(plan, bolt)
    for o in plan.units_of(bolt):
        if o.name() == unit or not ahead(order, after_of, o.name(), unit):
            continue
        pl = k["places"].get(o.name())
        if not pl or st_all.of(o.name())["stage"] in ("merged", "landed") or "entries" not in (pl.get("touches") or {}):
            continue
        pairs = [(m, t) for m in mine for t in pl["touches"]["entries"] if overlaps(m, t)]
        if pairs:
            on = "; ".join(m if m == t else f"{m} against {t}" for m, t in pairs)
            out.append(f"Its Touches overlap those of {o.name()}, ahead of it in the bolt and not merged, on {on}; "
                       f"{o.name()}'s change is {pl['path']}/openspec/changes/{o.name()}/.")
    return out


def undeclared(fleet, t, at, unit, entries, deps=()):
    """The paths a unit changed against its bolt, read at its ref (at, bolt_at_of), that no Touches entry matches, its
    own change's folder aside. Only
    the unit's own commits count: a dependent's place holds its After units' work as it stood, and a place that took a
    sibling unit's work by a merge, to settle a forecast, holds that unit's commits behind the merge's second parent;
    a path only their commits changed is theirs."""
    main = t["kit"]["main"]
    _, out = kit_git(fleet, t, main, "diff", "--name-only", f"{at}...unit/{unit}")
    held = [f"refs/heads/unit/{d}" for d in deps if head_of(fleet, t, main, f"unit/{d}")]
    _, mine = kit_git(fleet, t, main, "log", "--format=", "--name-only", "--no-merges", "--first-parent", f"unit/{unit}",
                      "--not", at, *held)
    return not_declared(out.splitlines(), set(mine.splitlines()), unit, entries)


def not_declared(changed, mine, unit, entries):
    """Of the paths a unit's place changed against its bolt, those its own commits changed (mine) that no Touches
    entry matches, its own change's folder aside: what its verify is told it did not declare (teams.12)."""
    own = f"openspec/changes/{unit}/"
    return [p for p in changed if p and p in mine and not p.startswith(own) and not any(matches(e, p) for e in entries)]


def took_from(st_all, k, u):
    """The branches a dependent's place takes, as TAKE takes them: of each unit or chore it comes after that has not
    merged and has a place, unit/<name> or chore/<name> (plan.13)."""
    places = lambda d: (k or {}).get("chore_places" if st_all.of(d)["kind"] == "chore" else "places", {})
    return [f"{st_all.of(d)['kind']}/{d}" for d in u.all("After") if st_all.of(d)["stage"] not in ("merged", "landed") and places(d).get(d)]


def read_at(k, bolt):
    """The ref a bolt is read at in its kit as gathered (gather.kit's at, gather.bolt_read): origin/bolt/<bolt> for a
    bolt on GitHub, else the host's bolt/<bolt>; None when crew can't tell or the host has neither."""
    return ((k or {}).get("bolts", {}).get(bolt) or {}).get("at")


def bolt_at_of(k, bolt):
    """read_at, refused when there is none, naming why (read.1): nothing is read from the host's copy in its place."""
    f = (k or {}).get("bolts", {}).get(bolt) or {}
    return f.get("at") or fail(f"crew can't read bolt/{bolt}: " + (f.get("error") or f"its kit holds neither bolt/{bolt} nor origin/bolt/{bolt}"))


def take(fleet, t, place, unit, at, deps, kind="unit"):
    """A dependent's place takes the head of each unmerged unit or chore it comes after with a place (deps, their
    branches, took_from), as it stands, while it holds nothing of its own beyond its bolt, read at its ref (at,
    bolt_at_of) (TAKE): the heads it holds, as "<name>@<head>"
    words for the start of its construct, or of a chore's code. Refused, with the place as it was, when two of them
    conflict."""
    if not deps:
        return ""
    r = crew.on_machine(fleet, t["machine"], ["bash", "-c", TAKE, "crew", place, unit, at, *deps])
    READ.drop_kit(t["machine"], t["kit"]["main"])
    if r.returncode == 3:
        _, other, *paths = r.stdout.strip().splitlines()[-1].split()
        fail(f"{kind} {unit}'s place can't take {other}'s work with the rest it comes after: they conflict on {', '.join(paths)}; "
             f"order what it comes after with crew {kind} after, then run " + ("code" if kind == "chore" else "construct") + " again")
    r.returncode == 0 or fail(f"on {t['machine']}: " + ((r.stderr or r.stdout).strip() or f"exit {r.returncode}"))
    return " ".join(f"{a}@{h}" for a, h in (l.split() for l in r.stdout.strip().splitlines() if l))


def merge_command(bolt):
    """How a unit, chore or fix merges into its bolt (teams.5, record 0026): only by a submission to sluice, sluice's
    verdict its gate, made without waiting so that the agent waits on it with `sluice wait`, a call at a time, which no
    capped command outlasts; sluice keeps the place, for crew to remove (plan.9). sluice queues and orders the
    submissions, so several may wait at once."""
    return f"sluice submit bolt/{bolt} --no-wait --json"


def run_check(fleet, a):
    """Whether a unit's stage may start, its place (made for construct), and the prompt the stage is sent, as facts for
    the stage's start (run_unit_stage): PLACE, BOLT, PROMPT, AMENDED, ENTRY, FORECAST and TOOK. Construct
    starts once each After unit has finished construct, never waiting on a merge (plan.13), and is run again at any
    stage before merge; on a unit whose change is committed, or one already amended, it first marks the unit amended in
    the plan at its head. Where that write is what marks the unit, only the conductor of the team holding its bolt, or
    the user, makes it; on a unit whose intent was amended, which the user approved, anyone starts its construct, and
    the prompt carries the amendment's words, read from the mark. Code starts once the change is committed, with no
    review between; code, verify, settle and merge wait while the mark stands (plan.6). Merge waits until its verify
    has delivered its report (record 0007) and each After unit has merged (teams.5), is refused while its bolt is split
    (split_refusal, plan.19), and a unit carried onto its bolt inside another's merge, whose place is gone, has its
    place made again from the bolt for its merge (teams.17), which holds the bolt's landing pull request first
    (merge_holds); settle runs only for a unit that has delivered its verify.
    crew chore run asks with --chore, and a chore's stages are chore_check's; a stage asked of the other kind is refused
    naming it (plan.11)."""
    label, repo, tip, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a), "chore" if a.chore else "unit")
    u = plan.item(a.unit)
    CONTEXT["kind"] = kind_of(u)  # a refusal is recorded on the chore's objects, or the unit's
    why = run_kind_refusal(kind_of(u), a.chore, a.unit, a.stage)
    not why or fail(why)
    if a.chore:
        return chore_check(fleet, a, label, plan, u)
    bolt = u.get("Bolt") or fail(f"unit {a.unit} is queued: move it into a bolt first")
    t = bolt_team(fleet, plan.bolt(bolt))
    st_all = Stages(fleet, plan, survey(fleet, [(t["name"], bolt, t["kit"]["name"])]))
    s = st_all.of(a.unit)
    st, place, mark = s["stage"], f"{t['kit']['dir']}/places/{a.unit}", u.get("Amended")
    st != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    why = left_refusal("unit", a.unit, bolt, s.get("left"))
    not why or fail(why)
    amended_at = entry = ""
    after = {d: st_all.of(d)["stage"] for d in u.all("After")}
    why = stage_refusal(a.unit, bolt, a.stage, st, mark, after, role(fleet, os.environ.get("CREW_AGENT")), t["name"],
                        s.get("open") or [], a.stage in ("settle", "merge") and st == "verify" and verified(label, a.unit),
                        bool(a.words), chores={d for d in u.all("After") if is_chore(plan.item(d))},
                        reports=team_state(t) / "reports")
    if why:
        refuse(*why) if isinstance(why, tuple) else fail(why)
    why = landing_refusal("unit", a.unit, a.stage, bolt, *landing_now(t, bolt))
    not why or fail(why)
    if a.stage == "construct":
        marking = bool(mark) or st in ("planned", "code", "verify")
        # The amendment's words, from the mark, so whoever starts the construct sends the same prompt.
        case = proposal(Plan(show(repo, tip, "proposals.rec") or PROPOSALS), mark.split("/", 1)[1], label).get("Case") \
            if amended(mark) and mark != "intent" else None
        _, kept = make_place(fleet, t, place, f"unit/{a.unit}", bolt)
        if kept:  # a branch an earlier drop kept, which this unit builds on (record 0003)
            print(f"{place} starts from the kept unit/{a.unit}, at {kept}")
        k, _ = st_all.kit(plan.bolt(bolt))
        deps = took_from(st_all, k, u)
        took = take(fleet, t, place, a.unit, bolt_at_of(k, bolt) if deps else None, deps)
        if marking:
            head = s.get("head") or host_run(fleet, t["machine"], HEAD, place)
            if head != mark:
                amended_at, entry = f"{repo}@{mark_amended(fleet, label, a.unit, bolt, head)}", CONTEXT["eid"]
        facts = dict(intent=u.get("Intent"), sources=u.all("Source"), again=again_words(mark, case))
    elif a.stage == "code":
        k, _ = st_all.kit(plan.bolt(bolt))
        facts = dict(overlaps=overlapping(plan, st_all, k, a.unit, declared(k, a.unit, "code")))
    elif a.stage == "verify":
        k, _ = st_all.kit(plan.bolt(bolt))
        got = (k["places"].get(a.unit) or {}).get("touches") or {}
        facts = dict(loose=undeclared(fleet, t, bolt_at_of(k, bolt), a.unit, got.get("entries", []), u.all("After")), touches=got)
    elif a.stage == "merge":
        split = bolt_split_check(fleet, t, bolt)
        why = split and split_refusal("unit", a.unit, bolt, t["machine"], *split)
        not why or fail(why)
        if not s.get("worktree"):  # carried onto the bolt inside another's merge, its place gone: made again from the bolt
            make_place(fleet, t, place, f"unit/{a.unit}", bolt)
        merge_carries(fleet, t, plan, st_all.kit(plan.bolt(bolt))[0], bolt, "unit", a.unit)
        merge_holds(fleet, t, bolt, f"unit {a.unit}'s merge into bolt/{bolt}")
        facts = dict(bolt=bolt, merge=merge_command(bolt))
    else:
        facts = {}
    # What reached the unit while no stage of it ran: forecasts, carried in this stage's prompt and named on its start.
    ids, said = carried_forecasts(fleet, t, plan, st_all, bolt, a.unit)
    prompt = stage_prompt(a.stage, a.unit, a.words, carried=said, **facts)
    # A construct that marked the unit amended: the plan's commit, and the entry it names, which the stage's start is.
    return dict(PLACE=place, BOLT=bolt, PROMPT=prompt, AMENDED=amended_at, ENTRY=entry, FORECAST=" ".join(ids),
                TOOK=took if a.stage == "construct" else "")


def merge_carries(fleet, t, plan, k, bolt, kind, name):
    """A unit's or chore's merge refused before its submission while its branch holds another unit's change open that
    its bolt does not hold archived (teams.17): read on the team's host, the branch's open changes in git and the bolt's
    archived ones as gathered (k), decided by carried_in and worded by carried_refusal. Refused when either can't be
    read (read.1)."""
    k or fail(f"can't tell what {kind}/{name} carries into bolt/{bolt}: its kit on {t['machine']} was not read")
    _, out = kit_git(fleet, t, t["kit"]["main"], "ls-tree", "-d", "--name-only", f"refs/heads/{kind}/{name}", "openspec/changes/")
    opened = [l[len("openspec/changes/"):] for l in out.splitlines() if l.startswith("openspec/changes/")]
    carried = carried_in(name, {u.name() for u in plan.units()}, opened, k["bolts"].get(bolt, {}).get("archived", []))
    not carried or fail(carried_refusal(kind, name, bolt, carried, bolt_order(plan, bolt)[1]))


def carried_in(name, units, opened, archived):
    """The changes a unit's or chore's branch holds open (opened) that are another unit's of the plan (units) and that
    its bolt does not hold archived (archived): what its merge would carry onto the bolt inside its own, which no merge
    may (teams.17). A change that is no unit's, as one main has held open since before archives, is not counted."""
    return sorted(c for c in opened if c != name and c in units and c not in archived)


def carried_refusal(kind, name, bolt, carried, after_of):
    """Why a merge is refused for the other units' changes its branch carries open (carried_in), naming each, and what
    the conductor does: a unit that comes after this one (after_of, plan.13) has its work taken out of this branch,
    since it merges later; any other merges first, its own merge archiving its change."""
    both = lambda xs: xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
    later = [c for c in carried if comes_after(after_of, c, name)]
    first = [c for c in carried if c not in later]
    return (f"{kind} {name} does not merge while {kind}/{name} holds the change" + ("" if len(carried) == 1 else "s")
            + f" of {both(carried)} open, which "
            f"bolt/{bolt} does not hold archived: no unit's change reaches a bolt inside another's merge; "
            + "; ".join(([f"{both(later)} " + ("comes" if len(later) == 1 else "come") + f" after {name}: take that work "
                          f"out of {kind}/{name} (crew {kind} run {name} code \"<what to take out>\")"] if later else [])
                        + ([f"merge {both(first)} first, each one's own merge archiving its change (crew unit run <unit> merge)"
                            if len(first) > 1 else f"merge {first[0]} first, its own merge archiving its change (crew unit run {first[0]} merge)"]
                           if first else [])))


def archives_owed(name, units, opened, ticked, specs):
    """The archives a unit's merge makes itself before its own (teams.17, record 0006): while its branch holds its own
    change open (opened), each other change it holds open that no unit of the plan has (units), every task ticked
    (ticked, change: bool), whose deltas touch a capability its own change's do, or one such change's do (specs,
    change: its capabilities), since openspec folds a delta only over the requirements the specs already hold. Another
    unit's change is that unit's own merge's to archive (carried_in). [] once its own is archived."""
    if name not in opened:
        return []
    can = {c for c in opened if c != name and c not in units and ticked.get(c)}
    caps, owed = set(specs.get(name, ())), set()
    while more := {c for c in can - owed if caps & set(specs.get(c, ()))}:
        owed |= more
        caps |= {cap for c in more for cap in specs.get(c, ())}
    return sorted(owed)


def archives_refusal(name, owed):
    """Why a unit's merge does not stop short while its branch holds archives it can make itself (archives_owed),
    naming each, and what it does instead: archives them, then its own, and submits."""
    both = lambda xs: xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
    one = len(owed) == 1
    return (f"merge on {name} does not stop short for archives it can make: unit/{name} holds {both(owed)} open, "
            + ("every task ticked, no unit's of the plan, and touching specs its change does" if one else
               "each with every task ticked, no unit's of the plan, and touching specs its change does")
            + "; a merge archives what its own archive needs first: archive " + ("it" if one else "each, oldest first,")
            + " with `openspec archive <change> --yes`, committed as `docs(openspec): archive <change>`, then "
            f"{name}'s own, and submit. If openspec refuses one of them, say so again with its words, and crew passes "
            "it on")


def merge_owes(fleet, t, name):
    """The archives a unit's merge stage could make itself (archives_owed), read on the team's host: the plan's units,
    and in git the changes its branch holds open, the tasks of each no unit of the plan has, and the capabilities each
    one's deltas touch. Refused when either can't be read (read.1)."""
    label = t["label"]
    plan = plan_of(fleet, label) or fail(f"can't tell which archives the merge on {name} can make: {label}/main could not be read")
    kt = unit_kit_team(fleet, label, t, name)
    main, ref = kt["kit"]["main"], f"refs/heads/unit/{name}"
    _, out = kit_git(fleet, kt, main, "ls-tree", "-r", "--name-only", ref, "openspec/changes/")
    files = {}
    for path in out.splitlines():
        c, _, rest = path[len("openspec/changes/"):].partition("/")
        if path.startswith("openspec/changes/") and rest and c != "archive":
            files.setdefault(c, []).append(rest)
    units = {u.name() for u in plan.units()}
    specs = {c: {r.split("/")[1] for r in rs if r.startswith("specs/") and r.count("/") > 1} for c, rs in files.items()}
    ticked = {}
    for c in sorted(set(files) - units - {name}):
        if "tasks.md" in files[c]:
            _, text = kit_git(fleet, kt, main, "show", f"{ref}:openspec/changes/{c}/tasks.md")
            tasks = gather.tasks_of(text)
            ticked[c] = bool(tasks) and all(done for done, _ in tasks)
    return archives_owed(name, units, sorted(files), ticked, specs)


def run_kind_refusal(kind, chore, name, stage):
    """Why a stage asked of a unit or chore is refused for its kind (plan.11), or None: crew unit run on a chore, which
    has no construct and no settle, or crew chore run (chore) on a unit, said with the command that runs it."""
    if kind == "chore" and not chore:
        if stage in ("construct", "settle"):
            return f"{name} is a chore, which has no {stage}: its stages are code, verify and merge (crew chore run {name} code)"
        return f"{name} is a chore: crew chore run {name} {stage}"
    if kind == "unit" and chore:
        return f"{name} is a unit: crew unit run {name} {stage}"
    return None


def landing_now(t, bolt):
    """What this host, the team's, holds of the bolt's landing (plan.8): the landing's worktree, <kit>/places/land-<bolt>
    (bolt_submit), whether it stands on bolt/<bolt>, and whether the process SUBMIT wrote into its git dir's
    crew-landing while sluice has the submission is alive. The worktree alone can outlive sluice's outcome, kept when
    git could not remove it or when the landing was stopped, until the tidy sweeps it with its bolt (tidy_over); its
    process cannot. (path, standing, alive)."""
    path = f"{t['kit']['dir']}/places/land-{bolt}"
    git = lambda *a: subprocess.run(["git", "-C", path, *a], capture_output=True, text=True, env=gitenv()).stdout.strip()
    if not os.path.isdir(path) or git("symbolic-ref", "-q", "--short", "HEAD") != f"bolt/{bolt}":
        return path, False, False
    try:
        pid = int(pathlib.Path(git("rev-parse", "--absolute-git-dir"), "crew-landing").read_text().strip())
        os.kill(pid, 0)
    except PermissionError:  # alive, as another user's
        return path, True, True
    except (OSError, ValueError):
        return path, True, False
    return path, True, True


def landing_refusal(kind, name, stage, bolt, path, standing, alive):
    """Why a unit's or chore's stage does not start while its bolt's landing is in flight (plan.8, record 0032 §3), or
    None: sluice lands the head that was submitted, so work merged into the bolt meanwhile is left out of main's
    landing and `crew bolt land` refuses until a second submission carries it. A construct, code or merge waits while
    the landing's worktree stands on the bolt's branch with its process alive (landing_now); a verify or settle starts,
    since it moves nothing toward the bolt, and so does every stage once sluice's outcome is in, landed or refused, so
    the fix that takes main into a refused bolt is never held."""
    if stage not in ("construct", "code", "merge") or not (standing and alive):
        return None
    return (f"bolt {bolt}'s landing is queued in sluice, submitted from {path}: {kind} {name}'s {stage} starts once it "
            f"has landed or been refused, since what merges into bolt/{bolt} meanwhile is left out of main's landing")


def split_refusal(kind, name, bolt, host, remote, f):
    """Why a unit's, chore's or fix's merge is refused while its bolt is split (plan.19), or None: the host's tip names
    remote for the bolt and that remote's bolt/<bolt> lacks it (f, kit.bolt_split), so sluice would form the merge
    there and drop what the host holds; the landing, whose push makes the two one, is the way on. A copy that holds the
    host's tip, or none at all, which sluice refuses itself, lets it through, and so does a fix whose head holds the
    host's tip (carried), having taken the host copy's merges in, which sluice's merge on the remote's copy then drops
    none of: the way on of a bolt whose two copies have diverged (landing_head). One crew could not read refuses
    (read.1)."""
    if f["read"]:
        return f"crew can't tell whether bolt/{bolt} is split, so {kind} {name}'s merge waits: {f['read']}"
    if f["there"] == "-" or f["held"] == "yes" or f.get("carried") == "yes":
        return None
    n = f["merges"]
    lacks = f"{host}'s tip" if not n else f"{n} merge{'' if n == 1 else 's'} {host} holds"
    carry = (f"; a fix that takes {host}'s merges in first (git merge bolt/{bolt} in its place) carries them, and merges"
             if kind == "fix" else "")
    return (f"bolt/{bolt} is split: its tip on {host}, {f['local'][:7]}, names {remote} for it, so sluice would form "
            f"{kind} {name}'s merge on {remote}'s bolt/{bolt} at {f['there'][:7]}, which lacks {lacks}, and drop "
            f"{'them' if n > 1 else 'it'}. The bolt takes no merge until it lands: its landing (crew bolt submit {bolt}, "
            f"main-level ops's on the user's word) pushes {host}'s tip to {remote} and makes the two one{carry}")


def landing_head(bolt, host, f):
    """The head a bolt's landing submits, from what it read of the bolt's two copies after one fetch (f,
    kit.land_copies; plan.19): {"head", "level", "said"}, or why it submits nothing. A bolt lands from where it lives.
    One whose copy on GitHub crew could not read submits nothing, in git's words (read.1). One that lives on its host,
    GitHub having no copy or GitHub's copy naming no remote for it, is submitted from the host's copy as it stands
    (head None), nothing levelled and nothing said. A bolt on GitHub is submitted at GitHub's head: the host's copy
    made there when the host has none, and levelled to it when it is behind, each said with both commits, or left
    alone when it is level. A host's copy ahead of GitHub's is the split a merge into the bolt is refused for, whose
    way on is this landing: its tip is submitted, nothing levelled, and its push moves GitHub's branch forward,
    dropping nothing. Two copies that have diverged submit nothing, naming both commits and what each lacks, since
    either submission would drop the other's merges, and the way on: the bolt is its branch on GitHub, so the host
    copy's merges are work only a fix carries, its place cut from GitHub's head and taking them in, merged into the
    bolt through sluice as any fix (split_refusal lets it through), after which the landing submits GitHub's head and
    levels the host's copy to it. level is whether SUBMIT writes the host's copy first, the one write the landing
    makes, the copy set to GitHub's own value, which changes nothing GitHub holds and is no second writer (record
    0032)."""
    def merges(n):
        return f"{n} merge{'' if n == 1 else 's'}"
    if f["read"]:
        return f"bolt/{bolt} was not submitted: crew can't read bolt/{bolt} on GitHub: {f['read']}"
    if f["there"] == "-" or f["remote"] is None:
        return dict(head=None, level=False, said=None)
    own, there = f["own"], f["there"]
    if own == "-":
        return dict(head=there, level=True, said=f"made {host}'s copy of bolt/{bolt} at GitHub's {there[:7]}")
    if own == there:
        return dict(head=there, level=False, said=None)
    if f["held"] == "yes":
        lacked = f", {merges(f['beyond'])} it lacked" if f["beyond"] else ""
        return dict(head=there, level=True,
                    said=f"levelled {host}'s copy of bolt/{bolt} from {own[:7]} to GitHub's {there[:7]}{lacked}")
    if f["ahead"] == "yes":
        return dict(head=own, level=False,
                    said=(f"bolt/{bolt} is split: {host}'s tip {own[:7]} holds {merges(f['lacks'])} GitHub's {there[:7]} "
                          "lacks; the landing submits that tip, its push moving GitHub's branch forward"))
    return (f"bolt/{bolt} was not submitted: its two copies have diverged: {host}'s {own[:7]} holds {merges(f['lacks'])} "
            f"GitHub's {there[:7]} lacks, and GitHub's holds {merges(f['beyond'])} {host}'s lacks, so either submission "
            f"would drop merges. The bolt is its branch on GitHub, so the way on is its team's: its conductor starts a fix "
            f"(crew fix), whose place is cut from GitHub's head, that takes {host}'s merges in (git merge bolt/{bolt}) and "
            f"merges into the bolt through sluice; the landing then submits GitHub's head, levelling {host}'s copy to it")


def chore_check(fleet, a, label, plan, c):
    """Whether a chore's stage may start (chore_refusal), its place (made at its first code, on chore/<name> from the
    bolt, tracking it, and taking the head of each unmerged unit or chore it comes after, as a unit's construct's place
    does, TOOK, plan.13), and the prompt the stage is sent (chore_prompt), as facts for the stage's start, as run_check
    gives a unit's. A merge is refused while its bolt is split (split_refusal, plan.19) or a commit of its own lacks the
    chore's trailer, which is how its merge and its landing are read (plan.11), and holds the bolt's landing pull
    request before it starts (merge_holds)."""
    bolt = c.get("Bolt") or fail(f"chore {a.unit} is queued: move it into a bolt first")
    t = bolt_team(fleet, plan.bolt(bolt))
    st_all = Stages(fleet, plan, survey(fleet, [(t["name"], bolt, t["kit"]["name"])]))
    s = st_all.of(a.unit)
    st, place = s["stage"], f"{t['kit']['dir']}/places/chore-{a.unit}"
    st != "unknown" or fail(f"cannot tell chore {a.unit}'s stage: {s.get('why')}")
    why = left_refusal("chore", a.unit, bolt, s.get("left"))
    not why or fail(why)
    after = {d: (st_all.of(d)["kind"], st_all.of(d)["stage"]) for d in c.all("After")}
    why = chore_refusal(a.unit, bolt, a.stage, st, after, a.stage == "merge" and st == "verify" and verified(label, a.unit))
    not why or fail(why)
    why = landing_refusal("chore", a.unit, a.stage, bolt, *landing_now(t, bolt))
    not why or fail(why)
    merge = took = ""
    if a.stage == "code":
        _, kept = make_place(fleet, t, place, f"chore/{a.unit}", bolt)
        if kept:  # a branch an earlier drop kept, which this chore builds on (record 0003)
            print(f"{place} starts from the kept chore/{a.unit}, at {kept}")
        k, _ = st_all.kit(plan.bolt(bolt))
        deps = took_from(st_all, k, c)
        took = take(fleet, t, place, a.unit, bolt_at_of(k, bolt) if deps else None, deps, "chore")
    elif a.stage == "merge":
        split = bolt_split_check(fleet, t, bolt)
        why = split and split_refusal("chore", a.unit, bolt, t["machine"], *split)
        not why or fail(why)
        loose = untrailed(chore_commits(fleet, t, bolt_at_of(st_all.kit(plan.bolt(bolt))[0], bolt), a.unit), a.unit)
        not loose or fail(f"chore {a.unit} merges only once every commit of its own beyond bolt/{bolt} carries `Chore: {a.unit}`, and "
                          + ", ".join(f"{sha} ({subject})" for sha, subject in loose) + (" does" if len(loose) == 1 else " do")
                          + f" not: run its code again to add the trailer (crew chore run {a.unit} code)")
        merge_carries(fleet, t, plan, st_all.kit(plan.bolt(bolt))[0], bolt, "chore", a.unit)
        merge_holds(fleet, t, bolt, f"chore {a.unit}'s merge into bolt/{bolt}")
        merge = merge_command(bolt)
    prompt = chore_prompt(a.stage, a.unit, c.get("Intent"), a.words, bolt, merge)
    return dict(PLACE=place, BOLT=bolt, PROMPT=prompt, AMENDED="", ENTRY="",
                FORECAST="", TOOK=took)


def left_refusal(kind, name, bolt, left):
    """Why no stage of a unit or chore starts while a place it has left stands at its path (left, as Stages.of marks a
    place tracking another bolt, kept from a drop or a move), or None: its stage cuts its place from bolt/<bolt>
    (make_place), never builds on that one, which the team's read before the stage removes when it is clean, its branch
    kept and built on when it holds work of its own (tidy_over, plan.10, record 0003); one the read kept, saying why, or
    left for a slot that holds it, waits for a hand."""
    if not left:
        return None
    return (f"{kind} {name}'s place {left['path']} tracks bolt/{left['bolt']}, which it has left for bolt/{bolt}, and still "
            f"stands: crew's tidy removes it only when it is clean, unlocked and no slot or run holds it, and once it is gone "
            f"{name}'s stage cuts its place from bolt/{bolt}")


def chore_refusal(name, bolt, stage, st, after, delivered_verify):
    """Why a chore's stage may not start, or None when it may (plan.11, plan.13, teams.5): stage is the one asked, st
    the chore's stage read from its kit, after each After unit's or chore's (kind, stage), delivered_verify whether its
    verify has delivered (verified). None runs on merged or landed work; code waits until each it comes after has
    something committed to build on, never a merge (built_on), and runs on a ready, coding or verified chore; verify
    once its place holds a commit of its own; merge once its verify has delivered, a fix round after it calling for no
    other (teams.17), and each it comes after has merged."""
    if stage not in ("code", "verify", "merge"):
        return f"a chore has no {stage}: its stages are code, verify and merge (crew chore run {name} code)"
    if st in ("merged", "landed"):
        return (f"chore {name} has " + ("merged into its bolt" if st == "merged" else "landed on main")
                + ": a defect in it is a fix (crew fix), and new maintenance a new chore")
    if st == "waiting":
        unbuilt = [d for d, (k, x) in after.items() if not built_on(k, x)]
        return (f"chore {name} is waiting: it comes after " + ", ".join(unbuilt) + (", which has" if len(unbuilt) == 1 else ", which have")
                + " nothing committed to build on yet")
    if stage == "code":
        return None
    if st == "ready":
        return f"chore {name} has not been coded yet: crew chore run {name} code"
    if st != "verify":
        return (f"chore {name} has nothing committed beyond bolt/{bolt} yet: "
                + ("verify waits for its code" if stage == "verify" else "it merges once its code is committed and its verify has delivered"))
    if stage == "merge" and not delivered_verify:
        return f"chore {name} merges once its verify has delivered: crew chore run {name} verify"
    ahead = [d for d, (_, x) in after.items() if stage == "merge" and x not in ("merged", "landed")]
    return f"chore {name} merges after " + ", ".join(ahead) + f", not yet merged into bolt/{bolt}" if ahead else None


def chore_prompt(stage, name, words_of, words="", bolt="", merge=""):
    """The prompt a chore's stage is sent (plan.11): code is told the chore and its words, `Chore <name>: <words>`,
    verify checks them, `Verify chore <name>: <words>`, and merge says how it merges into its bolt, as a unit's does;
    the conductor's or the user's words after the stage's own."""
    w = f" {words}" if words else ""
    if stage == "code":
        return f"Chore {name}: {words_of}{w}"
    if stage == "verify":
        return f"Verify chore {name}: {words_of}{w}"
    return f"Merge {name} into bolt/{bolt}: {merge}{w}"


# How a chore's own commits beyond its bolt are read: its first-parent line with no merges, so the work it took of what it
# comes after, merged in by TAKE, is not its own; each commit ended by NUL and its fields split by SOH, which no subject
# or name holds: its short sha, its subject, and the names its `Chore:` trailers give, joined by commas, as git parses them.
CHORE_LOG = ("log", "--reverse", "--first-parent", "--no-merges", "-z", "--abbrev=7",
             "--format=%h%x01%s%x01%(trailers:key=Chore,valueonly,separator=%x2c)")


def chore_commits(fleet, t, at, chore):
    """Each commit of the chore's own on chore/<chore> beyond its bolt, read at its ref (at, bolt_at_of), oldest first,
    read on the team's host (chore_log)."""
    return chore_log(kit_git(fleet, t, t["kit"]["main"], *CHORE_LOG, f"{at}..refs/heads/chore/{chore}")[1])


def chore_log(out):
    """CHORE_LOG's output as [(short sha, subject, [the names its Chore: trailers give])]."""
    fields = (r.split("\x01") for r in out.split("\0") if r.strip())
    return [(f[0].strip(), f[1], [n.strip() for n in f[2].split(",") if n.strip()]) for f in fields if len(f) == 3]


def untrailed(commits, chore):
    """The commits of a chore's branch beyond its bolt (chore_commits) that carry no `Chore: <chore>` trailer, as
    (short sha, subject): what a merge is refused for, since the bolt and main are read for the trailer (plan.11)."""
    return [(sha, subject) for sha, subject, names in commits if chore not in names]


def again_words(mark, case=None):
    """What construct run again on an amended intent adds to its prompt, from the unit's mark: the user's amendment, or
    an approved proposal's, with the planner's case as the user approved it; nothing for any other mark."""
    if mark == "intent":
        return " This unit's intent was amended by the user; revise the existing change to it."
    if amended(mark):
        return (f" This unit's intent was amended by proposal {mark.split('/', 1)[1]}; revise the existing change to it. "
                f"The planner's case, as the user approved it: {' '.join((case or '').split())}")
    return ""


def stage_prompt(stage, unit, words="", intent="", sources=(), again="", overlaps=(), loose=(), touches=None, bolt="",
                 merge="", carried=()):
    """The prompt a unit's stage is sent, the user's or conductor's words after the stage's own: construct proposes the
    change from the intent and its sources, with an amendment's words; code applies it, told each Touches it overlaps
    of an unmerged unit ahead of it; verify verifies it, told each path it changed and did not declare; settle names
    what reached it; merge says how the unit merges into its bolt. What reached the unit while no stage of it ran is
    carried at the end."""
    w = f" {words}" if words else ""
    if stage == "construct":
        prompt = f"/opsx:propose {unit} {intent}" + (" Sources: " + "; ".join(sources) + "." if sources else "") + again + w
    elif stage == "code":
        prompt = f"/opsx:apply {unit}{w}" + "".join(" " + x for x in overlaps)
    elif stage == "verify":
        touches = touches or {}
        prompt = f"/opsx:verify {unit}{w}" + (
            (" Changed and not declared in its Touches: " + ", ".join(loose) + "."
             + ("" if "entries" in touches else f" Its change declares no Touches: {touches.get('missing')}.")) if loose else "")
    elif stage == "settle":
        prompt = f"Settle {unit}:{w}"
    else:
        prompt = f"Merge {unit} into bolt/{bolt}: {merge}{w}"
    return prompt + "".join(" " + x for x in carried)


def stage_refusal(unit, bolt, stage, st, mark, after, caller, team, open_tasks, delivered_verify, has_words, chores=(),
                  reports="its team's reports folder"):
    """Why a unit's stage may not start, or None when it may (plan.6, plan.13, teams.5): stage is the one asked, st the
    unit's stage read from its place, mark its Amended mark, after each After unit's stage, caller the asker's (kind,
    team), team the name of the team holding its bolt, open_tasks the titles of its tasks still open, delivered_verify
    whether its verify has delivered its report since its change was last written (verified). A refusal that
    quotes typed text is (what is said, what the run record holds), else one string. Construct waits on its After
    units' construct, is never run on merged or landed work, and on a committed or amended unit is run again only by
    its conductor or the user, unless the user's approved amendment asked for it; every other stage waits while the
    mark stands; code needs the change committed; verify every task ticked; settle a delivered verify and what reached
    the unit; merge a verified unit, one whose verify delivered its report, named with the folder it is saved in
    (reports) when it did not (record 0007), whose After units have merged. chores names the After that are chores,
    whose code a unit's construct waits on as it waits on a unit's change (plan.13)."""
    if stage == "construct":
        if st == "waiting":
            deps = [d for d, x in after.items() if d not in chores and not built_on("unit", x)]
            uncoded = [d for d, x in after.items() if d in chores and not built_on("chore", x)]
            return (f"unit {unit} is waiting: it comes after "
                    + "; and ".join(([", ".join(deps) + ", whose change is not committed yet"] if deps else [])
                                    + ([f"chore {', '.join(uncoded)}, whose code has not delivered yet"] if uncoded else [])))
        if st in ("merged", "landed"):
            return (f"unit {unit} has " + ("merged into its bolt" if st == "merged" else "landed on main")
                    + ": a defect in it is a fix (crew fix), and a new need is a new unit")
        marking = bool(mark) or st in ("planned", "code", "verify")
        if marking and not amended(mark) and caller[0] != "user" and tuple(caller) != ("conductor", team):
            return (f"unit {unit} is in {st}, so construct run again marks it amended: a plan write only {team}-conductor "
                    "or the user makes")
        return None
    if st in ("amended", "construct") and mark:
        return f"unit {unit} was amended and " + (f"construct has not been run again (crew unit run {unit} construct)" if st == "amended"
                                                  else "its change is being written again, and has not been committed")
    if stage == "code":
        if st not in ("planned", "code", "verify"):
            return f"unit {unit} is in {st}: " + ("code waits until its change is committed" if st == "construct" else "it has no change to code yet")
        return None
    if stage == "verify":
        if st == "code":
            n = len(open_tasks)
            return (f"unit {unit} is in code, with these tasks still open: " + "; ".join(open_tasks),
                    f"unit {unit} is in code, with {n} task{'' if n == 1 else 's'} still open")  # titles are typed text
        return None if st == "verify" else f"unit {unit} is in {st}: verify waits until every task is ticked"
    if stage == "settle":
        if not (st == "verify" and delivered_verify):
            return (f"unit {unit} is in {st}" + (", and has not delivered its verify" if st == "verify" else "")
                    + ": settle runs only for a unit that has delivered its verify and waits to merge")
        return None if has_words else f"settle {unit} with what reached it: crew unit run {unit} settle \"<the forecast or the amendment>\""
    if st != "verify":
        return f"unit {unit} is in {st}: it merges once every task is ticked and verify has run"
    if not delivered_verify:
        return (f"unit {unit} merges only once its verify has delivered its report, and no verify since its change was "
                f"last written has: no report verify-{unit}-<YYYYMMDD-HHMM>.md was delivered from {reports} "
                f"(crew unit run {unit} verify)")
    ahead = [d for d, x in after.items() if x not in ("merged", "landed")]
    return f"unit {unit} merges after " + ", ".join(ahead) + f", not yet merged into bolt/{bolt}" if ahead else None


def amended_units(fleet, t):
    """The line a team's conductor is greeted with, or sent on crew resume, naming each unit of its bolt whose stage is
    amended, which no construct has run on since: "" when there is none. When the plan or the bolt's kit cannot be read
    it says so, rather than name no unit (read.1), and the greeting still goes out."""
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
    return amended_said(names, unread)


def amended_said(names, unread):
    """What a conductor brought back is told of its bolt's units that wait amended with no construct running (plan.15):
    each named, or that crew could not read whether any does, on one line; "" for none."""
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
    return " ".join(said)


def bolt_team(fleet, b):
    """The team holding a bolt, as it works on it: with the bolt's kit as its kit, since a team may hold several
    (record 0035); None when no team of the teams file holds it. Refused when the team builds no kit by the bolt's."""
    t = fleet["teams"].get(b.get("Team")) if b else None
    return crew.with_kit(t, b.get("Repo")) if t and b.get("Repo") else t


def held_repo(fleet, t):
    """The kit of the bolt a team builds (team_building), from its plan; None when it holds none. Refused when the plan
    can't be read, or which of two bolts it builds can't be told."""
    repo, ref = state_of(fleet, t["label"])
    tip = fetch(repo, ref) or fail(f"{repo} has no {ref} yet: crew state init {t['label']}")
    plan = read(repo, ref, tip)
    built = team_building(fleet, plan, t)
    return plan.bolt(built).get("Repo") if built else None


def at_work(fleet, name):
    """A team by name as it works on the bolt it holds (crew.held_team)."""
    return crew.held_team(fleet, crew.team_of(fleet, name))


def unit_kit_team(fleet, label, t, unit):
    """A team as it worked on a unit: with the kit of the unit's bolt as its kit, read from the plan, for a team that
    holds several kits; a team of one kit as it is. Refused when the plan can't be read or holds no such unit."""
    if len(crew.kits_of(t)) < 2:
        return t
    plan = plan_of(fleet, label) or fail(f"{label}/main could not be read, so the kit of {unit}'s bolt can't be told")
    u = plan.item(unit) or fail(f"{label}/main holds no unit {unit}")
    b = plan.bolt(u.get("Bolt")) if u.get("Bolt") else None
    (b and b.get("Repo")) or fail(f"{unit} is in no bolt of {label}/main, so the kit {t['name']} built it in can't be told")
    return crew.with_kit(t, b.get("Repo"))


def bolt_of_team(fleet, t):
    """The bolt a team builds (team_building), from its plan; refused when it holds none, the plan can't be read, or
    which of two bolts it builds can't be told."""
    repo, ref = state_of(fleet, t["label"])
    tip = fetch(repo, ref) or fail(f"{repo} has no {ref} yet: crew state init {t['label']}")
    return team_building(fleet, read(repo, ref, tip), t) or fail(f"{t['name']} holds no bolt: crew bolt give {t['name']}")


def fix_bolt(team, held, named, slotted, name):
    """The bolt a fix is of (teams.3, teams.16), from facts: held, the bolts the team holds, by name; named, the one
    --bolt names, or None; slotted, the fixes the team's slots hold (fix/<bolt>/<name>). The bolt named, refused when
    the team does not hold it; else the bolt of the fix by that name a slot holds, refused when one of each bolt does;
    else the one bolt held, refused when it holds none, or two, which a new fix names with --bolt."""
    if named:
        named in held or fail(f"{team} holds no bolt {named}: it holds " + (" and ".join(held) or "none"))
        return named
    mine = [b for b in held if f"fix/{b}/{name}" in slotted]
    len(mine) < 2 or fail(f"fix {name} is in flight on {' and '.join(mine)}: name its bolt with --bolt")
    if mine:
        return mine[0]
    held or fail(f"{team} holds no bolt: crew bolt give {team}")
    len(held) < 2 or fail(f"{team} holds {' and '.join(held)}: name the fix's bolt with --bolt")
    return held[0]


def fix_place(fleet, t, place, fix, bolt):
    """A fix's place made from the team's bolt, tracking it, and refused unless it is on the fix's own branch made
    from that bolt (teams.3, read.4). A place that could not be made ready is no refusal, since a fix is how a bolt is
    repaired (record 0028): what failed is returned, for the fix's agent to be told; None once it is ready."""
    unready, _ = make_place(fleet, t, place, fix, bolt, unready=True)
    why = own_place(place, *place_branch(fleet, t, place), fix, bolt)
    not why or fail(why)
    return unready


def fix_prompt(words, place, unready=None):
    """The prompt a fix's agent starts with: the fix's words, and when its place could not be made ready, what failed
    (kit.unready_said), so it knows what it stands in (teams.3, record 0028)."""
    return f"Fix: {words}" + (f" {kit.unready_said(place, unready)}" if unready else "")


def fix_in_slot(held, bolt, name, kdir):
    """What crew fix <name> acts on, from the team's slots file's lines (held): the slot holding fix/<bolt>/<name>, or
    the fix/<name> it was given before a fix's name held its bolt, with the branch and place that slot recorded; else
    no slot, and the branch and place a new fix of the bolt gets (teams.3)."""
    for want in (f"fix/{bolt}/{name}", f"fix/{name}"):
        for f in held:
            if len(f) >= 4 and f[2] == want:
                return f[0], f[2], f[3]
    return None, f"fix/{bolt}/{name}", f"{kdir}/places/fix-{bolt}--{name}"


def leftover(fix, place, team, place_there, branch_there):
    """Why a new fix is refused, or None (read.4): its place or its branch is already there, and no slot of the team
    holds it, so crew would be taking over what it did not make for this fix."""
    if place_there:
        return f"{fix} already has a place at {place} that no slot of {team} holds: name this fix differently"
    if branch_there:
        return f"{fix} already has a branch that no slot of {team} holds, though no place at {place}: name this fix differently"
    return None


def own_place(place, on, up, branch, bolt, does="starts a fix"):
    """Why a fix's place is not its own, or None (teams.3): it must be on the fix's branch (on: the one it is on, or is
    rebasing when a merge stopped partway through its rebase) made from the team's bolt (up: that branch's upstream,
    bolt/<bolt> or, for a bolt on GitHub, origin/bolt/<bolt>, gather.bolt_of). does is what crew does only in a fix's
    own place: starts or drops a fix."""
    if on == branch and gather.bolt_of(up) == bolt:
        return None
    return f"{place} is on {on or 'no branch'}, made from {up or 'no bolt'}, not {branch} from bolt/{bolt}: crew {does} only in its own place"


def fix_drop_why(fix, bolt, team, slot, place_there, branch_there, merged):
    """Why crew fix <name> --drop is refused, or None (teams.3, record 0028): the fix has merged into its bolt, so what
    it changed is the bolt's and a new fix undoes it; or no slot, place or branch of the team holds it."""
    if merged:
        return f"{fix} has merged into bolt/{bolt}, so it is not dropped: what it changed is the bolt's, and a new fix undoes it"
    if not (slot or place_there or branch_there):
        return f"{team} has no fix {fix}: no slot, place or branch holds it"
    return None


def place_branch(fleet, t, place):
    """What a place is on, read on the team's host: its branch, or the one it is rebasing when a merge stopped partway
    through its rebase, and that branch's upstream."""
    _, on = kit_git(fleet, t, place, "branch", "--show-current", ok=(0, 128))
    for d in ("rebase-merge", "rebase-apply"):
        if not on:
            _, at = kit_git(fleet, t, place, "rev-parse", "--path-format=absolute", "--git-path", f"{d}/head-name", ok=(0, 128))
            try:
                on = pathlib.Path(at).read_text().strip() if at else ""
            except OSError:
                on = ""
    on = on[len("refs/heads/"):] if on.startswith("refs/heads/") else on
    _, up = kit_git(fleet, t, place, "for-each-ref", "--format=%(upstream:short)", f"refs/heads/{on}", ok=(0, 128)) if on else (0, "")
    return on, up


def fix_cmd(fleet, a):
    """What crew fix decides before its stage, a.mode start, merge, drop or wait: the fix's bolt (BOLT, fix_bolt, by
    a.bolt while the team holds two) and its kit (REPO), the fix (FIX), its place (PLACE) and the slot holding it, if
    any (SLOT); for a merge, how it merges into the bolt (MERGE), by a submission to sluice as a unit's does, the bolt's
    landing pull request held first (merge_holds); for a drop, its branch when it is there (BRANCH). A name crew does
    not mint, a team holding no bolt, and a fix not in flight are refused; a new fix whose branch or place is
    already there (fix.start), a merge from a place not the fix's own or into a split bolt (fix.merge, split_refusal,
    plan.19), and a drop of a merged fix, of one
    nothing holds or of a place not the fix's own (fix.drop) are refused and recorded (teams.3, teams.5, record
    0028)."""
    t = at_work(fleet, a.team)
    crew.NAME.match(a.name) or fail("a fix is named with lowercase words and dashes")
    CONTEXT["label"] = t["label"]
    repo, ref = state_of(fleet, t["label"])
    tip = fetch(repo, ref) or fail(f"{repo} has no {ref} yet: crew state init {t['label']}")
    plan = read(repo, ref, tip)
    f = team_state(t) / "slots"
    lines = [l.split() for l in (f.read_text().splitlines() if f.exists() else []) if l.strip()]
    bolt = fix_bolt(t["name"], [b.name() for b in held_by(plan, t["name"])], getattr(a, "bolt", None),
                    [l[2] for l in lines if len(l) >= 3], a.name)
    t = crew.with_kit(t, plan.bolt(bolt).get("Repo"))  # a fix of a bolt in another of the team's kits is made in that kit
    slot, fix, place = fix_in_slot(lines, bolt, a.name, t["kit"]["dir"])
    a.mode in ("start", "drop") or slot or fail(f"{t['name']} has no fix {a.name} in flight")
    said = dict(BOLT=bolt, FIX=fix, PLACE=place, SLOT=slot or "", REPO=plan.bolt(bolt).get("Repo") or "")
    act = {"start": "fix.start", "merge": "fix.merge", "drop": "fix.drop"}.get(a.mode)
    try:
        if a.mode == "start" and not slot:
            why = leftover(fix, place, t["name"], os.path.exists(place),
                           kit_git(fleet, t, t["kit"]["main"], "rev-parse", "--verify", "-q", f"refs/heads/{fix}", ok=(0, 1))[0] == 0)
            not why or fail(why)
        elif a.mode == "merge":
            why = own_place(place, *place_branch(fleet, t, place), fix, bolt)
            not why or fail(why)
            split = bolt_split_check(fleet, t, bolt, f"refs/heads/{fix}")
            why = split and split_refusal("fix", a.name, bolt, t["machine"], *split)
            not why or fail(why)
            merge_holds(fleet, t, bolt, f"{fix}'s merge into bolt/{bolt}")
            said["MERGE"] = merge_command(bolt)
        elif a.mode == "drop":
            main, there = t["kit"]["main"], os.path.exists(place)
            branch = kit_git(fleet, t, main, "rev-parse", "--verify", "-q", f"refs/heads/{fix}", ok=(0, 1))[0] == 0
            why = fix_drop_why(fix, bolt, t["name"], slot, there, branch, branch and gather.fix_merged(main, fix, bolt))
            not why or fail(why)
            why = there and own_place(place, *place_branch(fleet, t, place), fix, bolt, "drops a fix")
            not why or fail(why)
            said["BRANCH"] = fix if branch else ""
    except Refusal as e:
        if act:
            record.emit(t["label"], act, [f"fix/{bolt}/{a.name}", f"bolt/{bolt}"], refused=str(e))
        raise
    return said


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


# What keeps a worktree from moving, by the file its git dir holds while it is in progress.
IN_PROGRESS = (("rebase-merge", "a rebase"), ("rebase-apply", "a rebase"), ("MERGE_HEAD", "a merge"), ("CHERRY_PICK_HEAD", "a cherry-pick"))


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
    return [dict(slot=slot, kind=kind, name=name, place=place, **dict(zip(("stage", "counts", "carried"), slot_stage(kind, name, kit, plan, bolts, marks))))
            for slot, kind, name, place in held]


def slot_stage(kind, name, kit, plan, bolts, marks):
    """The stage of the work a slot holds, and its tasks done and total where its change has a task list (teams.1):
    read from the kit as gathered (kit, unread unless ok) and the plan (None when it could not be read), bolts the
    names of those the team holds, marks the plan's Amended marks. A fix reads its stage from its branch's facts, its
    place's or, its place gone, its branch's (fix_stage); a unit or a chore has landed, merged into its bolt, been
    dropped from the plan, left the team's bolts, or reads its stage from its place. A unit has merged once its bolt
    holds its change archived; one whose change the bolt holds open, carried there inside another unit's merge, reads
    its stage from its place, or the bolt's change when its place is gone, with a third value, True, for carried
    (teams.17)."""
    if not kit.get("ok"):
        return "unknown", None
    if kind == "fix":
        f = next((f for f in kit["fixes"] if f["fix"] == name), None) or kit.get("fix_branches", {}).get(name)
        return (fix_stage(f, bool(plan.bolt(f["bolt"])) if plan and f["bolt"] else None) if f else "none"), None
    if kind == "chore":
        pl = kit.get("chore_places", {}).get(name)
        bolt = (pl or {}).get("bolt") or (plan.chore(name).get("Bolt") if plan and plan.chore(name) else None)
        if name in kit.get("chores", []):
            return "landed", None
        if bolt and name in kit["bolts"].get(bolt, {}).get("chores", []):
            return "merged", None
        if plan and not plan.chore(name):
            return "dropped", None
        if plan and plan.chore(name).get("Bolt") not in bolts:
            return "left", None
        return (chore_stage(name, bolt, kit, pl)[0] or "none") if pl else "none", None
    pl = kit["places"].get(name)
    if name in kit["main"]:
        return "landed", None
    bolt = (pl or {}).get("bolt") or (plan.unit(name).get("Bolt") if plan and plan.unit(name) else None)
    if bolt and name in kit["bolts"].get(bolt, {}).get("archived", []):
        return "merged", None
    if plan and not plan.unit(name):
        return "dropped", None
    if plan and plan.unit(name).get("Bolt") not in bolts:
        return "left", None
    carried = kit["bolts"].get(bolt, {}).get("open", {}) if bolt else {}
    pl = pl or (carried_place(carried[name]) if name in carried else None)
    if pl:
        return (place_stage(pl, marks.get(name)), "{}/{}".format(*pl["tasks"]) if pl["tasks"] else None) + ((True,) if name in carried else ())
    return "none", None


def fix_stage(f, planned):
    """A fix's stage from its branch's facts as gather reads them (gather.fix_facts) and whether its bolt is planned
    (True, False, or None when the plan could not be read or the fix tracks no bolt) (teams.1): landed once the kit's
    main holds its own work, its tip and it has moved, as a unit reads landed once main holds its change; merged once
    its bolt holds it; with its bolt in no plan, landed when main holds its tip, else dropped; else in flight. With the
    plan unread nothing is read dropped or landed by the plan (read.1)."""
    if f["on_main"] and f["moved"]:
        return "landed"
    if f["merged"]:
        return "merged"
    if planned is False:
        return "landed" if f["on_main"] else "dropped"
    return "fix"


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


def tidy(fleet, a):
    """Each worktree crew made in the team's kit checkout, on this host, whose work is over and that no slot holds:
    removed with its branch, saying the commit the branch was at, a unit's, chore's or fix's branch kept, named and
    recorded instead when git cherry finds work on it its bolt, or main once the bolt has landed or is gone, lacks
    (branch_gone, plan.10); or kept and named, with its branch, while it is locked or has uncommitted changes. The
    removal first releases the place through sluice, `sluice release --worktree <place>`, which runs the kit's policy's
    release command, ends what its runs left running and frees its ports, so what sluice stood up for it goes too; one
    sluice does not release, its release command having failed, is kept and named with its branch in sluice's words,
    and the next read tries it again (release_kept, plan.9). Then it goes through the kit's own `wt remove`, run from
    the kit's main checkout and leaving the branch to crew, so the kit's remove hooks run; one wt refuses, a hook having
    failed or waiting for the user's approval on this host, one wt leaves standing, or with no wt on this host's path, is
    kept and named with its branch, and the next read tries it again; when crew can't read from wt that it left the branch
    alone, the branch is kept and said. crew made it when it is directly in <kit>/bolts/ on bolt/<its folder>, or
    detached there, a bolt given before record 0026, or directly in <kit>/places/ on unit/<its folder>, on
    chore/<name> in chore-<name>, on bolt/<bolt> in land-<bolt>, or on a fix/ branch; nothing else is touched. While its
    bolt lasts, a bolt's worktree still on its branch is detached at the bolt's tip when it is clean, its branch then
    marked as crew's, and named as kept on the branch while it is not (bolt_detach, plan.18). A worktree the tidy would
    detach or remove is left as it is, named, while sluice's overview lists a run in it, or can't be read, read once and
    only then (run_kept, plan.9; sluice ADR 0024). The landing's place, which
    git could not remove after its submission or a stopped landing left, goes with its bolt, kept and named while its
    submission is still with sluice (landing_now), and leaves the bolt's branch to be judged in the same read. A bolt's
    branch crew marked, which no worktree holds, goes once no plan has the bolt, a landed bolt's only when main holds
    every commit of it, being kept, named and recorded otherwise (bolt_branch_gone, record 0003), and any other, a
    dropped bolt's among them, only by sluice's delete, which keeps it, marked dropped, named and recorded, while main
    lacks its tip, and is asked again once main holds it (bolt_branch_asked, plan.19); crew's marks are read
    once, before the worktrees are judged, so each place of a landed bolt is judged against main, and a mark whose branch
    sluice's delete removed is unset then, saying nothing (marks_gone, plan.19). At a landing (a.landed, the bolt), the
    landing's place gone, sluice is asked to delete the bolt's branch before it is judged (land_delete). A fix's branch
    no worktree and no slot holds goes once main or its bolt holds its tip (fix_branches_over). The worktrees are listed
    before the slots and plans are read: a plan has a bolt, a unit or a fix's bolt, and a slot is taken, before crew
    makes the worktree, so whatever is listed was planned or held by then. Nothing is removed when a plan the kit's work
    goes in can't be read. Once a worktree is removed, the command's next step reads the kit again."""
    t = at_work(fleet, a.team)
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
        print(unread_plans(errors))
        return
    bolts = {b.name() for *_, p in found for b in p.bolts() if b.get("Repo") == kit}
    units = {u.name(): u.get("Bolt") for *_, p in found for u in p.units() if u.get("Repo") == kit}
    chores = {u.name(): u.get("Bolt") for *_, p in found for u in p.chores() if u.get("Repo") == kit}
    now = gather.now_ref(gather.has_origin(main))  # the kit's main now, as Stages reads it (plan.18)
    ups, on_main = gather.upstreams(main), set(gather.changes(main, now))
    dropped, marks = fixes_dropped(main), bolt_marks(main)
    unmark_gone(main, marks)
    merged_now = []  # the bolt branches main now holds the tip of, read once and only for a dropped bolt's or a legacy one's

    def in_main():
        if not merged_now:
            merged_now.append(bolt_merged(main, now))
        return merged_now[0]
    fixes = gather.fix_facts(main, sorted({b for b in ups if b.startswith("fix/")}), ups, now)  # each fix branch's, read once

    def up_landed(branch):  # whether the bolt the branch tracks, the host's or GitHub's, is marked landed (record 0003)
        bolt = gather.bolt_ref(ups.get(branch, ""))[0]
        return bool(bolt) and marks.get(f"bolt/{bolt}") == "landed"
    chores_on = {}  # each branch's chores, read once each and only for a chore's place

    def chores_of(ref):
        if ref not in chores_on:
            chores_on[ref] = set(gather.chores(main, now if ref == "main" else f"refs/heads/{ref}"))
        return chores_on[ref]
    freed = set()  # the branches of the landings' places removed here
    overview = {}  # the runs sluice's overview lists, by canonical path, read once and only for a worktree that would go

    def run_in(p):
        if not overview:
            doc, why = sluice_read(main, "overview")
            runs = overview_runs(doc) if doc is not None else None
            overview.update(runs={os.path.realpath(k): v for k, v in (runs or {}).items()},
                            why=why or (None if runs is not None else f"it is not the {OVERVIEW} sluice 0.36.4 prints"))
        return run_kept(overview["runs"].get(os.path.realpath(p)), overview["why"])
    for w in trees:
        path, branch = w["path"], w.get("branch") or ""
        crews = tidy_over(path, branch, kdir, ups.get(branch, ""), bolts, units, on_main,
                          lambda bolt: gather.archived(main, f"bolt/{bolt}"), fixes.get, chores, chores_of, dropped)
        if crews is None:
            continue
        name, over = crews
        if not os.path.isdir(path):
            continue

        def status(p=path):
            r = subprocess.run(["git", "-C", p, "status", "--porcelain"], capture_output=True, text=True, env=gitenv())
            return r.returncode, r.stdout, r.stderr
        detach = bolt_detach(path, branch, kdir, over, w.get("locked"), status, lambda p=path: run_in(p))
        if detach:
            print(bolt_detached(main, path, branch) if detach[0] else f"{path} is kept on {branch}: {detach[1]}")
            continue
        if not over or name in held or path in held:
            continue
        landing = branch.startswith("bolt/") and name == f"land-{branch[5:]}"  # the landing's place (tidy_over)
        why = kept_why(over, w.get("locked"), None if w.get("locked") else status(), lambda p=path: run_in(p),
                       landing and landing_now(t, branch[5:])[2])
        held_too = f", and {branch} with it" if branch else ""  # a bolt's worktree the tidy detached holds no branch
        if why:
            print(f"{path} is kept{held_too}: {why}")
            continue
        kept = f"{path} is kept{held_too}: {over}, and "
        # sluice holds the release to the time limit its policy gives a run, as the kit's remove hooks run to their end
        unreleased = release_kept(*sluice_read(main, "release", "--worktree", path, timeout=None))
        if unreleased:
            print(kept + unreleased)
            continue
        try:  # the clean check above is the guard, so --force; the branch is crew's, so --no-delete-branch
            r = subprocess.run(["wt", "-C", main, "remove", path, "--foreground", "--no-delete-branch", "--force", "--format", "json"],
                               capture_output=True, text=True, stdin=subprocess.DEVNULL,
                               env={k: v for k, v in gitenv().items() if not k.startswith("WORKTRUNK_")})
        except FileNotFoundError:
            print(kept + f"wt, the kit's worktree tool, is not on {crew.this_host()}'s path")
            continue
        if r.returncode:
            print(kept + wt_refused(r.returncode, r.stderr, crew.this_host(), main))
            continue
        READ.drop_kit(t["machine"], t["kit"]["main"])  # the command's next step reads the kit again
        if os.path.isdir(path):
            print(kept + "the kit's wt remove exited 0 and left it there")
            continue
        if not branch:
            print(f"{path} is removed: {over}")
            continue
        if not wt_left_branch(r.stdout, path):
            print(f"{path} is removed, and {branch} is kept: crew could not read what wt remove said of the branch")
            continue
        if landing:  # the bolt's branch goes below, by crew's mark, now that no worktree holds it
            print(f"{path} is removed: {over}")
            freed.add(branch)
            continue
        if branch.startswith(("unit/", "chore/", "fix/")):  # judged by git cherry (plan.10)
            print(branch_gone(t, main, branch, ups.get(branch, ""), now, path, "it was dropped" if branch in dropped else over,
                              up_landed(branch)))
            continue
        mark = marks.get(branch)  # a legacy bolt's worktree, its branch judged by its mark
        print(bolt_branch_gone(t, main, branch, mark, now, bolts, False, mark == "dropped" and branch in in_main(), path)
              or f"{path} is removed: {over}")
    # A bolt is a branch with no worktree (record 0026): each one crew made, by its mark, goes once no plan has the bolt
    # and no worktree holds it, a landed bolt's only when main holds every commit of it, and any other by sluice's delete,
    # a dropped bolt's kept while main lacks its tip (plan.19); a deletion sluice's guard refuses, while a submission to
    # it waits, is kept and named.
    worked = {w.get("branch") for w in trees} - freed
    if getattr(a, "landed", None):  # the land's delete, asked now that the landing's place is gone (plan.19)
        b = f"bolt/{a.landed}"
        holder = next((w["path"] for w in trees if w.get("branch") == b), None) if b in worked else None
        print(land_delete(t, main, a.landed, holder))
        unmark_gone(main, marks)
        if marks.get(b) != "landed":  # asked of sluice once, here: only a landed mark is judged again below
            marks.pop(b, None)
    for branch in sorted(dropped - worked - held):  # a dropped fix's branch no worktree holds, its place gone already
        print(branch_gone(t, main, branch, ups.get(branch, ""), now, landed=up_landed(branch)))
    for branch, why in fix_branches_over(fixes, held | worked, dropped, bolts):
        sha = subprocess.run(["git", "-C", main, "rev-parse", "--short", "--verify", "-q", f"refs/heads/{branch}"],
                             capture_output=True, text=True, env=gitenv()).stdout.strip()
        r = subprocess.run(["git", "-C", main, "branch", "-q", "-D", branch], capture_output=True, text=True, env=gitenv())
        print(f"{branch} is removed: {why}; it was at {sha}" if r.returncode == 0 else f"{branch} is kept: {r.stderr.strip()}")
    for branch, mark in sorted(marks.items()):
        said = bolt_branch_gone(t, main, branch, mark, now, bolts, branch in worked, mark == "dropped" and branch in in_main())
        if said:
            print(said)


def bolt_marks(main):
    """crew's mark on each bolt branch of a kit checkout, {bolt/<bolt>: given, landed or dropped}, from the kit's git
    config, branch.bolt/<bolt>.crew, set given when crew makes the branch (BOLT_CREATE, bolt_detached), landed once
    sluice has landed it on main (LANDED) and dropped when sluice kept a dropped bolt's (bolt_branch_asked), which git
    drops with the branch and sluice's delete leaves (marks_gone; read.4, record 0003)."""
    out = gather.run(["git", "config", "--get-regexp", r"^branch\.bolt/.*\.crew$"], main) or ""
    return {k[len("branch."):-len(".crew")]: v for k, _, v in (l.partition(" ") for l in out.splitlines())}


def unmark_gone(main, marks):
    """Each of crew's marks (marks, bolt_marks) whose bolt branch is gone unset in the kit's git config and taken out of
    marks, saying nothing (marks_gone, plan.19)."""
    have = set((gather.run(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/bolt/"], main) or "").split())
    for branch in marks_gone(marks, have):
        subprocess.run(["git", "-C", main, "config", "--unset", f"branch.{branch}.crew"], capture_output=True, env=gitenv())
        del marks[branch]


def land_delete(t, main, bolt, held):
    """The land's delete of the bolt's branch, run by the tidy on the team's host once the landing's place is gone,
    `sluice branch delete bolt/<bolt> --into main` (BOLT_DELETE, plan.19), so sluice never deletes a branch from under
    a worktree, which its delete leaves on no branch (sluice 0.36.4, read 2026-10-22): what is said of it
    (deleted_said), and nothing asked while a worktree still holds the branch (held, its path)."""
    if held:
        return deleted_said(bolt, t["machine"], 0, "", "", held)
    r = subprocess.run(["bash", "-c", BOLT_DELETE, "crew", main, bolt, kit.DECLARATION], capture_output=True, text=True, env=gitenv())
    return deleted_said(bolt, t["machine"], r.returncode, r.stdout, r.stderr)


def marks_gone(marks, have):
    """The bolt branches crew's marks name (marks, bolt_marks) that are gone (have, the bolt branches the checkout has),
    in order (plan.19): sluice's delete removes a branch by ref edits, which leave its git config section, so the tidy
    unsets each such mark, saying nothing, rather than judge a branch that is not there on every read."""
    return sorted(b for b in marks if b not in have)


def fixes_dropped(main):
    """The fix branches of a kit checkout their conductor dropped (record 0028), by the mark crew fix --drop sets in
    the kit's git config, branch.<fix>.crew dropped, which git drops with the branch."""
    out = gather.run(["git", "config", "--get-regexp", r"^branch\.fix/.*\.crew$"], main) or ""
    return {k[len("branch."):-len(".crew")] for k, _, v in (l.partition(" ") for l in out.splitlines()) if v == "dropped"}


def branch_target(kind, up, up_exists, up_landed, main_ref):
    """What a branch whose place goes is compared with by git cherry (plan.10, record 0003), from plain facts: a unit's,
    a chore's or a fix's bolt, the branch it tracks (up), while that branch exists (up_exists) and is not marked landed
    (up_landed), else the kit's main now (main_ref, gather.now_ref), the only place its work could have arrived once its
    bolt has landed or been dropped, since a landed bolt can hold what main lacks, and a fix's bolt goes with its
    landing (teams.3); None for a fix tracking no bolt, which keeps it (record 0028). Whether the bolt exists is read
    apart from the upstream, which git still names once the branch is gone."""
    if kind == "fix" and not up:
        return None
    return up if up and up_exists and not up_landed else main_ref


def branch_kept(target, cherry):
    """Why a branch is kept when its place goes (plan.10, record 0003, record 0028), with how many commits it holds whose
    patch its target lacks, for the run record, None when git could not count them; or None when it goes: git cherry
    (exit, output, error) of the branch against target finds a commit whose patch target lacks (a + line), or can't
    compare the two, or there is no target, a fix tracking no bolt. A - line is a commit whose patch target holds under
    another hash, rebased as it merged, and a merge commit is not listed, so a branch that took another's head by a
    merge counts only its own."""
    if not target:
        return "it tracks no bolt to compare it with", None
    named = ref_named(target)
    code, out, err = cherry
    if code:
        return f"git cannot compare it with {named}: {' '.join(err.split()) or f'exit {code}'}", None
    n = sum(1 for l in out.splitlines() if l.startswith("+"))
    return (f"it holds {n} commit{'' if n == 1 else 's'} whose patch {named} lacks (git cherry), the user's to keep or "
            "delete", n) if n else None


def branch_gone(t, main, branch, up, now, path=None, over="it was dropped", landed=False):
    """A unit's, chore's or fix's branch once no worktree is on it, its place (path) removed now or before, its work
    over (over): compared by git cherry, in the kit's main checkout, with its bolt (up, the branch it tracks) while
    that branch stands and is not marked landed (landed), else with the kit's main now (now), a fix tracking no bolt
    with nothing (branch_target); deleted when it holds nothing its target lacks, else kept and named, a dropped fix's
    mark unset, so the user's from then on (branch_kept, plan.10, record 0003), and recorded once on the team's host as
    branch.kept, from its bolt, bolt/<bolt> whichever of its refs it tracks, when it was compared with it or the bolt has
    landed, since no later read reaches a branch no worktree is on. What crew says of it (branch_said)."""
    git = lambda *a: subprocess.run(["git", "-C", main, *a], capture_output=True, text=True, env=gitenv())
    kind = branch.split("/", 1)[0]
    sha = git("rev-parse", "--short", "--verify", "-q", f"refs/heads/{branch}").stdout.strip()
    ref = gather.bolt_ref(up)[1] or f"refs/heads/{up}"  # the host's bolt/<bolt> or GitHub's origin/bolt/<bolt>
    target = branch_target(kind, up, bool(up) and git("rev-parse", "--verify", "-q", ref).returncode == 0, landed, now)
    r = git("cherry", target, branch) if target else None
    kept = branch_kept(target, r and (r.returncode, r.stdout, r.stderr))
    if kept:
        why, n = kept
        git("config", "--unset", f"branch.{branch}.crew")
        why = kept_record(f"bolt {gather.bolt_ref(up)[0]} has landed", target, kept) if landed else over if n else f"{over}, and {why}"
        bolt = gather.bolt_ref(up)[0]  # recorded as the bolt, whichever of its refs the branch tracks (plan.19)
        record.emit(t["label"], "branch.kept", [branch, f"team/{t['name']}"], [f"bolt/{bolt}"] if bolt and (target == up or landed) else [],
                    why=why, Head=sha, Count=n)
        return branch_said(branch, path, sha, over, kept)
    r = git("branch", "-q", "-D", branch)
    return branch_said(branch, path, sha, over, None, (r.stderr.strip() or f"exit {r.returncode}") if r.returncode else None)


def branch_said(branch, path, sha, over, kept, refused=None):
    """What the tidy says of a branch whose place (path, None when it went before) is removed, its work over (over):
    removed, saying the commit it was at; kept as git refused its deletion (refused); or kept (kept, branch_kept's
    (why, count)) at its commit, the user's to keep or delete, and, for a unit's or a chore's, that the next of its
    name starts from it (plan.10, record 0003). A fix's keeps the words it had (record 0028)."""
    kind, name = branch.split("/", 1)
    lead = f"{path} is removed, and {branch}" if path else branch
    if refused:
        return f"{lead} is kept: {refused}"
    if not kept:
        return f"{path} and {branch} are removed; the branch was at {sha}" if path else f"{branch} is removed: {over}; it was at {sha}"
    why, n = kept
    said = f"{lead} is kept at {sha}: {over}, and {why}"
    if kind == "fix":
        return said
    said += "" if n else ", the user's to keep or delete"
    return said if kind == "bolt" else said + f"; a {kind} added as {name} starts from it"


def kept_record(over, target, kept):
    """The Why of a landed bolt's branch.kept entry, or of a branch of its work, composed from names (record.3): why it
    is over (over), and that main (target, which the run record has no kind for) lacks its patches, or git's words
    when it could not compare them (branch_kept's (why, count))."""
    why, n = kept
    return f"{over}, and {ref_named(target)} lacks its patches" if n else f"{over}, and {why}"


def ref_named(ref):
    """A ref as crew names it to the user: origin/main for refs/remotes/origin/main, a branch by its name."""
    return ref.split("/", 2)[-1] if ref.startswith("refs/") else ref


def fix_branches_over(facts, held, dropped, bolts):
    """Each fix branch no worktree holds whose work is over, for the tidy to remove (teams.3, plan.10), from each one's
    facts (facts, gather.fix_facts, by branch): of those no slot or worktree holds (held, the slots' names and places
    and the worktrees' branches) and their conductor did not drop (dropped, which branch_gone judges), each whose
    stage reads landed or merged (fix_stage, its bolt planned when it is in bolts), so main or its bolt holds its tip
    and nothing is lost; [(branch, why its work is over)] in name order. Any other is left as it is and not named."""
    out = []
    for branch, f in sorted(facts.items()):
        if branch in held or branch in dropped:
            continue
        stage = fix_stage(f, f["bolt"] in bolts if f["bolt"] else None)
        if stage in ("landed", "merged"):
            out.append((branch, "it has landed on main" if stage == "landed" else f"it has merged into bolt/{f['bolt']}"))
    return out


def bolt_branch_over(bolt, bolts, worktree):
    """Why a bolt's branch crew made, and holds no worktree of, is over (plan.9, record 0026): no plan has the bolt and
    no worktree holds the branch; else None, while the bolt is planned or held, or a worktree is on its branch."""
    return None if bolt in bolts or worktree else f"bolt {bolt} is in no plan"


def bolt_branch_judged(bolt, bolts, worktree, mark, in_main, target, cherry):
    """What becomes of a bolt's branch crew made (plan.9, plan.10, plan.19, record 0003), from plain facts: None while
    the bolt is planned (bolts) or a worktree holds the branch (worktree), left as it is; else (what crew does, why it
    is over, branch_kept's (why, count) or None). One marked landed (mark) is deleted with git ("delete") only when git
    cherry (cherry: exit, output, error) of it against the kit's main now (target) finds no commit whose patch main
    lacks, and is kept ("keep") otherwise, or when git cannot compare them (read.1). Any other is sluice's to delete
    ("ask", bolt_branch_asked), as a drop has it, never git's: one marked given, a dropped bolt's or one landed by a
    crew older than the landed mark, or a legacy bolt worktree's with no mark, once no plan has the bolt; and one
    marked dropped, which sluice kept at its drop, only once the kit's main holds its tip (in_main), sluice's own
    condition for the delete, left with nothing said while it does not."""
    over = bolt_branch_over(bolt, bolts, worktree)
    if not over:
        return None
    if mark == "landed":
        kept = branch_kept(target, cherry)
        return ("keep", f"bolt {bolt} has landed", kept) if kept else (
            "delete", f"bolt {bolt} has landed, and {ref_named(target)} holds every commit of it (git cherry)", None)
    if mark == "dropped":
        return ("ask", f"main now holds bolt {bolt}'s tip", None) if in_main else None
    return "ask", over, None


def bolt_branch_gone(t, main, branch, mark, now, bolts, worktree, in_main, path=None):
    """A bolt's branch crew made, by its mark (mark, bolt_marks), or a legacy bolt worktree's once its place (path) is
    removed: judged by bolt_branch_judged, a landed bolt's against the kit's main now (now) by git cherry, run only
    then; deleted, saying the commit it was at, or kept, its mark unset so no later read deletes it, named as the
    user's and recorded once on the team's host as branch.kept (record 0003); a deletion git or sluice's guard refuses
    is kept and named; any other asked of sluice (bolt_branch_asked, plan.19). None while the bolt lasts, or while a
    dropped bolt's kept branch waits for main to hold its tip (in_main)."""
    git = lambda *a: subprocess.run(["git", "-C", main, *a], capture_output=True, text=True, env=gitenv())
    bolt = branch.split("/", 1)[-1]
    r = git("cherry", now, branch) if mark == "landed" else None
    judged = bolt_branch_judged(bolt, bolts, worktree, mark, in_main, now, r and (r.returncode, r.stdout, r.stderr))
    if not judged:
        return None
    act, over, kept = judged
    if act == "ask":
        said = bolt_branch_asked(t, main, bolt, mark)
        return f"{path} is removed: {over}; {said}" if path else said
    sha = git("rev-parse", "--short", "--verify", "-q", f"refs/heads/{branch}").stdout.strip()
    if kept:
        git("config", "--unset", f"branch.{branch}.crew")
        record.emit(t["label"], "branch.kept", [branch, f"team/{t['name']}"], [branch], why=kept_record(over, now, kept),
                    Head=sha, Count=kept[1])
        return branch_said(branch, path, sha, over, kept)
    r = git("branch", "-q", "-D", branch)
    return branch_said(branch, path, sha, over, None,
                       f"{over}, and git refused to remove it: {' '.join(r.stderr.split()) or f'exit {r.returncode}'}" if r.returncode else None)


def bolt_branch_asked(t, main, bolt, mark):
    """A bolt's branch crew made, which sluice is to delete (bolt_branch_judged's "ask"): sluice's delete, `sluice branch
    delete bolt/<bolt> --into main`, run here, on the team's host, once no worktree holds the branch (BOLT_DELETE,
    plan.19), crew deleting nothing with git; when sluice refuses it a first time (exit 2), as it does while main lacks
    the tip, the host's branch marked dropped in the kit's git config, so the tidy knows it as a drop's kept work and
    not as one to delete (read.4), and recorded once on the team's host as branch.kept, from names (record.3); what is
    said of it (dropped_said), asked again for a branch marked dropped."""
    r = subprocess.run(["bash", "-c", BOLT_DELETE, "crew", main, bolt, kit.DECLARATION], capture_output=True, text=True, env=gitenv())
    again = mark == "dropped"
    h = None if r.returncode or again else delete_heard(bolt, t["machine"], r.stdout)
    if h and h["rc"] == 2:
        branch = f"bolt/{bolt}"
        git = lambda *a: subprocess.run(["git", "-C", main, *a], capture_output=True, text=True, env=gitenv())
        if git("rev-parse", "--verify", "-q", f"refs/heads/{branch}").returncode == 0:
            git("config", f"branch.{branch}.crew", "dropped")
        record.emit(t["label"], "branch.kept", [branch, f"team/{t['name']}"], [branch],
                    why=f"bolt {bolt} was dropped, and main does not hold its tip (sluice)", Head=h["tip"])
    return dropped_said(bolt, t["machine"], r.returncode, r.stdout, r.stderr, again)


def bolt_merged(main, now):
    """The bolt branches of a kit checkout whose tip the kit's main now (now) holds, by one listing (plan.19)."""
    return set((gather.run(["git", "for-each-ref", f"--merged={now}", "--format=%(refname:short)", "refs/heads/bolt/"], main) or "").split())


def bolt_detach(path, branch, kdir, over, locked, status, run):
    """Whether the tidy detaches a bolt's worktree from before record 0026 at its bolt's tip, so that no worktree of
    crew's holds a bolt branch (plan.9, plan.18): None for any worktree but one directly in <kit>/bolts/ on bolt/<its
    folder> while its bolt lasts (over, None), one whose bolt is over going as any finished worktree does; else (True,
    None) when it is clean, or (False, why it stays on the branch) when it is locked, git status (status(), read only
    then: exit, output, error) says it has uncommitted changes, git cannot read it, or, once it is clean, sluice's
    overview lists a run in it or can't be read (run(), run_kept's words or None, read only then), which is said on
    every read until it is clean and no run is in it."""
    if over or os.path.dirname(path) != os.path.join(kdir, "bolts") or branch != f"bolt/{os.path.basename(path)}":
        return None
    if locked:
        return False, "it is locked, and crew detaches it at the bolt's tip once it is not"
    code, out, err = status()
    if code:
        return False, f"git cannot read its status ({err.strip()}), so crew cannot tell it may detach it at the bolt's tip"
    if out.strip():
        return False, ("it has uncommitted changes, which are the user's to keep or discard, and crew detaches it at the "
                       "bolt's tip once it is clean")
    ran = run()
    if ran:
        return False, f"{ran}, and crew detaches it at the bolt's tip once no run is in it"
    return True, None


def bolt_detached(main, path, branch):
    """A clean bolt's worktree from before record 0026 detached at its bolt's tip (bolt_detach), `git switch --detach`
    in it, its files as they were; the bolt's branch then marked as crew's in the kit's git config, as a branch the give
    makes is (BOLT_CREATE), so it goes with the bolt once no worktree holds it (bolt_branch_over). What crew says of it,
    or why git refused."""
    git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True, env=gitenv())
    r = git("-C", path, "switch", "-q", "--detach")
    if r.returncode:
        return f"{path} is kept on {branch}: git could not detach it ({' '.join(r.stderr.split()) or f'exit {r.returncode}'})"
    git("-C", main, "config", f"branch.{branch}.crew", "given")
    sha = git("-C", path, "rev-parse", "--short", "HEAD").stdout.strip()
    return f"{path} is detached at {branch}'s tip, {sha}, so no worktree holds the bolt's branch"


def tidy_over(path, branch, kdir, up, bolts, units, on_main, archived_of, fix_of, chores=(), chores_of=None, dropped=()):
    """Whether a worktree is one crew made, and whether its work is over (plan.9): None for one crew did not make; else
    (the name a slot holds its work by, why its work is over or None while it goes on). crew made it when it is
    directly in <kit>/bolts/ on bolt/<its folder>, or detached there, as the tidy leaves it (bolt_detach), or directly
    in <kit>/places/ on unit/<its folder>, on chore/<name> in chore-<name>, on bolt/<bolt> in land-<bolt>, the landing's
    place (bolt_submit), or on a fix/ branch made from a bolt (up, its upstream, bolt/<bolt> or origin/bolt/<bolt>:
    gather.bolt_ref). A bolt's is over once no plan has the bolt (bolts), and so is its landing's, which the landing
    ends (plan.19); a unit's once it has landed on main (on_main), merged into its bolt (archived_of(bolt)), no plan
    has it (units, each unit's bolt by its name, None for one queued) or it has left the bolt its place tracks
    (left_over), merged meaning its bolt holds its change archived (archived_of(bolt), teams.17), never while the bolt
    holds it open; a chore's once main's or its bolt's history holds its trailer (chores_of(ref)), no plan has it
    (chores, each chore's bolt by its name) or it has left that bolt; a fix's once it has landed on main or merged into
    its bolt (fix_stage, on its branch's facts, fix_of(branch)), its conductor dropped it (its branch in dropped, record
    0028) or no plan has its bolt."""
    folder, bolt = os.path.basename(path), gather.bolt_of(up)
    if os.path.dirname(path) == os.path.join(kdir, "bolts") and branch in (f"bolt/{folder}", ""):
        return None, None if folder in bolts else f"bolt {folder} is in no plan"
    if os.path.dirname(path) == os.path.join(kdir, "places") and branch.startswith("bolt/") and folder == f"land-{branch[5:]}":
        return folder, None if branch[5:] in bolts else f"bolt {branch[5:]} is in no plan"
    if os.path.dirname(path) == os.path.join(kdir, "places") and branch.startswith("chore/") and folder == f"chore-{branch[6:]}":
        name = branch[6:]
        return name, (f"chore {name} has landed on main" if name in chores_of("main") else
                      f"chore {name} has merged into bolt/{bolt}" if bolt and name in chores_of(f"bolt/{bolt}") else
                      left_over("chore", name, bolt, chores[name]) if name in chores else f"chore {name} is in no plan")
    if os.path.dirname(path) == os.path.join(kdir, "places") and branch == f"unit/{folder}":
        return folder, (f"unit {folder} has landed on main" if folder in on_main else
                        f"unit {folder} has merged into bolt/{bolt}" if bolt and folder in archived_of(bolt) else
                        left_over("unit", folder, bolt, units[folder]) if folder in units else f"unit {folder} is in no plan")
    bolt = gather.bolt_ref(up)[0]  # a fix's, from either form of the bolt it tracks
    if os.path.dirname(path) == os.path.join(kdir, "places") and branch.startswith("fix/") and bolt:
        stage = fix_stage(fix_of(branch), bolt in bolts)
        return branch, (f"{branch} has landed on main" if stage == "landed" else
                        f"{branch} has merged into bolt/{bolt}" if stage == "merged" else
                        f"{branch} was dropped" if branch in dropped else
                        None if bolt in bolts else f"bolt {bolt}, which {branch} was made from, is in no plan")
    return None


def left_over(kind, name, bolt, now):
    """Why a unit's or chore's place is over once the plan holds it in another bolt than the one its place tracks
    (bolt), or in the queue (now, None there), as a slot's work is once it has left its team's bolt (teams.1): its work
    for that bolt is over, and a stage of its name cuts its place from the bolt it is in now (left_refusal). None while
    it is in that bolt, or when its place tracks no bolt crew can name, which it never removes on a guess (read.1)."""
    if not bolt or bolt == now:
        return None
    return f"{kind} {name} has left bolt/{bolt} for " + (f"bolt/{now}" if now else "the queue")


def unread_plans(errors):
    """What a tidy says when a plan the kit's work goes in could not be read, and so removes nothing (plan.9, read.1):
    each plan and why, on one line."""
    return "no worktree was removed: " + "; ".join(f"{k} could not be read: " + " ".join(v.split()) for k, v in errors.items())


def kept_why(over, locked, status, run, submitting=False):
    """Why a worktree whose work is over is kept, or None when it may go (plan.9): it is a landing's place whose
    submission is still with sluice (submitting, landing_now), it is locked, or git status (exit, output, error) says
    it has uncommitted changes, or git could not read it, or, when nothing else keeps it, sluice's overview lists a run
    in it or can't be read (run(), run_kept's words or None, read only then)."""
    if submitting:
        return f"{over}, and its submission is still with sluice"
    if locked:
        return "it is locked"
    code, out, err = status
    if code:
        return f"git cannot read its status: {err.strip()}"
    if out.strip():
        return f"{over}, and it has uncommitted changes, which are the user's to keep or discard"
    ran = run()
    return f"{over}, and {ran}" if ran else None


def overview_runs(doc):
    """The worktrees a run is in, as `sluice overview --json` lists them in sluice 0.36.4 (sluice ADR 0024 and 0035): the
    document is sluice/overview@1, each of its sessions[] names its worktree by its canonical path, and carries run,
    with when it started and, for a run of a command, the command, while a `sluice exec` runs there. Returns
    {worktree: its run}, or None when the document is not one sluice 0.36.4 prints."""
    if not isinstance(doc, dict) or doc.get("schema") != OVERVIEW or not isinstance(doc.get("sessions"), list):
        return None
    runs = {}
    for s in doc["sessions"]:
        if not isinstance(s, dict) or not isinstance(s.get("worktree"), str):
            return None
        if isinstance(s.get("run"), dict):
            runs[s["worktree"]] = s["run"]
    return runs


def run_kept(run, unread):
    """Why the tidy leaves a worktree it would detach or remove as it is, for a run sluice has in it (plan.9; wldn's
    signal 2026-10-20-swb-2-ops-20f43d6b/01, a legacy bolt worktree detached 45 s into a run in it): its run, as
    overview_runs reads it (run), named by its command, or as its checks, and when it started; or why sluice's overview
    could not be read (unread), so crew can't tell that no run is in it (read.1). None when neither."""
    if unread:
        return f"sluice's overview can't be read ({unread}), so crew can't tell whether a run is in it"
    if run is None:
        return None
    command = run.get("command")
    what = f"a run in it, `{command}`" if isinstance(command, str) and command else "a run of its checks in it"
    since = f", started {run['started']}" if isinstance(run.get("started"), str) else ""
    return f"sluice's overview lists {what}{since}"


def release_kept(doc, unread):
    """Why the tidy keeps a worktree it would remove once sluice was asked to release it, `sluice release --worktree
    <place> --json`, which runs the kit's policy's release command, ends what the place's runs left running and frees
    its ports, the worktree staying (plan.9; sluice 0.36.4, `exec::release`): sluice refused or failed it, a release
    command that failed among them, in its words (unread, sluice_read's), and keeps the place to release at the next
    read; or it answered with no document sluice 0.36.4 prints, {"released", "worktree"} (read.2). None once it
    answered, whether the place held anything to release or not, so the kit's worktree tool may remove it."""
    if unread:
        return f"sluice's release of it failed: {unread}"
    if not (isinstance(doc, dict) and isinstance(doc.get("released"), bool) and isinstance(doc.get("worktree"), str)):
        return "sluice's release of it printed no document crew reads"
    return None


def wt_refused(code, stderr, host, main):
    """Why the kit's wt remove kept a worktree, from its exit and its standing error, in its own words without its
    advice to skip the hooks or approve them unseen (its ↳ lines): its hooks wait for the user's approval on the host,
    or its ✗ lines, else its last line."""
    said = [l.strip() for l in stderr.splitlines() if l.strip() and not l.strip().startswith("↳")]
    if any("Cannot prompt for approval" in l for l in said):
        return f"the kit's remove hooks wait for the user's approval on {host}: wt config approvals add, in {main}"
    return "the kit's wt remove refused it: " + "; ".join([l[1:].strip() for l in said if l.startswith("✗")] or said[-1:]
                                                         or [f"wt remove exited {code}"])


def wt_left_branch(out, path):
    """Whether wt remove's JSON answer says it removed this one worktree and left its branch alone, for crew to judge."""
    try:
        told = json.loads(out)
        return (len(told) == 1 and os.path.realpath(told[0]["path"]) == os.path.realpath(path)
                and told[0]["branch_outcome"] == "not_attempted")
    except (ValueError, TypeError, KeyError, IndexError):
        return False


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
    """A stage crew owes an end, from its line in the team's stages file: <slot> <unit, chore, fix branch or bolt>
    <stage> <start entry id> <object>. A unit's stages are construct, code, verify, settle and merge; a chore's, code,
    verify and merge, its object chore/<name> (plan.11); a fix's, fix and merge, its name its branch and its object
    fix/<bolt>/<name>. A line ops's proof of a bolt left, stage proof in the slot ops, from before a bolt's proof was
    its verification (record 0025), is owed nothing and dropped when read (stage_ends)."""

    def __init__(self, t, fields):
        self.t, self.fields = t, list(fields)
        self.slot, self.name, self.stage, self.eid, self.obj = (self.fields + [""] * 5)[:5]
        self.agent = f"{t['name']}-{self.slot}"
        self.start = started(self.eid)
        self.proof = self.stage == "proof"
        self.fix = self.name.startswith("fix/")
        self.chore = self.obj.startswith("chore/")
        self.kind = "chore" if self.chore else "unit"

    def branch(self):
        """The branch whose head an end names: the unit's, the chore's or the fix's."""
        return self.name if self.fix else f"{self.kind}/{self.name}"

    def phrase(self):
        """The stage as the wait names it."""
        if self.fix:
            return f"fix {self.obj or self.name}" if self.stage == "fix" else f"{self.stage} of {self.obj or self.name}"
        return f"{self.stage} on {'chore ' if self.chore else ''}{self.name}"

    def on(self):
        if self.fix:
            return [self.obj or self.name, f"agent/{self.agent}"]
        return [f"stage/{self.name}/{self.stage}", f"{self.kind}/{self.name}", f"agent/{self.agent}"]

    def why(self, ended):
        how = "stopped short" if ended == "short" else "ended"
        if self.fix:
            return f"fix({self.name.rsplit('/', 1)[-1]}): {self.stage} {how}"
        return f"{self.kind}({self.name}): {self.stage} {how}"


def short_head(main, ref):
    return (gather.run(["git", "rev-parse", "--short", "--verify", "-q", ref], main) or "").strip()


def committed_at(main, ref):
    """When a branch's head was committed, in UTC, or None."""
    at = gather.head_at(main, ref)
    try:
        return datetime.datetime.fromisoformat(at).astimezone(datetime.timezone.utc) if at else None
    except ValueError:
        return None


def ticks(main, rev, unit):
    """A unit's tasks at a commit, done and total, read from the commit and not the working tree, by the reading every
    other reader of a unit's tasks uses (gather.tasks_of)."""
    tasks = gather.tasks_of(gather.run(["git", "show", f"{rev}:openspec/changes/{unit}/tasks.md"], main) or "")
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


def bolt_of_unit(fleet, t, main, unit, kind="unit"):
    """The bolt a unit's or chore's branch was made from and merges into, from its upstream; else the bolt the team
    builds (team_building)."""
    bolt = gather.bolt_of(gather.upstreams(main).get(f"{kind}/{unit}"))
    if bolt:
        return bolt
    plan = plan_of(fleet, t["label"])
    return team_building(fleet, plan, t) if plan else None


def merge_bolt(plan, team, name):
    """The bolt a unit's or chore's merge look reads, from the plan as it stands: the one the plan places it in now,
    held by the team whose wait looks, and that bolt's kit, (bolt, repo, None); else (None, None, why). Never the bolt
    its branch was cut from, which it may since have left, nor another team's, neither of which can hold its merge."""
    u = plan.item(name)
    if u is None:
        return None, None, f"the plan holds no {name}"
    b = plan.bolt(u.get("Bolt")) if u.get("Bolt") else None
    if b is None:
        return None, None, f"the plan places {name} in no bolt"
    if b.get("Team") != team:
        return None, None, f"the plan places {name} in bolt {b.name()}, which {team} does not hold"
    return b.name(), b.get("Repo"), None


def deliverable(fleet, t, o, place=None):
    """What an owed stage has delivered since it began, read on the team's host: (its object, what the wait says of
    it), or (None, what is missing), as delivered judges the facts deliverable_facts reads."""
    return delivered(o, deliverable_facts(fleet, t, o, place))


def deliverable_facts(fleet, t, o, place=None):
    """What delivered judges an owed stage by, read on the team's host, only what its stage asks: the newest verify
    report saved since it began; for a merge, the bolt it merges into, a fix's from its name and a unit's or chore's
    from the plan as each look reads it (merge_bolt), or why there is none crew can read (unplaced), whether that bolt
    holds it, a unit's change archived too, and its head, read in the bolt's kit where the bolt is read
    (gather.bolt_read) once its GitHub is fetched, or why it could not be fetched (fetch) or read (unread); for a
    chore's code, its own newest commit and when it was committed; else the branch's head and when it was committed, a
    code stage's ticks at that head, and, for a construct with a commit since it began, whether its planning is
    complete. The head is read once and the rest read at that commit, never at the branch again: an agent that commits
    between the reads would pair one commit's time or ticks with another's sha."""
    main, f = t["kit"]["main"], {}
    if o.start is None:
        return f
    if o.stage == "verify":
        f["saved"], f["folder"] = newest_saved(t, gather.REPORT, o.name, o.start), team_state(t) / "reports"
        return f
    if o.stage == "merge":
        if o.fix:
            f["bolt"] = o.obj.split("/")[1] if o.obj.count("/") == 2 else None
        else:
            errors = {}
            found = plans(fleet, [t["label"]], errors)
            p = found[0][3] if found else None
            f["bolt"], repo, f["unplaced"] = merge_bolt(p, t["name"], o.name) if p else (
                None, None, "; ".join(f"{k} could not be read: {v}" for k, v in errors.items()) or f"{t['label']} has no plan yet")
            try:
                main = crew.with_kit(t, repo)["kit"]["main"] if repo else main
            except Refusal as e:
                f["bolt"], f["unplaced"] = None, str(e)
        if f["bolt"]:
            # Each look fetches GitHub first: sluice lands the merge there, and moves neither the host's copy nor its
            # tracking ref when it pushes as its app (plan.19).
            why = gather.fetched(main)
            if why:
                f["fetch"] = why
                return f
            ref, why = gather.bolt_read(main, f["bolt"])
            if not ref:
                f["unread"] = why or f"this host has neither bolt/{f['bolt']} nor origin/bolt/{f['bolt']}"
                return f
            f["holds"] = (gather.fix_merged(main, o.name, f["bolt"], ref) if o.fix else
                          o.name in gather.chores(main, ref) if o.chore else o.name in gather.changes(main, ref))
            if not (o.fix or o.chore):
                f["archived"] = o.name in gather.archived(main, ref)
            f["bolt_head"] = short_head(main, ref)
        return f
    if o.chore:  # its own newest commit: what its place took of what it comes after is not its code (plan.13)
        bolt = bolt_of_unit(fleet, t, main, o.name, "chore")
        head, at = gather.own_head(main, o.branch(), bolt) if bolt else (None, None)
        try:
            f["head"], f["at"] = head, datetime.datetime.fromisoformat(at).astimezone(datetime.timezone.utc) if at else None
        except ValueError:
            f["head"], f["at"] = head, None
        return f
    f["head"] = short_head(main, f"refs/heads/{o.branch()}")
    at = f["head"] or f"refs/heads/{o.branch()}"
    f["at"] = committed_at(main, at)
    if o.fix or o.stage == "settle":
        return f
    if o.stage == "code":
        f["ticks"] = ticks(main, at, o.name)
        return f
    if f["head"] and f["at"] is not None and f["at"] >= o.start:
        place = place or f"{t['kit']['dir']}/places/{o.name}"
        planned = gather.planned(f"{place}/openspec/changes/{o.name}", place)
        if planned is None:
            status = gather.run(["openspec", "status", "--change", o.name, "--json"], place)
            try:
                planned = bool(json.loads(status).get("isPlanningComplete")) if status else False
            except (ValueError, AttributeError):
                planned = False
        f["planned"] = planned
    return f


def delivered(o, f):
    """What an owed stage has delivered, judged from deliverable_facts (teams.4): (its object, what the wait says of
    it), or (None, what is missing). construct: a commit on the unit's branch since the start, with its planning
    complete; code: a commit since the start, every task ticked at the head; verify: a report for the unit saved since
    the start, its lack named with the folder crew reads; settle: a commit on the unit's branch since the start
    (teams.14); merge: the bolt holding the unit's change archived, which its merge does first (teams.17), the chore's
    trailer or the fix's commits; a fix, and a chore's code: a commit on its branch since the start (record 0007). A
    start crew can't read delivers nothing."""
    if o.start is None:
        return None, f"no start crew can read in its entry {o.eid}"
    if o.stage == "verify":
        saved, folder = f.get("saved"), f.get("folder")
        if saved:
            return f"report/{saved.name}", f"the report is {saved}"
        return None, f"no report verify-{o.name}-<YYYYMMDD-HHMM>.md saved in {folder} since it began" if folder else "no report saved"
    if o.stage == "merge":
        bolt, head = f.get("bolt"), f.get("bolt_head")
        if not bolt:
            return None, "no bolt crew can read for it" + (f": {f['unplaced']}" if f.get("unplaced") else "")
        if f.get("fetch"):
            return None, f"can't fetch bolt/{bolt} from GitHub: {f['fetch']}"
        if f.get("unread"):
            return None, f"can't read bolt/{bolt}: {f['unread']}"
        if f.get("holds") and f.get("archived") is False:
            return None, f"bolt/{bolt} holds its change open: its merge did not archive it first"
        return (f"bolt/{bolt}@{head}", f"bolt/{bolt} holds it at {head}") if f.get("holds") and head else (None, f"bolt/{bolt} not yet holding it")
    head, at = f.get("head"), f.get("at")
    fresh = bool(head) and at is not None and at >= o.start
    if o.fix or o.chore:
        return (f"{o.obj or o.name}@{head}", f"its branch is at {head}") if fresh else (None, "nothing committed since it began")
    if o.stage == "settle":
        return (f"unit/{o.name}@{head}", f"its branch is at {head}, ready to merge") if fresh else (None, "nothing committed since it began")
    if o.stage == "code":
        done, total = f.get("ticks") or (0, 0)
        if fresh and total and done == total:
            return f"unit/{o.name}@{head}", f"every task is ticked ({done}/{total}) at {head}"
        return None, (f"{done} of {total} tasks ticked at its head" if total and done < total else
                      "no commit since it began" if total else "no task list at its head")
    if not fresh:
        return None, "nothing committed"
    return (f"unit/{o.name}@{head}", f"its change is committed at {head}") if f.get("planned") else (None, "its planning not complete")


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
    s = (now if now is not None else {x["slot"]: x for x in slot_stages(fleet, t)}).get(o.slot, {})
    result, tasks = s.get("stage", "unknown"), s.get("counts")
    record.emit(t["label"], "stage.end", o.on(), why=o.why(ended), Result=result, Tasks=tasks,
                Head=short_head(main, f"refs/heads/{o.branch()}"), Ended=ended, Delivered=delivered,
                Observed="late" if late else None)


def unmark(fleet, t, o):
    """Once an amended unit's construct has delivered, its mark stops counting, and crew removes it from the plan in a
    write that carries the construct's end (plan.6). A mark that still waits for construct, one set again meanwhile, or
    a write that fails is said on standard error and changes nothing else: the mark no longer counts either way."""
    if o.fix or o.stage != "construct":
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
    dropped without an entry, and so is a line ops's proof left (record 0025)."""
    t = at_work(fleet, a.team)
    held = {l.split()[0]: l.split() for l in (team_state(t) / "slots").read_text().splitlines() if l.strip()} \
        if (team_state(t) / "slots").exists() else {}
    with stages_file(t) as lines:
        keep, ended = [], []
        for l in lines:
            o = Owed(t, l)
            if a.slot and o.slot != a.slot:
                keep.append(l)
                continue
            if o.proof or o.slot not in held or held[o.slot][2] != o.name:
                continue
            if a.ending:
                got, _ = deliverable(fleet, t, o, held.get(o.slot, [None] * 4)[3])
                ended.append((o, "delivered" if got else "stopped", got))
            elif crew.agent_status(fleet, o.agent, fresh=False) != "working":
                got, _ = deliverable(fleet, t, o, held.get(o.slot, [None] * 4)[3])
                (ended.append((o, "delivered", got)) if got else keep.append(l))
            else:
                keep.append(l)
        now = {s["slot"]: s for s in slot_stages(fleet, t)} if ended else {}
        for o, how, got in ended:
            record_end(fleet, t, o, how, got, late=how == "delivered", now=now)
        lines[:] = keep
    for o, how, _ in ended:
        if how == "delivered":
            unmark(fleet, t, o)


# ----------------------------------------------------------------------------------- what reaches a unit

def merge_tree(main, ours, theirs, base=None):
    """The paths git merge-tree forecasts in conflict when theirs is merged into ours, from their merge base or from
    the base given (git 2.40+), [] for a clean merge, or None when git can't tell. It writes objects and no ref."""
    r = subprocess.run(["git", "-C", main, "merge-tree", "--write-tree", "--name-only", "--no-messages",
                        *([f"--merge-base={base}"] if base else []), ours, theirs], capture_output=True, text=True, env=gitenv())
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
    it has one, else on the bolt, where it is read (gather.bolt_read)."""
    pl = k["places"].get(unit)
    if pl:
        path = f"{pl['path']}/openspec/changes/{unit}/"
        try:
            text = pathlib.Path(path, "proposal.md").read_text()
        except OSError:
            text = None
    else:
        path, at = f"{kdir}/bolts/{bolt}/openspec/changes/{unit}/", read_at(k, bolt)
        text = gather.run(["git", "show", f"{at}:openspec/changes/{unit}/proposal.md"], main) if at else None
    why, items = case_of(text)
    return (f"{unit}'s change is {path}." + (f" Its Why: {why}" if why else "")
            + (" What it changes: " + " ".join(items) if items else ""))


def forecast_words(t, k, bolt, unit, other, paths, left_out=()):
    """What a forecast says to the later unit: the conflicting paths, how to resolve them keeping both intents, and the
    other unit's change, or, for a conflict with the bolt, how to rebase (rebase_words, left_out the After units' work
    a dependent's rebase left out) and the change of each unit merged since the unit's place was made (teams.13)."""
    main, kdir, on = t["kit"]["main"], t["kit"]["dir"], ", ".join(paths)
    if other == f"bolt/{bolt}":
        at = read_at(k, bolt)
        base = gather.run(["git", "merge-base", at, f"unit/{unit}"], main) if at else None
        since = [c for c in gather.changes(main, at) if c not in (gather.changes(main, base.strip()) if base else [])] if at else []
        return (f"Your branch is forecast to conflict with bolt/{bolt} on {on}. {rebase_words(bolt, left_out, at)}, resolve "
                "each conflict keeping both changes' intents, run the tests those paths affect, and commit."
                + "".join(" Merged since your place was made: " + change_words(main, kdir, k, bolt, c) for c in since))
    return (f"Your merge after {other}, ahead of you in the bolt and not merged, is forecast to conflict on {on}. You merge "
            f"after it: take its work into your place (git merge unit/{other}), resolve each conflict keeping both changes' "
            f"intents, run the tests those paths affect, and commit. " + change_words(main, kdir, k, bolt, other))


def rebase_words(bolt, left_out=(), at=None):
    """How a unit is told to rebase its place onto its bolt, where the bolt is read (at, gather.bolt_read): a bolt on
    GitHub, origin/bolt/<bolt>, fetched first, since the place's own copy of it is as the host last fetched it; else the
    host's bolt/<bolt>. Onto the bolt alone; or, for a dependent whose rebase at its After units' merge left their work
    out as its place took it (left_out, <unit>@<head> words), from the upstream crew's own rebase used, a commit whose
    parents are the bolt and those heads (ONTO), so it meets no conflict on their files. That commit has no ref, and
    nothing keeps it: the words give the command that makes it again, from the bolt as it then stands and heads the
    place holds (plan.13)."""
    ref = at or f"bolt/{bolt}"
    fetch = "git fetch origin && " if ref.startswith("origin/") else ""
    if not left_out:
        return f"Rebase your place onto the bolt ({fetch}git rebase {ref})"
    names, heads = zip(*(w.split("@", 1) for w in left_out))
    work = f"{names[0]}'s work" if len(names) == 1 else f"the work of {', '.join(names[:-1])} and {names[-1]}"
    parents = " ".join(f"-p {h}" for h in (ref,) + heads)
    return (f"Rebase your place onto the bolt, leaving out {work} as your place took it, which the bolt holds as merged "
            f"({fetch}git rebase --onto {ref} $(git commit-tree {parents} -m upstream '{ref}^{{tree}}'))")


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
    status = crew.agent_status(fleet, o.agent, fresh=False) if o else None
    way = reach_way(bool(o), status, stage, stage == "verify" and verified(t["label"], unit, entries))
    if way == "told":
        return "told" if crew.tell(fleet, o.agent, words) else None
    if way == "settle":
        try:  # in this process, on the team's host, as crew unit run starts it; what it says is not the wait's
            with contextlib.redirect_stdout(io.StringIO()):
                run_unit_stage(fleet, crew.Team(fleet, t), unit, "settle", words)
        except (Refusal, Stopped) as e:
            print(f"crew could not start {unit}'s settle stage" + (f": {e}" if isinstance(e, Refusal) else ""), file=sys.stderr)
            return None
        return "settle"
    return way


def reach_way(owed, status, stage, verified):
    """How a forecast or an amendment reaches a unit, once (teams.12, teams.14): not yet while the agent of the stage it
    owes is working; told to that agent while it is up; as a settle stage when the unit has delivered its verify and
    waits to merge (verified); else carried in its next stage's prompt."""
    if owed and status == "working":
        return None
    if owed and status:
        return "told"
    return "settle" if stage == "verify" and verified else "prompt"


# A dependent's place rebased onto its bolt, given by the ref it is read at (gather.bolt_read): printed "rebased" when
# it moved, nothing when it was already there; a
# rebase that conflicts is aborted, the place as it was, and printed "conflict <paths...>", exit 3. The heads given
# after the bolt, of merged After units as the place took them, are left out with the bolt's commits: the rebase
# replays what is beyond both, from a commit with no ref whose parents are the bolt and those heads.
ONTO = r"""cd "$1" || exit 1
at=$2; shift 2
git merge-base --is-ancestor "$at" HEAD && exit 0
upstream=$at
if [ $# -gt 0 ]; then
  parents=(-p "$upstream"); for h; do parents+=(-p "$h"); done
  upstream=$(git commit-tree "${parents[@]}" -m "crew: the bolt and the heads taken" "$upstream^{tree}") || exit 1
fi
if git rebase -q --onto "$at" "$upstream" >/dev/null 2>&1; then echo rebased; exit 0; fi
paths=$(git diff --name-only --diff-filter=U | tr '\n' ' ')
git rebase --abort >/dev/null 2>&1
echo "conflict $paths"; exit 3
"""


def landed_at(main, bolt, unit, kind="unit", at=None):
    """The commit on a bolt that brought a unit's change there, the first that holds its folder, or a chore's work, the
    first carrying its trailer (plan.11), read where the bolt is read (at, else gather.bolt_read); None when it holds
    none or the bolt can't be read. A unit lands on its bolt in sluice's merge commit with its change already archived
    (teams.17, record 0026), so the bolt's own side never held the folder: --full-history follows the merge's other
    parent, which git's default simplification prunes."""
    at = at or gather.bolt_read(main, bolt)[0]
    if not at:
        return None
    where = ([f"--grep=^Chore: {unit}$", at] if kind == "chore" else ["--full-history", at, "--", f"openspec/changes/{unit}"])
    out = gather.run(["git", "log", "--format=%H", "--reverse", *where], main)
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
    """Each unmerged unit or chore of the team's bolt with a place, one of whose After units or chores has merged since
    its place last met the bolt, is rebased onto the bolt, only while its agent is not working and its place is clean
    (teams.2, plan.9): the bolt's commits drop out of it, and so does each merged After's work as its place took it
    (rebase_leaves_out, from the run record's Took). A unit's rebase that conflicts is aborted, the place as it was, and
    returned to reach the dependent as a conflict does, with what it left out: [(bolt, unit, paths, <after>@<head>
    words)]; a chore's is said, since no forecast reaches a chore, and its merge meets it. say(text) reports what was
    done or left."""
    main, out, entries = t["kit"]["main"], [], None
    owed = owed_by_unit(t)
    for b in held_by(plan, t["name"]):
        k, _ = st.kit(b)
        at = read_at(k, b.name()) if k else None
        if not at:
            continue
        for u in plan.work_of(b.name()):
            kind = kind_of(u)
            pl = (k.get("chore_places", {}) if kind == "chore" else k["places"]).get(u.name())
            if not pl or st.of(u.name())["stage"] in ("merged", "landed", "unknown"):
                continue
            merged = [a for a in u.all("After") if st.of(a)["stage"] in ("merged", "landed")]
            due = [a for a in merged if (lambda c: c and subprocess.run(["git", "-C", main, "merge-base", "--is-ancestor", c, f"refs/heads/{kind}/{u.name()}"],
                                                                       env=gitenv()).returncode != 0)(landed_at(main, b.name(), a, st.of(a)["kind"], at))]
            if not due:
                continue
            o = owed.get(u.name())
            waits = rebase_waits(u.name(), b.name(), due, o and crew.agent_status(fleet, o.agent, fresh=False), lambda: clean(pl["path"]), pl["path"])
            if waits:
                say(waits)
                continue
            entries = local_entries(t["label"]) if entries is None else entries
            branch = f"refs/heads/{kind}/{u.name()}"
            holds = lambda head: subprocess.run(["git", "-C", main, "merge-base", "--is-ancestor", head, branch], env=gitenv(),
                                                stderr=subprocess.DEVNULL).returncode == 0
            left_out = rebase_leaves_out(due, took_heads(u.name(), entries), holds)
            r = subprocess.run(["bash", "-c", ONTO, "crew", pl["path"], at, *(w.split("@", 1)[1] for w in left_out)],
                               capture_output=True, text=True, env=gitenv())
            READ.drop_kit(t["machine"], main)
            if r.returncode == 3 and kind == "chore":
                say(f"rebasing chore {u.name()} onto bolt/{b.name()} conflicts on {', '.join(r.stdout.strip().split()[1:])}: its place "
                    "is as it was, and its merge meets the conflict")
            elif r.returncode == 3:
                out.append((b.name(), u.name(), r.stdout.strip().split()[1:], left_out))
                say(f"rebasing {u.name()} onto bolt/{b.name()} conflicts: its place is as it was, and it is told")
            elif r.returncode:
                say(f"{u.name()} was not rebased onto bolt/{b.name()}: " + ((r.stderr or r.stdout).strip() or f"exit {r.returncode}"))
            elif r.stdout.strip() == "rebased":
                record.emit(t["label"], f"{kind}.rebase", [f"{kind}/{u.name()}", f"bolt/{b.name()}"], frm=[f"{st.of(a)['kind']}/{a}" for a in due],
                            why=f"{kind}({u.name()}): rebase onto bolt/{b.name()}, now that {', '.join(due)} merged")
                say(f"{u.name()} is rebased onto bolt/{b.name()}, now that {', '.join(due)} merged")
    return out


def rebase_leaves_out(due, took, holds):
    """Each of a dependent's merged After units (due) whose head its place took (took, {after unit: head}) and still
    holds (holds(head)), as <unit>@<head>, in due's order: its rebase onto the bolt leaves their work out as it took it,
    since the bolt holds that work as it merged, rewritten since by a rebase or a settle (plan.13). [] when it took none
    or holds none of them, and it is rebased onto the bolt alone."""
    return [f"{a}@{took[a]}" for a in due if took.get(a) and holds(took[a])]


def rebase_waits(unit, bolt, due, status, is_clean, path):
    """Why a dependent whose After units (due) have merged is not rebased onto its bolt yet, or None when it is
    rebased now: its agent is working, or its place is not clean (is_clean(), read only when its agent is not)."""
    if status == "working":
        return f"{unit} waits to be rebased onto bolt/{bolt}, now that {', '.join(due)} merged: its agent is working"
    if not is_clean():
        return f"{unit} waits to be rebased onto bolt/{bolt}, now that {', '.join(due)} merged: {path} has uncommitted changes or work in progress"
    return None


def rebase_and_tidy(fleet, t, landed=None):
    """The end of a team's read: each dependent whose After unit has merged is rebased (rebase_dependents), a conflict
    waiting for the conductor's next wait, which tells the dependent; then the team's tidy runs, whether or not the
    rebase was refused, at a landing (landed, the bolt) having sluice delete the bolt's branch once the landing's place
    is gone (land_delete); then each bolt the team holds that is local until it lands is said, once (bolts_local_said,
    plan.19). What any of them refuses is said on standard error."""
    plan = None
    try:
        plan = plan_of(fleet, t["label"])
        if plan:
            rebase_dependents(fleet, t, plan, stages_for(fleet, plan, held_by(plan, t["name"])), print)
    except Refusal as e:
        print(e, file=sys.stderr)
    try:
        tidy(fleet, argparse.Namespace(team=t["name"], landed=landed))
    except Refusal as e:
        print(e, file=sys.stderr)
    try:
        for said in bolts_local_said(fleet, t, plan) if plan else []:
            print(said)
    except Refusal as e:
        print(e, file=sys.stderr)


def amendments(t, plan, st, entries):
    """For each dependent with a place, each After unit constructed again since the dependent's construct took its
    head (amended_afters), git telling whether the head the dependent took already holds the new one."""
    holds = lambda held, head: subprocess.run(["git", "-C", t["kit"]["main"], "merge-base", "--is-ancestor", head, held],
                                              env=gitenv()).returncode == 0
    return amended_afters(held_by(plan, t["name"]), plan, lambda n: st.of(n)["stage"], entries, holds)


def amended_afters(bolts, plan, stage_of, entries, holds):
    """For each unmerged dependent of the bolts, each After unit constructed again since the dependent's construct took
    its head: [(bolt, dependent, after unit, its new head)], from the run record's entries. A construct whose head the
    dependent already holds (holds(the head it took, the new head)), such as one recorded late, is no amendment."""
    out = []
    for b in bolts:
        for u in plan.units_of(b.name()):
            if stage_of(u.name()) in ("merged", "landed", "unknown") or not u.all("After"):
                continue
            starts = construct_starts(u.name(), entries)
            if not starts:
                continue
            since = (starts[0]["At"], starts[0]["Id"])
            took = took_heads(u.name(), entries)
            for a in u.all("After"):
                ends = [e for e in entries if e.get("Act") == "stage.end" and f"stage/{a}/construct" in e["On"]
                        and e.get("Ended") == "delivered" and (e["At"], e["Id"]) > since]
                head = (ends[-1].get("Delivered") or "").rpartition("@")[2] if ends else ""
                held = took.get(a)
                if head and head != held and not (held and holds(held, head)):
                    out.append((b.name(), u.name(), a, head))
    return out


def construct_starts(unit, entries):
    """A unit's construct starts that were not refused, from the run record's entries, in their order."""
    return [e for e in entries if e.get("Act") == "stage.start" and f"stage/{unit}/construct" in e["On"] and not e.get("Refused")]


def took_heads(unit, entries):
    """The head of each unit or chore it comes after that a unit's construct, or a chore's code, took into its place,
    from those starts' Took (<name>@<sha7> words), the latest taking of each: {name: head}. A start recorded before
    Took existed, or one whose place already held work of its own, took none."""
    starts = [e for e in entries if e.get("Act") == "stage.start" and not e.get("Refused")
              and any(o in e["On"] for o in (f"stage/{unit}/construct", f"stage/{unit}/code"))]
    return dict(w.split("@", 1) for e in starts for w in (e.get("Took") or "").split() if "@" in w)


def reach(fleet, t):
    """On each of the conductor's waits, before it waits: for each unmerged unit of the team's bolt with a place, git
    merge-tree on the team's host forecasts its merge with the bolt and with each unmerged unit ahead of it in the file's
    order, writing no ref, a dependent's with a unit it comes after from the head its place took; a unit that
    conflicts with the bolt resolves that first, and is forecast against the units ahead of it once it is clean with
    the bolt. A conflict is a forecast for the later unit, recorded once for a pair of
    heads (`forecast`, with both heads, the paths and how it reached the unit) and reaching it once (deliver). The
    earlier unit is told nothing, and the forecast orders neither: a settle that takes the other's work does, and an
    order of crew's own whose settle found nothing to change is lifted, both before the forecasts (settle_orders,
    plan.13). What crew can't read or write here is said on standard error, and the wait goes on (teams.12)."""
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
    ordered = settle_orders(fleet, t, plan, st)
    for text in ordered:
        say(text)
    if ordered:  # the forecasts read the plan as crew's own orders left it
        plan = plan_of(fleet, label) or plan
        bolts = held_by(plan, t["name"])
        st = stages_for(fleet, plan, bolts)
    entries = local_entries(label)
    done = {e.get("Heads") for e in entries if e.get("Act") in ("forecast", "amendment") and e.get("Heads")}
    for bolt, name, paths, left_out in met:
        k, _ = st.kit(plan.bolt(bolt))
        pl = (k or {"places": {}})["places"].get(name)
        bhead = (k or {"bolts": {}})["bolts"].get(bolt, {}).get("head")
        heads = f"{name}@{(pl or {}).get('head', '')[:7]} bolt/{bolt}@{(bhead or '')[:7]}"
        if not pl or not bhead or heads in done:
            continue
        way = deliver(fleet, t, entries, name, st.of(name)["stage"],
                      forecast_words(t, k, bolt, name, f"bolt/{bolt}", paths, left_out))
        if way:
            record.emit(label, "forecast", [f"unit/{name}", f"bolt/{bolt}"], why=f"unit({name}): rebase onto bolt/{bolt} conflicts",
                        Heads=heads, Paths=" ".join(paths), Reached=way, Took=" ".join(left_out))
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
        live = [(u.name(), k["places"][u.name()]["head"], u.all("After")) for u in plan.units_of(b.name())
                if k["places"].get(u.name()) and k["places"][u.name()].get("head")
                and st.of(u.name())["stage"] not in ("merged", "landed", "unknown")]
        took = {name: took_heads(name, entries) for name, _, _ in live}
        due, unread = forecasts_due(live, b.name(), k["bolts"].get(b.name(), {}).get("head"),
                                    lambda o, h, base: merge_tree(main, o, h, base), done, took, bolt_order(plan, b.name())[1])
        for name, other in unread:
            print(f"no forecast of {name} against {other}: git merge-tree could not read them", file=sys.stderr)
        for name, other, paths, heads in due:
            way = deliver(fleet, t, entries, name, st.of(name)["stage"], forecast_words(t, k, b.name(), name, other, paths))
            if way:
                record.emit(label, "forecast", [f"unit/{name}", other if other.startswith("bolt/") else f"unit/{other}"],
                            why=f"unit({name}): forecast to conflict with {other}", Heads=heads, Paths=" ".join(paths), Reached=way)
                done.add(heads)
    # The bolt itself against its kit's main and what is queued there, by sluice's forecast (teams.21).
    for b in bolts:
        k, _ = st.kit(b)
        if not k:
            continue  # said above
        checked, kept = bolt_check(k["team"]["kit"], b.name())
        if kept:
            say(kept)
        doc, why = bolt_forecast_read(*checked)
        if why:
            said = unread_said(b.name(), k["bolts"].get(b.name(), {}).get("head"), why, done)
            if said:
                heads, words = said
                say(words)
                if heads:
                    record.emit(label, "forecast", [f"bolt/{b.name()}"], why=f"bolt({b.name()}): no forecast against main",
                                Heads=heads, Reached="wait")
                    done.add(heads)
            continue
        bolt_said(fleet, t, b, doc, done, len(bolts) > 1, say)


def bolt_said(fleet, t, b, doc, done, two, say):
    """What a conductor's wait does with sluice's forecast of a bolt against main (teams.21), doc as bolt_forecast_read
    gives it: said once (bolt_forecast) and recorded on bolt/<bolt> with its Heads and Paths; and a conflict with what
    main has landed, meeting no submission queued there, changes the kit's landings card at once (land_hand), so the
    bolt's row takes main first without waiting for main to move again (bolt-teams "A wait's forecast conflict with main
    changes the kit's landings card"); one with a queued submission hands nothing."""
    told = bolt_forecast(t["name"], t["label"], b.name(), doc, done, two)
    if not told:
        return
    heads, paths, words = told
    say(words)
    record.emit(t["label"], "forecast", [f"bolt/{b.name()}"], why=f"bolt({b.name()}): forecast to conflict with main",
                Heads=heads, Paths=" ".join(paths), Reached="wait")
    done.add(heads)
    if "#" not in heads:  # with no note of its own: the card changes only when the bolt's row does
        land_hand(fleet, t["label"], b.get("Repo") or t["kit"]["name"])


def sluice_check(main, bolt):
    """`sluice submit main --check --head bolt/<bolt> --json` run in the kit's main checkout on this host, which needs
    no worktree on the bolt's branch (sluice's ADR 0039): (its exit, its output, its standard error), the exit None when
    it could not be run, the error then its why."""
    try:
        r = subprocess.run(["sluice", "submit", "main", "--check", "--head", f"bolt/{bolt}", "--json"], cwd=main,
                           capture_output=True, text=True, timeout=POLL)
    except FileNotFoundError:
        return None, "", "this host has no sluice on its path"
    except subprocess.TimeoutExpired:
        return None, "", f"it did not answer within {POLL} seconds"
    except OSError as e:
        return None, "", str(e)
    return r.returncode, r.stdout, r.stderr


# What a conductor's wait reads of a bolt before sluice forecasts it (plan.19), in its kit's main checkout with no fetch
# (plan.18), $bolt and $file its arguments: TIP, the commit of the host's own bolt/<bolt>, or - when it has none; AT_TIP,
# the policy ($file) at that commit, base64, or - when it holds none, as sluice reads a branch's policy; and TRACKED, the
# remotes this host holds a tracking ref of the branch from, as it last fetched them.
BOLT_TIP = r"""cd "$1" || exit 1
bolt=$2 file=$3
tip=$(git rev-parse --verify -q "refs/heads/bolt/$bolt^{commit}") || tip=-
echo "TIP=$tip"
if [ "$tip" != - ] && text=$(git show "$tip:$file" 2>/dev/null); then
  echo "AT_TIP=$(printf '%s\n' "$text" | base64 | tr -d '\n')"
else echo "AT_TIP=-"; fi
echo "TRACKED=$(git for-each-ref --format='%(refname)' "refs/remotes/*/bolt/$bolt" | sed -n "s|^refs/remotes/\([^/]*\)/bolt/$bolt\$|\1|p" | tr '\n' ' ')"
"""

# A legacy bolt's forecast from a place on it (plan.19, forecast_way), in its kit's main checkout: a worktree already on
# bolt/<bolt> is a place on it, the landing's while its submission is with sluice (bolt_submit) or a bolt's own from
# before record 0026 the tidy kept on its branch, and is read as it stands; else crew makes its own at the path given,
# on the branch with no checkout, since sluice reads only its head, and removes it once sluice has answered, as it does
# one a forecast that was stopped left there. Nothing moves the branch. Prints NOSLUICE when the host has no sluice,
# making nothing; PLACE, the worktree sluice forecast from, or - with WHY, git's words, when none could be made; RC and
# SAID, sluice's exit and its answer, base64; and KEPT, crew's own place when git could not remove it, with WHY.
FORECAST_PLACE = r"""main=$1 path=$2 bolt=$3
cd "$main" || exit 1
command -v sluice >/dev/null || { echo "NOSLUICE=yes"; exit 0; }
on=$(git worktree list --porcelain | awk -v want="branch refs/heads/bolt/$bolt" '/^worktree /{w = substr($0, 10)} $0 == want {print w; exit}')
made=
if [ -z "$on" ]; then
  if ! why=$(git worktree add -q --no-checkout "$path" "bolt/$bolt" 2>&1); then
    printf 'PLACE=-\nWHY=%s\n' "$(printf '%s' "$why" | tr '\n' ' ')"; exit 0
  fi
  on=$path made=yes
elif [ -d "$path" ] && [ "$(cd "$on" && pwd -P)" = "$(cd "$path" && pwd -P)" ]; then made=yes; fi
said=$(sluice submit main --check --worktree "$on" --json); rc=$?
echo "PLACE=$on"; echo "RC=$rc"; echo "SAID=$(printf '%s' "$said" | base64 | tr -d '\n')"
if [ -n "$made" ] && ! why=$(git worktree remove --force "$path" 2>&1); then
  printf 'KEPT=%s\nWHY=%s\n' "$path" "$(printf '%s' "$why" | tr '\n' ' ')"
fi
"""


def script_here(script, *args):
    """A bash script run on this host with its arguments: (its exit, its output, its standard error), the exit None when
    it could not be run or did not answer within POLL seconds, the error then its why."""
    try:
        r = subprocess.run(["bash", "-c", script, "crew", *args], capture_output=True, text=True, timeout=POLL, env=gitenv())
    except subprocess.TimeoutExpired:
        return None, "", f"it did not answer within {POLL} seconds"
    except OSError as e:
        return None, "", str(e)
    return r.returncode, r.stdout, r.stderr


def forecast_way(bolt, said):
    """How sluice forecasts a bolt against its kit's main on a conductor's wait (plan.19, teams.21), from what BOLT_TIP
    printed: ("place", None) for a legacy bolt, kept in the host's own refs (TIP), whose tip's policy (AT_TIP) names a
    remote for its branch (kit.bolt_remote) that this host holds no tracking ref of it from (TRACKED), since sluice
    reads a branch by its name where that policy routes it and finds such a bolt absent there until its landing pushes
    it; ("branch", None) for any other, read by its branch name; (None, why) when what was printed can't be read, or
    the policy at the tip is not TOML (read.1, read.2)."""
    f = kit.said_of(said)
    if not {"TIP", "AT_TIP", "TRACKED"} <= set(f):
        return None, f"crew can't read where bolt/{bolt}'s tip routes it from: {(said or '').strip()[:200] or 'nothing'}"
    if f["TIP"] == "-":
        return "branch", None
    try:
        text = None if f["AT_TIP"] == "-" else base64.b64decode(f["AT_TIP"], validate=True).decode()
        remote = kit.bolt_remote(text, f"bolt/{bolt}", f"{kit.DECLARATION} at bolt/{bolt}")
    except ValueError as e:  # binascii.Error and UnicodeDecodeError are both
        return None, f"crew can't read bolt/{bolt}'s {kit.DECLARATION} as it was sent: {e}"
    except Refusal as e:
        return None, str(e)
    return ("place" if remote and remote not in f["TRACKED"].split() else "branch"), None


def place_checked(bolt, said, err):
    """What FORECAST_PLACE came to, as sluice_check gives a forecast by name: ((sluice's exit, its answer, the standard
    error), the line naming crew's own place when git could not remove it, or None), the exit None with its why when the
    host has no sluice, no place on the bolt could be made, or what was printed is not FORECAST_PLACE's (read.1,
    read.2). A place left on the bolt's branch would refuse its landing's worktree, so it is named every wait until the
    next forecast removes it."""
    f = kit.said_of(said)
    if "NOSLUICE" in f:
        return (None, "", "this host has no sluice on its path"), None
    if f.get("PLACE") == "-":
        return (None, "", f"no place on bolt/{bolt} could be made to forecast it from: "
                          f"{' '.join(f.get('WHY', '').split()) or 'git said nothing'}"), None
    try:
        code, out = int(f["RC"]), base64.b64decode(f["SAID"], validate=True).decode()
    except (KeyError, ValueError):
        return (None, "", f"crew can't read what the forecast from a place on bolt/{bolt} came to: "
                          f"{(said or '').strip()[-200:] or 'nothing'}"), None
    kept = (f"{f['KEPT']} is kept on bolt/{bolt}, git refusing to remove it: {' '.join(f.get('WHY', '').split()) or 'git said nothing'}. "
            "crew removes it at the next forecast; while it stands, the bolt's landing cannot make its worktree"
            if f.get("KEPT") else None)
    return (code, out, err), kept


def bolt_check(team_kit, bolt):
    """sluice's forecast of a bolt against its kit's main, on this host, the team's (teams.21): read by its branch name
    (sluice_check), or from a place on it (FORECAST_PLACE, <kit>/places/forecast-<bolt>) for a legacy bolt whose tip
    names a remote that holds no branch of it (forecast_way, plan.19). (sluice's exit, its answer, its standard error),
    as sluice_check gives them, and the line naming crew's own place when git could not remove it, or None."""
    main = team_kit["main"]
    code, out, err = script_here(BOLT_TIP, main, bolt, kit.DECLARATION)
    if code is None:
        return (None, "", err), None
    way, why = forecast_way(bolt, out) if code == 0 else (None, f"crew can't read where bolt/{bolt}'s tip routes it: "
                                                               f"{(err or out).strip()[-200:] or f'exit {code}'}")
    if why:
        return (None, "", why), None
    if way == "branch":
        return sluice_check(main, bolt), None
    code, out, err = script_here(FORECAST_PLACE, main, f"{team_kit['dir']}/places/forecast-{bolt}", bolt)
    if code is None:
        return (None, "", err), None
    if code:
        return (None, "", f"crew could not read {main} to forecast bolt/{bolt} from a place on it: "
                          f"{(err or out).strip()[-200:] or f'exit {code}'}"), None
    return place_checked(bolt, out, err)


def bolt_forecast_read(code, out, err):
    """sluice's forecast of a bolt against main, as sluice_check gives it: (the document, None), or (None, why it can't
    be read). sluice exits 0 when the bolt merges with no conflict and 2 when it would conflict, printing
    {"conflict": null or {"paths", "with"}, "head", "onto", "ahead"}; a refusal is an error document; a sluice older
    than the forecast of a branch refuses `--head` on standard error. Every field read is checked (read.2)."""
    if code is None:
        return None, err
    try:
        doc = json.loads(out)
    except ValueError:
        doc = None
    if isinstance(doc, dict) and "conflict" in doc and code in (0, 2):
        c = doc["conflict"]
        if not isinstance(doc.get("head"), str) or not isinstance(doc.get("onto"), str):
            return None, "its answer names no head or no revision of main"
        if c is not None and not (isinstance(c, dict) and isinstance(c.get("paths"), list) and c["paths"]
                                  and all(isinstance(x, str) for x in c["paths"]) and isinstance(c.get("with", []), list)):
            return None, "its conflict names no paths"
        return doc, None
    if isinstance(doc, dict) and isinstance(doc.get("error"), dict) and isinstance(doc["error"].get("message"), str):
        return None, f"it exited {code}: {doc['error']['message']}"
    if "--head" in err:
        return None, "this host's sluice can't forecast a branch no worktree holds (sluice submit --check --head), which a newer sluice can"
    line = next((l.strip() for l in err.splitlines() if l.strip()), "")
    return None, f"it exited {code}" + (f": {line}" if line else "")


def bolt_forecast(team, label, bolt, doc, done, two=False):
    """What the forecast of a bolt against its kit's main tells the conductor, once (teams.21): doc as
    bolt_forecast_read gives it, done the Heads already recorded. None when the bolt merges with no conflict onto main
    and everything queued there, or when the same forecast, for the same bolt head, revision of main and submissions
    queued on main it meets, was said; else (heads, paths, words). A conflict with what main has landed is taken into
    the bolt now, by the fix the conductor starts when main-ops says a landing conflicts (plan.8); one with a
    submission queued on main is waited out, since that submission may yet fail and leave the queue. While the team
    holds two bolts (two), the fix's command names its bolt (teams.16)."""
    c = doc.get("conflict")
    if not c:
        return None
    paths = c["paths"]
    met = [w for w in c.get("with") or [] if isinstance(w, dict) and isinstance(w.get("id"), int)]
    heads = f"bolt/{bolt}@{doc['head'][:7]} main@{doc['onto'][:7]}" + "".join(f" #{w['id']}" for w in met)
    if heads in done:
        return None
    on = ", ".join(paths)
    if not met:
        return heads, paths, (
            f"bolt/{bolt} is forecast to conflict with main on {on}: main has landed work on them since the bolt took it. "
            f"Take main into the bolt now, while the conflict is small, by a fix as when {label}-ops says a landing "
            f'conflicts: crew fix {team} take-main-{doc["onto"][:7]} "Take main into the bolt: it is forecast to conflict '
            f'on {on}"' + (f" --bolt {bolt}" if two else ""))
    who = ", ".join(f"#{w['id']}" + (f" ({w['from']['worktree']})" if isinstance(w.get("from"), dict)
                                     and isinstance(w["from"].get("worktree"), str) else "") for w in met)
    return heads, paths, (
        f"bolt/{bolt} is forecast to conflict on {on} with {who}, queued on main ahead of it. Take nothing in for it: "
        "it may yet fail and leave the queue, and crew forecasts the bolt again when main or its queue moves.")


def unread_said(bolt, bolt_head, why, done):
    """What a wait says when sluice could not forecast the bolt against main: once for the bolt's head (heads, the
    words), or every wait when the head is not known (None, the words); None once said (read.1)."""
    heads = f"bolt/{bolt}@{bolt_head[:7]}" if bolt_head else None
    if heads and heads in done:
        return None
    return heads, f"no forecast of bolt/{bolt} against main: {why}"


def main_conflict(entries, bolt, head):
    """The conflict with what main has landed the run record holds for a bolt at its present head (rail-cards "A row
    forecast to conflict with main takes main first", teams.21), from the entries, oldest first: the latest forecast,
    not refused, on bolt/<bolt> alone, at the head (its Heads beginning bolt/<bolt>@<head7> main@), meeting no submission
    queued on main (no #<n> in its Heads) and naming its Paths, a conductor's wait's or a landings card's raise's: (main's
    short sha, [paths]); None for none, one at a head the bolt has moved from, one met only queued, and the form a wait
    records when sluice could not forecast (unread_said), which names no paths."""
    if not head:
        return None
    at = f"bolt/{bolt}@{head[:7]} main@"
    for e in reversed(entries):
        words = (e.get("Heads") or "").split()
        if (e.get("Act") == "forecast" and not e.get("Refused") and e.get("On") == [f"bolt/{bolt}"] and len(words) == 2
                and (e.get("Heads") or "").startswith(at) and (e.get("Paths") or "").split()):
            return words[1][len("main@"):], e["Paths"].split()
    return None


def forecasts_due(live, bolt, bolt_head, conflicts, done, took, after_of=None):
    """The forecasts a conductor's wait makes for a bolt (teams.12): live is each unmerged unit with a place, in the
    plan's order, as (name, head, its After units); conflicts(theirs, ours, base) the paths git merge-tree forecasts in
    conflict when theirs is merged into ours, from base or, when it is None, their merge base, [] for none, None when
    git can't tell. Each unit is forecast against the bolt, then against each unit ahead of it in the bolt's merge order
    (ahead, through after_of, the bolt's work's After names, the live units' own when none is given) once it is clean
    with the bolt, the later unit taking the forecast, so a unit is never forecast against one that comes after it; one
    already made for the same heads (done) is not made again. A unit is forecast against one it comes after only on
    what it adds beyond that unit's head its place took (took, {unit: {after unit: head}}), so the other's own work it
    carries, rewritten since by a rebase or a settle, is no conflict of its; with no head taken, from their merge base
    (plan.13). Returns the forecasts as (unit, other, paths, heads), none of which orders the two (plan.13, teams.12),
    and the pairs git could not read."""
    due, unread = [], []
    order = [name for name, _, _ in live]
    after_of = after_of if after_of is not None else {name: after for name, _, after in live}
    for name, head, after in live:
        others = ([(f"bolt/{bolt}", bolt_head)] if bolt_head else []) + [
            (o, h) for o, h, _ in live if o != name and ahead(order, after_of, o, name)]
        for other, ohead in others:
            paths = conflicts(ohead, head, took.get(name, {}).get(other) if other in after else None)
            if paths is None:
                unread.append((name, other))
                continue
            if not paths:
                continue
            heads = f"{name}@{head[:7]} {other}@{ohead[:7]}"
            if heads not in done:
                due.append((name, other, paths, heads))
            if other.startswith("bolt/"):
                break  # it meets the bolt first: the units ahead are forecast once it is clean with the bolt
    return due, unread


# The subject crew wrote an After with at a forecast, before a forecast stopped ordering two units (plan.13): crew's
# own words, matched whole, so an order a wait wrote then is read as crew's.
FORECAST_ORDER = re.compile(r"^plan\([a-z0-9][a-z0-9-]*\): ([a-z0-9][a-z0-9-]*) after ([a-z0-9][a-z0-9-]*), forecast to conflict$")


def forecast_ordered(e):
    """The pair a unit.after entry's subject says a forecast ordered before this was a settle's (FORECAST_ORDER), as
    (unit, other), or None."""
    m = FORECAST_ORDER.match(e.get("Why") or "")
    return m.groups() if m else None


def forecast_orders(after_of, unmerged, entries, holds):
    """Which pairs of a bolt's unmerged units crew puts in order, and which orders of its own it lifts (plan.13,
    teams.12, teams.14), from the run record's entries (oldest first), each unit's After names as the plan holds them
    (after_of) and the bolt's unmerged units. A pair is (unit, other) of a forecast entry on unit/<unit> and
    unit/<other>, both unmerged. crew's writes for a pair are its unit.after entries on unit/<unit> with After: <other>,
    made on a settle, or with the subject a forecast wrote before (FORECAST_ORDER); its lifts, those with Lifted:
    <other>. holds(unit, other, head) says whether the unit's branch holds the other's work, head being the other's as
    the pair's latest forecast recorded it, or None, and answers None when git can't tell, which orders and lifts
    nothing for the pair (read.1); it is asked only of a pair a settle's end may decide.

    A pair is ordered when the plan does not put the unit after the other, a settle of the unit delivered after a
    forecast for the pair and after crew's latest record for it, the branch holds the other's work, crew has never
    written the pair's order on a settle, and crew's latest record for the pair is not a write: a write the plan no
    longer holds was lifted by someone else, and stays lifted. A pair is lifted when the plan puts the unit after the
    other, crew's latest record for it is a write, the unit's latest settle end since that write stopped short with no
    settle of it delivered since, and the branch does not hold the other's work. An order set by hand or by a proposal
    is no write of crew's, and is never lifted. Returns (to order, to lift), each [(unit, other, the id of the settle
    end that decided it)], in the order of the pairs' first forecasts."""
    key = lambda e: (e["At"], e["Id"])
    pairs = []
    for e in entries:
        on = e.get("On") or []
        if e.get("Act") == "forecast" and not e.get("Refused") and len(on) > 1 and on[0].startswith("unit/") and on[1].startswith("unit/"):
            pair = (on[0][5:], on[1][5:])
            if pair not in pairs and pair[0] in unmerged and pair[1] in unmerged:
                pairs.append(pair)
    order, lift = [], []
    for unit, other in pairs:
        forecasts = [e for e in entries if e.get("Act") == "forecast" and not e.get("Refused")
                     and (e.get("On") or [])[:2] == [f"unit/{unit}", f"unit/{other}"]]
        records = [e for e in entries if e.get("Act") == "unit.after" and not e.get("Refused") and f"unit/{unit}" in (e.get("On") or [])
                   and (e.get("After") == other or e.get("Lifted") == other or forecast_ordered(e) == (unit, other))]
        ends = [e for e in entries if e.get("Act") == "stage.end" and not e.get("Refused") and f"stage/{unit}/settle" in (e.get("On") or [])]
        latest = records[-1] if records else None
        written = latest is not None and latest.get("Lifted") != other
        since = key(latest) if latest else None
        head = next((w.split("@", 1)[1] for w in reversed((forecasts[-1].get("Heads") or "").split()) if w.startswith(f"{other}@")), None)
        if comes_after(after_of, unit, other):
            later = [e for e in ends if since is None or key(e) > since]
            if written and other in after_of.get(unit, ()) and later and later[-1].get("Ended") == "short" \
                    and not any(e.get("Ended") == "delivered" for e in later) and holds(unit, other, head) is False:
                lift.append((unit, other, later[-1]["Id"]))
            continue
        if written or any(e.get("After") == other for e in records):
            continue
        settled = [e for e in ends if e.get("Ended") == "delivered" and key(e) > key(forecasts[0]) and (since is None or key(e) > since)]
        if settled and holds(unit, other, head) is True:
            order.append((unit, other, settled[-1]["Id"]))
    return order, lift


def settle_orders(fleet, t, plan, st, unit=None):
    """What forecast_orders says for the unmerged units of the team's bolts, or for one unit, written: each pair put in
    order or lifted in a write of its own in the waiting conductor's name (roles.1, state.1), the conductor told
    nothing by it, since its wait says it. Whether the unit's branch holds the other's work is read with git on the
    team's host (branch_holds). A write refused, or a pair git can't read, is said on standard error, and the next wait
    decides again. Returns what the writes did, a sentence each."""
    main, label, said, entries = t["kit"]["main"], t["label"], [], None
    for b in held_by(plan, t["name"]):
        order_of, after_of = bolt_order(plan, b.name())
        if unit is not None and unit not in order_of:
            continue
        unmerged = {n for n in order_of if st.of(n)["stage"] not in ("merged", "landed", "unknown")}
        entries = local_entries(label) if entries is None else entries
        order, lift = forecast_orders(after_of, unmerged, entries, lambda u, o, head: branch_holds(main, u, o, head))
        for u, o, settle in order + lift:
            if unit is not None and u != unit:
                continue
            lifted = (u, o, settle) in lift
            try:
                with contextlib.redirect_stdout(sys.stderr):
                    order_write(fleet, t, b.name(), u, o, settle, lifted)
            except Refusal as e:
                print(f"{u} is not {'lifted from after' if lifted else 'put after'} {o}: {e}", file=sys.stderr)
                continue
            said.append(f"{u} no longer comes after {o}: its settle found nothing to change" if lifted else
                        f"{u} now comes after {o}, whose work its settle took: it merges after {o}")
    return said


def branch_holds(main, unit, other, head):
    """Whether unit/<unit> holds the other's work (plan.13): its head as a forecast recorded it (head), or unit/<other>'s
    head now, read with git in the kit's main checkout. None, said on standard error, when git can't tell."""
    branch, why = f"refs/heads/unit/{unit}", None
    for h in (head, f"refs/heads/unit/{other}"):
        if not h:
            continue
        r = subprocess.run(["git", "-C", main, "merge-base", "--is-ancestor", h, branch], capture_output=True, text=True, env=gitenv())
        if r.returncode == 0:
            return True
        if r.returncode != 1:
            why = why or (r.stderr.strip() or f"git exited {r.returncode}")
    if why:
        print(f"crew can't tell whether unit/{unit} holds {other}'s work, so it neither orders nor lifts them: {why}", file=sys.stderr)
        return None
    return False


def order_write(fleet, t, bolt, unit, other, settle, lift):
    """crew's own order of a unit after another a forecast found it in conflict with, or its lift (plan.13): one write in
    the waiting conductor's name, the unit.after entry naming the other as After or Lifted and the settle end that
    decided it. The change removes or adds only that one After name."""
    def change(w):
        v = w.unit(unit)
        w.unit(other)
        v.get("Bolt") == bolt or fail(f"unit {unit} moved to {v.get('Bolt') or 'the queue'} meanwhile")
        if lift:
            other in v.all("After") or fail(f"unit {unit} no longer comes after {other}")
            v.fields = [(n, x) for n, x in v.fields if not (n == "After" and x == other)]
        else:
            other not in v.all("After") or fail(f"unit {unit} already comes after {other}")
            v.add("After", other, after="Intent")
        w.quiet.add(t["name"])  # its conductor learns it from its wait, not from this write
        return [bolt]
    subject = (f"plan({bolt}): {unit} no longer after {other}, its settle found nothing to change" if lift else
               f"plan({bolt}): {unit} after {other}, its settle took {other}'s work")
    return write(fleet, t["label"], change, subject, act="unit.after", on=[f"unit/{unit}", f"bolt/{bolt}"],
                 fields={"Lifted" if lift else "After": other, "Settle": settle})


def carried_forecasts(fleet, t, plan, st_all, bolt, unit):
    """The forecasts and amendments waiting to reach a unit in its next stage's prompt: this host's entries for it that
    reached it by prompt and that no stage start of it has carried since. Returns their ids and their words."""
    waiting = waiting_for(unit, local_entries(t["label"]))
    if not waiting:
        return [], []
    k, _ = st_all.kit(plan.bolt(bolt))
    other = lambda e: e["On"][1][5:] if e["On"][1].startswith("unit/") else e["On"][1]
    return [e["Id"] for e in waiting], [amendment_words(t, k, bolt, other(e)) if e["Act"] == "amendment" else
                                        forecast_words(t, k, bolt, unit, other(e), (e.get("Paths") or "").split(),
                                                       (e.get("Took") or "").split()) for e in waiting]


def waiting_for(unit, entries):
    """The forecasts and amendments that reached a unit by its next prompt and that no stage start of it has carried
    yet (its Forecast field naming their ids), from the run record's entries, oldest first. A forecast against the bolt
    is dropped once a newer one against the bolt was made for the unit, however that one reached it: the bolt it was
    read against has moved, and the newer one says how the unit meets the bolt now (teams.12)."""
    taken = {i for e in entries if e.get("Act") == "stage.start" and f"unit/{unit}" in e["On"] for i in (e.get("Forecast") or "").split()}
    mine = [e for e in entries if e.get("Act") in ("forecast", "amendment") and e["On"][:1] == [f"unit/{unit}"]]
    newest = {e["On"][1]: e["Id"] for e in mine if e["Act"] == "forecast" and e["On"][1].startswith("bolt/")}
    return [e for e in mine if e.get("Reached") == "prompt" and e["Id"] not in taken
            and newest.get(e["On"][1], e["Id"]) == e["Id"]]


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


def turn_of(info):
    """When the agent's own session says its turn ended, with nothing sent to it since (transcript.turn_over), or None
    while a turn goes on or crew can't read it."""
    sess = info.get("agent_session")
    sid = sess.get("value") if isinstance(sess, dict) else None
    path = transcript.find(sid) if isinstance(sid, str) and sid else None
    return transcript.turn_over(path) if path else None


def ended_turn(o, status, pending, over):
    """Whether a verify's agent has ended its turn since the stage began with nothing of its own still running (record
    0007, teams.4): herdr reads it idle or done, it waits on no background task of its own (pending, read and empty),
    and its session's turn ended since the stage began (over, turn_of). A verify ends only at its report, so one whose
    agent has ended so with none saved has not ended, and its wait says so then, never stuck by its clock."""
    return o.stage == "verify" and status in ("idle", "done") and pending == [] and over is not None \
        and o.start is not None and over >= o.start


def quiet_verdict(now, stuck, pending, last, unread, seen_quiet, seen_working):
    """Whether a quiet agent is stuck (teams.4), and what it is doing as the wait says it: (True, "quiet for <n>
    minutes") or (False, what it does). One waiting on background tasks of its own is never stuck. Else its clock
    starts at its transcript's last record, or when the wait first saw it quiet when that can't be read (unread), and
    never before the wait last saw it working; it is stuck once that clock reaches the limit."""
    if pending:
        return False, f"is waiting on {len(pending)} background task{'' if len(pending) == 1 else 's'} of its own"
    quiet = now - max(x for x in ((seen_quiet if unread or not last else last), seen_working) if x)
    if quiet >= stuck:
        return True, f"quiet for {minutes(quiet)}"
    return False, f"has been quiet for {minutes(quiet)}, under the limit of {minutes(stuck)}"


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
    return ended_words(t["name"], agent, last_end(t, agent))


def ended_words(team, agent, e):
    """What a wait says of a stage that has ended, from the newest stage.end recorded for its agent (e), or None when
    there is none: which stage, and how it ended."""
    if not e:
        return f"{agent} owes no stage's end, and none is recorded for it on this host"
    stage = next((o.split("/") for o in e["On"] if o.startswith("stage/")), None)
    fix = next((o for o in e["On"] if o.startswith("fix/")), None)
    m = re.match(r"^[a-z]+\([^)]*\): (\S+) ", e.get("Why") or "")
    what = (f"{stage[2]} on {stage[1]}" if stage and len(stage) > 2 else
            (f"fix {fix}" if not m or m.group(1) == "fix" else f"{m.group(1)} of {fix}") if fix else "its stage")
    how = {"delivered": f"{agent} delivered {e.get('Delivered')}" + (" (observed late)" if e.get("Observed") == "late" else ""),
           "short": f"{agent} stopped short, and {team}-conductor was told what it needs",
           "stopped": f"crew ended {agent} before it delivered"}.get(e.get("Ended"), f"{agent} reached {e.get('Result', 'unknown')}")
    return f"{what} has ended: {how}"


# What a wait reads of sluice beyond the refs (record 0032, point 4): `sluice overview --json`, and `sluice status
# <id> --json` for a submission it names, each read by facts checked against sluice 0.18.0 (read.2). A conflict or a
# blamed line of the overview's recent[] names its submission's id and not where it came from; the path is on the
# submission, which the overview lists only while it is in a chain, and a conflict is recorded 0 to 3 seconds after
# its submission (5 of 6 on mac-studio's crew, swancloud and sluice logs, 2026-10-17), inside a wait's look.
OVERVIEW, SUBMISSION = "sluice/overview@1", "sluice/submission@1"
OUTCOMES = ("conflict", "blamed")


def overview_facts(doc):
    """The facts a wait reads of `sluice overview --json`, as sluice 0.18.0 prints it: the document's schema is
    sluice/overview@1, and each of its branches[] names its branch and its records' version, an integer that moves
    on every write to them; its submissions[] are those still in a chain, each with its id and from.path, the absolute
    path of the worktree it came from, absent where sluice's driver had none; its recent[] holds its last landed,
    blamed and conflict log lines as written, a conflict naming its id and paths, a blame its id and combination, each
    its at. Returns (each branch's version, each listed submission's path or None, each conflict and blamed line as
    (branch, line, its at)), or None when the document is not one sluice 0.18.0 prints."""
    if not isinstance(doc, dict) or doc.get("schema") != OVERVIEW or not isinstance(doc.get("branches"), list):
        return None
    versions, paths, outcomes = {}, {}, []
    for b in doc["branches"]:
        if not isinstance(b, dict) or not isinstance(b.get("branch"), str) or type(b.get("version")) is not int \
                or not isinstance(b.get("submissions"), list) or not isinstance(b.get("recent"), list):
            return None
        versions[b["branch"]] = b["version"]
        for s in b["submissions"]:
            came = s.get("from") if isinstance(s, dict) else None
            if type(s.get("id") if isinstance(s, dict) else None) is int and isinstance(came, dict):
                paths[s["id"]] = came.get("path") if isinstance(came.get("path"), str) else None
        for r in b["recent"]:
            at = sluice_at(r.get("at")) if isinstance(r, dict) else None
            if at and r.get("event") in OUTCOMES and type(r.get("id")) is int:
                outcomes.append((b["branch"], r, at))
    return versions, paths, outcomes


def sluice_at(at):
    """A time sluice writes (2026-10-17T16:04:11Z), in UTC, or None when it holds none."""
    try:
        return datetime.datetime.fromisoformat(at).astimezone(datetime.timezone.utc) if isinstance(at, str) else None
    except ValueError:
        return None


def submission_from(doc):
    """Where a submission came from, as `sluice status <id> --json` prints it in sluice 0.18.0 (sluice/submission@1):
    its from.path, or None when its record names none, a pull request's or one written before sluice 0.12.0. Raises
    ValueError, naming what it read, when the document is no submission."""
    came = doc.get("from") if isinstance(doc, dict) and doc.get("schema") == SUBMISSION else None
    if not isinstance(came, dict):
        raise ValueError(f"it printed no {SUBMISSION}")
    return came.get("path") if isinstance(came.get("path"), str) else None


def overview_due(outcomes, place, since, paths, told):
    """Of an overview's conflict and blamed lines (overview_facts), those that are the stage's: recorded since it began,
    not yet told, and of a submission whose path (paths, by id, as the wait has learned them) is the stage's place.
    Returns them as (key, branch, line), and the ids of lines since it began whose path the wait has not learned."""
    due, ask = [], []
    for branch, r, at in outcomes:
        key = f"{branch} {r['event']} #{r['id']} {r['at']}"
        if at < since or key in told:
            continue
        if r["id"] not in paths:
            if r["id"] not in ask:
                ask.append(r["id"])
        elif paths[r["id"]] == place:
            due.append((key, branch, r))
    return due, ask


def overview_look(seen, doc, why, place, since, status):
    """One look of a wait at sluice's overview on the team's host. seen is what the wait keeps between its looks ({}
    at its start); doc the overview as read, or None with why it could not be read; place the stage's place as git
    names it; since when the stage began; status(id) reads `sluice status <id> --json`, (the document, None) or (None,
    why). A look whose branches' versions are all as the last look saw them reads nothing more. Else it learns the path
    of every submission the overview lists, asks status once of each conflict or blamed line since the stage began
    whose path it has not learned, and returns the lines that are the stage's, as (branch, line), each once a wait,
    with what to say on standard error: that the overview can't be read and the wait goes on by refs alone, once a
    wait (read.1), and each submission whose place crew could not read."""
    facts = overview_facts(doc) if doc is not None else None
    if facts is None:
        if seen.get("unread"):
            return [], []
        seen["unread"] = True
        return [], [f"sluice's overview can't be read ({why or f'it is not the {OVERVIEW} sluice 0.18.0 prints'}): "
                    "the wait goes on by refs alone, and says nothing of a conflict or a failed check sluice finds"]
    versions, learned, outcomes = facts
    if versions == seen.get("versions"):
        return [], []
    seen["versions"] = versions
    paths, told, notes = seen.setdefault("paths", {}), seen.setdefault("told", set()), []
    paths.update(learned)
    due, ask = overview_due(outcomes, place, since, paths, told)
    for sid in ask:
        sub, why = status(sid)
        try:
            paths[sid] = None if why else submission_from(sub)
        except ValueError as e:
            why = str(e)
        if why:  # never asked again: a line crew can't place is no line of the stage's
            paths[sid] = None
            notes.append(f"crew can't tell whether sluice's #{sid} came from this stage's place: "
                         f"sluice status {sid} --json: {why}")
    if ask:
        due, _ = overview_due(outcomes, place, since, paths, told)
    told.update(key for key, _, _ in due)
    return [(branch, r) for _, branch, r in due], notes


def sluice_words(r):
    """A conflict or blamed line as sluice's own overview says it: `conflict #2 on shared.txt`, `blamed #3 on
    3d44d6b`."""
    if r["event"] == "conflict":
        paths = [p for p in r.get("paths") or [] if isinstance(p, str)] if isinstance(r.get("paths"), list) else []
        return f"conflict #{r['id']}" + (f" on {', '.join(paths)}" if paths else "")
    combination = r.get("combination")
    return f"blamed #{r['id']}" + (f" on {combination[:7]}" if isinstance(combination, str) and combination else "")


def sluice_said(o, agent, branch, r):
    """What a wait tells the conductor of a conflict or blame sluice recorded for the stage's submission."""
    return f"{o.phrase()}: sluice says of {agent}'s submission to {branch}: {sluice_words(r)}; the wait goes on until the stage ends"


def sluice_read(main, *args, timeout=POLL):
    """`sluice <args> --json` run in a kit on this host: (the document, None), or (None, why it can't be read). It waits
    timeout seconds for sluice's answer, or for as long as sluice takes when None."""
    try:
        r = subprocess.run(["sluice", *args, "--json"], cwd=main, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return None, "this host has no sluice on its path"
    except subprocess.TimeoutExpired:
        return None, f"it did not answer within {timeout} seconds"
    except OSError as e:
        return None, str(e)
    if r.returncode != 0:  # sluice says why as {"error": {"message": ...}} under --json, clap on standard error
        try:
            said = json.loads(r.stdout)["error"]["message"]
        except (ValueError, TypeError, KeyError):
            said = next((l.strip() for l in r.stderr.splitlines() if l.strip()), "")
        return None, f"it exited {r.returncode}" + (f": {said}" if isinstance(said, str) and said else "")
    try:
        return json.loads(r.stdout), None
    except ValueError:
        return None, "it printed no JSON"


def stage_wait(fleet, a):
    """Wait on the stage a slot's agent, or ops, owes, until it ends at its deliverable, stops short, is stuck, its agent
    is gone, a verify's agent has ended its turn with no report (ended_turn), or the timeout passes, and print the one
    line that says which. A delivered end is recorded here; nothing else is. The wait holds waits/<slot>.lock for its
    life, so crew needs knows a wait is there to hand its words to. A unit's settle that ends delivered or short orders
    or lifts its unit's forecast orders, and its line says so (settle_said). Each look also reads sluice's overview,
    and says at once, before that line, each conflict or blame sluice records for a submission from the stage's place
    (overview_look)."""
    t = at_work(fleet, a.team)
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
    place = held.get(a.slot, [None] * 4)[3]
    deadline = time.monotonic() + a.timeout / 1000
    stuck = datetime.timedelta(milliseconds=a.stuck)
    seen_quiet = seen_working = None
    sluice_seen, here, main = {}, os.path.realpath(place) if place else None, t["kit"]["main"]
    with READ.fresh():  # each look reads the plan and the kit afresh
        while True:
            if here:  # what refs can't give: a conflict or a failed check sluice records for the place's submission
                doc, why = sluice_read(main, "overview")
                outcomes, notes = overview_look(sluice_seen, doc, why, here, o.start, lambda sid: sluice_read(main, "status", str(sid)))
                for note in notes:
                    print(note, file=sys.stderr)
                for branch, r in outcomes:
                    print(sluice_said(o, agent, branch, r), flush=True)
            with stages_file(t, shared=True) as lines:
                words = handed(t, a.slot, o.eid)
                owed = any(l[3:4] == [o.eid] for l in lines)
            info = crew.agent_get(fleet, agent) if words is None and owed else None
            status = info.get("agent_status") if info else None
            got, missing = deliverable(fleet, t, o, place) if words is None and owed and status != "working" else (None, None)
            now = datetime.datetime.now(datetime.timezone.utc)
            quiet, over = (False, "is working", None), False
            if status == "working":
                seen_working = now
            elif info is not None and not got:
                seen_quiet = seen_quiet or now
                pending, last, unread = background(info)
                quiet = (*quiet_verdict(now, stuck, pending, last, unread, seen_quiet, seen_working), unread)
                over = ended_turn(o, status, pending, turn_of(info) if o.stage == "verify" and pending == [] else None)
            remaining = deadline - time.monotonic()
            how, said = look(o, agent, a.timeout, words, owed, info is None, got, missing, quiet, remaining <= 0, over)
            if how == "ended":
                print(ended_said(t, agent))
                return
            then = []
            if how == "delivered":
                if not end_owed(fleet, t, o, "delivered", got):
                    continue
                unmark(fleet, t, o)
                then = after_delivery(o.stage, o.fix)
                if "batch" in then and "landing" not in then:  # the change it delivered is due, and may make a batch due now
                    batch_reckoned(fleet, t)
            if how in ("delivered", "short") and o.stage == "settle" and not o.fix and not o.chore:
                said = settle_said(fleet, t, o.name, said)
            if how:
                print(said, flush=True)
                if "landing" in then:  # the head of the bolt it merged into moved: its row on its kit's landings card (land_hand)
                    landing_after_merge(fleet, t, got.split("@")[0][len("bolt/"):])
                if "batch" in then and "landing" in then:  # its last unit merged may make a batch due at once
                    batch_reckoned(fleet, t)
                if "tidy" in then:  # its slot, place and branch go as it lands, not at the next read
                    try:
                        reap(fleet, on_team_host(fleet, t))
                    except Refusal as e:
                        print(f"its place is not removed yet: {e}; the team's next read removes it", file=sys.stderr)
                return
            time.sleep(min(POLL, remaining))


def after_delivery(stage, fix):
    """What crew does once a stage a wait watched has delivered (briefs.12, plan.16): "batch", reckon whether a batch is
    due (batch_check), after a construct's change, not a fix's, which is due itself, and after a merge, whose last unit
    merged makes a batch due at once for the bolt's units in none; "landing", raise or change the bolt's landing card,
    after a merge, which moved the bolt's head; "tidy", the team's read (reap), after a merge, so the slot is freed and
    the place and its branch removed as the merge lands rather than at the conductor's next read (teams.1, plan.9). A
    bolt whose last unit merged left no wait to reckon its batch, since its conductor waits on nothing more
    (every-deploy-has-its-live-card and every-host-reaches-every-other-by-its-tailnet-name on 2026-10-19, every unit
    merged and the planner never told, for two hours), and no read to remove its places."""
    return (["batch"] if stage == "construct" and not fix else []) + (["landing", "batch", "tidy"] if stage == "merge" else [])


def batch_reckoned(fleet, t):
    """batch_check at a wait's end, what crew can't read said on standard error, the wait's answer standing."""
    try:
        batch_check(fleet, t)
    except Refusal as e:
        print(f"no batch reckoned: {e}", file=sys.stderr)


def settle_said(fleet, t, unit, said):
    """A unit's settle ended, delivered or short: crew's own order of it after a unit a forecast found it in conflict
    with, or that order's lift, written now (settle_orders), and the wait's answer with a sentence for each. What crew
    can't read is said on standard error, and the next wait decides again."""
    try:
        plan = plan_of(fleet, t["label"])
        if plan is None:
            print(f"{t['label']}'s plan could not be read, so {unit}'s settle orders nothing yet", file=sys.stderr)
            return said
        more = settle_orders(fleet, t, plan, stages_for(fleet, plan, held_by(plan, t["name"])), unit)
    except Refusal as e:
        print(f"{unit}'s settle orders nothing yet: {e}", file=sys.stderr)
        return said
    if not more:
        return said
    said = said.rstrip()
    return " ".join([said if said.endswith(".") else f"{said}."] + [f"{x}." for x in more])


def look(o, agent, timeout, words, owed, gone, got, missing, quiet, out_of_time, over=False):
    """One look of a wait at the stage o its agent owes, as facts (teams.4): the words a stop-short handed it, whether
    the stage is still owed, whether the agent is gone, what it delivered (got, and missing: what the wait says of the
    deliverable, or of what it lacks), quiet, (stuck, what the agent is doing, what crew could not read of it), and
    over, whether a verify's agent has ended its turn with nothing of its own running (ended_turn): with no report, the
    verify has not ended, and the wait says so then, never calling it stuck (record 0007). Returns how the wait ends
    and the line it prints, "ended" when something else recorded the end, or (None, what the agent is doing) to look
    again."""
    if words is not None:
        return "short", f"{agent} stopped short in {o.phrase()}. It needs: {words}"
    if not owed:
        return "ended", None
    if got:
        return "delivered", f"{agent} delivered {o.phrase()}: {missing}"
    if gone:
        return "gone", f"{agent} is no longer running: {o.phrase()} delivered nothing and said nothing it needs"
    if over:
        return "unended", (f"{agent} ended its turn in {o.phrase()} with {missing}: the verify has not ended, since a "
                           "verify ends only at its report; nothing is recorded")
    stuck, doing, unread = quiet
    if stuck:
        return "stuck", (f"{agent} is stuck in {o.phrase()}: {doing}, with {missing} and nothing it needs said"
                         + (f"; crew could not read whether it waits on work of its own ({unread})" if unread else ""))
    if out_of_time:
        return "running", f"{o.phrase()} is still running after the wait's {timeout} ms: {agent} {doing}; nothing is recorded yet"
    return None, doing


def owed_of(t, slot, lines, held):
    """The stage a slot's agent owes an end, from the stages file's lines and the slots file's (held, by slot), as crew
    needs reads it: refused when it owes none, or the slot now holds other work than the stage's."""
    owed = [Owed(t, l) for l in lines if l[0] == slot and held.get(slot, [None] * 3)[2] == l[1]]
    return owed or fail(f"{t['name']}-{slot} runs no stage crew is waiting on")


def stage_needs(fleet, a):
    """crew needs: the caller's stage ends short, recorded with Ended short and never the words (record.3), and the
    words go to the conductor: to the wait running on the stage when there is one, through needs/<slot>, else in a
    tell marked as from the agent (roles.4); then its agent's end is handed on (short_hand), so the stage is ended in
    fact. Only the agent of a stage crew owes an end may say it. A unit's merge that stops short while its branch holds
    archives it can make itself (merge_owes) is refused once in the stage, naming them, so no stopped merge reaches the
    conductor for work its own stage does (teams.17, roles.3); told, it says so again only when openspec refuses one
    of them, and that stop-short is passed on, its agent's end handed on with it."""
    t = at_work(fleet, a.team)
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
        owed += owed_of(t, a.slot, lines, held)
    o = owed[0]
    told = needs.with_name(f".{a.slot}.archives")
    if o.stage == "merge" and o.kind == "unit" and not o.fix and not (told.exists() and told.read_text().strip() == o.eid):
        archives = merge_owes(fleet, t, o.name)
        if archives:
            told.parent.mkdir(parents=True, exist_ok=True)
            told.write_text(f"{o.eid}\n")
            fail(archives_refusal(o.name, archives))
    end_owed(fleet, t, o, "short", then=hand) or fail(f"{agent} runs no stage crew is waiting on")
    # The words are the wait's once it takes the file; when no wait holds its lock, or the one there ends without
    # taking them, they are told. A wait takes the file only while it holds the lock, so a free lock with the file
    # still there means nobody will.
    told = f"{agent} stopped short in {o.phrase()}. It needs: {a.words}"
    give_up, waits = time.monotonic() + 6 * POLL, team_state(t) / "waits" / f"{a.slot}.lock"
    said, to = f"{o.phrase()} is ended, stopped short: {conductor}'s wait has what you need", sys.stdout
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
                    said = f"{o.phrase()} is ended, stopped short: {conductor} is told what you need"
                else:
                    said, to = (f"{o.phrase()} is ended, stopped short, and {conductor} could not be told what you need: "
                                "say it in your last message"), sys.stderr
                break
        time.sleep(1)
    print(f"{said}. {short_hand(fleet, t, a.slot, o)}", file=to)


SHORT_GRACE = 30  # looks, a second apart, the agent of a stage that stopped short has to end its turn before crew ends it


def short_path(t, slot):
    """The mark of a slot whose stage stopped short (crew needs), there until its agent is ended or found gone: the
    stage's start entry id, then the Claude session that said it."""
    return team_state(t) / "short" / slot


@contextlib.contextmanager
def short_lock(t, slot):
    """The slot's lock while the agent of its stage that stopped short is looked at and ended, held by crew _end-short
    and by the slot's next start (short_taken), so neither ends an agent the other started."""
    f = short_path(t, slot).with_name(f"{slot}.lock")
    f.parent.mkdir(parents=True, exist_ok=True)
    with open(f, "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def short_marked(t, slot):
    """The Claude session a slot's mark names as the one whose stage stopped short, or None with no mark."""
    try:
        lines = short_path(t, slot).read_text().split("\n")
    except OSError:
        return None
    return lines[1].strip() if len(lines) > 1 else ""


def agent_facts(info):
    """Whether an agent is up, herdr's status of it and the Claude session it runs, from its item (crew.agent_get),
    the status and the session None when herdr gives none (read.2)."""
    if not isinstance(info, dict):
        return False, None, None
    status, sid = info.get("agent_status"), info.get("agent_session")
    sid = sid.get("value") if isinstance(sid, dict) else None
    return True, status if isinstance(status, str) else None, sid if isinstance(sid, str) and sid else None


def short_end(marked, up, status, session, looked, grace=SHORT_GRACE):
    """What crew does with the agent of a slot whose stage stopped short (record 0007), from the Claude session that
    said it (marked), whether an agent is up in the slot, herdr's status of it and the session it runs, and how many
    looks crew has given it: "gone" with none up; "other" when it runs another session than the one that stopped
    short, which is left be; "unread" when, past the grace, crew still can't read its status or which session it runs,
    so it ends none (read.1); "end" once it has stopped working, or still works past the grace, since its stage is over
    and nothing it does now is the stage's; else "wait", for its turn to end."""
    if not up:
        return "gone"
    if status is None or session is None:
        return "wait" if looked < grace else "unread"
    if session != marked:
        return "other"
    return "end" if status != "working" or looked >= grace else "wait"


def short_said(agent, how):
    """What crew says of the agent of a stage that stopped short once short_end has decided."""
    return {"end": f"{agent} is ended: its stage stopped short", "gone": f"{agent} is no longer up",
            "other": f"{agent} runs another session than the one that stopped short: crew leaves it be",
            "unread": f"crew could not read which session {agent} runs, so it ends none"}[how]


def short_over(team, slot, how):
    """short_end's decision acted on, under the slot's lock: the agent ended when "end", its exit's question answered
    and what it still runs stopped, since that was its stage's (Agents.stop's over); the mark then gone, as it goes for
    an agent gone, running another session or unread. None, or what crew says of an agent it could not end, whose mark
    stays for the slot's next start."""
    if how == "end":
        why = team.stop(slot, over=True)
        if why:
            return why
    short_path(team.t, slot).unlink(missing_ok=True)
    return None


def short_hand(fleet, t, slot, o):
    """crew needs' last act on a slot's stage (record 0007): the slot marked with the asker's Claude session
    (short_path), and the end of its agent handed to crew _end-short, a process of its own on this host that outlives
    this command (code.9); what crew needs then says of the session. A stage of ops's ends no session, and an asker
    whose session crew can't read is marked by none and ended by none (read.1)."""
    if not slot.startswith("unit-"):
        return "End your turn."
    host, _, sid = (record.session() or "").partition(":")
    if host != crew.this_host() or not sid:
        return "crew could not read which Claude session this is, so it ends none: end your turn."
    mark = short_path(t, slot)
    with short_lock(t, slot):
        tmp = mark.with_name(f".{slot}.new")
        tmp.write_text(f"{o.eid}\n{sid}\n")
        tmp.replace(mark)
    argv = ["bash", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bin", "crew"), "_end-short", t["name"], slot]
    try:
        with open(mark.with_name(f"{slot}.log"), "a") as out:
            subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
    except OSError as e:
        return f"crew could not hand this session's end on ({e}): end your turn, and the slot's next start ends it."
    return "crew ends this session once your turn ends: end it now."


def short_taken(fleet, team, slot):
    """Before a stage starts in a slot (run_stage): the agent of the slot's stage that stopped short, still up in its
    session, ended at once, working or not, its grace the start's to cut short (short_end), under the slot's lock, so
    the conductor's next start neither waits on it nor needs --force. None, or what crew says of an agent it could not
    end."""
    with short_lock(team.t, slot):
        marked = short_marked(team.t, slot)
        if marked is None:
            return None
        return short_over(team, slot, short_end(marked, *agent_facts(crew.agent_get(fleet, team.agent_of(slot))), SHORT_GRACE))


def end_short(fleet, a):
    """crew _end-short <team> <slot>, handed by crew needs to a process of its own on the team's host (short_hand): the
    agent of the slot's stage that stopped short ended as a stage's agent is ended for the next (teams.2), once it has
    ended its turn or SHORT_GRACE looks have passed (short_end), so no agent goes on after its needs as if its stage
    stood and the conductor's next start finds the slot free. Each look is under the slot's lock, as the next start's
    is (short_taken); a mark that start took first leaves nothing to end."""
    t = at_work(fleet, a.team)
    team = on_team_host(fleet, t)
    agent = team.agent_of(a.slot)
    for looked in range(SHORT_GRACE + 1):
        with short_lock(t, a.slot):
            marked = short_marked(t, a.slot)
            if marked is None:
                print(f"{agent}'s mark is gone: the slot's next start took it")
                return
            how = short_end(marked, *agent_facts(crew.agent_get(fleet, agent)), looked)
            if how != "wait":
                print(short_over(team, a.slot, how) or short_said(agent, how))
                return
        crew.nap(1)


# ------------------------------------------------------------------------------ a team's commands, one process each

def forwarded(fleet, machine):
    """A team's or a main level's command runs on the host its agents run on (code.3). On another host this process says
    on descriptor 3 where that is and how crew is run there, as shell assignments (teams.9), for bash crew to run the same
    command there as the one asking, and stops, having touched nothing."""
    if machine == crew.this_host():
        return
    said = sh(MACHINE=machine, SSH_TARGET=fleet["hosts"][machine]["ssh"], **crew.reach(fleet, machine))
    try:
        os.write(3, (said + "\n").encode())
    except OSError:
        fail(f"this runs on {machine}: run it there with crew")
    raise Stopped(0)


def arrived(fleet, machine):
    """A command where it runs: forwarded there when this is not that host (forwarded); what killed commands left of
    their readings swept; and the asker's Claude session read while herdr's listing is the one the command starts with
    (record.session)."""
    forwarded(fleet, machine)
    READ.sweep()
    record.session()


def on_team_host(fleet, t, force=False):
    """A team's command where it runs (arrived), with the team's state folder there."""
    arrived(fleet, t["machine"])
    team = crew.Team(fleet, t, force)
    team.ensure()
    return team


def not_held(label=None, act=None, on=()):
    """A command that would start an agent refused while this host is held (teams.19): said, and for an act that moves
    work recorded refused (stopped); nothing when it is not held."""
    h = crew.held()
    if not h:
        return
    said = crew.held_said(crew.this_host(), h)
    if label and act:
        stopped(label, act, list(on), said)
    fail(said)


def stopped(label, act, on, said):
    """A team's command refused: said on standard error, recorded as the act refused (record.1), and stopped."""
    print(said, file=sys.stderr)
    record.emit(label, act, on, refused=said)
    raise Stopped(1)


def ending(fleet, t):
    """What ends a slot's stage still owed an end as its agent is ended: delivered when its
    deliverable is there, else stopped (stage_ends), what that says and any failure of it dropped."""
    def end(role):
        with silenced():
            stage_ends(fleet, argparse.Namespace(team=t["name"], slot=role, ending=True))
    return end


def reap(fleet, team, landed=None):
    """A team's read on its host (teams.1, record.5): the end of each stage that delivered with nobody waiting recorded,
    late; each slot freed whose unit or fix has merged into its bolt, been dropped from the plan or left the team's
    bolt, once its agent is not working (crew.reaped); then each dependent whose After unit has merged rebased, and the
    worktrees whose work is over removed, at a landing (landed, the bolt) the bolt's branch deleted by sluice after them
    (rebase_and_tidy)."""
    t = team.t
    if team.owes():
        with silenced():
            stage_ends(fleet, argparse.Namespace(team=t["name"], slot=None, ending=False))
    try:
        held = slot_stages(fleet, t)
    except Refusal:
        held = []
    for s in held:
        how, said = crew.reaped(team.agent_of(s["slot"]), t["name"], s["name"], s["stage"], team.status(s["slot"]))
        if how == "free":
            why = team.free(s["slot"], ending(fleet, t))
            if why:
                print(why, file=sys.stderr)
                continue
        if said:
            print(said)
    rebase_and_tidy(fleet, t, landed)


def free_elsewhere(fleet, t, unit):
    """A unit moved from another team's bolt leaves that team's slot (teams.1): each other team of this host whose slot
    holds it frees that slot."""
    for o in sorted(fleet["teams"].values(), key=lambda o: o["name"]):
        if o["name"] == t["name"] or o["machine"] != crew.this_host():
            continue
        other = crew.Team(fleet, o)
        slot = other.holding(unit)
        if slot:
            why = other.free(slot, ending(fleet, o))
            print(why, file=sys.stderr) if why else print(f"{other.agent_of(slot)} is free")


def run_stage(fleet, team, slot, stage, prompt, act, what, obj, on, **extra):
    """A unit's or a fix's stage started fresh in its slot (teams.2, teams.15): the slot's agent ended, the stage's
    agent started, and its prompt sent, taken or sent again. The start is recorded as act, with extra's fields, and its
    end is owed in the stages file. A prompt the agent never took, or one crew can't tell it took, starts no stage: the
    start is recorded refused, no end is owed, the slot and its idle agent stay, and the command stops saying how to
    run the stage again. An agent whose stage stopped short is ended working or not (short_taken)."""
    why = short_taken(fleet, team, slot) or team.stop(slot, ending(fleet, team.t))
    if why:
        stopped(team.label, act, on, why)
    if not team.start(slot, stage):
        raise Stopped(1)
    agent = team.agent_of(slot)
    try:
        how, why = crew.send_taken(fleet, agent, prompt)
        said = None if how == "taken" else crew.never_started(agent, stage, what, obj, team.name, how, why)
    except Refusal as e:
        said = str(e)
    if said:
        stopped(team.label, act, on, said)
    eid = record.emit(team.label, act, on, why=f"{obj.split('/')[0]}({what.rsplit('/', 1)[-1]}): start {stage}", **extra)
    if eid:
        with stages_file(team.t) as lines:
            lines.append([slot, what, stage, eid, obj])


def run_unit_stage(fleet, team, unit, stage, words="", kind="unit"):
    """A unit's stage, or a chore's (kind, plan.11), started in its slot on the team's host (teams.1, teams.2, plan.6):
    refused, and recorded so, while the team is down, when every slot is in flight, and for a construct whose slot's
    agent works unless forced, each before the plan can be written, so an amended unit whose construct can't start keeps
    its mark and reads amended; an agent whose stage stopped short works for nothing, and is ended first (short_taken).
    The team's read frees first what is over, and a slot another team of this host holds the unit in. Whether the stage may start, the place and the stage's prompt are run_check's, a chore's chore_check's,
    its start run_stage's. It stops (Stopped), or is refused (Refusal), having said and recorded why."""
    t, label = team.t, team.label
    on = [f"stage/{unit}/{stage}", f"{kind}/{unit}"]
    if team.down():
        stopped(label, "stage.start", on, crew.down_said(t["name"]))
    not_held(label, "stage.start", on)
    reap(fleet, team)
    free_elsewhere(fleet, t, unit)
    try:
        slot, taken = team.take(kind, unit, f"{t['kit']['dir']}/places/" + (f"chore-{unit}" if kind == "chore" else unit))
    except Refusal as e:
        print(e, file=sys.stderr)
        record.emit(label, "stage.start", on, refused=f"all {t['units']} of {t['name']}'s slots are in flight")
        raise Stopped(1)
    agent = team.agent_of(slot)
    why = short_taken(fleet, team, slot)  # its stage is over, so a construct is not refused for its working
    if why:
        if taken:
            team.drop("slots", slot)
        stopped(label, "stage.start", on + [f"agent/{agent}"], why)
    if stage == "construct" and not team.force and team.status(slot) == "working":
        if taken:
            team.drop("slots", slot)
        stopped(label, "stage.start", on + [f"agent/{agent}"], crew.working_said(agent))
    try:
        facts = run_check(fleet, argparse.Namespace(unit=unit, stage=stage, words=words, label=None, chore=kind == "chore"))
    except Refusal as e:
        if taken:
            team.drop("slots", slot)
        record.emit(label, "stage.start", [f"{CONTEXT.get('kind', kind)}/{unit}", f"stage/{unit}/{stage}"],
                    refused=getattr(e, "recorded", None) or str(e))
        raise
    team.slot_pane(slot, facts["PLACE"])
    # A construct that marked the unit amended says so, and is the entry the plan's commit names; the forecasts its
    # prompt carries are named on its start, so none is carried twice; and the heads of the units it comes after that a
    # construct's new place took.
    extra = dict(Amended="yes", commit=[facts["AMENDED"]], eid=facts["ENTRY"]) if facts["AMENDED"] else {}
    extra.update(Forecast=facts["FORECAST"], Took=facts["TOOK"])
    run_stage(fleet, team, slot, stage, facts["PROMPT"], "stage.start", unit, f"{kind}/{unit}", on + [f"agent/{agent}"], **extra)
    print(f"{agent} has " + ("chore " if kind == "chore" else "") + f"{unit}: {stage}, in {facts['PLACE']}")


def unit_run(fleet, a):
    """crew unit run <unit> construct|code|verify|settle|merge ["<words>"] [--force], or crew chore run <chore>
    code|verify|merge (--chore), on the host of the team whose bolt holds it: its stage started there (run_unit_stage),
    refused while a construct an amendment handed there is starting (handed_state), whose wait is crew unit wait, and
    a construct, code or merge refused while its bolt's landing is in flight (landing_refusal)."""
    t = team_of_unit(fleet, a)
    team = on_team_host(fleet, t, a.force)
    state, said = construct_handed_state(t, a.unit)
    state != "starting" or fail(f"{said}: crew unit wait {a.unit} waits for it")
    if state:
        handed_path(t, a.unit).unlink(missing_ok=True)  # this run is the one that starts it now
    run_unit_stage(fleet, team, a.unit, a.stage, a.words, "chore" if a.chore else "unit")


def unit_wait(fleet, a):
    """crew unit wait <unit> [--timeout <ms>] [--stuck <ms>], on the host of the team whose bolt holds the unit: first,
    while a construct an amendment handed there is starting, its start (handed_state), saying why when it did not
    start; then the wait on the stage the slot holding it owes (stage_wait), within what is left of the timeout, whose
    merge look reads the bolt the plan places the unit in at each look (merge_bolt)."""
    t = team_of_unit(fleet, a)
    team = on_team_host(fleet, t)
    until = time.monotonic() + a.timeout / 1000
    state, said = construct_handed_state(t, a.unit)
    while state == "starting" and time.monotonic() < until:
        time.sleep(1)
        state, said = construct_handed_state(t, a.unit)
    if state == "starting":
        print(f"{said}, past the wait's timeout: wait again")
        return
    if state:
        handed_path(t, a.unit).unlink(missing_ok=True)
        fail(said)
    slot = team.holding(a.unit) or fail(f"no slot of {t['name']} holds {a.unit}")
    left = max(int((until - time.monotonic()) * 1000), 0)
    stage_wait(fleet, argparse.Namespace(team=t["name"], slot=slot, timeout=left, stuck=a.stuck))


def handed_path(t, unit):
    """The marker of a construct an amendment handed to the team's host (construct_hand): there from the hand-off until
    the construct starts, holding who handed it, the process starting it once that has named itself, and why it did
    not start when it could not."""
    return team_state(t) / "handed" / unit


def construct_handed_state(t, unit):
    """handed_state, read on the team's host from the unit's marker and whether its process is alive."""
    try:
        marker = json.loads(handed_path(t, unit).read_text())
    except (OSError, ValueError):
        marker = None
    alive = False
    if marker and marker.get("pid"):
        try:
            os.kill(int(marker["pid"]), 0)
            alive = True
        except (OSError, ValueError):
            alive = False
    return handed_state(unit, marker, alive, time.time())


def construct_hand(fleet, a):
    """crew _construct-again <team> <unit> --by <by> [--force], run by an amendment on its team's host (plan.15,
    code.9). A team taken down starts nothing: the start is recorded refused, and the conductor told, at once. Else the
    construct is handed to a process of its own on this host (--handed), which outlives this command: its marker is
    written (handed_path), and this command answers. The handed process, one at a time on a team, runs construct
    again (run_unit_stage), its agent ended first when forced, then clears the marker, or writes why it did not start
    into it, and tells the conductor what started or why nothing did; crew unit wait waits for it."""
    t = at_work(fleet, a.team)
    team = on_team_host(fleet, t, a.force)
    if a.handed:
        return construct_handed(fleet, team, a)
    if team.down():
        why = crew.down_said(t["name"])
        record.emit(team.label, "stage.start", [f"stage/{a.unit}/construct", f"unit/{a.unit}"], refused=why)
        print(f"construct did not start on unit {a.unit}: {why}")
        amend_tell(fleet, t["name"], *amend_told(a.unit, a.by, None, why))
        return
    mark = handed_path(t, a.unit)
    mark.parent.mkdir(parents=True, exist_ok=True)
    log = mark.parent / f"{a.unit}.log"
    mark.write_text(json.dumps({"by": a.by, "log": str(log), "at": time.time()}))
    argv = ["bash", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bin", "crew"), "_construct-again",
            t["name"], a.unit, "--by", a.by, "--handed"] + (["--force"] if a.force else [])
    try:
        with open(log, "w") as out:
            subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
    except OSError as e:
        mark.unlink(missing_ok=True)
        fail(f"construct could not be handed on {t['machine']}: {e}")
    print(f"construct on unit {a.unit} is handed to {t['machine']}, where it starts again: {t['name']}-conductor is told "
          f"what started, and crew unit wait {a.unit} waits for it")


def construct_handed(fleet, team, a):
    """The handed construct (construct_hand), in its own process on the team's host."""
    t, mark = team.t, handed_path(team.t, a.unit)
    try:
        marker = json.loads(mark.read_text())
    except (OSError, ValueError):
        marker = {"by": a.by}
    mark.write_text(json.dumps({**marker, "pid": os.getpid()}))
    out, err, why = io.StringIO(), io.StringIO(), None
    with open(team_state(t) / "handed" / ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # one handed construct at a time on a team, as one approval's were in turn
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                run_unit_stage(fleet, team, a.unit, "construct")
        except Refusal as e:
            why = str(e)
        except Stopped:
            why = (err.getvalue().strip().splitlines() or ["it stopped"])[-1]
        except Exception as e:  # said in the log, and to the conductor and the wait as any other
            import traceback
            traceback.print_exc()
            why = f"{type(e).__name__}: {e}"
        finally:
            print(out.getvalue() + err.getvalue(), end="")
            if why:
                why = why.rstrip(".")
                mark.write_text(json.dumps({**marker, "failed": why}))
            else:
                mark.unlink(missing_ok=True)
    m = re.search(rf"^(\S+) has {re.escape(a.unit)}: construct, in ", out.getvalue(), re.M)
    amend_tell(fleet, t["name"], *amend_told(a.unit, a.by, (m.group(1) if m else f"a slot of {t['name']}") if not why else None, why))


def fix_run(fleet, a):
    """crew fix <team> <name> "<what is wrong>" | --merge | --drop | --wait, on the team's host (teams.3, teams.5,
    plan.8): the team's read first, but for a wait or a drop, which reads the team last (fix_drop); then what fix_cmd
    decides. A new fix takes a slot, is refused and recorded when
    every slot is in flight or its place is not its own, and starts as a code stage, in a place that could not be made
    ready as in one that could, its agent told what failed (record 0028); a merge starts as a merge stage,
    a submission of the fix to the bolt through sluice; a wait waits on the stage the fix's slot owes (stage_wait)."""
    t = at_work(fleet, a.team)
    team = on_team_host(fleet, t, a.force)
    if a.mode not in ("wait", "drop"):
        not_held()
        reap(fleet, team)
    said = fix_cmd(fleet, argparse.Namespace(team=t["name"], name=a.name, mode=a.mode, bolt=a.bolt))
    slot, fix, place, bolt = said["SLOT"], said["FIX"], said["PLACE"], said["BOLT"]
    if said["REPO"] and crew.with_kit(t, said["REPO"]) is not t:  # the fix's bolt is in another of the team's kits
        t = crew.with_kit(t, said["REPO"])
        team = crew.Team(fleet, t, a.force)
    obj = f"fix/{bolt}/{a.name}"
    on = [obj, f"bolt/{bolt}"]
    if a.mode == "wait":
        return stage_wait(fleet, argparse.Namespace(team=t["name"], slot=slot, timeout=a.timeout, stuck=a.stuck))
    if a.mode == "drop":
        return fix_drop(fleet, team, said, on)
    unready = None
    if a.mode == "start":
        taken = False
        if not slot:  # a new fix never takes over a branch or place that is already there (fix_cmd)
            try:
                slot, taken = team.take("fix", fix, place)
            except Refusal as e:
                print(e, file=sys.stderr)
                record.emit(team.label, "fix.start", on, refused=f"all {t['units']} of {t['name']}'s slots are in flight")
                raise Stopped(1)
        try:
            unready = fix_place(fleet, t, place, fix, bolt)
        except Refusal as e:
            if taken:
                team.drop("slots", slot)
            stopped(team.label, "fix.start", on, str(e))
    team.slot_pane(slot, place)
    agent = team.agent_of(slot)
    if a.mode == "merge":
        run_stage(fleet, team, slot, "merge", f"Merge {fix} into bolt/{bolt}: {said['MERGE']}", "fix.merge", fix, obj, on + [f"agent/{agent}"])
        print(f"{agent} has {fix}: merge, in {place}")
    else:
        if unready:
            print(f"{unready.splitlines()[0].rstrip(':')}; {agent} starts on the fix all the same, told what failed")
        run_stage(fleet, team, slot, "fix", fix_prompt(a.words, place, unready), "fix.start", fix, obj, on + [f"agent/{agent}"])
        fix_said(t, fix, a.words)
        print(f"{agent} has {fix}: code, in {place}")
        landing_held(fleet, t, bolt, a.words)


def fix_drop(fleet, team, said, on):
    """crew fix <team> <name> --drop, once fix_cmd let it (teams.3, record 0028): the fix's slot freed, its agent ended
    when one is up, a working one only with --force (teams.2); its branch marked dropped in the kit's git config
    (fixes_dropped); the drop recorded; then the team's read, whose tidy removes its place and its branch as a dropped
    unit's go, keeping a branch with commits beyond the bolt, named (plan.9, plan.10)."""
    t, slot, fix = team.t, said["SLOT"], said["FIX"]
    if slot:
        agent = team.agent_of(slot)
        on = on + [f"agent/{agent}"]
        why = team.free(slot, ending(fleet, t))
        not why or stopped(team.label, "fix.drop", on, why)
        print(f"{agent} is free: {fix} is dropped")
    if said["BRANCH"]:
        kit_git(fleet, t, t["kit"]["main"], "config", f"branch.{fix}.crew", "dropped")
    record.emit(team.label, "fix.drop", on)
    reap(fleet, team)


def team_status(fleet, a):
    """crew status <team>, on the team's host: the team's read (reap); then its conductor and ops, each with its pane,
    its state as herdr lists it, and its context, compactions and start read from its transcript (crew.context_of);
    each slot with its pane, its agent's state and what it holds (crew.holds_said); each unit of the team's bolt
    carried onto it inside another unit's merge that no slot holds, its merge owed (carried_units, teams.17); and,
    while the team holds two bolts, the one it builds and the one that waits to land (two_held_said, teams.16)."""
    t = at_work(fleet, a.team)
    team = on_team_host(fleet, t, a.force)
    reap(fleet, team)
    print(crew.status_row(f"{t['name']}@{t['machine']}", "pane", "state", "context", "pct", "compacts", "started", "holds"))
    window = int(os.environ.get("WINDOW") or 1000000)
    for role in ("conductor", "ops"):
        pane = team.pane(role)
        st, cells = team.status(role), ("-",) * 4
        if st:
            sess = (team.herdr.agent(pane) or {}).get("agent_session")
            sid = sess.get("value") if isinstance(sess, dict) else None
            found = sorted(pathlib.Path.home().glob(f".claude*/projects/*/{sid}.jsonl")) if isinstance(sid, str) and sid else []
            try:
                if found:
                    with open(found[0], encoding="utf-8", errors="replace") as f:
                        cells = crew.context_of(f, window)
            except OSError:
                pass
        print(crew.status_row(team.agent_of(role), pane or "-", st or "not up", *cells, ""))
    try:
        held = {s["slot"]: s for s in slot_stages(fleet, t)}
    except Refusal:
        held = {}
    for slot in team.slots:
        holds = crew.holds_said(held.get(slot), team.held(slot))
        print(crew.status_row(team.agent_of(slot), team.pane(slot) or "-", (team.status(slot) or "not up") if holds else "free",
                              "-", "-", "-", "-", holds))
    try:
        for unit, bolt, stage in carried_units(fleet, t, {s["name"] for s in held.values()}):
            print(crew.carried_said(unit, bolt, stage))
    except Refusal as e:
        print(e, file=sys.stderr)
    built, waiting, unread = team_holds(fleet, t)
    if unread:
        print(f"which bolts {t['name']} holds can't be told: {unread}", file=sys.stderr)
    elif waiting:
        print(two_held_said(t["name"], built, waiting))


def two_held_said(team, built, waiting):
    """What crew status says of a team holding two bolts (teams.16): the one it builds and the one that waits to land."""
    return f"{team} builds {built}; {waiting} waits to land"


def carried_units(fleet, t, slotted):
    """Each unit of the bolts the team holds whose change its bolt holds open, carried there inside another unit's
    merge, that no slot holds (slotted, the names the slots hold): (unit, bolt, stage), its merge owed (teams.17)."""
    plan = plan_of(fleet, t["label"])
    bolts = held_by(plan, t["name"]) if plan else []
    st = stages_for(fleet, plan, bolts) if bolts else None
    return [(u.name(), b.name(), st.of(u.name())["stage"]) for b in bolts for u in plan.units_of(b.name())
            if st.of(u.name()).get("carried") and u.name() not in slotted]


def team_tidy(fleet, a):
    """crew _tidy <team> [--landed <bolt> --outcome <words> [--said <words>] [--here]], on the team's host: the team's
    read (reap), which a plan
    write that ends work asks for there, and crew rebuild runs once its agents are ended; the conductor's and ops's
    panes told the branch they work for now, none once the bolt has landed or been dropped, and each whose session
    carries the old one handed its restart at its next stop (teams.19, teams.20); after a landing, the bolt's branch
    deleted by sluice once the landing's place is gone (land_delete, plan.19), and its card closed there with the words
    (landing_cards_closed)."""
    t = at_work(fleet, a.team)
    team = on_team_host(fleet, t, a.force)
    reap(fleet, team, a.landed)
    import hold  # hold imports this module
    for name in team.hint_standing(crew.team_bolt(t)):
        hold.hand(name)
    if a.landed:
        landing_cards_closed(fleet, t, a.landed, a.outcome or "", a.said, a.here)


def unit_free(fleet, a):
    """crew unit free <unit> [--team <team>]: a slot still holding a unit no longer in its team's bolt freed now (teams.1),
    rather than at the read after its agent settles, its agent ended and the worktrees whose work is over removed; with
    no team named, the team of this host whose slot holds it. Refused while the unit is in the team's bolt, which a drop
    frees, or while its place has uncommitted changes, which are the user's."""
    if a.team:
        t = at_work(fleet, a.team)
    else:
        mine = [o for n, o in sorted(fleet["teams"].items()) if o["machine"] == crew.this_host()]
        t = next((o for o in mine if crew.Team(fleet, o).holding(a.unit)), None) or fail(
            f"no team on this host holds {a.unit} in a slot; name its team: crew unit free {a.unit} --team <team>")
    team = on_team_host(fleet, t, a.force)
    slot = team.holding(a.unit) or fail(f"no slot of {t['name']} holds {a.unit}")
    said = in_bolt(fleet, t, a.unit)
    not said or fail(f"{said}: drop it with crew {said.split()[0]} drop, which frees its slot")
    path = (team.held(slot) + [""] * 4)[3]
    if os.path.isdir(path) and subprocess.run(["git", "-C", path, "status", "--porcelain"], capture_output=True, text=True, env=gitenv()).stdout.strip():
        fail(f"{path} has uncommitted changes: they are the user's to keep or discard before the slot is freed")
    why = team.free(slot, ending(fleet, t))
    not why or fail(why)
    print(f"{team.agent_of(slot)} is free")
    try:
        tidy(fleet, argparse.Namespace(team=t["name"]))
    except Refusal as e:
        print(e, file=sys.stderr)


# ------------------------------------------------------------- the standing agents' commands, one process each

def greeting(fleet, agents, roles):
    """Each agent outside a team that a command started or brought back is greeted (teams.7), side by side, so one
    waiting on a question holds back no other; a greeting that can't be sent fails nothing. Returns the greetings, for
    the command to wait on before it ends (greeted)."""
    import threading

    def greet(name):
        try:
            crew.greet_standing(fleet, name)
        except Refusal as e:
            print(e, file=sys.stderr)
    out = [threading.Thread(target=greet, args=(agents.agent_of(r),)) for r in roles]
    for th in out:
        th.start()
    return out


def greeted(greetings):
    """Once every greeting has been sent, or given up on."""
    for th in greetings:
        th.join()


def greet_team(fleet, t, roles, bolt=None, notice=""):
    """Each of a team's roles a command greets (crew.greeted_roles), side by side, so neither waits on the other
    (teams.7): the conductor told to read where its bolt stands and carry on, before anyone asks it anything, the
    greeting opening with the notice of its restart when there is one, then the bolt a give has just given it, else,
    when its team holds two, the bolt it builds and the one waiting to land with its landing card and fixes
    (conductor_bolts, teams.16), and the units of its bolts that wait amended, for it to start their construct
    (plan.15); ops told who it is, the bolt its team holds, and to wait to be told. What each is told is read before
    either is sent; a greeting that can't be sent fails nothing. Returns the greetings, for the command to wait on
    before it ends (greeted)."""
    import threading
    sends = []
    if "conductor" in roles:
        said = [notice]
        try:
            said += [f"Your team now holds the bolt {bolt}."] if bolt else [conductor_bolts(fleet, t), amended_units(fleet, t)]
        except Refusal as e:
            said.append(f"crew could not read what your team holds ({e}): read crew bolts.")
        first = " ".join(x for x in said if x)
        sends.append(lambda first=first: crew.greet(fleet, t["name"], first=f"{first} " if first else ""))
    if "ops" in roles:
        try:
            held, waiting, unread = (bolt, None, None) if bolt else team_holds(fleet, t)
        except Refusal as e:
            held, waiting, unread = None, None, str(e)
        sends.append(lambda: crew.greet_ops(fleet, t["name"], held, unread, waiting=waiting))

    def send(greet):
        try:
            greet()
        except Refusal as e:
            print(e, file=sys.stderr)
    out = [threading.Thread(target=send, args=(s,)) for s in sends]
    for th in out:
        th.start()
    return out


def conductor_bolts(fleet, t):
    """What a team's conductor started afresh is told of the two bolts its team holds (two_bolts_said), read on the
    team's host, where its cards are: "" when it holds one or none."""
    plan = plan_of(fleet, t["label"])
    if plan is None or len(held_by(plan, t["name"])) < 2:
        return ""
    new = team_building(fleet, plan, t)
    old = waiting_bolt(plan, t["name"], new)
    k, why = stages_for(fleet, plan, [plan.bolt(old)]).kit(plan.bolt(old))
    fixes = [f.rsplit("/", 1)[-1] for f in fixes_in_flight(k.get("fixes", []), old)] if k else None  # fix/<bolt>/<name>
    return two_bolts_said(t["name"], new, old, plan.bolt(old).get("Repo") or t["kit"]["name"], t["label"], fixes, why)


def two_bolts_said(team, new, old, kit, label, fixes, unread=None):
    """What a conductor started afresh while its team holds two bolts is told first (teams.16): the bolt it builds
    (new), the one that waits to land (old), a row of its kit's landings card, main-level ops's, with the wait on its
    reading that brings the user's notes, and each fix in flight on it (fixes, by the name crew fix takes), with how to
    wait on it; when its kit could not be read (unread), that, rather than name no fix (read.1)."""
    said = (f"Your team now builds the bolt {new}. Bolt {old} waits to land, a row of {kit}'s landings card, {label}-ops's: "
            f"run crew card wait land/{old} in the background for its reading's notes.")
    if unread:
        said += f" crew could not read its fixes ({unread}): read crew status {team}."
    for f in fixes or []:
        said += f" Fix {f} is in flight on it: wait on it with crew fix {team} {f} --wait --bolt {old}."
    return said


def team_holds(fleet, t):
    """The bolt a team builds (team_building), for its ops's greeting, or None when it holds none, and the bolt that
    waits to land beside it, or None; and what crew could not read of its plan or of which bolt it builds, else None,
    which the greeting says rather than name no bolt (read.1)."""
    CONTEXT["label"] = t["label"]
    errors = {}
    found = plans(fleet, [t["label"]], errors)
    plan = found[0][3] if found else None
    built = None
    if plan:
        try:
            built = team_building(fleet, plan, t)
        except Refusal as e:
            errors[f"which bolt {t['name']} builds"] = str(e)
    return (built, waiting_bolt(plan, t["name"], built) if built else None,
            "; ".join(f"{k} could not be read: {v}" for k, v in errors.items()) or None)


def picked(team, roles):
    """The standing roles a command names, or all of them (crew.roles_picked); a role there is none of stops it, said,
    with exit 2."""
    try:
        return crew.roles_picked(roles, team.standing)
    except Refusal as e:
        print(e, file=sys.stderr)
        raise Stopped(2)


def started_all(team):
    """Each standing role of a team started fresh: the roles started. One that can't start stops the command."""
    for role in team.standing:
        if not team.start(role):
            raise Stopped(1)
    return list(team.standing)


def team_cmd(fleet, a):
    """crew up|close|rebuild|restart|resume|clear|down <team>, on the team's host, one process (code.7): the team's
    conductor and ops started, brought back, cleared or ended there (teams.2, teams.6, teams.7), each act recorded
    (record.1). close and rebuild end every agent, working or not."""
    t = at_work(fleet, a.team)
    team = on_team_host(fleet, t, a.force or a.act in ("close", "rebuild"))
    end, name = ending(fleet, t), t["name"]
    if a.act in ("up", "rebuild", "restart", "resume"):
        not_held()
    if a.act == "up":
        for role in team.standing:
            not team.status(role) or fail(crew.already_up_said(team.agent_of(role), name))
        team.mark(down=False)
        team.panes()
        started = started_all(team)
        team.record("team.up", f"team({name}): up", started)
        greeted(greet_team(fleet, t, crew.greeted_roles("up", started, team.fresh)))
    elif a.act == "close":
        team.teardown(end)
        team.mark(down=True)
        team.record("team.close", f"team({name}): close", team.ended)
        print(f"{name} is closed")
    elif a.act == "rebuild":  # a slot whose work is over, its agent ended with the rest, is freed rather than kept
        team.teardown(end)
        reap(fleet, team)
        team.mark(down=False)
        team.panes()
        started = started_all(team)
        team.record("team.rebuild", f"team({name}): rebuild", started)
        greeted(greet_team(fleet, t, crew.greeted_roles("rebuild", started, team.fresh)))
    elif a.act == "restart":
        roles, stopped_ = picked(team, a.roles), []
        team.mark(down=False)
        for role in roles:
            why = team.stop(role, end)
            print(why, file=sys.stderr) if why else stopped_.append(role)
        team.panes()
        for role in stopped_:
            if not team.start(role):
                raise Stopped(1)
            team.record("agent.restart", f"team({name}): restart {role}", [role])
        greeted(greet_team(fleet, t, crew.greeted_roles("restart", stopped_, team.fresh, a.greet)))
    elif a.act == "resume":
        roles, back = picked(team, a.roles), []
        team.mark(down=False)
        team.panes()
        for role in roles:
            if team.status(role):
                print(f"{team.agent_of(role)} is already up")
                continue
            if team.start(role, "resume"):
                team.record("agent.resume", f"team({name}): resume {role}", [role])
            else:
                print(f"{team.agent_of(role)} did not come back with its conversation; starting it fresh")
                if not team.start(role):
                    raise Stopped(1)
                team.record("agent.start", f"team({name}): start {role}", [role])
            back.append(role)
        # resume greets only what it had to start fresh: a conductor it brought back with its conversation is sent, as
        # crew's notice, the units of its bolt that wait amended
        greet = crew.greeted_roles("resume", back, team.fresh)
        line = amended_units(fleet, t) if "conductor" in back and "conductor" not in greet else ""
        if line:
            crew.tell(fleet, f"{name}-conductor", line)
        greeted(greet_team(fleet, t, greet))
    elif a.act == "clear":
        role = picked(team, a.roles[:1])[0]
        agent, pane = team.agent_of(role), team.pane(role)
        why = crew.clear_refusal(agent, team.status(role), team.force)
        not why or fail(why)
        r = team.herdr.run("agent", "prompt", pane, "/clear")
        r.returncode == 0 or fail((r.stderr or "").strip() or f"herdr could not send /clear to {agent}")
        crew.nap(2)
        if not team.give_name(pane, agent):
            raise Stopped(1)
        team.record("agent.clear", f"team({name}): clear {role}", [role])
        print(f"{agent} cleared")
    else:
        for role in (*team.standing, *team.slots):
            why = team.stop(role, end)
            if why:
                print(why, file=sys.stderr)
        team.mark(down=True)
        team.record("team.down", f"team({name}): down", team.ended)
        print(f"{name} is down; its panes are still there.")


def needs_cmd(fleet, a):
    """crew needs "<what you need>", run by a stage's agent: its team and slot read from its own
    name (crew.stage_agent), on the team's host, where its stage ends short (stage_needs)."""
    who = record.who()
    found = crew.stage_agent(list(fleet["teams"]), who)
    if not found:
        print(f"{who} runs no stage crew is waiting on", file=sys.stderr)
        raise Stopped(1)
    a.team, a.slot = found
    on_team_host(fleet, crew.team_of(fleet, a.team))
    stage_needs(fleet, a)


def dispatch_up(fleet, label):
    """This host's dispatcher of a partition started when it is not up, in a workspace of its own, recorded: its Agents
    and the roles started, for the caller to greet."""
    not_held()
    d = crew.standing(fleet, "dispatch", label)
    d.ensure()
    d.mark(down=False)
    d.panes()
    started = d.start_standing()
    d.record("main.up", f"main({label}): up {d.agent_of('dispatcher')}", started)
    return d, started


def dispatch_cmd(fleet, a):
    """crew _dispatch up|down|status <label>: this host's dispatcher of the partition, started and greeted, ended, or
    listed, as crew main runs it on each host its teams run on."""
    if a.act == "up":
        greeted(greeting(fleet, *dispatch_up(fleet, a.label)))
        return
    d = crew.standing(fleet, "dispatch", a.label)
    d.ensure()
    name = d.agent_of("dispatcher")
    if a.act == "down":
        why = d.stop("dispatcher")
        if why:
            print(why, file=sys.stderr)
        d.mark(down=True)
        d.record("main.down", f"main({a.label}): down {name}", d.ended)
        print(f"{name} is down")
    else:
        print("%-34s %-8s %s" % (name, d.pane("dispatcher"), d.status("dispatcher") or "not up"))


def elsewhere(fleet, host, *argv):
    """crew on another host, run as the one asking (crew_argv) and never prompting (code.3): its process, its output
    this command's."""
    return subprocess.Popen(["ssh", "-o", "BatchMode=yes", fleet["hosts"][host]["ssh"], shlex.join(crew.crew_argv(fleet, host, *argv))],
                            stdin=subprocess.DEVNULL)


def moved_role(fleet, label, ms):
    """What refuses a main level's up while one of its roles' agents still runs in a session the role no longer stands
    in, its pane recorded there, so up would start it a second time in its own: None when none does."""
    for m in ms:
        for role, *_ in m.lines("panes"):
            if role in crew.MAIN_STANDING and role not in m.standing and m.status(role):
                return (f"{label}-{role} still runs in session {m.session} ({m.pane(role)}), and its partition names it another session "
                        f"now: crew main down {label} ends it, then crew main up {label} starts it there")
    return None


def main_cmd(fleet, a):
    """crew main up|down|status <label>, on the main level's host: its design agent, planner, ops and operator, one tab
    each in the <label> workspace of the session each runs in (record 0035), started and greeted, ended, or listed; and
    the dispatcher on each host the partition's teams run on, that host's own, side by side, so one waiting on a
    question holds back no other host's. A dispatcher that fails fails main up once the rest are up. Up refuses while a
    role's agent still runs in a session it no longer stands in (moved_role), which down ends."""
    p = crew.partition_of(fleet, a.label)
    arrived(fleet, p["machine"])
    ms = crew.mains(fleet, a.label, a.force)
    for m in ms:
        m.ensure()
    here, label = crew.this_host(), p["label"]
    hosts = crew.partition_hosts(fleet, label)
    if a.act == "up":
        not_held()
        moved = moved_role(fleet, label, ms)
        not moved or fail(moved)
        started_in = []
        for m in ms:
            m.mark(down=False)
            m.panes()
            started = m.start_standing()
            m.record("main.up", f"main({label}): up", started)
            started_in.append((m, started))
        rc, greetings, away = 0, [], [(h, elsewhere(fleet, h, "_dispatch", "up", label)) for h in hosts if h != here]
        if here in hosts:
            try:
                greetings += greeting(fleet, *dispatch_up(fleet, label))
            except Refusal as e:
                print(e, file=sys.stderr)
                rc = 1
            except Stopped as e:
                rc = e.code
        for m, started in started_in:
            greetings += greeting(fleet, m, started)
        for _, proc in away:
            rc = proc.wait() or rc
        greeted(greetings)
        if rc:
            raise Stopped(rc)
    elif a.act == "down":
        for m in ms:
            # Every agent its panes file names, a role that stood here before its partition named it a session apart
            # among them, so down ends what up would refuse over.
            for role in [r for r, *_ in m.lines("panes") if r in crew.MAIN_STANDING]:
                why = m.stop(role)
                if why:
                    print(why, file=sys.stderr)
            m.mark(down=True)
            m.record("main.down", f"main({label}): down", m.ended)
        print(f"{label}'s main level is down; its panes are still there.")
        for host in hosts:
            if host == here:
                dispatch_cmd(fleet, argparse.Namespace(act="down", label=label))
            elif elsewhere(fleet, host, "_dispatch", "down", label).wait():
                raise Stopped(1)
    else:
        for m in ms:
            for role in m.standing:
                print("%-34s %-8s %-14s %s" % (m.agent_of(role), m.pane(role), m.session, m.status(role) or "not up"))
        for host in hosts:
            if host == here:
                dispatch_cmd(fleet, argparse.Namespace(act="status", label=label))
            elif elsewhere(fleet, host, "_dispatch", "status", label).wait():
                print(f"{label}-dispatch-{host}  {host} did not answer")


def review_cmd(fleet, a):
    """crew review <label> [--wait [--timeout <ms>]], on the main level's host: the partition's reviewer started fresh
    for the batch of changes due, in a review tab of the main level's workspace beside the planner, and sent its batch as
    its prompt, the start recorded; with --wait, the wait for its summary, which records the batch, and then its agent
    ended and its tab closed. Refused while a reviewer still reviews, or the main level is not up."""
    p = crew.partition_of(fleet, a.label)
    arrived(fleet, p["machine"])
    m = crew.main_holding(fleet, a.label, "reviewer")
    m.ensure()
    label, agent = p["label"], m.agent_of("reviewer")
    if a.wait:
        summary = review_wait(fleet, argparse.Namespace(label=label, timeout=a.timeout))
        why = m.stop("reviewer")
        if why:
            print(why, file=sys.stderr)
        m.close_pane("reviewer")
        tab = m.get("layout", "tab:review")
        if tab:
            m.herdr.run("tab", "close", tab)
            m.drop("layout", "tab:review")
        print(f"batch summary: {summary}")
        return
    not_held()
    not m.status("reviewer") or fail(f"{agent} is still reviewing a batch: crew review {label} --wait waits for its summary")
    m.get("layout", crew.ws_key(label)) or fail(f"{label}'s main level is not up in session {m.session}: crew main up {label}")
    b = review_start(fleet, argparse.Namespace(label=label))
    if not m.herdr.live(m.pane("reviewer")):  # the tab is kept in the layout, so the batch's end closes it
        made = m.tab(label, "review", m.cwd, "reviewer")
        m.put("layout", "tab:review", made["tab"]["tab_id"])
    if not m.start("reviewer"):
        raise Stopped(1)
    m.herdr.run("agent", "prompt", m.pane("reviewer"), b["PROMPT"])
    record.emit(label, "review.start", [f"batch/{b['N']}", f"agent/{agent}"] + [f"unit/{u}" for u in b["NAMES"].split()],
                why=f"batch({b['N']}): start review", Batch=b["N"], Units=b["UNITS"])
    print(f"{agent} is reviewing batch {b['N']} of {label}, into {b['FILE']}: crew review {label} --wait waits for it")


def console_cmd(fleet, a):
    """crew console up|down <label>: the partition's console on this host, the flow, rail and board tabs in the
    `console` workspace of this host's `<label>` session, starting no agent (record 0035): flow, following the run
    record; rail, what waits on the user above and a shell below with this crew on its path; and board, drawn from what
    the rail's loop read. Up opens each tab once, and a tab whose pane holds its shell alone, as herdr brings each pane
    back after a restart, runs its command there again, while one running anything else is left and said
    (crew.tab_holds, read.4); swancloud's timer runs it every five minutes, so a restart leaves the agents' bands
    unrefreshed no longer than that. An operator agent this host's console held before the operator was a main-level
    role is ended and its workspace closed once it is not working (retire_operator). Down closes the console's tabs."""
    c = crew.standing(fleet, "console", a.label)
    c.ensure()
    label, crew_cmd = a.label, shlex.quote(str(crew.HOME / "plugin/bin/crew"))
    if a.act == "down":
        c.teardown()
        print(f"{label}'s console on {crew.this_host()} is closed")
        return
    retire_operator(fleet, label)

    def keep(tab, words):
        run, pane = f"bash {crew_cmd} {shlex.join(words)}", c.pane(tab)
        if not c.herdr.live(pane):
            c.opened("console", tab, c.cwd, tab)
            c.herdr.run("pane", "run", c.pane(tab), run)
            return
        held, what = crew.tab_holds(c.herdr.process_info(pane), words)
        if held == "shell":
            c.herdr.run("pane", "run", pane, run)
            print(f"{label}'s {tab} tab ({pane}) held its shell alone; its {tab} runs there again")
        elif held == "other":
            print(f"{label}'s {tab} tab ({pane}) runs {what}, not crew's {tab}; crew left it", file=sys.stderr)
        elif held is None:
            print(f"{label}'s {tab} tab ({pane}): {what}; crew left it", file=sys.stderr)
    keep("flow", ["events", "--follow", "--label", label])
    keep("rail", ["_rail", label])
    if not c.herdr.live(c.pane("rail-shell")):
        c.put("panes", "rail-shell", c.split(c.pane("rail"), "down", c.cwd))
        c.herdr.run("pane", "run", c.pane("rail-shell"), f"export PATH={shlex.quote(str(crew.HOME / 'plugin/bin'))}:$PATH")
    keep("board", ["_board", label])


def retire_operator(fleet, label):
    """The operator agent this host ran in its operator session before record 0035, `<label>-operator-<host>`, ended,
    and the panes crew recorded in its `operator` workspace closed, once it is not working; one working, or one that
    did not exit, is left and said, and its console opens beside it. Nothing to do once it is gone."""
    state = pathlib.Path.home() / f".local/state/crew/{label}-operator"
    if not (state / "panes").exists():
        return
    host = crew.this_host()
    old = crew.Agents(fleet, "retired", label, label, label, state, ("operator",), str(state), host, host)
    old.agent_of = lambda role: f"{label}-operator-{host}"
    if old.status("operator") == "working":
        print(f"{label}-operator-{host} is working; it is no longer started (the operator is {label}-operator, at the main level), "
              f"and once it is not working the console ends it", file=sys.stderr)
        return
    why = old.stop("operator")
    if why:
        print(why, file=sys.stderr)
        return
    # Only the panes crew recorded there: a tab the user opened in that workspace stays, and the workspace goes with
    # its last pane.
    for _, pane, *_ in old.lines("panes"):
        if old.herdr.live(pane):
            old.herdr.run("pane", "close", pane)
    os.replace(state, state.with_name(f"{label}-operator.retired-{int(time.time())}"))
    print(f"{label}-operator-{host} is ended and its operator tabs closed: the operator is {label}-operator, at {label}'s main level")


def revive_cmd(fleet, a):
    """crew revive, after a restart: on this host, each team's, main level's in each of its sessions, and dispatcher's
    standing role whose pane came back with no agent in it, or dead, closed and opened again in its layout first (crew.revived,
    teams.2), picked up from its last conversation, a team's conductor greeted, and its ops when it had none to pick up
    (crew.greeted_roles), and every agent brought back outside a team greeted; one taken down with crew down stays
    down. What can't be revived is said, and the rest still are. Nothing is revived while this host is held (teams.19):
    crew go revives it."""
    not_held()
    greetings = []
    every = [(kind, scope, a) for kind, scope in crew.here(fleet)
             for a in ([None] if kind == "team" else crew.mains(fleet, scope) if kind == "main" else [crew.standing(fleet, kind, scope)])]
    for kind, scope, agents in every:
        try:
            agents = agents or crew.Team(fleet, crew.team_of(fleet, scope))
            if not agents.lines("panes"):
                continue
            if agents.down():
                print(f"{scope} was taken down; it stays down")
                continue
            back, ways = [], {r: crew.revived(agents.herdr.item(agents.pane(r)), agents.status(r)) for r in agents.standing}
            if "dead" in ways.values():
                agents.panes()
            for role in agents.standing:
                if not ways[role]:
                    continue
                if ways[role] == "empty":
                    crew.nap(10)
                    if agents.status(role, fresh=True):  # herdr may still be resuming it
                        continue
                if not agents.start(role, "resume"):
                    continue
                agents.record("agent.resume", f"{kind}({scope}): resume {agents.agent_of(role)}", [role])
                back.append(role)
            greetings += (greet_team(fleet, agents.t, crew.greeted_roles("revive", back, agents.fresh)) if kind == "team"
                          else greeting(fleet, agents, back))
        except Refusal as e:
            print(e, file=sys.stderr)
    greeted(greetings)


# ----------------------------------------------------------------------------------------------- crew bolts

def bolts_view(fleet, a):
    label = default_label(fleet, a)
    labels = [label] if label else list(fleet["partitions"])
    errors = {}
    found = plans(fleet, labels, errors)
    held = [(b.get("Team"), b.name(), b.get("Repo")) for _, _, _, p in found if p for b in p.bolts() if b.get("Team") and a.bolt in (None, b.name())]
    # Each kit's GitHub fetched once on its host before it is read: what has merged into a bolt is on GitHub (plan.19).
    data = bolts_data(fleet, labels, found, survey(fleet, held, fetch=True), errors, a.bolt)
    if a.bolt and not any(b for p in data["partitions"] for pl in p["plans"] for b in pl["bolts"]):
        fail(f"no bolt {a.bolt} in the plans of " + ", ".join(labels))
    if a.json:
        print(json.dumps(data, indent=1))
        sys.exit(1 if errors else 0)
    print(bolts_text(data))
    if errors:
        sys.exit("\n".join(errors.values()))


def bolts_data(fleet, labels, found, sv, errors, bolt=None):
    """What crew bolts shows, from the plans read (found) and the survey of the hosts holding their bolts (sv): each
    partition's plans, each bolt with its team, host, state, verification (sluice's verdict on its last landing, as
    kit.verification reads it, for a bolt whose kit was read), units and chores in build order with their kinds and
    stages read from the kits, and fixes, and the queue; the hosts that did not answer and the plans that could not be
    read. With bolt, that bolt alone."""
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
                if bolt not in (None, b.name()):
                    continue
                t = bolt_team(fleet, b)
                k, _ = st.kit(b) if t else (None, None)
                units = [dict(unit=u.name(), kind=kind_of(u), after=u.all("After"), sources=u.all("Source"), **{
                    x: st.of(u.name())[x] for x in ("stage", "tasks", "worktree")}) for u in plan.work_of(b.name())]
                fixes = [dict(fix=f["fix"], worktree=f["path"], merged=f["merged"]) for f in (k["fixes"] if k else []) if f["bolt"] == b.name()]
                bk = (k or {}).get("bolts", {}).get(b.name()) or {}
                verified = dict(zip(("state", "said"), kit.verification(bk.get("head"), bk.get("verdict")))) if k and bk.get("exists") else None
                bolts.append(dict(bolt=b.name(), repo=b.get("Repo"), goal=b.get("Goal"), sources=b.all("Source"), team=b.get("Team"),
                                  host=t["machine"] if t else None, state=st.bolt_state(b), verification=verified, units=units, fixes=fixes))
            queue = [] if bolt else [dict(unit=u.name(), kind=kind_of(u), repo=u.get("Repo"), stage="queued", sources=u.all("Source"))
                                     for u in plan.queue()]
            part["plans"].append({"repo": repo, "plan": tip, "bolts": bolts, "queue": queue})
        data["partitions"].append(part)
    return data


def bolts_text(data):
    """crew bolts as text: each plan's branch and tip, each bolt with its repo, team and state, its verification when
    its kit was read, and each unit with its stage, tasks and place, each chore among them with `chore` before its stage, each fix, the queue by repo with each
    unit's and chore's sources, and each host that did not answer."""
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
                if b.get("verification"):
                    lines.append(f"  verification: {b['verification']['state']}, {b['verification']['said']}")
                for u in b["units"]:
                    stage = ("chore " if u.get("kind") == "chore" else "") + u["stage"] + (
                        f" {u['tasks'][0]}/{u['tasks'][1]}" if u["stage"] in ("code", "verify") and u["tasks"] else "")
                    where = "places/" + os.path.basename(u["worktree"]) if u["worktree"] else ""
                    lines.append(f"  {u['unit']:<40} {stage:<12} {where}".rstrip())
                for f in b["fixes"]:
                    lines.append(f"  {f['fix']:<40} {'fix merged' if f['merged'] else 'fix':<12} places/{os.path.basename(f['worktree'])}")
            repos = sorted({u["repo"] for u in pl["queue"]})
            for r in repos:
                lines.append(f"queue  {r}")
                for u in (x for x in pl["queue"] if x["repo"] == r):
                    queued = "chore queued" if u.get("kind") == "chore" else "queued"
                    lines.append(f"  {u['unit']:<40} {queued:<12} {', '.join(u['sources'])}".rstrip())
    for h, why in data["unreachable"].items():
        lines.append(f"{h} did not answer ({why}): the stages of its bolts are unknown")
    return "\n".join(lines)


# ------------------------------------------------------------------------------------------------- batches

BATCH_DAYS = 60  # how far back the run record is read for constructs and batches
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
    """The partition's run record from days back, read from its branch alone, no host asked for it (read.5); refused
    naming the branch when it cannot be read (read.1), since what is due can't be told without it."""
    since = (datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=days)).isoformat()
    entries, missing = record.gather(fleet, [label], since)
    return entries if not missing else fail(unread_batches(state_of(fleet, label)[0], missing))


def unread_batches(repo, missing):
    """Why crew can't tell what a batch holds or is due, the branch named that could not be read, {<label>/main: why}."""
    return "crew can't tell which changes have been in a batch: " + "; ".join(f"{k} of {repo} could not be read ({v})" for k, v in missing.items())


def batches(entries):
    """The partition's review batches, oldest first: (number, when, [(unit, team, commit)])."""
    return [(int(e["Batch"]), e["At"], units_of_batch(e)) for e in entries
            if e.get("Act") == "review.batch" and not e.get("Refused") and (e.get("Batch") or "").isdigit()]


def batch_posts(entries):
    """The batch card keys the run record holds a card.post under."""
    return {e["Key"] for e in entries if e.get("Act") == "card.post" and (e.get("Key") or "").startswith("batch/")}


def card_part(key, units):
    """The units of a batch that its card under key holds: every one for batch/<n>, and for batch/<n>-<k>, a card of a
    batch posted as cards of five before a batch was one card, the k-th five."""
    _, _, k = key.split("/")[1].partition("-")
    return units[(int(k) - 1) * 5:int(k) * 5] if k else units


def batch_cards(n, units, posts):
    """Batch n's cards, as (key, the units it holds): one, batch/<n>, holding every unit, or, for a batch posted as
    cards of five before a batch was one card, each batch/<n>-<k> a card was posted under (posts, batch_posts), which
    is read as it was posted until it closes, and no batch/<n>."""
    old = sorted((int(m.group(1)), k) for k in posts for m in [re.fullmatch(rf"batch/{n}-(\d+)", k)] if m)
    return [(k, card_part(k, units)) for _, k in old] or [(f"batch/{n}", units)]


def latest_changes(entries):
    """Each unit's latest change, the commit its last delivered construct left, and when: {unit: (commit, when)}."""
    latest = {}
    for e in entries:
        if e.get("Act") != "stage.end" or e.get("Ended") != "delivered" or e.get("Refused"):
            continue
        st = next((o for o in e["On"] if o.startswith("stage/") and o.endswith("/construct")), None)
        unit = st.split("/")[1] if st else None
        got = e.get("Delivered") or ""
        if unit and got.startswith(f"unit/{unit}@"):
            latest[unit] = (got.rpartition("@")[2], e["At"])
    return latest


def batch_closed(entries):
    """The batch card keys the run record holds closed, entries oldest first: those whose last act under the key is a
    card.close, not refused and not lost to its owner, once the user sent the card back with a tap or sent its reading
    session, or closed it in Pending You, or crew's own close of the batch, a batch.close not refused, card or none,
    once the user sent its reading session and no card of it was closed (batch_read_close), or the sweep found it
    waits on nothing. A card posted under the key after it, one followed or raised again, opens the key again, and a
    close as lost leaves it open for its card posted again; a refused post or close changes nothing, since neither
    Pending You nor crew did it. A batch the user answered in a main-level pane (pane_answered) has every key of it
    closed for good, whatever card is posted under one after, in whichever order the hosts' entries came."""
    closed = set()
    for e in entries:
        key, act = e.get("Key") or "", e.get("Act")
        if not key.startswith("batch/") or e.get("Refused") or (act != "batch.close" and not e.get("Card")):
            continue
        if act == "card.post" or (act == "card.close" and e.get("State") == "lost"):
            closed.discard(key)
        elif act in ("card.close", "batch.close"):
            closed.add(key)
    return closed | set(pane_answered(entries))


def pane_answered(entries):
    """Each batch card key of a batch the user answered in their own words in a main-level pane, a batch.answer not
    refused (crew card answer), as {key: (who recorded it, when)}: batch/<n>, and every batch/<n>-<k> any entry is
    under, a card of a batch posted as cards of five before. The first answer of a batch is its answer."""
    answered = {}
    for e in entries:
        if e.get("Act") == "batch.answer" and not e.get("Refused") and (e.get("Batch") or "").isdigit():
            answered.setdefault(int(e["Batch"]), (e.get("By"), e.get("At")))
    keys = {e.get("Key") for e in entries if (e.get("Key") or "").startswith("batch/")}
    out = {f"batch/{n}": by for n, by in answered.items()}
    for k in keys:
        m = re.fullmatch(r"batch/(\d+)-\d+", k)
        if m and int(m.group(1)) in answered:
            out[k] = answered[int(m.group(1))]
    return out


def pane_said(by, at):
    """Where and when a batch was answered in a pane, as pane_answered gives it: "answered in <agent>'s pane at
    <HH:MM>Z"."""
    return f"answered in {by}'s pane at {(at or '')[11:16]}Z"


def batch_settled(entries):
    """The batch card keys whose batch waits on nothing (briefs.12), from the run record's entries, oldest first, as
    {key: why}: each batch/<n>, or for a batch posted as cards of five before, each batch/<n>-<k> (batch_cards), every
    unit of which has landed, a bolt.land not refused naming it, or was dropped since the batch was made, a unit.drop or
    bolt.drop not refused naming it later in the entries' order than the batch's review.batch, since a drop from before
    says nothing of a unit added again under its name, or is held by a later batch not refused, at any commit, since a
    later batch held the unit's latest change when it was made. Landings, drops and batches are only ever added, so a
    key once settled stays so. Whether a card of it closed is not read: batch_closed is what the user's answer closed.
    Each unit is counted once, the first of landed, dropped, held later true of it. The words name the units in the
    batch's order: those landed, those dropped, then, oldest first, each later batch with the units it is the newest to
    hold."""
    landed = {o[5:] for e in entries if e.get("Act") == "bolt.land" and not e.get("Refused") for o in e.get("On") or [] if o.startswith("unit/")}
    made_at, dropped_at = {}, {}
    for i, e in enumerate(entries):
        if e.get("Refused"):
            continue
        if e.get("Act") == "review.batch" and (e.get("Batch") or "").isdigit():
            made_at[int(e["Batch"])] = i
        elif e.get("Act") in ("unit.drop", "bolt.drop"):
            dropped_at.update({o[5:]: i for o in e.get("On") or [] if o.startswith("unit/")})
    made, posts, out = batches(entries), batch_posts(entries), {}
    for n, _, units in made:
        for key, part in batch_cards(n, units, posts):
            names = list(dict.fromkeys(u for u, *_ in part))
            here = [u for u in names if u in landed]
            gone = [u for u in names if u not in landed and dropped_at.get(u, -1) > made_at[n]]
            later = {u: max((m for m, _, us in made if m > n and any(v == u for v, *_ in us)), default=None)
                     for u in names if u not in here + gone}
            if not names or not all(later.values()):
                continue
            why = ([f"{joined(here)} {'has' if len(here) == 1 else 'have'} landed"] if here else []) + (
                [f"{joined(gone)} {'was' if len(gone) == 1 else 'were'} dropped"] if gone else []) + [
                f"batch {m} holds " + ("a newer change of " if len(us) == 1 else "newer changes of ") + joined(us)
                for m in sorted(set(later.values())) for us in [[u for u in later if later[u] == m]]]
            out[key] = "its batch waits on nothing: " + "; ".join(why)
    return out


def awaiting_answer(entries):
    """Each unit whose latest change has been in a batch whose card the user has not answered (briefs.12), as {unit: the
    batch}: no card of a batch holding the change at its commit (batch_cards) is closed (batch_closed), so its row
    still waits on the rail. A unit whose latest change no batch has held is due_changes', and a chore is in no batch."""
    latest, closed, posts, held = latest_changes(entries), batch_closed(entries), batch_posts(entries), {}
    for n, _, units in batches(entries):
        for key, part in batch_cards(n, units, posts):
            for u, _, sha in part:
                if u in latest and latest[u][0] == sha:
                    held.setdefault(u, []).append((n, key in closed))
    return {u: max(n for n, _ in ns) for u, ns in held.items() if not any(answered for _, answered in ns)}


def due_changes(plan, entries):
    """Each change due for the user's review, in the plan's order: a unit of a bolt a team holds whose last delivered
    construct left a commit no batch has held it at, as (unit, team, commit, when it was constructed)."""
    latest = latest_changes(entries)
    held = {(u, sha) for _, _, us in batches(entries) for u, _, sha in us}
    out = []
    for u in plan.units():
        b = plan.bolt(u.get("Bolt")) if u.get("Bolt") else None
        if b and b.get("Team") and u.name() in latest and (u.name(), latest[u.name()][0]) not in held:
            out.append((u.name(), b.get("Team"), *latest[u.name()]))
    return out


def told_since_last_batch(entries):
    """Whether the planner was told a batch is due since the last batch was delivered (a `batch.due` entry after it)."""
    done = [e["At"] for e in entries if e.get("Act") == "review.batch"]
    last = max(done) if done else None
    return any(e.get("Act") == "batch.due" and (last is None or e["At"] > last) for e in entries)


def batch_due(due, entries, setting, now, bolts):
    """Why a batch of the due changes is due now (briefs.12): at the partition's setting, `every` changes due or `hours`
    since the last batch, or since the first due change was constructed when there has been none, or at once for a bolt
    with every unit merged whose units' latest changes are due. bolts are the team's held bolts as (name, every unit
    merged, its units due). [] when none is, or when the planner was told of a batch since the last one was delivered."""
    if not due or told_since_last_batch(entries):
        return []
    done = [e["At"] for e in entries if e.get("Act") == "review.batch"]
    last = max(done) if done else None
    clock = utc(last) if last else min(utc(at) for *_, at in due)
    why = []
    if len(due) >= setting["every"]:
        why.append(f"{len(due)} changes are due, and a batch is every {setting['every']}")
    if now - clock >= datetime.timedelta(hours=setting["hours"]):
        why.append(f"{setting['hours']} hours have passed since " + ("the last batch" if last else "the first of them was constructed"))
    for name, merged, waiting in bolts:
        if merged and waiting:
            why.append(f"bolt {name} has every unit merged, and lands only once {either(waiting)} "
                       + ("has" if len(waiting) == 1 else "have") + " been in a batch the user has answered")
    return why


def batch_reckoners(found, teams, here):
    """The teams the rail's sweep on this host (here) reckons a batch for (briefs.12): for each partition whose plan was
    read, each team on this host holding a bolt of it, in the plan's order, as {label: [team]}; a partition is reckoned
    by its first team until one tells its planner (reckon_batches). A batch due by the partition's clock, or at once for
    a bolt whose units have all merged, so reaches the planner when no conductor waits on anything (2026-10-19: two
    bolts merged two hours with no batch begun)."""
    out = {}
    for label, _, _, pl in found:
        if not pl:
            continue
        names = [b.get("Team") for b in pl.bolts() if b.get("Team")]
        held = [n for n in dict.fromkeys(names) if (teams.get(n) or {}).get("machine") == here]
        if held:
            out[label] = held
    return out


def reckon_batches(fleet, found):
    """The rail's sweep reckons each partition's batch on this host (batch_reckoners, batch_check), stopping at the first
    of its teams that tells the planner, since a batch is told once; what crew can't read is said on standard error and
    the rail read stands."""
    for label, names in batch_reckoners(found, fleet["teams"], crew.this_host()).items():
        for name in names:
            try:
                if batch_check(fleet, fleet["teams"][name]):
                    break
            except Refusal as e:
                print(f"no batch reckoned for {name}: {e}", file=sys.stderr)
                break


def batch_check(fleet, t):
    """On each wait of a conductor of the partition, at the end of a construct or a merge it waited on
    (after_delivery), and on the rail's sweep (reckon_batches): the changes due across the partition, counted from the run
    record, make a batch due at the partition's setting, `every` of them or `hours` since its last batch with at least
    one due, or at once when the team's bolt has every unit merged and some unit's latest change has been in no batch.
    crew then tells the partition's planner once, `batch.due` in the run record, until the next batch is delivered
    (briefs.12). What crew can't read is said on standard error, and the wait goes on. Returns whether it told the planner."""
    label = t["label"]
    setting = fleet["partitions"][label]["review"]
    plan = plan_of(fleet, label)
    if plan is None:
        return
    entries = partition_entries(fleet, label)
    due = due_changes(plan, entries)
    if not due or told_since_last_batch(entries):
        return
    held = held_by(plan, t["name"])
    st = stages_for(fleet, plan, held) if held else None
    bolts = [(b.name(), bool(plan.work_of(b.name())) and all(st.of(u.name())["stage"] in ("merged", "landed") for u in plan.work_of(b.name())),
              [u for u, *_ in due if plan.unit(u).get("Bolt") == b.name()]) for b in held]
    why = batch_due(due, entries, setting, datetime.datetime.now(datetime.timezone.utc), bolts)
    if not why:
        return
    planner = f"{label}-planner"
    text = batch_due_said(label, due, why)
    if crew.tell(fleet, planner, text):
        record.emit(label, "batch.due", [f"agent/{planner}"] + [f"unit/{u}" for u, *_ in due], why=f"batch: due, {len(due)} changes",
                    Count=len(due))
        return True
    return False


def batch_due_said(label, due, why):
    """What the planner is told when a batch is due (briefs.12): the changes due, by unit and team, why, and how to start
    and wait for its reviewer, whose summary raises the batch's card."""
    return (f"A batch of {label}'s changes is due: " + ", ".join(f"{u} ({team})" for u, team, *_ in due) + "; " + "; ".join(why)
            + f". Start its reviewer with crew review {label}, and wait for the summary with crew review {label} --wait, which "
            "raises the batch's card and its reading session in your name.")


def reading_command(fleet, label, team, sha, unit):
    """How the reviewer, on the main level's host, reads a unit's change at a commit in its kit on the team's host, the
    kit of the unit's bolt (unit_kit_team)."""
    t, here = unit_kit_team(fleet, label, fleet["teams"][team], unit), fleet["partitions"][label]["machine"]
    pre = "" if t["machine"] == here else f"ssh -o BatchMode=yes {t['ssh']} "
    return (f"list its files with `{pre}git -C {t['kit']['main']} ls-tree -r --name-only {sha} openspec/changes/{unit}/` and read "
            f"each with `{pre}git -C {t['kit']['main']} show {sha}:<path>`")


def review_start(fleet, a):
    """The batch the partition's reviewer is started for: its number (N), the file it writes (FILE), its units as
    <unit>:<team>@<commit> (UNITS) and by name (NAMES), and its prompt (PROMPT), naming each change, its team, its kit
    and host, and how to read it at its commit. Refused when no change is due."""
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
    prompt = review_prompt(fleet, label, n, f, due)
    return dict(N=n, FILE=f, UNITS=" ".join(f"{u}:{team}@{sha}" for u, team, sha, _ in due), NAMES=" ".join(u for u, *_ in due),
                PROMPT=prompt)


def review_prompt(fleet, label, n, f, due):
    """What batch n's reviewer is sent: the changes due, each with its team, kit, host and commit and how to read it
    there, and the file its summary goes to."""
    return (f"Review batch {n} of {label}, {len(due)} change{'' if len(due) == 1 else 's'}, and write its summary to {f}. "
            + " ".join(f"{u} ({team}, {unit_kit_team(fleet, label, fleet['teams'][team], u)['kit']['name']} on {fleet['teams'][team]['machine']}, at {sha}): "
                       f"{reading_command(fleet, label, team, sha, u)}." for u, team, sha, _ in due))


def review_wait(fleet, a):
    """Wait, on the main level's host, for the summary of the batch the reviewer was last started for, written since it
    started: once it is, the batch is recorded (`review.batch`, its number and each unit at the commit its change was
    read at), its card raised with its reading session in the planner's name (raise_batch), and the file's path
    returned. A batch already recorded is returned at once, its card raised if the planner holds none on this host,
    so a batch's card is never changed in place. Stopped with exit 3 when the
    timeout passes first, refused when the reviewer is gone with no summary written."""
    label = crew.partition_of(fleet, a.label)["label"]
    CONTEXT["label"] = label
    entries = local_entries(label, BATCH_DAYS)
    starts = [e for e in entries if e.get("Act") == "review.start" and not e.get("Refused") and (e.get("Batch") or "").isdigit()]
    starts or fail(f"no batch of {label} has been started: crew review {label} starts one")
    s = starts[-1]
    n, f = int(s["Batch"]), batch_file(label, s["Batch"])
    if any(e.get("Act") == "review.batch" and e.get("Batch") == s["Batch"] for e in entries):
        if not cards.card_under(cards.host_entries(record, label, crew.this_host()), f"batch/{n}", f"{label}-planner"):
            raise_batch(fleet, {"label": label, "key": f"batch/{n}"})
        return f
    begun, deadline = utc(s["At"]), time.monotonic() + a.timeout / 1000
    while True:
        try:
            written = f.stat().st_mtime >= begun.timestamp()
        except OSError:
            written = False
        if written:
            record.emit(label, "review.batch", [f"batch/{n}"] + [f"unit/{u}" for u, *_ in units_of_batch(s)],
                        why=f"batch({n}): reviewed", Batch=n, Units=s.get("Units"))
            raise_batch(fleet, {"label": label, "key": f"batch/{n}"})
            return f
        if crew.agent_status(fleet, f"{label}-reviewer") is None:
            fail(f"{label}-reviewer is no longer running, and batch {n}'s summary {f} was not written")
        if time.monotonic() >= deadline:
            print(f"batch {n}'s review is still running after the wait's {a.timeout} ms: nothing is recorded yet", file=sys.stderr)
            raise Stopped(3)
        time.sleep(POLL)


# A heading in a batch's summary: a Markdown heading, or a line that opens in bold and says little after it.
HEADING = re.compile(r"^\s*(?:#{1,6}\s+(.+?)[\s#]*|\*\*([^*]+)\*\*(.{0,60}))$")


def summary_paragraph(summary, unit):
    """The paragraph the reviewer opened a unit's section of a batch's summary with, as its brief has it write one
    section per unit headed by the unit's name and its team: the first paragraph under the first heading that names the
    unit, a Markdown heading or a short line in bold; None when no heading names it, or a heading follows it at once."""
    named = re.compile(rf"(?<![a-z0-9-]){re.escape(unit)}(?![a-z0-9-])")
    out, found = [], False
    for line in summary.splitlines():
        head = HEADING.match(line)
        if not found:
            found = bool(head and named.search("".join(g or "" for g in head.groups())))
        elif head:
            break
        elif line.strip():
            out.append(line.strip())
        elif out:
            break
    return "\n".join(out) or None


def subject(goal):
    """A bolt's goal as a batch card's title names what a unit is about: its own words, with no closing stop, the first
    letter small but for a word in capitals."""
    s = (goal or "").strip().rstrip(".")
    return s[0].lower() + s[1:] if len(s) > 1 and not s[1].isupper() else s


def batch_subjects(plan):
    """What each unit of the plan is about, as a batch card's title says it: its bolt's goal (subject), by unit. Empty
    when the plan could not be read, and a unit no bolt holds left out: its card names it by its name instead."""
    out = {}
    for u in plan.units() if plan else []:
        b = plan.bolt(u.get("Bolt")) if u.get("Bolt") else None
        if b and b.get("Goal"):
            out[u.name()] = subject(b.get("Goal"))
    return out


def batch_facts(n, entries, summary, subjects):
    """Batch n's card's facts, as cards.batch_card takes them (record 0031 §5), from the run record's entries on the main
    level's host, oldest first, and the reviewer's summary: n, the batch before it, and each unit in the batch's order
    with its team, the commit the batch read it at, what it is about (subjects, else its name in words) and the
    paragraph the reviewer opened its section with, or a line saying the summary has none. None while the batch's point
    has not come or has passed: the run record holds no batch n, its summary is not there (None), its key is closed
    (batch_closed), the last card act under it a close, but as lost to its owner, or the batch waits on nothing
    (batch_settled), so crew review --wait raises no card for it. A card of it the owner holds open is no reason: the
    act changes it, or posts it again once lost."""
    key = f"batch/{n}"
    held = [e for e in entries if e.get("Act") == "review.batch" and not e.get("Refused") and e.get("Batch") == str(n)]
    if not held or summary is None:
        return None
    if key in batch_closed(entries) or key in batch_settled(entries):
        return None
    previous = max((m for m, _, _ in batches(entries) if m < n), default=None)
    units = [dict(unit=u, team=team, commit=sha, subject=subjects.get(u) or u.replace("-", " "),
                  paragraph=summary_paragraph(summary, u) or f"The reviewer's summary has no section for {u}.")
             for u, team, sha in units_of_batch(held[-1])]
    return dict(n=n, previous=previous, units=units, link=None)


def batch_read(fleet, label, n, acts):
    """Batch n's card's facts as its raise reads them, on the main level's host: from this host's run record, the
    reviewer's summary and the plan's goals (batch_facts); None while its point has not come or has passed. A summary
    crew can't read is refused, naming it."""
    f = batch_file(label, n)
    try:
        summary = f.read_text()
    except FileNotFoundError:
        summary = None
    except OSError as e:
        fail(f"crew can't read batch {n}'s summary {f}: {e.strerror or e}")
    return batch_facts(n, acts.entries(label), summary, batch_subjects(plan_of(fleet, label)))


def raise_batch(fleet, row, acts=None, note=None):
    """A batch's raise (record 0031 §1, briefs.12), for its rail row, of which it reads the label and the key: once the
    reviewer's summary is there, its one card, asked in the planner's name, filed in the kit of its first unit's team,
    its reading session started by the act, and posted through row_card_change, so a card the planner holds that
    Pending You no longer finds is recorded lost and posted again saying its older copy is dead, and one it holds is
    changed with note, by default that crew could not find its earlier copy, RELINKED when its reading opened after it
    was raised (reading_again); nothing while batch_facts finds its point not come or passed, and nothing for a key not
    batch/<n>, an old batch card's among them. crew review --wait calls it once the batch is recorded, and the rail's
    sweep for a row whose card is missing or lost, and for one whose card this host can't reach, handed that older copy
    as the row's dead, when the card is posted saying first that an older copy was lost and to dismiss it in the app
    (cards.posted_again). Run on the main level's host, where the batch and its card are recorded and its summary
    written. What crew can't read is said and refuses nothing, since the batch stands. The card's id, or None."""
    m = re.fullmatch(r"batch/(\d+)", row["key"] or "")
    if not m:
        return None
    acts, label, n = acts or CardActs(fleet), row["label"], int(m.group(1))
    owner = f"{label}-planner"
    try:
        facts = batch_read(fleet, label, n, acts)
    except Refusal as e:
        print(f"batch {n}'s card is not raised: {e}", file=sys.stderr)
        return None
    if not facts:
        return None
    t = next((fleet["teams"][u["team"]] for u in facts["units"] if u["team"] in fleet["teams"]), None)
    if not t:
        print(f"batch {n}'s card is not raised: none of its units' teams is in the teams file, so it has no kit to be filed in",
              file=sys.stderr)
        return None
    build = built_again(cards.batch_card) if row.get("dead") else cards.batch_card
    return row_card_change(fleet, label, owner, build, facts, note or "Raised again: crew could not find its earlier copy",
                           card_where(t["kit"]), acts)


def built_saying(build, said):
    """A builder whose kit's landings card says first, ahead of its summary, what changed of each bolt it asks for
    again since the user's send that ticked it (said, work_said's words), so the card that asks again says so
    (rail-cards "A ticked bolt whose own work changed is asked again, saying what changed"); build itself with none."""
    if not said:
        return build

    def saying(facts):
        b = build(facts)
        return dict(b, card=dict(b["card"], summary=cards.prose(" ".join(f"{w}." for w in said) + f"\n\n{b['card']['summary']}")))
    return saying


def built_again(build):
    """A builder whose card, posted again under its key once an older copy was lost to its owner, says so first
    (built_copy)."""
    return lambda facts: built_copy(build(facts))


def built_copy(b):
    """A built card posted again under its key once an older copy was lost to its owner: its summary saying so first
    (cards.posted_again), and marked again, since it is the row's card the user can no longer reach and never a
    follow-on with nothing changed, so its post is never withheld (card_posted, row_card_change)."""
    return dict(b, card=cards.posted_again(b["card"]), again=True)


# ------------------------------------------------------------------------------------------------ crew rail

RAIL = ("proposals", "batches", "land", "operations")


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
    card.post of the last 14 days with a Card that no later card.close of that Card closes, and that no later card.post
    by the same agent under the same Key names another Card for: within one Pending You sign-in a key gives its card
    back, so a second card under it from its owner means the first was lost to it, and the newer is the row's; the
    branch whose record could not be read, {label: {<label>/main: why}}, no host being asked for it (read.5); the landings, each {label, bolt, units, at, by, host}, from each
    bolt.land entry not refused, oldest first; the team each bolt was given to, {(label, bolt): team}, from the newest
    bolt.give entry naming it that was not refused; what the batches hold, {label: {"batches": [(n, at, units)],
    "closed": card keys closed, "posts": batch card keys posted, "due": units whose latest change no batch has held,
    "unanswered": {unit: the batch} whose card the user has not answered that holds its latest change}}, the last two
    None for a partition whose branch could not be read, since then they can't be told; the rail's rows for the
    operations; the entries the operations are read from, {label: entries}, the ops entries of the main level's host
    and the landings, oldest first, which the board's Operation lane reads (ops.environments); and every entry read,
    {label: entries}, oldest first, which the sweep (sweep_cards) and the board's design band read."""
    times, cards, unread, landings, gives, held, deploys, opses, logs = {}, [], {}, [], {}, {}, [], {}, {}
    today = datetime.datetime.now(datetime.timezone.utc).date()
    fresh = utc(f"{today - datetime.timedelta(days=CARD_DAYS)}T00:00:00Z")
    for l, _, _, plan in [f for f in found if f[3]]:
        since = today - datetime.timedelta(days=BATCH_DAYS)
        opened = [d["opened"] for d in props if d["label"] == l]
        if opened:
            since = min(since, datetime.date.fromisoformat(min(opened)) - datetime.timedelta(days=1))
        entries, missing = record.gather(fleet, [l], since.isoformat())
        unread[l], logs[l] = missing, entries
        r = record_reading(l, entries, plan, fresh, missing)
        times.update(r["times"])
        cards += r["cards"]
        landings += r["landings"]
        gives.update(r["gives"])
        held[l] = r["held"]
        import ops  # ops.py imports nothing of this module
        mine = [e for e in entries if (e.get("Act") or "").startswith("ops.") and e.get("Host") == fleet["partitions"][l]["machine"]]
        deploys += [dict(r, at=utc(r["at"]), doc=None) for r in ops.rows(fleet, l, mine)]
        opses[l] = sorted(mine + [e for e in entries if e.get("Act") == "bolt.land"], key=lambda e: (e["At"], e["Id"]))
    return times, cards, unread, landings, gives, held, deploys, opses, logs


def record_reading(l, entries, plan, fresh, missing=None):
    """What the rail reads of one partition's run record entries, as rail_record gives it: when each proposal was
    proposed, the cards open (posted since fresh and not closed, the same owner's newer card under a key replacing its
    older, lost to it), the landings, the team each bolt was last given to, and what the batches hold, the due units
    None while its branch could not be read (missing), as are the units whose latest change waits on the user's
    answer to its batch's card (awaiting_answer). A close refused leaves its card open; a card's close as lost to its
    owner ends that card but not its row, whose card is posted again under its key; and a batch's key is closed while
    its last card act is a close (batch_closed), so a batch card posted again after a close keeps its row, or once its
    batch waits on nothing (batch_settled), whose words are held as settled."""
    times, posted, closed, landings, gives = {}, {}, set(), [], {}
    for e in entries:
        act = e.get("Act")
        if act == "plan.propose" and not e.get("Refused"):
            for o in e["On"]:
                if o.startswith("proposal/"):
                    times.setdefault((l, o), utc(e["At"]))
        elif act == "card.post" and e.get("Card") and not e.get("Refused") and utc(e["At"]) >= fresh:
            if e.get("Key"):  # the same owner's card under the same key, but another, is the older copy, lost to it
                for c in [c for c, d in posted.items() if (d["key"], d["by"]) == (e["Key"], e.get("By")) and c != e["Card"]]:
                    del posted[c]
            posted.setdefault(e["Card"], dict(label=l, card=e["Card"], key=e.get("Key"), on=(e["On"] or [None])[0],
                                              by=e.get("By"), host=e.get("Host"), at=utc(e["At"])))
        elif act == "card.close" and e.get("Card") and not e.get("Refused"):  # a refused close leaves the card open
            posted.pop(e["Card"], None)
            if e.get("Key") and e.get("State") != "lost":  # a lost card's row still waits, for its card posted again
                closed.add(e["Key"])
        elif act == "bolt.land" and not e.get("Refused"):
            bolt = next((o[5:] for o in e["On"] if o.startswith("bolt/")), None)
            if bolt:
                landings.append(dict(label=l, bolt=bolt, units=[o.split("/", 1)[1] for o in e["On"] if o.startswith(("unit/", "chore/"))], at=utc(e["At"]),
                                     by=e.get("By"), host=e.get("Host")))
        elif act == "bolt.give" and not e.get("Refused"):
            bolt = next((o[5:] for o in e["On"] if o.startswith("bolt/")), None)
            team = next((o[5:] for o in e["On"] if o.startswith("team/")), None)
            if bolt and team:
                gives[(l, bolt)] = team
    settled = batch_settled(entries)
    closed = {k for k in closed if not k.startswith("batch/")} | batch_closed(entries) | set(settled)  # a batch card posted again reopens its row
    held = dict(batches=batches(entries), closed=closed, settled=settled, posts=batch_posts(entries),
                due=None if missing else {u for u, *_ in due_changes(plan, entries)},
                unanswered=None if missing else awaiting_answer(entries), refused=refusals(entries), stopped=stops(entries),
                forecasts=[e for e in entries if e.get("Act") == "forecast"])
    return dict(times=times, cards=list(posted.values()), landings=landings, gives=gives, held=held)


def rail_rows(fleet, found, sv, props, times, held=None):
    """What waits on the user in the plans read, from the open proposals and when each was proposed, the batches the run
    record holds (held, as rail_record reads it), and the kits as surveyed: each row's group, its partition, its card
    key, the time it began to wait (shown as a date alone when that is all that is known), what it is, its commands, and
    the document its card asks the user to read: ("page", label, n) for a proposal, ("batch", label, n) for a batch
    card, whose units, their teams and the commits the batch read them at the row holds too, None for a landing. A
    proposal's row is keyed by its chain's card, proposal/<first>, the first proposal it was rewritten from. A
    verify report is no row: its findings are fixed in one round with no card (teams.17). A batch is one row, keyed
    batch/<n>, holding every unit, until its card closes or it waits on nothing (batch_settled); a batch posted as cards
    of five before a batch was one card is a row for each card posted, keyed batch/<n>-<k>, until it closes or the units
    it holds wait on nothing. Each kit with a bolt a team holds whose every unit has merged is one landing row, keyed
    land/<kit>, main-level ops's (record 0031 as amended 2026-10-23), naming each such bolt in the plan's order with its
    team, what a yes frees of it and what it waits on (bolts, each {bolt, team, host, can}): a bolt can land only once
    its verification is green, sluice's verdict on its last landing (kit.verification, record 0025), every unit's latest
    change has been in a batch whose card the user has answered, no fix is in flight on it, sluice did not refuse its
    landing at its head (refusals, held's refused) and the run record holds no conflict with main forecast at its head
    (main_conflict, held's forecasts); until then its line says which units no batch has held, which batches wait on the
    user's answer, the fix, sluice's words, or that it takes main first (briefs.12). The row's answer tells ops to land
    those that can, in order, and offers nothing while none can."""
    rows, here, held = [], crew.this_host(), held or {}
    for d in props:
        l, n = d["label"], d["proposal"]
        what = [f"proposal {n} ({l}), by {d['by']}: {d['case'].splitlines()[0][:70]}"]
        if d["waiting"]:
            what.append("still needs the agreement of " + ", ".join(f"{t}-conductor" for t in d["waiting"]))
        at = times.get((l, f"proposal/{n}"))
        rows.append(dict(group="proposals", label=l, key=f"proposal/{d.get('first') or n}", at=at or utc(f"{d['opened']}T00:00:00Z"),
                         date=None if at else d["opened"], what=what, doc=("page", l, n),
                         cmds=[("read", f"crew plan proposed {n} --label {l}"), ("open", f"crew plan proposed {n} --label {l} --open"),
                               ("answer", f"crew plan approve {n} --label {l}")]))
    for l, h in held.items():
        main = fleet["partitions"][l]["machine"]
        for n, at, units in h["batches"]:
            for key, part in batch_cards(n, units, h.get("posts", set())):
                if key in h["closed"]:
                    continue
                home = fleet["hosts"].get(main, {}).get("home")
                f = str(batch_file(l, n)) if main == here else f"{home}/.local/state/crew/{l}-main/reports/batch-{l}-{n}.md" if home else None
                k = key.partition("-")[2]
                card = f", card {k} of {-(-len(units) // 5)}" if k else ""
                rows.append(dict(group="batches", label=l, key=key, at=utc(at), doc=("batch", l, n),
                                 units=[u for u, *_ in part], teams={u: team for u, team, _ in part},
                                 commits={u: sha for u, _, sha in part},
                                 what=[f"batch {n} ({l}){card}: " + ", ".join(f"{u} ({team})" for u, team, _ in part)],
                                 cmds=([("open", opener(fleet, main, here, f))] if f else [])
                                 + [("answer", f'crew tell {l}-planner "On batch {n}: "')]))
    for l, _, _, plan in found:
        if not plan:
            continue
        st, kits = Stages(fleet, plan, sv), {}
        for b in plan.bolts():
            if not b.get("Team"):
                continue
            k, _ = st.kit(b)
            if not k:
                continue
            team, host = k["team"]["name"], k["host"]
            units = plan.work_of(b.name())
            stages = [st.of(u.name())["stage"] for u in units]
            at, head = k["bolts"].get(b.name(), {}).get("head_at"), k["bolts"].get(b.name(), {}).get("head")
            if not (stages and at and head and all(x in ("merged", "landed") for x in stages) and not all(x == "landed" for x in stages)):
                continue
            due, waits = held.get(l, {}).get("due"), held.get(l, {}).get("unanswered") or {}
            outside = [u.name() for u in units if due is not None and u.name() in due]
            unread = sorted({waits[u.name()] for u in units if u.name() in waits})
            said = [x for x in [frees_said(team, frees_of(st, plan, k["team"], b.name()))] if x]
            state, verdict = kit.verification(head, k["bolts"].get(b.name(), {}).get("verdict"))
            if state != "green":  # a bolt's proof is its verification (record 0025, tests.5)
                lands = [f"lands once its verification is green; now {verdict}"]
            elif due is None and l in held:
                lands = [f"whether every unit's latest change has been in a batch can't be told: {l}/main could not be read"]
            else:  # in a batch whose card the user has answered (briefs.12)
                lands = ([f"lands once {either(outside)} " + ("has" if len(outside) == 1 else "have") + " been in a batch, which is due for them"]
                         if outside else []) + ([f"lands once you have answered batch{'' if len(unread) == 1 else 'es'} "
                                                 f"{joined([str(n) for n in unread])}"] if unread else [])
            fixes = fixes_in_flight(k.get("fixes", []), b.name())
            refused = held_at(held.get(l, {}).get("refused") or {}, b.name(), head)
            stop = stopped_at(held.get(l, {}).get("stopped") or {}, b.name(), head)
            conflict = main_conflict(held.get(l, {}).get("forecasts") or [], b.name(), head)
            if not lands and fixes:  # a fix started on the bolt holds its landing (landing_held)
                lands = [f"lands once {either(sorted(fixes))} has merged or been dropped"]
            elif not lands and refused:  # sluice refused its landing at this head (refused_at)
                lands = [f"held: sluice refused its landing at {head[:7]}, until its team's fix moves its head: {refused}"]
            elif not lands and conflict:  # forecast at this head to conflict with what main holds (main_conflict)
                lands = [f"takes main first: forecast to conflict with main on {joined(conflict[1])}, until its team's "
                         "take-main fix moves its head"]
            can = ["can land"] + ([f"its last landing at {head[:7]} was stopped, nothing of the bolt's: {stop.rstrip('.')}; "
                                   f"{l}-ops submits it again once that is cleared"] if stop else [])  # stopped_at, holding nothing
            kits.setdefault(b.get("Repo") or k["kit"]["name"], []).append(
                dict(bolt=b.name(), team=team, host=host, at=at, can=not lands, line=f"{b.name()}, {team} on {host}: "
                     + "; ".join(said + (lands or can))))
        for kit_name, bolts in kits.items():
            can = [x["bolt"] for x in bolts if x["can"]]
            what = [f"{kit_name} ({l}): {plural_of(len(bolts), 'bolt waits', 'bolts wait')} to land on its main, in the plan's order; "
                    f"{l}-ops lands them"] + [x["line"] for x in bolts]
            rows.append(dict(group="land", label=l, key=f"land/{kit_name}", at=min(utc(x["at"]) for x in bolts), doc=None, what=what,
                             cmds=[("answer", f'crew tell {l}-ops "Land {", ".join(can)}."')] if can else [],
                             bolts=[{k_: x[k_] for k_ in ("bolt", "team", "host", "can")} for x in bolts]))
    return rows


def plural_of(n, one, more):
    """n with the words for one or for more."""
    return f"{n} {one if n == 1 else more}"


def card_kind(key):
    """What an open card is, from its key: a row's ("row"), under a key crew raises a row's card under, as record
    0031 keys them or as they were keyed before it (crews_key); a decision record's ("record"), which is no row's; or
    an agent's question ("question"), under a key of its asker's own or none (briefs.11)."""
    kind = crews_key(key or "")
    return "record" if kind == "record" else "row" if kind else "question"


def unjudged(unread, c):
    """Whether it can't be told that an open card is still open: its partition's run record could not be read from its
    branch, so its close may not have been read (read.1). A host that does not answer hides no card's close, which is
    on the branch whatever host recorded it (read.5)."""
    return bool(unread.get(c["label"]))


def record_cards(cards, unread):
    """The open cards under a decision record's key, oldest first: no row's, so never among the cards with no row. A
    card is left out while its partition's record could not be read, as stray_cards leaves one out, since its close may
    not have been read."""
    return sorted((c for c in cards if card_kind(c["key"]) == "record" and not unjudged(unread, c)), key=lambda c: (c["at"], c["card"]))


def question_cards(cards, unread):
    """The open questions the four asking roles posted in their own name, oldest first (briefs.11), but one whose
    partition's record could not be read, as record_cards leaves one out."""
    return sorted((c for c in cards if card_kind(c["key"]) == "question" and not unjudged(unread, c)), key=lambda c: (c["at"], c["card"]))


def stray_cards(fleet, found, sv, rows, cards, unread, logs=None):
    """The open cards under a row's key that match no row, oldest first: never a decision record's (record_cards) nor
    a question (question_cards), nor a deploy's whose word stands, from each partition's entries (logs), which the
    deploy's end closes (ops.word_stands). A card is left out when whether it has a row can't be known: its partition's
    record could not be read from its branch, so its close may not have been read, or it is a land card of a bolt whose
    team's host did not answer. A verify report's card, posted before its row went (teams.17), matches none."""
    import ops  # its decision of a deploy's card alone
    plans_, rowed, out = {l: p for l, _, _, p in found if p}, {(r["label"], r["key"]) for r in rows}, []
    for c in cards:
        if (c["label"], c["key"]) in rowed or card_kind(c["key"]) != "row" or unjudged(unread, c):
            continue
        if ops.word_stands(c["key"], (logs or {}).get(c["label"], [])):
            continue
        if c["key"] and blind_land(fleet, plans_[c["label"]], sv, c["key"]):
            continue
        out.append(c)
    return sorted(out, key=lambda c: (c["at"], c["card"]))


def blind_land(fleet, plan, sv, key):
    """Whether a card's key is a landing's whose row can't be told, since the host of a team holding its bolt, or for a
    kit's landings card, land/<kit>, a bolt of the kit, did not answer."""
    m = re.match(r"land/([a-z0-9][a-z0-9-]*)", key)
    if not m:
        return False
    down = lambda b: (lambda t: bool(t) and t["machine"] in sv and not sv[t["machine"]]["ok"])(bolt_team(fleet, b))
    if plan.bolt(m.group(1)):
        return down(plan.bolt(m.group(1)))
    return any(down(b) for b in plan.bolts() if b.get("Repo") == m.group(1) and b.get("Team"))


# How long crew leaves a card, or a row's card, whose last post or close Pending You refused before the sweep tries it
# again, so a refusal that stands is not tried again at the rail tab's pace, every thirty seconds, each try an entry.
CARD_RETRY = 600


def row_gone(key, entries, kits=(), kit_of=None):
    """Why a row's card has no row now, from the run record's entries, oldest first: (outcome, None) when the event
    that ends its row was recorded, so its card is closed with what was done, a proposal applied, a bolt landed or a
    batch answered in a main-level pane, in whose and when (pane_answered); else (None, reason), its card withdrawn
    with why, a proposal or a bolt dropped among them, and a batch that waits on nothing with the words of crew's close
    (batch_settled). A kit's landings card, land/<kit> (kits, the partition's kits' names), that nothing waits to land
    on its main; and a landing card of a bolt's own, from before a kit's card, whose bolt its kit's landing row names
    (kit_of, {bolt: its kit}), that it is now a row of its kit's landings card (rail-cards "A bolt's own landing card
    gives way to its kit's")."""
    kind, _, rest = (key or "").partition("/")
    thing, _, head = rest.partition("/")
    if kind == "land" and not head and thing in kits:
        return None, f"nothing waits to land on {thing}'s main"

    def last(on, *acts):
        return next((e["Act"] for e in reversed(entries) if e.get("Act") in acts and not e.get("Refused") and on in (e.get("On") or [])), None)
    if kind == "proposal":
        act = last(f"proposal/{thing}", "plan.approve", "plan.drop")
        return (("its proposal was applied", None) if act == "plan.approve" else
                (None, "its proposal was dropped" if act == "plan.drop" else "its proposal is closed"))
    if kind == "land":
        act = last(f"bolt/{thing}", "bolt.land", "bolt.drop")
        return (("its bolt landed", None) if act == "bolt.land" else
                (None, "its bolt was dropped" if act == "bolt.drop" else
                 f"{thing} is now a row of {(kit_of or {})[thing]}'s landings card" if (kit_of or {}).get(thing) else
                 "its bolt no longer waits to land" + (f" at {head}" if head else "")))
    answered = pane_answered(entries) if kind == "batch" else {}
    if key in answered:
        said = pane_said(*answered[key])
        return said[0].upper() + said[1:], None
    settled = batch_settled(entries) if kind == "batch" else {}
    if key in settled:
        return None, settled[key]
    return None, {"batch": "its batch no longer waits to be read", "deploy": "its deploy no longer waits on your word",
                  "op": "its step no longer waits on you",
                  "verify": "a verify report has no card, its findings fixed in one round"}.get(kind, "its row is gone")


def record_settled(key, entries, kits=()):
    """The outcome a decision record's card closes with, under its key in either form (cards.row_object, kits as it
    takes them), from the run
    record's entries, oldest first: the record's last status crew record recorded, "Accepted at <commit>" or "Rejected
    at <commit>" as crew record closes it, the commit left out when the entry names none; None while it is proposed,
    or none is recorded."""
    obj = cards.row_object(key or "", kits)
    last = next((e for e in reversed(entries) if obj and e.get("Act") in ("record.proposed", "record.accepted", "record.rejected")
                 and not e.get("Refused") and obj in (e.get("On") or [])), None)
    if not last or last["Act"] == "record.proposed":
        return None
    commit = next((c.rsplit("@", 1)[-1][:7] for c in last.get("Commit") or [] if "@" in c), None)
    return last["Act"].split(".")[1].capitalize() + (f" at {commit}" if commit else "")


def record_proposed(key, entries):
    """A decision record's last record.proposed entry, done, under its key in either form (cards.row_object), from the
    run record's entries, oldest first: its State says whether the user settled it in the pane, its Form whether its
    card offered alternatives; None when crew record recorded it proposed nowhere."""
    obj = cards.row_object(key or "")
    return next((e for e in reversed(entries) if obj and e.get("Act") == "record.proposed" and not e.get("Refused")
                 and obj in (e.get("On") or [])), None)


def refused_lately(entries, now, key=None, card=None):
    """Whether crew's last post under a row's key, or its last close of a card, was refused under CARD_RETRY seconds
    before now, so the sweep leaves it for a later read."""
    last = None
    for e in entries:
        if (card and e.get("Act") == "card.close" and e.get("Card") == card) or (key and e.get("Act") == "card.post" and e.get("Key") == key):
            last = e
    return bool(last and last.get("Refused") and (now - utc(last["At"])).total_seconds() < CARD_RETRY)


def reading_unread(entries, key, card, now=None):
    """Whether a batch's, a long proposal's or a landing's card stands without its reading, from this host's run
    record, oldest first (card-sessions "The rail's read tries a reading its card stands without"): a done post or
    change of the card with Unread, or a refused try of the key's reading (card.reading), marks it so from that entry's
    time; a done post or change of the card without Unread clears it; a refused post or change, and a done try, change
    nothing. With now, whether it stands so and its last such entry is CARD_RETRY seconds old or more, so the rail's
    sweep tries it again no sooner than it posts a refused card again."""
    last = None
    for e in entries:
        if e.get("Act") in ("card.post", "card.update") and card and e.get("Card") == card and not e.get("Refused"):
            last = e if e.get("Unread") else None
        elif e.get("Act") == "card.reading" and e.get("Key") == key and e.get("Refused"):
            last = e
    if not last or now is None:
        return bool(last)
    return (now - utc(last["At"])).total_seconds() >= CARD_RETRY


def stood(entries, key, owner):
    """Whether the owner's newest post under a row's key was a follow-on crew withheld, nothing having changed since the
    user answered the card before it (rail-cards "A follow-on with nothing changed is not posted"), from the run
    record's entries, oldest first: the rail's sweep raises no card for that row, and records nothing more."""
    last = None
    for e in entries:
        if e.get("Act") == "card.post" and e.get("Key") == key and e.get("By") == owner:
            last = e
    return bool(last and last.get("State") == cards.STANDS)


def last_refusal(entries, key):
    """The words of the last post under a row's key when it was refused, as the row's card line gives them; None when
    it was not, or there was none."""
    said = None
    for e in entries:
        if e.get("Act") == "card.post" and e.get("Key") == key:
            said = e.get("Refused") or None
    return said


def row_owner(fleet, plan, row):
    """Whose a rail row's card is and the host it runs on, where its card is posted under that host's sign-in: the
    planner's a proposal's and a batch's, and main-level ops's an operation's and a kit's landings card's, land/<kit>,
    on the partition's main machine (rail-cards, record 0031 as amended 2026-10-23)."""
    l = row["label"]
    return f"{l}-{'planner' if row['group'] in ('proposals', 'batches') else 'ops'}", fleet["partitions"][l]["machine"]


def older_than_card(key, proposed):
    """Whether the plan the rail read is older than a proposal's card under key (record 0031 §1, briefs.11): it holds
    no proposal by the number the key names, proposed being the numbers its proposals.rec holds, open or closed, or
    None when they were not read. A proposal is numbered once and never removed (plan.4), and its card is raised at the
    commit that proposed it or past it, so a read that holds the proposal is at or past that commit, and one that does
    not is older than the card: a fresh proposal's row missing from it says nothing of whether the proposal stands.
    False for a key that is no proposal's."""
    m = re.fullmatch(r"proposal/(\d+)", key or "")
    return bool(m) and (proposed is None or int(m.group(1)) not in proposed)


def proposals_held(found):
    """The numbers of the proposals each plan read holds, open or closed, {label: {n}}, from proposals.rec at the tip
    it was read at (found, as plans() gives it), an empty set where the branch holds none; a label whose plan was not
    read is left out, so its proposals' cards are judged against no read (older_than_card)."""
    return {l: {int(p.get("Proposal")) for p in Plan(show(repo, tip, "proposals.rec") or "").recs("Proposal")}
            for l, repo, tip, pl in found if pl}


def sweep_judged(here, rows, cards_, entries, owners, blind, proposed, now, planner=(None, None), design=(None, None), kits=(),
                 kit_of=None):
    """What the rail's read does with one partition's cards, of those posted on this host (here), the only ones its
    sign-in reaches: each row's card whose row is gone, to close with why (row_gone), but a land card whose row can't
    be told (blind, the bolts whose team's host did not answer) and a proposal's card on a plan read older than it
    (older_than_card, proposed the numbers of the proposals the read holds), which is left for a later read, its
    proposal maybe still open; each question, whose asker herdr is asked for; and
    each row's card with its row, which Pending You is asked whether it still finds; a deploy's card whose word stands
    left for the deploy's end to close (ops.word_stands); and each decision record's card, under either key form,
    whose record crew record has recorded accepted or rejected since, to close with its status (record_settled). Then
    each row in record 0031's
    form with no card open on any host, whose owner runs here (owners, {row key: (owner, host)}), to post through its
    kind's raise; but each row whose owner runs here and whose owner's newest card under its key this host's sign-in
    can't reach, one posted from another host and not closed, or one lost to its owner on any host (cards.stranded,
    over the whole record read), to post again through its kind's raise, the older copy named, and not as a row with no
    card; nor a row whose owner's newest post under its key was a follow-on crew withheld, its earlier card's answer
    standing (stood), until an event raises it with something changed. And, where the partition's design agent runs
    (design, its <label>-design and host), each decision record's
    key in record 0031's form under which the design agent posted a card, whose record crew record last recorded
    proposed (record_proposed) and not settled in the pane, and whose card this host's sign-in can't reach so, to post
    again through the record's raise as a row of the group records, with whether its card offered alternatives (the
    Form its last record.proposed records). A card or a row whose last close or post was refused under CARD_RETRY
    seconds ago is left for a later read. And, where the partition's batches' owner runs (planner, (owner, host), row_owner's for a
    batch), each batch card key whose batch waits on nothing (batch_settled), to record crew's close of, with why,
    once: none is under its key yet, and the user's answer has not closed it (batch_closed). And each row's card of a
    batch, batch/<n>, a proposal, proposal/<n>, or a kit's landings, land/<kit>, that the run record shows standing
    without its reading, or a row's of it, last posted, changed or tried CARD_RETRY seconds ago or more
    (reading_unread), to try its reading again. Returns {gone: [(card, outcome, reason)], questions: [card], held: [(card, row)], none: [row], again: [(row,
    older card)], settled: [(key, why)], unread: [(card, row)]}."""
    import ops  # its decision of a deploy's card alone
    rowed = {r["key"]: r for r in rows}
    out = {"gone": [], "questions": [], "held": [], "none": [], "again": [], "settled": [], "unread": []}
    for c in cards_:
        kind = card_kind(c["key"])
        if c["host"] != here:
            continue
        if kind == "record":
            settled = record_settled(c["key"], entries)
            if settled and not refused_lately(entries, now, card=c["card"]):
                out["gone"].append((c, settled, None))
        elif kind == "question":
            out["questions"].append(c)
        elif c["key"] in rowed:
            out["held"].append((c, rowed[c["key"]]))
            if re.fullmatch(r"(batch|proposal)/\d+|land/[a-z0-9][a-z0-9-]*", c["key"]) and reading_unread(entries, c["key"], c["card"], now):
                out["unread"].append((c, rowed[c["key"]]))
        elif (not (c["key"].startswith("land/") and c["key"].split("/")[1] in blind) and not refused_lately(entries, now, card=c["card"])
              and not ops.word_stands(c["key"], entries) and not older_than_card(c["key"], proposed)):
            out["gone"].append((c, *row_gone(c["key"], entries, kits, kit_of)))
    carded = {c["key"] for c in cards_}
    mine = [r for r in rows if cards.row_object(r["key"]) and (owners.get(r["key"]) or (None, None))[1] == here
            and not refused_lately(entries, now, key=r["key"])]
    for r in mine:
        older = cards.stranded(entries, r["key"], owners[r["key"]][0], here)
        if older:
            out["again"].append((r, older))
    again = {r["key"] for r, _ in out["again"]}
    out["none"] = [r for r in mine if r["key"] not in carded | again and not stood(entries, r["key"], owners[r["key"]][0])]
    if design[1] == here:
        posted = (e.get("Key") for e in entries if e.get("Act") == "card.post" and e.get("By") == design[0])
        for key in dict.fromkeys(k for k in posted if re.fullmatch(r"record/[a-z0-9][a-z0-9-]*/\d{4}", k or "")):
            last = record_proposed(key, entries)
            if (not last or record_settled(key, entries) or last.get("State") == "settled in the pane"
                    or refused_lately(entries, now, key=key)):
                continue
            older = cards.stranded(entries, key, design[0], here)
            if older:
                out["again"].append((dict(label=design[0].removesuffix("-design"), key=key, group="records",
                                          alternatives=last.get("Form") == "alternatives"), older))
    if planner[1] == here:
        done = {e.get("Key") for e in entries if e.get("Act") == "batch.close" and not e.get("Refused")} | batch_closed(entries)
        out["settled"] = [(k, why) for k, why in batch_settled(entries).items() if k not in done]
    return out


def stranded_said(entries, card, owner, new):
    """What the sweep says of a row's card this host could not reach once its raise posted it again as new
    (cards.stranded), from the run record's entries, oldest first: lost to its owner when its last close says so, else
    held on the host its post names, which this host's sign-in does not reach."""
    state, host = None, None
    for e in entries:
        if e.get("Card") != card or e.get("Refused"):
            continue
        if e.get("Act") == "card.post":
            host = e.get("Host")
        elif e.get("Act") == "card.close":
            state = e.get("State")
    return (f"lost to {owner}" if state == "lost" else f"held on {host}, which this host's sign-in does not reach") + f": posted again as {new}"


def sweep_sessions(fleet, found, sv, rows, cards, unread, batched):
    """End the card sessions crew started, and release the landings' previews it asked for, whose card is closed or
    whose row is gone, on every host of each partition
    whose plan was read, its main machine and each team's: one crew card sweep --label <label> on each (code.3), handed
    as live every row key less each the record holds as closed with no card open under it (batched, what the batches
    hold as rail_record reads it, {label: {batches, closed, due}}), and as blind the key prefixes it can't judge, batch/
    while the record could not be read from its branch, when no key is taken out for being closed either (read.1). A host the survey
    found not answering is not asked again. Returns what the sweeps did, each {label, host, key, unit, why, said}, why
    "its row is gone" or "its card is closed", and the hosts not checked, each {label, host, why} (read.3)."""
    ended, unchecked = [], []
    for l, _, _, plan in found:
        if not plan:
            continue
        readings = {f"land/{b['bolt']}" for r in rows if r["label"] == l and r["group"] == "land" for b in r.get("bolts", []) if b["can"]}
        rowed = {r["key"] for r in rows if r["label"] == l} | readings  # each row's, and each landing row's reading and preview
        judged = json.dumps(sweep_judgment(l, rowed, cards, unread.get(l), batched.get(l, {}), readings))
        for h in sorted({crew.partition_of(fleet, l)["machine"], *crew.partition_hosts(fleet, l)}):
            if h in sv and not sv[h]["ok"]:
                unchecked.append(dict(label=l, host=h, why=f"did not answer ({sv[h]['error']})"))
                continue
            try:
                r = crew.on_machine(fleet, h, crew.crew_argv(fleet, h, "card", "sweep", "--label", l), input=judged)
            except Refusal as e:
                unchecked.append(dict(label=l, host=h, why=str(e)))
                continue
            if r.returncode:
                said = ((r.stderr or "").strip().splitlines() or [f"exit {r.returncode}"])[-1]
                unchecked.append(dict(label=l, host=h, why=f"did not answer ({said})" if r.returncode == 255 else f"its sweep failed ({said})"))
                continue
            try:
                got = json.loads(r.stdout)
            except ValueError:
                got = None
            if not (isinstance(got, list) and all(isinstance(x, dict) and isinstance(x.get("key"), str) and isinstance(x.get("said"), str)
                                                  and (x.get("unit") is None or isinstance(x["unit"], str)) for x in got)):
                unchecked.append(dict(label=l, host=h, why="its sweep printed no list of sessions crew reads"))
                continue
            ended += [dict(label=l, host=h, key=x["key"], unit=x.get("unit"), said=x["said"],
                           why="its card is closed" if x["key"] in rowed else "its row is gone") for x in got]
    return ended, unchecked


def sweep_judgment(label, rowed, cards, unread, batched, readings=()):
    """The rail's judgment a card sweep acts on (read.1): live, every row key of the partition less each the run record
    holds as closed with no card open under it, and every reading of a bolt that is a row of its kit's landings card,
    land/<bolt> (readings), whatever card of the bolt's own was closed under that key before, which is no word on the
    row; blind, the key prefixes it can't judge, batch/ while the record could not be read from its branch, when no key
    is taken out for being closed either."""
    closed = set() if unread else batched.get("closed", set()) - {c["key"] for c in cards if c["label"] == label}
    blind = ["batch/"] if unread else []
    return {"live": sorted((rowed - closed) | set(readings)), "blind": sorted(blind)}


def landings_moved(cards_, mains, kept):
    """Which kits' landings cards main moved under (rail-cards "Main moves under an open card", "Main has not moved"),
    from facts alone (code.7): cards_, each open landings card as (label, kit); mains, the revision of main the survey
    read each kit at in its builder's main checkout, {(label, kit): main_at}, as last fetched (gather.kit, plan.18);
    kept, the revision its rows were last forecast against, {(label, kit): sha}, none when none is kept. Returns (due,
    unread): the cards due a raise, whose kit's main is at another revision than the kept one, or with none kept; and
    those whose kit's read names no revision, an older gather's or a read that failed, which are not judged moved
    (read.2)."""
    due, unread = [], []
    for c in dict.fromkeys(cards_):
        now, was = mains.get(c), kept.get(c)
        if not now:
            unread.append(c)
        elif not was or not (now.startswith(was) or was.startswith(now)):
            due.append(c)
    return due, unread


def rail_read(fleet, labels, board=False, sweep=False):
    """Everything the rail is made from, in one read of the labels' plans, proposals, kits and run record: the plans
    found and the errors of those that could not be read, the survey, the open proposals, the cards, the branches whose
    record could not be read, the landings and gives, the operations' entries, every entry read, and the rows. The survey
    is of each host holding a bolt; with board, of every team of the labels, with the bolt it holds or none, and its
    dev servers, slots and explorations too, for the board (board.py), from which the rail's text is made as well.
    With sweep, once the rows are made, the cards on this host are swept under its sign-in (sweep_cards), against the
    proposals the plans read hold (proposals_held), the cards read then being those open once it acted, each kit's
    landings card main moved under is raised again (sweep_moved), and the card sessions whose card is closed or whose row is gone are
    ended on every host of the labels read; what the sweeps did, and which hosts were not checked, are in the read
    (sweep_sessions). No state is written but by those sweeps' acts."""
    errors = {}
    found = plans(fleet, labels, errors)
    held = [(b.get("Team"), b.name(), b.get("Repo")) for _, _, _, p in found if p for b in p.bolts() if b.get("Team")]
    if board:
        held += [(t, None) for l in labels for t in crew.partition_of(fleet, l)["teams"]]
    sv = survey(fleet, held, board=board)
    props = open_proposals(fleet, [l for l, _, _, p in found if p], found)
    times, cards_, unread, landings, gives, batched, deploys, opses, logs = rail_record(fleet, found, props)
    read = dict(found=found, errors=errors, sv=sv, props=props, times=times, cards=cards_, unread=unread, landings=landings,
                gives=gives, ops=opses, logs=logs, rows=rail_rows(fleet, found, sv, props, times, batched) + deploys)
    if sweep:
        read["proposed"] = proposals_held(found)
        read["swept"] = sweep_cards(fleet, read)
        read["cards"] = swept_cards(read["cards"], read["swept"], crew.this_host(), datetime.datetime.now(datetime.timezone.utc),
                                    {l: partition_kits(fleet, l) for l, *_ in found})
        read["moved"] = sweep_moved(fleet, read)
        read["ended"], read["unchecked"] = sweep_sessions(fleet, found, sv, read["rows"], read["cards"], unread, batched)
        reckon_batches(fleet, found)
    return read


def swept_cards(cards_, swept, here, now, kits=()):
    """The open cards once the sweep acted (sweep_cards): each it closed, withdrew or recorded lost gone, and each it
    posted, again or anew, there, posted on this host (here) at now under its row's key in its owner's name, on its
    row's object (cards.row_object, the kits of its partition, {label: names}, as it takes them)."""
    gone = {d["card"] for d in swept["done"] if d["did"] in ("closed", "withdrawn", "lost") and d["card"]}
    return [c for c in cards_ if c["card"] not in gone] + [
        dict(label=d["label"], card=d["new"], key=d["key"], on=cards.row_object(d["key"], kits.get(d["label"], ()) if kits else ()), by=d["by"], host=here, at=now)
        for d in swept["done"] if d.get("new")]


def rail_text(fleet, labels, read, now):
    """The rail as crew rail prints it, from a read rail_read made: its groups in order, each row with when it began to
    wait, how long ago that was, the commands that answer it, and its card key with whether a card is open for it,
    whose and its id, by which its owner asks Pending You for it, or, with none open, the words of the refusal of its
    last post, oldest first; then the questions the asking roles put to the user, each with its key, which names it,
    its asker and its age, since no entry holds a card's words (record.3); then each card act of an agent's whose reply
    crew could not read (unread_card_acts); then the decision records waiting on the user, each the design
    agent's open card for one, with when it was asked and by whom, and no command, since the card is where it is
    answered; then any open card whose row is gone that the sweep did not close, with the host whose rail read closes
    it; then, from a read that swept, each card the sweep closed, withdrew, recorded lost or posted, and each batch it
    closed or left with no card, named so, each partition it changed nothing for and why, each landings card raised
    again as main moved under it and each whose kit's revision of main can't be read (sweep_moved), each card session ended,
    with its host and why, and each host whose sessions were not checked. A host is named as not answering only when it holds a bolt of the plans read, so a read that surveyed more
    (the board's) gives the same text."""
    found, rows, cards_, here = read["found"], read["rows"], read["cards"], crew.this_host()
    holding = {fleet["teams"][b.get("Team")]["machine"] for _, _, _, p in found if p for b in p.bolts() if b.get("Team") in fleet["teams"]}
    sv = {h: v for h, v in read["sv"].items() if h in holding}
    swept = read.get("swept") or {"done": [], "unswept": []}
    logs = read.get("logs") or {}
    lines = [f"What waits on you ({', '.join(labels)}), as of {now.astimezone():%H:%M:%S}"]

    def when(c):
        return f"  {c['at'].astimezone():%Y-%m-%d %H:%M}  {age(c['at'], now):<7}  "
    for g in RAIL:
        lines += ["", g]
        mine = sorted((r for r in rows if r["group"] == g), key=lambda r: (r["at"] is None, r["at"] or now, r["what"][0]))
        if not mine:
            lines.append("  none")
        for r in mine:
            at = r.get("date") or (f"{r['at'].astimezone():%Y-%m-%d %H:%M}" if r["at"] else "-")
            first, *rest = r["what"]
            lines.append(f"  {at:<16}  {age(r['at'], now) if r['at'] else '-':<7}  {first}")
            lines += [" " * 29 + w for w in rest]
            lines += [f"    {c + ':':<8}{cmd}" for c, cmd in r["cmds"]]
            refused = last_refusal(logs.get(r["label"], []), r["key"])
            lines += [f"    {'card:':<8}{r['key']}, open, asked by {c['by']} ({c['card']})" for c in cards_
                      if (c["label"], c["key"]) == (r["label"], r["key"])] or [
                f"    {'card:':<8}{r['key']}, none open" + (f"; its last post was refused: {refused}" if refused else "")]
    questions = question_cards(cards_, read["unread"])
    if questions:
        lines += ["", "questions waiting on you:"]
    for c in questions:
        lines.append(when(c) + f"{c['key'] or 'a question'} ({c['label']}), asked by {c['by']} on {c['host']} ({c['card']})")
    unread_acts = unread_card_acts(logs, now)
    if unread_acts:
        lines += ["", "card acts crew could not read:"]
    for label, e in unread_acts:
        lines.append(f"  {utc(e['At']).astimezone():%Y-%m-%d %H:%M}  {age(utc(e['At']), now):<7}  {e['Act']} by {e.get('By')} "
                     f"on {e.get('Host')} ({label})" + (f", under {e['Key']}" if e.get("Key") else "")
                     + ": Pending You's reply named no card")
    records = record_cards(cards_, read["unread"])
    if records:
        lines += ["", "decision records waiting on you:"]
    for c in records:
        lines.append(when(c) + f"{c['key']} ({c['label']}), asked by {c['by']} on {c['host']}")
    stray = stray_cards(fleet, found, sv, rows, cards_, read["unread"], logs)
    if stray:
        lines += ["", "open cards whose row is gone:"]
    for c in stray:
        lines.append(when(c) + f"{c['key']} ({c['label']}), asked by {c['by']} on {c['host']}")
        lines.append(f"    {'left:':<8}" + (f"a rail read on {c['host']} closes it, under that host's sign-in" if c["host"] != here
                                            else "a later rail read here closes it"))
    done = [f"  {d['key'] or 'a question'} ({d['label']}), {d['by']}" + (f"'s {d['card'] or d['new']}" if d["card"] or d["new"] else ", no card")
            + f": {d['did']}: {d['words']}" for d in swept["done"]]
    lines += (["", "cards swept:"] + done if done else []) + (
        ["", "cards not swept:"] + [f"  {u['label']}: {u['why']}" for u in swept["unswept"]] if swept["unswept"] else [])
    moved = read.get("moved") or {"raised": [], "unread": []}
    lines += (["", "landings cards forecast again, main having moved:"] + [
        f"  land/{m['kit']} ({m['label']}): main is at {m['now'][:7]}, its rows forecast at "
        + (m["was"][:7] if m["was"] else "no revision crew kept") + ": "
        + (f"its raise refused: {m['said']}" if m["said"] else f"raised again ({m['card']})" if m["card"] else "raised again, no card left open")
        for m in moved["raised"]] if moved["raised"] else []) + (
        ["", "landings cards whose main can't be read:"] + [
            f"  land/{u['kit']} ({u['label']}): whether main moved under it can't be told: {u['why']}" for u in moved["unread"]]
        if moved["unread"] else [])
    ended = [f"  {e['key']}{' ' + e['unit'] if e['unit'] else ''} ({e['label']}) on {e['host']}: {e['why']}; {e['said']}"
             for e in read.get("ended") or []]
    unended = [f"  {u['host']} ({u['label']}): {u['why']}" for u in read.get("unchecked") or []]
    lines += [""] if ended or unended else []
    lines += (["card sessions ended:"] + ended if ended else []) + (["card sessions not checked:"] + unended if unended else [])
    for h, v in sv.items():
        if not v["ok"]:
            lines.append(f"\n{h} did not answer ({v['error']}): its units and bolts may also wait on you")
    return "\n".join(lines)


def unread_card_acts(logs, now):
    """Each card act a crew agent made through Pending You's tools whose reply named no card, recorded unread by the card
    hook, in the last CARD_DAYS days, oldest first: (label, entry), from each partition's entries (logs)."""
    since = now - datetime.timedelta(days=CARD_DAYS)
    return [(l, e) for l, es in sorted(logs.items()) for e in es
            if (e.get("Act") or "").startswith("card.") and e.get("State") == "unread" and utc(e["At"]) >= since]


def rail_view(fleet, a):
    """crew rail [--label L]: what waits on the user, as rail_text gives it, read from the plans, the proposals, the
    kits and the run record. It sweeps the cards on this host under its sign-in (sweep_cards) and ends the card
    sessions whose card is closed or whose row is gone, on every host of the partitions read, and says what each did;
    it writes nothing else. It prints everything it could read, then exits non-zero naming each plan it could not."""
    label = default_label(fleet, a)
    labels = [label] if label else list(fleet["partitions"])
    read = rail_read(fleet, labels, sweep=True)
    print(rail_text(fleet, labels, read, datetime.datetime.now(datetime.timezone.utc)))
    if read["errors"]:
        sys.exit("\n".join(read["errors"].values()))


# ------------------------------------------------------------------------------------------------ crew card

# A card's plannotator session, by its card key, in ~/.local/state/crew/cards/<label>/<key>/ on the owner's host, the
# key's slashes as folders, an old batch card's per unit under <key>/<unit>/: session.json (pid, document, url,
# started, its document the files plannotator was given joined by ", "), and plannotator's result.json once the user
# decides.
CARDS = pathlib.Path.home() / ".local/state/crew/cards"


def landings_main(label, kit):
    """Where the main level's host keeps the revision of main a kit's landings card's rows were last forecast against
    (CardActs.keep_main), beside the card's state: no session's, so no card's close or sweep removes it."""
    return CARDS / label / "land" / kit / "main"
# The rail rows' card keys, the thing's and not its version's (record 0031): a card crew keys them by, which its
# commands name. A card under an older form, land/<bolt>/<head> or a verify report's verify/<unit>/<stamp>, is still
# crew's (crews_key), closed by the rail's read as one whose row is gone, and none is posted.
CARD_KEYS = (r"proposal/\d+", r"batch/\d+", r"batch/\d+-\d+", r"land/[a-z0-9][a-z0-9-]*", r"deploy/[a-z0-9][a-z0-9-]*",
             r"op/[a-z0-9][a-z0-9-]*/\d+")
# A verify report's key, verify/<unit>/<stamp>, whose card and session from before teams.17 a sweep still ends, and
# whose answered card its asker closes (card_refusal).
VERIFY_KEY = r"verify/[a-z0-9][a-z0-9-]*/\d{8}-\d{4}"
# A decision record's card key, the design agent's: the kit and the record's four digits, one card per record however
# often it is revised (briefs.15, record 0031 §1), raised by crew record. It is no rail row's: the rail lists its open
# cards apart. A card the design agent posted before record 0031, under the key with the commit after it,
# record/<kit>/<number>/<commit>, is the record's too (cards.row_object), closed at the record's status as one under
# this key is.
RECORD_KEY = r"record/([a-z0-9][a-z0-9-]*)/(\d{4})"
CARD_START = 10  # seconds a start waits for plannotator to list its session
# The ports a card's session takes the first free one of when its environment names no range: swancloud's agents'
# range, set in its lib/agent-config.nix (session_env).
CARD_PORTS = "19432-19451"
CARD_POLL = 5  # seconds between a wait's reads
CARD_GRACE = 120  # seconds a session is left alone after it starts, since the rail's read may not have seen its row


# The roles that ask the user a question of their own on a card, by the kind role() gives them (record 0031, briefs.11).
ASKERS = ("conductor", "planner", "main-ops", "design")
# The first part of every key crew raises a card under: a rail row's, a decision record's, and a verify report's,
# which no row has had since teams.17. No agent's question takes one (crews_key).
CREWS = {"proposal": "a proposal's card is crew's, raised by crew plan propose and closed at its approval or drop",
         "batch": "a batch's card is crew's, raised with its reading session once the reviewer's summary is delivered",
         "land": "a kit's landings card is crew's, raised in main-level ops's name when a bolt of the kit reads proven, "
                 "and closed when nothing waits to land on the kit's main",
         "deploy": "a deploy's card is crew's, raised by crew ops offer and closed at the deploy's end",
         "op": "a step's card is crew's, raised by crew ops step and closed with the step's state",
         "record": "a record's card is crew's, raised by crew record and closed at the record's status",
         "verify": "a verify report has no card: its findings are fixed in one round"}


def crews_key(key):
    """The kind of crew's own card a key names, by its first part (CREWS), whatever follows, the partition's label
    crew qualifies a key with as it sends it, its revision and its fill of a short one (cards.post_key) and a key of an
    older form among it; None for any other key, an agent's question's."""
    kind = key.split("/", 1)[0] if isinstance(key, str) and "/" in key else None
    return kind if kind in CREWS else None


def card_refusal(fleet, name, label, tool, key):
    """Whether a crew agent's Pending You call may go through (briefs.11, record 0031): None to let it, else the
    refusal's words. The user's own name is never checked. A card's post, change or close is a question's, the agent's
    own, only from a conductor, the planner, main-level ops or the design agent (ASKERS), and never under crew's own
    key (crews_key). A post's key is its idempotencyKey, judged by its form alone, with or without the partition's
    @<label>, :<n> or the fill of a short key (cards.post_key), and no plan read. A change or a close carries a request id and no key, so its key is
    the one this host's run record holds the card under, crew's raises and the agents' own posts alike, read locally
    with no state-branch fetch, None when it holds none; the hook refuses the call when that record can't be read. The planner's close of a card under
    batch/<n>-<k>, which it posted itself before a batch was one card and crew never raises, passes, a departure from
    briefs.11 that goes once no such card is open; its post or change there is refused. So does an asker's ack of an
    answered card under a verify report's key, verify/<unit>/<stamp>, a row form crew no longer raises (teams.17),
    which a conductor posted before it and no event of crew's closes, the same departure: its post, change or
    withdrawal there is refused (signal 2026-10-19-crw-2-conductor-2bec975e/01). An area is made only under
    create-area:<owner>/<kit> for a kit the agent's team builds or, for the main level, a kit of any team of its
    partition, read from the teams file. Everything else passes: a question's form, and its key but crew's, are its
    asker's. A decision of the role, the call and the key alone (code.7)."""
    kind, of = role(fleet, name)
    if kind == "user":
        return None
    what = "an area" if tool == "create_area" else "a card"
    cmd = f"{crew.HOME}/plugin/bin/crew"
    if kind not in ASKERS:
        if kind == "team":
            left = (f"Tell {of}-conductor what you wait on with `{cmd} tell`." if name == f"{of}-ops"
                    else f"Say what you need with `{cmd} needs`, and your conductor gets it and asks if it must.")
        elif kind == "dispatcher":
            left = f"Ask through {of}-planner with `{cmd} tell`."
        elif kind == "operator":
            left = "The user is in your pane: ask them there."
        else:
            left = "Tell the partition's operator what you wait on, as your brief says."
        return (f"crew refuses {what} from {name}: only a conductor, the planner, main-level ops and the design agent ask "
                f"the user on a card. {left}")
    if tool == "create_area":
        teams = [of] if kind == "conductor" else crew.partition_of(fleet, label)["teams"]
        mine = sorted({f"create-area:{fleet['teams'][t]['kit']['repo']}" for t in teams})
        if key in mine:
            return None
        return (f"crew refuses an area under {key}: " + (f"{name} makes a kit's area only under {either(mine)}." if mine
                else f"no kit's area is {name}'s to make."))
    crews = crews_key(key)
    old = (kind == "planner" and tool in ("cancel_request", "ack_answer") and old_batch(key)
           or tool == "ack_answer" and old_verify(key))
    if crews and not old:
        verb = {"post_request": "post", "update_request": "change"}.get(tool, "close")
        return (f"crew refuses {name}'s {verb} of the card under {key}: {CREWS[crews]}. Ask a question of your own under "
                f"a key of your own, ask/{name}/<what it is about>.")
    return None


def old_batch(key):
    """Whether a card key is a batch's posted as cards of five before a batch was one card, batch/<n>-<k>, whose
    sessions are its units'."""
    return bool(re.fullmatch(r"batch/\d+-\d+", key or ""))


def old_verify(key):
    """Whether a card key is a verify report's, verify/<unit>/<stamp>, posted by a conductor before teams.17."""
    return bool(re.fullmatch(VERIFY_KEY, key or ""))


def card_of(fleet, a, unit_needed=True):
    """The partition a card command runs as and the key's folder, an old batch card's per unit: refused with no
    partition, a key that is not one of the rail's, a batch/<n> key with a unit, since a batch has one session on the
    whole batch, a batch/<n>-<k> key with no unit where one is needed, and a unit with any other key."""
    label = default_label(fleet, a) or fail("crew card runs as the card's partition: run it as a crew agent, or add --label")
    any(re.fullmatch(k, a.key) for k in CARD_KEYS) or fail(
        f"{a.key} is not a card key: proposal/<n>, batch/<n>, land/<kit> or land/<bolt>")
    old = old_batch(a.key)
    if old:
        a.unit or not unit_needed or fail(f"a batch card posted as cards of five has a session for each of its units: "
                                          f"crew card {a.sub} {a.key} <unit>")
    elif a.key.startswith("batch/"):
        not a.unit or fail(f"a batch has one reading session, on the whole batch: crew card {a.sub} {a.key}")
    else:
        not a.unit or fail(f"only an old batch card's key, batch/<n>-<k>, takes a unit, and {a.key} is not one")
    if a.unit:
        crew.NAME.match(a.unit) or fail(f"a unit's name is lowercase words with dashes, not {a.unit}")
    return label, CARDS / label / a.key / a.unit if old and a.unit else CARDS / label / a.key


def session_refusal(key, label, main, here, team=None, kits=()):
    """Why a card key's session is not started or waited on here, before its row is read: a batch card's one session
    runs on the partition's main level's host (main), where its summary is written and its card raised; a bolt's
    reading, land/<bolt>, on the host of the team holding the bolt (team), where its kit's main checkout is; a kit's
    landings card, land/<kit> (kits, the partition's kits' names, land_key), has no reading of its own, each of its
    rows having its bolt's."""
    kind = land_key(key, kits)
    if kind and kind[0] == "kit":
        return (f"{key} is {kind[1]}'s landings card, {label}-ops's, which has no reading of its own: each of its rows "
                f"has its bolt's, land/<bolt>, on the host of the team holding the bolt")
    if key.startswith("land/") and team != here:
        return (f"{key}'s reading session runs on {team}, the host of the team holding its bolt, where its kit's main "
                f"checkout is: run crew card session {key} there")
    if key.startswith("batch/") and not old_batch(key) and main != here:
        return (f"{key}'s reading session runs on {main}, where {label}'s main level writes the batch's summary: run crew card "
                f"session {key} there")
    return None


def no_row(label, key, down):
    """What a card command says of a key no row of the rail has: its row is gone, or whether one would can't be known,
    naming each host that did not answer (read.1)."""
    return (f"no row of {label}'s rail has the card key {key}"
            + (", and whether one would can't be known: " + "; ".join(down) if down else ": its row is gone, so its card has nothing to read"))


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
    """Whether plannotator lists the recorded session's pid as serving its document, path by path: a session of
    several files is listed with their paths joined by ", ", as crew records its document, and a folder's target, as
    a session started before crew gave plannotator files, without its last slash."""
    got = listed.get(s["pid"])
    return bool(got) and [os.path.realpath(p) for p in got["target"].split(", ")] == s["document"].split(", ")


def card_result(d):
    """The user's decision in a key's session, as plannotator wrote it to result.json: (decision, feedback, how many
    annotations), feedback None when it gave none and the count None when it gave none; None while there is no result."""
    f = d / "result.json"
    try:
        r = json.loads(f.read_text())
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        fail(f"crew can't read plannotator's result {f}: {e}")
    if not isinstance(r, dict) or r.get("decision") not in ("approved", "annotated", "dismissed"):
        fail(f"plannotator's result {f} holds no decision crew knows: approved, annotated or dismissed")
    fb, k = r.get("feedback"), r.get("annotationCount")
    return (r["decision"], fb if isinstance(fb, str) and fb.strip() else None,
            k if isinstance(k, int) and not isinstance(k, bool) and k >= 0 else None)


def card_row(fleet, label, key):
    """The rail row of one partition with that card key, read as crew rail reads its rows: only the proposals for a
    proposal's key, and only the run record's batches for a batch card's."""
    found = plans(fleet, [label])
    plan = found[0][3]
    kind = key.split("/")[0]
    sv = survey(fleet, [])
    props = open_proposals(fleet, [label], found) if kind == "proposal" and plan else []
    batched = {}
    if kind == "batch" and plan:
        _, _, unread, _, _, batched, *_ = rail_record(fleet, found, [])
        not unread.get(label) or fail(f"crew can't tell whether {key}'s card is still open: "
                                      + "; ".join(f"{h} did not answer" for h in sorted(unread[label])))
    row = next((r for r in rail_rows(fleet, found, sv, props, {}, batched) if r["key"] == key), None)
    if row:
        return row, props
    fail(no_row(label, key, [f"{h} did not answer ({v['error']})" for h, v in sv.items() if not v["ok"]]))


def card_stop(proc):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def card_session(fleet, a, acts=None):
    """crew card session <key> [<unit>] [--label L]: the plannotator session of a card that has one, on what the rail
    row with that card key asks the user to read, started on this host with an Approve button and no browser if none
    runs, and its link printed (session_open). A batch card's, batch/<n>, is one session on the whole batch, started on
    the partition's main level's host and refused elsewhere, naming it: crew writes the batch's folder (batch_folder)
    and gives plannotator its files as one review. A proposal's is on its page, for a proposal whose card links one
    (proposal_reads), and refused for any other, whose card holds it whole. Either is opened by reading_again, so a
    start anew is recorded and the planner's card, while it waits on the user, changed to carry the link, and a card
    the user has answered left as it is. An old batch card's, batch/<n>-<k>, is one
    session for each unit it holds, on that unit's whole change as its Markdown files, started on the host the teams
    file names for the unit's team (code.3) and refused for a unit the card does not hold. A landing's, land/<bolt>, is
    one session on what the bolt brings to main, on the host of the team holding it (land_session). Refused for a key
    with no row, a document crew can't read whole, and a link that would open only on this host."""
    label, d = card_of(fleet, a)
    if a.key.startswith("land/"):
        return land_session(fleet, label, a.key, acts)
    here = crew.this_host()
    why = session_refusal(a.key, label, fleet["partitions"][label]["machine"], here)
    not why or fail(why)
    row, props = card_row(fleet, label, a.key)
    row["doc"] or fail(f"{a.key}'s card has no document to read, so it has no session")
    name = f"{a.key}'s session"

    def said(url, decided):
        print(url)
        if decided:
            print(f"the user decided in {name} before it ended: crew card wait {a.key}{' ' + a.unit if a.unit else ''} gives "
                  "the decision", file=sys.stderr)
    if not old_batch(a.key):
        if row["doc"][0] == "page":
            p = next(x for x in props if x["proposal"] == row["doc"][2])
            proposal_reads([do_args(label, c["do"]) for c in p["changes"]]) or fail(
                f"{a.key}'s card has nothing to read: it holds the proposal whole, and only a proposal of more than "
                f"{cards.CARD_NEW} new units has a reading session")
        reading_again(fleet, label, a.key, acts, said)
        return
    a.unit in row["units"] or fail(f"{a.key} holds {either(row['units'])}, not {a.unit}: its sessions are its units'")
    t = fleet["teams"].get(row["teams"][a.unit]) or fail(f"{a.unit}'s team {row['teams'][a.unit]} is not in the teams file")
    t = unit_kit_team(fleet, label, t, a.unit)
    if t["machine"] != here:
        return forward_card(fleet, t, a, label)
    folder, name = change_folder(fleet, t, a.unit, d / "change"), f"{a.key}'s session of {a.unit}"
    said(*session_open(d, name, lambda: change_files(folder) or fail(
        f"{a.unit}'s change {folder} on {here} holds no Markdown file to read"))[:2])


# The change note of a card changed to carry its reading's new link, a kit's landings card a row's (card-sessions).
RELINKED = "Its reading is open again at a new link"


def relinks(due, got):
    """Whether crew changes a card to carry its reading's new link (card-sessions "Starting a batch's or a proposal's
    reading changes its card"): only when it is due, the session started anew or the card standing without its
    reading, and the card, as get_request gives it (got, None when none is held or it could not be read), still waits on
    the user; a card the user has answered is left as it is, since a new card following it would ask again."""
    return bool(due) and card_waiting(got)


def card_waiting(got):
    """Whether a card, as get_request gives it (got, None when none is held or it could not be read), still waits on
    the user, so crew changes it in place; one the user answered is left as it is."""
    return isinstance(got, dict) and got.get("status") in OPEN


def land_session(fleet, label, key, acts=None, say=None):
    """crew card session land/<bolt>: the bolt's one reading session, on what it brings to main at its head, on the host
    of the team holding it and refused elsewhere, naming it, while it is a row of its kit's landings card that can land,
    read from the same facts as its row (land_read) and opened as its row's raise opens it (reading_open), its link
    printed, or said by say(link, decided) when given. The try, from the row's read on, is recorded as one card.reading
    entry on the bolt in its conductor's name, done when the session started anew and refused with crew's message when
    the bolt is no row that can land or the reading could not open, a session given again recording nothing (record.1),
    nor a refusal before the try. When it started the session anew, none running, or the run record shows the kit's
    card standing without a row's reading (kit_unread), the kit's card is raised on the partition's main machine with
    the new link's note (land_hand), changed in place while it waits on the user and left as it is once they answered
    it (card-sessions "A landing's session follows the bolt's head"). Refused for land/<kit>, which has no reading of
    its own, a bolt the plan does not hold, one no team holds, and one that is no row that can land, saying what it
    waits on or why it is held (card-sessions "A bolt that is no row"). As reading_open returns it: its link, whether
    the user decided in it, and whether it was started anew; a refusal of the try, recorded, is raised again."""
    acts = acts or CardActs(fleet)
    kits = partition_kits(fleet, label)
    why = session_refusal(key, label, fleet["partitions"][label]["machine"], acts.host(), None, kits)
    if why and land_key(key, kits)[0] == "kit":
        fail(why)
    bolt = key.split("/", 1)[1]
    plan, b, t = land_held(fleet, label, bolt)
    b or fail(f"{label}'s plan holds no bolt {bolt}, so {key} has no reading")
    t or fail(f"bolt {bolt} is held by no team, so it is no row of its kit's landings card, and it has no reading")
    why = session_refusal(key, label, fleet["partitions"][label]["machine"], acts.host(), t["machine"], kits)
    not why or fail(why)
    owner, obj, kit = f"{t['name']}-conductor", cards.row_object(key, kits), b.get("Repo") or t["kit"]["name"]
    try:
        row, why = land_read(fleet, label, plan, b, t)
        row or fail(f"{bolt} is no row of {kit}'s landings card, so it has no reading: {why}")
        row["box"] or fail(f"{bolt} is {row['why']} on {kit}'s landings card, so it has no reading until it can land again")
        url, decided, started = acts.reading(label, key, row["facts"])
    except Refusal as e:
        acts.emit(label, "card.reading", [obj], by=owner, refused=str(e), Key=key)
        raise
    if started:
        acts.emit(label, "card.reading", [obj], by=owner, Key=key)
    if say:
        say(url, decided)
    else:
        print(url)
        if decided:
            print(f"the user decided in {key}'s session before it ended: crew card wait {key} gives the decision", file=sys.stderr)
    if started or kit_unread(acts, label, kit):
        land_hand(fleet, label, kit, f"{bolt}: {RELINKED}")
    return url, decided, started


def kit_unread(acts, label, kit):
    """Whether the kit's landings card, main-level ops's, stands without a row's reading (reading_unread), read from the
    partition's run record, where its posts and changes reach the branch from the main machine (read.5); False, said,
    when that record can't be read, so a session given again changes no card."""
    try:
        entries = acts.partition(label)
    except Refusal as e:
        print(f"card land/{kit}: whether it stands without a row's reading can't be read: {e}", file=sys.stderr)
        return False
    key = f"land/{kit}"
    return reading_unread(entries, key, cards.card_under(entries, key, f"{label}-ops"))


def relink(acts, label, key, owner, due, change):
    """The card owner holds under key on this host changed to carry its reading's link, when due (relinks): read in the
    owner's name, and changed in place by change(), the kind's change with RELINKED as its note, while it waits on the
    user; left as it is, said, once the user has answered it; not changed, said, when whether it waits can't be read.
    Nothing when none is held or it is not due."""
    card = cards.card_under(acts.entries(label), key, owner) if due else None
    if not card:
        return
    got = None
    try:
        with acts.bridge(owner, "The reading stands at its new link, and its card is not changed.") as py:
            got, words = py.answer("get_request", {"requestId": card, "name": owner})
    except Refusal as e:
        words = str(e)
    if relinks(due, got):
        change()
    elif got is not None:
        print(f"card {key}: {card} is left as it is: " + ("the user has answered it" if got.get("status") == "answered"
                                                          else f"Pending You shows it {got.get('status')}"))
    else:
        print(f"card {key}: {card} is not changed, since whether it waits on the user can't be read: {words}", file=sys.stderr)


def reading_facts(fleet, label, key, acts):
    """The facts a batch's or a long proposal's reading is opened on (reading_open), read as its raise reads them: a
    batch's card's from this host's run record and the reviewer's summary (batch_read); a proposal's number, the open
    one of its chain at the branch's tip (chain_read), whose page is its reading. Refused when its point has passed."""
    kind, n = key.split("/")[0], int(key.split("/")[1])
    if kind == "batch":
        return batch_read(fleet, label, n, acts) or fail(
            f"{key}'s card has nothing to read: this host's run record holds no batch {n} waiting on the user, or its "
            "summary is not there")
    got = chain_read(fleet, label, n) or fail(f"{key}'s card has nothing to read: no proposal of its chain is open")
    return dict(n=got[1], first=n)


def reading_again(fleet, label, key, acts=None, say=None):
    """A batch's or a long proposal's reading, batch/<n> or proposal/<n>, opened after its card's raise
    (card-sessions "Starting a batch's or a proposal's reading changes its card"): its facts read as its raise reads
    them (reading_facts), and its reading opened as the raise opens it (reading_open), said by say(link, decided) when
    given; the try recorded as one card.reading entry on the row's object in the planner's name, with the card held
    under the key, done when the session started anew and refused with crew's message when it could not open, a
    session given again recording nothing (record.1); then the card the planner holds under the key changed in place
    to carry the link, while it waits on the user, when the session started anew or the run record shows the card
    standing without its reading (reading_unread), by the kind's raise with RELINKED as its note (relink). As
    reading_open returns it: its link, whether the user decided in it, and whether it was started anew; a refusal,
    recorded, is raised again."""
    acts = acts or CardActs(fleet)
    owner, obj = f"{label}-planner", cards.row_object(key)
    card = cards.card_under(acts.entries(label), key, owner)
    held = {"Card": card} if card else {}
    try:
        url, decided, started = acts.reading(label, key, reading_facts(fleet, label, key, acts))
    except Refusal as e:
        acts.emit(label, "card.reading", [obj], by=owner, refused=str(e), Key=key, **held)
        raise
    if started:
        acts.emit(label, "card.reading", [obj], by=owner, Key=key, **held)
    if say:
        say(url, decided)
    row = {"label": label, "key": key, "group": "proposals" if key.startswith("proposal/") else "batches"}
    relink(acts, label, key, owner, started or reading_unread(acts.entries(label), key, card),
           lambda: raise_proposal(fleet, row, acts, "relink") if key.startswith("proposal/") else raise_batch(fleet, row, acts, RELINKED))
    return url, decided, started


def proposal_reads(argvs):
    """Whether a proposal's card links a reading session, as cards.proposal_card decides it from the proposal's
    commands (briefs.9): more units and chores new to a bolt or the queue than its boxes take, whatever else it
    changes, since only those are boxes."""
    return len(new_units(argvs)) > cards.CARD_NEW


# What a card's session does not carry of the agent that starts it: herdr's reading of the agent's pane, which the
# Claude plannotator starts to answer the user would report its own session to, so herdr took it for a new session in
# the agent's pane and dropped the agent's name (swc-3-conductor on deneb, 2026-10-23: its landing card's session,
# started by `crew card wait`, gave herdr the session of the Claude that answered the user's question on the page, and
# crew read the conductor ended; signal 2026-10-23-swc-3-conductor-8556b697/01); and the identity crew-role gives
# the agent (teams.6), which would record that Claude's start as the agent's own (hooks/session-start), and the
# agent's Claude session a command carries to another host (record.session), so the session and what it starts act
# under no agent's name (briefs.17).
NOT_CARRIED = ("HERDR_ENV", "HERDR_PANE_ID", "HERDR_TAB_ID", "HERDR_WORKSPACE_ID", "HERDR_AGENT", "HERDR_SESSION",
               "HERDR_SOCKET_PATH", "CREW_AGENT", "CREW_LABEL", "CREW_ROLE", "CREW_LAUNCH", "CREW_SESSION", "SLUICE_AGENT",
               "SLUICE_BRANCH")


def session_env(environ):
    """The environment a card's session starts plannotator in, from the caller's environ, which is not changed:
    everything but what it does not carry of the agent (NOT_CARRIED), with no browser opened and its links for another
    host (session_open), and PLANNOTATOR_PORT kept when it names a range plannotator 0.28.26 reads (<a>-<b>,
    1 <= a <= b <= 65535), else crew's own, CARD_PORTS, so the session takes the first free port of a range wherever
    crew runs: unset, one port, which plannotator holds alone, and a value it can't read, which in remote mode it takes
    as the one port 19432."""
    env = {**{k: v for k, v in environ.items() if k not in NOT_CARRIED}, "PLANNOTATOR_SKIP_BROWSER_OPEN": "1", "PLANNOTATOR_REMOTE": "1"}
    m = re.fullmatch(r"([0-9]+)-([0-9]+)", env.get("PLANNOTATOR_PORT", ""))
    if not (m and 1 <= int(m[1]) <= int(m[2]) <= 65535):
        env["PLANNOTATOR_PORT"] = CARD_PORTS
    return env


def session_open(d, name, write):
    """The plannotator session of a card key on this host, kept in its folder d, called name in what is said: the one
    crew recorded given again while it serves its document, or kept for crew card wait when the user decided in it
    before it ended; else started anew on the files write() writes and returns, as one review in their order, with an
    Approve button and no browser (plannotator 0.28.6), recorded once plannotator lists it. One the user closed
    undecided has its result moved aside, so a new one starts. Returns its link, whether the user decided in it before
    it ended, and whether it was started anew rather than given again. Refused, any session it started ended, when
    plannotator can't be listed, is not on this host, does not list it in time, ends first, or gives a link only this
    host could open (read.1)."""
    import shutil
    d.mkdir(parents=True, exist_ok=True)
    with open(d / ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        s = card_recorded(d)
        if s:
            listed, why = plannotator_sessions()
            listed is not None or fail(f"crew can't tell whether {name} still runs: {why}")
            verdict = session_verdict(s, serving(listed, s), card_result(d))
            if verdict in ("serving", "decided"):
                return s["url"], verdict == "decided", False
            if verdict == "dismissed":
                (d / "result.json").rename(d / f"result.{re.sub(r'[-:]', '', s['started'])}.json")
            (d / "session.json").unlink()
        shutil.which("plannotator") or fail("plannotator is not on this host's path, and a card's session is a plannotator session")
        here = crew.this_host()
        files = [os.path.realpath(f) for f in write()]
        gone = [f for f in files if not os.path.isfile(f)]
        not gone or fail(f"{name}'s document {gone[0]} is not on {here}")
        doc = ", ".join(files)  # as plannotator lists a session of several files
        started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        env = session_env(os.environ)
        with open(d / "out", "w") as out, open(d / "err", "w") as err:
            # Several files, each its own path, open as one review in that order with one decision (plannotator 0.28.6).
            # Its own session, so it outlives the command that started it, and the shell that ran that.
            proc = subprocess.Popen(["plannotator", "annotate", *files, "--gate", "--json", "--result-file", str(d / "result.json")],
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
        if local_link(got["url"]):
            card_stop(proc)
            fail(f"plannotator gave {name} the link {got['url']}, which would open only on {here}, so crew ended it: "
                 "a card's session needs PLANNOTATOR_URL_HOST naming the host on the tailnet (swancloud sets it to auto)")
        tmp = d / ".session.json"
        tmp.write_text(json.dumps({"pid": proc.pid, "document": doc, "url": got["url"], "started": started}) + "\n")
        tmp.replace(d / "session.json")
    return got["url"], False, True


def reading_open(fleet, label, key, facts):
    """The reading session of a card crew raises with one (briefs.9), started on this host or given again while it
    serves (session_open): a batch's, batch/<n>, on its folder, the reviewer's summary and every unit's change at the
    commit the batch read it at (facts' units), and refused but on the partition's main level's host; a landing's,
    land/<bolt>, on what the bolt brings to main at its head (landing_write), in the head's own folder, and refused but
    on the host of the team holding the bolt (facts' host), a session of the key on another head ended first; a long
    proposal's on its page, as crew plan proposed <n> prints it, a session of the key serving an older page of its
    chain ended first. As session_open returns it: its link, whether the user decided in it before it ended, and
    whether it was started anew; a Refusal says why it could not open."""
    d = CARDS / label / key
    why = session_refusal(key, label, fleet["partitions"][label]["machine"], crew.this_host(), facts.get("host"))
    not why or fail(why)
    if key.startswith("batch/"):
        units = [(u["unit"], u["team"], u["commit"]) for u in facts["units"]]
        return session_open(d, f"{key}'s session", lambda: batch_folder_write(fleet, label, facts["n"], units))
    if key.startswith("land/"):
        folder = d / facts["head"][:7]
        s = card_recorded(d) if d.is_dir() else None
        if s and not all(os.path.dirname(p) == os.path.realpath(folder) for p in s["document"].split(", ")):
            print(end_session(label, key)[0])
        return session_open(d, f"{key}'s session", lambda: landing_write(fleet, facts, folder))
    f = d / f"proposal-{facts['n']}.md"
    s = card_recorded(d) if d.is_dir() else None
    if s and s["document"] != os.path.realpath(f):
        print(end_session(label, key)[0])

    def write():
        p = next((x for x in open_proposals(fleet, [label]) if str(x["proposal"]) == str(facts["n"])), None) or fail(
            f"proposal {facts['n']} of {label} is not open, so it has no page to read")
        f.write_text(page(p, label))
        return [str(f)]
    return session_open(d, f"{key}'s session", write)


def session_verdict(s, serves, decided):
    """What crew card session does with the session it recorded for a key, s (plan's card-sessions): it still serves its
    document, so its link is given again ("serving"); the user approved or annotated before it ended, so it is kept for
    crew card wait ("decided"); the user closed it undecided, so its result is moved aside and a new one starts
    ("dismissed"); else it ended, and a new one starts ("ended")."""
    if serves:
        return "serving"
    if decided and decided[0] != "dismissed":
        return "decided"
    return "dismissed" if decided else "ended"


def local_link(url):
    """Whether plannotator's link would open only on the host it runs on, so a card's session can't use it."""
    import urllib.parse
    host = urllib.parse.urlsplit(url).hostname or ""
    return host in ("localhost", "::1") or host.startswith("127.")


def change_folder(fleet, t, unit, into):
    """A unit's whole change on its team's host, this one: in its place while it has one, else on its bolt's worktree,
    else as the kit's main holds it now, open or archived, read by ref after a fetch (MAIN, plan.18), never from the
    main checkout's files, which the fleet's timer moves minutes behind: its Markdown written into the folder into
    (change_written)."""
    k = survey(fleet, [(t["name"], None)]).get(t["machine"], {})
    kit = k.get("kits", {}).get(t["kit"]["main"], {}) if k.get("ok") else {}
    kit.get("ok") or fail(f"{t['kit']['main']} on {t['machine']} could not be read: {kit.get('error') or k.get('error')}")
    pl = kit["places"].get(unit)
    where = [f"{pl['path']}/openspec/changes/{unit}"] if pl else []
    where += [f"{w}/openspec/changes/{unit}" for w in (b["worktree"] for b in kit["bolts"].values()) if w]
    found = next((w for w in where if os.path.isdir(w)), None)
    if found:
        return found
    r = subprocess.run(["bash", "-c", MAIN, "crew", t["kit"]["main"]], capture_output=True, text=True, env=gitenv())
    r.returncode == 0 or fail(f"on {t['machine']}: " + ((r.stderr or r.stdout).strip() or f"exit {r.returncode}"))
    head, why = main_held(t["kit"]["name"], t["machine"], r.stdout)
    not why or fail(why)
    return change_written(t["kit"]["main"], head, unit, into) or fail(
        f"unit {unit}'s change is in no checkout of {t['kit']['name']} on {t['machine']}, nor on its main at {head[:7]}")


def change_held(main, ref, unit):
    """A unit's change as a checkout of its kit holds it at ref, open, else archived (gather.DATED): its Markdown files,
    [(path under the change, content)] as git holds them, or None when ref holds no change by that name."""
    out = gather.run(["git", "ls-tree", "-d", "--name-only", ref, "openspec/changes/", "openspec/changes/archive/"], main) or ""
    archive = "openspec/changes/archive/"
    held = [l for l in out.splitlines() if l == f"openspec/changes/{unit}"] or sorted(
        l for l in out.splitlines() if l.startswith(archive) and l[len(archive) + 11:] == unit and gather.DATED.fullmatch(l[len(archive):][:11]))
    if not held:
        return None
    folder = held[-1]
    return [(f[len(folder) + 1:], gather.run(["git", "show", f"{ref}:{f}"], main) or "")
            for f in (gather.run(["git", "ls-tree", "-r", "--name-only", ref, "--", f"{folder}/"], main) or "").splitlines()
            if f.endswith(".md")]


def change_written(main, ref, unit, into):
    """A unit's change as a kit's main holds it at ref, open, else archived (change_held), its Markdown files written
    into the folder into, emptied first, as git holds them: the folder, or None when main holds no change by that
    name."""
    import shutil
    files = change_held(main, ref, unit)
    if files is None:
        return None
    shutil.rmtree(into, ignore_errors=True)
    for p, text in files:
        target = pathlib.Path(into, p)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    return str(into)


def landing_write(fleet, f, folder):
    """Write a landing's reading afresh into folder, its head's, on the host of the team holding the bolt, from the
    landing's facts (land_facts): each unit's change as the kit holds it at the bolt's head, open or archived
    (change_held), and the bolt's diff against main from where it last met main (base) to its head, less
    openspec/changes/, whose Markdown the units' files show whole, named and ordered by landing_reading. Every file is
    read before any is written: what crew can't read refuses, naming it, and nothing is written (read.1). Returns the
    files' paths, in order."""
    t = crew.with_kit(fleet["teams"][f["team"]], f["kit"])
    main, head = t["kit"]["main"], f["head"]
    changes = []
    for u in f["units"]:
        held = change_held(main, head, u)
        held is not None or fail(f"unit {u}'s change is not on bolt {f['bolt']} at {head[:7]}, open or archived, in {main} on {t['machine']}")
        held or fail(f"unit {u}'s change on bolt {f['bolt']} at {head[:7]} holds no Markdown file to read")
        changes.append((u, held))
    _, diff = kit_git(fleet, t, main, "diff", "--no-color", "--no-ext-diff", f["base"], head, "--", ".", ":(exclude)openspec/changes")
    out = landing_reading(f["bolt"], f["kit"], head, f["units"], f.get("chores") or [], changes, diff + "\n" if diff else "")
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.iterdir():
        if old.is_file():
            old.unlink()
    for name, text in out:
        (folder / name).write_text(text)
    return [str(folder / name) for name, _ in out]


def change_order(path):
    """Where a file of a change, by its path under the change, comes in its reading: its proposal, design, specs in
    path order, tasks, then any other Markdown in path order."""
    return ({"proposal.md": 0, "design.md": 1, "tasks.md": 3}.get(path, 2 if path.startswith("specs/") else 4), path)


def change_files(folder):
    """A change's Markdown files in a folder on this host, each a path, in the order of its reading (change_order):
    what plannotator is given, never the folder, whose listed files the user would have to open one by one."""
    root = pathlib.Path(folder)
    found = [p.relative_to(root).as_posix() for p in root.rglob("*.md") if p.is_file()]
    return [str(root / p) for p in sorted(found, key=change_order)]


def batch_folder(label, n):
    """Batch n's own folder on the partition's main level's host, beside its summary: the files its one reading session
    opens."""
    return reviews(label) / f"batch-{label}-{n}"


# A change's Markdown files at a commit in a kit, run on the team's host: each file's path under the change, then its
# content as git holds it, each ended by NUL, which no Markdown file holds.
CHANGE_AT = r"""set -eo pipefail
main=$1 sha=$2 unit=$3
cd "$main"
git cat-file -e "$sha^{commit}" 2>/dev/null || { echo "$sha is not a commit of $main" >&2; exit 1; }
git ls-tree -r -z --name-only "$sha" -- "openspec/changes/$unit/" | while IFS= read -r -d '' p; do
  case $p in *.md) printf '%s\0' "${p#"openspec/changes/$unit/"}"; git cat-file blob "$sha:$p"; printf '\0' ;; esac
done
"""


def change_at(fleet, t, unit, sha):
    """A unit's change as read at a commit in its kit's main checkout on its team's host, over ssh when that host is
    another (code.3), as the reviewer reads it (reading_command): its Markdown files, [(path under the change,
    content)], in the order of its reading. Refused naming the unit, the host and what failed (read.1)."""
    r = crew.on_machine(fleet, t["machine"], ["bash", "-c", CHANGE_AT, "crew", t["kit"]["main"], sha, unit])
    why = unread_change(t, unit, sha, r.returncode, r.stderr)
    not why or fail(why)
    parts = r.stdout.split("\0")
    files = sorted(zip(parts[0:-1:2], parts[1::2]), key=lambda f: change_order(f[0]))
    return files or fail(f"{unit}'s change at {sha} in {t['kit']['main']} on {t['machine']} holds no Markdown file")


def unread_change(t, unit, sha, code, stderr):
    """Why a batch can't be read whole, from CHANGE_AT's exit on the unit's team's host (read.1): the host did not
    answer, naming it, or the change could not be read at its commit, naming the unit, the commit and the host."""
    said = ((stderr or "").strip().splitlines() or [f"exit {code}"])[-1]
    if code == 255:
        return f"crew can't read {unit}'s change: {t['machine']}, {t['name']}'s host, did not answer ({said})"
    return f"crew can't read {unit}'s change at {sha} in {t['kit']['main']} on {t['machine']}: {said}" if code else None


def batch_folder_write(fleet, label, n, units):
    """Write batch n's folder afresh, on the main level's host, from the batch the run record holds, its units in the
    batch's order as (unit, team, the commit the batch read it at): 00-summary.md, the reviewer's summary as written,
    then for the k-th unit each Markdown file of its change at that commit, named <kk>-<unit>-<its path under the
    change, / as ->, so each file plannotator shows by its name alone names its unit. Every file is read before any is
    written: what crew can't read refuses, naming it, and nothing is written (read.1). Returns the files' paths, in that
    order."""
    f = batch_file(label, n)
    try:
        summary = f.read_text()
    except OSError as e:
        fail(f"crew can't read batch {n}'s summary {f}: {e.strerror or e}")
    out = [("00-summary.md", summary)]
    for k, (u, team, sha) in enumerate(units, 1):
        t = unit_kit_team(fleet, label, fleet["teams"].get(team) or fail(f"{u}'s team {team} is not in the teams file"), u)
        out += [(f"{k:02d}-{u}-{p.replace('/', '-')}", text) for p, text in change_at(fleet, t, u, sha)]
    folder = batch_folder(label, n)
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.iterdir():
        if old.is_file() and re.fullmatch(r"\d{2}-.+\.md", old.name):
            old.unlink()
    for name, text in out:
        (folder / name).write_text(text)
    return [str(folder / name) for name, _ in out]


def landing_reading(bolt, kit, head, units, chores, changes, diff):
    """A landing's reading, the files its one session opens as one review, in order, each (name, text) (card-sessions,
    briefs.9): 00-<bolt>.md, a page naming the bolt, its kit and its head, the units and chores that land, one a line,
    and saying that the reading lands nothing, approving the card being the word to land, and that what the user sends
    from it reaches the bolt's conductor as notes on the card, a note naming a defect holding the landing for a fix;
    then for the k-th unit each Markdown file of its change as the head holds it, named <kk>-<unit>-<its path under the
    change, / as ->, in a change's reading order (change_order), as a batch's folder names them; then
    <nn>-<bolt>-diff.txt, the bolt's diff against main, numbered after the last unit, as text, which plannotator opens
    beside Markdown in one review where it refuses a .diff (plannotator 0.28.23). changes: [(unit, [(path under the
    change, text)])] in the plan's order; diff: the diff's text."""
    cover = "\n".join([f"# Bolt {bolt}, landing on {kit}'s main", "", f"What lands, at its head {head[:7]}:", ""]
                      + [f"- {u}" for u in units] + [f"- {c} (chore)" for c in chores]
                      + ["", "This reading lands nothing: approving the landing card is the word to land, and its Approve "
                             "here lands nothing.", "",
                         "What you send from it reaches the bolt's conductor as notes on the landing card, and a note "
                         "naming a defect holds the landing for a fix.", "",
                         "After this page come each unit's change as the bolt holds it, then what the bolt changes against "
                         "main, from where it last met main to its head, less its change folders, shown whole before it."])
    out = [(f"00-{bolt}.md", cover + "\n")]
    for k, (u, files) in enumerate(changes, 1):
        out += [(f"{k:02d}-{u}-{p.replace('/', '-')}", text) for p, text in sorted(files, key=lambda f: change_order(f[0]))]
    said = diff if diff.strip() else "The bolt changes nothing against main outside its change folders.\n"
    return out + [(f"{len(changes) + 1:02d}-{bolt}-diff.txt", said)]


def forward_card(fleet, t, a, label):
    """An old batch card's command for one of its units, run on the host the teams file names for that unit's team
    (code.3), as the one asking here; its output passed on, and its failure this command's."""
    r = crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], "card", a.sub, a.key, a.unit, "--label", label))
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode:
        sys.exit(r.returncode)


def batch_team(fleet, label, key, unit):
    """The team of a unit a batch card holds, from the batch in the run record, whether or not the card is still open:
    every unit of the batch for batch/<n>, the k-th five for batch/<n>-<k>."""
    n = int(key.split("/")[1].split("-")[0])
    entries = partition_entries(fleet, label)
    for m, _, units in batches(entries):
        if m == n:
            part = card_part(key, units)
            names = [u for u, *_ in part]
            names or fail(f"batch {n} of {label} has no card {key.partition('-')[2]}")
            team = next((tm for u, tm, _ in part if u == unit), None) or fail(f"{key} holds {either(names)}, not {unit}")
            return unit_kit_team(fleet, label, fleet["teams"].get(team) or fail(f"{unit}'s team {team} is not in the teams file"), unit)
    fail(f"{label}'s run record holds no batch {n}")


def card_wait(fleet, a):
    """crew card wait <key> [<unit>] [--label L]: wait, with no timeout, until the user decides in the session crew
    started for the key on this host, or it ends without a decision, and print which: approved or annotated with the
    user's words after it as they are, closed in plannotator with no decision, or ended with no decision; a decision
    made before the wait began is printed at once. A session crew ended, its card closed, is said so. A batch card's,
    batch/<n>, waits on the card and its one session together, on the main level's host (batch_wait); an old batch
    card's, batch/<n>-<k>, takes a unit and is waited on at that unit's team's host. A landing's, land/<bolt>, waits on
    its reading alone, on the team's host: its decision is notes on the bolt's row of its kit's landings card and never
    the word to land (land_waited), and once it is printed the session is forgotten (reading_decided), so the next crew
    card session starts it anew; the card is left as it is. The reading stays up while the bolt is a row of that card,
    until the row is held or leaves it (land_end) or crew card end is run, and no close of a card of the bolt's own,
    land/<bolt> or land/<bolt>/<head> as its conductor posted one before, ends it (row_card_close, sweep_judgment).
    With no session of its own while the bolt is a row, the raise having failed to open it or a wait having forgotten
    it, it starts the reading as crew card session does and waits on it (land_start). Refused for any other key with no
    session started."""
    label, d = card_of(fleet, a)
    if a.key.startswith("batch/") and not old_batch(a.key):
        return batch_wait(fleet, label, a.key, d)
    if a.unit:
        t = batch_team(fleet, label, a.key, a.unit)
        if t["machine"] != crew.this_host():
            return forward_card(fleet, t, a, label)
    name = f"{a.key} {a.unit}" if a.unit else a.key
    say = land_waited if a.key.startswith("land/") else waited
    kind = land_key(a.key, partition_kits(fleet, label))
    if kind and kind[0] == "kit":
        fail(session_refusal(a.key, label, fleet["partitions"][label]["machine"], crew.this_host(), None, partition_kits(fleet, label)))
    if say is land_waited and not card_recorded(d):
        land_start(fleet, label, a.key)
    card_recorded(d) or fail(f"no session was started for card {name}: crew card session {name} starts one")
    while True:
        decided = card_result(d)
        said = say(name, decided, True)
        if not said:
            s = card_recorded(d)
            if s is None:
                said = say(name, None, False)
            else:
                listed, _ = plannotator_sessions()  # a list that can't be read says nothing: the wait goes on
                decided = card_result(d)
                said = say(name, decided, card_recorded(d) == s, gone=listed is not None and not serving(listed, s))
        if said:
            print(said)
            if say is land_waited:
                reading_decided(d, decided)
            return
        time.sleep(CARD_POLL)


def land_unstarted(key, recorded, held, refused=None):
    """What crew card wait land/<bolt> does before it waits (card-sessions "A wait on a landing card starts its reading
    when none runs"), from whether a session of the key is recorded on this host, whether the bolt is a row of its kit's
    landings card that can land (held, land_read), and why the start it made refused (refused): ("wait", None) on a
    session recorded; ("start", None) with none and the bolt a row, to start it as crew card session does; ("refuse",
    words) when the start refused, naming crew card session to start it once that is mended, or the bolt is no row."""
    if recorded:
        return "wait", None
    if not held:
        return "refuse", f"no session was started for card {key}, and {key.split('/', 1)[1]} is no row of its kit's landings card"
    if refused:
        return "refuse", f"{key}'s reading could not be opened: {refused}; crew card session {key} starts it once that is mended"
    return "start", None


def land_start(fleet, label, key, acts=None):
    """A landing's reading started for its wait when none is recorded (land_unstarted): while the bolt is a row of its
    kit's landings card that can land, read on this, its team's, host (land_read), opened as crew card session opens it,
    its link printed and the kit's card changed in place to carry it while it waits on the user (land_session); refused
    naming why and crew card session when it could not open, and when the bolt is no such row."""
    acts = acts or CardActs(fleet)
    plan, b, t = land_held(fleet, label, key.split("/", 1)[1])
    held = False
    if t and t["machine"] == acts.host():
        try:
            row, _ = land_read(fleet, label, plan, b, t)
            held = bool(row and row["box"])
        except Refusal:
            held = False
    step, words = land_unstarted(key, False, held)
    if step == "start":
        try:
            land_session(fleet, label, key, acts)
        except Refusal as e:
            step, words = land_unstarted(key, False, held, str(e))
    not words or fail(words)


def batch_unstarted(key, recorded, held, refused=None, answered=False):
    """What crew card wait batch/<n> does before it waits (card-sessions "A batch's wait starts its reading when none
    runs"), from whether a session of the key is recorded on this host, whether the planner holds its card open here
    (held), why the start it made refused (refused), and whether the batch is answered in a main-level pane already
    (answered, pane_answered): ("wait", None) with a session recorded, or no card held, which the wait refuses when
    neither is there, or the batch answered so, since it waits on the user no more and the wait ends on its answer;
    ("start", None) with none and the card held, to start it as crew card session does; ("card", words) when the start
    refused, to say once, naming crew card session, and wait on the card alone, which the user sends back with a tap."""
    if recorded or not held or answered:
        return "wait", None
    if refused:
        return "card", (f"{key}'s reading could not be opened: {refused}; crew card session {key} starts it once that is "
                        "mended, and the wait goes on for its card")
    return "start", None


CARD_READ = 30  # seconds between a batch wait's reads of its card in Pending You, the poll its post's answer asks for
OPEN = ("pending", "snoozed", "delegated")  # a card's statuses in Pending You while it still waits on the user


def batch_wait(fleet, label, key, d, acts=None):
    """crew card wait batch/<n>: wait, with no timeout, on the planner's card of the batch and its one reading session
    together, on the main level's host, until the user sends either back: the card read in Pending You every CARD_READ
    seconds, the session's result every CARD_POLL. It prints what batch_waited gives, the card's note and every
    annotation as the user wrote them, and closes the card with the outcome, which ends the session (row_card_close); a
    word given while nobody waited is returned at once. A session sent with no card held on this host, or one lost or
    whose close Pending You refused, so that no card is closed, records the batch read: crew's own close of it,
    batch.close on batch/<n> in the planner's name with what was read (batch_read_close, briefs.12), the session
    ended when no card was held. A card closed outside crew is recorded closed as Pending You shows it, and the session
    ended. A batch answered in a main-level pane (pane_answered), read in this host's run record each round before the
    card, ends the wait, saying in whose pane and when and never the words, which the planner has from crew card
    answer: its card is closed answered and the session ended. A session closed or ended with no decision leaves the
    wait on the card, said once; a card lost to its owner is recorded lost, leaving the wait on the session; a session
    crew ended, as its card closed, ends the wait. With the card held and no session recorded, the reading is started
    first, as crew card session starts it, its link printed and the card changed to carry it (reading_again); one that
    will not open is said once, naming crew card session, and the wait is on the card alone (batch_unstarted). Refused
    with neither a card nor a session of the batch on this host."""
    acts = acts or CardActs(fleet)
    here = acts.host()
    why = session_refusal(key, label, fleet["partitions"][label]["machine"], here)
    not why or fail(why)
    owner, entries = f"{label}-planner", acts.entries(label)
    card, started = cards.card_under(entries, key, owner), card_recorded(d)
    card or started or fail(f"no card and no session of {key} is open on {here}: crew raises both when the reviewer's "
                            f"summary is delivered, with crew review {label} --wait")
    if batch_unstarted(key, started, card, answered=key in pane_answered(entries))[0] == "start":
        try:
            reading_again(fleet, label, key, acts, lambda url, decided: print(url))
        except Refusal as e:
            print(batch_unstarted(key, started, card, str(e))[1], file=sys.stderr)
        else:
            started = card_recorded(d)
    got, due, said, quiet = None, 0.0, set(), False

    def once(words):
        if words not in said:
            said.add(words)
            print(words, file=sys.stderr)
    while True:
        answer = pane_answered(acts.entries(label)).get(key)
        if answer:  # the user answered it in a main-level pane, whose agent sends the words on (crew card answer)
            said = pane_said(*answer)
            print(f"{key}: {said}")
            row_card_close(fleet, label, owner, key, outcome=said[0].upper() + said[1:], acts=acts)
            ended = acts.end(label, key)  # a close Pending You refused leaves the session to end here
            if ended:
                print(ended)
            return
        s, decided = card_recorded(d), card_result(d)
        if card and time.monotonic() >= due:
            due = time.monotonic() + CARD_READ
            try:
                with acts.bridge(owner, "The wait goes on.") as py:
                    got, words = py.answer("get_request", {"requestId": card, "name": owner})
            except Refusal as e:
                once(f"{key}: crew can't read its card {card} now: {e}")
            else:
                if words is not None and cards.lost(words):
                    card_lost(acts, label, owner, key, card, words)
                    card, got = None, None
                elif words is not None:
                    once(f"{key}: Pending You refused to read its card {card}: {words}")
        done = batch_waited(key, decided, got)
        if done:
            print(done[1])
            if done[0] == "read":
                closed = row_card_close(fleet, label, owner, key, outcome=done[2], acts=acts) if card else None
                if batch_read_close(closed):
                    acts.emit(label, "batch.close", [cards.row_object(key) or key], by=owner,
                              why=f"batch({key.split('/', 1)[1]}): read in its session", Key=key, State="read", Outcome=done[2])
                    print(f"{key}: recorded read, {done[2]}")
                if card:
                    return
            elif done[0] == "closed":
                acts.emit(label, "card.close", [cards.row_object(key)], by=owner, Card=card, Key=key, State=done[2],
                          Outcome="closed outside crew", Answer=cards.answer_said(got))
            print(acts.end(label, key) or f"no session was running for {key}")
            return
        if started and s is None:
            print(waited(key, None, False))
            return
        ended = None
        if decided and decided[0] == "dismissed":
            ended = waited(key, decided, True)
        elif s and not decided and not quiet:
            listed, _ = plannotator_sessions()  # a list that can't be read says nothing: the wait goes on
            if listed is not None and not serving(listed, s) and card_recorded(d) == s and card_result(d) is None:
                ended = waited(key, None, True, gone=True)
        if ended and not card:
            print(ended)
            return
        if ended:
            quiet = True
            once(f"{ended}: the wait goes on for its card, which the user sends back with a tap; crew card session {key} "
                 "starts its reading again")
        if not card and not s:
            print(f"{key}: its card is lost to {owner}, and it has no session to wait on")
            return
        time.sleep(CARD_POLL)


def batch_read_close(closed):
    """Whether a batch whose reading the user sent is recorded read by crew's own close of it (review-batches, briefs.12):
    when no card of it was closed, closed being what row_card_close gave, the card's id or None, or None when no card
    was held, so the user's word holds the batch's landings no longer whatever became of the card."""
    return closed is None


def batch_waited(key, decided, got):
    """What a wait on a batch's card and its session does once either has the user's word (review-batches): ("read",
    what it prints, the card's outcome) once the card is sent back, its note after it as the user wrote it, or the
    session sent, approved or annotated with every annotation as written, or both; ("closed", what it prints, the
    card's status) when Pending You shows the card closed outside crew; None while neither has, the session closed or
    ended undecided among them. decided is the session's result (card_result), got the card as get_request gives it,
    each None when there is none."""
    answer = got.get("answer") if isinstance(got, dict) and got.get("turn") == "agent" else None
    answer = answer if isinstance(answer, dict) else None
    status = got.get("status") if isinstance(got, dict) and isinstance(got.get("status"), str) else None
    sent = decided if decided and decided[0] in ("approved", "annotated") else None
    if answer is None and not sent:
        if status and status not in OPEN and status != "answered":
            return "closed", f"{key}: its card was closed outside crew; Pending You shows it {status}", status
        return None
    lines, notes = [], 0
    if answer is not None:
        note = cards.text_of(answer.get("note")) or cards.text_of(answer.get("text"))
        lines.append(f"{key}: sent back on its card" + (f", with a note:\n{note}" if note else ", with no note"))
        notes += 1 if note else 0
    if sent:
        lines.append(waited(key, sent, True))
        k = sent[2] if len(sent) > 2 else None
        notes = None if k is None and sent[1] else notes + (k if k is not None else 0)
    return "read", "\n".join(lines), read_outcome(notes)


def read_outcome(notes):
    """A batch card's close once the user has read the batch (review-batches): with no notes, or the notes that go to
    the units' teams, counted when crew can count them (None when it cannot)."""
    if notes == 0:
        return "Read; no notes"
    if notes is None:
        return "Read; its notes sent to their teams"
    return f"Read; {notes} note{'' if notes == 1 else 's'} sent to {'its team' if notes == 1 else 'their teams'}"


def waited(name, decided, recorded, gone=False):
    """What a wait on a key's session says once it ends: the user's decision, approved or annotated with their words
    after it as they are, or closed in plannotator with no decision; that crew ended the session (no longer recorded);
    or that it ended with no decision (gone: plannotator lists it serving nothing). None while it runs undecided."""
    if decided:
        said = {"approved": "approved", "annotated": "annotated", "dismissed": "closed in plannotator with no decision"}[decided[0]]
        return f"{name}: {said}" + (f"\n{decided[1].rstrip(chr(10))}" if decided[1] else "")
    if not recorded:
        return f"{name}: crew ended its session, as its card closed or crew card end was run"
    return f"{name}: the session ended with no decision" if gone else None


def land_waited(name, decided, recorded, gone=False):
    """What a wait on a landing's reading says once it ends (card-sessions, briefs.9): its annotations, with the user's
    words as plannotator gives them, as notes on the landing card; an approval, with any words after it, as landing
    nothing, the card's approval being the word to land; a reading crew ended (no longer recorded) as ended with its
    row or by crew card end, which no card's close does (row_card_close); anything else as waited says it. None while
    it runs undecided."""
    words = f"\n{decided[1].rstrip(chr(10))}" if decided and decided[1] else ""
    if decided and decided[0] == "annotated":
        return f"{name}: notes from its reading, as notes on the landing card:" + words
    if decided and decided[0] == "approved":
        return f"{name}: approved in its reading, which lands nothing: the card's approval is the word to land" + words
    if not decided and not recorded:
        return f"{name}: crew ended its reading, as its row was held or left its kit's landings card, or crew card end was run"
    return waited(name, decided, recorded, gone)


def reading_decided(d, decided):
    """A landing's reading once its wait printed the user's decision (card-sessions): an approval or annotations set
    aside, as result.<started>.json, and the session forgotten, plannotator having ended with the decision, so the next
    crew card session starts it anew and changes the card's link, and the next wait waits on that one. Anything else,
    and a session crew ended meanwhile, is left as it is."""
    if not decided or decided[0] not in ("approved", "annotated"):
        return
    try:
        lock = open(d / ".lock", "w")
    except FileNotFoundError:
        return  # crew ended the session, its card closed, while the wait printed
    with lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        s = card_recorded(d)
        if s and (d / "result.json").exists():
            (d / "result.json").rename(d / f"result.{re.sub(r'[-:]', '', s['started'])}.json")
            (d / "session.json").unlink()


def end_session(label, key, unit=None):
    """End the plannotator session crew started for a card key on this host, an old batch card's (batch/<n>-<k>) for
    one of its units, and forget it: its folder goes first, so a wait on it hears crew ended it, then the recorded pid is sent SIGTERM only
    while plannotator lists it as serving the recorded document (read.4). When plannotator's list can't be read, nothing
    is ended and the session is kept as recorded, so a later rail read ends it (read.1). The answers crew plan answer
    gathered for a proposal's card stay, and with them their folder: they go only with the approval or the decline.
    Returns what it did, in words, and whether it sent SIGTERM. crew's card hook runs it when a crew agent closes or
    withdraws a keyed card, the act when crew closes or withdraws one of its own (row_card_close), and crew card sweep
    for each session the rail judges dead. A session that ended as the user sent it is forgotten, said so. A folder or
    file of the key's that another of these ends swept first, while this one read plannotator's list, is swept as
    empty, never raised, so a wait whose card's close ends the session returns."""
    any(re.fullmatch(k, key) for k in CARD_KEYS) or fail(f"{key} is not a card key")
    d = CARDS / label / key / unit if unit else CARDS / label / key
    key = f"{key} {unit}" if unit else key
    if not d.is_dir():
        return f"no session was running for {key}", False
    try:
        s = card_recorded(d)
    except Refusal:
        s = None
    try:
        decided = card_result(d)
    except Refusal:
        decided = None
    listed, why = plannotator_sessions() if s else (None, None)
    import shutil
    if s and listed is None:
        return end_said(key, s, None, why), False
    try:
        left = list(d.iterdir())
    except FileNotFoundError:
        left = []  # another end swept it first
    for f in left:
        if f.name != "answers.json":
            try:
                shutil.rmtree(f) if f.is_dir() and not f.is_symlink() else f.unlink()
            except FileNotFoundError:
                pass  # another end swept it first
    for p in [d, *d.parents]:
        if p == CARDS / label:
            break
        try:
            if any(p.iterdir()):
                break
            p.rmdir()
        except FileNotFoundError:
            continue  # another end swept it first: swept as empty
        except NotADirectoryError:
            break
    if s and decided and decided[0] != "dismissed" and not serving(listed, s):
        return f"{key}'s session had ended as the user sent it, and {key} is forgotten", False
    if not s or not serving(listed, s):
        return end_said(key, s, listed, why), False
    try:
        os.kill(s["pid"], SIGTERM)
    except ProcessLookupError:
        return f"{key}'s session had already ended, and {key} is forgotten", False
    return f"ended {key}'s session, plannotator pid {s['pid']}", True


def end_said(key, s, listed, why):
    """What crew card end says when it ends nothing (read.1, read.4): plannotator's list could not be read (listed
    None), so the session recorded (s) is kept; none was recorded, so only the key's folder goes; or plannotator lists
    the recorded pid on no session of the recorded document, so nothing is killed and the key is forgotten."""
    if s and listed is None:
        return f"crew can't read plannotator's sessions ({why}): it ended nothing, and keeps {key} to end later"
    if not s:
        return f"no session was recorded for {key}; its folder is removed"
    return f"plannotator lists no session of pid {s['pid']} on {s['document']}: crew ended nothing, and {key} is forgotten"


def card_end(fleet, a):
    """crew card end <key> [<unit>] [--label L]: end the session crew started for a card key on this host, and forget
    the key: a batch card's, batch/<n>, its one session; an old batch card's, batch/<n>-<k>, for one of its units on
    that unit's team's host, or with no unit for each of its units, as its close does."""
    label, _ = card_of(fleet, a, unit_needed=False)
    if not old_batch(a.key):
        print(end_session(label, a.key)[0])
        return
    names = [a.unit] if a.unit else card_units(fleet, label, a.key)
    for u in names:
        t = batch_team(fleet, label, a.key, u)
        if t["machine"] != crew.this_host():
            forward_card(fleet, t, argparse.Namespace(**dict(vars(a), unit=u)), label)
        else:
            print(end_session(label, a.key, u)[0])


def card_asker(fleet, a):
    """The partition and the asker of a crew card read (briefs.16): --label, else the agent's own; the asker the agent
    crew started, else the user at this host. An agent's label is its own."""
    agent, own = os.environ.get("CREW_AGENT"), os.environ.get("CREW_LABEL")
    not (agent and own and a.label and a.label != own) or fail(
        f"{agent}'s cards are {own}'s: crew card {a.sub} runs as the agent's own partition")
    label = default_label(fleet, a) or fail(f"crew card {a.sub} runs as the card's partition: run it as a crew agent, or add --label")
    if agent:
        os.environ["CREW_LABEL"] = label
    return label, record.who()


def card_held(label, who, key):
    """The card `who` holds under a key on this host, read from its run record; refused when there is none."""
    import cards
    return cards.card_under(cards.host_entries(record, label, crew.this_host()), key, who) or fail(
        f"{who} holds no open card under {key} on {crew.this_host()}")


def landing_lines(label, got, heads, earlier=(), unknown=(), stopped=None):
    """What crew card read land/<kit> prints beside the answer once the user sent the kit's landings card (rail-cards
    "An answer wakes the owner"): the bolts they ticked in the card's order (ticked_of, heads its rows as card_heads
    gives them), and the one crew bolt submit that lands them in that order, or that none was ticked, so nothing lands;
    nothing while it waits on them, nor with no card open (got {}, heads []). The bolts an earlier send still lands
    (earlier, sent_left), its card closed, come first, said while this one waits too or with none open, and the submit
    lands them before this card's; each sent bolt crew can't tell of (unknown, [(bolt, why)]) is said, and left out of
    it (main-level "Ops lands a bolt on a send that still stands"). Each of them whose last landing sluice or its host
    stopped (stopped, {bolt: (head, words)}, stops) is said with what stopped it and the head it was at, the same
    submit landing it once that is cleared (rail-cards "Checks that never ran")."""
    ticked, earlier, stopped = ticked_of(got, heads), list(earlier), stopped or {}
    lines = [f"  can't tell whether the user's earlier send still lands {b}: {why}" for b, why in unknown]
    lines += [f"  to land on the user's send of an earlier card: {joined(earlier)}"] if earlier else []
    if ticked == []:
        lines += ["  no bolt ticked on this card: nothing of it lands" if earlier else "  no bolt ticked: nothing lands"]
    elif ticked:
        lines += [f"  to land, in the card's order: {joined(ticked)}"]
    both = earlier + (ticked or [])
    lines += [f"  {b}'s last landing at {stopped[b][0][:7]} was stopped, nothing of the bolt's: {stopped[b][1].rstrip('.')}; "
              "once that is cleared, the submit below lands it on the user's send" for b in both if b in stopped]
    return lines + ([f"  lands them: crew bolt submit {' '.join(both)} --label {label}"] if both else [])


def landings_earlier(fleet, label, kit, key, who, entries, heads, acts=None):
    """The bolts an earlier send on a kit's landings card still lands beside the card who holds under key now, if any
    (heads its rows, [] for none), from this host's run record (entries), where ops's closes and submissions are
    (landings_sent, refusals), the partition's plan, read only when such a send stands, and each sent bolt's head now
    and its own work since the send, read by one acts.work where the kit's forecasts are made (bolt_work): (bolts,
    [(bolt, why)]) as sent_left gives them, a bolt on a row of the card read now being that card's to ask for. Refused
    naming the plan when it can't be read, since what the send still lands can't be told without it (read.1)."""
    on = {b for b, _, _ in heads}
    sent = {b: h for b, h in landings_sent(entries, key, who).items() if b not in on}
    if not sent:
        return [], []
    plan = plan_of(fleet, label) or fail(f"{label}/main could not be read, so what an earlier send on {key} still lands can't be told")
    in_plan = {b.name() for b in plan.bolts() if b.get("Repo") == kit}
    moves = {b: (h, None) for b, h in sent.items() if b in in_plan}
    work = (acts or CardActs(fleet)).work(label, kit, moves) if moves else {}
    return sent_left(sent, {b: (work.get(b) or {}).get("head") for b in moves}, in_plan, refusals(entries), work)


def landings_unopened(fleet, a, label, who, kit, entries, acts=None):
    """crew card read land/<kit> when who holds no landings card of the kit open (main-level "Ops lands a bolt on a
    send that still stands"): that no card is open, then what an earlier send still lands at each bolt's head now and
    the crew bolt submit that lands it, and each bolt crew can't tell of, left out of it (landings_earlier,
    landing_lines); with --json, the same as {key, card: null, earlier, unknown}. Refuses nothing but what it can't read
    (read.1)."""
    earlier, unknown = landings_earlier(fleet, label, kit, a.key, who, entries, [], acts)
    if a.json:
        print(json.dumps(dict(key=a.key, card=None, earlier=earlier, unknown=dict(unknown)), indent=1, ensure_ascii=False))
        return
    print("\n".join([f"card {a.key}: no landings card of {kit} is open"] + landing_lines(label, {}, [], earlier, unknown,
                                                                                          stops(entries))))


def card_read(fleet, a):
    """crew card read <key> [--label L] [--json]: where the card the asker holds under the key stands, read from
    Pending You: its status, whose turn it is, and on the asker's turn the user's answer and words; for a kit's
    landings card, land/<kit>, the bolts they ticked in the card's order and the crew bolt submit that lands them,
    those an earlier send still lands, whose card closed as this one followed it, first (landings_earlier,
    landing_lines), each whose last landing sluice or its host stopped said with what stopped it (stops), and with no
    card of the kit open, those alone (landings_unopened). An approval the user declined is then closed with their
    words, and the close recorded (record 0031 §1), with what they answered in crew's words (cards.answer_said);
    nothing else is."""
    import cards
    label, who = card_asker(fleet, a)
    kind = land_key(a.key, partition_kits(fleet, label))
    if kind and kind[0] == "kit":
        entries = cards.host_entries(record, label, crew.this_host())
        if not cards.card_under(entries, a.key, who):
            return landings_unopened(fleet, a, label, who, kind[1], entries)
    card = card_held(label, who, a.key)
    with cards.Bridge(who, "Read it again later.", (a.key, card)) as py:
        got = py.call("get_request", {"requestId": card, "name": who})
        words = cards.declined(got)
        if words is not None:
            tool, args, _ = cards.close_call(got, card, who, cards.declined_outcome(words))
            py.call(tool, args)
    if a.json:
        print(json.dumps(got, indent=1, ensure_ascii=False))
    else:
        entries = cards.host_entries(record, label, crew.this_host()) if kind and kind[0] == "kit" else []
        heads = card_heads(next((e.get("Heads") for e in reversed(entries) if e.get("Card") == card and e.get("Heads")
                                 and not e.get("Refused")), None))
        earlier, unknown = landings_earlier(fleet, label, kind[1], a.key, who, entries, heads) if kind and kind[0] == "kit" else ([], [])
        print("\n".join(cards.answer_lines(a.key, card, got)
                        + (landing_lines(label, got, heads, earlier, unknown, stops(entries)) if kind and kind[0] == "kit" else [])))
    if words is not None:
        record.emit(label, "card.close", [cards.row_object(a.key, partition_kits(fleet, label)) or f"agent/{who}"], Card=card,
                    Key=a.key, State="declined", Outcome=cards.declined_outcome(words), Answer=cards.answer_said(got))
        print(f"card {a.key}: {card} closed, as the user declined it")


# ------------------------------------------------------------------------------------- a batch answered in a pane

ANSWERERS = ("planner", "operator")  # the main-level roles in whose pane the user answers a batch (briefs.12)


def pane_answer_refusal(n, entries, v, kind):
    """Why crew card answer records no answer of batch n (review-batches, briefs.12), or None: the caller is not the
    partition's planner or operator, whose kind it is (role); the run record's entries, oldest first, hold no batch n;
    a card key of it is closed (batch_closed), by a tap, its reading session's send or a pane, naming in whose pane and
    when for a pane's (pane_answered); every card of it waits on nothing (batch_settled); or the verdict v on the words
    in the caller's own transcript (transcript.check, want="user") does not read them as the user's (signals.5), naming
    who said them. A decision of facts alone (code.7)."""
    head = f"crew records no answer of batch {n}"
    if kind not in ANSWERERS:
        return (f"{head}: only the planner and the operator record a batch the user answered in their pane, in the "
                "user's own words; the user answers a batch on its card or in one of those two panes")
    made = [units for m, _, units in batches(entries) if m == n]
    if not made:
        return f"{head}: the run record holds no batch {n}"
    keys = [k for k, _ in batch_cards(n, made[-1], batch_posts(entries))]
    closed, answered = batch_closed(entries), pane_answered(entries)
    done = [k for k in keys if k in closed]
    if done:
        how = pane_said(*answered[done[0]]) if done[0] in answered else "answered on its card or in its reading session"
        return f"{head}: batch {n} was {how} already"
    settled = batch_settled(entries)
    if all(k in settled for k in keys):
        return f"{head}: {settled[keys[0]]}"
    return words_refusal(head, v, "answer a batch", "the user answers a batch on its card or in your pane")


def words_refusal(head, v, what, advice):
    """Why crew takes no words the user said in the caller's pane to what, after head, or None: the verdict v on the
    words in the caller's own transcript (transcript.check, want="user") reads them as the user's (signals.5), and not
    only in a word from the board, which answers nothing (record 0038 §3, record 0010), so the caller is given advice;
    else why not, naming who said them, and for another agent's tell, telling the caller to tell that agent advice. A
    decision of facts alone (code.7)."""
    if v.grade == "verified" and v.asserted_by == "user" and v.board:
        return f"{head}: the words came from the board, which answers nothing; {advice}"
    if v.grade == "verified" and v.asserted_by == "user":
        return None
    if v.grade == "unverified":
        return f"{head}: crew can't read your session's transcript, so it can't tell the words are the user's: {v.reason}"
    if v.grade == "refused":
        return (f"{head}: the words are not in a record your session received; only the user's own words {what}, "
                "quoted as they wrote them in your pane, never your own")
    if v.grade == "found":
        return f"{head}: the words are in a record of your transcript crew can't read as anyone's, so it can't tell they are the user's"
    if v.asserted_by.startswith("agent:"):
        other = v.asserted_by[6:]
        return f"{head}: the words are {other}'s, passed on with crew tell, and not the user's; tell {other} that {advice}"
    return f"{head}: the words are " + ("crew's own message" if v.asserted_by == "crew" else "a tool's output") + ", not the user's"


def settled_refusal(n, kit, v):
    """Why crew record <kit> <n> --proposed --settled-in-pane records no record settled in the pane (briefs.15,
    signals.5), or None: the verdict v on the user's yes in the caller's own transcript (words_refusal) does not read
    the words as the user's. No caller is refused by who it is (roles.2): the record names who ran it and in which
    session. Each refusal sends the record to its card. A decision of facts alone (code.7)."""
    head = f"crew records record {n:04d} in {kit} as settled in no pane"
    why = words_refusal(head, v, "settle a record", "the user settles a record in your pane or on its card")
    return why and f"{why}; run crew record {kit} {n} --proposed without --settled-in-pane, and the user answers on its card"


def answer_said(n, by, words):
    """What crew card answer tells the planner when the operator recorded the answer (review-batches, "Notes reach the
    unit's conductor"): the batch, whose pane, and the user's words whole, to send on as a batch's notes."""
    return (f'Batch {n} was answered in {by}\'s pane: "{words}". Send each unit\'s part to its conductor, as you send a '
            "batch's notes.")


def batch_answer(fleet, a, acts=None):
    """crew card answer batch/<n> --excerpt "<words>" [--label L]: the user's answer to batch n in their own words in
    the caller's pane, the planner's or the operator's, recorded once crew reads the words in the caller's own session
    transcript on this host as the user's (pane_answer_refusal). Run on this host, never forwarded, since the
    transcript is here. One batch.answer entry on batch/<n>, naming the batch, the transcript record the words were
    read from and their length, never the words (record.3); then the planner's card of the batch held on this host
    closed answered with the words, its reading session ended with it (row_card_close), or, with none held here, the
    host the card was posted from named, whose rail's sweep closes it; and, when the operator ran it, the planner told
    the words, crew's tell, to send on as the batch's notes. Refused for any key but batch/<n>."""
    acts = acts or CardActs(fleet)
    m = re.fullmatch(r"batch/(\d+)", a.key or "") or fail(
        f"crew card answer records a batch's answer, under its key batch/<n>, not {a.key}")
    n, key, words = int(m.group(1)), a.key, a.excerpt
    words.strip() or fail("crew card answer needs the user's words: --excerpt \"<their words, as they wrote them>\"")
    who = acts.caller()
    kind, label = role(fleet, who)
    entries, v, sid = [], None, None
    if kind in ANSWERERS:
        a.label in (None, label) or fail(f"{who} answers {label}'s batches, not {a.label}'s")
        CONTEXT["label"] = label
        v, sid = acts.heard(words)
        entries = acts.partition(label)
    why = pane_answer_refusal(n, entries, v, kind)
    not why or fail(why)
    rid = v.uuid or f"line-{v.line_hash()[:16]}"
    acts.emit(label, "batch.answer", [key], frm=[f"session/{sid}/{rid}"], Key=key, Batch=str(n), Chars=len(words))
    print(f"batch {n} answered in {who}'s pane" + (f":\n{words}" if kind == "planner" else ""))
    owner, here = f"{label}-planner", acts.host()
    held = cards.card_under(acts.entries(label), key, owner)
    row_card_close(fleet, label, owner, key, outcome=f"Answered in {who}'s pane", said=f"Answered in {who}'s pane: {words}", acts=acts)
    if not held:
        posted = [e for e in entries if e.get("Act") == "card.post" and e.get("Key") == key and e.get("Card") and not e.get("Refused")]
        there = posted[-1].get("Host") if posted else None
        print(f"card {key}: its card was posted from {there}, whose rail's sweep closes it answered" if there and there != here
              else f"card {key}: no card of it is held on any host")
    if kind == "operator":
        if acts.tell(owner, answer_said(n, who, words)):
            print(f"{owner} was told the user's words, to send each unit's part to its conductor")
        else:
            print(f"crew could not tell {owner} the user's words, and batch {n} stands answered: tell {owner} them "
                  "yourself with crew tell, as the user wrote them")


# ----------------------------------------------------------------------------------------- a landing's preview

# crew's record of the preview it asked sluice for at a bolt's head with its landing card (rail-cards, record 0031 §3),
# on the team's host, ~/.local/state/crew/previews/<label>/<bolt>.json, apart from the card's folder, which its reading
# session's end empties: the head, the kit's main checkout it runs in (main), when it was asked (asked, UTC), the handed
# process's pid, the preview's name once sluice names it, what the card was raised with (shown, "addresses" or
# "reason"), and how it ended (outcome, {state: "up" or "failed", why}); the handed process's output in <bolt>.log.
PREVIEWS = pathlib.Path.home() / ".local/state/crew/previews"
PREVIEW_START = 20  # seconds a landing card's raise waits for sluice to name its preview's addresses
PREVIEW_POLL = 0.5  # seconds between that wait's reads of sluice's previews


def preview_path(label, bolt):
    return PREVIEWS / label / f"{bolt}.json"


@contextlib.contextmanager
def preview_lock(label):
    """The partition's preview records held for one act on them, as session_open holds a card's folder."""
    d = PREVIEWS / label
    d.mkdir(parents=True, exist_ok=True)
    with open(d / ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def preview_recorded(label, bolt):
    """crew's record of the bolt's preview on this host, or None when none stands; refused when it can't be read
    (read.1)."""
    p = preview_path(label, bolt)
    try:
        r = json.loads(p.read_text())
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        fail(f"crew's record of bolt {bolt}'s preview, {p}, can't be read: {e}")
    (isinstance(r, dict) and isinstance(r.get("head"), str) and isinstance(r.get("main"), str)) or fail(
        f"crew's record of bolt {bolt}'s preview, {p}, holds no head and checkout crew reads")
    return r


def preview_write(label, bolt, r):
    p = preview_path(label, bolt)
    tmp = p.with_name(f".{p.name}")
    tmp.write_text(json.dumps(r) + "\n")
    tmp.replace(p)


def handed_named(command, label, bolt):
    """Whether ps names a process as the preview crew handed for the bolt, crew _preview <label> <bolt> <head> as
    plan.py runs it (read.4)."""
    return f" _preview {label} {bolt} " in f" {command} "


def preview_alive(r, label, bolt):
    """Whether the handed process crew recorded (r) still runs, as ps names it (handed_named): nothing else is ended."""
    pid = r.get("pid")
    if not isinstance(pid, int):
        return False
    try:
        ps = subprocess.run(["ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True, timeout=POLL)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return ps.returncode == 0 and handed_named(ps.stdout.strip(), label, bolt)


def previews_of(main, bolt, head):
    """The preview of head on the bolt's branch as sluice lists it on this host (preview_listed), or None; refused when
    sluice's previews can't be read."""
    doc, why = sluice_read(main, "previews")
    not why or fail(f"sluice's previews can't be read in {main}: {why}")
    return preview_listed(doc, f"bolt/{bolt}", head)


def shown_of(p):
    """What a card built with the preview p shows of it (preview_said): its addresses, or a reason."""
    return "addresses" if p.get("state") in ("waiting", "starting", "up") else "reason"


def preview_ask(fleet, t, label, bolt, head, declared):
    """The preview of the bolt's head its landing card is raised with (rail-cards, record 0031 §3), on the team's host,
    this one: what preview_step makes of crew's record, sluice's list and the handed process, done under the partition's
    previews lock. Asked anew, `crew _preview <label> <bolt> <head>` is handed to a process of its own (code.9), which
    runs sluice's preview to its end in the kit's main checkout (preview_handed); then sluice's previews are read every
    PREVIEW_POLL seconds, up to PREVIEW_START, for the head's (preview_listed). Returns what the card is built with: the
    preview as sluice lists it, {head, name, addresses, state}; {head, why} when the handed process ended first, in its
    words, or sluice named none in time, the process left running; None when none is declared or recorded. What the card
    shows is recorded, for the preview's end to read (preview_change); what crew can't read is said on the card the
    same way, and released nothing it could not (read.1)."""
    main = t["kit"]["main"]
    try:
        with preview_lock(label):
            r = preview_recorded(label, bolt)
            listed = previews_of(main, bolt, head) if r and r["head"] == head else None
            alive = bool(r) and r["head"] == head and preview_alive(r, label, bolt)
            step = preview_step(declared, r["head"] if r else None, head, listed is not None, alive)
            if step in ("release", "replace"):
                said, released = preview_released(label, bolt, r)
                print(said)
                if not released:
                    return None if step == "release" else {"head": head, "why": f"its earlier preview is not released yet: {said}"}
            if step in ("none", "release"):
                return None
            if step == "keep" and not listed and r.get("outcome"):  # it ended unlisted, as a refusal does
                listed = {"head": head, "why": r["outcome"].get("why") or f"it ended {r['outcome'].get('state')}"}
            proc = None
            if step != "keep":
                r = dict(head=head, main=main, asked=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
                preview_write(label, bolt, r)
                proc = preview_hand(label, bolt, head)
                preview_write(label, bolt, dict(r, pid=proc.pid))
        got = listed or preview_awaited(main, bolt, head, proc, label)
        with preview_lock(label):
            r = preview_recorded(label, bolt)
            if not r or r["head"] != head:
                return {"head": head, "why": "it was released while the card was raised"}
            if r.get("outcome"):  # it ended while it was awaited: what it came to is what the card shows
                got = previews_of(main, bolt, head) or {"head": head, "why": r["outcome"].get("why") or f"it ended {r['outcome'].get('state')}"}
            preview_write(label, bolt, dict(r, shown=shown_of(got), **({"name": got["name"]} if got.get("name") else {})))
        return got
    except Refusal as e:
        return {"head": head, "why": str(e)}


def preview_hand(label, bolt, head):
    """crew _preview <label> <bolt> <head> started in a session of its own, which outlives the command that raised the
    card, its output in <bolt>.log beside the record; refused when it can't be started."""
    argv = ["bash", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bin", "crew"), "_preview", label, bolt, head]
    try:
        with open(PREVIEWS / label / f"{bolt}.log", "w") as out:
            return subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
    except OSError as e:
        fail(f"crew could not hand the ask for it to a process of its own: {e}")


def preview_awaited(main, bolt, head, proc, label):
    """The head's preview once sluice lists it, read every PREVIEW_POLL seconds up to PREVIEW_START: as sluice lists it,
    or {head, why} when the handed process (proc, or the one recorded when a raise keeps it) ended first, in the words
    it recorded or its log's last line, or when sluice named none in time."""
    deadline = time.monotonic() + PREVIEW_START
    while True:
        got = previews_of(main, bolt, head)
        if got:
            return got
        ended = proc.poll() is not None if proc else not preview_alive(preview_recorded(label, bolt) or {}, label, bolt)
        if ended:
            got = previews_of(main, bolt, head)
            if got:
                return got
            r = preview_recorded(label, bolt) or {}
            why = (r.get("outcome") or {}).get("why")
            if not why:
                try:
                    said = (PREVIEWS / label / f"{bolt}.log").read_text().strip().splitlines()
                except OSError:
                    said = []
                why = said[-1] if said else "the process crew handed it to ended, saying nothing"
            return {"head": head, "why": why}
        if time.monotonic() > deadline:
            return {"head": head, "why": f"sluice named no preview within {PREVIEW_START} seconds"}
        time.sleep(PREVIEW_POLL)


def preview_ended(code, out, err):
    """How `sluice preview <branch> <revision> --wait --json` ended, from its exit, its standard output and its standard
    error, as sluice 0.29.3 gives them (read.2): {state: "up"}, or {state: "failed", why}, why sluice's error's message
    when it refused, the end of the preview command's output when its stack failed, else sluice's last line."""
    try:
        doc = json.loads(out)
    except ValueError:
        doc = None
    if isinstance(doc, dict) and isinstance(doc.get("error"), dict) and isinstance(doc["error"].get("message"), str):
        return {"state": "failed", "why": doc["error"]["message"]}
    if isinstance(doc, dict) and doc.get("state") == "up" and code == 0:
        return {"state": "up"}
    if isinstance(doc, dict) and doc.get("state") == "failed":
        return {"state": "failed", "why": cards.last_lines(doc.get("output") if isinstance(doc.get("output"), str) else "",
                                                           cards.DETAIL) or "its command failed, printing nothing"}
    said = [l.strip() for l in f"{err or ''}\n{out or ''}".splitlines() if l.strip()]
    return {"state": "failed", "why": said[-1] if said else f"sluice exited {code}"}


def preview_handed(fleet, a):
    """crew _preview <label> <bolt> <head>: the ask preview_ask hands to a process of its own on the team's host (code.9).
    It runs `sluice preview bolt/<bolt> <head> --wait --json` in the checkout crew's record names, with no timeout of
    crew's, since the policy's [preview] timeout bounds sluice's command and a release ends this wait
    (preview_released); writes how it ended (preview_ended) to the record while the record still names this head; and,
    when that changes what the card says (preview_change), changes the landing card in place with the note while it
    waits on the user (preview_changed). A record naming another head, or none, has nothing written and nothing
    changed. What goes wrong is said in its log, never a traceback to anyone (code.2)."""
    sys.stdout.reconfigure(line_buffering=True)
    name = f"bolt/{a.bolt}'s preview of {a.head[:7]}"
    try:
        r = preview_recorded(a.label, a.bolt)
        if not r or r["head"] != a.head:
            print(f"{name} is no longer crew's to ask: its record names " + (f"{r['head'][:7]}" if r else "none"))
            return
        print(f"asking sluice for {name} in {r['main']}")
        try:
            run = subprocess.run(["sluice", "preview", f"bolt/{a.bolt}", a.head, "--wait", "--json"], cwd=r["main"],
                                 stdin=subprocess.DEVNULL, capture_output=True, text=True)
            ended = preview_ended(run.returncode, run.stdout, run.stderr)
        except OSError as e:
            ended = {"state": "failed", "why": f"sluice could not run: {e}"}
        with preview_lock(a.label):
            r = preview_recorded(a.label, a.bolt)
            if not r or r["head"] != a.head:
                print(f"{name} ended {ended['state']}, and crew writes nothing: its record has moved on")
                return
            preview_write(a.label, a.bolt, dict(r, outcome=ended))
        print(f"{name} ended {ended['state']}" + (f": {ended['why']}" if ended.get("why") else ""))
        note = preview_change(r.get("shown"), ended["state"], a.head)
        if note:
            preview_changed(fleet, a.label, a.bolt, note)
    except Refusal as e:
        print(f"{name}: {e}")
    except Exception as e:  # said in its log, as the handed construct's are
        import traceback
        traceback.print_exc()
        print(f"{name}: {type(e).__name__}: {e}")


def preview_changed(fleet, label, bolt, note):
    """A preview's end said on its kit's landings card (rail-cards "A preview that fails is said on the card"): the
    card's raise handed to the partition's main machine with the preview's note (land_hand), where the row is read
    again, its preview taken by keep, and the card changed in place while it waits on the user, and left as it is once
    they answered it (landings_step)."""
    plan, b, t = land_held(fleet, label, bolt)
    if not t:
        print(f"land/{bolt}'s preview ended, and no card is changed: no team holds bolt {bolt}")
        return
    land_hand(fleet, label, b.get("Repo") or t["kit"]["name"], f"{bolt}: {landing_act('preview', words=note)[1]}")


def preview_released(label, bolt, r):
    """The preview crew recorded for the bolt (r) released, under the previews lock its caller holds: the handed process
    ended first, by its process group, only while ps names it as crew's (preview_alive, read.4), then `sluice release`
    of its name, or of its head when sluice named none, in the checkout it ran in, and the record removed once sluice
    answers. A release sluice refuses, or that can't run, is said and the record kept, so the next close or sweep tries
    again (read.1). Returns (words, released)."""
    key, h, target = f"land/{bolt}", r["head"][:7], r.get("name") or r["head"]
    if preview_alive(r, label, bolt):
        try:
            os.killpg(r["pid"], SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
    doc, why = sluice_read(r["main"], "release", target)
    if why or not (isinstance(doc, dict) and "released" in doc):
        return (f"{key}'s preview of {h} is not released, and crew keeps it to release later: sluice release {target} "
                + (why or "printed no document crew reads")), False
    preview_path(label, bolt).unlink(missing_ok=True)
    (PREVIEWS / label / f"{bolt}.log").unlink(missing_ok=True)
    if doc["released"]:
        return f"released {key}'s preview of {h}" + (f", {r['name']}" if r.get("name") else ""), True
    return f"{key}'s preview of {h} had nothing left for sluice to release, and crew's record of it is removed", True


def preview_release(label, bolt):
    """The preview crew recorded for the bolt released on this host, its record's lock held (preview_released): (words,
    released), or (None, False) when crew recorded none. A record crew can't read is kept and said."""
    with preview_lock(label):
        try:
            r = preview_recorded(label, bolt)
        except Refusal as e:
            return f"{e}: crew released nothing, and keeps it", False
        if not r:
            return None, False
        return preview_released(label, bolt, r)


# ------------------------------------------------------------------------------------- a landing's words, kept

# The user's words to land a bolt, given in main-level ops's pane, kept on the host crew bolt submit ran on until crew
# bolt land closes the landing card with them (plan.16), ~/.local/state/crew/landings/<label>/<bolt>.json: the words,
# who submitted them, when, and the transcript record they were read from (from), as the bolt.submit entry names it.
# Host state, like a preview's record, never the run record, which holds no words (record.3).
LANDINGS = pathlib.Path.home() / ".local/state/crew/landings"


def landing_word_path(label, bolt):
    return LANDINGS / label / f"{bolt}.json"


def landing_word_keep(label, bolt, words, by, at, frm):
    """The user's words to land the bolt kept on this host, replacing any kept before for a bolt of that name."""
    p = landing_word_path(label, bolt)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(f".{p.name}.{os.getpid()}")
    tmp.write_text(json.dumps({"words": words, "by": by, "at": at, "from": frm}, ensure_ascii=False))
    tmp.replace(p)


def landing_word_read(label, bolt, frm):
    """The user's words kept on this host for the bolt's landing whose bolt.submit names the transcript record frm,
    or None when none are kept here or the words kept are another landing's; refused naming the file when it is
    there but can't be read (read.1)."""
    p = landing_word_path(label, bolt)
    try:
        r = json.loads(p.read_text())
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        fail(f"crew can't read the user's words kept for bolt {bolt}'s landing in {p}: {e}")
    isinstance(r, dict) and isinstance(r.get("words"), str) or fail(
        f"crew can't read the user's words kept for bolt {bolt}'s landing in {p}: it holds no words")
    return r["words"] if r.get("from") == frm else None


def landing_word_drop(label, bolt):
    """The words kept for the bolt's landing removed from this host, once its landing is written."""
    landing_word_path(label, bolt).unlink(missing_ok=True)


# ------------------------------------------------------------------------------- crew's own cards: the act

class CardActs:
    """What the act reaches beyond its facts: Pending You through the fleet's bridge, this host's run record, a tell,
    a picture's upload, a card's reading session started and ended, this host and who runs the command. A logic test
    hands the act a stand-in (code.7)."""

    def __init__(self, fleet):
        self.fleet = fleet

    def bridge(self, name, later, held=None):
        return cards.Bridge(name, later, held)

    def emit(self, label, act, on, **fields):
        return record.emit(label, act, on, **fields)

    def entries(self, label):
        return cards.host_entries(record, label, crew.this_host())

    def tell(self, name, text):
        return crew.tell(self.fleet, name, text)

    def put(self, url, data, kind):
        return cards.put(url, data, kind)

    def session(self, label, key, facts):
        """The link of the key's reading session, started or given again (reading_open)."""
        return self.reading(label, key, facts)[0]

    def reading(self, label, key, facts):
        """The key's reading session as reading_open gives it: its link, whether the user decided in it before it
        ended, and whether it was started anew."""
        return reading_open(self.fleet, label, key, facts)

    def end(self, label, key):
        """The key's session ended, in words; None when crew recorded none for it on this host."""
        return end_session(label, key)[0] if (CARDS / label / key / "session.json").exists() else None

    def preview(self, label, key, facts):
        """The preview a landing card is raised with, asked, kept, replaced or released (preview_ask)."""
        t = self.fleet["teams"][facts["team"]]
        return preview_ask(self.fleet, crew.with_kit(t, facts["kit"]) if facts.get("kit") else t, label, key.split("/", 1)[1], facts["head"], facts["previewed"])

    def release_preview(self, label, key):
        """The preview crew recorded for a landing card's bolt released (preview_release), in words; None when none was
        recorded."""
        return preview_release(label, key.split("/", 1)[1])[0] if key.startswith("land/") else None

    def host(self):
        return crew.this_host()

    def caller(self):
        return agent()

    def heard(self, words):
        """The verdict on the words in the caller's own Claude session's transcript on this host, preferring the
        user's record of them (transcript.check, want="user"), and the session's id."""
        sid, elsewhere = session_here(record.session(), crew.this_host())
        return (transcript.unverified(elsewhere) if elsewhere else transcript.check(sid, words, want="user")), sid

    def kits(self, label):
        """The names of the kits the partition's teams build, which tell a kit's landings card's key from a bolt's
        (cards.row_object)."""
        return partition_kits(self.fleet, label)

    def partition(self, label):
        """The partition's run record from BATCH_DAYS back, read from its branch (partition_entries), refused naming
        the branch when it cannot be read (read.1)."""
        return partition_entries(self.fleet, label)

    def forecast(self, label, kit, bolts, held=()):
        """The forecasts of a kit's landings card's rows (forecast_rows)."""
        return forecast_rows(self.fleet, label, kit, bolts, held)

    def keep_main(self, label, kit, sha):
        """The revision of main a kit's landings card's rows were forecast against kept on this host, the main level's,
        beside the card's state (landings_main), crew's own note of what it read and no entry of the run record
        (state.1); what can't be written is said, and the raise goes on."""
        f = landings_main(label, kit)
        try:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(sha + "\n")
        except OSError as e:
            print(f"card land/{kit}: crew could not keep the revision of main its rows were forecast against: {e.strerror or e}; "
                  "the next rail read raises the card again", file=sys.stderr)

    def kept_main(self, label, kit):
        """The revision of main keep_main kept for a kit's landings card, or None when none is kept or it can't be read,
        which costs one more raise."""
        try:
            return landings_main(label, kit).read_text().strip() or None
        except OSError:
            return None

    def work(self, label, kit, moves):
        """Each moved bolt's own work between the head the user sent and its head now (bolt_work)."""
        return bolt_work(self.fleet, label, kit, moves)

    def land_row(self, label, bolt, host):
        """A bolt's row on its kit's landings card, read on its team's host (land_row): (row, None), in this process
        when that is this host, else by crew _land-row there as the one asking (code.3), what it said passed on; (None,
        why) when that host did not answer, the read refused, or it printed no row crew reads (read.2, read.3)."""
        if host == self.host():
            try:
                with contextlib.redirect_stdout(sys.stderr):
                    return land_row(self.fleet, label, bolt, self), None
            except Refusal as e:
                return None, str(e)
        r = crew.on_machine(self.fleet, host, crew.crew_argv(self.fleet, host, "_land-row", label, bolt, "--json"))
        if r.stderr.strip():
            print(r.stderr.rstrip(), file=sys.stderr)
        if r.returncode:
            return None, ((r.stderr or r.stdout).strip().splitlines() or [f"exit {r.returncode}"])[-1]
        try:
            row = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            row = None
        ok = isinstance(row, dict) and row.get("bolt") == bolt and (isinstance(row.get("why"), str) or row.get("box") is True)
        return (row, None) if ok else (None, f"crew _land-row printed no row crew reads: {cut(r.stdout.strip(), 200)}")


CARD_LATER = "The event stands, and its card is not posted."
# A card the user answered before its thing changed, as its close is recorded: its note, the user's to read, is on the
# card, and the run record holds crew's words alone (record.3).
REVISED = "answered, then changed: a new card follows it"
# A card whose kind changed while it waited, as its withdrawal is recorded: Pending You changes no card's kind.
RENEWED = "changed in kind: a new card follows it"
# A card built again with questions while it waited, as its withdrawal is recorded: Pending You changes no card's
# questions.
REASKED = "changed with its questions: a new card follows it"
# A card Pending You had ended already, by another hand than crew's close, as its close is recorded (cards.ended).
ENDED_ELSEWHERE = "ended in Pending You already"
# A card Pending You resolved as crew's post of a card following it went in, as its close is recorded (card_posted).
FOLLOWED = "picked up in Pending You by the card that follows it"


def card_where(kit):
    """Where a kit's card is asked from and filed, as the act takes it: the kit's checkout, the card's folder, and its
    git remote as Pending You files an area by it."""
    return kit["main"], cards.remote_of(f"github.com/{kit['repo']}")


def card_area(py, label, cwd, remote, name):
    """The area a card of the kit at remote is filed in: the one Pending You matches to it, else the kit's, made under
    create-area:<owner>/<kit> in the partition's group (briefs.11)."""
    matched = py.call("match_area", {"cwd": cwd, "remote": remote, "task": name})
    area = cards.area_of(matched)
    if area:
        return area
    make = cards.create_area_args(remote, label, matched)
    made = py.call("create_area", make)
    area = made.get("areaId")
    isinstance(area, str) and cards.AREA_ID.match(area) or fail(
        f"Pending You's answer to create_area names no area: crew can't tell where the card would go. {CARD_LATER}")
    note = made.get("groupNote")
    if isinstance(note, str) and note.strip():
        print(f"area {make['name']}: {note.strip()}")
    return area


def card_heard(acts, key, card, owner):
    """How the owner hears a card crew posted in no session (briefs.16): the line that adopts it, printed, and told
    to the owner when the command that raised it is not the owner's own (roles.4)."""
    line = cards.adopt_line(card, owner)
    print(line)
    to = cards.told_to(owner, acts.caller())
    if to and acts.tell(to, f"Your card {key} is up for the user: {line}, to hear their answer."):
        print(f"told {to}: {line}")


def card_uploaded(acts, key, b, got):
    """A built card's picture put to the upload URL its post or change was given, or said where it did not land."""
    if not b.get("picture"):
        return
    title = next(x["title"] for x in b["card"].get("artifacts") or [] if x.get("upload"))
    url = cards.upload_of(got, title)
    why = acts.put(url, b["picture"], "image/png") if url else "Pending You gave no upload URL for it"
    if why:
        print(f"card {key}: its picture did not reach the card: {why}", file=sys.stderr)


def built_fields(b):
    """A built card's post or change entry's own fields: Unread, why its reading could not open (unopened), crew's own
    message (record.3), left out when it opened or the card links none; and Heads, a kit's landings card's rows as
    <bolt>@<head>, :left after one the user cleared on their last send (cards.landings_card), which its next raise reads
    (landings_step)."""
    return ({"Unread": b["unread"]} if b.get("unread") else {}) | ({"Heads": " ".join(b["heads"])} if b.get("heads") else {})


def asked_of(b):
    """A built card's post or change entry's Head: the head a landing's or a deploy's card asks about, so a card the
    user answered is asked again only once the head moved (cards.head_anew); nothing for any other card."""
    return {"Head": b["head"]} if b.get("head") else {}


def card_posted(acts, label, owner, b, where, entries=None, since=None):
    """A built card posted, recorded, printed and heard; or said and recorded refused, refusing nothing else. It is
    posted under the row's key qualified by the partition's label, or that key with its revision once a card of the
    owner's under it closed, either filled out to Pending You's eight characters when shorter (post_key, from entries,
    this host's run record of the partition unless given), and recorded under the row's key, with why its reading could not open when it did not (built_fields) and the head it
    asks about (asked_of). A post Pending
    You answers
    with the card this host's record holds open under the key already, another command's post of it recorded while
    this one was asked, as two rail reads at once ask (record 0031 §1: two readers of one event make one card), is
    that card, printed with the line that adopts it and recorded once, by the command that recorded it first. A post
    that follows a card of the owner's those entries still hold open reads that card once it is made, and records it
    closed when Pending You has ended it, as it picks up an answered card a new card follows (followed_closed); one
    given back as recorded already reads nothing, the command that recorded it having read it.

    A post that comes after a card the user answered, the card it follows closed or declined, or the card whose answer
    stands under the row's key (cards.answered_before, record 0031 as amended 2026-10-24), opens its summary and its
    details with what they answered, when, and what changed since, since being the event's sentences, and follows that
    card (cards.answered_opening, cards.opened); with nothing changed, since empty or not given, it is not posted: it is
    recorded as a post refused in crew's words, naming that card and saying its answer stands (cards.stands_said), with
    the card and the state stands, said, and None returned, refusing nothing of the event (roles.3). A card posted again
    once an older copy was lost (built_copy) is no follow-on but the row's card, and is posted whatever since says, as
    built when it gives nothing (rail-cards "A row's card lost to its owner is posted again")."""
    key, obj = b["key"], cards.row_object(b["key"], acts.kits(label)) or f"agent/{owner}"
    cwd, remote = where
    known = acts.entries(label) if entries is None else entries
    earlier = cards.answered_before(known, b["card"].get("follows"), key, owner)
    if earlier:
        opening = cards.answered_opening(earlier, since)
        if not opening and not b.get("again"):
            words = cards.stands_said(earlier)
            acts.emit(label, "card.post", [obj], by=owner, refused=words, Card=earlier["card"], Key=key, State=cards.STANDS)
            print(f"card {key}: {words}", file=sys.stderr)
            return None
        b = dict(b, card=cards.opened(b["card"], opening, earlier["card"])) if opening else b
    asked = cards.post_key(known, key, owner, label)
    follows = b["card"].get("follows")
    held = cards.followed_open(known, follows, owner) if follows else None
    try:
        with acts.bridge(owner, CARD_LATER) as py:
            area = card_area(py, label, cwd, remote, owner)
            got = py.call("post_request", cards.post_args(b["card"], asked, owner, acts.host(), cwd, area))
            card = cards.request_id(got, "post_request")
            card_uploaded(acts, key, b, got)
            again = cards.card_under(acts.entries(label), key, owner) == card
            read = followed_read(py, follows, owner) if held and not again else None
    except Refusal as e:
        acts.emit(label, "card.post", [obj], by=owner, refused=str(e), Key=key, **built_fields(b))
        print(f"card {key} not posted: {e}", file=sys.stderr)
        return None
    url = got.get("url")
    url = f" {url}" if isinstance(url, str) else ""
    if again:
        print(f"card {key}: {card}{url}, its post recorded already")
        print(cards.adopt_line(card, owner))
        return card
    acts.emit(label, "card.post", [obj], by=owner, Card=card, Key=key, **built_fields(b), **asked_of(b))
    print(f"card {key}: {card}{url}")
    card_heard(acts, key, card, owner)
    if held:
        followed_closed(acts, label, owner, held, follows, card, *read)
    return card


def followed_read(py, card, owner):
    """The card a post followed, read in the post's session once the post is made: (get_request's answer, None), or
    (None, why) when it could not be read, the session's failure caught here so the post stands."""
    try:
        got, words = py.answer("get_request", {"requestId": card, "name": owner})
    except Refusal as e:
        return None, str(e).removesuffix(f" {CARD_LATER}")
    return (None, f"Pending You refused get_request: {words}") if words is not None else (got, None)


def followed_closed(acts, label, owner, key, card, by, got, why):
    """The card a post followed, held open under key, once read: recorded closed when Pending You has ended it, picked
    up by the card by that follows it when it reports it resolved, with what the user answered on it when its reply
    still carries that (cards.answer_said); left as the run record holds it while it waits or is answered, for the
    event that ends it to close, and when the read failed, which is said."""
    if why:
        print(f"card {key}: whether {card} was picked up can't be read: {why}", file=sys.stderr)
        return
    state = cards.ended(got)
    if not state:
        return
    picked, answer = got.get("status") == "resolved", cards.answer_said(got)
    acts.emit(label, "card.close", [cards.row_object(key, acts.kits(label)) or f"agent/{owner}"], by=owner, Card=card, Key=key, State=state,
              Outcome=FOLLOWED if picked else ENDED_ELSEWHERE, **({"Answer": answer} if answer else {}))
    print(f"card {key}: {card} picked up in Pending You by {by}, which follows it" if picked else
          f"card {key}: {card} was {state} in Pending You already")


# The fact a builder takes a card's reading session's link as, by the kind of card that links one (briefs.9).
READING = {"batch": "link", "proposal": "session", "land": "link"}


def reading_of(b):
    """Whether a built card links a reading session, and of which kind: a batch's and a landing's always, a
    proposal's when its builder says it needs one, for more than fifteen new units; None for any other."""
    kind = b["key"].split("/")[0]
    if b.get("linked"):  # a kit's landings card, each of whose rows' readings its raise opened (landings_card)
        return None
    return kind if kind in ("batch", "land") or (kind == "proposal" and b.get("session")) else None


def unopened(b, why):
    """A built card whose reading session could not open, raised all the same (briefs.9): its summary saying so after
    its first paragraph, cut again to Pending You's budget, saying that crew tries it again when the rail is read
    (sweep_cards) and naming crew card session <key> as how its owner starts it, the card then carrying its link
    (briefs.13: the owner's act, nothing for the user to run), a landing's the bolt's conductor, a batch's and a long
    proposal's the planner; its details opening with why, where the link would be; and why kept on the built card
    (unread), for its post's or change's entry in the run record."""
    key = b["key"]
    owner = "the bolt's conductor" if key.startswith("land/") else "the planner"
    said = (f"Its reading could not be opened on the tailnet: crew tries it again when the rail is read, and {owner} "
            f"starts it with crew card session {key}; this card then carries its link.")
    first, _, rest = b["card"]["summary"].partition("\n\n")
    summary = cards.prose("\n\n".join(x for x in (first, said, rest) if x))
    context = dict(b["card"]["context"], background=f"The reading could not be opened on the tailnet: {why}\n\n"
                   + b["card"]["context"]["background"])
    return dict(b, card=dict(b["card"], summary=summary, context=context), unread=why)


def card_built(acts, label, build, facts):
    """A card of crew's own built from its facts, with its reading session's link among them when it links one: the
    session started, or given again while it serves, before the card is built (reading_of); a batch's or a long
    proposal's tried once more when it refuses, its refusal said, the files it reads written afresh at the second
    start (card-sessions "A batch's or a long proposal's raise tries its reading twice"); facts that carry the link
    already, or why it could not be opened (unread), as a landing's raise opens it, twice if it must (landing_opened),
    used as they are, nothing started; a session that could not open said, naming crew card session <key>, and the card
    built without it, saying so, with the last try's reason (unopened)."""
    b = build(facts)
    kind = reading_of(b)
    if not kind or facts.get(READING[kind]):
        return b
    key, why = b["key"], facts.get("unread")
    for again in range(0 if why else 1 if kind == "land" else 2):
        if again:
            print(f"card {key}: its reading could not be opened on the tailnet: {why}; crew tries once more", file=sys.stderr)
        try:
            with READ.fresh() if again else contextlib.nullcontext():
                url = acts.session(label, key, facts)
        except Refusal as e:
            why = str(e)
        else:
            return build(dict(facts, **{READING[kind]: url}))
    print(f"card {key}: its reading could not be opened on the tailnet: {why}; crew card session {key} starts it", file=sys.stderr)
    return unopened(b, why)


def row_card_post(fleet, label, owner, build, facts, where, acts=None, since=None):
    """The act that posts a card of crew's own (briefs.16, record 0031 §1): build(facts), one of cards.py's six
    builders, posted through the fleet's `pendingyou mcp` under the host's sign-in, asked in the name of owner, the
    role whose row it is, under the row's key, from where, the kit's (checkout, remote) as card_where gives it, and
    filed in the kit's area, its picture uploaded; recorded on the row's object with the card's id and key, and
    printed with the line that adopts it, told to the owner when the command is not the owner's. A batch's card, a
    landing's and a long proposal's have their reading session started first, its link handed to the builder
    (card_built). Pending
    You's refusal, a host not signed in, no answer within a minute or a reply naming no card is said and recorded as
    the post refused, and refuses nothing of the event it was raised for. A card that follows one the user answered
    says first what they answered and what changed since, since, or is not posted when nothing did (card_posted). The
    card's id, or None."""
    acts = acts or CardActs(fleet)
    return card_posted(acts, label, owner, card_built(acts, label, build, facts), where, since=since)


def card_lost(acts, label, owner, key, card, words):
    """A card Pending You no longer finds for its owner, recorded closed as lost so it is held no longer."""
    acts.emit(label, "card.close", [cards.row_object(key, acts.kits(label)) or f"agent/{owner}"], by=owner, Card=card, Key=key, State="lost",
              Outcome=f"lost to its owner: {words}")
    print(f"card {key}: {card} is lost to {owner} (Pending You: \"{words}\")", file=sys.stderr)


def row_card_change(fleet, label, owner, build, facts, note, where, acts=None, kind_changed=False, anew=None, since=None):
    """The act that changes a card of crew's own when its thing changes (record 0031 §3): build(facts) sent as
    update_request takes it, with note as the change note the user sees, at the version Pending You reports, to the
    card the owner holds under the row's key on this host, while it waits on the user. Once they have answered it,
    which Pending You changes no longer, it is final for what it asked (cards.revision): left as it is, the act their
    answer calls for going on, unless what it asks changed since (anew, None while it has not; else the facts that say
    so, {} for none, a landing's head moved since their approval among them, cards.head_anew), or its kind; then acked
    with note as its outcome and closed, its close keeping what they answered (cards.answer_said), and build(facts and
    anew) posted as a new card that follows it, under the key with its revision (post_key), against the run record with
    that close in it, its state, time and answer. A card whose kind changed (kind_changed), or one built again that carries questions,
    a proposal's whose rows fill more than one list, neither of which update_request ever changes, is followed the same
    way, withdrawn with note while it waits. Posted instead when the owner holds none, and posted again, its summary
    saying the older copy is dead, when Pending You no longer finds it. A landing's card and a long proposal's are
    built with their reading session's link, as a post's is (card_built), a landing's session on a moved head started
    anew there, so the card changed carries the new link, and its entry why it could not open when it did not
    (built_fields), and a landing's or a deploy's the head it asks about (asked_of). A new card posted after one the user
    answered opens with what they answered and what changed since, since, the event's sentences, or note when the
    event gives none, and is not posted when since is given empty (card_posted); a card posted again, the older copy
    lost or one this host can't reach handed over as dead (built_copy), is the row's card and never withheld, opening
    with note when the event gives nothing changed. A refusal is said and recorded as the change refused, refusing
    nothing of the event. The card's id, the new card's when one was posted, or None."""
    acts = acts or CardActs(fleet)
    b = card_built(acts, label, build, facts)
    key, obj = b["key"], cards.row_object(b["key"], acts.kits(label)) or f"agent/{owner}"
    entries = acts.entries(label)
    card = cards.card_under(entries, key, owner)
    if not card:
        return card_posted(acts, label, owner, b, where, entries, (since or [note]) if b.get("again") else since)
    lost, how, state = None, "change", None
    why = "its kind having changed" if kind_changed else "its questions having to be asked anew"
    try:
        with acts.bridge(owner, CARD_LATER) as py:
            got, lost = py.answer("get_request", {"requestId": card, "name": owner})
            if lost is None:
                state = cards.ended(got)
                how = cards.revision(got, kind_changed, "questions" in b["card"], anew is not None)
            if lost is None and how == "follow":
                tool, args, state = cards.close_call(got, card, owner, outcome=cut(note, 120))
                _, lost = py.answer(tool, args)
            elif lost is None and how == "change":
                change = dict(cards.change_args(b["card"], note), requestId=card, name=owner,
                              expectedVersion=cards.version_of(got, card))
                got, lost = py.answer("update_request", change)
            if lost is not None and not cards.lost(lost):
                what = {"closed": "close of the card the user answered", "withdrawn": f"withdrawal of the card, {why}"}
                fail(f"Pending You refused the {what.get(state, 'change')}: {lost}")
            if lost is None and how == "change":
                card_uploaded(acts, key, b, got)
    except Refusal as e:
        acts.emit(label, "card.update", [obj], by=owner, refused=str(e), Card=card, Key=key, **built_fields(b))
        print(f"card {key} not changed: {e}", file=sys.stderr)
        return None
    if how == "leave":
        print(f"card {key}: {card} is left as it is: the user has answered it")
        return card
    answer = cards.answer_said(got) if lost is None else None
    answered = {"Answer": answer} if answer else {}
    at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    closed = entries + [dict(Act="card.close", Card=card, Key=key, By=owner, State="lost" if lost is not None else state, At=at, **answered)]
    if lost is not None:
        card_lost(acts, label, owner, key, card, lost)
        return card_posted(acts, label, owner, built_copy(b), where, closed, since or [note])
    if state == "closed" and anew:  # what it asks changed since the user answered it, which the new card says
        b = card_built(acts, label, build, dict(facts, **anew))
    if how == "ended":
        acts.emit(label, "card.close", [obj], by=owner, Card=card, Key=key, State=state, Outcome=ENDED_ELSEWHERE, **answered)
        print(f"card {key}: {card} was {state} in Pending You already, and its new version follows it")
        follows = {"follows": card} if state == "closed" else {}
        return card_posted(acts, label, owner, dict(b, card=dict(b["card"], **follows)), where, closed, [note] if since is None else since)
    if how == "follow":
        acts.emit(label, "card.close", [obj], by=owner, Card=card, Key=key, State=state,
                  Outcome=REVISED if state == "closed" else RENEWED if kind_changed else REASKED, **answered)
        print(f"card {key}: {card} " + ("closed, the user having answered it" if state == "closed" else f"withdrawn, {why}")
              + ", and its new version follows it")
        return card_posted(acts, label, owner, dict(b, card=dict(b["card"], follows=card)), where, closed, [note] if since is None else since)
    acts.emit(label, "card.update", [obj], by=owner, Card=card, Key=key, **built_fields(b), **asked_of(b))
    v = got.get("version")
    print(f"card {key}: {card} changed" + (f", now version {v}" if isinstance(v, int) else ""))
    return card


def row_card_close(fleet, label, owner, key, outcome=None, reason=None, acts=None, said=None, here=False, offered=(), **more):
    """The act that closes a card of crew's own at the event that ends it (record 0031 §1): the card the owner holds
    under the row's key on this host, acked with the outcome once the user answered it, else withdrawn with the
    reason, or the outcome; recorded with how it closed. A card Pending You no longer finds is recorded lost, and a
    refusal said and recorded as the close refused, neither refusing the event. The key's reading session on this
    host ends with the card, closed, lost or held by nobody, and stays while a refused close leaves the card open
    (card-sessions). A land/ key ends nothing: a kit's landings card has no reading or preview of its own, and a closed
    card of a bolt's own, land/<bolt> or land/<bolt>/<head> as a conductor posted one before, is no word on the bolt's
    row, whose reading and preview end with the row (land_end). said, when given, is what Pending You is sent in place
    of the outcome, words the run record does not keep (record.3); here, that the user answered it in a conversation,
    so a card still waiting closes as answered there (cards.close_call). A card the user answered is closed with what
    they answered, as Answer (card_closed); offered, the ids of the boxes the card offered, a kit's landings card's
    rows as land:<bolt>, so the answer names those they left. more, fields the close's entry carries beside crew's own,
    a kit's landings card's Rows (landings_step). The card's id, or None when none was closed."""
    acts = acts or CardActs(fleet)
    card = card_closed(acts, label, owner, key, outcome, reason, said, here, more, offered)
    if card is not False and key.split("/")[0] in READING and not key.startswith("land/"):
        said = acts.end(label, key)
        if said:
            print(said)
    return card or None


def card_closed(acts, label, owner, key, outcome, reason, said=None, here=False, more=None, offered=()):
    """row_card_close's close in Pending You: the card's id once closed, None when none was held or it was lost, and
    False when the close was refused, so the card stays open. said is sent in place of the outcome, and the outcome
    recorded; here closes a card still waiting as answered in a conversation. The close's entry carries what the user
    answered, as Answer, in crew's words (cards.answer_said, offered the ids of the boxes the card offered), or that
    they answered it in the owner's pane when it closed as answered there; a card withdrawn while it waits, none."""
    obj = cards.row_object(key, acts.kits(label)) or f"agent/{owner}"
    card = cards.card_under(acts.entries(label), key, owner)
    if not card:
        print(f"card {key}: {owner} holds none open on this host, so none is closed")
        return None
    lost = None
    try:
        with acts.bridge(owner, "The event stands, and its card stays open.") as py:
            got, lost = py.answer("get_request", {"requestId": card, "name": owner})
            state = cards.ended(got) if lost is None else None
            if state:
                outcome, reason = ENDED_ELSEWHERE, None
            elif lost is None:
                tool, args, state = cards.close_call(got, card, owner, outcome if said is None else said, reason, here)
                _, lost = py.answer(tool, args)
            if lost is not None and not cards.lost(lost):
                fail(f"Pending You refused the close: {lost}")
    except Refusal as e:
        acts.emit(label, "card.close", [obj], by=owner, refused=str(e), Card=card, Key=key)
        print(f"card {key} not closed: {e}", file=sys.stderr)
        return False
    if lost is not None:
        card_lost(acts, label, owner, key, card, lost)
        return None
    answer = cards.answer_said(got, offered) or (f"answered in {owner}'s pane" if here and state == "closed" else None)
    acts.emit(label, "card.close", [obj], by=owner, Card=card, Key=key, State=state, Outcome=cards.close_words(got, outcome, reason),
              **(more or {}), **({"Answer": answer} if answer else {}))
    print(f"card {key}: {card} {state}")
    return card


# ------------------------------------------------------------------------------------------------ crew record

def record_split(md):
    """A decision record's Markdown as crew reads it: its frontmatter's fields, its body and the body's paragraphs."""
    m = re.match(r"---\n(.*?)\n---\n", md, re.S)
    fields = dict(l.split(":", 1) for l in m.group(1).splitlines() if re.match(r"[a-z][\w-]*:", l)) if m else {}
    body = (md[m.end():] if m else md).strip()
    return {k: v.strip().strip("'\"") for k, v in fields.items()}, body, [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def record_status_held(md):
    """A decision record's status as its file holds it, the one reading crew record and a proposal's check share
    (briefs.15): its frontmatter's status, and the paragraphs that mark an amendment proposed ("Status: proposed" past
    the record's own status line)."""
    fields, _, paras = record_split(md)
    own = next((i for i, p in enumerate(paras) if p.startswith("Status:")), None)
    return fields.get("status", "").lower(), [p for i, p in enumerate(paras) if i != own and "Status: proposed" in p]


def record_says(status, marked):
    """What a record's file holds, in crew's words, from its status and the amendments marked proposed."""
    return "accepted, with an amendment still marked proposed" if marked and status == "accepted" else status or "no status in its frontmatter"


def record_accepted(status, marked):
    """Whether a record's file holds it accepted: its status accepted, with no amendment still marked proposed."""
    return status == "accepted" and not marked


def record_facts(kit, number, text, status, before=None, alternatives=None):
    """A decision record's facts as its card is built from them (cards.record_card), from its Markdown at a commit, and
    whether the file holds the status the design agent records (briefs.15): its title, its frontmatter's or else its
    heading's; its opening, the first paragraph of its body that is neither a heading nor a `Name:` line, or, for an
    amendment, the paragraph its proposed mark stands in; an amendment's own first words, which title its card in
    place of the record's (cards.first_words, record 0031 as amended 2026-10-24), else None; the user's words its
    deciders line quotes; its body whole; and the alternatives a rule of the user's decided between, from the Markdown
    --alternatives hands, whose frontmatter names the rules that decided (`rules:`, separated by commas), the other
    path (`other:`) and, when the user's own words point there, `recommended: loosen`, else accepting as ruled is. A
    file holds its frontmatter's status, but proposed while an amendment to an accepted record is still marked proposed
    ("Status: proposed" past the record's own status line), and accepted or rejected alike once the mark the text
    before (before, the record at the commit before) held is gone, the amendment taken in or out. Refused naming what
    the file holds when it holds no such status, and refused when what the card is built from can't be read (read.1)."""
    n = f"{number:04d}"
    fields, body, paras = record_split(text)
    now, marked = record_status_held(text)
    then, was = record_status_held(before) if before else ("", [])
    holds = ["proposed"] if now == "accepted" and marked else ["accepted", "rejected"] if now == "accepted" and then == "accepted" and was else [now]
    says = record_says(now, marked)
    status in holds or fail(f"crew refuses record {n} in {kit} as {status}: its file on main says {says}. Commit it {status} "
                            f"and land it on main, then run crew record again.")
    head = next((p for p in paras if p.startswith("# ")), "")
    title = fields.get("title") or re.sub(r"^#\s+(\d+\.\s+)?", "", head)
    amended = bool(marked) and now == "accepted"
    if amended:
        opening = re.sub(r"\s*Status: proposed\b.*?(?:\.(?=\s|$)|$)", "", marked[0], flags=re.S).strip()
    else:
        opening = next((p for p in paras if not p.startswith("#") and not re.match(r"[A-Z][\w -]*:\s", p)), "")
    amendment = cards.first_words(opening) if amended else None
    title and opening and amendment != "" or fail(
        f"crew can't read record {n} in {kit} for its card: it has no "
        + ("title" if not title else "opening paragraph" if not opening else "words of its amendment") + ". Nothing is raised.")
    deciders = next((p for p in paras if p.startswith("Deciders:")), "")
    quoted = [a or b for a, b in re.findall(r"“([^”]+)”|\"([^\"]+)\"", deciders)]
    alt = None
    if alternatives is not None:
        afields, abody, _ = record_split(alternatives)
        rules = [r.strip() for r in afields.get("rules", "").split(",") if r.strip()]
        other, rec = afields.get("other", ""), afields.get("recommended", "accept")
        why = ("their frontmatter names no rules that decided, as rules: <rule ids, separated by commas>" if not rules else
               "their frontmatter names no other path, as other: <the path the rules ruled out>" if not other else
               f"their frontmatter recommends {rec}, where it takes loosen or accept" if rec not in ("loosen", "accept") else
               "the file holds nothing under its frontmatter for the card" if not abody else None)
        not why or fail(f"crew refuses the alternatives for record {n} in {kit}: {why}. Nothing is raised.")
        alt = {"rules": rules, "other": other, "text": abody, "recommended": rec}
    return {"kit": kit, "number": number, "title": title, "opening": opening, "amendment": amendment, "quoted": quoted, "text": body,
            "alternatives": alt}


def raise_record(fleet, label, facts, where, note, acts=None, dead=False):
    """A decision record's card raised in its design agent's name (record 0031 §1, briefs.15), record/<kit>/<number>,
    from the record's facts (record_facts), from where, the kit's checkout on this host and its remote: posted the
    first time, and while the design agent holds it open, changed in place with note, naming the new commit, or once the
    user has answered it, closed with note and followed by a new card, since a revision asks anew (row_card_change),
    which opens saying what they answered and that the record was revised, note.
    With dead, an older copy this host can't reach standing, the card is built saying first that it was lost
    (built_again). A refusal is said and recorded and refuses nothing of the status, already recorded. The card's id,
    or None."""
    build = built_again(cards.record_card) if dead else cards.record_card
    return row_card_change(fleet, label, f"{label}-design", build, facts, note, where, acts, anew={}, since=[note])


def raise_record_again(fleet, row, acts=None):
    """The rail's sweep's raise of a decision record's card its design agent's host can't reach (sweep_judged's again,
    record 0031 §1), for its row of the group records, of which it reads the label, the key record/<kit>/<number> and
    whether its card offered alternatives: the record read with status proposed as crew record reads it on the kit's
    main (record_read), and its card posted in the design agent's name saying first that an older copy was lost
    (raise_record). A card that offered alternatives is refused, since crew keeps no copy of the file they were read
    from (read.1), naming the crew record command that raises it again; a record whose file no longer holds proposed,
    or that crew can't read, is refused in record_read's words. The card's id, or None."""
    m = re.fullmatch(r"record/([a-z0-9][a-z0-9-]*)/(\d{4})", row.get("key") or "")
    if not m:
        return None
    label, kit_, n = row["label"], m.group(1), int(m.group(2))
    not row.get("alternatives") or fail(
        f"crew keeps no copy of record {n:04d}'s alternatives, so {label}-design raises it again with "
        f"crew record {kit_} {n} --proposed --alternatives <file>")
    facts, where, sha, subject = record_read(fleet, label, kit_, n, "proposed")
    return raise_record(fleet, label, facts, where, f"Raised again at {sha[:7]}: {subject}", acts, dead=True)


def record_card_close(fleet, label, owner, obj, outcome, acts=None):
    """A decision record's cards closed at its accepted or rejected status with outcome: each the owner holds open on
    this host under the record's key, obj, in either form, record 0031's or the one with the commit after it
    (cards.record_keys), closed as row_card_close closes a row's, and said when it holds none. The ids closed."""
    acts = acts or CardActs(fleet)
    keys = cards.record_keys(acts.entries(label), obj, owner, acts.kits(label)) or [obj]
    return [c for c in (row_card_close(fleet, label, owner, k, outcome=outcome, acts=acts) for k in keys) if c]


def record_kit(fleet, label, name):
    """The kit of a partition's teams named name, read from the teams file alone (code.5); refused naming the kits it
    takes."""
    kits = {k["name"]: k for t in crew.partition_of(fleet, label)["teams"] for k in crew.kits_of(fleet["teams"][t])}
    name in kits or fail(f"crew record takes a kit of {label}'s, " + (f"{either(sorted(kits))}, not {name}." if kits else
                                                                     f"and no team of {label} builds one."))
    return kits[name]


def record_read(fleet, label, kit_, number, status, alternatives=None):
    """A decision record as crew record reads it (briefs.15): the kit's docs/adr/<number>-*.md on its main now, GitHub's
    after a fetch for a kit with an origin (kit.main_now, plan.18), read in this host's checkout of the kit, at the
    last commit that changed it, and its facts with the status and alternatives text given (record_facts). (facts,
    where, the commit, its subject), where as card_where gives it for the checkout; refused when the checkout, main,
    the one file or the status it holds can't be read (read.1)."""
    here, k, n = crew.this_host(), record_kit(fleet, label, kit_), f"{number:04d}"
    checkout = crew.kept_on(fleet, here, k["repo"]) or fail(f"no session of {here} keeps {k['repo']}, so crew can't read its records")

    def git(*args):
        r = subprocess.run(["git", "-C", checkout, *args], capture_output=True, text=True)
        r.returncode == 0 or fail(f"git {args[0]} in {checkout} failed: {(r.stderr or r.stdout).strip() or f'exit {r.returncode}'}")
        return r.stdout
    # The record as the kit's main holds it now, GitHub's after a fetch for a kit with an origin (kit.main_now, plan.18).
    r = subprocess.run(["bash", "-c", MAIN, "crew", checkout], capture_output=True, text=True, env=gitenv())
    r.returncode == 0 or fail(f"{checkout} could not be read: {(r.stderr or r.stdout).strip() or f'exit {r.returncode}'}")
    _, now, why = kit.main_now(r.stdout, kit_, here)
    not why or fail(why)
    files = [f for f in git("ls-tree", "--name-only", now, "docs/adr/").splitlines() if re.fullmatch(rf"docs/adr/{n}-[^/]*\.md", f)]
    len(files) == 1 or fail(f"{kit_}'s main holds " + (f"no record {n} in docs/adr/" if not files else
                                                         f"{len(files)} records numbered {n}: {', '.join(files)}") + ", so crew records nothing.")
    commits = [l.split("\t", 1) for l in git("log", "-2", "--format=%H\t%s", now, "--", files[0]).splitlines()]
    sha, subject = commits[0]
    facts = record_facts(kit_, number, git("show", f"{sha}:{files[0]}"), status,
                         git("show", f"{commits[1][0]}:{files[0]}") if len(commits) > 1 else None, alternatives)
    return facts, card_where(dict(k, main=checkout)), sha, subject


def record_status(fleet, a):
    """crew record <kit> <number> --proposed|--accepted|--rejected [--settled-in-pane --excerpt "<words>"]
    [--alternatives <file>] [--label L]: the design agent's record at each turn of its status (briefs.15, record 0031
    §1). The kit is one of the partition's teams', read from the teams file alone (code.5); the record is read as
    record_read reads it, where the partition's main level runs. A status its file does not hold there is refused,
    naming what it holds, and so is an alternatives file crew can't read, with nothing recorded. Else record.<status>
    is recorded on record/<kit>/<number> with that commit; then --proposed raises the record's card in the design
    agent's name, or changes the one it holds, naming the commit, unless --settled-in-pane says the user said yes in
    the pane, in the words --excerpt gives, which crew reads in the caller's own transcript on this host as the user's
    before it reads the kit (settled_refusal), whoever the caller is (roles.2), and records naming the transcript
    record and the words' length, never the words (record.3), raising nothing; --alternatives makes the card the
    choice a rule decided, recorded as the proposed status's Form, none of the file's words (record.3); and --accepted
    or --rejected closes the card with the commit, under either key form (record_card_close). A card the design agent
    holds where this host's sign-in can't reach it, posted from another host or lost to it (record_stranded), is
    posted again saying first that the older copy was lost."""
    label = default_label(fleet, a) or fail("crew record runs as the record's partition: run it as the design agent, or add --label")
    p = crew.partition_of(fleet, label)
    k = record_kit(fleet, label, a.kit)
    0 < a.number < 10000 or fail(f"a record's number is its one to four digits, not {a.number}")
    a.status == "proposed" or not (a.settled_in_pane or a.alternatives) or fail(
        f"--settled-in-pane and --alternatives go with --proposed: a record {a.status} closes its card")
    not (a.settled_in_pane and a.alternatives) or fail(
        "a record settled in the pane raises no card, so it takes no alternatives: give --settled-in-pane or --alternatives")
    not a.settled_in_pane or (a.excerpt or "").strip() or fail(
        "--settled-in-pane needs --excerpt \"<the user's yes, as they wrote it in your pane>\": crew reads it in your transcript")
    a.excerpt is None or a.settled_in_pane or fail(
        "--excerpt goes with --settled-in-pane: the words are the user's yes, given in your pane")
    here, n = crew.this_host(), f"{a.number:04d}"
    p["machine"] == here or fail(f"crew record runs on {p['machine']}, where {label}'s design agent holds its records' cards")
    v = sid = None
    if a.settled_in_pane:
        v, sid = CardActs(fleet).heard(a.excerpt)
        why = settled_refusal(a.number, a.kit, v)
        not why or fail(why)
    alternatives = None
    if a.alternatives:
        try:
            alternatives = pathlib.Path(a.alternatives).read_text()
        except (OSError, UnicodeDecodeError) as e:
            fail(f"crew can't read the alternatives file {a.alternatives}: {getattr(e, 'strerror', None) or e}. Nothing is raised.")
    facts, where, sha, subject = record_read(fleet, label, a.kit, a.number, a.status, alternatives)
    key, settled = f"record/{a.kit}/{n}", a.status == "proposed" and a.settled_in_pane
    frm = [f"session/{sid}/{v.uuid or f'line-{v.line_hash()[:16]}'}"] if settled else []
    record.emit(label, f"record.{a.status}", [key], frm=frm, commit=[f"{k['repo']}@{sha}"],
                State="settled in the pane" if settled else None, Chars=len(a.excerpt) if settled else None,
                Form="alternatives" if alternatives is not None else None)
    print(f"record {n} in {a.kit}: {a.status} at {sha[:7]}" + (", the user's yes given in the pane; no card is raised" if settled else ""))
    if a.status != "proposed":
        record_card_close(fleet, label, f"{label}-design", key, f"{a.status.capitalize()} at {sha[:7]}")
    elif not settled:
        raise_record(fleet, label, facts, where, f"Revised at {sha[:7]}: {subject}", dead=record_stranded(fleet, label, key))


def record_stranded(fleet, label, key):
    """Whether the design agent's newest card under a record's key is one this host's sign-in can't reach, posted from
    another host and not closed, or lost to it (cards.stranded), from the partition's run record of the last cards.DAYS
    days, read from its branch (record.gather); False, said, when the branch could not be read, so the card is posted
    as it would be."""
    since = (datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=cards.DAYS)).isoformat()
    entries, missing = record.gather(fleet, [label], since)
    if missing:
        print(f"card {key}: whether an older copy of it is held where this host's sign-in can't reach could not be looked for: "
              + "; ".join(f"{h}: {v}" for h, v in sorted(missing.items())), file=sys.stderr)
        return False
    return cards.stranded(entries, key, f"{label}-design", crew.this_host()) is not None


# ------------------------------------------------------------------------------- the rail's sweep of the cards

# The name crew's sweep gives Pending You when it asks after cards: no agent's, so it claims no agent's answers
# (briefs.17). Pending You refuses it another assistant's card as that assistant's ("This is crw-2-conductor's card;
# leave it."), so the card is there, and answers "not found" only for a card this host's sign-in no longer reaches
# (the recovery session, 2026-10-15 and 16), which is all the sweep asks.
SWEEPER = "crew"
# Each kind's raise, the function its change of the series gives it, handed a rail row (record 0031 §1): by the row
# key's first part, a name in this module or, as ops.<name>, in ops.py. A kind whose function is not there has none yet.
RAISES = {"proposal": "raise_proposal", "batch": "raise_batch", "land": "raise_landings_row", "deploy": "ops.raise_deploy",
          "op": "ops.raise_step", "record": "raise_record_again"}
SWEEP_LATER = "The rail's sweep changes nothing on this read."


class SweepActs(CardActs):
    """What the rail's sweep reaches beyond the act's own: herdr's listing of an asker, a kind's raise, a reading tried
    again and the clock. A logic test hands the sweep a stand-in (code.7)."""

    def listed(self, name):
        """Whether herdr lists an agent in the pane crew keeps for the asker, from one listing of its session (read.2,
        crew.read_pane_agent): (True or False, None), or (None, why) when that can't be read; never by the agent's
        name, which herdr drops when the pane's session changes."""
        return crew.read_pane_agent(self.fleet, name)

    def raise_of(self, kind):
        name = RAISES.get(kind)
        if name and name.startswith("ops."):
            import ops  # ops.py imports nothing of this module
            return getattr(ops, name[4:], None)
        return globals().get(name) if name else None

    def now(self):
        return datetime.datetime.now(datetime.timezone.utc)

    def main_at(self, label, kit, sv):
        """The revision of main the rail's survey (sv) read a kit at in its builder's main checkout (gather.kit's
        main_at), as last fetched (plan.18): (sha, None), or (None, why) when no team builds it, its host did not
        answer or its read names none. A builder holding no bolt is not in the rail's survey, and is surveyed alone."""
        t = builder(self.fleet, label, kit)
        if not t:
            return None, f"no team of {label} builds {kit}"
        host, main = t["machine"], t["kit"]["main"]
        v = sv.get(host)
        if v is None or (v["ok"] and main not in v["kits"]):
            v = survey(self.fleet, [(t["name"], None, kit)]).get(host) or {"ok": False, "error": "it was not read"}
        if not v["ok"]:
            return None, f"{host} did not answer ({v['error']})"
        k = v["kits"].get(main) or {}
        if not k.get("ok"):
            return None, f"{main} on {host} could not be read: {k.get('error') or 'it was not read'}"
        return (k["main_at"], None) if k.get("main_at") else (
            None, f"crew on {host} names no revision of main it read {main} at, as a crew older than the read of it does")

    def raise_kit(self, label, kit):
        """A kit's landings card raised again as main moved under it (raise_landings, with no note of its own), what it
        says going to standard error, the rail's text saying what it did: the card's id, or None."""
        with contextlib.redirect_stdout(sys.stderr):
            return raise_landings(self.fleet, label, kit, self)

    def reading_again(self, label, key):
        """A card's reading opened again and its card changed to carry the link: a kit's landings card's, land/<kit>,
        by its raise with RELINKED as its note (raise_landings), which tries each row's reading on its team's host as
        crew card session land/<bolt> opens it, refused in the words its card then stands without one in (Unread) when
        one still will not open; a batch's or a proposal's as before (reading_again). As reading_open returns it: the
        link, None for a kit's card, whose links are its rows', whether the user decided in it, and whether it was
        started anew."""
        if not key.startswith("land/"):
            return reading_again(self.fleet, label, key, self)
        raise_landings(self.fleet, label, key.split("/", 1)[1], self, note=RELINKED)
        entries = self.entries(label)
        card = cards.card_under(entries, key, f"{label}-ops")
        if reading_unread(entries, key, card):
            fail(next((e["Unread"] for e in reversed(entries) if e.get("Card") == card and e.get("Unread") and not e.get("Refused")
                       and e.get("Act") in ("card.post", "card.update")), "a row's reading still stands unopened"))
        return None, False, True


def question_close(acts, label, c, words):
    """A question withdrawn by crew once its asker has ended (briefs.11): read in the asker's name, which no session
    holds now, and withdrawn with words, or acked with them when the user answered it to nobody; recorded on the
    asker. One Pending You ended already, followed up by its asker or dismissed by the user, is recorded so and sent
    nothing (cards.ended). Pending You's "not found" records it lost, and a refusal is said and recorded refused. The
    close's state, or None."""
    who, card, key = c["by"], c["card"], c["key"] or ""
    lost, outcome = None, words
    try:
        with acts.bridge(who, "The question stays open.") as py:
            got, lost = py.answer("get_request", {"requestId": card, "name": who})
            state = cards.ended(got) if lost is None else None
            if state:
                outcome = ENDED_ELSEWHERE
            elif lost is None:
                tool, args, state = cards.close_call(got, card, who, reason=words)
                _, lost = py.answer(tool, args)
            if lost is not None and not cards.lost(lost):
                fail(f"Pending You refused the close: {lost}")
    except Refusal as e:
        acts.emit(label, "card.close", [f"agent/{who}"], by=who, refused=str(e), Card=card, Key=key)
        print(f"question {card} of {who} not withdrawn: {e}", file=sys.stderr)
        return None
    if lost is not None:
        card_lost(acts, label, who, key, card, lost)
        return "lost"
    acts.emit(label, "card.close", [f"agent/{who}"], by=who, Card=card, Key=key, State=state, Outcome=outcome)
    return state


def sweep_cards(fleet, read, acts=None):
    """The rail read's sweep of the cards on this host, under its sign-in (record 0031 §1, §2, read.4): for each
    partition whose plan was read, and whose run record was read from its branch, it closes each card of a row that
    is gone with why (sweep_judged, row_gone), a proposal's only on the plan as this read holds it (read["proposed"],
    proposals_held), at or past the commit its card was raised at (older_than_card), and each decision record's card,
    under either key form, at the record's status
    (record_settled), withdraws each question whose asker's pane herdr lists with no agent in it, naming the asker,
    and leaves one whose asker's pane it can't read, saying why (SweepActs.listed, read.1), posts again
    through its kind's raise each row's card Pending You no longer finds, and posts through its kind's raise each row's
    card that has none; a lost card of a kind with no raise is recorded lost, for its owner to raise again with the
    command that raised it, and a row of one is left as it is. Before any of it, where the partition's planner runs,
    it records crew's close of each batch that waits on nothing, once, as batch.close on batch/<n> in the planner's
    name with its card key and why (briefs.12), so a host not signed in still records it; a card open under its key is
    withdrawn with the same words, as a card whose row is gone. It asks Pending You in crew's own name
    (SWEEPER) whether it finds each card, which Pending You answers for another assistant's card by refusing it as
    that assistant's, and for a card this host's sign-in no longer reaches with "not found". Every row's card this
    host's sign-in can't reach, posted from another host or lost to its owner, while the row's owner runs here, is
    posted again through its kind's raise, its summary saying the older copy is dead, the older copy reported lost and
    never asked after nor closed from here, and a raise that posts none reported left (sweep_judged's again, briefs.11,
    briefs.12, read.1). A host not signed in,
    or a bridge that fails, changes nothing more, and is said, as is a partition whose record could not be read from its
    branch, which records no close either (read.1). crew board sweeps nothing (state.4). Returns {done: [{label, key,
    card, by, did, words, new}], unswept: [{label, why}]}, did closed, withdrawn, lost, posted or left, a batch's close
    by crew with card and new None."""
    acts = acts or SweepActs(fleet)
    here, now = acts.host(), acts.now()
    out, judged = {"done": [], "unswept": []}, []
    down = {h for h, v in read["sv"].items() if not v["ok"]}
    for l, _, _, pl in read["found"]:
        if not pl:
            continue
        unread = read["unread"].get(l, {})
        if unread:
            out["unswept"].append(dict(label=l, why="; ".join(f"its run record could not be read from {b}, so which cards are open can't be told: {v}"
                                                              for b, v in sorted(unread.items()))))
            continue
        rows = [r for r in read["rows"] if r["label"] == l]
        owners = {r["key"]: row_owner(fleet, pl, r) for r in rows}
        blind = {b.name() for b in pl.bolts() if (fleet["teams"].get(b.get("Team")) or {}).get("machine") in down}
        blind |= {b.get("Repo") for b in pl.bolts() if b.name() in blind and b.get("Repo")}  # a kit's card, a bolt of it unread
        planner = row_owner(fleet, pl, dict(label=l, group="batches", key=None))
        design = (f"{l}-design", fleet["partitions"][l]["machine"])
        j = sweep_judged(here, rows, [c for c in read["cards"] if c["label"] == l], read["logs"].get(l, []), owners, blind,
                         read["proposed"].get(l), now, planner, design, partition_kits(fleet, l),
                         {x["bolt"]: r["key"].split("/", 1)[1] for r in rows if r["group"] == "land" for x in r.get("bolts", [])})
        for key, why in j.pop("settled"):
            got = acts.emit(l, "batch.close", [key.partition("-")[0]], by=planner[0], why="batch: closed by crew, it waits on nothing",
                            Key=key, Outcome=why)
            out["done"].append(dict(label=l, key=key, card=None, by=planner[0], did="closed" if got else "left",
                                    words=why if got else "crew's close was not recorded, as said above", new=None))
        j["none"] = [r for r in j["none"] if acts.raise_of(r["key"].split("/")[0])]
        j["again"] = [(r, c) for r, c in j["again"] if acts.raise_of(r["key"].split("/")[0])]
        if any(j.values()):
            judged.append((l, dict(owners, **{r["key"]: design for r, _ in j["again"] if r["group"] == "records"}), j))
    if not judged:
        return out
    asked = [c["card"] for _, _, j in judged for c in [c for c, *_ in j["gone"]] + [c for c, _ in j["held"]] + j["questions"]]
    try:
        with acts.bridge(SWEEPER, SWEEP_LATER) as py:
            found = {card: py.answer("get_request", {"requestId": card, "name": SWEEPER}) for card in asked}
    except Refusal as e:
        out["unswept"] += [dict(label=l, why=str(e)) for l, _, _ in judged]
        return out

    def did(l, key, card, by, what, words, new=None):
        out["done"].append(dict(label=l, key=key, card=card, by=by, did=what, words=words, new=new))

    def raised(l, row, owner):
        """The row's card posted through its kind's raise, in record 0031's key form alone: its id, or None, with
        whether the kind has a raise; a raise's refusal is said, and taken as no raise on this read."""
        up = acts.raise_of(row["key"].split("/")[0]) if cards.row_object(row["key"]) else None
        try:
            return (up(fleet, row, acts=acts) if up else None), bool(up)
        except Refusal as e:
            did(l, row["key"], None, owner, "left", f"its raise refused: {e}")
            return None, None
    for l, owners, j in judged:
        for c, outcome, reason in j["gone"]:
            words = found[c["card"]][1]
            if cards.lost(words):
                card_lost(acts, l, c["by"], c["key"], c["card"], words)
                did(l, c["key"], c["card"], c["by"], "lost", ("its row is gone" if card_kind(c["key"]) == "row" else "its record is settled")
                    + ", so nobody posts it again")
            elif row_card_close(fleet, l, c["by"], c["key"], outcome, reason, acts):
                did(l, c["key"], c["card"], c["by"], "closed" if outcome else "withdrawn", outcome or reason)
            else:
                did(l, c["key"], c["card"], c["by"], "left", "its close did not go through, as said above")
        for c in j["questions"]:
            words = found[c["card"]][1]
            if cards.lost(words):
                card_lost(acts, l, c["by"], c["key"] or "", c["card"], words)
                did(l, c["key"], c["card"], c["by"], "lost", "this host's sign-in no longer reaches it")
                continue
            listed, why = acts.listed(c["by"])
            if listed is None:
                did(l, c["key"], c["card"], c["by"], "left", f"whether {c['by']} still runs can't be told: {why}")
            elif not listed:
                state = question_close(acts, l, c, f"{c['by']} ended; ask again if it still matters")
                did(l, c["key"], c["card"], c["by"], state or "left", {None: "its close did not go through, as said above",
                                                                       "lost": "this host's sign-in no longer reaches it"}.get(state, f"{c['by']} ended"))
        for c, row in j["held"]:
            words = found[c["card"]][1]
            if not cards.lost(words):
                continue
            new, kind_raises = raised(l, row, c["by"])
            if new:
                did(l, c["key"], c["card"], c["by"], "lost", f"posted again as {new}", new)
            elif kind_raises is False:
                card_lost(acts, l, c["by"], c["key"], c["card"], words)
                did(l, c["key"], c["card"], c["by"], "lost", f"crew raises no card for {c['key']} on a rail read, so {c['by']} raises it again with the command that raised it")
            elif kind_raises:
                did(l, c["key"], c["card"], c["by"], "left", "Pending You no longer finds it, and its raise posted none")
        for row, older in j["again"]:
            owner = owners[row["key"]][0]
            new, kind_raises = raised(l, dict(row, dead=older), owner)
            if new:
                did(l, row["key"], older, owner, "lost", stranded_said(read["logs"].get(l, []), older, owner, new), new)
            elif kind_raises:
                did(l, row["key"], older, owner, "left",
                    "its batch no longer waits to be read" if row["key"].startswith("batch/") else "its raise posted none")
        for c, row in j["unread"]:
            if cards.lost(found[c["card"]][1]):
                continue
            try:
                with acts.bridge(c["by"], SWEEP_LATER) as py:
                    got, words = py.answer("get_request", {"requestId": c["card"], "name": c["by"]})
                not words or fail(f"Pending You refused get_request: {words}")
            except Refusal as e:
                did(l, c["key"], c["card"], c["by"], "left", f"whether it waits on the user can't be read: {e}")
                continue
            if not card_waiting(got):
                continue
            try:
                url = acts.reading_again(l, c["key"])[0]
            except Refusal as e:
                did(l, c["key"], c["card"], c["by"], "left", f"its reading could not be opened: {e}")
            else:
                did(l, c["key"], c["card"], c["by"], "opened", f"its reading opened at {url}" if url else "its rows' readings opened")
        for row in j["none"]:
            owner = owners[row["key"]][0]
            new, _ = raised(l, row, owner)
            if new:
                did(l, row["key"], None, owner, "posted", "its row had none open", new)
    return out


def sweep_moved(fleet, read, acts=None):
    """The rail read's raise of each kit's landings card main moved under (rail-cards "Main moves under an open card"),
    once its sweep acted, on the partition's main machine alone, where main-level ops's cards are: for each partition
    whose plan was read, each landings card open on this host in ops's name (land/<kit>), the revision of main the
    survey read its kit at in its builder's checkout, as last fetched with no fetch of its own (SweepActs.main_at,
    plan.18), and the one its rows were last forecast against (CardActs.kept_main) are compared (landings_moved), and
    each card main moved under is raised again (SweepActs.raise_kit), which fetches GitHub's main and forecasts its
    rows there; a card main has not moved under is fetched for and raised by none. A raise refused is said, and the read
    goes on. Returns {raised: [{label, kit, was, now, card, said}], unread: [{label, kit, why}]}, said the refusal's
    words or None."""
    acts = acts or SweepActs(fleet)
    here, out = acts.host(), {"raised": [], "unread": []}
    for l, _, _, pl in read["found"]:
        if not pl or crew.partition_of(fleet, l)["machine"] != here:
            continue
        kits = partition_kits(fleet, l)
        open_ = [(l, kit) for c in read["cards"] if c["label"] == l and c["host"] == here and c["by"] == f"{l}-ops"
                 for kind, kit in [land_key(c["key"], kits) or (None, None)] if kind == "kit"]
        mains = {c: acts.main_at(l, c[1], read["sv"]) for c in dict.fromkeys(open_)}
        kept = {c: acts.kept_main(*c) for c in mains}
        due, unread = landings_moved(open_, {c: m for c, (m, _) in mains.items()}, kept)
        out["unread"] += [dict(label=l, kit=c[1], why=mains[c][1]) for c in unread]
        for c in due:
            moved = dict(label=l, kit=c[1], was=kept[c], now=mains[c][0], card=None, said=None)
            try:
                moved["card"] = acts.raise_kit(l, c[1])
            except Refusal as e:
                moved["said"] = str(e)
            out["raised"].append(moved)
    return out


def card_folder(rel):
    """The card key and unit (None but for an old batch card's, batch/<n>-<k>) whose session a folder under
    ~/.local/state/crew/cards/<label>/ keeps, from its path there: batch/<n> is a key's own folder, as a proposal's;
    None when the path is no key's folder."""
    path = "/".join(rel.parts)
    if any(re.fullmatch(k, path) for k in CARD_KEYS + (VERIFY_KEY,)):
        return path, None
    key = "/".join(rel.parts[:2])
    if len(rel.parts) == 3 and old_batch(key) and crew.NAME.match(rel.parts[2]):
        return key, rel.parts[2]
    return None


def card_sweep(fleet, a):
    """crew card sweep --label L: the rail's, run on each host of the partition with its judgment on standard input as
    JSON, {"live": [card keys], "blind": [key prefixes]}. It ends, through end_session, each session crew recorded on
    this host for the partition whose key is in no live entry and starts with no blind prefix, once it is at least two
    minutes old by its own start against this host's clock and its folder's lock is free (crew card session holds it
    while it starts one). Then it releases, through preview_release, each preview crew recorded on this host for a
    bolt of the partition whose landing card's key the judgment holds dead, once it is two minutes old by when it was
    asked (preview_dead). It prints, as a JSON list, each session and preview it acted on: its key, its unit (a batch
    card's) or null, what it said, and whether it sent SIGTERM or released the preview. A folder with no session.json,
    or whose path is no card key's, is left alone, and a record it can't read is kept and said (read.1, read.4)."""
    a.key is None or fail("crew card sweep takes no key: it judges every session crew recorded on this host, from the "
                          "rail's judgment on standard input")
    label = default_label(fleet, a) or fail("crew card sweep runs for a partition: add --label")
    try:
        j = json.loads(sys.stdin.read())
    except ValueError:
        j = None
    (isinstance(j, dict) and set(j) == {"live", "blind"}
     and all(isinstance(j[k], list) and all(isinstance(x, str) for x in j[k]) for k in j)) or fail(
        'crew card sweep reads the rail\'s judgment on standard input as {"live": [card keys], "blind": [key prefixes]}')
    live, blind, root = set(j["live"]), tuple(j["blind"]), CARDS / label
    now, out = datetime.datetime.now(datetime.timezone.utc), []
    for f in sorted(root.rglob("session.json")) if root.is_dir() else []:
        found = card_folder(f.parent.relative_to(root))
        if not judged_dead(found, live, blind):
            continue
        key, unit = found
        name = f"{key} {unit}" if unit else key
        try:
            lock = open(f.parent / ".lock", "a")
        except FileNotFoundError:
            continue  # ended while the sweep looked
        with lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                continue  # its session is being started
            try:
                s = card_recorded(f.parent)
            except Refusal as e:
                out.append(dict(key=key, unit=unit, said=f"{e}; crew ended nothing, and keeps {name}", ended=False))
                continue
            if not s:
                continue
            try:
                left = young(s["started"], now)
            except (ValueError, TypeError):
                out.append(dict(key=key, unit=unit, ended=False,
                                said=f"crew can't read when {name}'s session started ({s['started']}): it ended nothing, and keeps {name}"))
                continue
            if left:
                continue
            said, ended = end_session(label, key, unit)
            out.append(dict(key=key, unit=unit, said=said, ended=ended))
    previews = PREVIEWS / label
    for f in sorted(previews.glob("*.json")) if previews.is_dir() else []:
        bolt, key = f.stem, f"land/{f.stem}"
        if not crew.NAME.match(bolt) or not judged_dead((key, None), live, blind):
            continue
        try:
            r = preview_recorded(label, bolt)
            dead = bool(r) and preview_dead(key, r.get("asked"), live, blind, now)
        except Refusal as e:
            out.append(dict(key=key, unit=None, said=f"{e}; crew released nothing, and keeps it", ended=False))
            continue
        except (ValueError, TypeError):
            out.append(dict(key=key, unit=None, ended=False,
                            said=f"crew can't read when {key}'s preview was asked ({r.get('asked')}): it released nothing, and keeps it"))
            continue
        if dead:
            said, released = preview_release(label, bolt)
            if said:
                out.append(dict(key=key, unit=None, said=said, ended=released))
    print(json.dumps(out))


def judged_dead(found, live, blind):
    """Whether the rail's judgment makes a recorded session's key dead: a card key's folder (found), in no live entry and
    under no blind prefix."""
    return bool(found) and found[0] not in live and not found[0].startswith(tuple(blind))


def preview_dead(key, asked, live, blind, now):
    """Whether the rail's sweep releases the preview crew asked for with a landing card under key (rail-cards "A card
    closed elsewhere"): its key dead by the rail's judgment (judged_dead), and asked at least CARD_GRACE seconds before
    now, so a card raised since the rail's read is not taken for one whose row is gone. Refused, as young is, when when
    it was asked can't be read."""
    return judged_dead((key, None), live, blind) and not young(asked, now)


def young(started, now):
    """Whether a session started under CARD_GRACE seconds before now, so the rail's read may not have seen its row yet:
    left for a later sweep. Refused when its start can't be read."""
    return (now - utc(started)).total_seconds() < CARD_GRACE


def card_units(fleet, label, key):
    """The units a batch card holds, from the batch in the run record: every unit of the batch for batch/<n>, the k-th
    five for batch/<n>-<k>."""
    n = int(key.split("/")[1].split("-")[0])
    for m, _, units in batches(partition_entries(fleet, label)):
        if m == n:
            return [u for u, *_ in card_part(key, units)]
    fail(f"{label}'s run record holds no batch {n}")


# ----------------------------------------------------------------------------------------------------- the CLI

class _Unbuilt:
    """A command's parser this run does not need: it takes every definition parser() gives it and keeps none."""

    def __getattr__(self, name):
        return lambda *args, **kwargs: self


SIGNAL_ID = "a signal's full id, <capture>/<NN>-<slug>, or its short one, <capture>/<NN>"


def parser(cls=argparse.ArgumentParser, only=None):
    """crew's command line. With only, the one command a run names is built and the rest are not, since building
    every command's parser is a third of what starting plan.py costs; the names built are in parser.built."""
    ap = cls(prog="crew", add_help=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ap.built = []
    if only:
        add = sub.add_parser

        def one(name, **kwargs):
            ap.built.append(name)
            return add(name, **kwargs) if name == only else _Unbuilt()
        sub.add_parser = one
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
    x = ca.add_parser("sweep")  # the rail's, run on each host; a key or unit given is refused
    x.add_argument("key", nargs="?")
    x.add_argument("unit", nargs="?")
    x.add_argument("--label")
    x = ca.add_parser("read")
    x.add_argument("key")
    x.add_argument("--label")
    x.add_argument("--json", action="store_true")
    x = ca.add_parser("answer")
    x.add_argument("key")
    x.add_argument("--excerpt", required=True)
    x.add_argument("--label")
    x = sub.add_parser("record")
    x.add_argument("kit")
    x.add_argument("number", type=int)
    g = x.add_mutually_exclusive_group(required=True)
    for status in ("proposed", "accepted", "rejected"):
        g.add_argument(f"--{status}", dest="status", action="store_const", const=status)
    x.add_argument("--settled-in-pane", action="store_true")
    x.add_argument("--excerpt")
    x.add_argument("--alternatives", metavar="FILE")
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
    x = bo.add_parser("submit")
    x.add_argument("bolt", nargs="+")
    x.add_argument("--excerpt", help="the user's words in your pane that said to land them, as they wrote them")
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
    x.add_argument("--signal", metavar="ID", help=SIGNAL_ID)
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

    # A chore's commands are a unit's of the same name, their subject in `unit` so the same ops build them (plan.11).
    ch = sub.add_parser("chore").add_subparsers(dest="sub", required=True)
    x = ch.add_parser("add")
    x.add_argument("unit", metavar="chore")
    x.add_argument("intent", metavar="words")
    x.add_argument("--bolt")
    x.add_argument("--repo")
    x.add_argument("--source", action="append", default=[])
    x.add_argument("--after", action="append", default=[])
    x.add_argument("--before")
    x.add_argument("--signal", metavar="ID", help=SIGNAL_ID)
    x.add_argument("--unblocks", metavar="BOLT")
    x.add_argument("--label")
    x = ch.add_parser("order")
    x.add_argument("unit", metavar="chore")
    g = x.add_mutually_exclusive_group(required=True)
    g.add_argument("--before")
    g.add_argument("--first", action="store_true")
    g.add_argument("--last", action="store_true")
    x.add_argument("--label")
    x = ch.add_parser("after")
    x.add_argument("unit", metavar="chore")
    x.add_argument("deps", nargs="*")
    x.add_argument("--none", action="store_true")
    x.add_argument("--label")
    x = ch.add_parser("move")
    x.add_argument("unit", metavar="chore")
    x.add_argument("bolt", metavar="bolt|queue")
    x.add_argument("--unblocks", metavar="BOLT")
    x.add_argument("--label")
    x = ch.add_parser("drop")
    x.add_argument("unit", metavar="chore")
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
    x.add_argument("--clear", nargs="+", action="extend", default=[], metavar="UNIT")
    x.add_argument("--label")
    x = pp.add_parser("answer")
    x.add_argument("n", type=int)
    x.add_argument("question")
    x.add_argument("answer", nargs="*")
    x.add_argument("--note")
    x.add_argument("--label")
    x = pp.add_parser("drop")
    x.add_argument("n", type=int)
    x.add_argument("reason")
    x.add_argument("--label")

    x = sub.add_parser("signal-move", prog="crew signal move")
    x.add_argument("signal", metavar="id", help=SIGNAL_ID)
    x.add_argument("move", choices=CURATION)
    x.add_argument("--target")
    x.add_argument("--reason")
    x.add_argument("--label")
    x = sub.add_parser("signal-show", prog="crew signal show")
    x.add_argument("signal", metavar="id", help=SIGNAL_ID)
    x.add_argument("--label")
    x = sub.add_parser("signal-land", prog="crew signal land")
    x.add_argument("dir", metavar="capture-dir")
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

    # The commands on a team and on a partition's main level, each one process on the host its agents run on (bash crew
    # runs them, and forwards them when one names another host).
    x = sub.add_parser("_status")
    x.add_argument("team")
    x.add_argument("--force", action="store_true")
    x = sub.add_parser("_unit-run")
    x.add_argument("unit")
    x.add_argument("stage", choices=("construct", "code", "verify", "settle", "merge"))
    x.add_argument("words", nargs="?", default="")
    x.add_argument("--chore", action="store_true", help="crew chore run asks: the name is a chore's")
    x.add_argument("--force", action="store_true")
    x = sub.add_parser("_construct-again")
    x.add_argument("team")
    x.add_argument("unit")
    x.add_argument("--by", required=True)
    x.add_argument("--handed", action="store_true", help="the handed construct's own process")
    x.add_argument("--force", action="store_true")
    x = sub.add_parser("_preview")
    x.add_argument("label")
    x.add_argument("bolt")
    x.add_argument("head")
    x = sub.add_parser("_land-row")
    x.add_argument("label")
    x.add_argument("bolt")
    x.add_argument("--json", action="store_true")
    x = sub.add_parser("_land-card")
    x.add_argument("label")
    x.add_argument("kit")
    x.add_argument("--note")
    x.add_argument("--pane")
    x = sub.add_parser("_unit-wait")
    x.add_argument("unit")
    x.add_argument("--timeout", type=int, default=3600000)
    x.add_argument("--stuck", type=int, default=900000)
    x = sub.add_parser("_fix-run")
    x.add_argument("team")
    x.add_argument("name")
    x.add_argument("mode", choices=("start", "merge", "drop", "wait"))
    x.add_argument("words", nargs="?", default="")
    x.add_argument("--bolt")
    x.add_argument("--timeout", type=int, default=3600000)
    x.add_argument("--stuck", type=int, default=900000)
    x.add_argument("--force", action="store_true")
    x = sub.add_parser("_tidy")
    x.add_argument("team")
    x.add_argument("--force", action="store_true")
    x.add_argument("--landed")
    x.add_argument("--outcome")
    x.add_argument("--said")
    x.add_argument("--here", action="store_true")
    x = sub.add_parser("_unit-free")
    x.add_argument("unit")
    x.add_argument("--team")
    x.add_argument("--force", action="store_true")
    x = sub.add_parser("_team")
    x.add_argument("act", choices=("up", "close", "rebuild", "restart", "resume", "clear", "down"))
    x.add_argument("team")
    x.add_argument("roles", nargs="*")
    x.add_argument("--force", action="store_true")
    x.add_argument("--no-greet", dest="greet", action="store_false")
    x = sub.add_parser("_needs")
    x.add_argument("words")
    x.set_defaults(team=None, slot=None)
    x = sub.add_parser("_end-short")
    x.add_argument("team")
    x.add_argument("slot")
    x = sub.add_parser("_main")
    x.add_argument("act", choices=("up", "down", "status"))
    x.add_argument("label")
    x.add_argument("--force", action="store_true")
    x = sub.add_parser("_dispatch")
    x.add_argument("act", choices=("up", "down", "status"))
    x.add_argument("label")
    x = sub.add_parser("_review")
    x.add_argument("label")
    x.add_argument("--wait", action="store_true")
    x.add_argument("--timeout", type=int, default=3600000)
    x = sub.add_parser("_console")
    x.add_argument("act", choices=("up", "down"))
    x.add_argument("label")
    sub.add_parser("_revive")
    return ap


COMMANDS = {
    ("state", "init"): state_init, ("bolts", None): bolts_view, ("rail", None): rail_view,
    ("card", "session"): card_session, ("card", "wait"): card_wait, ("card", "end"): card_end, ("card", "sweep"): card_sweep,
    ("card", "read"): card_read, ("card", "answer"): batch_answer,
    ("record", None): record_status,
    ("bolt", "new"): direct(("bolt", "new")), ("bolt", "give"): bolt_give, ("bolt", "order"): direct(("bolt", "order")), ("bolt", "drop"): direct(("bolt", "drop")),
    ("bolt", "land"): bolt_land, ("bolt", "submit"): bolt_submit,
    ("unit", "add"): direct(("unit", "add")), ("unit", "split"): direct(("unit", "split")), ("unit", "amend"): direct(("unit", "amend")),
    ("unit", "order"): direct(("unit", "order")), ("unit", "after"): direct(("unit", "after")),
    ("unit", "move"): direct(("unit", "move")), ("unit", "drop"): direct(("unit", "drop")),
    ("chore", "add"): direct(("chore", "add")), ("chore", "order"): direct(("chore", "order")), ("chore", "after"): direct(("chore", "after")),
    ("chore", "move"): direct(("chore", "move")), ("chore", "drop"): direct(("chore", "drop")),
    ("_status", None): team_status, ("_unit-run", None): unit_run, ("_unit-wait", None): unit_wait, ("_fix-run", None): fix_run,
    ("_construct-again", None): construct_hand, ("_preview", None): preview_handed,
    ("_land-row", None): land_row_cmd, ("_land-card", None): land_card_cmd,
    ("_tidy", None): team_tidy, ("_unit-free", None): unit_free,
    ("_team", None): team_cmd, ("_main", None): main_cmd, ("_dispatch", None): dispatch_cmd,
    ("_review", None): review_cmd, ("_console", None): console_cmd, ("_revive", None): revive_cmd,
    ("signal", None): signal, ("signal-move", None): signal_move,
    ("signal-show", None): signal_show, ("signal-land", None): signal_land,
    ("_needs", None): needs_cmd, ("_end-short", None): end_short,
    ("plan", "propose"): plan_propose, ("plan", "proposed"): plan_proposed, ("plan", "agree"): plan_agree,
    ("plan", "approve"): plan_approve, ("plan", "drop"): plan_drop, ("plan", "answer"): plan_answer,
}
# The commands on a team and on a main level, each one process on the host its agents run on.
TEAM_COMMANDS = {(c, None) for c in ("_status", "_unit-run", "_unit-wait", "_fix-run", "_construct-again", "_tidy", "_unit-free",
                                      "_team", "_needs", "_end-short", "_main", "_dispatch", "_review", "_console", "_revive")}
# The act a command that moves work records, done or refused. A command that only reads records nothing.
ACTS = {
    ("state", "init"): "state.init", ("bolt", "new"): "bolt.new", ("bolt", "give"): "bolt.give", ("bolt", "order"): "bolt.order",
    ("bolt", "drop"): "bolt.drop", ("bolt", "land"): "bolt.land", ("bolt", "submit"): "bolt.submit", ("unit", "add"): "unit.add", ("unit", "split"): "unit.split",
    ("unit", "amend"): "unit.amend",
    ("unit", "order"): "unit.order", ("unit", "after"): "unit.after", ("unit", "move"): "unit.move", ("unit", "drop"): "unit.drop",
    ("chore", "add"): "chore.add", ("chore", "order"): "chore.order", ("chore", "after"): "chore.after", ("chore", "move"): "chore.move",
    ("chore", "drop"): "chore.drop",
    ("signal", None): "capture", ("signal-move", None): "signal.move", ("signal-land", None): "capture",
    ("_needs", None): "stage.end",
    ("plan", "propose"): "plan.propose", ("plan", "agree"): "plan.agree", ("plan", "approve"): "plan.approve",
    ("plan", "drop"): "plan.drop",
}


def named(a):
    """The objects a command names on its command line: a refusal's entry names those. A unit or chore is named by
    its kind: the command's, crew chore run's, or the plan's, once a stage's check has read it (CONTEXT["kind"])."""
    kind = "chore" if a.cmd == "chore" or getattr(a, "chore", False) else CONTEXT.get("kind") or "unit"
    out = [f"{kind}/{a.unit}"] if getattr(a, "unit", None) else []
    if getattr(a, "unit", None) and getattr(a, "stage", None):
        out.append(f"stage/{a.unit}/{a.stage}")
    for bolt in (a.bolt if isinstance(getattr(a, "bolt", None), list) else [getattr(a, "bolt", None)]):  # crew bolt submit names several
        if bolt and bolt != "queue":
            out.append(f"bolt/{bolt}")
    if getattr(a, "team", None):
        out.append(f"team/{a.team}")
    if a.cmd == "_needs":
        out.append(f"agent/{a.team}-{a.slot}")
    if a.cmd == "signal-move":
        out.append(f"signals/{a.signal}")
    if a.cmd == "signal-land" and crew.NAME.match(pathlib.Path(a.dir).name):
        out.append(f"signals/{pathlib.Path(a.dir).name}")
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
    if argv[:2] in (["signal", "move"], ["signal", "show"], ["signal", "land"]):  # beside crew signal <slug> "<asserts>"
        argv = [f"signal-{argv[1]}"] + argv[2:]
    ap = parser(only=argv[0]) if argv and not argv[0].startswith("-") else None
    args = (ap if ap is not None and argv[0] in ap.built else parser()).parse_args(argv)
    fleet = crew.load()
    key = (args.cmd, getattr(args, "sub", None))
    if key in TEAM_COMMANDS:  # one process says what each of its steps did, in the order they did it
        sys.stdout.reconfigure(line_buffering=True)
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
    except Stopped as e:
        sys.exit(e.code)
