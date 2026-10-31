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
recfix; each runner answers on a branch of its own, <label>/runner/<host>, which crew never writes (state.5).

Each is a function of plain facts (code.7); plan.py, crew.py and hold.py read the facts and act on what they decide.
This module imports nothing outside the standard library and crew's own modules (code.1)."""
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

