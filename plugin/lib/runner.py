"""crew's side of the runner's interface (flywheel-runner core.2): how a team crosses to Flume, one team at a time
(record 0050 parts 2 and 3, roles.8), and the decisions over a crossed team's work.

A team's path is read from its setting in teams.json (crew.load's `flume`, False or a Flume stream) and the bolts the
plan gives it, a bolt given while the team was crossed marked `Path: flume`: today's, crossed or due (team_path). A due
team is given no new bolt (due_refusal); its bolts go on as they were given until each lands or is dropped, and the
landing or drop that leaves it holding none of its old path makes its path its setting's. A crossed team runs no
standing agent and has no slots: its conductor and ops are due an end (cross_due), and every standing-agent or slot
command of it is refused (crossed_refusal).

crew asks a host's runner for work by requests on the flywheel's branch, requests.rec (REQUESTS), each appended in the
commit of the plan write that occasions it and checked by crew's own rules (request_refusal, append_refusal) as well as
recfix; each runner answers on a branch of its own, <label>/runner/<host>, which crew fetches with <label>/main and
reads (host_read) and never writes (state.5). A crossed piece's stage is read from its launch, the runner's answer and
Flume's status of its place as the runner carried it (stage_of, flume_facts).

A give to a crossed team launches its bolt whole, refused only where no runner answers (runnerless), and every plan
write reaches the places a crossed bolt launched as its own act: added work launched, dropped work dropped, a dependent
launched again when what it waits on is (reach), an amendment a retry of construct or a launch anew (amending), and a
move, split or change of After of launched work refused (launched_refusal); each launch's priority follows its bolt's
place in the plan (priorities). A bolt planned in a crossed team's kit is the dispatchers' to give it (takers).

A place that stopped short asking, or waits on its caller, is answered by a retry with the answer's words (answer_retry).
A fix on a crossed bolt is a launch of Flume's fix kind on the bolt's branch (fix_launch), dropped by a drop
(fix_drop_refusal), merged and waited on by Flume alone (fix_flume_refusal), and holds the bolt's landing while it is in
flight (fixes_in_flight); a crossed bolt whose landing sluice refused for a conflict with main takes main in by one
(take_main). A red main's fix is a launch of the fix kind on main with its submission held, on the host of a crossed
team building the kit (main_fixer, main_fix_launch), a bolt of one chore where none does (state.3).

Each is a function of plain facts (code.7); plan.py, crew.py and hold.py read the facts and act on what they decide.
This module imports nothing outside the standard library and crew's own modules (code.1)."""
import json
import re

# How a bolt was given, by its Path on the plan's Bolt record, as crew says it.
GIVEN = {"flume": "through Flume", None: "on today's path"}


def team_path(setting, held):
    """A team's path (Decision 2 of teams-cross-to-flume-as-their-bolts-land), from its setting (crew.load's `flume`,
    False or a stream's name) and the Path of each bolt the plan gives it ("flume", or None for one given on today's
    path): ("today", None) while its setting is off and it holds no bolt given through Flume; ("crossed", None) while
    its setting names a stream and it holds no bolt given on today's path, or none at all; and ("due", "cross") or
    ("due", "back") while the setting and a bolt it holds disagree, due to cross while the setting names a stream and
    due back while it is off."""
    if setting is False:
        return ("due", "back") if "flume" in held else ("today", None)
    return ("due", "cross") if any(p != "flume" for p in held) else ("crossed", None)


def path_of(plan, t):
    """A team's path (team_path) as a plan has it: t's setting and the Path of each bolt the plan gives t."""
    return team_path(t["flume"], [b.get("Path") for b in plan.bolts() if b.get("Team") == t["name"]])


def due_refusal(team, path, held):
    """Why a give hands a due team no bolt (Decision 2), or None for a team that is not due: held is each bolt the team
    holds as (name, its Path), each named with the path it was given on, and the give is refused until those of its old
    path have landed or been dropped, since nothing moves a bolt from one path to the other and a team crosses empty."""
    kind, way = path
    if kind != "due":
        return None
    groups = {}
    for name, p in held:
        groups.setdefault(p, []).append(name)
    holds = " and ".join(f"{' and '.join(names)}, given {GIVEN[p]}" for p, names in groups.items())
    old = groups.get(None if way == "cross" else "flume", [])
    towards = "due to cross to Flume" if way == "cross" else "due back to today's path"
    return (f"{team} is {towards}, so it is given no bolt now: it holds {holds}, and is given its next bolt once "
            + " and ".join(old) + (" has" if len(old) == 1 else " have") + " landed or been dropped")


def runnerless(label, host, tips):
    """Why a give to a crossed team on a host is refused for want of a runner (Decision 5), or None: tips, the hosts
    whose runner branch the partition's state repository holds (plan.runner_tips), and a host with none has no runner
    answering there, so nothing would launch the bolt's work."""
    if host in tips:
        return None
    return (f"no runner answers on {host}: {runner_branch(label, host)} does not exist, so nothing would launch the bolt's "
            "work there; a give to a team crossed to Flume waits for the runner (flywheel-runner) to serve the partition there")


def cross_due(path, up):
    """What a team's crossing owes its standing agents (Decision 3), from facts: its path (team_path) and its standing
    roles that are up. Returns (the roles due an end, whether the crossing is whole): once it has crossed, every role
    up is due an end, never a restart, and the crossing is whole once none is up, when the act that ended the last
    closes its workspaces and records team.cross. A team not crossed owes nothing."""
    if path[0] != "crossed":
        return [], False
    return list(up), not up


def crossed_refusal(team, path, stream, host, what):
    """What crew says refusing crew <what> of a team (Decision 15), or None when the team has not crossed: a crossed
    team runs no conductor, ops or slot, its work running in Flume places on its host, which crew bolts shows."""
    if path[0] != "crossed":
        return None
    return (f"{team} has crossed to Flume: its work runs in Flume places on {host}, in stream {stream}, and crew bolts shows "
            f"them; it runs no conductor, ops or slot, so crew {what} has nothing of it to act on")


# ------------------------------------------------------------------------------------------------- the requests

REQUESTS = """\
# crew's requests of each host's runner: a launch of a Flume place for a
# crossed team's work, or a retry, drop or priority of a place launched.
# Written only by crew, each in the commit of the plan write that occasions it;
# numbered once, and never changed or removed. Each host's runner answers on
# <label>/runner/<host> of this repository, which crew reads and never writes.

%rec: Request
%doc: A request of Host's runner for Work: a launch of a Flume place of Kind named Name, cut from Base of Repo, or a retry, drop or priority of the place the launch Of names launched.
%key: Request
%type: Request,Of,After,Priority int
%type: Act enum launch retry drop priority
%type: Kind enum change chore fix
%type: Hold enum submission
%type: Submission bool
%type: Host regexp /^[a-z0-9][a-z0-9-]*$/
%type: Date date
%mandatory: Request Act Host Work Date By
%allowed: Request Act Host Work Repo Kind Name Base Stream Priority Intent Recipient Hold After Brief Of Stage Submission Words Date By
"""
# A request's fields in the order requests.rec writes them (Decision 4's table).
FIELDS = ("Request", "Act", "Host", "Work", "Repo", "Kind", "Name", "Base", "Stream", "Priority", "Intent", "Recipient", "Hold",
          "After", "Brief", "Of", "Stage", "Submission", "Words", "Date", "By")
# What every request carries, and, by its act, what it must carry beside them and what else it may.
COMMON = ("Request", "Act", "Host", "Work", "Date", "By")
ACTS = {
    "launch": (("Repo", "Kind", "Name", "Base", "Stream", "Priority", "Intent", "Recipient", "Brief"), ("Hold", "After")),
    "retry": (("Of",), ("Stage", "Submission", "Words")),
    "drop": (("Of",), ()),
    "priority": (("Of", "Priority"), ()),
}
# The work a request serves, as crew names it: a unit, a chore, a fix on a bolt or a fix of a kit's main.
WORK = re.compile(r"^(?:unit/N|chore/N|fix/N/N|fix/main/N/N)$".replace("N", "[a-z0-9][a-z0-9-]*"))


def number(v):
    """A record's number field as an int, None when it holds none or no number."""
    return int(v) if isinstance(v, str) and v.isdigit() else None


def next_request(requests):
    """The number the next request takes (Decision 4): one past the highest requests.rec holds, 1 for the first."""
    return max((number(r.get("Request")) or 0 for r in requests), default=0) + 1


def request_fields(n, act, host, work, given, date, by):
    """A request's fields in requests.rec's order (FIELDS), as (field, value): its number, act, host and work, what the
    command gives (given, {field: a value or a list of them, None or False for none and True written yes}), and when
    and by whom. A field FIELDS does not hold goes last, for request_refusal to name."""
    given = dict(given, Request=n, Act=act, Host=host, Work=work, Date=date, By=by)
    out = []
    for f in list(FIELDS) + sorted(set(given) - set(FIELDS)):
        v = given.get(f)
        for x in v if isinstance(v, (list, tuple)) else [v]:
            if x is not None and x is not False:
                out.append((f, "yes" if x is True else str(x)))
    return out


def request_refusal(requests, new):
    """Why crew's own rules refuse a request (plan.1), beyond what recfix checks of requests.rec, or None: requests, the
    file's records before it, and new, the request appended, each a record of the plan's kind (plan.Rec). A request is
    the next by number; its work is a unit's, a chore's or a fix's as crew names them; it carries every field its act
    needs and none its act does not take; a retry, drop or priority names by Of a launch of the same work on the same
    host; a launch's After names launches on the same base, the work of the same bolt; a fix of main holds its
    submission; and a retry starts a stage again or submits again, not both (Decision 4)."""
    n, act, work, host = new.get("Request"), new.get("Act"), new.get("Work"), new.get("Host")
    want = next_request(requests)
    if number(n) != want:
        return (f"request {n} is not the next in requests.rec: it holds "
                + (f"requests 1 to {want - 1}" if want > 2 else "request 1" if want == 2 else "none") + f", so the next is {want}")
    if act not in ACTS:
        return f"request {n} is a {act}, and a request is a launch, a retry, a drop or a priority"
    need, may = ACTS[act]
    missing = [f for f in COMMON + need if not new.get(f)]
    if missing:
        return (f"{act} {n} for {work} names no {' and no '.join(missing)}: a {act} carries "
                + ", ".join(COMMON + need))
    extra = sorted({f for f, _ in new.fields if f not in COMMON + need + may})
    if extra:
        return f"{act} {n} for {work} carries {', '.join(extra)}, which a {act} does not take"
    if not WORK.match(work):
        return f"{act} {n} serves {work}, and a request serves unit/<unit>, chore/<chore>, fix/<bolt>/<name> or fix/main/<kit>/<name>"
    by = {r.get("Request"): r for r in requests}
    if act != "launch":
        of = by.get(new.get("Of"))
        if of is None or of.get("Act") != "launch":
            return f"{act} {n} for {work} names request {new.get('Of')}, which is no launch" + (
                "" if of is not None else ": requests.rec does not hold it")
        if (of.get("Work"), of.get("Host")) != (work, host):
            return (f"{act} {n} for {work} on {host} names launch {of.get('Request')}, which is {of.get('Work')}'s on "
                    f"{of.get('Host')}")
    for a in new.all("After"):
        l = by.get(a)
        if l is None or l.get("Act") != "launch":
            return f"launch {n} of {work} comes after request {a}, which is no launch"
        if l.get("Base") != new.get("Base"):
            return (f"launch {n} of {work} on {new.get('Base')} comes after launch {a}, which is on {l.get('Base')}: an After "
                    "names work of the same bolt")
    if act == "launch" and work.startswith("fix/main/") and new.get("Hold") != "submission":
        return (f"launch {n} of {work} is a fix of main, which is launched with its submission held (Hold: submission) "
                "until the user's send (state.3)")
    if act == "retry" and new.get("Stage") and new.get("Submission"):
        return f"retry {n} of {work} names stage {new.get('Stage')} and the submission: a retry starts a stage again or submits again"
    return None


def append_refusal(before, after):
    """Why a write is refused for changing requests.rec other than by appending to it (Decision 4: a request is never
    changed or removed), or None: before and after, the file's records at the tip and as the write leaves them, each
    as its fields, a list of (field, value)."""
    for i, old in enumerate(before):
        n = dict(old).get("Request")
        if i >= len(after) or list(after[i]) != list(old):
            return (f"request {n} would be {'removed from' if i >= len(after) else 'changed in'} requests.rec, and a request "
                    "is never changed or removed: a later request retries, drops or reprioritises what it launched")
    return None


# ------------------------------------------------------------------------------------------ the runners' branches

def runner_branch(label, host):
    """The branch a host's runner answers a partition's requests on, in the partition's state repository (Decision 4)."""
    return f"{label}/runner/{host}"


# A runner's branch as crew reads it: each file and the record set it holds, written by the host's runner alone with
# these descriptors (flywheel-runner core.2), and never by crew (state.5). runner.rec names the host and the runner
# serving the partition there, so a branch that exists says a runner answers; answers.rec where each request it has
# read stands; places.rec Flume's status of each place it launched, `flume status --json <place>`'s answer on one line
# as Flume gave it (flywheel-runner core.1), kept after Flume tidies the place until its work has left crew's plan.
RUNNER = """\
%rec: Runner
%key: Host
%type: Since date
%mandatory: Host Version Since
%allowed: Host Version Since
"""
ANSWERS = """\
%rec: Answer
%key: Request
%type: Request int
%type: Outcome enum held launched done refused
%type: At date
%mandatory: Request Outcome At
%allowed: Request Outcome Place Words At
"""
PLACES = """\
%rec: Place
%key: Request
%type: Request int
%type: At date
%mandatory: Request Place At Status
%allowed: Request Place At Status
"""
FILES = {"runner.rec": "Runner", "answers.rec": "Answer", "places.rec": "Place"}


def host_read(label, host, tip, files, refused):
    """A host's runner as crew reads it from its branch (Decision 4), from facts: tip, the branch's commit in crew's
    cache, None when no such branch exists; files, each of FILES parsed at the tip as the plan is (plan.Plan), None
    for one the tip lacks, answers and places then none; refused, recfix's words for each file it refused. Returns
    the reading, its host, branch and tip, with either why it could not be read, which hides this host's work alone
    (read.1, read.3), or the runner's record, each answer by its request's number and each place by its launch's: the
    place's path, when the runner carried it, and its Status parsed, or with why it could not be."""
    branch = runner_branch(label, host)
    out = {"host": host, "branch": branch, "tip": tip, "why": None}
    if tip is None:
        return dict(out, why=f"no runner answers on {host}: {branch} does not exist")
    at = f"{branch} at {tip[:7]}"
    for name, kind in FILES.items():
        if name in refused:
            return dict(out, why=f"{host}'s runner can't be read: {at}: {refused[name]}")
        if files.get(name) is not None and files[name].recs(None):
            return dict(out, why=f"{host}'s runner can't be read: {at}: {name} holds a record before its %rec: {kind}")
    run = files["runner.rec"].recs("Runner") if files.get("runner.rec") is not None else []
    if len(run) != 1 or run[0].get("Host") != host:
        return dict(out, why=f"{host}'s runner can't be read: {at}: " + (
            "it holds no runner.rec" if files.get("runner.rec") is None else
            f"runner.rec holds {len(run)} Runner records, and names one" if len(run) != 1 else
            f"runner.rec names host {run[0].get('Host')}"))
    answers, places = {}, {}
    for name, kind, into in (("answers.rec", "Answer", answers), ("places.rec", "Place", places)):
        for r in files[name].recs(kind) if files.get(name) is not None else []:
            n = number(r.get("Request"))
            if n is None or n in into:
                return dict(out, why=f"{host}'s runner can't be read: {at}: {name} holds "
                            + ("a record with no request's number" if n is None else f"request {n} twice"))
            into[n] = r
    for n, r in places.items():
        try:
            status, why = json.loads(r.get("Status") or ""), None
        except ValueError as e:
            status, why = None, f"{at}: places.rec's status of the place of request {n} is no JSON ({e})"
        places[n] = {"place": r.get("Place"), "at": r.get("At"), "status": status, "why": why}
    return dict(out, runner=run[0], answers=answers, places=places)


def of_host(reads, label, host):
    """A host's reading among a partition's (host_read's, by host), or why none is: no runner branch for it exists."""
    return reads.get(host) or host_read(label, host, None, {}, {})


# ------------------------------------------------------------------------------------------- a crossed piece's stage

def launch_of(requests, work):
    """The launch a piece's stage is read from (Decision 8): the newest launch request of the work that no drop request
    names, None when it has none; requests in requests.rec's order."""
    dropped = {r.get("Of") for r in requests if r.get("Act") == "drop"}
    return next((r for r in reversed(requests)
                 if r.get("Act") == "launch" and r.get("Work") == work and r.get("Request") not in dropped), None)


def after_work(requests, launch):
    """The work each launch a launch comes after serves, as its waiting stage names it (Decision 5)."""
    by = {r.get("Request"): r for r in requests}
    return [by[a].get("Work") if a in by else f"request {a}" for a in launch.all("After")]


def at(d, *path):
    """The value at a path of keys in a JSON value, None where any step is absent or not an object (read.2)."""
    for k in path:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def tagged(v):
    """A Rust enum as Flume's JSON gives it (serde's external tag): its variant's name and its fields, ("name", {}) for
    a unit variant given as its name and ("name", fields) for one given as {name: fields}; (None, {}) for neither."""
    if isinstance(v, str):
        return v, {}
    if isinstance(v, dict) and len(v) == 1:
        (k, f), = v.items()
        return k, f if isinstance(f, dict) else {}
    return None, {}


def text(v):
    """A JSON string as text, None for anything else (read.2)."""
    return v if isinstance(v, str) else None


def flume_facts(status, place):
    """What crew reads of Flume's status of a place (Decision 8), as flume 0.3.6's `flume status --json <place>` gives it
    and the runner carried it (tests/py/flume-0.3.6/), each field guarded so one absent or of another shape reads None
    and never becomes text (read.2): the place's entry, the one at its path or, tidied, at <path>@<when>; its phase
    (live, making, over, gone or tidied) and, once its work is over, how (landed, dropped or done) and the commit it
    landed; its current stage, that stage's state and end; its tasks, ticked and in all; its submission: the merge
    queue's entry's number and state, why Flume could not read it, the pull request its last submit opened, how often
    it was submitted and sent back, the last verdict and its words, and whether it is held; what it waits on its caller
    for, the stage named, why and Flume's words, and whether it is stalled. None when status holds no entry for it."""
    places = at(status, "status", "places")
    mine = [p for p in places if isinstance(p, dict) and isinstance(p.get("place"), str)
            and (p["place"] == place or p["place"].startswith(f"{place}@"))] if isinstance(places, list) and place else []
    if not mine:
        return None
    p = mine[-1]
    phase, pf = tagged(p.get("phase"))
    over, of = tagged(pf.get("over")) if phase in ("over", "gone", "tidied") else (None, {})
    current = text(p.get("current"))
    stage = next((s for s in p.get("stages") or [] if isinstance(s, dict) and s.get("name") == current), None) \
        if isinstance(p.get("stages"), list) else None
    tasks = p.get("tasks")
    tasks = (sum(1 for t in tasks if t["ticked"]), len(tasks)) if isinstance(tasks, list) and all(
        isinstance(t, dict) and isinstance(t.get("ticked"), bool) for t in tasks) else None
    sub = p.get("submission") if isinstance(p.get("submission"), dict) else {}
    read, rf = tagged(sub.get("read"))
    entry = at(rf, "submission") if read == "found" else None
    verdict, vf = tagged(sub.get("verdict"))
    count = lambda v: v if isinstance(v, int) and not isinstance(v, bool) else None
    waiting = p.get("waiting_on") if isinstance(p.get("waiting_on"), dict) else {}
    return {
        "phase": phase, "over": over, "commit": text(of.get("commit")) if over == "landed" else None,
        "current": current, "state": text(at(stage, "state")), "end": at(stage, "end") if isinstance(at(stage, "end"), dict) else {},
        "tasks": tasks,
        "entry": text(at(entry, "id")), "entry_state": tagged(at(entry, "state"))[0],
        "unread": text(rf.get("reason")) if read == "could_not_read" else None,
        "request": text(sub.get("request")), "submits": count(sub.get("submits")), "send_backs": count(sub.get("send_backs")),
        "verdict": verdict, "verdict_words": text(vf.get("words")) or text(vf.get("reason")), "held": sub.get("held") is True,
        "waiting": text(waiting.get("why")), "waiting_stage": text(waiting.get("stage")), "waiting_words": text(waiting.get("words")),
        "stalled": p.get("stalled") is True,
    }


def stage_of(work, launch, answer, place, read, after=()):
    """A crossed piece's stage (Decision 8), from plain facts: work, as requests name it (unit/<u>, chore/<c>,
    fix/<bolt>/<name>, fix/main/<kit>/<name>); launch, its newest launch not dropped (launch_of), None for none;
    answer, the runner's answer to that launch, None while it has none; place, the runner's record of the place it
    launched (host_read's), None while it has none; read, True when its host's runner branch was read, else why not;
    after, the work its launch's After names (after_work). Returns {"stage", and what goes with it}: unknown, with why,
    for an unread host, no launch, or a fact crew can't read; launching while unanswered or unplaced; waiting, on the
    work after names, while the runner holds it; refused, with the runner's words; then from Flume's status: merged on
    a bolt and landed on main once its place landed, with the commit; dropped; queued for room; needs, with the agent's
    words, once its stage stopped short asking or found work; stalled, or else waits, with Flume's words and why, while
    it waits on its caller, the submission held among them; submitted, with sluice's number; its stage, with sluice's
    words, once sent back after a failed or conflicting submission; else its current stage. Each names its place, and
    a stage of a change its tasks, ticked and in all."""
    if read is not True:
        return {"stage": "unknown", "why": read}
    if launch is None:
        return {"stage": "unknown", "why": f"{work} has no launch in requests.rec"}
    n, outcome = launch.get("Request"), answer.get("Outcome") if answer is not None else None
    if answer is None:
        return {"stage": "launching"}
    if outcome == "held":
        return {"stage": "waiting", "after": list(after)}
    if outcome == "refused":
        return {"stage": "refused", "words": answer.get("Words")}
    if outcome != "launched":
        return {"stage": "unknown", "why": f"the runner answered launch {n} of {work} {outcome}, and a launch is answered held, launched or refused"}
    if place is None:
        return {"stage": "launching", "place": answer.get("Place")}
    res = {"place": place["place"]}
    if place.get("why"):
        return dict(res, stage="unknown", why=place["why"])
    f = flume_facts(place["status"], place["place"])
    if f is None:
        return dict(res, stage="unknown", why=f"Flume's status of {work}'s place, as the runner carried it, holds no place {place['place']}")
    if f["tasks"] is not None:
        res["tasks"] = f["tasks"]
    if f["over"] == "landed":
        return dict(res, stage="landed" if launch.get("Base") == "main" else "merged", commit=f["commit"])
    if f["over"] == "dropped":
        return dict(res, stage="dropped")
    if f["phase"] == "making":
        return dict(res, stage="launching")
    if f["phase"] != "live":
        said = f"Flume's status of {work}'s place {place['place']}"
        return dict(res, stage="unknown", why=(
            f"{said} says its work is {f['over']}, and a place of a kind that lands ends landed or dropped" if f["over"] else
            f"{said} gives phase {f['phase']}, which crew does not read" if f["phase"] else f"{said} gives no phase crew reads"))
    if f["state"] == "waiting_for_room":
        return dict(res, stage="queued", of=f["current"])
    if f["waiting"] == "answer":
        return dict(res, stage="needs", of=f["waiting_stage"] or f["current"], words=text(f["end"].get("words")) or f["waiting_words"],
                    found=f["end"].get("needs") == "found_work", stalled=f["stalled"])
    if f["waiting"]:
        return dict(res, stage="stalled" if f["stalled"] else "waits", of=f["waiting_stage"], why=f["waiting"], words=f["waiting_words"],
                    held=f["held"] and not f["waiting_stage"])
    if f["entry_state"] in ("waiting", "under_test", "landed") or (f["request"] and f["entry"] is None and f["submits"]):
        return dict(res, stage="submitted", submission=f["entry"] or f["request"])
    if f["unread"] and f["submits"]:
        return dict(res, stage="unknown", why=f"Flume could not read {work}'s submission: {f['unread']}")
    if f["current"] is None:
        return dict(res, stage="unknown", why=f"Flume's status of {work}'s place {place['place']} names no current stage")
    if f["send_backs"] and f["verdict"] in ("failed", "conflict"):
        return dict(res, stage=f["current"], words=f["verdict_words"], sent_back=f["send_backs"], verdict=f["verdict"])
    return dict(res, stage=f["current"])


# ------------------------------------------------------------------------------------- a crossed team's launches

def work_of(u):
    """How a request names a unit or chore of the plan (Decision 4): unit/<unit>, or chore/<chore> for one marked
    Kind: chore (plan.11)."""
    return f"{'chore' if u.get('Kind') == 'chore' else 'unit'}/{u.name()}"


def brief(u):
    """A launch's brief for a unit or chore (Decision 5): the work's own words as crew's prompts give them, less what
    the stage itself is told, which is its kind's: a unit's intent with its sources, as stage_prompt gives construct,
    and a chore's words, as chore_prompt gives code."""
    sources = u.all("Source") if u.get("Kind") != "chore" else []
    return (u.get("Intent") or "") + (" Sources: " + "; ".join(sources) + "." if sources else "")


def priority_of(plan, bolt):
    """A crossed bolt's priority (Decision 6): its place among the plan's bolts given through Flume (Path: flume),
    counted from the end, so the first in the plan's order has the highest and Flume starts its waiting stages first
    (flume record 0010); None for a bolt not given through Flume, or gone from the plan."""
    given = [b.name() for b in plan.bolts() if b.get("Path") == "flume"]
    return len(given) - given.index(bolt) if bolt in given else None


def standing(requests):
    """The launches no drop names, in requests.rec's order."""
    dropped = {r.get("Of") for r in requests if r.get("Act") == "drop"}
    return [r for r in requests if r.get("Act") == "launch" and r.get("Request") not in dropped]


def built_order(work):
    """A bolt's work in the order its launches are numbered (Decision 5): the file's order, but each after the work its
    After names, so a dependent's After names launches written before it. A cycle, which crew's rules refuse (plan.1),
    leaves the rest in the file's order."""
    names, order, placed = {u.name() for u in work}, [], set()
    while len(order) < len(work):
        u = next((u for u in work if u.name() not in placed and all(d in placed or d not in names for d in u.all("After"))),
                 next(u for u in work if u.name() not in placed))
        order.append(u)
        placed.add(u.name())
    return order


def reach(plan, requests, bolt, team, again=()):
    """What a plan write asks of the runner for a bolt given through Flume (Decisions 5 and 7), as the requests to
    append in order, each (act, host, work, its fields as plan.request takes them), from facts: plan, as the write
    leaves it; requests, requests.rec's records before them; team, the team holding the bolt as crew.load gives it with
    the bolt's kit as its kit; again, the work (as requests name it) whose launch is dropped and launched anew, an
    amendment of a unit whose place is not launched. Each unit and chore of the bolt with no launch standing is
    launched, as a give launches them: in the file's order, each after the work its After names, cut from the bolt's
    branch, carrying the team's host and stream, the kit's forge address, the bolt's priority, its intent, the
    planner as recipient, its brief, and the launches of its After work; a launch standing whose After no longer names
    its After work's standing launches, one of them dropped, launched anew or gone from its After, is dropped and the
    work launched again, so no place waits on a launch that will never land; and each unit's or chore's launch on the
    bolt whose work has left it is dropped, every launch on the bolt's branch, its fixes' too, once the bolt has left
    the plan. The drops come first, numbered from the next request, then the launches."""
    base = f"bolt/{bolt}"
    on = [r for r in standing(requests) if r.get("Base") == base]
    newest = {r.get("Work"): r for r in on}
    work = plan.work_of(bolt) if plan.bolt(bolt) is not None else []
    names = {u.name(): work_of(u) for u in work}
    order = built_order(work)
    fresh = set()
    for u in order:
        wk, l, deps = names[u.name()], newest.get(names[u.name()]), [d for d in u.all("After") if d in names]
        if l is None or wk in again or any(names[d] in fresh for d in deps) or \
                sorted(l.all("After")) != sorted(newest[names[d]].get("Request") for d in deps):
            fresh.add(wk)
    left = [r for r in on if r.get("Work") not in names.values()
            and (plan.bolt(bolt) is None or r.get("Work").startswith(("unit/", "chore/")))]
    drops = [r for r in on if newest[r.get("Work")] is not r or r.get("Work") in fresh or r in left]
    out = [("drop", r.get("Host"), r.get("Work"), {"Of": r.get("Request")}) for r in drops]
    n, num = next_request(requests) + len(out), {}
    # A team turned back holds its bolts given through Flume until they land (Decision 2): their work runs on in the
    # stream its launches named.
    stream = (team["flume"] or next((r.get("Stream") for r in reversed(on)), None)) if team else None
    for u in order:
        wk = names[u.name()]
        if wk not in fresh:
            num[u.name()] = number(newest[wk].get("Request"))
            continue
        num[u.name()], n = n, n + 1
        out.append(("launch", team["machine"], wk, {
            "Repo": team["kit"]["repo"], "Kind": "chore" if u.get("Kind") == "chore" else "change", "Name": u.name(), "Base": base,
            "Stream": stream, "Priority": priority_of(plan, bolt), "Intent": f"{team['label']}/{bolt}",
            "Recipient": f"{team['label']}/planner", "After": [num[d] for d in u.all("After") if d in num], "Brief": brief(u)}))
    return out


def priorities(plan, requests):
    """The priority requests a write that launches or reorders bolts appends (Decision 6): [(launch, its priority now)]
    for each launch standing on a bolt given through Flume whose priority, its bolt's place in the plan now
    (priority_of), differs from the last its requests set, its launch's or a later priority's; none for a fix of main,
    or a bolt gone from the plan."""
    last = {}
    for r in requests:
        if r.get("Act") == "launch" or (r.get("Act") == "priority" and r.get("Of") in last):
            last[r.get("Request") if r.get("Act") == "launch" else r.get("Of")] = r.get("Priority")
    out = []
    for r in standing(requests):
        base = r.get("Base") or ""
        p = priority_of(plan, base[len("bolt/"):]) if base.startswith("bolt/") else None
        if p is not None and str(p) != last.get(r.get("Request")):
            out.append((r, p))
    return out


def amending(work, launch, answer, place, read):
    """How an approved amendment of a crossed team's unit reaches its place (Decision 7), from the facts stage_of takes:
    ("again", None) while its launch is held, refused or unanswered, or it has none, its launch dropped and the unit
    launched anew with the amended intent; ("retry", None) once its place is launched, construct started again with
    the amendment's words, the place's later stages then running again as Flume runs its kind through (plan.15);
    ("refused", why) when crew can't tell which, its host's runner or its place unread (read.1), or its place has
    merged, landed or been dropped, which is not amended (plan.6)."""
    outcome = answer.get("Outcome") if answer is not None else None
    if launch is None or (read is True and outcome != "launched"):
        return "again", None
    s = stage_of(work, launch, answer, place, read)
    if s["stage"] == "unknown":
        return "refused", f"can't tell how far {work}'s place has got, so the amendment can't reach it: {s['why']}"
    if s["stage"] in ("merged", "landed", "dropped"):
        how = {"merged": "merged into its bolt", "landed": "landed on main", "dropped": "been dropped"}[s["stage"]]
        return "refused", f"{work}'s place {s['place']} has {how}, so it is not amended: a defect in it is a fix, and new work is a new unit"
    return "retry", None


def launched_refusal(requests, work, how):
    """Why a move out of a bolt given through Flume, a split, or a change of After is refused for work whose launch is
    written (Decision 7), or None while none stands: a place's base and order are fixed at its launch, so the way on is
    to drop the work and add it again as it should be. how says what the write would do to it."""
    l = launch_of(requests, work)
    if l is None:
        return None
    kind, name = work.split("/", 1)
    return (f"{kind} {name} is launched as Flume place {l.get('Name')} on {l.get('Base')} (request {l.get('Request')}), whose "
            f"base and order are fixed at its launch, so it is not {how}: drop it (crew {kind} drop {name}) and add it "
            f"again as it should be (crew {kind} add)")


def crossed_builders(plan, teams, label, kit):
    """The partition's teams that have crossed to Flume and build a kit, by its name or owner/name, by name, sorted:
    those a bolt planned in it is given to (takers), and those whose host runs a fix of its main (main_fixer)."""
    return sorted(n for n, t in teams.items() if t["label"] == label and path_of(plan, t)[0] == "crossed"
                  and any(kit in (k.get("name"), k.get("repo")) for k in t.get("kits") or [t.get("kit") or {}]))


def takers(plan, teams, label, bolt):
    """The partition's teams that have crossed to Flume and build a planned bolt's kit, by name, sorted (Decision 3):
    a bolt held by no team in a kit one of them builds is theirs whenever it is planned, a crossed team holding no
    bound; none for a bolt a team holds."""
    b = plan.bolt(bolt)
    if b is None or b.get("Team"):
        return []
    return crossed_builders(plan, teams, label, b.get("Repo"))


def planned_said(bolt, names):
    """What the partition's dispatchers are told of a bolt planned in a kit teams crossed to Flume build (Decision 3,
    takers): that it can be given, and to whom."""
    who = " or ".join(names)
    return (f"bolt {bolt} can be given to {who}, which {'has' if len(names) == 1 else 'have'} crossed to Flume and "
            f"{'takes' if len(names) == 1 else 'take'} each planned bolt of {'its' if len(names) == 1 else 'their'} kits: "
            + " or ".join(f"crew bolt give {n} {bolt}" for n in names))


# ------------------------------------------------------------------------------------------ answers and fixes

def piece_stage(requests, reading, launch):
    """A launch's piece's stage (stage_of), from requests.rec's records and its host's runner as crew read it (host_read,
    of_host): the runner's answer to the launch and its record of the place launched, read only where the host's branch
    was."""
    n, why = number(launch.get("Request")), reading["why"]
    answer, place = (None, None) if why else (reading["answers"].get(n), reading["places"].get(n))
    return stage_of(launch.get("Work"), launch, answer, place, why or True, after_work(requests, launch))


def named_launch(requests, work):
    """The launch standing for the work a command names (Decision 9), as (launch, None), or (None, why): named as
    requests name it (unit/<u>, chore/<c>, fix/<bolt>/<name>, fix/main/<kit>/<name>), by its place's name (<u>,
    <bolt>--<name>, main--<name>), or a unit or chore by its own name. None stands for work a team crossed to Flume
    does not build, and a name two works answer to is said with both."""
    hits = {r.get("Work"): r for r in standing(requests)
            if work in (r.get("Work"), r.get("Name")) or r.get("Work") in (f"unit/{work}", f"chore/{work}")}
    if not hits:
        return None, (f"no launch of {work} stands in requests.rec, so no Flume place of it waits on an answer: crew answer "
                      "answers a place of work a team crossed to Flume builds, by its unit's, chore's or place's name")
    if len(hits) > 1:
        return None, f"{work} names {' and '.join(sorted(hits))}: name the one meant as requests.rec does"
    return next(iter(hits.values())), None


def stage_said(s):
    """A crossed piece's stage (stage_of) in a few words, for a refusal to name."""
    st = s["stage"]
    return {"launching": "launching", "waiting": "held for its After work", "refused": "refused by the runner",
            "queued": f"queued for room at {s.get('of')}", "submitted": f"submitted to sluice ({s.get('submission')})",
            "merged": "merged", "landed": "landed", "dropped": "dropped"}.get(st, f"at {st}")


def answer_retry(work, s):
    """What crew answer asks of a crossed piece's place (Decision 9), from its stage as stage_of gives it: ("stage", the
    stage) to start again with the words, for a place whose stage stopped short asking or that waits on its caller to
    retry a stage, stalled or not; ("submission", None) to submit again with them, for one whose submission waits on its
    caller and is not held; else (None, why), naming its stage: crew can't tell it (read.1), its submission waits held
    for the user's send, which no answer gives (state.3), or it neither stopped short nor waits on its caller."""
    st, place = s["stage"], f"{work}'s place" + (f" {s['place']}" if s.get("place") else "")
    if st == "unknown":
        return None, f"can't tell whether {work}'s place waits on an answer: {s['why']}"
    if st == "needs" or (st in ("waits", "stalled") and s.get("of")):
        return "stage", s["of"]
    if st in ("waits", "stalled") and s.get("held"):
        send = "crew main fix {} {} --send".format(*work.split("/")[2:]) if work.startswith("fix/main/") else "its send"
        return None, (f"{place} has delivered, and its submission waits held for the user's send, which no answer gives: "
                      f"{send}, on the user's word")
    if st in ("waits", "stalled"):
        return "submission", None
    return None, (f"{place} is {stage_said(s)}, with no question and nothing it waits on its caller for, so there is nothing "
                  "to answer: crew bolts shows its stage")


def fix_launch(plan, requests, bolt, team, name, words):
    """The launch crew fix <team> <name> "<words>" appends for a fix on a bolt given through Flume (Decision 10), as
    (act, host, work, its fields as plan.request takes them), or (None, why): a place of the fix kind named
    <bolt>--<name>, cut from the bolt's branch, on the team's host and in its stream (or, turned back, the stream the
    bolt's launches named, as reach has it), with the bolt's priority and intent, the planner as recipient, the fix's
    words as its brief and nothing held. Refused while a launch of that fix stands on the bolt, merged or not, since
    the name is in use there (teams.3). team carries the bolt's kit as its kit."""
    work, base = f"fix/{bolt}/{name}", f"bolt/{bolt}"
    l = launch_of(requests, work)
    if l is not None:
        return None, (f"fix {name} is in use on bolt {bolt}: it is launched as Flume place {l.get('Name')} (request "
                      f"{l.get('Request')}), so name this fix differently")
    stream = team["flume"] or next((r.get("Stream") for r in reversed(requests)
                                    if r.get("Act") == "launch" and r.get("Base") == base and r.get("Stream")), None)
    return ("launch", team["machine"], work, {
        "Repo": team["kit"]["repo"], "Kind": "fix", "Name": f"{bolt}--{name}", "Base": base, "Stream": stream,
        "Priority": priority_of(plan, bolt), "Intent": f"{team['label']}/{bolt}", "Recipient": f"{team['label']}/planner",
        "Brief": words}), None


def take_main(plan, requests, bolt, team, main, words):
    """The launch of a crossed bolt's take-main fix (Decision 10, plan.8), once sluice refused its landing for a
    conflict with main at main (its revision): a fix as fix_launch makes it, named take-main-<main, seven>, its brief
    saying to take origin/main into the bolt and resolve, with sluice's words of the conflict, and beginning as every
    take-main fix's does, so the bolt's row says it takes main first (plan.TAKE_MAIN); None while a fix of that name
    stands on the bolt, so a refusal read twice launches it once."""
    name = f"take-main-{main[:7]}"
    if launch_of(requests, f"fix/{bolt}/{name}") is not None:
        return None
    return fix_launch(plan, requests, bolt, team, name, (
        f"Take main into the bolt: merge origin/main, at {main[:7]}, into this place, cut from bolt/{bolt}, resolving each "
        f"conflicting path keeping both intents, main's and the bolt's; sluice refused the bolt's landing for its conflict "
        f"with main: {words}"))[0]


def fix_drop_refusal(team, work, launch, s):
    """Why crew fix --drop of a fix on a bolt given through Flume, or crew main fix --drop of a fix of main, is refused
    (Decisions 10 and 11, teams.3), or None to drop the launch standing: none stands, so the team, or the kit, has no
    such fix; crew can't tell how far its place got (read.1); or its place has merged into its base, so what it changed
    is the bolt's, or main's, and a new fix undoes it. s, its stage (piece_stage)."""
    if launch is None:
        return f"{team} has no fix {work}: no launch of it stands in requests.rec"
    if s["stage"] == "unknown":
        return f"can't tell whether {work}'s place has merged into {launch.get('Base')}, so it is not dropped: {s['why']}"
    if s["stage"] in ("merged", "landed"):
        return (f"{work} has merged into {launch.get('Base')}, so it is not dropped: what it changed is "
                f"{'main' if launch.get('Base') == 'main' else 'the bolt'}'s, and a new fix undoes it")
    return None


def fix_flume_refusal(mode, team, bolt, name):
    """What crew fix <team> <name> --merge or --wait says refusing a fix on a bolt given through Flume (Decision 10):
    Flume submits the fix's place to the bolt through sluice itself and tells its end to the planner, so nothing of
    crew's merges it or waits on it, and crew bolts shows its stage."""
    said = f"crew fix {team} {name} --{mode}"
    return (f"fix/{bolt}/{name} is a Flume place on bolt/{bolt}, which Flume submits to the bolt through sluice itself once its "
            f"code has delivered, telling the planner its end, so {said} has nothing to do: crew bolts shows its stage")


def fixes_in_flight(requests, reads, label, bolt):
    """The fixes in flight on a bolt given through Flume (Decision 10), {fix/<bolt>/<name>: its brief}: each whose launch
    stands and whose place has not merged into the bolt, landed or been dropped, its stage read from its host's runner
    (reads, by host, of_host; piece_stage), one crew can't read counted in flight (read.1). A fix in flight holds the
    bolt's landing as today's does (plan.landing_unready, landing_rows)."""
    out = {}
    for l in standing(requests):
        work = l.get("Work") or ""
        if l.get("Base") == f"bolt/{bolt}" and work.startswith(f"fix/{bolt}/"):
            if piece_stage(requests, of_host(reads, label, l.get("Host")), l)["stage"] not in ("merged", "landed", "dropped"):
                out[work] = l.get("Brief")
    return out


# ------------------------------------------------------------------------------------------------ a fix of main

def main_fixer(plan, teams, label, kit, team=None):
    """The team on whose host a fix of a kit's red main runs (Decision 11, state.3), as (its name, None), or (None, why):
    among the partition's teams crossed to Flume that build the kit (crossed_builders), the one team names, else the
    first by name while they all run on one host, since the place wants the host and its stream and nothing else of a
    team. Refused when team names none of them, when they run on several hosts and team names none, and when no team
    crossed to Flume builds the kit, its red main's fix then being a bolt of one chore, proposed first among the
    planned, as state.3 has it until one does."""
    names = crossed_builders(plan, teams, label, kit)
    if not names:
        return None, (f"no team of {label} crossed to Flume builds {kit}, so a fix of its red main is no Flume place: it is a bolt "
                      "of one chore, proposed first among the planned, which the dispatcher gives to the next team that frees "
                      f"(state.3); tell {label}-planner, who proposes it")
    if team is not None:
        return (team, None) if team in names else (None, (
            f"{team} is no team of {label} crossed to Flume building {kit}; " + " and ".join(names)
            + (" is" if len(names) == 1 else " are")))
    hosts = sorted({teams[n]["machine"] for n in names})
    if len(hosts) > 1:
        return None, (f"{' and '.join(names)} build {kit} through Flume on {' and '.join(hosts)}: name the team on whose host the "
                      "fix runs, --team <team>")
    return names[0], None


def main_priority(plan):
    """A fix of main's priority at its launch (Decision 11): one above every bolt given through Flume (priority_of), so
    Flume starts its code ahead of theirs, a red main holding back every landing on it."""
    return sum(1 for b in plan.bolts() if b.get("Path") == "flume") + 1


def main_fix_launch(plan, requests, label, team, name, words, served):
    """The launch crew main fix <kit> <name> "<the failure's words>" appends (Decision 11), as (act, host, work, its
    fields as plan.request takes them), or (None, why): a place of the fix kind named main--<name>, cut from main, on
    the host of team (main_fixer, carrying the kit as its kit) and in its stream, ahead of every bolt (main_priority),
    its intent the kit's main, main-level ops as its recipient, the failure's words as its brief, and its submission
    held for the user's send (state.3). Refused while no runner answers on the host (served, whether its runner's
    branch exists), since nothing would launch it there and the red main waits on it, the fix then being a bolt of one
    chore as main_fixer has it where no crossed team builds the kit; and while a launch of that fix of the kit's main
    stands, landed or not, since the name is in use there."""
    kit, host = team["kit"]["name"], team["machine"]
    if not served:
        return None, (f"no runner answers on {host}: {runner_branch(label, host)} does not exist, so nothing would launch the fix "
                      f"there; until the runner (flywheel-runner) serves {label} there, a fix of {kit}'s red main is a bolt of one "
                      f"chore, proposed first among the planned (state.3); tell {label}-planner, who proposes it")
    work = f"fix/main/{kit}/{name}"
    l = launch_of(requests, work)
    if l is not None:
        return None, (f"fix {name} of {kit}'s main is in use: it is launched as Flume place {l.get('Name')} (request "
                      f"{l.get('Request')}), so name this fix differently")
    return ("launch", host, work, {
        "Repo": team["kit"]["repo"], "Kind": "fix", "Name": f"main--{name}", "Base": "main", "Stream": team["flume"],
        "Priority": main_priority(plan), "Intent": f"{label}/main/{kit}", "Recipient": f"{label}/ops", "Hold": "submission",
        "Brief": words}), None
