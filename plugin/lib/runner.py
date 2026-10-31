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
