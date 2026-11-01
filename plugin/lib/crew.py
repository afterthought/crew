#!/usr/bin/env python3
"""crew.py: read the teams file and answer from it.

  crew.py labels                      every partition's label
  crew.py brief <label> <definition> [name]
                                      a definition's brief for a partition's main level; name is the agent's own
  crew.py launch <label> <role> [resume]
                                      how crew-role starts a main level's role, as shell assignments
  crew.py tell <agent> "<text>" [--taken]
                                      prompt an agent wherever it runs, the text marked [crew tell from <sender>];
                                      refused, with nothing typed, while it waits on a question in its pane; with
                                      --taken, read back from its transcript and sent once more when not taken
  crew.py tell --board < word.json    a word posted from a dock, {label, key, to, text}, checked and told its item's
                                      agent, marked [crew tell from <user>@board] (on <kind> <name>)
  crew.py send <label> "<text>"       send the text to the partition's operator, its door, marked
                                      [crew tell from <sender>] (sent to <label>)
  crew.py found <agent>               an agent of this host as herdr lists it, one JSON object, its name given back in
                                      the pane crew keeps for it when herdr dropped it there from the session crew
                                      started (read_agent from another host)
  crew.py run-name                    the name and partition of the role's run FLUME_PLACE is, as shell assignments of
                                      CREW_AGENT and CREW_LABEL; nothing for a place that is no run

The agents themselves, a main level's, are started, greeted and ended by plan.py's commands, through Agents here.

Each role is an agent definition, roles/<role>.md: frontmatter naming its model and effort, which a partition's
`roles` in the teams file may override, and its brief as the body, with its {{TOKENS}} filled. Every token is built here
from the partition's data; a token with no builder, or data a builder needs and the partition lacks, is an error, never
blank text."""
import functools, getpass, hashlib, itertools, json, os, pathlib, re, shlex, subprocess, sys, time
# Run as the command, this module is the crew the modules it imports import, so a refusal raised in plan.py, which a
# tell to a role that runs as its kind writes its ask through, is the Refusal main catches.
if __name__ == "__main__":
    sys.modules.setdefault("crew", sys.modules[__name__])

LIB = pathlib.Path(__file__).resolve().parent
HOME = LIB.parent.parent
HOSTS = pathlib.Path.home() / ".config/swancloud/herdr-hosts.json"
TEAMS = pathlib.Path.home() / ".config/crew/teams.json"
# The version of the teams file crew reads (Decision 2 of the-team-machinery-leaves): 5, its partitions alone, each
# naming the Flume setting of each of its main-level roles (record 0047 move 6), as version 4 did beside its teams.
VERSION = 5
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
# The roles a partition's entry may override: each is a definition in roles/.
MAIN_ROLES = ("design", "planner", "main-ops", "operator", "reviewer")
# A main level's standing roles, each in the session its partition names for it (record 0035): the design agent, the
# planner, ops and the operator, the partition's one door. The reviewer opens beside the planner unless named apart.
MAIN_STANDING = ("design", "planner", "ops", "operator")
# A main level's roles that may run as Flume kinds crew's release carries (record 0047 move 6), each by the name its
# agent takes, <label>-<role>: a partition's `flume` names every one, false while it stands.
KIND_ROLES = ("design", "planner", "reviewer", "ops", "operator")
# What tells whether an agent waits on a question crew's own hook saw it open: piped to the agent's host, whose crew may be older.
QUESTIONS = (LIB / "questions.py").read_text()
# What reads whether an agent's session received a prompt crew sent: piped to the agent's host the same way.
TRANSCRIPT = (LIB / "transcript.py").read_text()
# A prompt taken or sent again (teams.15), in seconds: how long an agent is given to be ready for input before a
# sending, a stage's fresh agent once it has started; how long crew reads on in the transcript of an agent that went to
# work with no record of the prompt; and the pause after a ctrl+c, so that a press on an input already empty, which
# arms Claude's "press again to exit", lapses before the prompt is sent again.
READY_WAIT = 60
WORKING_GRACE = 60
CLEARED = 2


class Refusal(Exception):
    """Data that is missing or inconsistent: crew says what and stops, never guesses."""


def fail(msg):
    raise Refusal(msg)


class Stopped(Exception):
    """A command of crew's that has said, and recorded, why it stops: it ends with code and says nothing more."""

    def __init__(self, code=1):
        super().__init__(code)
        self.code = code


def need(entry, what, field, kind=None):
    if field not in entry or entry[field] in (None, "", []):
        fail(f"{what} in {TEAMS} has no '{field}'")
    if kind and not isinstance(entry[field], kind):
        fail(f"{what} in {TEAMS}: '{field}' must be a {kind.__name__}, not {json.dumps(entry[field])}")
    return entry[field]


def read_hosts():
    """swancloud's generated list of herdr hosts, which owns every ssh name, session and session's repos."""
    if not HOSTS.exists():
        fail(f"{HOSTS} is missing; swancloud's home-manager writes it")
    return json.loads(HOSTS.read_text())["hosts"]


def session_of(hosts, what, machine, session):
    host = hosts.get(machine) or fail(f"{what} runs on {machine}, which {HOSTS} does not list. hosts: " + " ".join(hosts))
    if session not in host["sessions"]:
        fail(f"{what} uses herdr session {session}, which {HOSTS} does not list on {machine}. sessions: " + " ".join(host["sessions"]))
    return host, host["sessions"][session]


def repo_in(sess, what, machine, session, name):
    """A repo named as `name` or `owner/name`, found in the repos the session's space keeps."""
    kept = sess.get("repos") or []
    found = [r for r in kept if r == name or r.split("/")[-1] == name]
    if not found:
        fail(f"{what}: the space of {machine}'s session {session} does not keep {name}. it keeps: " + (" ".join(kept) or "nothing"))
    if len(found) > 1:
        fail(f"{what}: {name} is ambiguous in the space of {machine}'s session {session}: " + " ".join(found))
    return found[0]


def checkout(sess, repo):
    """A repo's main checkout in a session's folder: <dir>/<name>/main."""
    return f"{sess['dir']}/{repo.split('/')[-1]}/main"


def roles_of(entry, what):
    """A partition's role overrides: a main-level role's model, effort or the session it runs in (record 0035), checked
    by load against the hosts file."""
    roles = entry.get("roles") or {}
    if not isinstance(roles, dict):
        fail(f"{what} in {TEAMS}: 'roles' must map a role to its model, effort or session")
    for role, o in roles.items():
        if role not in MAIN_ROLES:
            fail(f"{what} in {TEAMS} overrides role '{role}', which it has no definition for. roles: " + " ".join(MAIN_ROLES))
        if not isinstance(o, dict) or not o or set(o) - {"model", "effort", "session"}:
            fail(f"{what} in {TEAMS}: roles.{role} sets only 'model', 'effort' or 'session', not {json.dumps(o)}")
        if "session" in o and (not isinstance(o["session"], str) or not o["session"]):
            fail(f"{what} in {TEAMS}: roles.{role}.session must name a session of the main level's machine")
        if "effort" in o and o["effort"] not in EFFORTS:
            fail(f"{what} in {TEAMS}: roles.{role}.effort is '{o['effort']}', which is no effort level. levels: " + " ".join(EFFORTS))
        if "model" in o and (not isinstance(o["model"], str) or not o["model"]):
            fail(f"{what} in {TEAMS}: roles.{role}.model must name a model")
    return roles


def role_settings(entry, what):
    """A partition's `flume`, the Flume setting of each of its main-level roles (record 0047 move 6): every role of
    KIND_ROLES named, and no other, each False while it stands or the name of the Flume stream its runs run in on the
    main level's host."""
    fix = f"regenerate {TEAMS} from the machine's configuration (swancloud's lib/crew-teams.nix)"
    "flume" in entry or fail(f"{what} in {TEAMS} has no 'flume', which names each of its roles, " + ", ".join(KIND_ROLES)
                             + f", false or the name of a Flume stream its host declares: {fix}")
    flume = entry["flume"]
    isinstance(flume, dict) or fail(f"{what} in {TEAMS}: 'flume' names each of its roles, not {json.dumps(flume)}: {fix}")
    for role in flume:
        role in KIND_ROLES or fail(f"{what} in {TEAMS}: 'flume' names {role}, which crew has no kind for. roles: "
                                   + " ".join(KIND_ROLES) + f": {fix}")
    for role in KIND_ROLES:
        role in flume or fail(f"{what} in {TEAMS}: 'flume' leaves out {role}: {fix}")
        s = flume[role]
        s is False or isinstance(s, str) and NAME.match(s) or fail(
            f"{what} in {TEAMS}: flume.{role} is false, or the name of a Flume stream its host declares, not {json.dumps(s)}: {fix}")
    return dict(flume)


@functools.lru_cache(maxsize=None)
def load():
    """The partitions, written by the machine's own configuration (swancloud's lib/crew-teams.nix), never by crew: the
    file at version 5 (Decision 2 of the-team-machinery-leaves), its partitions alone, each with its main level and its
    `flume`, the Flume setting of each of its main-level roles (record 0047 move 6), False while the role stands or the
    stream its runs run in on the main level's host, every role of KIND_ROLES and no other. A file at any other
    version, one that still lists teams among them, was written for a crew that runs them and is refused, as is a
    `teams` list in a version-5 file, which holds none (code.5). Every entry is checked here, against the hosts file,
    before any is used, once a process: a later call is answered with the same fleet."""
    if not TEAMS.exists():
        fail(f"{TEAMS} is missing; the machine's configuration writes it")
    data = json.loads(TEAMS.read_text())
    version = data.get("version")
    if type(version) is not int or version != VERSION:
        fail(f"{TEAMS} is version {json.dumps(version)}, and crew reads only version {VERSION}. "
             f"It must be regenerated by the machine's configuration (swancloud's lib/crew-teams.nix); crew has done nothing.")
    "teams" not in data or fail(f"{TEAMS} lists teams, which version {VERSION} has no place for: crew runs no team. It must be "
                                f"regenerated by the machine's configuration (swancloud's lib/crew-teams.nix); crew has done nothing.")
    hosts = read_hosts()
    parts = {}
    for p in data.get("partitions") or fail(f"{TEAMS} lists no partitions"):
        label = need(p, "a partition", "label", str)
        what = f"partition {label}"
        NAME.match(label) or fail(f"{what}: a label is lowercase words with dashes")
        label not in parts or fail(f"{TEAMS} lists partition {label} twice")
        name, machine, session = (need(p, what, f, str) for f in ("partition", "machine", "session"))
        blueprints = need(p, what, "blueprints", list)
        for b in blueprints:
            isinstance(b, str) and re.match(r"^[^/\s]+/[^/\s]+$", b) or fail(f"{what}: a blueprints repo is GitHub owner/name, not {json.dumps(b)}")
        # Where the flywheel's plan, moves and run record live: a branch <label>/main of this repository. Never a
        # default: a file without it predates state repositories and is regenerated, not guessed at.
        p.get("state") not in (None, "") or fail(
            f"{what} in {TEAMS} names no state repository ('state'): regenerate {TEAMS} from the machine's configuration "
            f"(swancloud's lib/crew-teams.nix), which gives every partition one")
        isinstance(p["state"], str) and re.match(r"^[^/\s]+/[^/\s]+$", p["state"]) or fail(
            f"{what}: 'state' is its state repository as GitHub owner/name, not {json.dumps(p['state'])}")
        # The partition's batch setting: a batch of its constructed changes is due every `every` of them or every
        # `hours` hours (briefs.12). Never a default: swancloud's lib/crew-teams.nix writes it for every partition.
        r = p.get("review")
        isinstance(r, dict) and "every" in r and "hours" in r or fail(
            f"{what} in {TEAMS} has no batch setting ('review', with 'every' and 'hours'): regenerate {TEAMS} from the "
            f"machine's configuration (swancloud's lib/crew-teams.nix), which gives every partition one")
        isinstance(r["every"], int) and not isinstance(r["every"], bool) and r["every"] > 0 or fail(
            f"{what}: 'review.every' is how many changes make a batch, a whole number of at least 1, not {json.dumps(r['every'])}")
        isinstance(r["hours"], (int, float)) and not isinstance(r["hours"], bool) and r["hours"] > 0 or fail(
            f"{what}: 'review.hours' is how many hours make a batch due, a number above 0, not {json.dumps(r['hours'])}")
        host, sess = session_of(hosts, f"{what}'s main level", machine, session)
        if sess.get("partition") != name:
            fail(f"{what}'s main level runs in {machine}'s session {session}, which is in partition {sess.get('partition')}, not {name}")
        repo_in(sess, f"{what}'s main level", machine, session, blueprints[0])
        roles = roles_of(p, what)
        for defn, o in sorted(roles.items()):
            if "session" in o:
                _, rs = session_of(hosts, f"{what}'s {defn}", machine, o["session"])
                rs.get("partition") == name or fail(f"{what}'s {defn} runs in {machine}'s session {o['session']}, which is in "
                                                     f"partition {rs.get('partition')}, not {name}")
        parts[label] = dict(p, label=label, partition=name, ssh=host["ssh"], dir=sess["dir"], checkout=checkout(sess, blueprints[0]),
                            roles=roles, flume=role_settings(p, what))
        parts[label]["sessions"] = {r: role_session(parts[label], r) for r in MAIN_STANDING + ("reviewer",)}
    return {"hosts": hosts, "partitions": parts}


def partition_of(fleet, label):
    return fleet["partitions"].get(label) or fail(f"no partition '{label}'. partitions: " + " ".join(fleet["partitions"]))


def role_stream(fleet, label, role):
    """The Flume stream a partition's main-level role runs in as its kind (record 0047 move 6), or False while it
    stands, as the partition's `flume` names it."""
    role in KIND_ROLES or fail(f"{role} is no main-level role that runs as a kind. roles: " + " ".join(KIND_ROLES))
    return partition_of(fleet, label)["flume"][role]


def kind_role_of(fleet, name):
    """The partition and role an agent name is, (label, role), where the name is <label>-<role> and its partition
    runs that role as its kind; None for any other name, a role that stands among them."""
    for label, p in fleet["partitions"].items():
        for role in KIND_ROLES:
            if name == f"{label}-{role}" and p["flume"][role] is not False:
                return label, role
    return None


# The place a role's run is, as its role record names it: <Kind>--<Name>, crew-<role>--<label>.
RUN_PLACE = re.compile(r"crew-([a-z]+)--([a-z0-9][a-z0-9-]*)")


def run_of(fleet, place):
    """The role's run a Flume place is (record 0047 move 6), (label, role), from its path alone: its folder is
    crew-<role>--<label>, the place the role record names, and its partition runs that role as its kind. None for any
    other place, a change's or a fix's among them, and for one so named whose role stands."""
    m = RUN_PLACE.fullmatch(pathlib.PurePath(place or "").name)
    if not m or m[2] not in fleet["partitions"] or m[1] not in KIND_ROLES:
        return None
    return (m[2], m[1]) if fleet["partitions"][m[2]]["flume"][m[1]] is not False else None


def run_here(fleet=None):
    """The role's run this command runs in, (label, role), read from FLUME_PLACE, the place Flume started it in; None
    elsewhere. The teams file is read only for a place named as a run's."""
    place = os.environ.get("FLUME_PLACE")
    if not place or not RUN_PLACE.fullmatch(pathlib.PurePath(place).name):
        return None
    return run_of(fleet or load(), place)


def caller(fleet=None):
    """The agent a crew command runs as: CREW_AGENT, which crew gives each agent it starts, else the role's run its
    place is, named as the role, <label>-<role> (run_here); None for the user."""
    name = os.environ.get("CREW_AGENT")
    if name:
        return name
    run = run_here(fleet)
    return f"{run[0]}-{run[1]}" if run else None


def caller_label(fleet=None):
    """The partition a crew command runs as: CREW_LABEL, which crew gives each agent it starts, else the label of the
    role's run its place is (run_here); None for none."""
    label = os.environ.get("CREW_LABEL")
    if label:
        return label
    run = run_here(fleet)
    return run[0] if run else None


def run_exports(run):
    """What plugin/bin/crew sets for a role's run before it runs or forwards any command (code.3): its name and
    partition as a standing agent's CREW_AGENT and CREW_LABEL, and no Claude session, which a run has none of crew's
    to read, as shell assignments quoted (teams.9); nothing for a place that is no run."""
    if not run:
        return ""
    return "export " + " ".join(f"{k}={shlex.quote(v)}" for k, v in (("CREW_AGENT", f"{run[0]}-{run[1]}"), ("CREW_LABEL", run[0]), ("CREW_SESSION", "")))


def role_session(p, role):
    """The session a main-level role runs in: the one its partition's `roles` names for its definition, else the
    main level's; the reviewer, named none, opens beside the planner (record 0035)."""
    o = (p.get("roles") or {}).get("main-ops" if role == "ops" else role) or {}
    if "session" in o:
        return o["session"]
    return role_session(p, "planner") if role == "reviewer" else p["session"]


@functools.lru_cache(maxsize=None)
def this_host():
    """The host crew runs on, as `hostname -s` names it: the same name the hosts file and the teams file use. Read once
    a process."""
    return subprocess.run(["hostname", "-s"], capture_output=True, text=True, check=True).stdout.strip()


def on_machine(fleet, host, argv, input=None):
    """Run a command on a host: here when it is this host, else over ssh, never prompting. A host that does not
    answer exits 255, as ssh does. herdr here goes through its session's Herdr, so what it does is read again."""
    if host == this_host():
        if argv[:2] == ["herdr", "--session"] and input is None:
            return herdr_in(argv[2]).run(*argv[3:])
        return subprocess.run(argv, input=input, capture_output=True, text=True)
    return subprocess.run(["ssh", "-o", "BatchMode=yes", fleet["hosts"][host]["ssh"], shlex.join(argv)],
                          input=input, capture_output=True, text=True)


def place_of_agent(fleet, name):
    """The host and herdr session an agent crew starts runs in, from its name alone: a main level's standing role or
    its reviewer."""
    for p in fleet["partitions"].values():
        l = p["label"]
        for role in MAIN_STANDING + ("reviewer",):
            if name == f"{l}-{role}":
                return p["machine"], role_session(p, role)
    fail(f"no agent {name}: crew starts none by that name")


def label_of_agent(fleet, name):
    """The partition an agent crew starts works for, from its name alone."""
    for l in fleet["partitions"]:
        if name in (f"{l}-{r}" for r in MAIN_STANDING + ("reviewer",)):
            return l
    return None


def send_door(fleet, name, caller):
    """Where crew send delivers (briefs.10, record 0035): a partition named by its label, as (label, its operator). Any
    other name, a team's from before teams left among them, is refused naming the partitions, never placed by a guess
    (read.1), and so is the operator sending to its own partition, which it carries on with crew tell."""
    name in fleet["partitions"] or fail(f"crew send sends to a partition by its label, not '{name}': partitions "
                                        f"{' '.join(sorted(fleet['partitions'])) or 'none'}")
    door = f"{name}-operator"
    if caller == door:
        fail(f"you are {name}'s door: carry it on with `crew tell <agent>`")
    return name, door


# Whom a word from the board goes to, by the role its item's kind names (record 0038 §3, board-page "A word goes to the
# agent its item's kind names"): a bolt's, a unit's or chore's, a fix's, a proposal's or a batch's planner; a signal's or
# a record's design agent; a landing's, a deploy's or an operation's main-level ops; and any other kind's, the
# partition's operator.
ROLE_OF = {"bolt": "planner", "unit": "planner", "fix": "planner", "proposal": "planner", "batch": "planner",
           "signal": "design", "record": "design", "landing": "ops", "deploy": "ops", "operation": "ops"}


def tell(fleet, name, text, record=True, sender=None, taken=False, what="its prompt", again="", ask="tell", reading=None):
    """Send an agent a prompt wherever it runs, marked as crew's: `[crew tell from <sender>]` for what crew tell
    carries for someone, `[crew]` for crew's own greetings and notices, so the recipient, and crew reading its
    transcript, never take it for the user's typing. A tell reaches its agent as a prompt or not at all (teams.11):
    an agent that is not up, one waiting on a question in its pane, and one crew can't read that of is reported, with
    nothing typed, and the tell fails. With taken, the text is taken or sent again (send_taken), and a sending not
    taken fails the tell, saying so of what was sent, with again, what to do once it is ready, when it was never
    taken. A tell is in the run record of the recipient's partition, with its length and never its text.

    To a role its partition runs as its kind (record 0047 move 6), with no standing agent of it up, the tell is an ask
    of the role instead, of the kind ask, from the sender or crew (tell_ask), and does not fail for the agent not being
    up; a standing agent of it still up is told as today, and one crew can't read is refused (asks_instead). reading,
    what waits_on_question read of the agent, where the caller already read it."""
    host, session = place_of_agent(fleet, name)
    status, asking, unread = reading or waits_on_question(fleet, name)
    run = kind_role_of(fleet, name)
    if asks_instead(run, status, unread):
        return tell_ask(fleet, run, text, sender or "crew", ask)
    why = tell_refusal(name, host, status, asking, unread, run)
    if why:
        print(why, file=sys.stderr)
        return False
    mark = f"[crew tell from {sender}]" if sender else "[crew]"
    if taken:
        how, why = send_taken(fleet, name, f"{mark} {text}")
        if how != "taken":
            print(untaken_said(name, what, how, why, again), file=sys.stderr)
        sent = how == "taken"
    else:
        r = on_machine(fleet, host, ["herdr", "--session", session, "agent", "prompt", name, f"{mark} {text}"])
        if r.returncode:
            print(typed_refusal(name, host, r.stderr), file=sys.stderr)
        sent = r.returncode == 0
    if sent and record:
        import record as rec  # record imports this module
        rec.emit(label_of_agent(fleet, name), "tell", on=[f"agent/{name}"], why=f"tell {name}", Chars=len(text))
    return sent


def asks_instead(run, status, unread):
    """Whether a tell is an ask of the role rather than a prompt (role-runs "A tell finds a standing agent of the role
    first"): the agent is a role its partition runs as its kind, run, and crew read that no standing agent of it is up.
    One still up is told as today; one crew could not read is refused (tell_refusal), never asked on a guess (read.1)."""
    return bool(run) and status is None and not unread


def tell_ask(fleet, run, text, frm, what="tell"):
    """A tell to a role that runs as its kind, run (label, role), written as an ask of the role on its partition's
    flywheel branch (plan.ask_write), from frm, carrying the text, typed into no pane; `asked <label>-<role>` once it is
    written. Whether it was written: an ask crew could not write is said, as a tell not typed is."""
    import plan  # plan imports this module
    name = f"{run[0]}-{run[1]}"
    try:
        plan.ask_write(fleet, run[0], run[1], what, frm, words=text)
    except Refusal as e:
        print(f"could not ask {name}: {e}; nothing was sent", file=sys.stderr)
        return False
    print(f"asked {name}")
    return True


def send(fleet, name, text):
    """Send the text to the door of the partition named by its label (briefs.10): a tell to its operator, marked with
    who sent it and `(sent to <name>)` before the text, so the operator knows whom it is for. A send is one `send` entry in
    the receiving partition's record, with its length and never its text, and no tell entry; one that typed nothing
    records nothing. To an operator that runs as its kind, with no standing operator up, the send is a `send` ask of it
    carrying `(sent to <name>)` and the text, its entry the ask's (tell)."""
    import record as rec  # record imports this module
    label, door = send_door(fleet, name, caller(fleet))
    run = kind_role_of(fleet, door)
    reading = waits_on_question(fleet, door) if run else None
    asked = bool(reading) and asks_instead(run, reading[0], reading[2])
    sent = tell(fleet, door, f"(sent to {name}) {text}", record=False, sender=rec.who(), ask="send", reading=reading)
    if sent and not asked:
        rec.emit(label, "send", on=[f"agent/{door}"], why=f"send {name}", Chars=len(text))
    return sent


# The kinds of item a word from the board is on: a dock's, and a batch, a record and the partition itself.
KINDS = ("signal", "proposal", "bolt", "unit", "fix", "landing", "deploy", "operation", "subscription", "batch", "record",
         "partition")
BOARD_KEY = re.compile(r"^([a-z]+):([A-Za-z0-9._:/+-]{1,200})$")
WORD_MOST = 1000


def board_word(fleet, raw):
    """A word posted from a dock, as the board's listener pipes it (record 0038 §4): one JSON object holding the
    partition, the item's key, the agent and the text, each a string, the agent the one its item's kind goes to in that
    partition (ROLE_OF); the text one line of at most WORD_MOST characters. Returns the agent
    and the text to tell it, `(on <kind> <name>) <text>`; anything else is refused (read.2)."""
    try:
        w = json.loads(raw)
    except ValueError:
        w = None
    if not isinstance(w, dict) or not all(isinstance(w.get(f), str) for f in ("label", "key", "to", "text")):
        fail("a word from the board is one JSON object holding label, key, to and text")
    label, key, to, text = w["label"], w["key"], w["to"], w["text"]
    partition_of(fleet, label)
    m = BOARD_KEY.match(key) or fail(f"a word from the board is on an item's key, <kind>:<name>, not '{key}'")
    kind, name = m.groups()
    kind in KINDS or fail(f"a word from the board is on no item of the kind '{kind}': kinds " + " ".join(KINDS))
    role = ROLE_OF.get(kind, "operator")
    a = "an" if kind[0] in "aeio" else "a"
    to == f"{label}-{role}" or fail(f"a word on {a} {kind} goes to {label}-{role}, not {to}")
    if "\n" in text or "\r" in text:
        fail("a word from the board is one line")
    text.strip() or fail("a word from the board holds no text")
    len(text) <= WORD_MOST or fail(f"a word from the board is at most {WORD_MOST} characters, not {len(text)}")
    return to, f"(on {kind} {name}) {text}"


def board_tell(fleet, raw):
    """crew tell --board: the word checked (board_word) and told its agent as the user's from the board,
    `[crew tell from <user>@board]`, the user being whom the listener runs as; `sent to <agent>` once it is typed, and
    tell's own words on standard error when it is not."""
    to, text = board_word(fleet, raw)
    sent = tell(fleet, to, text, sender=f"{getpass.getuser()}@board")
    if sent:
        print(f"sent to {to}")
    return sent


def tell_refusal(name, host, status, asking, unread, run=None):
    """Why a tell types nothing (teams.11), from what crew read of the agent: what it could not read, the agent not
    up, or waiting on a question in its pane; None when the tell may be typed. For a role that runs as its kind, run,
    what crew could not read is whether a standing agent of it is up, so it neither types nor asks."""
    if unread and run:
        return (f"could not tell {name} on {host}: {unread}, so crew can't tell whether a standing agent of it is up or "
                f"its role is to be asked; nothing was sent or asked")
    if unread:
        return f"could not tell {name} on {host}: {unread}, so crew can't tell whether it is waiting on a question; nothing was sent"
    if status is None:
        return f"could not tell {name} on {host}: it is not up"
    return waiting_said(name) if asking else None


def untaken_said(name, what, how, why, again=""):
    """What a tell sent to be taken or sent again says when it was not (teams.15): never taken, with how to send it once
    the agent is ready, or not told whether it was, so nothing more was sent."""
    if how == "never":
        return f"{name} did not take {what}, {why}; nothing is left typed" + (f"; {again}" if again else "")
    return f"crew could not tell whether {name} took {what}: {why}; nothing more was sent"


def typed_refusal(name, host, stderr):
    """What a tell herdr refused to type says: herdr's own check, at the moment of typing, of a question opened since crew
    read the agent, in the same words as crew's; else herdr's words, or that the agent is not up."""
    return waiting_said(name) if herdr_error(stderr) == "agent_blocked" else f"could not tell {name} on {host}: " + (
        (stderr or "").strip() or "it is not up")


def waiting_said(name):
    return f"{name} is waiting on a question in its pane: nothing was sent; tell it again once the question is answered"


def herdr_error(stderr):
    """The code of the error herdr's CLI writes on standard error, {"error": {"code": ..., "message": ...}}, or None."""
    for line in (stderr or "").splitlines():
        try:
            e = json.loads(line)["error"]
        except (ValueError, KeyError, TypeError):
            continue
        if isinstance(e, dict) and isinstance(e.get("code"), str):
            return e["code"]
    return None


def unanswered(host, r):
    """What a failed run on a host says could not be read, or None when the host answered: a host that does not
    answer exits 255, as ssh does."""
    if host == this_host() or r.returncode != 255:
        return None
    return f"{host} did not answer ({((r.stderr or '').strip().splitlines() or ['ssh exited 255'])[-1]})"


def read_agent(fleet, name, fresh=True):
    """An agent crew starts, as herdr answers wherever it runs: (the agent, None), (None, None) when it is not up, or
    (None, what could not be read) when its host does not answer or herdr's answer can't be read. One herdr lists by no
    name is looked for in the pane crew keeps for it there and given its name back (found_again), the host's own crew
    looking when it is another host (crew.py found). On this host, with fresh False, it is answered from its session's
    listing as this command read it (Herdr)."""
    host, session = place_of_agent(fleet, name)
    if host == this_host():
        try:
            a = herdr_in(session).agent(name, fresh)
            return (a, None) if a else found_again(fleet, name, fresh)
        except Refusal as e:
            return None, str(e)
    try:
        found = shlex.join(["python3", f"{crew_at(fleet, host).rsplit('/bin/', 1)[0]}/lib/crew.py", "found", name])
    except Refusal as e:
        return None, str(e)
    r = on_machine(fleet, host, ["sh", "-c", f"{shlex.join(['herdr', '--session', session, 'agent', 'get', name])} || exec {found}"])
    return found_answer(host, r)


def found_answer(host, r):
    """read_agent's reading of an agent on another host, from what ran there, as subprocess.run gives it: herdr's agent
    get, or that host's crew.py found when herdr lists no agent by its name, each answering herdr's
    {"result": {"agent": ...}}, which found answers too, its agent null when it is not up, or found's {"unread": why}.
    A host that does not answer, a found that fails, as one on a host whose crew is older, and an answer crew can't read
    are each a read it names (read.1)."""
    if r.returncode:
        return None, unanswered(host, r) or (f"crew on {host} could not look for it in the pane it keeps for it: "
                                             + ((r.stderr or "").strip().splitlines() or [f"exit {r.returncode}"])[-1])
    try:
        got = json.loads(r.stdout)
    except ValueError:
        got = None
    if isinstance(got, dict) and isinstance(got.get("unread"), str) and got["unread"]:
        return None, got["unread"]
    a = got.get("result", {}).get("agent", False) if isinstance(got, dict) and isinstance(got.get("result"), dict) else False
    return (a, None) if a is None or isinstance(a, dict) else (None, f"herdr's answer on {host} about it can't be read")


def name_back(name, pane, agent, started):
    """Whether crew gives an agent it started its name back in its pane (briefs.17), from the pane crew keeps for it
    ("" when none), the agent herdr lists in that pane (None when none) and the Claude session crew's last start of it
    on this host recorded (start_of; None when none): (True, None) when herdr lists an agent there by no name whose
    session is that one, herdr having dropped its name when another session reported itself in the pane; (False, None)
    when crew keeps no pane for it or herdr lists no agent there, so it is not up; and (False, why) when the pane holds
    an agent crew did not start as it, another agent's or a session crew started for none, which is never given its
    name and is a read crew names (read.1)."""
    if not pane or agent is None:
        return False, None
    if agent.get("name"):
        return False, f"herdr lists no agent named {name}, and its pane {pane} holds {agent['name']}"
    sess = agent.get("agent_session")
    sid = sess.get("value") if isinstance(sess, dict) else None
    if not isinstance(sid, str) or not sid:
        return False, f"herdr lists the agent in its pane {pane} by no name and names no session for it, so crew can't tell it is {name}"
    if sid != started:
        return False, f"herdr lists the agent in its pane {pane} by no name, in session {sid}, which crew did not start as {name}"
    return True, None


def found_again(fleet, name, fresh=True):
    """An agent crew started on this host that herdr lists by no name, found in the pane crew keeps for it and given its
    name back when its session there is the one crew started (name_back): (the agent, None), (None, None) when it is not
    up, or (None, why) when its pane holds an agent crew does not name so, or herdr would not take the name. It is said
    on standard error when given back."""
    held = held_in(fleet, name)
    if not held:
        return None, None
    agents, role = held
    pane = agents.pane(role)
    a = agents.herdr.agent(pane, fresh) if pane else None
    started = start_of(name) if a is not None and not a.get("name") else None
    back, why = name_back(name, pane, a, started and started["session"])
    if not back:
        return None, why
    r = agents.herdr.run("agent", "rename", pane, name)
    if r.returncode:
        return None, f"herdr dropped its name in its pane {pane} and would not take it back: " + (
            (r.stderr or "").strip().splitlines() or [f"exit {r.returncode}"])[-1]
    print(f"herdr had dropped {name}'s name in its pane {pane}, whose session crew started as {name}; crew gave it back", file=sys.stderr)
    return dict(a, name=name), None


def found_here(fleet, name):
    """crew.py found: read_agent of an agent of this host, its dropped name given back (found_again), as one JSON
    object found_answer reads: herdr's {"result": {"agent": ...}}, or {"unread": why}."""
    host, _ = place_of_agent(fleet, name)
    if host != this_host():
        return {"unread": f"{name} runs on {host}, not on {this_host()}, where crew looked for it"}
    a, why = read_agent(fleet, name)
    return {"unread": why} if why else {"result": {"agent": a}}


def agent_get(fleet, name, fresh=True):
    """An agent crew starts, as herdr answers wherever it runs, or None when it is not up."""
    return read_agent(fleet, name, fresh)[0]


def agent_status(fleet, name, fresh=True):
    """An agent crew starts, as herdr sees it wherever it runs: idle, done, working, blocked, or None when it is not up.
    With fresh False, an agent on this host is answered from its session's listing as this command last read it."""
    a = agent_get(fleet, name, fresh)
    return a.get("agent_status") if a else None


def pane_holds(name, pane, item, agent):
    """Whether a standing agent's pane holds an agent, as the rail's sweep reads a question's asker (briefs.11, read.1),
    from the pane crew keeps for it ("" when none), herdr's item for that pane in its pane list and the agent herdr lists
    in it (each None when herdr lists none): (True, None) while herdr lists an agent there, named or not, since herdr
    drops a name when the pane's session changes; (False, None) when herdr lists the pane with no agent in it, the one
    reading that the agent ended; (None, why) when crew keeps no pane for it or herdr lists none by that id."""
    if not pane:
        return None, f"crew keeps no pane for {name}"
    if item is None:
        return None, f"herdr lists no pane {pane}, which crew keeps for {name}"
    return agent is not None, None


def held_in(fleet, name):
    """The Agents an agent crew starts is kept in on its host and its role there, from its name alone: a main level's
    for its roles and its reviewer; None for a name crew starts no agent by."""
    label = label_of_agent(fleet, name)
    if not label:
        return None
    role = name[len(label) + 1:]
    return main_holding(fleet, label, role), role


def holding_of(fleet, name):
    """The Agents a standing agent's role is kept in and that role, from its name alone, a main level's; None for a
    name that is no standing agent's (standing_role)."""
    return held_in(fleet, name) if standing_role(fleet, name) else None


def read_pane_agent(fleet, name):
    """pane_holds for a standing agent on this host, from its pane in crew's panes file and one listing of its
    session's panes and agents (Herdr): an agent on another host, or one crew keeps no pane for, is a read it names,
    never taken for ended (read.1)."""
    try:
        host, _ = place_of_agent(fleet, name)
        if host != this_host():
            return None, f"{name} runs on {host}, whose panes this host does not read"
        held = holding_of(fleet, name)
        if not held:
            return None, f"{name} is no standing agent of crew's, so crew keeps no pane for it"
        agents, role = held
        pane = agents.pane(role)
        return pane_holds(name, pane, agents.herdr.item(pane), agents.herdr.agent(pane))
    except Refusal as e:
        return None, str(e)


# What each herdr command a crew command runs leaves to read again in its session: the agents (`agent list`), the panes
# (`pane list`), both, or neither. A command not named here leaves both.
STALE = {("agent", "list"): "", ("agent", "get"): "", ("agent", "read"): "", ("pane", "list"): "", ("pane", "get"): "",
         ("pane", "read"): "", ("workspace", "list"): "", ("workspace", "get"): "", ("tab", "list"): "", ("tab", "get"): "",
         ("tab", "rename"): "", ("workspace", "create"): "pane", ("tab", "create"): "pane", ("pane", "split"): "pane",
         ("pane", "run"): "agent", ("pane", "send-keys"): "agent", ("agent", "prompt"): "agent", ("agent", "send-keys"): "agent",
         ("agent", "rename"): "agent", ("pane", "process-info"): ""}


class Herdr:
    """herdr's session on this host, as one crew command reads it (read.2): its agents (`agent list`) and its panes
    (`pane list`), each listed once and listed again only after crew acts in the session in a way that can change it
    (STALE), so every agent's status and every pane's life at a moment is answered from one listing, never a call each;
    a poll of one agent, or a tell's reading of it, asks herdr of that agent afresh, and what it answers stands for that
    agent until crew acts again. A session whose server is not running has no agents and no panes; any other listing
    crew can't read is a refusal (read.1). An agent unnamed has no `name`, as herdr lists it."""

    def __init__(self, session):
        self.session, self.listed, self.got = session, {}, {}

    def run(self, *args):
        """herdr in this session, acting or reading: its answer, as subprocess.run gives it."""
        stale = STALE.get(tuple(args[:2]), "agent pane")
        for what in stale.split():
            self.listed.pop(what, None)
        if "agent" in stale:
            self.got.clear()
        return subprocess.run(["herdr", "--session", self.session, *args], capture_output=True, text=True)

    def listing(self, what, fresh=False):
        """herdr's `<what> list` in this session, agent or pane: its items, from this command's listing unless fresh."""
        if fresh or what not in self.listed:
            r = subprocess.run(["herdr", "--session", self.session, what, "list"], capture_output=True, text=True)
            self.listed[what] = listed(what, r.returncode, r.stdout, r.stderr, f"in session {self.session} on {this_host()}")
        return self.listed[what]

    def agent(self, target, fresh=False):
        """The agent in a pane, or by its name: herdr's item for it, or None when there is none. Fresh, it is herdr's
        agent get of that one agent now, as a poll or a tell reads it, any failure taken as no agent; else it is from
        this command's listing."""
        if not target:
            return None
        if fresh:
            r = self.run("agent", "get", target)
            try:
                a = None if r.returncode else json.loads(r.stdout)["result"]["agent"]
            except (ValueError, KeyError, TypeError):
                a = False
            isinstance(a, dict) or a is None or fail(f"herdr's answer on {this_host()} about {target} can't be read")
            self.got[target] = a
            return a
        if "agent" not in self.listed and target in self.got:
            return self.got[target]
        return next((a for a in self.listing("agent") if target in (a.get("pane_id"), a.get("name"))), None)

    def status(self, target, fresh=False):
        """An agent's status, by its pane or name: idle, done, working, blocked, or None when it is not up."""
        s = (self.agent(target, fresh) or {}).get("agent_status")
        return s if isinstance(s, str) and s else None

    def item(self, pane):
        """A pane's item in this command's listing of the session's panes, or None when herdr lists none."""
        return next((p for p in self.listing("pane") if p.get("pane_id") == pane), None) if pane else None

    def live(self, pane):
        """Whether the pane is there."""
        return self.item(pane) is not None

    def process_info(self, pane):
        """What runs in a pane's terminal, as herdr's pane process-info answers: its process_info object, or None when
        herdr's answer can't be read (tab_holds reads it)."""
        r = self.run("pane", "process-info", "--pane", pane)
        try:
            return json.loads(r.stdout)["result"]["process_info"] if r.returncode == 0 else None
        except (ValueError, KeyError, TypeError):
            return None


def tab_holds(info, words):
    """What a tab's pane holds of the command crew runs in it, from herdr's process-info of the pane (info) and the
    words that end the command's argv: ("running", None) when a process in the pane's foreground runs it; ("shell",
    None) when the pane's shell alone is in its foreground, as herdr brings a pane back after a restart, or as the
    command left it when it ended; ("other", what runs there) for anything else, which crew leaves (read.4); and
    (None, why) when herdr's answer can't be read (read.1). Read against herdr 0.9.3 on mac-studio on 2026-10-18
    (read.2): {"shell_pid": n, "foreground_process_group_id": n, "foreground_processes": [{"pid": n, "argv": [...]}]},
    the group the shell's own pid while it waits at its prompt."""
    shell, group, procs = ((info.get("shell_pid"), info.get("foreground_process_group_id"), info.get("foreground_processes"))
                           if isinstance(info, dict) else (None, None, None))
    if not isinstance(shell, int) or not isinstance(group, int) or not isinstance(procs, list):
        return None, "herdr's process-info for it can't be read"
    argvs = [p["argv"] for p in procs if isinstance(p, dict) and isinstance(p.get("argv"), list) and all(isinstance(a, str) for a in p["argv"])]
    if any(a[-len(words):] == words for a in argvs):
        return "running", None
    if group == shell:
        return "shell", None
    return "other", shlex.join(argvs[0]) if argvs else f"process group {group}"


def dead_said(scope, role, item, status):
    """What crew says of a role's pane that herdr lists but holds no terminal for, or None when crew can drive it or
    herdr lists none (teams.2): item is the pane's in herdr's pane list, and status its agent's. herdr 0.9.3 lists a
    pane it could not bring back when its server started, its saved folder gone, with a restore_error, and answers its
    read, run, send-keys and process-info with pane_not_found, so nothing typed there runs, while pane close closes it
    (read.2: read on mac-studio on 2026-10-19 in a scratch session, and in swancloud's, where crw-3's w10:p6 stood in a
    removed worktree). A pane an agent holds is never dead (read.4), nor one whose folder went while herdr ran, whose
    shell takes what crew types."""
    err = unrestored(item)
    if status or not err:
        return None
    cwd = item.get("cwd")
    where = f" in {cwd}" if isinstance(cwd, str) and cwd else ""
    return f"{scope}'s {role} pane {item['pane_id']} is dead: herdr could not bring it back{where} ({err})"


def unrestored(item):
    """herdr's words for a pane it lists but could not bring back when its server started (dead_said), from the pane's
    item in its pane list: its restore_error, or None when it has none or none crew can read (read.2)."""
    err = item.get("restore_error") if isinstance(item, dict) else None
    return err.strip() if isinstance(err, str) and err.strip() else None


def revived(item, status):
    """How crew revive brings back a standing role after a restart, from its pane's item in herdr's pane list (None
    when herdr lists none) and its agent's status (teams.2, teams.6): "dead" when herdr brought the pane back with no
    terminal behind it (unrestored), to be closed and opened again in its layout before its agent is picked up there;
    "empty" when herdr brought it back with no agent in it, which herdr may still be resuming; None when an agent holds
    it or there is no pane to bring back."""
    if status or item is None:
        return None
    return "dead" if unrestored(item) else "empty"


def opens_at(beside, workspace):
    """Where a role's pane opens when it is not there: split from beside, the open pane it shares its tab with, as
    ("split", beside); else as a tab of its workspace while that stands, ("tab", workspace); else as the first tab of a
    new workspace, ("workspace", None). beside and workspace are "" when not open or not standing."""
    return ("split", beside) if beside else ("tab", workspace) if workspace else ("workspace", None)


def listed(what, code, out, err, where):
    """The items of herdr's `agent list` or `pane list` (what: agent or pane), from its exit, standard output and
    standard error (read.2): {"result": {"<what>s": [...]}} as herdr 0.9.3 answers, each item a JSON object; none when
    the session's server is not running, as herdr says with the error code server_not_running. Any other failure, or
    an answer crew can't read, is refused, saying where (read.1)."""
    if code:
        herdr_error(err) == "server_not_running" or fail(
            f"herdr's {what} list {where} failed: " + ((err or "").strip().splitlines() or [f"exit {code}"])[-1])
        return []
    try:
        items = json.loads(out)["result"][f"{what}s"]
    except (ValueError, KeyError, TypeError):
        items = None
    isinstance(items, list) or fail(f"herdr's {what} list {where} can't be read")
    return [i for i in items if isinstance(i, dict)]


def herdr_made(group, cmd, code, out, err, where, ids=()):
    """What herdr's act (group and cmd, as `workspace create`) made, from its exit, standard output and standard error:
    its result, each of ids (a path of keys into it) a string that is not empty. An answer crew can't read, or one whose
    id is missing or empty, is refused in herdr's words, saying where (read.1, read.2), so crew keeps nothing of it and
    acts on no id it lacks."""
    try:
        result = json.loads(out)["result"]
        ok = all(isinstance(v, str) and v for v in (functools.reduce(lambda d, k: d[k], path, result) for path in ids))
    except (ValueError, KeyError, TypeError):
        ok = False
    ok or fail(f"herdr could not {cmd} a {group} {where}: " + ((err or "").strip().splitlines() or [f"exit {code}"])[-1])
    return result


_SESSIONS = {}


def herdr_in(session):
    """This command's Herdr of a session on this host."""
    return _SESSIONS.setdefault(session, Herdr(session))


def herdr_fresh():
    """herdr's sessions listed again at their next read: a long-lived process's, the host's follower at its tick."""
    _SESSIONS.clear()


def waits_on_question(fleet, name):
    """Whether an agent crew starts waits on a question in its pane, as a tell and a greeting read it: (herdr's status
    of it, None when it is not up; whether it waits; what crew could not read to know, or None). It waits when herdr
    reports it blocked, or when the mark crew's hook left as it opened a question or a plan for the user
    (hooks/questions) is still open in its session, read by questions.py on its host. Either is enough: herdr reads
    the dialog from the screen alone, and on 2026-10-07 took a tell into one it did not see. A host with no mark, such
    as an agent started before the hook, reads as no question open, and herdr's reading alone guards it (the
    a-tell-never-lands-in-a-question design, decision 5, departing from read.1). So does an agent whose session neither
    herdr nor crew's record of its pane names, which goes on rather than refusing, since every message between agents
    is a tell (roles.4) and a refusal would leave it unreachable (the crew-tell-reaches-a-pane-with-no-recorded-session
    design, decision 3, departing from read.1)."""
    status, asking, _, unread = agent_reading(fleet, name)
    return status, asking, unread


def agent_reading(fleet, name):
    """What waits_on_question reads of an agent, with its session: (herdr's status of it, None when it is not up;
    whether it waits on a question in its pane; its Claude session, or None; what crew could not read, or None). Its
    session is the one herdr names for its pane, or, when herdr names none, the newest crew's session-start hook
    recorded of the agent starting in that herdr session and pane, read by questions.py --pane on its host; whether it
    waits is read from crew's own mark of that session. With neither session it reads as waiting on nothing herdr does
    not report, and herdr's reading alone guards it (waits_on_question)."""
    host, session = place_of_agent(fleet, name)
    a, unread = read_agent(fleet, name)
    if a is None:
        return None, False, None, unread
    status = a.get("agent_status")
    sess = a.get("agent_session")
    sid = sess.get("value") if isinstance(sess, dict) else None
    sid = sid if isinstance(sid, str) and sid else None
    if status == "blocked":
        return status, True, sid, None
    if not sid:
        pane = a.get("pane_id")
        if not isinstance(pane, str) or not pane:
            return status, False, None, None
        got = piped(fleet, host, QUESTIONS, "questions", "--pane", session, pane, name)
        if isinstance(got, str):
            return status, False, None, got
        sid = got.get("session")
        if sid is None:
            return status, False, None, None
        if not isinstance(sid, str) or not sid:
            return status, False, None, f"crew's reading of its questions on {host} gave no answer crew reads"
    else:
        got = piped(fleet, host, QUESTIONS, "questions", sid)
        if isinstance(got, str):
            return status, False, sid, got
    if got.get("question") not in (None, "open", "answered"):
        return status, False, sid, f"crew's reading of its questions on {host} gave no answer crew reads"
    return status, got["question"] == "open", sid, None


def piped(fleet, host, script, what, *args):
    """A reading crew pipes to python3 on a host, questions.py or transcript.py: its answer, one JSON object, or what
    could not be read, its own {"unread": ...} among it. On this host it is read in this process, the same reading."""
    if host == this_host():
        try:
            got = here_reading(what, *args)
        except Exception as e:
            return f"crew's reading of its {what} on {host} failed ({e})"
    else:
        r = on_machine(fleet, host, ["python3", "-", *args], input=script)
        if r.returncode:
            return unanswered(host, r) or (
                f"crew's reading of its {what} on {host} failed ({((r.stderr or '').strip().splitlines() or [f'exit {r.returncode}'])[-1]})")
        try:
            got = json.loads(r.stdout)
        except ValueError:
            got = None
    if isinstance(got, dict) and isinstance(got.get("unread"), str):
        return got["unread"]
    return got if isinstance(got, dict) else f"crew's reading of its {what} on {host} gave no answer crew reads"


def here_reading(what, *args):
    """What questions.py or transcript.py answers on this host, as its own command line would print it, read in this
    process: questions <session> | --pane <herdr session> <pane> <agent>, or transcript end <session> | received
    <session> <offset> <text>."""
    if what == "questions":
        import questions
        return questions.answer(list(args))
    import transcript
    return transcript.end(args[1]) if args[0] == "end" else transcript.received(args[1], int(args[2]), args[3])


@functools.lru_cache(maxsize=None)
def taken_within():
    """How long crew reads an agent's transcript for a prompt it sent before taking it as not taken: 15 seconds, or
    CREW_TAKEN_WITHIN's whole seconds, which only crew's tests set (tests.8)."""
    v = os.environ.get("CREW_TAKEN_WITHIN")
    if v is None:
        return 15
    v.isdigit() and int(v) > 0 or fail(f"CREW_TAKEN_WITHIN is a whole number of seconds above 0, not {json.dumps(v)}")
    return int(v)


class Pane:
    """An agent's pane as the taken-or-sent-again exchange reads it and types into it (teams.15): herdr on the agent's
    host, and its session's transcript there, read by transcript.py piped to the host; the clock it waits by. A logic
    test hands send_taken a pane of its own."""

    def __init__(self, fleet, name):
        self.fleet, self.name = fleet, name
        self.host, self.session = place_of_agent(fleet, name)

    def reading(self):
        return agent_reading(self.fleet, self.name)

    def agent(self):
        return read_agent(self.fleet, self.name)

    def end(self, sid):
        return piped(self.fleet, self.host, TRANSCRIPT, "transcript", "end", sid)

    def received(self, sid, size, text):
        return piped(self.fleet, self.host, TRANSCRIPT, "transcript", "received", sid, str(size), text)

    def herdr(self, *args):
        return on_machine(self.fleet, self.host, ["herdr", "--session", self.session, "agent", *args])

    def unanswered(self, r):
        return unanswered(self.host, r)

    def now(self):
        return time.monotonic()

    def sleep(self, seconds):
        time.sleep(seconds)


def send_taken(fleet, name, text, ready_wait=READY_WAIT, pane=None):
    """Send an agent a prompt so that it is taken or sent again (teams.15). crew waits until the agent is ready for
    input (ready_for), notes where its session's transcript ends, sends the text, and reads the transcript for it
    (read_back). Not taken while the agent sits idle or done, its input is cleared with one ctrl+c, which Claude Code
    documents as clearing the prompt input when nothing runs, and it is sent once more, from the wait; the second not
    taken either, the input is cleared again. Returns ("taken", how many sendings), ("never", why) when the agent never
    took it, or was never ready and nothing was typed, or ("unread", what) when crew could not tell whether it took
    it: then nothing more is sent and nothing is pressed (read.1). herdr's own --wait gate is not used: it reads
    whether the agent got busy, not whether the prompt landed, and herdr warns against sending again on it."""
    pane = pane or Pane(fleet, name)
    taken_within()  # a limit crew can't read refuses before anything is typed
    for sending in (1, 2):
        sid, not_ready = ready_for(pane, ready_wait)
        if not_ready:
            return not_ready
        end = pane.end(sid)
        if isinstance(end, str):
            return "unread", end
        if not isinstance(end.get("size"), int):
            return "unread", f"crew's reading of its transcript on {pane.host} gave no answer crew reads"
        r = pane.herdr("prompt", name, text)
        if r.returncode:
            # herdr's own check, at the moment of typing, refuses a question opened since crew read the agent, typing nothing.
            if herdr_error(r.stderr) == "agent_blocked":
                return "never", "as it was waiting on a question in its pane"
            return "unread", pane.unanswered(r) or f"herdr on {pane.host} did not send it ({((r.stderr or '').strip().splitlines() or [f'exit {r.returncode}'])[-1]})"
        how, why = read_back(pane, sid, end["size"], text)
        if how != "not taken":
            return (how, sending) if how == "taken" else (how, why)
        r = pane.herdr("send-keys", name, "ctrl+c")
        if r.returncode:
            return "unread", pane.unanswered(r) or f"crew could not clear its input on {pane.host}, so it may still hold the prompt"
        if sending == 1:
            pane.sleep(CLEARED)
    return "never", "sent twice"


def ready_for(pane, wait):
    """Wait, up to wait seconds, until the pane's agent is ready for input: herdr reports it idle or done, it waits on no
    question in its pane, and crew finds its session, herdr's or the one crew recorded in its pane. Returns (its session id, None), or (None, ("never", why)) when
    it is not ready in time, or (None, ("unread", what))."""
    deadline = pane.now() + wait
    while True:
        status, asking, sid, unread = pane.reading()
        if unread:
            return None, ("unread", unread)
        if status in ("idle", "done") and not asking and sid:
            return sid, None
        if pane.now() >= deadline:
            return None, ("never", "as it was not up" if status is None else "as it was waiting on a question in its pane"
                          if asking else "as crew found no session for it" if not sid else f"as herdr still reported it {status}")
        pane.sleep(1)


def read_back(pane, sid, size, text):
    """Read, about once a second for up to taken_within() seconds, whether the agent's session received the text past
    size bytes into its transcript, or from the start of the transcript of another session, when herdr names another
    now. Returns ("taken", None) when it did; ("not taken", None) when the time passes with the agent idle or done;
    ("unread", what) when crew cannot tell: the agent is blocked, gone, or still working WORKING_GRACE seconds on with
    no record of the prompt, which it may have taken with the record still to come, or a reading failed."""
    deadline, working = pane.now() + taken_within(), False
    while True:
        a, unread = pane.agent()
        sess = (a or {}).get("agent_session")
        now = sess.get("value") if isinstance(sess, dict) and isinstance(sess.get("value"), str) and sess["value"] else sid
        got = unread or pane.received(now, size if now == sid else 0, text)
        if isinstance(got, str):
            return "unread", got
        if got.get("received") is True:
            return "taken", None
        if got.get("received") is not False:
            return "unread", f"crew's reading of its transcript on {pane.host} gave no answer crew reads"
        if pane.now() >= deadline:
            if working:
                return "unread", (f"it went to work, and its transcript showed no prompt received {WORKING_GRACE} seconds "
                                  "on, so it may have taken it")
            status, asking, _, unread = pane.reading()
            if unread:
                return "unread", unread
            if status in ("idle", "done") and not asking:
                return "not taken", None
            if status != "working":
                return "unread", ("it is no longer up" if status is None else "it is waiting on a question in its pane"
                                  if asking else f"herdr reports it {status}")
            working, deadline = True, pane.now() + WORKING_GRACE
        pane.sleep(1)


# The greeting of each agent crew starts, by role: the reads its brief already teaches, and what is its own.
GREETINGS = {
    "design": ("Read where {label} stands with `crew bolts` and `crew rail`, and the signals waiting for curation, tell me in "
               "a few lines, then carry on with what is yours: curate the signals that have no move."),
    "planner": ("Read where {label} stands with `crew bolts` and `crew plan proposed`, tell me in a few lines, then carry on "
                "with what is yours: plan what is queued and see each open proposal through."),
    "ops": ("Read where {label} stands with `crew bolts` and `crew rail`, tell me in a few lines, then carry on with what is "
            "yours: a bolt lands only on the user's word, so land nothing until it comes."),
    "operator": ("Read where {label} stands with `crew rail` and `crew bolts`, and tell me in a few lines what is moving and "
                 "what waits on me."),
}


def greet_agent(fleet, name, text, on, label, why, hint, wait=90):
    """Greet an agent crew started: once it is up and settled, send it the text, marked [crew], taken or sent again
    (teams.15), and record a `greet` entry on the objects `on` in the label's run record. One stopped on a question in
    its pane, such as a first run's consent, is greeted once that is answered, for up to five minutes. Returns whether
    it was greeted; an agent that is not up is reported with the hint, one never ready or that never took the greeting
    with the crew tell that would greet it, one crew can't tell took it with what it could not read, and none is an
    error."""
    deadline, asked = time.monotonic() + wait, False
    while True:
        s, asking, _ = waits_on_question(fleet, name)
        how, said = greet_waits(name, s, asking, asked, time.monotonic() >= deadline, hint, text)
        if said:
            print(said, file=sys.stderr)
        if how == "greet":
            break  # what crew could not read, tell says
        if how == "gave up":
            return False
        if how == "asking":
            asked, deadline = True, time.monotonic() + 300
        time.sleep(2)
    if not tell(fleet, name, text, record=False, taken=True, what="its greeting",
                again=f"once it is ready: crew tell {name} {shlex.quote(text)}"):
        return False
    import record as rec  # record imports this module
    rec.emit(label, "greet", on=on, why=why)
    print(f"{name} greeted")
    return True


def greet_waits(name, status, asking, asked, out_of_time, hint, text):
    """One look of a greeting's wait for its agent (teams.7, teams.11): greet it once it is idle or done with no question
    open ("greet"); say once that it waits on a question, which then gives it five minutes ("asking"); give up when the
    time passes, saying it is not up with the hint, or the crew tell that would greet it ("gave up"); else look again
    (None). Returns (what to do, what to say or None)."""
    if status in ("idle", "done") and not asking:
        return "greet", None
    if asking and not asked:
        return "asking", f"{name} is waiting on a question in its pane; answer it there and it will be greeted"
    if out_of_time:
        return "gave up", (f"{name} is not up: {hint}" if status is None
                           else f"{name} was not ready to greet; once it is: crew tell {name} {shlex.quote(text)}")
    return None, None


def greet_standing(fleet, name, wait=90):
    """Get an agent crew starts going (a main level's design agent, planner, ops or operator): tell it to read where its
    partition stands and carry on with what is its role's. A name crew starts no agent by is refused."""
    label, text, why, hint = standing_greeting(fleet, name)
    return greet_agent(fleet, name, text, [f"agent/{name}"], label, why, hint, wait)


def standing_greeting(fleet, name):
    """The greeting of an agent crew starts, by its role, read from its name alone: its partition, the text, the greet
    entry's why, and how it is started when it is not up. The reviewer, sent its batch as its prompt, and a name crew
    starts no agent by are refused."""
    label = label_of_agent(fleet, name) or fail(f"no agent {name}: crew starts none by that name")
    host, _ = place_of_agent(fleet, name)
    role = name[len(label) + 1:]  # design, planner, ops, operator or reviewer
    role != "reviewer" or fail(f"{name} is sent its batch as its prompt by crew review, and is not greeted")
    role = role if role in GREETINGS else role.split("-")[0]
    return label, GREETINGS[role].format(label=label, host=host), f"main({label}): greet {name}", f"crew main up {label} starts and greets it"


def kept_on(fleet, host, repo):
    """The main checkout of a repo (owner/name) on a host: the first of the host's sessions whose space keeps it."""
    for sess in fleet["hosts"].get(host, {}).get("sessions", {}).values():
        if repo in (sess.get("repos") or []):
            return checkout(sess, repo)
    return None


def kit_kept(fleet, host, kit):
    """A kit as a host keeps it, named as a plan names it, by its forge address, <owner>/<name>, or its name alone: the
    repository of that address, or of that name, the first of the host's sessions whose space keeps it holds, as
    kept_on finds a repo, {"name", "repo" (owner/name as the space keeps it), "dir" (its folder), "main" (its main
    checkout)}; None where no session's space keeps it. Refused for a name alone when the spaces keep two repositories
    by it, since crew can't tell which is meant (read.1)."""
    same = (lambda r: r == kit) if "/" in kit else (lambda r: r.split("/")[-1] == kit)
    found = [(r, s) for s in fleet["hosts"].get(host, {}).get("sessions", {}).values() for r in (s.get("repos") or []) if same(r)]
    repos = list(dict.fromkeys(r for r, _ in found))
    len(repos) < 2 or fail(f"{host}'s spaces keep " + " and ".join(repos) + f" by the name {kit}, so crew can't tell which is meant")
    if not found:
        return None
    r, s = found[0]
    name = r.split("/")[-1]
    return {"name": name, "repo": r, "dir": f"{s['dir']}/{name}", "main": checkout(s, r)}


def crew_at(fleet, host):
    """The crew command on a host: this checkout here, else the crew checkout the host's spaces keep."""
    if host == this_host():
        return str(HOME / "plugin/bin/crew")
    c = kept_on(fleet, host, "afterthought/crew") or fail(f"none of {host}'s sessions keeps afterthought/crew, so crew can't run there")
    return f"{c}/plugin/bin/crew"


def crew_argv(fleet, host, *args):
    """crew on a host, run as the one asking here: their name, partition and Claude session go with it, so what it
    records names them and not the host that did the work."""
    import record as rec  # record imports this module
    return ["env", f"CREW_AGENT={rec.who()}", f"CREW_LABEL={caller_label(fleet) or ''}",
            f"CREW_SESSION={rec.session() or ''}", "bash", crew_at(fleet, host), *args]


def kits_on(fleet, label, host, fetch=False):
    """The main checkouts on a host of a partition's kits, the repositories its plan and its landings name
    (plan.kits_read), each as the host's spaces keep it (kit_kept), each once, a kit the host keeps no checkout of left
    out: the kit folders its main level reaches on its host (the user's ruling of 2026-11-01). Read from the partition's
    branch as crew's cache holds it, with no fetch (plan.12), as a standing agent's due restart reads it at each stop,
    or fetched first with fetch, as a role's start reads it."""
    import plan  # plan imports this module
    return [k["main"] for k in kits_kept(fleet, host, plan.kits_read(fleet, label, fetch))]


def kits_kept(fleet, host, kits):
    """The kits a host keeps of those named (a partition's, plan.partition_kits), each as the host's spaces keep it
    (kit_kept), each once by its main checkout, a kit the host keeps no checkout of left out."""
    out = {}
    for kit in kits:
        k = kit_kept(fleet, host, kit)
        if k:
            out.setdefault(k["main"], k)
    return list(out.values())


def blueprints_on(fleet, label, host):
    """The main checkouts on a host of the partition's blueprints repos, the default first."""
    return [c for c in (kept_on(fleet, host, b) for b in partition_of(fleet, label)["blueprints"]) if c]


def definition(role):
    """roles/<role>.md: an agent definition in Claude Code's format, its frontmatter naming the role's model and effort."""
    path = LIB.parent / "roles" / f"{role}.md"
    path.exists() or fail(f"no definition {path}")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", path.read_text(), re.S) or fail(f"{path} has no frontmatter")
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if line.strip())
    for k in ("name", "description", "model", "effort"):
        meta.get(k) or fail(f"{path}: its frontmatter has no '{k}'")
    meta["effort"] in EFFORTS or fail(f"{path}: effort '{meta['effort']}' is no effort level. levels: " + " ".join(EFFORTS))
    return meta, m.group(2)


def launch(fleet, label, role, fetch=False):
    """How crew-role starts a partition's main-level role: its folder, agent name, partition, the definition it comes
    from, the folders it may also reach, its blueprints' and its kits' on its host (kits_on, fetched first with fetch),
    and the model and effort after the teams file's override."""
    p = partition_of(fleet, label)
    roles = p["roles"]
    main = dict(cwd=p["checkout"], dirs=[d for d in blueprints_on(fleet, label, p["machine"])[1:] + kits_on(fleet, label, p["machine"], fetch)])
    if role in MAIN_STANDING + ("reviewer",):
        spec = dict(main, defn="main-ops" if role == "ops" else role, name=f"{label}-{role}")
    else:
        fail(f"no role '{role}' at {label}'s main level. roles: design planner ops reviewer operator")
    meta, _ = definition(spec["defn"])
    o = roles.get(spec["defn"], {})
    return dict(spec, label=label, model=o.get("model", meta["model"]), effort=o.get("effort", meta["effort"]))


def operator_session(fleet, label, host):
    """The operator session of a partition on a host is the session named after its label there, where crew console
    up opens the partition's console."""
    p = partition_of(fleet, label)
    sess = fleet["hosts"].get(host, {}).get("sessions", {}).get(label)
    sess or fail(f"{host} has no session named {label} in {HOSTS}, so no operator session of {label} runs here")
    sess.get("partition") == p["partition"] or fail(f"{host}'s session {label} is in partition {sess.get('partition')}, not {p['partition']}")
    return sess


def reach(fleet, machine):
    """What bash crew needs to run a command again on the machine it acts on, given with the command's env so that
    forwarding starts no Python of its own: on another host, the crew there (REMOTE_CREW, or REMOTE_CREW_REFUSED
    saying why there is none) and the caller's Claude session (CALLER_SESSION, empty for the user); on this host,
    nothing."""
    if machine == this_host():
        return {}
    import record as rec  # record imports this module
    out = {"CALLER_SESSION": rec.session() or ""}
    try:
        out["REMOTE_CREW"] = crew_at(fleet, machine)
    except Refusal as e:
        out["REMOTE_CREW_REFUSED"] = str(e)
    return out


# How an agent records a finding, the same in every brief that records one.
def signal_how(cmd, label, state):
    return (f"`{cmd} signal <slug> \"<what it asserts, in a sentence>\" --excerpt \"<the exact words the user said or the tool "
            f"printed>\" --kind constraint|ask|question|commitment|reaction`. Copy the excerpt, never reword it: crew looks for it "
            f"in your own session's transcript, and a refusal means the words were reworded or are a background task's output "
            "you have not read: read the output file its task notification names, then record the signal again. When the words "
            "point at something made elsewhere, such as another conversation, a page or prototype, an artifact, files in another "
            "repo or a spike, "
            "find it and name in the sentence where it lives, in a form another agent can open: `<owner>/<repo>:<path>`, a "
            "branch, an artifact's link. A conversation's id alone is not enough: name what it made. crew writes the signal under "
            f"`signals/` on `{label}/main` of {state}.")


# How an agent asks the user a question of its own, the same in the brief of each of the three that ask: the planner's,
# main-level ops's and the design agent's (record 0031, briefs.11; Decision 6 of the-team-machinery-leaves).
def cards_how(cmd, label, kits):
    return ("A question of yours for the user reaches them on a Pending You card you ask yourself; every other card on "
            "the rail is crew's. Three ask the user: the planner, main-level ops and the design agent. A Flume place "
            "that stops short asks the one of you it names, who gets the answer and gives it to the place with "
            f"`{cmd} answer`; the operator and the reviewer ask nothing; and crew refuses a card from any other agent. "
            "Before you ask, answer it from the "
            f"records and the rules already written, or ask the agent whose it is with `{cmd} tell`: `{label}-design` for "
            f"the design, `{label}-ops` for a live system or a deploy, `{label}-planner` for the plan. It is the user's "
            "only when they alone can decide, know or do it, in their name, their money, their plans, public or hard to "
            "undo, and not what is cheap to change later; when the records do not settle it; and when its choices lead "
            "to noticeably different products. Otherwise decide what a careful product designer would, and say so.\n\n"
            "Ask it through Pending You's own tools in your session, shaped as the question needs: its options, with the "
            "one you recommend; `blocking` false and the fallback you take meanwhile when you can go on without it, and "
            "go on; and what you tried, in its `tried`. Post it with the `idempotencyKey` "
            "`ask/<your crew name>/<what it is about>`, a key of your own, so a retry never makes a second card. Never "
            "post again under a key whose card was answered: Pending You gives that card back, and the user is not "
            "asked. What you need after an answer is a new card under a new key, following the one answered. A card "
            "under a row's key, `proposal/`, `batch/`, `land/`, `deploy/`, `op/` or `record/`, is crew's: it raises "
            "each at its event, in its owner's name, changes it in place and closes it at the event that ends it, and "
            "refuses your post, change or close of one. Your brief says which of them are yours to adopt and answer.\n\n"
            "At your start, call `whoami` with your crew name and one line on your role. Then call `list_pending` with "
            "that name, and act on any card the user has answered. Ask every card in your crew name, with this host as "
            "the session's machine and your worktree as its folder. File it in the area of its kit, found with "
            "`match_area` from the kit's git remote. When there is none, create it with `create_area`, named for the "
            f"kit, in the group `{label}`, with the key `create-area:<owner>/<kit>`: crew refuses an area under any other "
            f"key. Never make a group: if `{label}` isn't one of the user's groups, the area is left ungrouped, and you "
            "say so once. You hear an answer by being woken in your pane. Never run `npx pendingyou` or `pendingyou "
            "hold`: the `pendingyou` on the path is the fleet's, and the wake needs neither. Act on the user's answer as "
            "if they had said it in your pane, then close your question's card with `ack_answer` and a one-line "
            "outcome; withdraw one you no longer need with `cancel_request` and the reason. A card of yours Pending You "
            "answers \"not found\" stayed with the host's sign-in before this one, where the user may still answer it, "
            "to nobody: ask it again if it still matters, under the same key, saying in it that an older copy is dead "
            "and to dismiss it in the app. Only your own cards are yours: leave every other card alone. The kits: "
            f"{kits}.")


def kits_named(kits):
    """Kits as the card discipline names them, <name>: <owner>/<repo>."""
    return "; ".join(f"{k['name']}: {k['repo']}" for k in sorted(kits, key=lambda k: k["name"])) or "none yet"


# Who is speaking in an agent's pane, beside every brief's roster.
SENDERS = ("A message in your pane that begins `[crew tell from <name>]` was sent with crew tell by that agent, or by "
           "the user when the name is `<user>@<host>`; one that begins `[crew tell from <user>@board]` is the user's word "
           "sent from the board about the item it names, and answers no card; one that begins `[crew]` is crew's own; "
           "anything else typed there is the user.")

# How anything for another partition is sent, beside every brief's roster (briefs.10): to that partition's operator,
# its one door, and to nobody else.
SENDS = (f"`{HOME}/plugin/bin/crew send <partition> \"<text>\"`, which reaches that partition's operator, its one door, "
         "and to nobody else")

# How an agent reports results, the same in every brief that reports them.
RESULTS = ("## Test, check and proof results\n\n"
           "Whenever you report how tests, checks or proofs went (a suite you ran, a merge's checks, the bolt's verification, "
           "an `openspec validate`, a verify's checks), list them first, before any prose, "
           "one bullet per suite, check or proof:\n\n"
           "- ✅ <what ran>: passed, with its counts where the tool gave them (`46 passed`)\n"
           "- ❌ <what ran>: failed, with how many failed and one line on why (`2 of 46 failed: t-briefs lacks \"open nothing\"`)\n"
           "- ⏳ <what ran>: not yet run, or still running, and what it waits on\n\n"
           "Use these three marks and no other. A check skipped on purpose, or one you don't run yourself, is ⏳ with what it "
           "waits on; a check that is red on purpose is still ❌, its line saying so. A verify's checks are the dimensions of "
           "its scorecard: one with a CRITICAL issue is ❌ with how many, one with only warnings or suggestions is ✅ with "
           "those counts, and one it skipped is ⏳ with the reason its report gives.\n\n"
           "Never say a result only in a sentence (\"they all passed\"), and never fold several suites into one bullet. Take "
           "every count from what the tool printed; where it printed none, give none. What you would do about a failure, and "
           "anything else you have to say, comes after the list. Use the same list wherever the results go: your reply, a "
           "file you write them to, or a message to another agent that will pass them on. When you pass on results another "
           "agent reported, show its list as it is, first.")


# How a main-level role's work reaches it, the brief's {{TURN}} (design Decision 9, role-runs "A run's brief says how a
# turn goes"): for a role its partition runs as its kind, how a turn goes, with what is the role's own in a turn
# (TURN_OWN); for one that stands, that its work reaches it in its pane.
KIND_TURN = (
    "You run as your kind: no agent of you stands, and each run of you is one turn, a place the host's runner launches "
    "while anything waits for you, one at a time. Your turn starts with `{{TEAM_CMD}} role start`, which takes everything "
    "asked of you since your last turn and prints this brief's path, each ask, each place that waits on you and the "
    "cards the user answered in your name; act on what it took, as this brief says, and end the turn with "
    "`{{TEAM_CMD}} role end`, as your turn's prompt says. Wait "
    "in your session on nothing: where this brief says to wait for an answer, a submission, a review or a tell, end your "
    "turn instead, and the thing reaches your next run as an ask. What is asked after your start waits for your next "
    "turn. Ask the user only on a card in your own name, {{SELF}}, never by stopping short.")
TURN_OWN = {
    "reviewer": " A batch asked of you names the file its summary goes to; once each batch your turn took has its summary "
                "written, run `{{TEAM_CMD}} review delivered`, which records it, raises its card in the planner's name and "
                "asks the planner.",
    "main-ops": " From your run, `{{TEAM_CMD}} bolt submit` returns once each bolt is queued: how each landing ends "
                "reaches your next run as an ask when it does not land, and the planner's and the design agent's when it "
                "does.",
    "planner": " `{{TEAM_CMD}} review {{LABEL}}` asks the reviewer a batch where it runs as its kind, and its delivery "
               "reaches you as an ask, with the line that adopts its card.",
}
STANDING_TURN = ("You stand in your pane, an agent crew started and keeps up: your work reaches you there, as tells marked "
                 "`[crew tell from <sender>]` or `[crew]`, and as the answers to the cards you adopted.")


def turn_said(p, defn):
    """The brief's {{TURN}} for a partition's main-level role, by its definition: how a turn goes for a role its
    partition runs as its kind (KIND_TURN, TURN_OWN), else how a standing role's work reaches it."""
    role = "ops" if defn == "main-ops" else defn
    if role in KIND_ROLES and p["flume"][role] is not False:
        return KIND_TURN + TURN_OWN.get(defn, "")
    return STANDING_TURN


def main_tokens(fleet, p, role, self_name):
    import plan  # plan imports this module
    label, host, cmd = p["label"], this_host(), f"{HOME}/plugin/bin/crew"
    # The partition's kits, the repositories its plan and its landings name, as crew's cache holds its branch (plan.12),
    # and those its main level's host keeps a checkout of (Decision 3 of the-team-machinery-leaves).
    named = plan.kits_read(fleet, label, False)
    kept = kits_kept(fleet, p["machine"], named)
    names = {"design": f"{label}-design", "planner": f"{label}-planner", "main-ops": f"{label}-ops",
             "operator": f"{label}-operator", "reviewer": f"{label}-reviewer"}
    account = lambda s: fleet["hosts"].get(p["machine"], {}).get("sessions", {}).get(s, {}).get("account", "")
    places = "; ".join(f"`{label}-{r}` in session {s}" + (f" (account {account(s)})" if account(s) else "")
                       for r, s in ((r, role_session(p, r)) for r in MAIN_STANDING + ("reviewer",)))
    # The partitions whose operator can change the teams, by label for crew send: one whose main level runs on a Mac
    # keeping swancloud's checkout, where lib/crew-teams.nix is edited.
    doors = sorted(f"`{o['label']}`" for o in fleet["partitions"].values()
                   if fleet["hosts"].get(o["machine"], {}).get("kind") == "darwin" and kept_on(fleet, o["machine"], "afterthought/swancloud"))
    tok = {
        "SELF": self_name or names[role], "LABEL": label, "PARTITION": p["partition"], "HOST": host, "TEAM_CMD": cmd,
        "BLUEPRINTS_REPOS": ", ".join(f"`{b}`" for b in p["blueprints"]), "SIGNALS_REPO": p["blueprints"][0],
        "PLANS": f"`{label}/main` of {p['state']}", "STATE_REPO": p["state"], "SIGNAL": signal_how(cmd, label, p["state"]),
        "CARDS": cards_how(cmd, label, kits_named(kept)), "RESULTS": RESULTS,
        "CHECKOUT": p["checkout"], "MAIN_PLACE": f"session {p['session']} on {p['machine']}", "MAIN_SESSIONS": places,
        "DESIGN_AGENT": f"{label}-design", "PLANNER": f"{label}-planner", "MAIN_OPS": f"{label}-ops",
        "REVIEWER": f"{label}-reviewer", "REVIEWS": f"~/.local/state/crew/{label}-main/reports",
        "KITS": ", ".join(sorted({k.split("/")[-1] for k in named})) or "none yet",
        "KIT_CHECKOUTS": ", ".join(f"`{k['main']}`" for k in kept) or "none on this host",
        "TEAMS_DOORS": ", ".join(doors) or "none", "TURN": turn_said(p, role),
        "SHOWING": (f"{host} is a Mac: open the site the user picks in terminal-browser beside your pane, "
                    "`terminal-browser open <url> --split right`." if fleet["hosts"].get(host, {}).get("kind") == "darwin" else
                    f"{host} is a box, which can't open the dev.swancloud.net names: say so, and give the user the URL "
                    "`crew sites` marks to open from a Mac."),
    }
    tok["ROSTER"] = (
        f"{label}'s main level ({p['partition']}) runs on {p['machine']}, in the `{label}` workspace of each of its sessions: {places}. "
        f"`{label}-design`, the design agent, keeps the design true on main and curates signals; `{label}-planner` plans the partition's "
        f"bolts and posts its review batches; `{label}-reviewer`, started fresh for each batch, summarizes its changes; `{label}-ops` lands "
        f"proven bolts on the user's send on each kit's landings card; and `{label}-operator`, the partition's door, works for the user. "
        f"Any of these is reached with `{cmd} tell <agent> \"<text>\"`, wherever it runs; "
        f"anything for another partition is sent with {SENDS}. {SENDERS}")
    return tok


def brief(fleet, label, role, self_name=""):
    """A definition's body, filled from the teams file for a partition's main level."""
    role in MAIN_ROLES or fail(f"no definition '{role}' for a main level. definitions: " + " ".join(MAIN_ROLES))
    tok = main_tokens(fleet, partition_of(fleet, label), role, self_name)
    def fill(m):
        k = m.group(1)
        if k not in tok:
            fail(f"roles/{role}.md needs {{{{{k}}}}} and crew.py builds no such token")
        return tok[k]
    text = definition(role)[1]
    for _ in range(2):  # a token's text may itself carry tokens
        text = re.sub(r"\{\{([A-Z_]+)\}\}", fill, text)
    return text


# What crew's SessionStart hook (plugin/hooks/session-start) records of each session of an agent it started.
SESSIONS = pathlib.Path.home() / ".local/state/crew/sessions"


def transcript_cwd(path):
    """The folder a Claude conversation began in, from the first of its transcript's records that names one."""
    try:
        with open(path) as f:
            for line in itertools.islice(f, 200):
                try:
                    cwd = json.loads(line).get("cwd")
                except (ValueError, AttributeError):
                    continue
                if isinstance(cwd, str) and cwd:
                    return cwd
    except OSError:
        pass
    return None


def last_conversation(name):
    """The agent's last session, as (session id, the folder it began in), when it can be resumed. None when it can't:
    Claude Code keeps a conversation only once it has had a message, and finds it again only from the folder it began
    in, which must still exist. Only the last session counts: one started fresh and never spoken to is not a reason to
    pick up the conversation before it. Records from before the hook kept the folder are read for it from the
    conversation's own transcript."""
    found = []
    for p in (SESSIONS.iterdir() if SESSIONS.is_dir() else []):
        try:
            kv = dict(l.split("=", 1) for l in p.read_text().splitlines() if "=" in l)
            if kv.get("CREW_AGENT") == name:
                found.append((p.stat().st_mtime, p.name, kv))
        except OSError:
            continue
    for _, sid, kv in sorted(found, reverse=True)[:1]:
        kept = sorted(pathlib.Path.home().glob(f".claude*/projects/*/{sid}.jsonl"))
        cwd = kept and (kv.get("CREW_CWD") or transcript_cwd(kept[0]))
        if cwd and pathlib.Path(cwd).is_dir():
            return sid, cwd
    return None


def brief_due(source, launched, saved):
    """The agent whose brief crew's SessionStart hook gives a session back as context (teams.6), or None. source is the
    hook's, launched whether CREW_AGENT is in the hook's environment, saved the session's record. Only a compaction
    calls for it, of a crew agent's session whose process crew-role did not start: one herdr resumed with a bare
    `claude --resume`, which keeps its brief from the transcript only until its first compaction. A resume needs none,
    herdr's or crew's, since the transcript still holds the brief; nor does a session crew-role started, which carries
    its brief in its arguments through every compaction."""
    if source != "compact" or launched:
        return None
    return saved.get("CREW_AGENT") or None


def main_named(name, label):
    """The main-level role a session's recorded agent is, from its record alone: its role when the name is
    <label>-design, -planner, -ops, -operator or -reviewer, else None, as for a team's agent or a dispatcher from
    before teams left, or a record with no label. These are every agent crew starts, so a session whose record names
    no such role is given nothing of crew's back (main-level), and its identity, tied to its main level's host, is the
    one that reads the teams file."""
    if not name or not label:
        return None
    return next((r for r in MAIN_STANDING + ("reviewer",) if name == f"{label}-{r}"), None)


def kind_said(label, role):
    """Why crew-role starts no standing agent of a role its partition runs as its kind (main-level "A role that runs as
    its kind is not started by crew-role", design Decision 14): its runs are places the host's runner launches, and the
    user opens one to talk with crew role open."""
    return (f"{label}'s {role} runs as its kind, so crew starts no standing agent of it: it is opened with crew role open "
            f"{role} --label {label}")


def main_elsewhere_said(name, label, main, here):
    """Why a main level's agent is not started, nor given its identity back, on this host: crew-role's refusal."""
    return f"{label}'s main level runs on {main}, not {here}, and crew starts {name} only there"


def identity_withheld(name, label, here, main, unread=None):
    """What a session herdr resumed as a main level's agent is told in place of its identity, or None when it gets
    its identity back: on its main level's host, the teams file read. Off that host, or with the teams file unread
    (unread, the refusal's words), it is told it is no agent of crew's here and to do nothing of crew's (read.1)."""
    if unread is None and main == here:
        return None
    why = (f"it can't tell where {label}'s main level runs, {unread.rstrip('.')}" if unread is not None
           else main_elsewhere_said(name, label, main, here))
    return (f"[crew] This session was {name}, and crew gives it no identity here: {why}. In this session you are no "
            "agent of crew's: run no crew command, which crew would record as the user's, write nothing to the plan, "
            "a kit, a card or another agent, and wait for the user.")


def brief_role(fleet, name, recorded):
    """The partition and definition an agent's brief is built from: the definition crew-role recorded starting it from
    (recorded), else, for a session recorded before crew-role named it, the one its name gives. Refused for a name crew
    starts no agent by."""
    label = label_of_agent(fleet, name) or fail(f"no agent {name}: crew starts none by that name")
    role = name[len(label) + 1:]  # design, planner, ops, reviewer, operator
    return label, recorded or {"ops": "main-ops"}.get(role, role)


def brief_back_said(name, text):
    """What a session is given back after a compaction: its brief whole, behind a line saying what it is. Claude Code
    keeps to a file one longer than its cap on a hook's context, passing its path and opening words, so the line says to read it."""
    return (f"[crew] This is your brief as {name}, which the compaction took out of your context, given back whole as crew "
            "built it when it started you; it binds you as before. If it is cut short below, with the path of a file "
            f"holding the whole of it, read that file whole now, before anything else.\n\n{text}")


# ------------------------------------------------------------------------- a host's hold, and what an agent loaded

# A host's hold (teams.19): while `crew hold` holds it, crew starts no agent there until `crew go`.
HOLD = pathlib.Path.home() / ".local/state/crew/hold"
# What a Claude session loads of crew's plugin once, at its start, besides its brief (teams.19): a change to any of
# these reaches a standing agent only when it starts again. The hooks' own scripts and crew's code run afresh at each
# call, so a change to them alone is live at once.
LOADED = ("plugin/hooks/hooks.json", "plugin/hooks/status.js", "plugin/skills", "plugin/.claude-plugin")


def held():
    """This host's hold, {"by", "why", "at"} and whether it was --now, while crew hold holds it, else None; a hold file
    crew can't read holds the host all the same, its why saying so (read.1)."""
    try:
        text = HOLD.read_text()
    except FileNotFoundError:
        return None
    except OSError as e:
        return {"by": "?", "why": f"crew can't read its hold file {HOLD}: {e.strerror or e}", "at": None}
    try:
        h = json.loads(text)
    except ValueError:
        h = None
    if isinstance(h, dict) and all(isinstance(h.get(k), str) for k in ("by", "why", "at")):
        return h
    return {"by": "?", "why": f"crew can't read its hold file {HOLD}", "at": None}


def held_on(fleet, host):
    """A host's hold, read where it is (held): None when it is not held, or when the host does not answer, whose own
    crew then refuses what would start an agent there."""
    if host == this_host():
        return held()
    r = on_machine(fleet, host, ["cat", ".local/state/crew/hold"])
    if r.returncode:
        return None
    try:
        h = json.loads(r.stdout)
    except ValueError:
        h = None
    return h if isinstance(h, dict) and all(isinstance(h.get(k), str) for k in ("by", "why", "at")) else \
        {"by": "?", "why": f"crew can't read {host}'s hold file", "at": None}

def held_said(host, h):
    """What crew says of a start a host's hold refuses."""
    since = f" since {h['at']}" if h.get("at") else ""
    return f"{host} is held by {h['by']}{since}: {h['why']}. crew starts no agent there until crew go {host}"


SHA = re.compile(r"[0-9a-f]{40}([0-9a-f]{24})?")


def files_ref(common, name):
    """A ref's commit read from a git folder's files, with no process: its loose file, else its line in packed-refs;
    "" when neither holds it, in a folder whose refs are files; None when the files can't say, a symbolic ref, a
    reftable folder or a file that can't be read, for the caller to ask git (read.1)."""
    common = pathlib.Path(common)
    if (common / "reftable").exists():
        return None
    try:
        text = (common / name).read_text().strip()
        return text if SHA.fullmatch(text) else None
    except (FileNotFoundError, NotADirectoryError):
        pass
    except OSError:
        return None
    try:
        lines = (common / "packed-refs").read_text().splitlines()
    except FileNotFoundError:
        return ""
    except OSError:
        return None
    for line in lines:
        sha, _, ref = line.partition(" ")
        if ref == name and SHA.fullmatch(sha):
            return sha
    return ""


def files_refs(common, prefix):
    """Every ref under a prefix read from a git folder's files, with no process, as files_ref reads one: {name: commit},
    each loose file over its line in packed-refs; None when the files can't say, a reftable folder, a ref that is not
    a commit's name or a file that can't be read, for the caller to ask git (read.1)."""
    common = pathlib.Path(common)
    if (common / "reftable").exists():
        return None
    refs = {}
    try:
        lines = (common / "packed-refs").read_text().splitlines()
    except FileNotFoundError:
        lines = []
    except OSError:
        return None
    for line in lines:
        sha, _, ref = line.partition(" ")
        if ref.startswith(prefix) and SHA.fullmatch(sha):
            refs[ref] = sha
    try:
        for f in (common / prefix).rglob("*"):
            if f.is_file():
                text = f.read_text().strip()
                if not SHA.fullmatch(text):
                    return None
                refs[f.relative_to(common).as_posix()] = text
    except OSError:
        return None
    return refs


def head_here(root=None):
    """crew's checkout's commit, read from its files with no process (files_ref): its .git, a folder or a linked
    worktree's file naming one, its HEAD, and the branch HEAD names in the folder its worktrees share; through git
    rev-parse only when the files can't say. None when neither can read it."""
    root = pathlib.Path(root or HOME)
    try:
        dot = root / ".git"
        if dot.is_dir():
            gitdir = dot
        else:
            line = dot.read_text().strip()
            gitdir = root / line[len("gitdir: "):] if line.startswith("gitdir: ") else None
        if gitdir:
            head = (gitdir / "HEAD").read_text().strip()
            if SHA.fullmatch(head):
                return head
            common = gitdir / (gitdir / "commondir").read_text().strip() if (gitdir / "commondir").exists() else gitdir
            got = files_ref(common, head[len("ref: "):]) if head.startswith("ref: ") else None
            if got:
                return got
    except OSError:
        pass
    r = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    return (r.stdout.strip() or None) if r.returncode == 0 else None


def crew_version(root=None):
    """This host's crew: (its checkout's commit, its version), the version being the release tag at or before the
    commit, with `+<n>` for the commits past it; the version None when no release tag is reachable, and both None when
    git can't read the checkout."""
    root = str(root or HOME)
    r = subprocess.run(["git", "-C", root, "describe", "--tags", "--long", "--match", "v[0-9]*", "--abbrev=40", "HEAD"],
                       capture_output=True, text=True)
    m = re.fullmatch(r"(v[0-9]\S*)-([0-9]+)-g([0-9a-f]{40})", r.stdout.strip()) if r.returncode == 0 else None
    if m:
        return m.group(3), m.group(1) + ("" if m.group(2) == "0" else f"+{m.group(2)}")
    r = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True)
    return (r.stdout.strip() or None, None) if r.returncode == 0 else (None, None)


def loaded_changed(old, new, root=None):
    """Whether what a session loads of crew's plugin at its start (LOADED) differs between two commits of crew: True,
    False, or None when git can't tell, as when the older commit is not in this checkout."""
    r = subprocess.run(["git", "-C", str(root or HOME), "diff", "--quiet", old, new, "--", *LOADED],
                       capture_output=True, text=True)
    return {0: False, 1: True}.get(r.returncode)


def launch_digest(l, text):
    """What an agent's start is made of besides crew's plugin, as one short digest: its model, effort, folders and
    brief (teams.6), so that a change to any of them reads as due (update_due)."""
    return hashlib.sha256(json.dumps([l["model"], l["effort"], sorted(l["dirs"]), text]).encode()).hexdigest()[:16]


def launch_now(fleet, scope, role):
    """The digest of what crew-role would start a standing role with now (launch_digest), its kits read from the
    partition's branch as crew's cache holds it, with no fetch (kits_on)."""
    l = launch(fleet, scope, role)
    return launch_digest(l, brief(fleet, scope, l["defn"], l["name"]))


def standing_role(fleet, name):
    """The partition and role crew-role starts a standing agent as, from its name alone: (label,
    design|planner|ops|operator); None for the reviewer, or a name crew starts no agent by. Only a standing agent
    outlives a batch, so only it is restarted for an update (teams.19)."""
    label = label_of_agent(fleet, name)
    role = name[len(label) + 1:] if label else ""
    return (label, role) if role in MAIN_STANDING else None


def agents_here(fleet, label=None):
    """The standing agents crew runs on this host, by name, of one partition or of every one: the main level's roles
    whose machine this is."""
    host, out = this_host(), []
    for l, p in sorted(fleet["partitions"].items()):
        if label not in (None, l):
            continue
        out += [f"{l}-{r}" for r in MAIN_STANDING if p["machine"] == host]
    return out


def starts():
    """What each agent's last start on this host recorded (hooks/session-start), by the agent's name: its session, the
    commit and version of crew it loaded and the digest of the launch it was started with, each None when the start did
    not record it, as one before crew kept them."""
    found = {}
    for p in (SESSIONS.iterdir() if SESSIONS.is_dir() else []):
        try:
            kv = dict(l.split("=", 1) for l in p.read_text().splitlines() if "=" in l)
            at = p.stat().st_mtime
        except OSError:
            continue
        name = kv.get("CREW_AGENT")
        if name and (name not in found or (at, p.name) > found[name][0]):
            found[name] = ((at, p.name), {"session": p.name, "commit": kv.get("CREW_COMMIT") or None,
                                          "version": kv.get("CREW_VERSION") or None, "launch": kv.get("CREW_LAUNCH") or None})
    return {name: s for name, (_, s) in found.items()}


def start_of(name):
    """What an agent's last start on this host recorded (starts), or None when it has no record."""
    return starts().get(name)


# What the update check says of a start that recorded its launch but no crew commit, as one on a host that loads crew
# from its release, where there is no git to read the commit from (record 0050 as amended 2026-10-30).
NO_COMMIT_SAID = ("crew can't tell whether its plugin changed since it started, its start having recorded no crew commit: "
                  "a bump of crew's pin restarts it only by crew main down and crew main up, until crew reads its release "
                  "where it runs")


def update_due(started, commit, launch, loaded):
    """Whether a standing agent is due a restart for crew's update (teams.19), and why, from facts: what its last start
    recorded (start_of), this checkout's commit, the digest of the launch it would be started with now, and whether
    what a session loads of crew's plugin changed between its start's commit and this one (loaded_changed, None when
    git can't tell). Returns (due, why): due when it started before crew kept what it loaded, when its brief, model,
    effort or folders changed, or when what it loaded of crew's plugin did; never for a change to crew's code alone,
    which is live at once; and not when crew can't tell, which it says (read.1). A start that recorded its launch and no
    crew commit is read by its launch alone, since the digest covers no part of crew's plugin (NO_COMMIT_SAID)."""
    if started is None:
        return False, None
    if not started["launch"]:
        return True, "it started before crew kept what an agent loads"
    if started["launch"] != launch:
        return True, "its brief, model, effort or folders changed"
    if not started["commit"]:
        return False, NO_COMMIT_SAID
    if started["commit"] == commit:
        return False, None
    if loaded is None:
        return False, f"crew can't tell whether its plugin changed since {started['commit'][:7]}"
    return (True, "crew's plugin changed") if loaded else (False, None)


# Why a main level's standing agent is due an end and never a restart once its partition runs its role as its kind
# (end_due; design Decision 14 of roles-run-as-flume-kinds).
KIND_SAID = "its role now runs as its kind, in Flume runs of its own"


def end_due(fleet, name):
    """Why a standing agent is due an end rather than a restart, or None: a main level's design agent, planner, ops or
    operator once its partition runs its role as its kind (kind_role_of; design Decision 14 of
    roles-run-as-flume-kinds), read from the teams file alone, KIND_SAID; never another agent."""
    kind = kind_role_of(fleet, name)
    return KIND_SAID if kind and kind[1] in MAIN_STANDING else None


def due_of(fleet, name, started=None, commit=None):
    """Whether a standing agent of this host is due a restart for crew's update, read: (due, why, what its start
    recorded). A name that is no standing agent's is never due. A main level's agent whose role now runs as its kind
    is due an end, its why KIND_SAID (end_due)."""
    started = started or start_of(name)
    role = standing_role(fleet, name)
    if started is None or role is None:
        return False, None, started
    ends = end_due(fleet, name)
    if ends:
        return True, ends, started
    commit = commit or crew_version()[0]
    try:
        now = launch_now(fleet, *role)
    except Refusal as e:
        return False, f"crew can't build its brief: {e}", started
    loaded = loaded_changed(started["commit"], commit) if started["commit"] and commit and started["commit"] != commit else None
    return (*update_due(started, commit, now, loaded), started)


def resolve(fleet, scope, role, extra, fetch=False):
    """How a role starts, and with "resume" the session it picks up: its last conversation, in the folder that began
    it, which need not be where the role starts today; its kits read as launch reads them, fetched first with fetch."""
    l = launch(fleet, scope, role, fetch)
    found = last_conversation(l["name"]) if extra == "resume" else None
    return (dict(l, cwd=found[1]), found[0]) if found else (l, None)


def launch_shell(fleet, scope, role, extra):
    """crew-role's start, as shell assignments: CWD, NAME, LABEL, ROLE (the definition its brief comes from), LAUNCH
    (what the start is made of besides crew's plugin, launch_digest) and the claude arguments in `args`. A resume with
    no conversation to pick up starts the role fresh.
    A main level's role, fresh or resumed, is refused on any host but its main level's (main_elsewhere_said), and on
    every host when its partition runs it as its kind (kind_said). Its kit folders are the partition's kits as its
    branch stands on GitHub, fetched once for the start (kits_on), which its brief then reads with no fetch of its own."""
    if role in MAIN_STANDING + ("reviewer",):
        p, here = partition_of(fleet, scope), this_host()
        p["flume"][role] is False or fail(kind_said(p["label"], role))
        p["machine"] == here or fail(main_elsewhere_said(f"{p['label']}-{role}", p["label"], p["machine"], here))
    l, session = resolve(fleet, scope, role, extra, fetch=True)
    args = ["--model", l["model"], "--effort", l["effort"], "--permission-mode", "bypassPermissions"]
    for d in l["dirs"]:
        args += ["--add-dir", d]
    args += ["--name", l["name"]]
    if session:
        args += ["--resume", session]
    text = brief(fleet, scope, l["defn"], l["name"])
    args += ["--append-system-prompt", text]
    return (f"CWD={shlex.quote(l['cwd'])}\nNAME={shlex.quote(l['name'])}\nLABEL={shlex.quote(l['label'])}\n"
            f"ROLE={shlex.quote(l['defn'])}\nLAUNCH={launch_digest(l, text)}\n"
            f"args=({' '.join(shlex.quote(a) for a in args)})")


def here(fleet):
    """What crew runs on this host: the labels of the main levels whose machine is here, each of whose sessions is one
    Agents (mains). A console runs no agent and is not listed."""
    host = this_host()
    return [label for label, p in sorted(fleet["partitions"].items()) if p["machine"] == host]


# ------------------------------------------------------------------------------------------ a main level's panes

def nap(seconds):
    """A pause between looks at a pane: the host's sleep, which crew's tests stub to return at once."""
    subprocess.run(["sleep", str(seconds)])


def working_said(agent):
    """What crew says of an agent it will not end because it works (teams.2)."""
    return f"{agent} is working; add --force to end it anyway."


# Claude Code's question at /exit while background work of the session runs: its title, and its first option, which it
# focuses, so Enter takes it. Read in Claude Code 2.1.307's bundle on 2026-10-22: "Background work is running", "The
# following will stop when you exit:", then Exit and stop tasks, Move to background and exit when the session can be
# moved, and Stay (read.2); a give's restart of swc-3's and swc-4's conductors stopped there on their landing-card waits
# (signal 2026-10-22-swancloud-dispatch-deneb-bddc208d/01).
EXIT_ASKS = ("Background work is running", "Exit and stop tasks")


def exit_asks(screen):
    """Whether an agent's pane shows Claude Code's question at its exit while background work of its session runs
    (EXIT_ASKS), from the lines herdr reads of the pane's screen."""
    return bool(screen) and all(w in screen for w in EXIT_ASKS)


def started_said(name, pane, stage=None):
    """What crew says of a role it started, fresh at a stage or brought back with its conversation."""
    return f"{name} resumed in {pane}" if stage == "resume" else f"{name} started {stage} in {pane}" if stage else f"{name} started in {pane}"


def moved_said(scope, was, session):
    """What crew says when an agents' state folder last named another session than the one its teams file gives now,
    so its pane ids are another session's (teams.2): None when it names this one, or none."""
    if not was or was == session:
        return None
    return f"{scope}'s panes were recorded in session {was}, and it runs in {session} now; their ids name nothing here"


def ws_key(label):
    """A workspace's label as a key of the layout file, which splits on spaces."""
    return "ws:" + label.replace(" ", "_")


class Agents:
    """The agents crew starts in one herdr session of this host and their panes, as one crew command acts on them there
    (code.3): a main level's, or a console's (standing). The panes and layout files of its state folder change only by
    writing a new file over the old (teams.9), and its herdr session is read through the command's Herdr. A working agent is ended only when force is given (teams.2); `ended` names each
    role whose agent this command ended, and `fresh` each it started with a new conversation, none picked up."""

    def __init__(self, fleet, kind, scope, label, session, state, standing, cwd, machine, host=None, force=False):
        self.fleet, self.kind, self.scope, self.label, self.force = fleet, kind, scope, label, force
        self.session, self.state, self.standing, self.cwd, self.machine, self.host = session, state, standing, cwd, machine, host
        self.herdr = herdr_in(session)
        self.ended, self.fresh = [], []

    def ensure(self):
        """Its state folder, with the session its panes are in (`where`): panes another session's ids name are set
        aside under the folder's `stale/` and said, since a pane id means nothing in another session, so nothing is
        taken for up that is another agent of this one (moved_said). A folder from before `where` is taken as this
        session's."""
        self.state.mkdir(parents=True, exist_ok=True)
        where = self.state / "where"
        was = where.read_text().strip() if where.exists() else ""
        why = moved_said(self.scope, was, self.session)
        if why:
            stale = self.state / "stale" / f"{was}-{int(time.time())}"
            stale.mkdir(parents=True, exist_ok=True)
            for f in ("panes", "layout"):
                if (self.state / f).exists():
                    os.replace(self.state / f, stale / f)
            print(f"{why}; set aside in {stale}", file=sys.stderr)
        if was != self.session:
            where.write_text(self.session + "\n")
        for f in ("panes", "layout"):
            (self.state / f).touch()

    def lines(self, f):
        p = self.state / f
        return [l.split() for l in (p.read_text().splitlines() if p.exists() else []) if l.strip()]

    def write(self, f, lines):
        p = self.state / f
        new = p.with_name(f"{f}.new")
        new.write_text("".join(" ".join(l) + "\n" for l in lines))
        os.replace(new, p)

    def get(self, f, key):
        return next((l[1] for l in self.lines(f) if l[0] == key and len(l) > 1), "")

    def put(self, f, key, value):
        self.write(f, [l for l in self.lines(f) if l[0] != key] + [[key, value]])

    def drop(self, f, key):
        self.write(f, [l for l in self.lines(f) if l[0] != key])

    def agent_of(self, role):
        return f"{self.scope}-{role}"

    def pane(self, role):
        return self.get("panes", role)

    def status(self, role, fresh=False):
        return self.herdr.status(self.pane(role), fresh)

    def down(self):
        """Whether it was taken down, and stays down through a restart until it is brought up (crew revive leaves it)."""
        return (self.state / "down").exists()

    def mark(self, down):
        (self.state / "down").touch() if down else (self.state / "down").unlink(missing_ok=True)

    def record(self, act, why, roles):
        """One entry for an act on its agents, naming each (record.1); none when it names none."""
        on = [f"agent/{self.agent_of(r)}" for r in roles]
        if on:
            import record as rec  # record imports this module
            rec.emit(self.label, act, on, why=why)

    def answer(self, *args, ids=()):
        """herdr's result for an act that answers with what it made; refused in herdr's words when it fails, or when an
        id of ids it names is missing or empty (herdr_made)."""
        r = self.herdr.run(*args)
        return herdr_made(args[0], args[1], r.returncode, r.stdout, r.stderr, f"in session {self.session}", ids)

    def workspace(self, label, cwd):
        """A new workspace, kept in the layout file: its first tab and its root pane. One herdr makes with no id is
        refused and kept nowhere, so no tab is later made in it."""
        made = self.answer("workspace", "create", "--cwd", cwd, "--label", label, "--no-focus", ids=[("workspace", "workspace_id")])
        self.put("layout", ws_key(label), made["workspace"]["workspace_id"])
        return made["tab"]["tab_id"], made["root_pane"]["pane_id"]

    def tab(self, workspace, label, cwd, role):
        """A tab of a workspace in the layout file, its one pane the role's."""
        made = self.answer("tab", "create", "--workspace", self.get("layout", ws_key(workspace)), "--cwd", cwd, "--label", label, "--no-focus")
        self.put("panes", role, made["root_pane"]["pane_id"])
        return made

    def first_tab(self, workspace, label, cwd, role):
        """A new workspace whose first tab, so named, holds the role's pane."""
        tab, pane = self.workspace(workspace, cwd)
        self.herdr.run("tab", "rename", tab, label)
        self.put("panes", role, pane)

    def split(self, pane, way, cwd):
        return self.answer("pane", "split", pane, "--direction", way, "--cwd", cwd, "--no-focus")["pane"]["pane_id"]

    def panes(self):
        """Each standing role's pane, opened when it is not there, a dead one closed first (mend): a main level's roles
        in this session one tab each in the <label> workspace, in MAIN_STANDING's order, the first opening the workspace
        when it is not there. A console's tabs are crew console up's."""
        self.mend(self.standing)
        for role in self.standing:
            if not self.herdr.live(self.pane(role)):
                self.opened(self.label, role, self.cwd, role)

    def mend(self, roles):
        """Each of the roles' panes that herdr lists but holds no terminal for (dead_said) closed and dropped from the
        panes file, said on standard error, so that what opens a role's pane when it is not there opens it again in its
        layout (teams.2); a pane an agent holds is never touched (read.4). One herdr does not close is refused."""
        for role in roles:
            pane = self.pane(role)
            why = dead_said(self.scope, role, self.herdr.item(pane), self.herdr.status(pane))
            if why:
                print(f"{why}; crew closes it and opens it again", file=sys.stderr)
                self.answer("pane", "close", pane)
                self.drop("panes", role)

    def opened(self, workspace, label, cwd, role, beside=""):
        """A role's pane opened where opens_at says, given the pane it shares its tab with (beside), if any: split to
        its right while it is open, else a tab of the workspace, so named, while any pane of the workspace the layout
        file keeps is there, else the first tab of a new one."""
        ws = self.get("layout", ws_key(workspace))
        stands = ws and any(p.get("workspace_id") == ws for p in self.herdr.listing("pane"))
        way, at = opens_at(beside if self.herdr.live(beside) else "", ws if stands else "")
        if way == "split":
            self.put("panes", role, self.split(at, "right", cwd))
        elif way == "tab":
            self.tab(workspace, label, cwd, role)
        else:
            self.first_tab(workspace, label, cwd, role)

    def stop(self, role, waits=False):
        """End a role's agent before anything else starts in its pane (teams.2): None once it is ended, or when none was
        up; else what crew says, refused while the agent works unless forced, or failed when it did not exit. waits says
        the agent's only background work is crew's own waits (hold.renew_ready), which its exit then ends: Claude Code's
        question at the exit (exit_asks) answered with its first option, Exit and stop tasks, so the exit never stops
        there (teams.19)."""
        pane = self.pane(role)
        st = self.herdr.status(pane)
        if st == "working" and not self.force:
            return working_said(self.agent_of(role))
        if not st:
            return None
        if self.herdr.run("agent", "prompt", pane, "/exit").returncode:
            self.herdr.run("pane", "send-keys", pane, "ctrl+c", "ctrl+c")
        asked = False
        for _ in range(30):
            if not self.herdr.status(pane, fresh=True):
                self.ended.append(role)
                return None
            if waits and not asked:
                r = self.herdr.run("pane", "read", pane, "--source", "visible", "--lines", "30")
                if r.returncode == 0 and exit_asks(r.stdout):
                    self.herdr.run("agent", "send-keys", pane, "enter")
                    asked = True
            nap(1)
        # Still running means anything started next would be typed into it as a message. Say so and leave it be.
        self.herdr.run("pane", "send-keys", pane, "ctrl+c", "ctrl+c")
        nap(2)
        if self.herdr.status(pane, fresh=True):
            return f"{self.agent_of(role)} did not exit (busy or waiting on the user); it was left running"
        self.ended.append(role)
        return None

    def exited(self, role, looks):
        """Whether a role's agent exits within looks five seconds apart, read from herdr afresh at each, as stop reads
        it: the exit a stop's keys set going after the stop gave up, which a restart for an update watches for
        (teams.19). Once herdr reads it gone it is one this command ended. Nothing is typed into its pane, so an agent
        that never goes runs on as it was (teams.2)."""
        pane = self.pane(role)
        for _ in range(looks):
            nap(5)
            if not self.herdr.status(pane, fresh=True):
                self.ended.append(role)
                return True
        return False

    def start(self, role, stage=None):
        """Start a role in its pane, fresh, or picking up its last conversation with "resume"
        (teams.2, teams.6): never over an agent still running. Its shell is cleared and moved to the folder the role
        runs in, which herdr keeps for the pane and Claude finds its conversation from; crew-role starts it there, it is
        given its name, and Claude's folder-trust question alone is answered for it, never the Bypass Permissions
        warning (teams.8). Nothing is started on a host crew hold holds (teams.19), nor in a pane herdr lists with no
        terminal behind it (dead_said): what opens
        a role's pane closes such a pane and opens it again (mend). Returns whether it started, said on standard error
        when not."""
        pane, name = self.pane(role), self.agent_of(role)
        h = held()
        if h:
            print(held_said(this_host(), h), file=sys.stderr)
            return False
        if self.herdr.status(pane):
            print(f"{name} is still running; not starting another over it", file=sys.stderr)
            return False
        dead = dead_said(self.scope, role, self.herdr.item(pane), None)
        if dead:
            print(f"{dead}; crew starts nothing in it", file=sys.stderr)
            return False
        try:
            l, session = resolve(self.fleet, self.scope, role, stage)
        except Refusal as e:
            print(e, file=sys.stderr)
            return False
        if stage == "resume" and not session:
            print(f"{l['name']} has no conversation to resume; starting it fresh", file=sys.stderr)
        # A Claude that died badly leaves the pane reporting mouse movement, which types escape codes into the shell
        # and into whatever is run next. Clear the line and switch the reporting off first.
        self.herdr.run("pane", "send-keys", pane, "ctrl+c")
        self.herdr.run("pane", "run", pane, "printf '\\033[?1000l\\033[?1002l\\033[?1003l\\033[?1006l\\033[?1015l\\033[?2004l'; clear")
        nap(1)
        self.herdr.run("pane", "run", pane, f"cd {shlex.quote(l['cwd'])} && bash {shlex.quote(str(HOME / 'plugin/bin/crew-role'))} "
                                            f"{self.scope} {role}" + (f" {stage}" if stage else ""))
        if not self.give_name(pane, name):
            return False
        for _ in range(15):
            nap(2)
            r = self.herdr.run("pane", "read", pane, "--source", "visible", "--lines", "30")
            if r.returncode == 0 and "Yes, I trust this folder" in r.stdout:
                self.herdr.run("agent", "send-keys", pane, "down", "enter")
                nap(3)
                break
            if self.herdr.status(pane, fresh=True) == "idle":
                break
        if not (stage == "resume" and session):
            self.fresh.append(role)
        print(started_said(name, pane, stage))
        return True

    def give_name(self, pane, name):
        """herdr drops an agent's name whenever its session changes: the agent is given it, once it is up, within a minute."""
        for _ in range(60):
            if self.herdr.run("agent", "rename", pane, name).returncode == 0:
                return True
            nap(1)
        print(f"{name} did not come up in {pane}; look at that pane.", file=sys.stderr)
        return False

    def start_standing(self):
        """Each standing role started that is not up, said when one is: the roles started. One that can't start stops
        the command."""
        started = []
        for role in self.standing:
            if self.status(role):
                print(f"{self.agent_of(role)} is already up")
            else:
                if not self.start(role):
                    raise Stopped(1)
                started.append(role)
        return started

    def close_pane(self, role):
        pane = self.pane(role)
        if self.herdr.live(pane):
            self.herdr.run("pane", "close", pane)
        self.drop("panes", role)

    def teardown(self):
        """Every agent of its panes file ended, each pane closed and each workspace of its layout closed. An agent that
        could not be ended is said and left."""
        for role, *_ in self.lines("panes"):
            why = self.stop(role)
            if why:
                print(why, file=sys.stderr)
        for _, pane, *_ in self.lines("panes"):
            if self.herdr.live(pane):
                self.herdr.run("pane", "close", pane)
        for key, ws, *_ in self.lines("layout"):
            if key.startswith("ws:"):
                self.herdr.run("workspace", "close", ws)
        self.write("panes", [])
        self.write("layout", [])


def main_sessions(p):
    """A main level's sessions, the main level's own first, each with its standing roles in MAIN_STANDING's order. A
    role its partition runs as its kind stands in none (design Decision 14), but the session it stood in is still one,
    so a standing agent of it left there is ended."""
    by = {}
    for role in MAIN_STANDING:
        by.setdefault(role_session(p, role), []).extend([role] if p["flume"][role] is False else [])
    return [(s, tuple(by[s])) for s in sorted(by, key=lambda s: (s != p["session"], s))]


def main_state(label, p, session):
    """A main level's state folder in one of its sessions: <label>-main for the main level's own session, as it has
    always been, and <label>-main-<session> for a session its partition names for a role apart."""
    return pathlib.Path.home() / ".local/state/crew" / (f"{label}-main" if session == p["session"] else f"{label}-main-{session}")


def mains(fleet, label, force=False):
    """A partition's main level as the Agents of each of its sessions (record 0035): the main level's own first, then
    each session its partition names for a role apart, each with the roles standing there."""
    p = partition_of(fleet, label)
    return [Agents(fleet, "main", label, label, s, main_state(label, p, s), roles, p["checkout"], p["machine"], force=force)
            for s, roles in main_sessions(p)]


def main_holding(fleet, label, role, force=False):
    """The Agents of the main level's session a role runs in: the reviewer's is its own session's, beside the planner
    unless named apart, which need hold no standing role."""
    p = partition_of(fleet, label)
    s = role_session(p, role)
    held = next((m for m in mains(fleet, label, force) if m.session == s), None)
    return held or Agents(fleet, "main", label, label, s, main_state(label, p, s), (), p["checkout"], p["machine"], force=force)


def standing(fleet, kind, label, force=False):
    """The partition's console on this host (console), as the Agents of its session here: its state folder, standing
    roles and the folder it runs in. A main level is mains."""
    host = this_host()
    state = pathlib.Path.home() / f".local/state/crew/{label}-{kind}"
    kind == "console" or fail(f"crew.standing: no kind {kind}")
    sess = operator_session(fleet, label, host)
    return Agents(fleet, "console", label, label, label, state, (), sess["dir"], host, host, force)


def main(a):
    fleet = load()
    if a[:1] == ["labels"]:
        print("\n".join(fleet["partitions"]))
    elif a[:1] == ["brief"] and len(a) >= 3:
        sys.stdout.write(brief(fleet, a[1], a[2], a[3] if len(a) > 3 else ""))
    elif a[:1] == ["launch"] and len(a) >= 3:
        print(launch_shell(fleet, a[1], a[2], a[3] if len(a) > 3 else None))
    elif a == ["tell", "--board"]:
        sys.exit(0 if board_tell(fleet, sys.stdin.read()) else 1)
    elif a[:1] == ["tell"] and len(a) in (3, 4) and a[3:] in ([], ["--taken"]):
        import record as rec  # record imports this module
        sys.exit(0 if tell(fleet, a[1], a[2], sender=rec.who(), taken=a[3:] == ["--taken"]) else 1)
    elif a[:1] == ["send"] and len(a) == 3:
        sys.exit(0 if send(fleet, a[1], a[2]) else 1)
    elif a[:1] == ["found"] and len(a) == 2:
        print(json.dumps(found_here(fleet, a[1])))
    elif a == ["run-name"]:
        print(run_exports(run_of(fleet, os.environ.get("FLUME_PLACE"))))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
