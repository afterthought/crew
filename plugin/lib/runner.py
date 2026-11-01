"""crew's side of the runner's interface (flywheel-runner core.2), and the decisions over a bolt's work given through
Flume: crew records a kit's work against its repository, and the runner whose configuration names that repository
takes it and launches it in Flume places on its host, in the stream that configuration gives (the user's ruling of
2026-11-01; Decision 4 of the-team-machinery-leaves); crew looks up no kit's host and models no account, and where it
must say or act where a kit's work runs, it reads what the runner reported for the work it took (taken, where).

crew asks the runners for work by requests on the flywheel's branch, requests.rec (REQUESTS), each appended in the
commit of the plan write that occasions it and checked by crew's own rules (request_refusal, append_refusal) as well as
recfix; each runner answers on a branch of its own, <label>/runner/<host>, which crew fetches with <label>/main and
reads (host_read) and never writes (state.5). A started piece's stage is read from its launch, the answer of the
runner that took it and Flume's status of its place as that runner carried it (stage_of, flume_facts), and shown with
its stream on every view (stream_said, piece_said).

A start launches its bolt whole, refused only where no runner answers for the partition (runnerless), and every plan
write reaches the places a started bolt launched as its own act: added work launched, dropped work dropped, a dependent
launched again when what it waits on is (reach), an amendment a retry of construct or a launch anew (amending), and a
move, split or change of After of launched work refused (launched_refusal); each launch's priority follows its bolt's
place in the plan (priorities).

A place that stopped short asking, or waits on its caller, is answered by a retry with the answer's words (answer_retry).
A fix on a started bolt is a launch of Flume's fix kind on the bolt's branch (fix_launch), dropped by a drop
(fix_drop_refusal), merged and waited on by Flume alone, and holds the bolt's landing while it is in flight
(fixes_in_flight); a started bolt whose landing sluice refused for a conflict with main takes main in by one
(take_main). A red main's fix is a launch of the fix kind on main with its submission held, taken by the runner that
keeps the kit (main_fix_launch); its kit's landings row carries it once its code has delivered and its submission
waits held (main_fixes_waiting), and the user's send of it is the retry of its submission, made once (send_refusal,
sent_of).

A main-level role that runs as its kind has its run read from the runner's records (role_run), and its work that lands
is a launch of Flume's chore kind on its repository's default branch, the role's address its recipient (role_launch).

Each is a function of plain facts (code.7); plan.py, crew.py and hold.py read the facts and act on what they decide.
This module imports nothing outside the standard library and crew's own modules (code.1)."""
import json
import os
import re

def runnerless(label, tips):
    """Why a start is refused for want of a runner (Decision 5), or None: tips, the hosts whose runner branch the
    partition's state repository holds (plan.runner_tips); with none, no runner answers for the partition, so nothing
    would take the bolt's work."""
    if tips:
        return None
    return (f"no runner answers for {label}: its state repository holds no {runner_branch(label, '<host>')}, so nothing "
            "would take the bolt's work; a start waits for a runner (flywheel-runner) to serve the partition")


REQUESTS = """\
# crew's requests of the runners: a launch of a Flume place for a started
# bolt's work, a fix or a role's work that lands, or a retry, drop or priority
# of a place launched.
# Written only by crew, each in the commit of the plan write that occasions it;
# numbered once, and never changed or removed. The runner whose configuration
# names a launch's Repo takes it, or for a role's the runner on its Host, and
# answers on <label>/runner/<host> of this repository, which crew reads and
# never writes.

%rec: Request
%doc: A request for Work: a launch of a Flume place of Kind named Name, cut from Base of Repo, taken by the runner whose configuration names Repo, in the stream it gives, or by Host's runner in Stream for a role's work; or a retry, drop or priority of the place the launch Of names launched, taken by the runner that took it.
%key: Request
%type: Request,Of,After,Priority int
%type: Act enum launch retry drop priority
%type: Kind enum change chore fix
%type: Hold enum submission
%type: Submission bool
%type: Host regexp /^[a-z0-9][a-z0-9-]*$/
%type: Date date
%mandatory: Request Act Work Date By
%allowed: Request Act Host Work Repo Kind Name Base Stream Priority Intent Recipient Hold After Brief Of Stage Submission Words Date By
"""
# A request's fields in the order requests.rec writes them (Decision 4's table).
FIELDS = ("Request", "Act", "Host", "Work", "Repo", "Kind", "Name", "Base", "Stream", "Priority", "Intent", "Recipient", "Hold",
          "After", "Brief", "Of", "Stage", "Submission", "Words", "Date", "By")
# What every request carries, and, by its act, what it must carry beside them and what else it may: a launch of a
# role's work names its Host and Stream, and a launch of a kit's work neither (request_refusal).
COMMON = ("Request", "Act", "Work", "Date", "By")
ACTS = {
    "launch": (("Repo", "Kind", "Name", "Base", "Priority", "Intent", "Recipient", "Brief"), ("Hold", "After", "Host", "Stream")),
    "retry": (("Of",), ("Stage", "Submission", "Words")),
    "drop": (("Of",), ()),
    "priority": (("Of", "Priority"), ()),
}
# The work a request serves, as crew names it: a unit, a chore, a fix on a bolt or a fix of a kit's main, or a role's
# work that lands (Decision 10 of roles-run-as-flume-kinds).
WORK = re.compile(r"^(?:unit/N|chore/N|fix/N/N|fix/main/N/N|role/N/N)$".replace("N", "[a-z0-9][a-z0-9-]*"))


def number(v):
    """A record's number field as an int, None when it holds none or no number."""
    return int(v) if isinstance(v, str) and v.isdigit() else None


def next_request(requests):
    """The number the next request takes (Decision 4): one past the highest requests.rec holds, 1 for the first."""
    return max((number(r.get("Request")) or 0 for r in requests), default=0) + 1


def request_fields(n, act, work, given, date, by):
    """A request's fields in requests.rec's order (FIELDS), as (field, value): its number, act and work, what the
    command gives (given, {field: a value or a list of them, None or False for none and True written yes}), and when
    and by whom. A field FIELDS does not hold goes last, for request_refusal to name."""
    given = dict(given, Request=n, Act=act, Work=work, Date=date, By=by)
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
    needs and none its act does not take; a launch of a role's work names the host and stream its role runs in, and a
    launch of a kit's work neither, the runner whose configuration names its repository taking it in the stream that
    configuration gives (the user's ruling of 2026-11-01); a retry, drop or priority names by Of a launch of the same
    work; a launch's After names launches on the same base, the work of the same bolt; a fix of main holds its
    submission; and a retry starts a stage again or submits again, not both (Decision 4)."""
    n, act, work = new.get("Request"), new.get("Act"), new.get("Work")
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
        return (f"{act} {n} serves {work}, and a request serves unit/<unit>, chore/<chore>, fix/<bolt>/<name>, fix/main/<kit>/<name> "
                "or role/<role>/<name>")
    if act == "launch" and work.startswith("role/") and not (new.get("Host") and new.get("Stream")):
        return f"launch {n} of {work} names no Host or no Stream: a role's work runs on the host and in the stream its role runs in"
    if act == "launch" and not work.startswith("role/") and (new.get("Host") or new.get("Stream")):
        return (f"launch {n} of {work} names a Host or a Stream: a kit's work is taken by the runner whose configuration "
                "names its repository, in the stream that configuration gives, and crew names neither")
    by = {r.get("Request"): r for r in requests}
    if act != "launch":
        of = by.get(new.get("Of"))
        if of is None or of.get("Act") != "launch":
            return f"{act} {n} for {work} names request {new.get('Of')}, which is no launch" + (
                "" if of is not None else ": requests.rec does not hold it")
        if of.get("Work") != work:
            return f"{act} {n} for {work} names launch {of.get('Request')}, which is {of.get('Work')}'s"
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
# as Flume gave it (flywheel-runner core.1), kept after Flume tidies the place until its work has left crew's plan,
# and after those each role's latest run on the host, a Run record keyed by the role's address (R4 of
# roles-run-as-flume-kinds), with Flume's status of its place, or the runner's words where no run could be launched
# (flywheel-runner's the-runner-carries-crews-work-into-flume, Decision 14).
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
RUNS = """\
%rec: Run
%key: Address
%type: At date
%mandatory: Address At
%allowed: Address Place At Status Words
"""
FILES = {"runner.rec": "Runner", "answers.rec": "Answer", "places.rec": "Place"}


def host_read(label, host, tip, files, refused):
    """A host's runner as crew reads it from its branch (Decision 4), from facts: tip, the branch's commit in crew's
    cache, None when no such branch exists; files, each of FILES parsed at the tip as the plan is (plan.Plan), None
    for one the tip lacks, answers and places then none; refused, recfix's words for each file it refused. Returns
    the reading, its host, branch and tip, with either why it could not be read, which hides this host's work alone
    (read.1, read.3), or the runner's record, each answer by its request's number and each place by its launch's: the
    place's path, when the runner carried it, and its Status parsed, or with why it could not be; and each role's run
    by its address, likewise, with the runner's words where it could launch none."""
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
    runs = {}
    for r in files["places.rec"].recs("Run") if files.get("places.rec") is not None else []:
        a = r.get("Address")
        if not a or a in runs:
            return dict(out, why=f"{host}'s runner can't be read: {at}: places.rec holds "
                        + ("a run with no role's address" if not a else f"the run of {a} twice"))
        try:
            status, why = (json.loads(r.get("Status")) if r.get("Status") is not None else None), None
        except ValueError as e:
            status, why = None, f"{at}: places.rec's status of the run of {a} is no JSON ({e})"
        runs[a] = {"place": r.get("Place"), "at": r.get("At"), "status": status, "words": r.get("Words"), "why": why}
    return dict(out, runner=run[0], answers=answers, places=places, runs=runs)


def role_run(reading, address):
    """A role's latest run on a host as its runner's records show it (R4 of roles-run-as-flume-kinds), from host_read's
    reading and the role's address, <label>/<role>: whether it is live, its place, the runner's words where it could
    launch none, and why crew can't tell, the host's runner unread or the run's status no JSON (read.1). A run is live
    while its place reads live or making in Flume's status, as the runner judges a run that stands; one tidied, over,
    gone, refused or never launched is not."""
    if reading.get("why"):
        return {"live": None, "place": None, "words": None, "why": reading["why"]}
    r = reading["runs"].get(address)
    if r is None:
        return {"live": False, "place": None, "words": None, "why": None}
    if r["why"]:
        return {"live": None, "place": r["place"], "words": r["words"], "why": r["why"]}
    facts = flume_facts(r["status"], r["place"]) if r["status"] is not None else None
    return {"live": bool(facts) and facts["phase"] in ("live", "making"), "place": r["place"], "words": r["words"], "why": None}


def run_waiting(reading, address):
    """What a role's latest run on a host waits on its caller for, as Flume's status the runner carried shows it (Decision
    15 of roles-run-as-flume-kinds): (why, words, place), why as Flume's `waiting_on.why` names it, answer for a turn
    that stopped short and lost for one whose agent was lost, the words the stop-short's own where it has them, else
    Flume's; None for a run that waits on nothing, is not live, or that crew can't read, which role_run says why (read.1)."""
    r = None if reading.get("why") else reading["runs"].get(address)
    if r is None or r["why"] or r["status"] is None:
        return None
    f = flume_facts(r["status"], r["place"])
    if not f or f["phase"] != "live" or not f["waiting"]:
        return None
    return f["waiting"], text(f["end"].get("words")) or f["waiting_words"], r["place"]


def of_host(reads, label, host):
    """A host's reading among a partition's (host_read's, by host), or why none is: no runner branch for it exists."""
    return reads.get(host) or host_read(label, host, None, {}, {})


def takers(reads, n):
    """The runners that took request n, from the partition's runners as crew read them (reads, host_read's by host): (the
    readings whose answers hold it, the readings crew could not read), each by host."""
    return ([r for _, r in sorted(reads.items()) if not r["why"] and n in r["answers"]],
            [r for _, r in sorted(reads.items()) if r["why"]])


def taken(reads, n):
    """The runner that took request n (takers): (its reading, None) for the one whose answers hold it; (None, None)
    while none read holds it and every one was read, the request not taken yet; (None, why) when two hold it, or none
    read holds it and one could not be read, or no runner answers for the partition at all (read.1, read.3). crew names
    no host on a kit's launch: the runner whose configuration names its repository takes it (the user's ruling of
    2026-11-01)."""
    if not reads:
        return None, f"no runner answers for the partition: no <label>/runner/<host> branch exists, so nothing takes request {n}"
    hits, unread = takers(reads, n)
    if len(hits) > 1:
        return None, (f"request {n} was taken by the runners on {' and '.join(r['host'] for r in hits)}, whose configurations "
                      "each name its repository, so crew can't tell which place is its work")
    if hits:
        return hits[0], None
    if unread:
        return None, f"no runner crew read has taken request {n}, and " + "; ".join(r["why"] for r in unread)
    return None, None


def where(reads, launches, what):
    """Where a runner reported taking work (the user's ruling of 2026-11-01; Decision 4), from the partition's runners as
    crew read them (reads) and the launches of the work (launches, requests.rec's records, a bolt's on its branch or a
    kit's): the host whose runner took the newest of them taken (takers), and the kit's folder there and the stream its
    work runs in, as Flume's status of the newest place that runner carries of them names them, None where it carries
    none naming them yet; as ({"host", "dir", "stream"}, None); (None, None) while no runner has taken any of them and
    every runner was read; or (None, why) when none has and one could not be read, naming what (what) and that runner,
    or two runners took the newest (read.1)."""
    unread = sorted({r["host"]: r["why"] for _, r in reads.items() if r["why"]}.items())
    for l in sorted(launches, key=lambda l: -(number(l.get("Request")) or 0)):
        hits, _ = takers(reads, number(l.get("Request")))
        if len(hits) > 1:
            return None, (f"crew can't tell where {what}'s work runs: request {l.get('Request')} was taken by the runners on "
                          f"{' and '.join(r['host'] for r in hits)}, whose configurations each name its repository")
        if not hits:
            continue
        reading = hits[0]
        mine = sorted((number(x.get("Request")) for x in launches if number(x.get("Request")) in reading["places"]), reverse=True)
        facts = [f for n in mine for p in [reading["places"][n]] if not p["why"] for f in [flume_facts(p["status"], p["place"])] if f]
        return {"host": reading["host"], "dir": next((f["repository"] for f in facts if f["repository"]), None),
                "stream": next((f["stream"] for f in facts if f["stream"]), None)}, None
    return None, (f"no runner has reported taking {what}'s work yet, so crew can't tell where it runs"
                  + "".join(f"; {why}" for _, why in unread)) if unread else None


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
    for, the stage named, why, Flume's words and since when, in seconds, and whether it is stalled. None when status
    holds no entry for it. Each also names the folder of the place's repository on its host, and the stream it runs in,
    which say where the runner that took it keeps the kit (where)."""
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
        "repository": text(p.get("repository")), "stream": text(at(p, "stream", "name")),
        "phase": phase, "over": over, "commit": text(of.get("commit")) if over == "landed" else None,
        "current": current, "state": text(at(stage, "state")), "end": at(stage, "end") if isinstance(at(stage, "end"), dict) else {},
        "tasks": tasks,
        "entry": text(at(entry, "id")), "entry_state": tagged(at(entry, "state"))[0],
        "unread": text(rf.get("reason")) if read == "could_not_read" else None,
        "request": text(sub.get("request")), "submits": count(sub.get("submits")), "send_backs": count(sub.get("send_backs")),
        "verdict": verdict, "verdict_words": text(vf.get("words")) or text(vf.get("reason")), "held": sub.get("held") is True,
        "waiting": text(waiting.get("why")), "waiting_stage": text(waiting.get("stage")), "waiting_words": text(waiting.get("words")),
        "waiting_since": count(waiting.get("since")), "stalled": p.get("stalled") is True,
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


def working(reading):
    """The places a host's runner carries Flume's status of whose current stage is working, begun with its phase live
    (flume_facts), from reading, host_read's, read: (each place's folder name, in its launches' order, None), or (None,
    why one of them can't be read) (read.1)."""
    out = []
    for n, p in sorted((reading.get("places") or {}).items()):
        if p.get("why"):
            return None, p["why"]
        f = flume_facts(p.get("status"), p.get("place"))
        if f is not None and f["phase"] == "live" and f["state"] == "begun":
            out.append(os.path.basename(p["place"].rstrip("/")))
    return out, None


# --------------------------------------------------------------------------- a bolt given through Flume as it is shown

def stream_said(stream):
    """The Flume stream a started bolt's work runs in, in the words of its head line (Decision 14), as Flume's status
    of its places names it (where); nothing while crew reads none."""
    return f"in Flume stream {stream}" if stream else ""


def bare(work):
    """A piece of work as a line names it: a unit or chore by its own name, a fix by its place's, <bolt>--<name>."""
    kind, _, rest = work.partition("/")
    return rest.replace("/", "--", 1) if kind == "fix" else rest if kind in ("unit", "chore") else work


def piece_said(s):
    """A crossed piece's stage (stage_of) as its line in crew bolts and the board says it (Decision 14): (its stage, as
    today's piece's word, with the tasks of a stage that has them and sluice's number of a submission; what goes with
    it, or ""): the work it waits on; the question it stopped short with, or the work it found; sluice's words it was
    sent back with; Flume's words of what it waits on its caller for, its held submission waiting on the user's send;
    the room it is queued for; the runner's words refusing it; or why crew can't tell its stage."""
    st = s["stage"]
    tasks = f" {s['tasks'][0]}/{s['tasks'][1]}" if s.get("tasks") and s["tasks"][1] and st in ("code", "verify") else ""
    stage = f"submitted #{s['submission']}" if st == "submitted" and s.get("submission") else st + tasks
    first = (s.get("words") or "").strip().splitlines()[0] if (s.get("words") or "").strip() else ""
    detail = (
        "on " + ", ".join(bare(w) for w in s.get("after", [])) if st == "waiting" else
        (f"found at {s.get('of')}: {first}" if s.get("found") else f"asks at {s.get('of')}: {first}") if st == "needs" else
        f"sent back by sluice: {first}" if s.get("sent_back") else
        "its submission waits held for the user's send" if st in ("waits", "stalled") and s.get("held") else
        f"waits on its caller at {s.get('of') or 'its submission'}: {first or s.get('why') or 'no words'}" if st in ("waits", "stalled") else
        f"for room at {s['of']}" if st == "queued" and s.get("of") else
        f"refused by the runner: {first or 'no words'}" if st == "refused" else
        s.get("why") or "" if st == "unknown" else "")
    return stage, detail


# ------------------------------------------------------------------------------------- a started bolt's launches

def work_of(u):
    """How a request names a unit or chore of the plan (Decision 4): unit/<unit>, or chore/<chore> for one marked
    Kind: chore (plan.11)."""
    return f"{'chore' if u.get('Kind') == 'chore' else 'unit'}/{u.name()}"


def brief(u):
    """A launch's brief for a unit or chore (Decision 5): the work's own words, less what the stage itself is told,
    which is its kind's: a unit's intent with its sources, and a chore's words."""
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


def reach(plan, requests, bolt, label, again=()):
    """What a plan write asks of the runners for a started bolt (Decisions 5 and 7), as the requests to append in order,
    each (act, work, its fields as plan.request takes them), from facts: plan, as the write leaves it; requests,
    requests.rec's records before them; label, the bolt's partition; again, the work (as requests name it) whose launch
    is dropped and launched anew, an amendment of a unit whose place is not launched. Each unit and chore of the bolt
    with no launch standing is launched, as a start launches them: in the file's order, each after the work its After
    names, cut from the bolt's branch, carrying the bolt's repository as the plan names it, for the runner whose
    configuration names it to take in the stream it gives (the user's ruling of 2026-11-01), the bolt's priority, its
    intent, the planner as recipient, its brief, and the launches of its After work; a launch standing whose After no longer names
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
    out = [("drop", r.get("Work"), {"Of": r.get("Request")}) for r in drops]
    n, num = next_request(requests) + len(out), {}
    for u in order:
        wk = names[u.name()]
        if wk not in fresh:
            num[u.name()] = number(newest[wk].get("Request"))
            continue
        num[u.name()], n = n, n + 1
        out.append(("launch", wk, {
            "Repo": plan.bolt(bolt).get("Repo"), "Kind": "chore" if u.get("Kind") == "chore" else "change", "Name": u.name(),
            "Base": base, "Priority": priority_of(plan, bolt), "Intent": f"{label}/{bolt}", "Recipient": f"{label}/planner",
            "After": [num[d] for d in u.all("After") if d in num], "Brief": brief(u)}))
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
    """How an approved amendment of a started bolt's unit reaches its place (Decision 7), from the facts stage_of takes:
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


# ------------------------------------------------------------------------------------------ answers and fixes

def piece_stage(requests, reads, launch):
    """A launch's piece's stage (stage_of), from requests.rec's records and the partition's runners as crew read them
    (reads, host_read's by host): the answer of the runner that took the launch (taken) and its record of the place
    launched; launching while none has taken it, and unknown where crew can't tell which did."""
    n = number(launch.get("Request"))
    reading, why = taken(reads, n)
    answer, place = (reading["answers"].get(n), reading["places"].get(n)) if reading else (None, None)
    return stage_of(launch.get("Work"), launch, answer, place, why or True, after_work(requests, launch))


def named_launch(requests, work):
    """The launch standing for the work a command names (Decision 9), as (launch, None), or (None, why): named as
    requests name it (unit/<u>, chore/<c>, fix/<bolt>/<name>, fix/main/<kit>/<name>), by its place's name (<u>,
    <bolt>--<name>, main--<name>), or a unit or chore by its own name. None stands for work Flume
    does not build, and a name two works answer to is said with both."""
    hits = {r.get("Work"): r for r in standing(requests)
            if work in (r.get("Work"), r.get("Name")) or r.get("Work") in (f"unit/{work}", f"chore/{work}")}
    if not hits:
        return None, (f"no launch of {work} stands in requests.rec, so no Flume place of it waits on an answer: crew answer "
                      "answers a place of work Flume builds, by its unit's, chore's or place's name")
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


def fix_launch(plan, requests, bolt, label, name, words):
    """The launch crew fix <bolt> <name> "<words>" appends for a fix on a started bolt (Decision 10), as (act, work, its
    fields as plan.request takes them), or (None, why): a place of the fix kind named <bolt>--<name>, cut from the
    bolt's branch, in the bolt's repository for the runner whose configuration names it to take, as reach launches its
    units, with the bolt's priority and its partition's (label) intent, the planner as recipient, the fix's words as its
    brief and nothing held. Refused while a launch of that fix stands on the bolt, merged or not, since the name is in
    use there (teams.3)."""
    work, base = f"fix/{bolt}/{name}", f"bolt/{bolt}"
    l = launch_of(requests, work)
    if l is not None:
        return None, (f"fix {name} is in use on bolt {bolt}: it is launched as Flume place {l.get('Name')} (request "
                      f"{l.get('Request')}), so name this fix differently")
    return ("launch", work, {
        "Repo": plan.bolt(bolt).get("Repo"), "Kind": "fix", "Name": f"{bolt}--{name}", "Base": base,
        "Priority": priority_of(plan, bolt), "Intent": f"{label}/{bolt}", "Recipient": f"{label}/planner", "Brief": words}), None


def take_main(plan, requests, bolt, label, main, words):
    """The launch of a crossed bolt's take-main fix (Decision 10, plan.8), once sluice refused its landing for a
    conflict with main at main (its revision): a fix as fix_launch makes it, named take-main-<main, seven>, its brief
    saying to take origin/main into the bolt and resolve, with sluice's words of the conflict, and beginning as every
    take-main fix's does, so the bolt's row says it takes main first (plan.TAKE_MAIN); None while a fix of that name
    stands on the bolt, so a refusal read twice launches it once."""
    name = f"take-main-{main[:7]}"
    if launch_of(requests, f"fix/{bolt}/{name}") is not None:
        return None
    return fix_launch(plan, requests, bolt, label, name, (
        f"Take main into the bolt: merge origin/main, at {main[:7]}, into this place, cut from bolt/{bolt}, resolving each "
        f"conflicting path keeping both intents, main's and the bolt's; sluice refused the bolt's landing for its conflict "
        f"with main: {words}"))[0]


def fix_drop_refusal(of, work, launch, s):
    """Why crew fix --drop of a fix on a started bolt, or crew main fix --drop of a fix of main, is refused (Decisions
    10 and 11, teams.3), or None to drop the launch standing: none stands, so what it would fix (of, bolt <bolt> or the
    kit) has no such fix; crew can't tell how far its place got (read.1); or its place has merged into its base, so
    what it changed is the bolt's, or main's, and a new fix undoes it. s, its stage (piece_stage)."""
    if launch is None:
        return f"{of} has no fix {work}: no launch of it stands in requests.rec"
    if s["stage"] == "unknown":
        return f"can't tell whether {work}'s place has merged into {launch.get('Base')}, so it is not dropped: {s['why']}"
    if s["stage"] in ("merged", "landed"):
        return (f"{work} has merged into {launch.get('Base')}, so it is not dropped: what it changed is "
                f"{'main' if launch.get('Base') == 'main' else 'the bolt'}'s, and a new fix undoes it")
    return None


def unlanded(bolt, kit, work, held):
    """Why a bolt given through Flume is not closed as landed (Decision 12), or None, from facts: work, each of its
    units and chores as (name, kind, its stage as stage_of gives it, with the commit its place landed at on the bolt);
    held, {commit: git's exit asking whether the kit's main now holds it, 0 yes, 1 no, any other git could not tell}.
    Its close reads each piece merged from the runner's records where today's reads a change archived or a chore's
    trailer on main, a Flume chore's commits carrying no crew trailer, and lands once main holds the commit each place
    landed at on the bolt, so a bolt sluice has not landed is not closed; a piece crew can't tell is not taken as
    landed (read.1)."""
    for name, kind, s in work:
        if s["stage"] == "unknown":
            return f"cannot tell whether {kind} {name} has landed: {s.get('why')}"
        if s["stage"] not in ("merged", "landed"):
            return f"{kind} {name} has not merged into bolt/{bolt}: it is {s['stage']}"
        c = s.get("commit")
        if not c:
            return (f"cannot tell whether {kind} {name} has landed on {kit}'s main: Flume's status of its place, as the runner "
                    "carried it, names no commit it landed at")
        if held.get(c) == 1:
            return (f"{kind} {name} has not landed on {kit}'s main: its place landed on bolt/{bolt} at {c[:7]}, which main does "
                    "not hold")
        if held.get(c) != 0:
            return f"cannot tell whether {kind} {name} has landed on {kit}'s main: git could not read {c[:7]} there"
    return None


def fixes_on(requests, reads, base):
    """Each fix whose launch stands on a base, bolt/<bolt> or main, in requests.rec's order, as (its launch, its stage),
    read from the runner that took it (reads, by host; piece_stage)."""
    return [(l, piece_stage(requests, reads, l)) for l in standing(requests)
            if l.get("Base") == base and (l.get("Work") or "").startswith("fix/")]


def fixes_in_flight(requests, reads, bolt):
    """The fixes in flight on a bolt given through Flume (Decision 10), {fix/<bolt>/<name>: its brief}: each whose launch
    stands and whose place has not merged into the bolt, landed or been dropped, its stage read from the runner that
    took it (fixes_on), one crew can't read counted in flight (read.1). A fix in flight holds the bolt's landing as
    today's does (plan.landing_unready, landing_rows)."""
    return {l.get("Work"): l.get("Brief") for l, s in fixes_on(requests, reads, f"bolt/{bolt}")
            if l.get("Work").startswith(f"fix/{bolt}/") and s["stage"] not in ("merged", "landed", "dropped")}


# ------------------------------------------------------------------------------------------------ a fix of main

def main_priority(plan):
    """A fix of main's priority at its launch (Decision 11): one above every bolt given through Flume (priority_of), so
    Flume starts its code ahead of theirs, a red main holding back every landing on it."""
    return sum(1 for b in plan.bolts() if b.get("Path") == "flume") + 1


def main_fix_launch(plan, requests, label, repo, name, words, served):
    """The launch crew main fix <kit> <name> "<the failure's words>" appends (Decision 11; Decision 15 of
    the-team-machinery-leaves), as (act, work, its fields as plan.request takes them), or (None, why): a place of the fix
    kind named main--<name>, cut from main, in the kit's repository (repo, as the partition's kits name it) for the
    runner whose configuration names it to take in the stream it gives (the user's ruling of 2026-11-01), ahead of every
    bolt (main_priority), its intent the kit's main, main-level ops as its recipient, the failure's words as its brief,
    and its submission held for the user's send (state.3). Refused while no runner answers for the partition (served,
    whether any runner's branch exists), since nothing would take it and the red main waits on it, the fix then being a
    bolt of one chore (state.3); and while a launch of that fix of the kit's main stands, landed or not, since the name
    is in use there."""
    kit = repo.split("/")[-1]
    if not served:
        return None, (f"no runner answers for {label}: its state repository holds no {runner_branch(label, '<host>')}, so nothing "
                      f"would take the fix; until a runner (flywheel-runner) serves {label}, a fix of {kit}'s red main is a bolt "
                      f"of one chore, proposed first among the planned (state.3); tell {label}-planner, who proposes it")
    work = f"fix/main/{kit}/{name}"
    l = launch_of(requests, work)
    if l is not None:
        return None, (f"fix {name} of {kit}'s main is in use: it is launched as Flume place {l.get('Name')} (request "
                      f"{l.get('Request')}), so name this fix differently")
    return ("launch", work, {
        "Repo": repo, "Kind": "fix", "Name": f"main--{name}", "Base": "main", "Priority": main_priority(plan),
        "Intent": f"{label}/main/{kit}", "Recipient": f"{label}/ops", "Hold": "submission", "Brief": words}), None


def sent_of(requests, reads, launch):
    """The retry that sent a fix of main's held submission on the user's word (Decision 11), standing for its launch:
    the newest retry of its submission, unless the runner that took the launch (reads, by host; taken) answered it
    refused; None while none stands. One whose runner crew can't read or tell stands, so no send is made twice on a
    reading crew lacks (read.1)."""
    n = launch.get("Request")
    sent = next((r for r in reversed(requests) if r.get("Act") == "retry" and r.get("Of") == n and r.get("Submission") == "yes"), None)
    reading = taken(reads, number(n))[0] if sent is not None else None
    answer = reading["answers"].get(number(sent.get("Request"))) if reading else None
    return None if answer is not None and answer.get("Outcome") == "refused" else sent


def send_refusal(work, launch, s, sent):
    """Why crew main fix <kit> <name> --send appends no retry of a fix of main's submission (Decision 11, state.3), or
    None to send it: no launch of it stands; the user's send of it was made already (sent_of), which the runner acts
    on, so it is not made twice; crew can't tell its stage (read.1); or its place is not one whose code has delivered
    and whose submission waits held, the one a send submits. s, its stage (piece_stage)."""
    if launch is None:
        return f"no launch of {work} stands in requests.rec, so there is no fix of main to send"
    if sent is not None:
        return (f"{work} was sent on the user's word by request {sent.get('Request')}, which the runner that took it acts "
                "on, so it is not sent twice")
    if s["stage"] == "unknown":
        return f"can't tell whether {work}'s submission waits held, so it is not sent: {s['why']}"
    if s["stage"] in ("waits", "stalled") and s.get("held"):
        return None
    return (f"{work}'s place{' ' + s['place'] if s.get('place') else ''} is {stage_said(s)}, and a fix of main is sent only once "
            "its code has delivered and its submission waits held")


def main_fixes_waiting(requests, reads):
    """Each fix of main a kit's landings row carries (Decision 11; crew-rail "A fix of main waits to land on its kit's
    row"): those whose launch stands and whose code has delivered with its submission waiting held, their stage read
    from the runner that took them (reads, by host; taken, piece_stage), in requests.rec's order, each {kit, name, host,
    brief, since, carried, sent}: since, when Flume read it waiting, in seconds, or None; carried, when the runner
    carried that status; sent, the number of the request that sent it on the user's word (sent_of), None while it waits
    on that word. One crew can't read is left off, as a bolt whose stage crew can't read is, being in no state it can
    tell to send (read.1)."""
    out = []
    for l in standing(requests):
        work = l.get("Work") or ""
        if not work.startswith("fix/main/"):
            continue
        s = piece_stage(requests, reads, l)
        if s["stage"] not in ("waits", "stalled") or not s.get("held"):
            continue
        reading = taken(reads, number(l.get("Request")))[0]
        place, sent = reading["places"][number(l.get("Request"))], sent_of(requests, reads, l)
        _, _, kit, name = work.split("/", 3)
        out.append(dict(kit=kit, name=name, host=reading["host"], brief=l.get("Brief") or "",
                        since=flume_facts(place["status"], place["place"])["waiting_since"], carried=place["at"],
                        sent=number(sent.get("Request")) if sent is not None else None))
    return out


# ------------------------------------------------------------------------------------- a role's work that lands

# The branch a role's work lands on, its repository's default: main, as crew reads every kit's main (plan.18) and cuts a
# fix of it (main_fix_launch).
ROLE_BASE = "main"
FORGE = re.compile(r"^[^/\s]+/[^/\s]+$")


def role_launch(requests, named, label, role, host, stream, repo, name, brief):
    """The launch crew role land <repo> <name> --brief-file <file> appends for a role's work that lands (Decision 10 of
    roles-run-as-flume-kinds; roles.7 part 3), as (act, work, its fields as plan.request takes them), or (None,
    why): a place of Flume's own chore kind named name, cut from repo's default branch (ROLE_BASE), on the main level's
    host and in the role's stream, at priority 0, its intent the role's run, <label>-<role>, its recipient the role's
    address, <label>/<role>, so its landing, or a wait on its caller, reaches the role's next run, and its brief the
    file's text whole, since the stage's agent is fresh. Refused for a repository not named as its forge address,
    <owner>/<name>, or one crew does not name (named, the teams file's and the plan's), for a brief with no words, and
    while a launch of role/<role>/<name> stands, since the name is in use there."""
    if not FORGE.match(repo):
        return None, f"a repository is named by its forge address, <owner>/<name>, which the runner resolves to its clone, not {repo}"
    if repo not in named:
        return None, (f"crew names no repository {repo}: a role's work lands in a blueprints repository or a kit the teams file "
                      "names, or a repository the plan names, and it names " + ", ".join(sorted(n for n in named if FORGE.match(n))))
    if not brief.strip():
        return None, f"the brief for {name} holds no words, and a chore's agent starts fresh with its brief alone"
    work = f"role/{role}/{name}"
    l = launch_of(requests, work)
    if l is not None:
        return None, (f"{name} is in use for {label}/{role}: request {l.get('Request')} launched it in {l.get('Repo')} as Flume "
                      f"place chore--{l.get('Name')}, so name this work differently")
    return ("launch", work, {
        "Repo": repo, "Kind": "chore", "Name": name, "Base": ROLE_BASE, "Host": host, "Stream": stream, "Priority": 0,
        "Intent": f"{label}-{role}", "Recipient": f"{label}/{role}", "Brief": brief}), None
