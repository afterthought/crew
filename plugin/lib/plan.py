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

A command that names no partition reads them all, or the agent's own (CREW_LABEL); --label names one.
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
        self.repo, self.label, self.tip, self.plan, self.subject = repo, label, tip, plan, None

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

    def make(tip):
        tip or fail(f"{repo} has no plan/{label} yet: crew plan init {repo} {label}")
        w = Write(repo, label, tip, read(repo, label, tip))
        before = w.plan.teams()
        touched = change(w) or []
        check(w.plan)
        text = w.plan.text()
        recfix(text, "plan.rec")
        seen.update(before=before, after=w.plan.teams(), touched=touched, subject=f"{w.subject or subject} ({agent()})")
        return text, seen["subject"] + (f"\n\n{body}" if body else "") + "\n"
    sha = land(repo, ref, "plan.rec", make)
    print(f"plan/{label} {sha[:7]}: {seen['subject']}")
    notify(fleet, seen, seen["subject"])
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


# ------------------------------------------------------------------------------------------ the kits, per host

GATHER = (LIB / "gather.py").read_text()
LATER = ("code", "verify", "merged", "landed")


def survey(fleet, held):
    """Read the kits of every host holding active bolts, one call per host. held is [(team, bolt)]. The answer is
    per host: its kits by main checkout, or why it did not answer."""
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
        r = crew.on_machine(fleet, host, ["python3", "-", json.dumps({"kits": list(kits.values())})], input=GATHER)
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
    return hits[0]


def kit_teams(fleet, kit, label=None):
    return [t for n, t in sorted(fleet["teams"].items()) if t["kit"]["name"] == kit and label in (None, t["label"])]


def plan_for(fleet, kit, label):
    """The plan a kit's work goes in: the blueprints repo of the teams that build it."""
    pairs = sorted({(t["label"], t["blueprints"]["repo"]) for t in kit_teams(fleet, kit, label)})
    pairs or fail(f"no team" + (f" of {label}" if label else "") + f" builds {kit}, so no plan holds its work")
    len(pairs) == 1 or fail(f"{kit}'s work could go in " + ", ".join(f"plan/{l} of {r}" for l, r in pairs) + "; add --label")
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


def free_slot(fleet, t, unit):
    """End the agent in the slot a unit or fix holds and free the slot, on the team's host."""
    r = crew.on_machine(fleet, t["machine"], ["bash", crew.crew_at(fleet, t["machine"]), "_free", t["name"], unit])
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
        return []
    write(fleet, label, repo, change, f"plan({a.bolt}): add the bolt")


def held_by(plan, team):
    return [b for b in plan.bolts() if b.get("Team") == team]


def bolt_give(fleet, a):
    t = crew.team_of(fleet, a.team)
    label, repo, kit = t["label"], t["blueprints"]["repo"], t["kit"]["name"]
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
        seen["bolt"] = b.name()
        return [b.name()]
    seen = {}
    write(fleet, label, repo, change, "plan: give a bolt")
    b = seen["bolt"]
    path = f"{t['kit']['dir']}/bolts/{b}"
    make_place(fleet, t, path, f"bolt/{b}", "main")
    print(f"{t['name']} holds {b}: bolt/{b} at {path} on {t['machine']}")


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
    write(fleet, label, repo, change, f"plan({a.bolt}): order the bolt {where}")


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
        w.plan.remove(b)
        return [a.bolt]
    write(fleet, label, repo, change, f"plan({a.bolt}): drop the bolt" + (", its units queued" if a.requeue else ""), a.reason)


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

    def change(w):
        w.bolt(a.bolt)
        late = [u.name() for u in w.plan.units_of(a.bolt) if u.name() not in units]
        not late or fail(f"unit {late[0]} was added to {a.bolt} since it was checked; it has not landed")
        for u in w.plan.units_of(a.bolt):
            w.plan.remove(u)
        w.plan.remove(w.plan.bolt(a.bolt))
        return [a.bolt]
    write(fleet, label, repo, change, f"plan({a.bolt}): land the bolt")
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
        sources.insert(0, signal_source(fleet, label, repo, a.signal))

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
    write(fleet, label, repo, change, f"plan({a.bolt or 'queue'}): add {a.unit}")
    if a.signal:
        route(fleet, label, a.signal, a.unit)


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
    write(fleet, label, repo, change, f"plan({bolt}): split {a.unit} into " + ", ".join(n for n, _ in a.into))


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
    write(fleet, label, repo, change, f"plan({plan.unit(a.unit).get('Bolt') or 'queue'}): order {a.unit} {where}")


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
    write(fleet, label, repo, change, f"plan({plan.unit(a.unit).get('Bolt') or 'queue'}): {a.unit} {what}")


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
        write(fleet, label, repo, change, f"plan({to or 'queue'}): move {a.unit} from {src or 'the queue'}")
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
    write(fleet, label, repo, change, f"plan({bolt or 'queue'}): drop {a.unit}", a.reason)
    team = fleet["teams"].get(plan.bolt(bolt).get("Team")) if bolt else None
    if team:
        free_slot(fleet, team, a.unit)
    if s["worktree"]:
        print(f"its worktree stays at {s['worktree']}, on unit/{a.unit}")


APPROVE = r"""cd "$1" || exit 1
git commit -q --allow-empty -m "review($2): approved" --trailer "Reviewed-by: $(git config user.name) <$(git config user.email)>"
git rev-parse --short HEAD
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
    print(f"unit {a.unit} approved: {sha} on unit/{a.unit}")


# -------------------------------------------------------------------------------------------------- signals

def signal_source(fleet, label, repo, sig):
    """A signal's path as a unit's Source, checked to exist and to have no move yet in the partition's first
    blueprints repo, where its signals are."""
    srepo = crew.partition_of(fleet, label)["blueprints"][0]
    tip = fetch(srepo, "main") or fail(f"{srepo} has no main")
    show(srepo, tip, f"signals/{sig}.md") is not None or fail(f"no signal {sig} in {srepo}: signals/{sig}.md is not on main")
    moved = [m for m in Plan(show(srepo, tip, "signals/moves.rec") or "").recs("Move") if m.get("Signal") == sig]
    not moved or fail(f"signal {sig} already has its move: {moved[0].get('Move')}")
    return f"signals/{sig}" if srepo == repo else f"{srepo}:signals/{sig}"


def append(repo, path, rec_lines, message, check=None):
    """Append a record to a recutils file on main, by path, pushed without force and replayed on the new tip
    when someone pushed first."""
    def make(tip):
        tip or fail(f"{repo} has no main")
        text = show(repo, tip, path)
        text is not None or fail(f"{repo} has no {path} on main")
        if check:
            check(text)
        new = text.rstrip("\n") + "\n\n" + "\n".join(rec_lines) + "\n"
        recfix(new, path)
        return new, message
    return land(repo, "main", path, make)


def route(fleet, label, sig, unit):
    """A signal's one move, route, targeting the unit it became, in signals/moves.rec."""
    srepo = crew.partition_of(fleet, label)["blueprints"][0]

    def unmoved(text):
        moved = [m for m in Plan(text).recs("Move") if m.get("Signal") == sig]
        not moved or fail(f"signal {sig} already has its move: {moved[0].get('Move')}")
    rec = Rec("Move", [("Signal", sig), ("Move", "route"), ("Target", f"unit/{unit}"),
                       ("Date", datetime.date.today().isoformat()), ("By", agent())])
    sha = append(srepo, "signals/moves.rec", rec.lines(), f"signals({sig}): route to unit/{unit} ({agent()})\n", unmoved)
    print(f"{srepo} main {sha[:7]}: signal {sig} routed to unit/{unit}")


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
    return ap


COMMANDS = {
    ("plan", "init"): init, ("bolts", None): bolts_view,
    ("bolt", "new"): bolt_new, ("bolt", "give"): bolt_give, ("bolt", "order"): bolt_order, ("bolt", "drop"): bolt_drop,
    ("bolt", "land"): bolt_land,
    ("unit", "add"): unit_add, ("unit", "split"): unit_split, ("unit", "order"): unit_order, ("unit", "after"): unit_after,
    ("unit", "move"): unit_move, ("unit", "drop"): unit_drop, ("unit", "approve"): unit_approve,
}


def main(argv):
    need_recutils()
    args = parser().parse_args(argv)
    fleet = crew.load()
    COMMANDS[(args.cmd, getattr(args, "sub", None))](fleet, args)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
