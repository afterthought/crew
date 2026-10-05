#!/usr/bin/env python3
"""plan.py: the bolt plan, one recutils plan.rec per partition and blueprints repo, alone on its plan/<label> branch.

The plan holds only intent: Bolt and Unit records. Every stage is read from the kits. A write fetches the branch
over https, applies itself to the tip, checks the result with recfix and crew's own rules, commits through a
temporary index in crew's own bare cache of the repo (no working tree is touched), and pushes without force. A push
that is refused because someone wrote first is applied again to the new tip, up to five times.

  crew plan init <blueprints> <label>        create plan/<label> in a blueprints repo with the schema and no records
  crew bolts [<bolt>] [--label L] [--json]   every bolt and unit of the plans, each unit's stage read from its kit
  crew bolt new <bolt> "<goal>" --repo <kit> [--source S]... [--before <bolt>]
  crew bolt give <team> [<bolt>]             the team takes the bolt (default: the first planned in its kit)
  crew bolt order <bolt> --before <bolt>|--first|--last
  crew bolt drop <bolt> "<reason>" [--requeue]
  crew bolt land <bolt>                      once every unit has landed on main
  crew unit add <unit> "<intent>" --bolt <bolt>|--repo <kit> [--source S]... [--after U]... [--before U] [--signal ID]
  crew unit split <unit> "<narrowed intent>" --into <unit> "<intent>" [--into ...]
  crew unit order <unit> --before <unit>|--first|--last
  crew unit after <unit> <unit>...|--none
  crew unit move <unit> <bolt>|queue
  crew unit drop <unit> "<reason>"
  crew unit approve <unit>                   the user's review, an empty Reviewed-by: commit on unit/<unit>
  crew signal <slug> "<what it asserts>" [--kind K] [--subject a,b] [--excerpt "<text>"]
                                             a finding, as a signal in the partition's first blueprints repo
  crew signal move <id> attach|challenge|new-territory|answered|drop [--target T] [--reason R]
                                             curation's move for a signal, in that repo's signals/moves.rec

A command that names no partition reads them all, or the agent's own (CREW_LABEL); --label names one.
"""
import argparse, datetime, fcntl, getpass, json, os, pathlib, re, subprocess, sys, tempfile

LIB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
import crew  # noqa: E402
import record  # noqa: E402
from crew import Refusal, fail  # noqa: E402

REPLAYS = 5
# What a command found out before it wrote or was refused: the partition whose run record its entry goes in.
CONTEXT = {}
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
        self.repo, self.label, self.tip, self.plan, self.subject = repo, label, tip, plan, None
        self.quiet = set()  # teams the write's own command greets, so notify leaves them be
        self.on, self.frm = [], []  # objects only the change can name, for the write's run-record entry

    def bolt(self, name):
        return self.plan.bolt(name) or self.gone("Bolt", name)

    def unit(self, name):
        return self.plan.unit(name) or self.gone("Unit", name)

    def gone(self, kind, name):
        by = removed_by(self.repo, self.tip, kind, name)
        fail(f"no {kind.lower()} {name} in plan/{self.label} of {self.repo}" + (f": {by} removed it" if by else ""))


def write(fleet, label, repo, change, subject, body="", act=None, on=(), frm=()):
    """Apply change(Write) to the tip of plan/<label>, check, commit and push it, replaying on a refused push.
    change returns the bolts it touched; each one's conductor is told the subject, unless it wrote it. With act, the
    write is recorded once pushed, naming on and frm and whatever the change added to them."""
    ref, seen = f"plan/{label}", {}
    CONTEXT["label"] = label

    def make(tip):
        tip or fail(f"{repo} has no plan/{label} yet: crew plan init {repo} {label}")
        w = Write(repo, label, tip, read(repo, label, tip))
        before = w.plan.teams()
        touched = change(w) or []
        check(w.plan)
        text = w.plan.text()
        recfix(text, "plan.rec")
        seen.update(before=before, after=w.plan.teams(), touched=touched, quiet=w.quiet, label=label,
                    subject=f"{w.subject or subject} ({agent()})", on=list(on) + w.on, frm=list(frm) + w.frm)
        return text, seen["subject"] + (f"\n\n{body}" if body else "") + "\n"
    sha = land(repo, ref, "plan.rec", make)
    print(f"plan/{label} {sha[:7]}: {seen['subject']}")
    if act:
        record.emit(label, act, seen["on"], seen["frm"], [f"{repo}@{sha}"], record.subject(seen["subject"]))
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


def init(fleet, args):
    p = crew.partition_of(fleet, args.label)
    repo = blueprints_of(p, args.blueprints)

    def make(tip):
        tip is None or fail(f"{repo} already has plan/{p['label']} (at {tip[:7]})")
        recfix(HEADER, "plan.rec")
        return HEADER, f"plan: start plan/{p['label']} ({agent()})\n"
    CONTEXT["label"] = p["label"]
    sha = land(repo, f"plan/{p['label']}", "plan.rec", lambda tip: make(tip))
    print(f"plan/{p['label']} {sha[:7]}: created in {repo}")
    record.emit(p["label"], "plan.init", [f"plan/{p['label']}"], commit=[f"{repo}@{sha}"], why=f"plan: start plan/{p['label']}")


def blueprints_of(p, name):
    """One of a partition's blueprints repos, named as owner/name or by its name."""
    found = [b for b in p["blueprints"] if b == name or b.split("/")[-1] == name]
    len(found) == 1 or fail(f"{name} is not one of {p['label']}'s blueprints repos: " + " ".join(p["blueprints"]))
    return found[0]


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


class Stages:
    """Each unit's stage, read from its kit on its team's host. The first rule that holds is the stage:
    landed, merged, verify, code, approved, review, construct, then ready or waiting by its After units; a unit
    with no bolt is queued, and one whose host does not answer is unknown."""

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
            res["worktree"] = pl["path"] if pl else None
            if name in k["main"]:
                res["stage"] = "landed"
                return res
            if name in k["bolts"].get(b, {}).get("changes", []):
                res["stage"] = "merged"
                return res
            if pl:
                done, total = pl["tasks"] or (0, 0)
                res.update(tasks=pl["tasks"], open=pl["open"])
                if total and done == total:
                    res["stage"] = "verify"
                elif done:
                    res["stage"] = "code"
                elif pl["planning"] and pl["reviewed"]:
                    res["stage"] = "approved"
                elif pl["planning"]:
                    res["stage"] = "review"
                else:
                    res["stage"] = "construct"
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
    """(label, repo, tip, plan) for each plan of the partitions, with tip and plan None where none is started.
    A plan that can't be read is left out and its reason put in errors when that is given, else refused."""
    out = []
    for l in labels:
        for repo in crew.partition_of(fleet, l)["blueprints"]:
            try:
                tip = fetch(repo, f"plan/{l}")
                out.append((l, repo, tip, read(repo, l, tip) if tip else None))
            except Refusal as e:
                if errors is None:
                    raise
                errors[f"plan/{l} of {repo}"] = str(e)
    return out


def locate(fleet, kind, name, label):
    labels, errors = [label] if label else list(fleet["partitions"]), {}
    hits = [h for h in plans(fleet, labels, errors) if h[3] and (h[3].bolt(name) if kind == "Bolt" else h[3].unit(name))]
    hits or fail(f"no {kind.lower()} {name} in the plans of " + ", ".join(labels)
                 + "".join(f"; {k} could not be read: {v}" for k, v in errors.items()))
    len(hits) == 1 or fail(f"{kind.lower()} {name} is in more than one plan: " + ", ".join(f"plan/{h[0]} of {h[1]}" for h in hits) + "; add --label")
    CONTEXT["label"] = hits[0][0]
    return hits[0]


def kit_teams(fleet, kit, label=None):
    return [t for n, t in sorted(fleet["teams"].items()) if t["kit"]["name"] == kit and label in (None, t["label"])]


def plan_for(fleet, kit, label):
    """The plan a kit's work goes in: the blueprints repo of the teams that build it."""
    pairs = sorted({(t["label"], t["blueprints"]["repo"]) for t in kit_teams(fleet, kit, label)})
    pairs or fail(f"no team" + (f" of {label}" if label else "") + f" builds {kit}, so no plan holds its work")
    len(pairs) == 1 or fail(f"{kit}'s work could go in " + ", ".join(f"plan/{l} of {r}" for l, r in pairs) + "; add --label")
    CONTEXT["label"] = pairs[0][0]
    return pairs[0]


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


def free_slot(fleet, t, unit, remove=False):
    """End the agent in the slot a unit or fix holds and free the slot, on the team's host; with remove, a dropped
    unit's worktree, unless it has uncommitted changes, and its branch go too."""
    r = crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], "_free", t["name"], unit, *(["--remove"] if remove else [])))
    if r.returncode:
        print(f"{unit}'s slot on {t['name']} was not freed: " + (r.stderr.strip() or f"exit {r.returncode}"), file=sys.stderr)
    elif r.stdout.strip():
        print(r.stdout.strip())


# --------------------------------------------------------------------------------------------------- bolts

def bolt_new(fleet, a):
    label, repo = plan_for(fleet, a.repo, default_label(fleet, a))
    crew.NAME.match(a.bolt) or fail(f"a bolt's name is lowercase words with dashes, not {a.bolt}")

    def change(w):
        w.plan.bolt(a.bolt) is None or fail(f"plan/{label} already has bolt {a.bolt}")
        r = Rec("Bolt", [("Bolt", a.bolt), ("Repo", a.repo), ("Goal", a.goal)] + [("Source", x) for x in a.source])
        w.plan.insert(r, before=w.bolt(a.before) if a.before else None)
        return [a.bolt]
    write(fleet, label, repo, change, f"plan({a.bolt}): add the bolt", act="bolt.new", on=[f"bolt/{a.bolt}"])


def held_by(plan, team):
    return [b for b in plan.bolts() if b.get("Team") == team]


def bolt_give(fleet, a):
    t = crew.team_of(fleet, a.team)
    label, repo, kit = t["label"], t["blueprints"]["repo"], t["kit"]["name"]
    CONTEXT["label"] = label
    tip = fetch(repo, f"plan/{label}")
    tip or fail(f"{repo} has no plan/{label} yet: crew plan init {repo} {label}")
    plan = read(repo, label, tip)
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
            free or fail(f"plan/{label} has no planned bolt in {kit} for {t['name']}")
            b = free[0]
        b.set("Team", t["name"])
        w.subject = f"plan({b.name()}): give to {t['name']}"
        w.quiet = {t["name"]}  # greeted below, once its bolt's worktree exists
        seen["bolt"] = b.name()
        return [b.name()]
    seen = {}
    sha = write(fleet, label, repo, change, "plan: give a bolt")
    b = seen["bolt"]
    path = f"{t['kit']['dir']}/bolts/{b}"
    make_place(fleet, t, path, f"bolt/{b}", base)
    print(f"{t['name']} holds {b}: bolt/{b} at {path} on {t['machine']}")
    record.emit(label, "bolt.give", [f"bolt/{b}", f"team/{t['name']}"], commit=[f"{repo}@{sha}"], why=f"plan({b}): give to {t['name']}")
    # A team takes a bolt only once its last one has landed or been dropped, so nothing is in flight: a conductor
    # or ops that is up starts again in the new bolt's worktree, with fresh context, before the conductor is greeted.
    up = [r for r in ("conductor", "ops") if crew.agent_status(fleet, f"{t['name']}-{r}")]
    if up:
        r = crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], "restart", t["name"], *up, "--no-greet"))
        said = (r.stdout + r.stderr).strip()
        if said:
            print(said)
    crew.greet(fleet, t["name"], first=f"Your team now holds the bolt {b}. ", wait=90 if "conductor" in up else 0)


def bolt_order(fleet, a):
    label, repo, _, _ = locate(fleet, "Bolt", a.bolt, default_label(fleet, a))

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
    write(fleet, label, repo, change, f"plan({a.bolt}): order the bolt {where}", act="bolt.order", on=[f"bolt/{a.bolt}"])


def bolt_drop(fleet, a):
    label, repo, _, _ = locate(fleet, "Bolt", a.bolt, default_label(fleet, a))

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
    write(fleet, label, repo, change, f"plan({a.bolt}): drop the bolt" + (", its units queued" if a.requeue else ""), a.reason,
          act="bolt.drop", on=[f"bolt/{a.bolt}"])


DROP_BOLT = r"""main=$1 path=$2 bolt=$3
cd "$main" || exit 1
if [ -d "$path" ]; then git worktree remove "$path" || exit 1; fi
if git rev-parse --verify -q "refs/heads/bolt/$bolt" >/dev/null; then
  git branch -d "bolt/$bolt" >/dev/null 2>&1 || echo "bolt/$bolt is kept: it holds commits main does not"
fi
"""


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
    write(fleet, label, repo, change, f"plan({a.bolt}): land the bolt", act="bolt.land", on=[f"bolt/{a.bolt}"])
    said = host_run(fleet, t["machine"], DROP_BOLT, t["kit"]["main"], f"{t['kit']['dir']}/bolts/{a.bolt}", a.bolt)
    print(f"{a.bolt} has landed: its worktree is removed and {t['name']} holds no bolt" + (f". {said}" if said else ""))


# ---------------------------------------------------------------------------------------------------- units

def unit_add(fleet, a):
    label = default_label(fleet, a)
    if a.bolt:
        label, repo, _, plan = locate(fleet, "Bolt", a.bolt, label)
        kit = plan.bolt(a.bolt).get("Repo")
        a.repo in (None, kit) or fail(f"bolt {a.bolt} is in {kit}, not {a.repo}")
    else:
        a.repo or fail("a unit goes in a bolt (--bolt) or in a repo's queue (--repo)")
        (label, repo), kit = plan_for(fleet, a.repo, label), a.repo
    name_free(fleet, label, kit, [a.unit])
    sources = list(a.source)
    if a.signal:
        sources.insert(0, signal_source(fleet, label, repo, a.signal, a.unit))

    def change(w):
        w.plan.unit(a.unit) is None or fail(f"plan/{label} already has unit {a.unit}")
        if a.bolt:
            w.bolt(a.bolt)
        r = Rec("Unit", [("Unit", a.unit), ("Repo", kit)] + ([("Bolt", a.bolt)] if a.bolt else []) + [("Intent", a.intent)]
                + [("After", x) for x in a.after] + [("Source", x) for x in sources])
        if a.before:
            o = w.unit(a.before)
            o.get("Bolt") == a.bolt and o.get("Repo") == kit or fail(f"unit {a.before} is not in {a.bolt or 'the queue of ' + kit}")
            w.plan.insert(r, before=o)
        else:
            w.plan.place_last(r)
        return [a.bolt] if a.bolt else []
    write(fleet, label, repo, change, f"plan({a.bolt or 'queue'}): add {a.unit}", act="unit.add",
          on=[f"unit/{a.unit}", f"bolt/{a.bolt}" if a.bolt else f"queue/{kit}"], frm=[f"signals/{a.signal}"] if a.signal else [])
    if a.signal:
        route(fleet, label, a.signal, a.unit)


def group_of(u):
    """Where a unit is, as an object: its bolt, or its kit's queue."""
    return f"bolt/{u.get('Bolt')}" if u.get("Bolt") else f"queue/{u.get('Repo')}"


def unit_stage(fleet, plan, name):
    u = plan.unit(name)
    b = plan.bolt(u.get("Bolt")) if u.get("Bolt") else None
    return (stages_for(fleet, plan, [b]) if b else Stages(fleet, plan, {})).of(name)


def unit_split(fleet, a):
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))
    s = unit_stage(fleet, plan, a.unit)
    s["stage"] not in LATER or fail(f"unit {a.unit} is in {s['stage']}, so it is no longer split; add the remainder as a new unit instead (crew unit add)")
    s["stage"] != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    name_free(fleet, label, plan.unit(a.unit).get("Repo"), [n for n, _ in a.into])

    def change(w):
        u = w.unit(a.unit)
        u.set("Intent", a.intent)
        prev = u
        for n, intent in a.into:
            w.plan.unit(n) is None or fail(f"plan/{label} already has unit {n}")
            r = Rec("Unit", [("Unit", n), ("Repo", u.get("Repo"))] + ([("Bolt", u.get("Bolt"))] if u.get("Bolt") else [])
                    + [("Intent", intent)] + [("Source", x) for x in u.all("Source")])
            w.plan.insert(r, after=prev)
            prev = r
        return [u.get("Bolt")] if u.get("Bolt") else []
    bolt = plan.unit(a.unit).get("Bolt") or "queue"
    write(fleet, label, repo, change, f"plan({bolt}): split {a.unit} into " + ", ".join(n for n, _ in a.into), act="unit.split",
          on=[f"unit/{a.unit}"] + [f"unit/{n}" for n, _ in a.into], frm=[f"unit/{a.unit}"])


def unit_order(fleet, a):
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))

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
    write(fleet, label, repo, change, f"plan({plan.unit(a.unit).get('Bolt') or 'queue'}): order {a.unit} {where}", act="unit.order",
          on=[f"unit/{a.unit}", group_of(plan.unit(a.unit))])


def unit_after(fleet, a):
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))
    a.none or a.deps or fail("name the units it comes after, or --none")

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
    write(fleet, label, repo, change, f"plan({plan.unit(a.unit).get('Bolt') or 'queue'}): {a.unit} {what}", act="unit.after",
          on=[f"unit/{a.unit}", group_of(plan.unit(a.unit))])


REBASE = r"""cd "$1" || exit 1
orig=$(git rev-parse HEAD)
if git rebase -q --onto "bolt/$3" "bolt/$2" "unit/$4" >/dev/null 2>&1; then
  git branch -q --set-upstream-to="bolt/$3" "unit/$4"; echo "$orig"
else
  git rebase --abort >/dev/null 2>&1; exit 3
fi
"""
UNREBASE = r"""cd "$1" && git reset -q --hard "$2" && git branch -q --set-upstream-to="bolt/$3" "unit/$4" """


def unit_move(fleet, a):
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))
    u = plan.unit(a.unit)
    src, to = u.get("Bolt"), None if a.bolt == "queue" else a.bolt
    to != src or fail(f"unit {a.unit} is already in {src or 'the queue'}")
    if to:
        tb = plan.bolt(to) or fail(f"no bolt {to} in plan/{label} of {repo}")
        tb.get("Repo") == u.get("Repo") or fail(f"bolt {to} is in {tb.get('Repo')}; a unit moves only between bolts of its own repo, {u.get('Repo')}")
    s = unit_stage(fleet, plan, a.unit)
    s["stage"] not in ("merged", "landed") or fail(f"unit {a.unit} has merged into {src}, so it can't move")
    s["stage"] != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    rebased = None
    if s["worktree"]:
        to or fail(f"unit {a.unit} has a worktree at {s['worktree']}, and a queued unit has none")
        ft, tt = fleet["teams"][plan.bolt(src).get("Team")], fleet["teams"].get(plan.bolt(to).get("Team"))
        tt or fail(f"bolt {to} is held by no team, so it has no branch to rebase {a.unit} onto")
        (ft["machine"], ft["kit"]["main"]) == (tt["machine"], tt["kit"]["main"]) or fail(
            f"bolt {to} is built in {tt['kit']['main']} on {tt['machine']}, not in {a.unit}'s checkout; a unit with a worktree moves only within it")
        r = crew.on_machine(fleet, ft["machine"], ["bash", "-c", REBASE, "crew", s["worktree"], src, to, a.unit])
        r.returncode != 3 or fail(f"rebasing {a.unit} onto bolt/{to} conflicts: the move is abandoned and the plan is unchanged")
        r.returncode == 0 or fail(f"rebasing {a.unit} on {ft['machine']} failed: {r.stderr.strip()}")
        rebased = (ft, r.stdout.strip())

    def change(w):
        u = w.unit(a.unit)
        u.get("Bolt") == src or fail(f"unit {a.unit} moved to {u.get('Bolt') or 'the queue'} meanwhile")
        u.drop("After")
        if to:
            w.bolt(to)
            u.set("Bolt", to, after="Repo")
        else:
            u.drop("Bolt")
        w.plan.place_last(u)
        return [b for b in (src, to) if b]
    try:
        kit = u.get("Repo")
        write(fleet, label, repo, change, f"plan({to or 'queue'}): move {a.unit} from {src or 'the queue'}", act="unit.move",
              on=[f"unit/{a.unit}", f"bolt/{to}" if to else f"queue/{kit}"], frm=[f"bolt/{src}" if src else f"queue/{kit}"])
    except Refusal:
        if rebased:
            crew.on_machine(fleet, rebased[0]["machine"], ["bash", "-c", UNREBASE, "crew", s["worktree"], rebased[1], src, a.unit])
        raise


def unit_drop(fleet, a):
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))
    s = unit_stage(fleet, plan, a.unit)
    s["stage"] not in ("merged", "landed") or fail(f"unit {a.unit} has merged into its bolt, so it can't be dropped")
    s["stage"] != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    bolt = plan.unit(a.unit).get("Bolt")

    def change(w):
        u = w.unit(a.unit)
        for o in w.plan.group(u):
            if a.unit in o.all("After"):
                o.fields = [(n, v) for n, v in o.fields if not (n == "After" and v == a.unit)]
        w.plan.remove(u)
        return [bolt] if bolt else []
    write(fleet, label, repo, change, f"plan({bolt or 'queue'}): drop {a.unit}", a.reason, act="unit.drop",
          on=[f"unit/{a.unit}", group_of(plan.unit(a.unit))])
    team = fleet["teams"].get(plan.bolt(bolt).get("Team")) if bolt else None
    if team:
        free_slot(fleet, team, a.unit, remove=True)
    elif s["worktree"]:
        print(f"its worktree stays at {s['worktree']}, on unit/{a.unit}")


APPROVE = r"""cd "$1" || exit 1
git commit -q --allow-empty -m "review($2): approved" --trailer "Reviewed-by: $(git config user.name) <$(git config user.email)>"
git rev-parse HEAD
"""


def unit_approve(fleet, a):
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))
    s = unit_stage(fleet, plan, a.unit)
    if s["stage"] == "approved":
        print(f"unit {a.unit} is already approved")
        return
    s["stage"] == "review" or fail(f"unit {a.unit} is in {s['stage']}: " + (
        "its change's planning is not complete" if s["stage"] == "construct" else
        "it has no change to review yet" if s["stage"] in ("ready", "waiting", "queued") else
        s.get("why", "it is past review")))
    t = fleet["teams"][plan.bolt(plan.unit(a.unit).get("Bolt")).get("Team")]
    sha = host_run(fleet, t["machine"], APPROVE, s["worktree"], a.unit)
    print(f"unit {a.unit} approved: {sha[:7]} on unit/{a.unit}")
    record.emit(label, "unit.approve", [f"unit/{a.unit}"], commit=[f"{t['kit']['repo']}@{sha}"], why=f"review({a.unit}): approved")


# -------------------------------------------------------------------------------------------------- signals

def signal_source(fleet, label, repo, sig, unit):
    """A signal's path as a unit's Source, checked before anything is written: the signal exists in the
    partition's first blueprints repo, where its signals are, it has no move yet, and its route move would pass
    recfix there."""
    srepo = crew.partition_of(fleet, label)["blueprints"][0]
    tip = fetch(srepo, "main") or fail(f"{srepo} has no main")
    show(srepo, tip, f"signals/{sig}.md") is not None or fail(f"no signal {sig} in {srepo}: signals/{sig}.md is not on main")
    moves = show(srepo, tip, "signals/moves.rec")
    moves is not None or fail(f"{srepo} has no signals/moves.rec on main")
    unmoved(moves, sig)
    recfix(moves.rstrip("\n") + "\n\n" + "\n".join(route_move(sig, unit).lines()) + "\n", f"{srepo}'s signals/moves.rec")
    return f"signals/{sig}" if srepo == repo else f"{srepo}:signals/{sig}"


def unmoved(text, sig):
    moved = [m for m in Plan(text).recs("Move") if m.get("Signal") == sig]
    not moved or fail(f"signal {sig} already has its move: {moved[0].get('Move')}")


def route_move(sig, unit):
    return Rec("Move", [("Signal", sig), ("Move", "route"), ("Target", f"unit/{unit}"),
                        ("Date", datetime.date.today().isoformat()), ("By", agent())])


def append(repo, path, rec_lines, message, check=None):
    """Append a record to a recutils file on main, by path, pushed without force and replayed on the new tip
    when someone pushed first: never merged. check(text, tip) runs again on each tip."""
    def make(tip):
        tip or fail(f"{repo} has no main")
        text = show(repo, tip, path)
        text is not None or fail(f"{repo} has no {path} on main")
        if check:
            check(text, tip)
        new = text.rstrip("\n") + "\n\n" + "\n".join(rec_lines) + "\n"
        recfix(new, path)
        return new, message
    return land(repo, "main", path, make)


def route(fleet, label, sig, unit):
    """A signal's one move, route, targeting the unit it became, in signals/moves.rec."""
    srepo = crew.partition_of(fleet, label)["blueprints"][0]
    sha = append(srepo, "signals/moves.rec", route_move(sig, unit).lines(), f"signals({sig}): route to unit/{unit} ({agent()})\n",
                 lambda text, tip: unmoved(text, sig))
    print(f"{srepo} main {sha[:7]}: signal {sig} routed to unit/{unit}")
    record.emit(label, "signal.move", [f"signals/{sig}", f"unit/{unit}"], commit=[f"{srepo}@{sha}"], why=f"signals({sig}): route to unit/{unit}")


CURATION = ("attach", "challenge", "new-territory", "answered", "drop")


def signal_move(fleet, a):
    """Curation's five moves, each written through crew the way the route is: one move per signal, appended to
    signals/moves.rec in the partition's first blueprints repo, never merged."""
    label = default_label(fleet, a) or fail("which partition's signals? add --label " + "|".join(fleet["partitions"]))
    repo = crew.partition_of(fleet, label)["blueprints"][0]
    a.move not in ("attach", "challenge", "answered") or a.target or fail(
        f"a {a.move} move names its target (--target): the intent, claim or record it " + {"attach": "lands on", "challenge": "argues with", "answered": "was settled by"}[a.move])
    a.move != "drop" or a.reason or fail("a drop gives its reason (--reason)")

    def present(text, tip):
        show(repo, tip, f"signals/{a.signal}.md") is not None or fail(f"no signal {a.signal} in {repo}: signals/{a.signal}.md is not on main")
        unmoved(text, a.signal)
    rec = Rec("Move", [("Signal", a.signal), ("Move", a.move)] + ([("Target", a.target)] if a.target else [])
              + ([("Reason", a.reason)] if a.reason else []) + [("Date", datetime.date.today().isoformat()), ("By", agent())])
    sha = append(repo, "signals/moves.rec", rec.lines(), f"signals({a.signal}): {a.move} ({agent()})\n", present)
    print(f"{repo} main {sha[:7]}: signal {a.signal} moved: {a.move}")
    # A target is a pointer, a typed name such as unit/<unit> or a path; anything else could be typed text.
    target = [a.target] if a.target and re.fullmatch(r"[a-z]+/[^\s]+", a.target) else []
    record.emit(label, "signal.move", [f"signals/{a.signal}"] + target, commit=[f"{repo}@{sha}"], why=f"signals({a.signal}): {a.move}")


def signal(fleet, a):
    """A finding written as a signal in the partition's first blueprints repo, in the shape its signals/README.md
    gives: one capture per agent and day, signals/<date>-<agent>/, holding capture.md and one file per signal.
    Committed by those paths alone on main, and pushed; replayed on the new tip when main moved."""
    label = default_label(fleet, a) or fail("which partition's signals? add --label " + "|".join(fleet["partitions"]))
    crew.NAME.match(a.slug) or fail(f"a signal's slug is lowercase words with dashes, not {a.slug}")
    a.slug != "move" or fail("a signal's slug can't be 'move'")
    repo, who, today = crew.partition_of(fleet, label)["blueprints"][0], agent(), datetime.date.today().isoformat()
    capture = f"{today}-" + re.sub(r"[^a-z0-9]+", "-", who.lower()).strip("-")
    seen = {}

    def make(tip):
        tip or fail(f"{repo} has no main")
        listed = git(repo, "ls-tree", "--name-only", f"{tip}:signals/{capture}", check=False)
        names = listed.stdout.split() if listed.returncode == 0 else []
        nn = 1 + max([int(n[:2]) for n in names if re.match(r"^[0-9]{2}-", n)] or [0])
        sid = f"{capture}/{nn:02d}-{a.slug}"
        subject = "[" + ", ".join(x.strip() for x in a.subject.split(",") if x.strip()) + "]" if a.subject else None
        body = "---\n" + f"signal: {sid}\nkind: {a.kind}\nwho: {who}\n" + (f"subject: {subject}\n" if subject else "") + "---\n\n"
        body += a.asserts.strip() + "\n" + (f"\n> {a.excerpt.strip()}\n" if a.excerpt else "")
        cap = (f"---\ncapture: {capture}\nsource: crew\ncaptured_by: {who}\nevent_date: {today}\nimported: {today}\nstatus: read\n"
               f"signals: {nn}\n---\n\n# Findings of {who}, {today}\n\nFindings {who} recorded with crew signal while building, "
               f"each about something outside its own work.\n")
        seen["id"] = sid
        return {f"signals/{capture}/capture.md": cap, f"signals/{sid}.md": body}, f"signals({sid}): {a.slug} ({who})\n"
    sha = land(repo, "main", None, make)
    print(f"{repo} main {sha[:7]}: signal {seen['id']}")
    record.emit(label, "capture", [f"signals/{seen['id']}"], commit=[f"{repo}@{sha}"], why=f"signals({seen['id']}): {a.slug}")


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
        print(f"unit {a.unit} is in plan/{hits[0][0]} of {hits[0][1]}")
        return
    not errors or fail(f"can't tell whether unit {a.unit} is still planned: "
                       + "; ".join(f"{k} could not be read: {v}" for k, v in errors.items()))
    sys.exit(3)


def run_check(fleet, a):
    """Whether a unit's stage may start, its place (made for construct), and the prompt the stage is sent."""
    label, repo, _, plan = locate(fleet, "Unit", a.unit, default_label(fleet, a))
    u = plan.unit(a.unit)
    bolt = u.get("Bolt") or fail(f"unit {a.unit} is queued: move it into a bolt first")
    t = fleet["teams"][plan.bolt(bolt).get("Team")]
    s = Stages(fleet, plan, survey(fleet, [(t["name"], bolt)])).of(a.unit)
    st, place = s["stage"], f"{t['kit']['dir']}/places/{a.unit}"
    st != "unknown" or fail(f"cannot tell unit {a.unit}'s stage: {s.get('why')}")
    words = f" {a.words}" if a.words else ""
    if a.stage == "construct":
        if st == "waiting":
            deps = [d for d in u.all("After") if Stages(fleet, plan, survey(fleet, [(t["name"], bolt)])).of(d)["stage"] not in ("merged", "landed")]
            fail(f"unit {a.unit} is waiting: it comes after " + ", ".join(deps) + ", not yet merged into its bolt")
        st in ("ready", "construct", "review") or fail(f"unit {a.unit} is in {st}; construct is behind it")
        make_place(fleet, t, place, f"unit/{a.unit}", f"bolt/{bolt}", track=True)
        sources = u.all("Source")
        prompt = f"/opsx:propose {a.unit} {u.get('Intent')}" + (" Sources: " + "; ".join(sources) + "." if sources else "") + words
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
    print(sh(PLACE=place, BOLT=bolt, PROMPT=prompt))


def bolt_of_team(fleet, a):
    t = crew.team_of(fleet, a.team)
    tip = fetch(t["blueprints"]["repo"], f"plan/{t['label']}") or fail(f"{t['blueprints']['repo']} has no plan/{t['label']} yet")
    held = held_by(read(t["blueprints"]["repo"], t["label"], tip), t["name"])
    held or fail(f"{t['name']} holds no bolt: crew bolt give {t['name']}")
    print(sh(BOLT=held[0].name()))


def place_cmd(fleet, a):
    make_place(fleet, crew.team_of(fleet, a.team), a.path, a.branch, a.base, track=True)


def slot_stages(fleet, t):
    """Each slot of the team on this host that holds a unit or fix: what it holds and that work's stage, read from the
    kit alone, with its tasks done and total where its change has a task list."""
    path = pathlib.Path.home() / f".local/state/{t['name']}-team/slots"
    held = [l.split() for l in (path.read_text().splitlines() if path.exists() else []) if l.strip()]
    if not held:
        return []
    k = survey(fleet, [(t["name"], None)]).get(t["machine"], {})
    kit = k.get("kits", {}).get(t["kit"]["main"], {}) if k.get("ok") else {}
    out = []
    for slot, kind, name, place in held:
        stage, counts = "unknown", None
        if kit.get("ok") and kind == "fix":
            f = next((f for f in kit["fixes"] if f["fix"] == name), None)
            stage = ("merged" if f["merged"] else "fix") if f else "none"
        elif kit.get("ok"):
            pl = kit["places"].get(name)
            if name in kit["main"]:
                stage = "landed"
            elif pl and pl["bolt"] and name in kit["bolts"].get(pl["bolt"], {}).get("changes", []):
                stage = "merged"
            elif pl:
                done, total = pl["tasks"] or (0, 0)
                stage = ("verify" if total and done == total else "code" if done else
                         "approved" if pl["planning"] and pl["reviewed"] else "review" if pl["planning"] else "construct")
                counts = f"{done}/{total}" if pl["tasks"] else None
            else:
                stage = "none"
        out.append(dict(slot=slot, kind=kind, name=name, stage=stage, counts=counts, place=place))
    return out


def slots_cmd(fleet, a):
    """Each slot of the team on this host: what it holds and that work's stage, read from the kit alone."""
    for s in slot_stages(fleet, crew.team_of(fleet, a.team)):
        tasks = s["counts"] if s["counts"] and s["stage"] in ("code", "verify") else "-"
        print(s["slot"], s["kind"], s["name"], s["stage"], tasks, s["place"])


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
            why = f"fix({name[4:]}): {stage} ended" if fix else f"unit({name}): {stage} ended"
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
                lines.append(f"plan/{p['label']}  {pl['repo']}  not started: crew plan init {pl['repo']} {p['label']}")
                continue
            lines.append(f"plan/{p['label']} {pl['plan'][:7]}  {pl['repo']}")
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

def parser():
    ap = argparse.ArgumentParser(prog="crew", add_help=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("plan").add_subparsers(dest="sub", required=True)
    i = pl.add_parser("init")
    i.add_argument("blueprints")
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
    x.add_argument("--label")
    x = un.add_parser("split")
    x.add_argument("unit")
    x.add_argument("intent")
    x.add_argument("--into", nargs=2, action="append", required=True, metavar=("UNIT", "INTENT"))
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
    x.add_argument("--label")
    x = un.add_parser("drop")
    x.add_argument("unit")
    x.add_argument("reason")
    x.add_argument("--label")
    x = un.add_parser("approve")
    x.add_argument("unit")
    x.add_argument("--label")

    x = sub.add_parser("signal-move", prog="crew signal move")
    x.add_argument("signal", metavar="id")
    x.add_argument("move", choices=CURATION)
    x.add_argument("--target")
    x.add_argument("--reason")
    x.add_argument("--label")
    x = sub.add_parser("signal")
    x.add_argument("slug")
    x.add_argument("asserts")
    x.add_argument("--kind", choices=("constraint", "ask", "question", "commitment", "reaction"), default="constraint")
    x.add_argument("--subject", help="tags, separated by commas")
    x.add_argument("--excerpt")
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
    ("plan", "init"): init, ("bolts", None): bolts_view,
    ("bolt", "new"): bolt_new, ("bolt", "give"): bolt_give, ("bolt", "order"): bolt_order, ("bolt", "drop"): bolt_drop,
    ("bolt", "land"): bolt_land,
    ("unit", "add"): unit_add, ("unit", "split"): unit_split, ("unit", "order"): unit_order, ("unit", "after"): unit_after,
    ("unit", "move"): unit_move, ("unit", "drop"): unit_drop, ("unit", "approve"): unit_approve,
    ("_team-of", None): team_of_unit, ("_run", None): run_check, ("_bolt-of", None): bolt_of_team, ("_place", None): place_cmd,
    ("_slots", None): slots_cmd, ("_in-plan", None): in_plan, ("signal", None): signal, ("signal-move", None): signal_move,
    ("_ends", None): stage_ends,
}
# The act a command that moves work records, done or refused. A command that only reads records nothing.
ACTS = {
    ("plan", "init"): "plan.init", ("bolt", "new"): "bolt.new", ("bolt", "give"): "bolt.give", ("bolt", "order"): "bolt.order",
    ("bolt", "drop"): "bolt.drop", ("bolt", "land"): "bolt.land", ("unit", "add"): "unit.add", ("unit", "split"): "unit.split",
    ("unit", "order"): "unit.order", ("unit", "after"): "unit.after", ("unit", "move"): "unit.move", ("unit", "drop"): "unit.drop",
    ("unit", "approve"): "unit.approve", ("signal", None): "capture", ("signal-move", None): "signal.move",
    ("_run", None): "stage.start",
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
    if a.cmd == "plan":
        out.append(f"plan/{a.label}")
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
    if argv[:2] == ["signal", "move"]:  # crew signal move <id> <move>, beside crew signal <slug> "<asserts>"
        argv = ["signal-move"] + argv[2:]
    args = parser().parse_args(argv)
    fleet = crew.load()
    key = (args.cmd, getattr(args, "sub", None))
    try:
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
