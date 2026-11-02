#!/usr/bin/env python3
"""hold.py: crew hold, crew go and crew update, and the restart an update makes due (teams.19).

  crew hold <host>|--all "<why>" [--now]
                                 hold each host named: crew starts no agent there until crew go, and every standing
                                 agent up there is told to finish the step it is in and start nothing new; a stage
                                 already running ends as it would. With --now every crew agent there is ended at once,
                                 a stage's included, which its conductor runs again after go
  crew hold status [<host>|--all]
                                 each host's hold, and what still works there: an agent working, waiting on a question
                                 to the user or running background work of its own, a stage not yet ended, crew's tests
  crew hold wait [<host>|--all] [--timeout <ms>]
                                 wait until each host is quiet, then end every crew agent there, its panes kept, so
                                 herdr can be restarted or the host rebooted; half an hour unless --timeout says
  crew go <host>|--all           lift the hold: every standing agent whose pane is empty brought back with its
                                 conversation and greeted (crew revive), every one still up told the hold is lifted,
                                 the consoles' tabs run again, and every agent an update has made due restarted; a
                                 team crossed to Flume meanwhile is closed, never brought back (close_crossing)
  crew update [<host>|--all]     every standing agent whose start an update of crew, or of its brief, has made due
                                 handed to crew _renew, which restarts it once it is idle with nothing of its own
                                 running in the background; a team's conductor and ops once their team has crossed to
                                 Flume are due an end, which crew _renew gives them the same way, never a restart, and
                                 the team is closed once both are down; a main level's agent whose role now runs as
                                 its kind is passed over, its next turn's end ending it, never restarted

Each runs on the host it acts on (code.3): crew _hold set|status|wait, crew _go and crew _update there, and crew
_renew <agent> on the agent's host, which crew's Stop hook hands it to at the end of the agent's turn (hooks/stop).
Every host crew runs agents on is one of --all; a host that does not answer is named, and the rest still act (read.3)."""
import argparse, contextlib, datetime, fcntl, json, os, pathlib, re, shlex, subprocess, sys, threading, time

import crew
import ops
import plan
import record
import runner
import transcript
from crew import Refusal, Stopped, fail

# Where each agent's restart for an update keeps its lock and says what it did.
RENEW = pathlib.Path.home() / ".local/state/crew/renew"
# How long a restart handed at the end of an agent's turn waits for herdr to read it idle.
SETTLE = 120
# How many times a restart looks for its agent's exit after its stop gave up, five seconds apart: ten minutes.
EXITING = 120
# How often a hold's wait looks again, in seconds.
LOOK = 10

HOLD_NOTICE = ("{host} is held by {by}: {why}. Finish the step you are in, then start nothing new: crew starts no agent on "
               "{host} until crew go {host}, and refuses a stage, a fix, a give or a review there meanwhile. A stage "
               "already running ends as it would: let it end, and run no next one. Then end your turn and wait to be told.")
GO_NOTICE = "{host} is no longer held: crew starts agents there again. Carry on with what is yours."


# ------------------------------------------------------------------------------------------- what crew decides

def hosts_named(fleet, which):
    """The hosts a command acts on: every host crew runs agents on, a team's or a main level's, for --all; else the one
    named, which must be a host of the hosts file."""
    if which in (None, "--all"):
        return sorted({t["machine"] for t in fleet["teams"].values()} | {p["machine"] for p in fleet["partitions"].values()})
    which in fleet["hosts"] or fail(f"{which} is no host of the fleet's hosts file. hosts: " + " ".join(sorted(fleet["hosts"])))
    return [which]


def crew_wait(command):
    """Whether a background command is one of crew's waits, which only reads and which the agent starts again after a
    restart: crew unit wait, crew chore wait, crew fix ... --wait, crew review ... --wait, and any other crew command
    ending in a wait, a card's wait from before crew kept none among them (teams.24)."""
    return bool(command and re.search(r"(^|[\s/;&|(])crew\s", command) and re.search(r"(^|\s)(--)?wait(\s|$)", command))


def busy_said(facts, tests):
    """What still works on a held host (teams.19), from what crew read of each crew agent up there and of crew's
    tests: an agent working, one waiting on a question to the user, one running background work of its own other than
    crew's waits, a stage still owed its end, and one crew can't read (read.1). Empty once the host is quiet."""
    out = []
    for f in facts:
        name = f["name"]
        if f.get("owes"):
            out.append(f"{name}'s {f['owes']} has not ended")
        if f.get("unread"):
            out.append(f"crew can't tell what {name} is doing: {f['unread']}")
        elif f["status"] == "working":
            out.append(f"{name} is working")
        elif f.get("asking") or f["status"] == "blocked":
            out.append(f"{name} waits on a question to you in its pane")
        elif f.get("own"):
            n = len(f["own"])
            out.append(f"{name} runs {n} background task{'' if n == 1 else 's'} of its own: " + "; ".join(c or "?" for c in f["own"]))
    if tests:
        out.append(f"{tests} of crew's tests {'is' if tests == 1 else 'are'} running")
    return out


def renew_ready(status, asking, unread, own):
    """Whether an agent due a restart for an update may be restarted now (teams.19): once it is idle, waiting on no
    question to the user and running no background work of its own other than crew's waits. Returns (ready, why not)."""
    if unread:
        return False, f"crew can't tell what it is doing: {unread}"
    if status is None:
        return False, "it is not up"
    if status == "working":
        return False, "it is working"
    if asking or status == "blocked":
        return False, "it waits on a question to you in its pane"
    if own:
        return False, f"it runs background work of its own: {'; '.join(c or '?' for c in own)}"
    return True, None


def renew_exited(holds, unread, marked, session, down):
    """Whether a restart for an update starts an agent it finds not up, with no stop (teams.19): only one an earlier
    restart's keys ended, from facts: whether herdr lists its pane with an agent in it (pane_holds: False for none,
    None when unread), what crew could not read of the pane, the session an earlier restart that could not see it exit
    typed its exit into (its mark, None when none), the session of its last start, and whether its team, main level or
    dispatcher was taken down. An agent the user ended by hand, or one a crash took, has no mark naming its session and
    stays crew revive's. Returns (start, why not)."""
    if down:
        return False, "it was taken down; it stays down"
    if unread:
        return False, f"crew can't tell whether its pane holds it: {unread}"
    if holds is False and marked and marked == session:
        return True, None
    return False, "it is not up"


def renew_notice(was, now, changes):
    """What an agent restarted for an update is told: the crew it started on and the one it runs now, what changed
    there for it, and that its background waits ended with the restart."""
    said = f"crew restarted you on crew {now or 'as it now is'}" + (f" (you started on {was})" if was else "") + \
        ", so your brief and crew's plugin are as they now stand."
    if changes:
        said += " What changed: " + "; ".join(changes) + "."
    return said + (" A command you ran in the background ended with the restart: start again any wait you still need, "
                   "then carry on with what is yours.")


def stamp(t=None):
    return (t or datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%dT%H:%MZ")


# ------------------------------------------------------------------------------------------- what crew reads

def agents_on_host(fleet):
    """Every Agents crew keeps on this host: each team's, each of its main levels' sessions, each dispatcher's."""
    out = []
    for kind, scope in crew.here(fleet):
        if kind == "team":
            out.append(crew.Team(fleet, crew.team_of(fleet, scope)))
        elif kind == "main":
            out += crew.mains(fleet, scope)
        else:
            out.append(crew.standing(fleet, "dispatch", scope))
    return out


def roles_of(a):
    """The roles of an Agents' panes file that hold an agent: its standing roles, a team's slots and the reviewer."""
    return [r for r, *_ in a.lines("panes") if r in a.standing or r.startswith("unit-") or r == "reviewer"]


def own_work(info):
    """The background work an agent started that is not one of crew's waits: (its commands, what crew could not
    read), from its session's transcript (plan.background)."""
    pending, _, unread = plan.background(info or {})
    if unread:
        return None, unread
    if not pending:
        return [], None
    sid = info["agent_session"]["value"]
    commands = transcript.started_commands(transcript.find(sid)) or {}
    return [commands.get(t) for t in pending if not crew_wait(commands.get(t))], None


def labels_here(fleet):
    """The partitions crew runs anything for on this host."""
    return sorted({fleet["teams"][s]["label"] if k == "team" else s for k, s in crew.here(fleet)})


def facts_here(fleet):
    """What crew reads of each crew agent up on this host, for busy_said, and the count of crew's tests running."""
    facts = []
    for a in agents_on_host(fleet):
        owed = {l[0]: f"{l[2]} of {l[1]}" for l in a.lines("stages") if len(l) > 2} if isinstance(a, crew.Team) else {}
        for role in roles_of(a):
            name, pane = a.agent_of(role), a.pane(role)
            status = a.status(role, fresh=True)
            f = {"name": name, "status": status, "owes": owed.get(role)}
            if status is not None:
                _, f["asking"], unread = crew.waits_on_question(fleet, name)
                own, unread2 = own_work(a.herdr.agent(pane, fresh=True)) if not unread else (None, None)
                f.update(own=own, unread=unread or unread2)
            if status is not None or f["owes"]:
                facts.append(f)
    r = subprocess.run(["python3", "-c", ops.SLOTS], capture_output=True, text=True)
    tests = int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else 0
    return facts, tests


def marked_exit(name, session):
    """The session an earlier restart of an agent typed its exit into and did not see go (RENEW/<agent>.exiting), or
    None when no restart left one. A mark of another session than the agent's last start is stale, another start having
    come since, and is removed as it is read."""
    mark = RENEW / f"{name}.exiting"
    try:
        marked = mark.read_text().strip()
    except FileNotFoundError:
        return None
    except OSError as e:
        fail(f"crew can't read {mark}: {e}")
    if marked != session:
        mark.unlink(missing_ok=True)
    return marked or None


def changes_for(was, now):
    """The subjects of crew's commits between two of its commits that changed what an agent loads or its briefs, at
    most five, newest first; none when git can't read them."""
    if not (was and now) or was == now:
        return []
    r = subprocess.run(["git", "-C", str(crew.HOME), "log", "--no-merges", "--format=%s", f"{was}..{now}", "--",
                        *crew.LOADED, "plugin/roles"], capture_output=True, text=True)
    return r.stdout.splitlines()[:5] if r.returncode == 0 else []


# ------------------------------------------------------------------------------------------- what crew does

def write_hold(h):
    crew.HOLD.parent.mkdir(parents=True, exist_ok=True)
    new = crew.HOLD.with_name("hold.new")
    new.write_text(json.dumps(h) + "\n")
    os.replace(new, crew.HOLD)


def tell_each(fleet, names, text):
    """A notice told to each agent of names that is up, side by side; one not up, or waiting on a question, is said."""
    def one(name):
        try:
            if crew.agent_status(fleet, name):
                crew.tell(fleet, name, text)
        except Refusal as e:
            print(e, file=sys.stderr)
    ths = [threading.Thread(target=one, args=(n,)) for n in names]
    for th in ths:
        th.start()
    for th in ths:
        th.join()


def take_down(fleet, force):
    """Every crew agent on this host ended, its pane kept, so a restart of herdr brings back only shells, which crew go
    revives (teams.19): an agent working is left and said unless force, and a slot's stage still owed its end ends with
    its agent (Agents.stop). Returns what could not be ended."""
    left, host = [], crew.this_host()
    for a in agents_on_host(fleet):
        a.force = force
        end = plan.ending(fleet, a.t) if isinstance(a, crew.Team) else None
        for role in roles_of(a):
            if not a.status(role):
                continue
            why = a.stop(role, end)
            if why:
                left.append(why)
            else:
                print(f"{a.agent_of(role)} is ended")
        if a.ended:
            a.record("host.down", f"host({host}): down", a.ended)
    return left


def hold_set(fleet, a):
    """crew _hold set: this host held, recorded, its standing agents told, and with --now every crew agent ended."""
    host, was = crew.this_host(), crew.held()
    h = {"by": record.who(), "why": a.why, "at": (was or {}).get("at") or stamp(), "now": a.now}
    write_hold(h)
    for label in labels_here(fleet):
        record.emit(label, "host.hold", [f"host/{host}"], why=f"host({host}): hold" + (" now" if a.now else ""))
    print(f"{host} is held: crew starts no agent here until crew go {host}")
    if a.now:
        for why in take_down(fleet, force=True):
            print(why, file=sys.stderr)
    else:
        tell_each(fleet, crew.agents_here(fleet), HOLD_NOTICE.format(host=host, **h))
    hold_status(fleet, a)


def hold_status(fleet, a):
    """crew _hold status: this host's hold and what still works here."""
    host, h = crew.this_host(), crew.held()
    print(crew.held_said(host, h) if h else f"{host} is not held")
    facts, tests = facts_here(fleet)
    busy = busy_said(facts, tests)
    for line in busy:
        print(f"  {line}")
    if not busy:
        up = [f["name"] for f in facts if f["status"] is not None]
        print(f"  quiet: {len(up)} crew agent{'' if len(up) == 1 else 's'} up, none at work; crew hold wait {host} ends them"
              if up else f"  every crew agent here is down: herdr can be restarted; crew go {host} brings them back")
    return busy


def hold_wait(fleet, a):
    """crew _hold wait: once this host is quiet, every crew agent here ended (take_down); stops at the timeout,
    saying what still works."""
    host = crew.this_host()
    crew.held() or fail(f"{host} is not held: crew hold {host} \"<why>\" holds it first")
    deadline, said = time.monotonic() + a.timeout / 1000, None
    while True:
        facts, tests = facts_here(fleet)
        busy = busy_said(facts, tests)
        if not busy:
            left = take_down(fleet, force=False)
            if not left:
                print(f"{host}: every crew agent is down. herdr can be restarted, or the host rebooted; crew go {host} brings them back")
                return
            busy = left
        if busy != said:
            print(f"{host} waits on: " + "; ".join(busy))
            said = busy
        if time.monotonic() >= deadline:
            print(f"{host} is still not quiet at the timeout: " + "; ".join(busy), file=sys.stderr)
            raise Stopped(1)
        crew.nap(LOOK)


def go(fleet, a):
    """crew _go: this host's hold lifted and recorded; every standing agent whose pane is empty brought back with its
    conversation and greeted (plan.revive_cmd); every one that stayed up told the hold is lifted; each console's tabs
    run again; and every agent an update made due handed its restart."""
    host = crew.this_host()
    if not crew.held():
        print(f"{host} is not held")
    up = [n for n in crew.agents_here(fleet) if crew.agent_status(fleet, n)]
    crew.HOLD.unlink(missing_ok=True)
    for label in labels_here(fleet):
        record.emit(label, "host.go", [f"host/{host}"], why=f"host({host}): go")
    print(f"{host} is no longer held")
    plan.revive_cmd(fleet, argparse.Namespace())
    tell_each(fleet, up, GO_NOTICE.format(host=host))
    for label in sorted(fleet["partitions"]):
        if label in fleet["hosts"].get(host, {}).get("sessions", {}):
            try:
                plan.console_cmd(fleet, argparse.Namespace(act="up", label=label, tabs=[]))
            except Refusal as e:
                print(e, file=sys.stderr)
    update_here(fleet, argparse.Namespace(label=None))


def update_here(fleet, a):
    """crew _update: every standing agent of this host, or of one partition here, that an update has made due handed to
    crew _renew, which restarts it once it is idle; none while the host is held, whose go does it."""
    host, h = crew.this_host(), crew.held()
    if h:
        print(f"{host} is held; crew go {host} restarts what an update made due")
        return
    commit, version = crew.crew_version()
    for name in crew.agents_here(fleet, a.label):
        due, why, started = crew.due_of(fleet, name, commit=commit)
        if due and why == crew.KIND_SAID:  # passed over (design Decision 14): its own stop, or crew main up, ends it
            print(f"{name} is passed over, never restarted: {why}; while it is up, the end of its next turn ends it, "
                  f"as crew main up {crew.label_of_agent(fleet, name)} does")
        elif due:
            hand(name)
            print(f"{name} is due ({why}): " + ("it is ended once it is idle, never restarted" if why == crew.CROSSED_SAID else
                                                f"it is restarted on crew {version or (commit or '?')[:7]} once it is idle"))
        elif why:
            print(f"{name}: {why}", file=sys.stderr)


def hand(name):
    """The restart of an agent due for an update handed to a process of its own on this host (code.9), its words kept in
    RENEW/<agent>.log."""
    RENEW.mkdir(parents=True, exist_ok=True)
    with open(RENEW / f"{name}.log", "a") as log:
        subprocess.Popen(["bash", str(crew.HOME / "plugin/bin/crew"), "_renew", name], stdin=subprocess.DEVNULL,
                         stdout=log, stderr=log, start_new_session=True)


def holding(fleet, name):
    """The Agents an agent's standing role is kept in, and that role: a team's, a main level's or a dispatcher's."""
    return crew.holding_of(fleet, name) or fail(f"{name} is no standing agent of crew's: only those are restarted for an update")


def renew(fleet, a):
    """crew _renew <agent>: an agent an update made due (crew.due_of), or whose team's bolt changed under it (teams.20),
    restarted on crew as it now is, once herdr reads it
    idle with no question open and no background work of its own but crew's waits (renew_ready), within a.wait seconds;
    a conductor fresh, as its restart always is, and every other role with its conversation; greeted, or told what
    changed, and recorded. One process at a time per agent; nothing while the host is held. It ends with the agent
    running: one still up when its stop gives up is watched for EXITING looks and started the moment it goes, or left
    as it was, still due, when it never does, with a mark naming the session its exit was typed into; and one a later
    restart finds those keys ended (renew_exited) is started with no stop. A crossed team's conductor or ops, due an
    end (crew.end_due), is ended in the same way once idle and never started again (cross_end); one not up has
    nothing to end, and once neither is up its team's crossing is closed (close_crossing), however they went down. A
    main level's agent whose role now runs as its kind is ended so too, its pane left with nothing started in it
    (kind_end)."""
    name = a.agent
    host, _ = crew.place_of_agent(fleet, name)
    host == crew.this_host() or fail(f"{name} runs on {host}: crew _renew runs there")
    RENEW.mkdir(parents=True, exist_ok=True)
    lock = open(RENEW / f"{name}.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(f"{name} is already being restarted")
        return
    deadline = time.monotonic() + a.wait
    branch = crew.branch_now(fleet, name)  # read once: it reads the plan
    gone = False  # an earlier restart's keys ended it, so it is started with no stop
    while True:
        if crew.held():
            print(f"{host} is held; crew go {host} hands {name} what it is due")
            return
        due, why, started = crew.due_of(fleet, name, branch=branch)
        if not due:
            print(f"{name} is not due a restart" + (f": {why}" if why else ""))
            return
        ending = why in (crew.CROSSED_SAID, crew.KIND_SAID)
        status, asking, unread = crew.waits_on_question(fleet, name)
        if status is None and not unread and why == crew.KIND_SAID:
            print(f"{name} is not up, so nothing of it is left to end: {why}")
            return
        if status is None and not unread and ending:
            print(f"{name} is not up, so its team's crossing to Flume has nothing of it to end")
            team, _ = holding(fleet, name)
            team.ensure()
            with crossing(team):
                close_crossing(fleet, team)
            return
        if status is None and not unread:
            holds, unread = crew.read_pane_agent(fleet, name)
            session = started["session"]
            gone, not_yet = renew_exited(holds, unread, marked_exit(name, session), session, holding(fleet, name)[0].down())
            if gone:
                break
        else:
            own, unread2 = own_work(crew.agent_get(fleet, name)) if status and not unread else ([], None)
            ready, not_yet = renew_ready(status, asking, unread or unread2, own)
            if ready:
                break
        if time.monotonic() >= deadline:
            print(f"{name} is not {'ended' if ending else 'restarted'}: {not_yet}; the end of its next turn hands it back")
            return
        crew.nap(5)
    agents, role = holding(fleet, name)
    agents.ensure()
    if why == crew.KIND_SAID:
        kind_end(fleet, agents, role)
        return
    if ending:
        cross_end(fleet, agents, role)
        return
    commit, version = crew.crew_version()
    mark = RENEW / f"{name}.exiting"
    if gone:
        print(f"{name} was ended by the exit an earlier restart typed; crew starts it")
    else:
        why = agents.stop(role, waits=True)  # renew_ready: nothing runs in its background but crew's waits, which end here
        if why == crew.working_said(name):  # it went to work since herdr read it idle, and nothing was typed to it
            print(why, file=sys.stderr)
            return
        if why:  # its exit was typed and it has not gone yet: the keys may still end it
            if started.get("session"):
                mark.write_text(started["session"] + "\n")
            print(f"{name} did not exit at once; crew watches for its exit")
            if not agents.exited(role, EXITING):
                print(f"{why}; it runs on as it was, still due: the end of its next turn hands it back", file=sys.stderr)
                return
    fresh = role == "conductor"
    if not agents.start(role, None if fresh else "resume"):
        raise Stopped(1)
    mark.unlink(missing_ok=True)
    agents.record("agent.renew", f"update({host}): restart {name}", [role])
    started = started or {}
    moved = crew.branch_due(started, branch)[1] if branch is not crew.UNREAD else None
    notice = renew_notice(started.get("version"), version, changes_for(started.get("commit"), commit) + ([moved] if moved else []))
    if isinstance(agents, crew.Team) and role == "conductor":
        plan.greeted(plan.greet_team(fleet, agents.t, ["conductor"], notice=notice))
    elif role in agents.fresh:  # it had no conversation to pick up, so it is greeted as any fresh start is
        plan.greeted(plan.greet_team(fleet, agents.t, [role]) if isinstance(agents, crew.Team) else plan.greeting(fleet, agents, [role]))
    else:
        crew.tell(fleet, name, notice, taken=True, what="the notice of its restart")
    print(f"{name} is restarted on crew {version or (commit or '?')[:7]}")


def crossed_told(team, kits):
    """What the partition's dispatchers are told once a team has crossed to Flume (Decision 3 of
    teams-cross-to-flume-as-their-bolts-land): it takes a bolt of its kits whenever one is planned."""
    return (f"{team} has crossed to Flume: it takes a bolt of {' or '.join(kits)} whenever one is planned, never full, its work "
            f"running in Flume places. Give it the next planned bolt of its kits.")


def crossing_recorded(label, team):
    """Whether this host's run record already holds a team's crossing (runner.cross_recorded), read from its own day
    files for the partition, newest first, until one tells: a team's crossing is recorded on its own host alone, by the
    act that closes it there (close_crossing), and is in this host's file before it reaches the branch, whose push a
    busy branch may refuse (record.2), so this host's own entries answer it, as they answer a card's close
    (cards.host_entries). A file crew can't read is a refusal naming it (read.1)."""
    d = record.ROOT / label / "runs" / crew.this_host()
    for f in sorted(d.glob("*.rec"), reverse=True) if d.is_dir() else []:
        try:
            entries = record.parse(f.read_text())
        except OSError as err:
            fail(f"crew can't tell whether {team} has crossed to Flume: {f} could not be read: {err.strerror or err}")
        found = runner.cross_recorded(sorted(entries, key=lambda e: (e["At"], e["Id"])), team)
        if found is not None:
            return found
    return False


@contextlib.contextmanager
def crossing(team):
    """One team's crossing acts on this host, one at a time (RENEW/<team>.cross.lock), so the act that finds its last
    role down is the one that closes it."""
    RENEW.mkdir(parents=True, exist_ok=True)
    with open(RENEW / f"{team.name}.cross.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def cross_end(fleet, team, role):
    """A crossed team's conductor or ops ended once idle, never started again (Decision 3 of
    teams-cross-to-flume-as-their-bolts-land): its exit typed as a restart's is, watched for when slow, and recorded
    (agent.end); then its team's crossing closed once neither role is up (close_crossing). A host held meanwhile ends
    nothing (teams.19)."""
    name, t = team.agent_of(role), team.t
    with crossing(team):
        if crew.held():
            print(f"{t['machine']} is held; crew go {t['machine']} hands {name} its end")
            return
        why = team.stop(role, waits=True)  # renew_ready: nothing runs in its background but crew's waits, which end here
        if why == crew.working_said(name):  # it went to work since herdr read it idle, and nothing was typed to it
            print(why, file=sys.stderr)
            return
        if why:  # its exit was typed and it has not gone yet: the keys may still end it
            print(f"{name} did not exit at once; crew watches for its exit")
            if not team.exited(role, EXITING):
                print(f"{why}; it runs on as it was, still due its end: the end of its next turn hands it back", file=sys.stderr)
                return
        team.record("agent.end", f"cross({team.name}): end {name}", [role])
        print(f"{name} is ended: {team.name} has crossed to Flume, whose places run its work")
        close_crossing(fleet, team)


def kind_end(fleet, main, role):
    """A main level's standing agent ended once idle and never started again, its partition now running its role as its
    kind (design Decision 14 of roles-run-as-flume-kinds; host-holds-and-updates "A standing agent of a role that now
    runs as its kind is ended at its next stop"): its exit typed as a restart's is, watched for when slow, its pane left
    with nothing started in it, and recorded (agent.end). Nothing starts it again: it stands in no session of the main
    level (crew.main_sessions), so neither crew main up nor crew revive does. A host held meanwhile ends nothing
    (teams.19)."""
    name, host = main.agent_of(role), crew.this_host()
    if crew.held():
        print(f"{host} is held; crew go {host} hands {name} its end")
        return
    why = main.stop(role, waits=True)  # renew_ready: nothing runs in its background but crew's waits, which end here
    if why == crew.working_said(name):  # it went to work since herdr read it idle, and nothing was typed to it
        print(why, file=sys.stderr)
        return
    if why:  # its exit was typed and it has not gone yet: the keys may still end it
        print(f"{name} did not exit at once; crew watches for its exit")
        if not main.exited(role, EXITING):
            print(f"{why}; it runs on as it was, still due its end: the end of its next turn hands it back", file=sys.stderr)
            return
    main.record("agent.end", f"main({main.label}): end {name}, which runs as its kind", [role])
    print(f"{name} is ended: {crew.KIND_SAID}, so nothing starts it again; its pane is left")


def close_crossing(fleet, team):
    """A crossed team's crossing closed once neither its conductor nor its ops is up, however they went down: ended at
    their stops (cross_end), by a host's hold (take_down) or by any other hand (runner.cross_close, Decision 3 of
    teams-cross-to-flume-as-their-bolts-land): its workspaces closed as crew close closes them and the team marked
    down, its slots freed (plan.reap), team.cross recorded naming its stream, and the partition's dispatchers that are
    up told it takes bolts of its kits; once, a crossing this host's record already holds (crossing_recorded) closing
    nothing again; never on a held host, whose crew go closes it (teams.19). Run inside the team's crossing lock."""
    t = team.t
    if crew.held():
        print(f"{t['machine']} is held; crew go {t['machine']} closes {team.name}'s crossing to Flume")
        return
    try:
        path = plan.crossing_path(fleet, t)
        recorded = crossing_recorded(t["label"], team.name)
    except Refusal as e:
        print(f"{e}; {team.name}'s workspaces are left as they are", file=sys.stderr)
        return
    if not runner.cross_close(path, [r for r in team.standing if team.status(r, fresh=True)], recorded):
        if recorded:
            print(f"{team.name}'s crossing to Flume is recorded already: nothing of it is left to close")
        return
    team.teardown(plan.ending(fleet, t))
    team.mark(down=True)
    try:
        plan.reap(fleet, team)
    except Refusal as e:
        print(e, file=sys.stderr)
    record.emit(t["label"], "team.cross", [f"team/{team.name}"], why=f"team({team.name}): cross to flume", State=t["flume"])
    plan.tell_dispatchers(fleet, t["label"], crossed_told(team.name, [k["name"] for k in crew.kits_of(t)]))
    print(f"{team.name} has crossed to Flume: its workspaces are closed, and its work runs in Flume places on "
          f"{t['machine']}, in stream {t['flume']}")


# ------------------------------------------------------------------------------------------- across hosts

def fan(fleet, hosts, *argv):
    """crew <argv> run on each host, side by side, as the one asking (crew.crew_argv), each line it says prefixed with
    its host when there is more than one; a host that does not answer is named (read.3). Returns the worst exit."""
    procs = []
    for host in hosts:
        argv_ = crew.crew_argv(fleet, host, *argv)
        cmd = argv_ if host == crew.this_host() else ["ssh", "-o", "BatchMode=yes", fleet["hosts"][host]["ssh"], shlex.join(argv_)]
        procs.append((host, subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)))

    def relay(host, proc):
        for line in proc.stdout:
            sys.stdout.write((f"{host}: " if len(procs) > 1 else "") + line)
            sys.stdout.flush()
    ths = [threading.Thread(target=relay, args=p) for p in procs]
    for th in ths:
        th.start()
    rc = 0
    for (host, proc), th in zip(procs, ths):
        th.join()
        code = proc.wait()
        if code == 255 and host != crew.this_host():
            print(f"{host} did not answer", file=sys.stderr)
        rc = max(rc, code)
    return rc


def front(fleet, argv):
    """crew hold|go|update as the user or an agent types them, run on each host they name."""
    cmd, rest = argv[0], argv[1:]
    if cmd == "go":
        len(rest) == 1 or fail("usage: crew go <host>|--all")
        return fan(fleet, hosts_named(fleet, rest[0]), "_go")
    if cmd == "update":
        len(rest) <= 1 or fail("usage: crew update [<host>|--all]")
        return fan(fleet, hosts_named(fleet, rest[0] if rest else None), "_update")
    if rest[:1] == ["status"]:
        len(rest) <= 2 or fail("usage: crew hold status [<host>|--all]")
        return fan(fleet, hosts_named(fleet, rest[1] if len(rest) > 1 else None), "_hold", "status")
    if rest[:1] == ["wait"]:
        words, timeout = rest[1:], "1800000"
        if "--timeout" in words:
            i = words.index("--timeout")
            timeout = words[i + 1] if i + 1 < len(words) and words[i + 1].isdigit() else fail("--timeout takes a number of milliseconds")
            words = words[:i] + words[i + 2:]
        len(words) <= 1 or fail("usage: crew hold wait [<host>|--all] [--timeout <ms>]")
        return fan(fleet, hosts_named(fleet, words[0] if words else None), "_hold", "wait", "--timeout", timeout)
    now, words = "--now" in rest, [w for w in rest if w != "--now"]
    len(words) == 2 and words[1].strip() or fail('usage: crew hold <host>|--all "<why>" [--now]')
    return fan(fleet, hosts_named(fleet, words[0]), "_hold", "set", "--why", words[1], *(["--now"] if now else []))


def parser():
    ap = argparse.ArgumentParser(prog="crew")
    sub = ap.add_subparsers(dest="cmd", required=True)
    x = sub.add_parser("_hold")
    acts = x.add_subparsers(dest="act", required=True)
    y = acts.add_parser("set")
    y.add_argument("--why", required=True)
    y.add_argument("--now", action="store_true")
    acts.add_parser("status")
    y = acts.add_parser("wait")
    y.add_argument("--timeout", type=int, default=1800000)
    sub.add_parser("_go")
    x = sub.add_parser("_update")
    x.add_argument("--label")
    x = sub.add_parser("_renew")
    x.add_argument("agent")
    x.add_argument("--wait", type=int, default=SETTLE)
    return ap


def main(argv):
    plan.need_recutils()
    fleet = crew.load()
    if argv[:1] in (["hold"], ["go"], ["update"]):
        sys.exit(front(fleet, argv))
    a = parser().parse_args(argv)
    sys.stdout.reconfigure(line_buffering=True)
    if a.cmd == "_hold":
        {"set": hold_set, "status": hold_status, "wait": hold_wait}[a.act](fleet, a)
    else:
        {"_go": go, "_update": update_here, "_renew": renew}[a.cmd](fleet, a)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
    except Stopped as e:
        sys.exit(e.code)
