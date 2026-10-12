#!/usr/bin/env python3
"""crew.py: read the teams file and answer from it.

  crew.py teams                       every team's name
  crew.py labels                      every partition's label
  crew.py env <team>                  the team's settings as shell assignments
  crew.py brief <team|label> <definition> [name]
                                      a definition's brief for a team or a partition's main level; name is the agent's own
  crew.py launch <team|label> <role> [stage|resume]
                                      how crew-role starts the role, as shell assignments
  crew.py place <team|label> <role> [stage|resume]
                                      the folder the role runs in; with resume, the one its last conversation began in
  crew.py env-main|env-dispatch|env-operator <label>
                                      a main level's, this host's dispatcher's or operator agent's settings
  crew.py hosts <label>               the hosts where the partition's teams run: name, ssh name, crew there
  crew.py crew-at <host>              the crew command on a host
  crew.py tell <agent> "<text>" [--taken]
                                      prompt an agent wherever it runs, the text marked [crew tell from <sender>];
                                      refused, with nothing typed, while it waits on a question in its pane; with
                                      --taken, read back from its transcript and sent once more when not taken
  crew.py notice <agent> "<text>"     prompt an agent wherever it runs, the text marked [crew], as crew's own notice
  crew.py greet <team> [--first "<text>"]
                                      greet the team's conductor, marked [crew], once it is up and settled; the text,
                                      when given, opens the greeting
  crew.py greet-agent <agent> [--wait <seconds>]
                                      greet an agent crew starts outside a team, with its role's greeting, the same way
  crew.py here                        what runs on this host, one per line: team <name>, main <label>,
                                      dispatch <label> and operator <label>

Each role is an agent definition, roles/<role>.md: frontmatter naming its model and effort, which a team's or a
partition's `roles` in the teams file may override, and its brief as the body, with its {{TOKENS}} filled. Every token is built here from the team's
data; a token with no builder, or data a builder needs and the team lacks, is an error, never blank text."""
import collections, functools, itertools, json, os, pathlib, re, shlex, subprocess, sys, time

LIB = pathlib.Path(__file__).resolve().parent
HOME = LIB.parent.parent
HOSTS = pathlib.Path.home() / ".config/swancloud/herdr-hosts.json"
TEAMS = pathlib.Path.home() / ".config/crew/teams.json"
VERSION = 2
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
# The roles a team's entry may override, and those a partition's entry may: each is a definition in roles/.
TEAM_ROLES = ("conductor", "ops", "construct", "coder", "verify")
MAIN_ROLES = ("design", "planner", "main-ops", "dispatcher", "operator", "reviewer")
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


def roles_of(entry, what, allowed):
    roles = entry.get("roles") or {}
    if not isinstance(roles, dict):
        fail(f"{what} in {TEAMS}: 'roles' must map a role to its model or effort")
    for role, o in roles.items():
        if role not in allowed:
            fail(f"{what} in {TEAMS} overrides role '{role}', which it has no definition for. roles: " + " ".join(allowed))
        if not isinstance(o, dict) or not o or set(o) - {"model", "effort"}:
            fail(f"{what} in {TEAMS}: roles.{role} sets only 'model' or 'effort', not {json.dumps(o)}")
        if "effort" in o and o["effort"] not in EFFORTS:
            fail(f"{what} in {TEAMS}: roles.{role}.effort is '{o['effort']}', which is no effort level. levels: " + " ".join(EFFORTS))
        if "model" in o and (not isinstance(o["model"], str) or not o["model"]):
            fail(f"{what} in {TEAMS}: roles.{role}.model must name a model")
    return roles


@functools.lru_cache(maxsize=None)
def load():
    """The partitions and teams, written by the machine's own configuration (swancloud's lib/crew-teams.nix),
    never by crew. Every entry is checked here, against the hosts file, before any is used, once a process: a later
    call is answered with the same fleet."""
    if not TEAMS.exists():
        fail(f"{TEAMS} is missing; the machine's configuration writes it")
    data = json.loads(TEAMS.read_text())
    if data.get("version") != VERSION:
        fail(f"{TEAMS} is version {data.get('version')}, and crew reads only version {VERSION}. It must be regenerated "
             f"by the machine's configuration (swancloud's lib/crew-teams.nix); crew has done nothing.")
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
        parts[label] = dict(p, label=label, partition=name, ssh=host["ssh"], dir=sess["dir"], checkout=checkout(sess, blueprints[0]),
                            roles=roles_of(p, what, MAIN_ROLES), teams=[])
    by_name = {p["partition"]: p for p in parts.values()}
    teams = {}
    for t in data.get("teams") or []:
        name = need(t, "a team", "name", str)
        what = f"team {name}"
        NAME.match(name) or fail(f"{what}: a team's name is lowercase words with dashes")
        name not in teams or fail(f"{TEAMS} lists team {name} twice")
        name not in parts or fail(f"{what} has the name of a partition's label")
        system, machine, session = (need(t, what, f, str) for f in ("system", "machine", "session"))
        units = need(t, what, "units", int)
        units > 0 or fail(f"{what}: 'units' must be at least 1")
        repos = need(t, what, "repos", list)
        if len(repos) != 2 or not all(isinstance(r, str) and "/" not in r for r in repos):
            fail(f"{what}: 'repos' is two names, its kit then its partition's blueprints repo, not {json.dumps(repos)}")
        for gone in ("coders", "base"):
            gone not in t or fail(f"{what} in {TEAMS} still has '{gone}', which version {VERSION} has no place for")
        host, sess = session_of(hosts, what, machine, session)
        pname = sess.get("partition") or fail(f"{what} runs in {machine}'s session {session}, which {HOSTS} puts in no partition")
        part = by_name.get(pname) or fail(f"{what} runs in {machine}'s session {session}, of partition {pname}, which {TEAMS} does not list")
        kit, bp = (repo_in(sess, what, machine, session, r) for r in repos)
        if bp not in part["blueprints"]:
            fail(f"{what} names {bp} as its blueprints repo, which is not one of {pname}'s: " + " ".join(part["blueprints"]))
        kname = kit.split("/")[-1]
        teams[name] = dict(t, name=name, system=system, machine=machine, session=session, units=units, label=part["label"],
                           partition=pname, ssh=host["ssh"], kind=host.get("kind", ""), dir=sess["dir"], roles=roles_of(t, what, TEAM_ROLES),
                           kit={"name": kname, "repo": kit, "dir": f"{sess['dir']}/{kname}", "main": checkout(sess, kit)},
                           blueprints={"name": bp.split("/")[-1], "repo": bp, "main": checkout(sess, bp)})
        part["teams"].append(name)
    return {"hosts": hosts, "partitions": parts, "teams": teams}


def team_of(fleet, name):
    return fleet["teams"].get(name) or fail(f"no team '{name}'. teams: " + " ".join(fleet["teams"]))


def partition_of(fleet, label):
    return fleet["partitions"].get(label) or fail(f"no partition '{label}'. partitions: " + " ".join(fleet["partitions"]))


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


def team_of_agent(fleet, name):
    """The team an agent crew starts belongs to, from its name alone: its conductor, ops or a unit slot; else None."""
    for t in fleet["teams"].values():
        if name in (f"{t['name']}-conductor", f"{t['name']}-ops") or re.match(rf"^{re.escape(t['name'])}-unit-[1-9][0-9]*$", name):
            return t
    return None


def place_of_agent(fleet, name):
    """The host and herdr session an agent crew starts runs in, from its name alone."""
    t = team_of_agent(fleet, name)
    if t:
        return t["machine"], t["session"]
    for p in fleet["partitions"].values():
        l = p["label"]
        if name in (f"{l}-design", f"{l}-planner", f"{l}-ops", f"{l}-reviewer"):
            return p["machine"], p["session"]
        m = re.match(rf"^{re.escape(l)}-dispatch-(.+)$", name)
        if m:
            return m.group(1), dispatch_place(fleet, l, m.group(1))
        m = re.match(rf"^{re.escape(l)}-operator-(.+)$", name)
        if m:
            operator_session(fleet, l, m.group(1))
            return m.group(1), l
    fail(f"no agent {name}: crew starts none by that name")


def label_of_agent(fleet, name):
    """The partition an agent crew starts works for, from its name alone."""
    t = team_of_agent(fleet, name)
    if t:
        return t["label"]
    for l in fleet["partitions"]:
        if name in (f"{l}-design", f"{l}-planner", f"{l}-ops", f"{l}-reviewer") or re.match(rf"^{re.escape(l)}-(dispatch|operator)-.+$", name):
            return l
    return None


def tell(fleet, name, text, record=True, sender=None, taken=False, what="its prompt", again=""):
    """Send an agent a prompt wherever it runs, marked as crew's: `[crew tell from <sender>]` for what crew tell
    carries for someone, `[crew]` for crew's own greetings and notices, so the recipient, and crew reading its
    transcript, never take it for the user's typing. A tell reaches its agent as a prompt or not at all (teams.11):
    an agent that is not up, one waiting on a question in its pane, and one crew can't read that of is reported, with
    nothing typed, and the tell fails. With taken, the text is taken or sent again (send_taken), and a sending not
    taken fails the tell, saying so of what was sent, with again, what to do once it is ready, when it was never
    taken. A tell is in the run record of the recipient's partition, with its length and never its text."""
    host, session = place_of_agent(fleet, name)
    why = tell_refusal(name, host, *waits_on_question(fleet, name))
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


def tell_refusal(name, host, status, asking, unread):
    """Why a tell types nothing (teams.11), from what crew read of the agent: what it could not read, the agent not
    up, or waiting on a question in its pane; None when the tell may be typed."""
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
    (None, what could not be read) when its host does not answer or herdr's answer can't be read. On this host, with
    fresh False, it is answered from its session's listing as this command read it (Herdr)."""
    host, session = place_of_agent(fleet, name)
    if host == this_host():
        try:
            return herdr_in(session).agent(name, fresh), None
        except Refusal as e:
            return None, str(e)
    r = on_machine(fleet, host, ["herdr", "--session", session, "agent", "get", name])
    if r.returncode:
        return None, unanswered(host, r)
    try:
        a = json.loads(r.stdout)["result"]["agent"]
    except (ValueError, KeyError, TypeError):
        a = None
    return (a, None) if isinstance(a, dict) else (None, f"herdr's answer on {host} about it can't be read")


def agent_get(fleet, name, fresh=True):
    """An agent crew starts, as herdr answers wherever it runs, or None when it is not up."""
    return read_agent(fleet, name, fresh)[0]


def agent_status(fleet, name, fresh=True):
    """An agent crew starts, as herdr sees it wherever it runs: idle, done, working, blocked, or None when it is not up.
    With fresh False, an agent on this host is answered from its session's listing as this command last read it."""
    a = agent_get(fleet, name, fresh)
    return a.get("agent_status") if a else None


# What each herdr command a crew command runs leaves to read again in its session: the agents (`agent list`), the panes
# (`pane list`), both, or neither. A command not named here leaves both.
STALE = {("agent", "list"): "", ("agent", "get"): "", ("agent", "read"): "", ("pane", "list"): "", ("pane", "get"): "",
         ("pane", "read"): "", ("workspace", "list"): "", ("workspace", "get"): "", ("tab", "list"): "", ("tab", "get"): "",
         ("tab", "rename"): "", ("workspace", "create"): "pane", ("tab", "create"): "pane", ("pane", "split"): "pane",
         ("pane", "run"): "agent", ("pane", "send-keys"): "agent", ("agent", "prompt"): "agent", ("agent", "send-keys"): "agent",
         ("agent", "rename"): "agent"}


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

    def live(self, pane):
        """Whether the pane is there."""
        return bool(pane) and any(p.get("pane_id") == pane for p in self.listing("pane"))


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


_SESSIONS = {}


def herdr_in(session):
    """This command's Herdr of a session on this host."""
    return _SESSIONS.setdefault(session, Herdr(session))


def waits_on_question(fleet, name):
    """Whether an agent crew starts waits on a question in its pane, as a tell and a greeting read it: (herdr's status
    of it, None when it is not up; whether it waits; what crew could not read to know, or None). It waits when herdr
    reports it blocked, or when the mark crew's hook left as it opened a question or a plan for the user
    (hooks/questions) is still open in its session, read by questions.py on its host. Either is enough: herdr reads
    the dialog from the screen alone, and on 2026-10-07 took a tell into one it did not see. A host with no mark, such
    as an agent started before the hook, reads as no question open, and herdr's reading alone guards it (the
    a-tell-never-lands-in-a-question design, decision 5, departing from read.1)."""
    status, asking, sid, unread = agent_reading(fleet, name)
    if status not in (None, "blocked") and not sid and not unread:
        unread = "herdr names no session for it"
    return status, asking, unread


def agent_reading(fleet, name):
    """What waits_on_question reads of an agent, with its session: (herdr's status of it, None when it is not up;
    whether it waits on a question in its pane; the Claude session herdr names for it, or None; what crew could not
    read, or None). Whether it waits is read from crew's own mark only when herdr names its session."""
    host, _ = place_of_agent(fleet, name)
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
        return status, False, None, None
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
    process: questions <session>, or transcript end <session> | received <session> <offset> <text>."""
    if what == "questions":
        import questions
        return questions.read(*args)
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


def never_started(agent, stage, what, obj, team, how, why):
    """What crew says of a stage whose prompt its agent never took, sent twice or never ready (how "never"), or of one
    crew could not tell it took (teams.15, read.1): the stage never started, nothing is left typed, and how to run it
    again, by the unit's or the fix's own command."""
    name = obj.rsplit("/", 1)[-1]
    again = (f"crew unit run {what} {stage}" if obj.startswith("unit/") else f"crew fix {team} {name} --merge" if stage == "merge"
             else f'crew fix {team} {name} "<what is wrong>"')
    if how == "never":
        return f"{agent} never took its {stage} prompt for {what}, {why}; the stage never started and nothing is left typed in its pane: run it again with {again}"
    return (f"crew could not tell whether {agent} took its {stage} prompt for {what}: {why}; nothing more was sent, and the stage is "
            f"taken as never started: run it again with {again}")


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
    question in its pane, and herdr names its session. Returns (its session id, None), or (None, ("never", why)) when
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
                          if asking else "as herdr named no session for it" if not sid else f"as herdr still reported it {status}")
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


GREETING = ("Read where your bolt stands with `crew bolts`, tell me in a few lines, then carry on with it: "
            "start each stage that is ready.")

# The greeting of each agent crew starts outside a team, by role: the reads its brief already teaches, and what is its own.
GREETINGS = {
    "design": ("Read where {label} stands with `crew bolts` and `crew rail`, and the signals waiting for curation, tell me in "
               "a few lines, then carry on with what is yours: curate the signals that have no move."),
    "planner": ("Read where {label} stands with `crew bolts` and `crew plan proposed`, tell me in a few lines, then carry on "
                "with what is yours: plan what is queued and see each open proposal through."),
    "ops": ("Read where {label} stands with `crew bolts` and `crew rail`, tell me in a few lines, then carry on with what is "
            "yours: a bolt lands only on the user's word, so land nothing until it comes."),
    "dispatch": ("Read where {label} stands on {host} with `crew bolts` and `crew status` for each team here, tell me in a few "
                 "lines, then carry on with what is yours: give each team here that holds no bolt its next one."),
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


def greet(fleet, team, first="", wait=90):
    """Get a team's conductor going: tell it to read where its bolt stands and carry on."""
    t = team_of(fleet, team)
    name = f"{t['name']}-conductor"
    return greet_agent(fleet, name, first + GREETING, [f"agent/{name}", f"team/{t['name']}"], t["label"],
                       f"team({t['name']}): greet {name}", f"crew up {t['name']} starts and greets it", wait)


def greet_standing(fleet, name, wait=90):
    """Get an agent crew starts outside a team going (a main level's design agent, planner or ops, a dispatcher, an
    operator agent): tell it to read where its partition stands and carry on with what is its role's. A team's agent,
    or a name crew starts no agent by, is refused."""
    label, text, why, hint = standing_greeting(fleet, name)
    return greet_agent(fleet, name, text, [f"agent/{name}"], label, why, hint, wait)


def standing_greeting(fleet, name):
    """The greeting of an agent crew starts outside a team, by its role, read from its name alone: its partition, the
    text, the greet entry's why, and how it is started when it is not up. A team's agent, the reviewer, sent its batch
    as its prompt, and a name crew starts no agent by are refused."""
    t = team_of_agent(fleet, name)
    t is None or fail(f"{name} is one of team {t['name']}'s agents, not one crew starts outside a team; "
                      f"crew up {t['name']} greets its conductor")
    label = label_of_agent(fleet, name) or fail(f"no agent {name}: crew starts none by that name")
    host, _ = place_of_agent(fleet, name)
    role = name[len(label) + 1:]  # design, planner, ops, reviewer, dispatch-<host> or operator-<host>
    role != "reviewer" or fail(f"{name} is sent its batch as its prompt by crew review, and is not greeted")
    role = role if role in GREETINGS else role.split("-")[0]
    kind, up = ("operator", f"crew operator up {label}") if role == "operator" else ("main", f"crew main up {label}")
    return label, GREETINGS[role].format(label=label, host=host), f"{kind}({label}): greet {name}", f"{up} starts and greets it"


def kept_on(fleet, host, repo):
    """The main checkout of a repo (owner/name) on a host: the first of the host's sessions whose space keeps it."""
    for sess in fleet["hosts"].get(host, {}).get("sessions", {}).values():
        if repo in (sess.get("repos") or []):
            return checkout(sess, repo)
    return None


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
    return ["env", f"CREW_AGENT={rec.who()}", f"CREW_LABEL={os.environ.get('CREW_LABEL', '')}",
            f"CREW_SESSION={rec.session() or ''}", "bash", crew_at(fleet, host), *args]


def partition_hosts(fleet, label):
    """The hosts where a partition's teams run, each once, by name."""
    return sorted({fleet["teams"][t]["machine"] for t in partition_of(fleet, label)["teams"]})


def dispatch_place(fleet, label, host):
    """A dispatcher runs in the main level's session when that is on the host, else in the session of the
    host's first team of the partition by name."""
    p = partition_of(fleet, label)
    if p["machine"] == host:
        return p["session"]
    here = sorted(t for t in p["teams"] if fleet["teams"][t]["machine"] == host)
    here or fail(f"no team of {label} runs on {host}, so {host} has no dispatcher. hosts: " + " ".join(partition_hosts(fleet, label)))
    return fleet["teams"][here[0]]["session"]


def kits_on(fleet, label, host):
    """The main checkouts on a host of the kits the partition's teams build, each once."""
    out = []
    for t in sorted(partition_of(fleet, label)["teams"]):
        c = kept_on(fleet, host, fleet["teams"][t]["kit"]["repo"])
        if c and c not in out:
            out.append(c)
    return out


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


def slot_of(t, slot):
    """What a unit slot holds, from the team's state on its host: kind (unit or fix), name, and its place."""
    path = pathlib.Path.home() / f".local/state/{t['name']}-team/slots"
    for line in (path.read_text().splitlines() if path.exists() else []):
        f = line.split()
        if f and f[0] == slot:
            return {"kind": f[1], "name": f[2], "place": f[3]}
    fail(f"{t['name']}-{slot} holds no unit or fix")


def bolt_place(t):
    """The worktree of the bolt a team holds, from the plan, where its conductor and ops start; None when it holds
    none. A plan that can't be read is reported, and the role starts in the kit's main checkout."""
    import argparse, contextlib, io
    import crew as this, plan  # read in this process, as plan.py _bolt-of reads it; plan imports this module by name
    said = io.StringIO()
    try:
        with contextlib.redirect_stdout(said):
            plan.bolt_of_team(this.load(), argparse.Namespace(team=t["name"]))
    except this.Refusal as e:
        why = str(e).strip()
        if "holds no bolt" not in why:
            print(f"{t['name']}'s bolt could not be read ({why}); starting in {t['kit']['main']}", file=sys.stderr)
        return None
    bolt = said.getvalue().strip().partition("=")[2].strip("'\"")
    path = f"{t['kit']['dir']}/bolts/{bolt}"
    return path if bolt and pathlib.Path(path).is_dir() else None


# A unit's stages and the definition each is started from.
STAGES = {"construct": "construct", "code": "coder", "verify": "verify", "settle": "coder", "merge": "coder", "fix": "coder"}
def launch(fleet, scope, role, extra=None):
    """How crew-role starts a role: its folder, agent name, partition, the definition it comes from, the
    folders it may also reach, and the model and effort after the teams file's override."""
    if scope in fleet["teams"]:
        t = fleet["teams"][scope]
        label, roles, kit, bp = t["label"], t["roles"], t["kit"], t["blueprints"]
        if role in ("conductor", "ops"):
            spec = dict(defn=role, name=f"{t['name']}-{role}", cwd=bolt_place(t) or kit["main"], dirs=[kit["dir"], bp["main"]])
        elif re.match(r"^unit-[1-9][0-9]*$", role):
            int(role[5:]) <= t["units"] or fail(f"{t['name']} has {t['units']} unit slots, so no {role}")
            extra in STAGES or fail(f"{t['name']}-{role}: which stage? stages: " + " ".join(STAGES))
            held = slot_of(t, role)
            spec = dict(defn=STAGES[extra], name=f"{t['name']}-{role}", cwd=held["place"], dirs=[kit["main"], bp["main"]])
        else:
            fail(f"no role '{role}' on team {t['name']}. roles: conductor ops unit-<n>")
    else:
        p = partition_of(fleet, scope)
        label, roles, host = p["label"], p["roles"], this_host()
        main = dict(cwd=p["checkout"], dirs=[d for d in blueprints_on(fleet, label, p["machine"])[1:] + kits_on(fleet, label, p["machine"])])
        if role in ("design", "planner", "ops", "reviewer"):
            spec = dict(main, defn="main-ops" if role == "ops" else role, name=f"{label}-{role}")
        elif role == "dispatcher":
            dispatch_place(fleet, label, host)
            bps = blueprints_on(fleet, label, host)
            spec = dict(defn="dispatcher", name=f"{label}-dispatch-{host}", cwd=bps[0] if bps else fleet["hosts"][host]["sessions"][dispatch_place(fleet, label, host)]["dir"],
                        dirs=bps[1:] + kits_on(fleet, label, host))
        elif role == "operator":
            sess = operator_session(fleet, label, host)
            spec = dict(defn="operator", name=f"{label}-operator-{host}", cwd=sess["dir"], dirs=[])
        else:
            fail(f"no role '{role}' at {label}'s main level. roles: design planner ops reviewer dispatcher operator")
    meta, _ = definition(spec["defn"])
    o = roles.get(spec["defn"], {})
    return dict(spec, label=label, model=o.get("model", meta["model"]), effort=o.get("effort", meta["effort"]))


def operator_session(fleet, label, host):
    """The operator session of a partition on a host is the session named after its label there."""
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


def env(fleet, t):
    pairs = {
        "TEAM": t["name"], "SYSTEM": t["system"], "MACHINE": t["machine"], "SSH_TARGET": t["ssh"], "SESSION": t["session"],
        "LABEL": t["label"], "CREW_HOME": str(HOME), "KIT": t["kit"]["main"], "KIT_DIR": t["kit"]["dir"], "KIT_NAME": t["kit"]["name"],
        "BLUEPRINTS": t["blueprints"]["main"], "UNITS": str(t["units"]), "HOST_KIND": t.get("kind", ""), **reach(fleet, t["machine"]),
    }
    return "\n".join(f"{k}={shlex.quote(v)}" for k, v in pairs.items()) + f'\nSTATE="$HOME/.local/state/{t["name"]}-team"'


# How an agent records a finding, the same in every brief that records one.
def signal_how(cmd, label, state):
    return (f"`{cmd} signal <slug> \"<what it asserts, in a sentence>\" --excerpt \"<the exact words the user said or the tool "
            f"printed>\" --kind constraint|ask|question|commitment|reaction`. Copy the excerpt, never reword it: crew looks for it "
            f"in your own session's transcript, and a refusal means the words were reworded. When the words point at something "
            "made elsewhere, such as another conversation, a page or prototype, an artifact, files in another repo or a spike, "
            "find it and name in the sentence where it lives, in a form another agent can open: `<owner>/<repo>:<path>`, a "
            "branch, an artifact's link. A conversation's id alone is not enough: name what it made. crew writes the signal under "
            f"`signals/` on `{label}/main` of {state}.")


# How a stage's agent, or ops during a proof, stops short, the same in every brief that runs a stage: work is "stage"
# or "proof".
def needs_how(cmd, work):
    return (f"When you cannot finish without something only someone else can give (a decision, a fact about a live system, "
            f"the user's word), run `{cmd} needs \"<what you tried and what you need>\"` and end your turn. Post no Pending "
            "You card and make no area: your team's cards are its conductor's, and crew refuses any other. crew ends your "
            f"{work} there and gives your words to the conductor, who gets the answer and starts the {work} again with it. "
            "Never ask in your pane: nobody watches it. Ending a turn to wait on something you started in the background is "
            f"fine: crew knows your {work} is over only when what it delivers is there.")


# What an agent does with a row's card Pending You no longer finds for it, the same in every brief that cards a row: the
# card discipline below, and main-level ops's for its operations rows.
def lost_card_how(cmd, label):
    return ("A card of yours is lost when it reads \"not found\" to you in Pending You: the host signed in to Pending You "
            "again, and the card stayed with the old sign-in, where the user may still see it and answer it, to nobody. "
            "At your start, and whenever Pending You has you call `whoami` again, ask Pending You with `get_request` for "
            f"each card the `card:` line of `{cmd} rail --label {label}` shows open under a row of yours, by the id it "
            "names; and any Pending You tool that answers \"not found\" for a card of yours has found a lost one. While its "
            "row still waits, post the row's card again under the row's key, in its row's form and with the words it "
            "always carries, and put in its summary, right after the link and the bolt where it has them, these words: "
            "\"An older copy of this card is dead: it can no longer be answered, so dismiss it in the app. Answer this "
            f"one.\" A card that links a plannotator session keeps the row's: `{cmd} card session <key> --label {label}` "
            "gives back the running link. This is the one time you post again under a key you have posted under before. "
            "A lost card whose row is gone is posted again by nobody, and there is nothing more to do with it.")


# How an agent keeps one Pending You card for each rail row it owns, the same in the planner's brief and the conductor's.
def cards_how(cmd, label, kits):
    return ("When your session has Pending You's tools, every decision of yours the rail lists gets one card, and only those. "
            "crew refuses a card you post under any key but a rail row's of your own, and an area under any key but "
            "`create-area:<owner>/<kit>`, and its refusal names the key to use. A question you ask in your pane gets no card. Take the row's card key from the `card:` line under its row in "
            f"`{cmd} rail --label {label}`, and post the card with that key as its `idempotencyKey`. That way a retry never "
            "makes a second card, and the rail knows the card is the row's. A row's key changes when what it asks changes: "
            "a verify report written again, or a bolt a fix moved. Then close the card you hold under the old key with what changed, "
            "unless it is already closed on its answer, and post a new card under the new key when the row asks again. Never "
            "post again under a key whose card was answered: Pending You gives that card back, and the user is not asked. "
            "The one exception is a lost card, which Pending You no longer finds, as the next paragraph says. "
            "At your start, call `whoami` with your crew name "
            "and one line on your role. Then call `list_pending` with that name, and act on any card the user has answered. "
            "Post a card for any row of yours that has none open. Ask every card in your crew name, with this host as the "
            "session's machine and your worktree as its folder. File it in the area of its kit, found with `match_area` from "
            "the kit's git remote. When there is none, create it with `create_area`, named for the kit, in the group "
            f"`{label}`, with the key `create-area:<owner>/<kit>`. Never make a group: if `{label}` isn't one of the user's "
            "groups, the area is left ungrouped, and you say so once. Title it with what you ask and its bolt, give it the "
            "form its row takes, as your brief says, with `blocking` false: crew refuses a row's card in another form, and "
            "names the form to use. Its words are as the paragraph after next says. You hear an answer "
            "by being woken in your pane. Never run `npx pendingyou` or `pendingyou hold`: the `pendingyou` on the path is the "
            "fleet's, and the wake needs neither. Act on the user's answer as if they had said it in your pane, then close the "
            "card with `ack_answer` and a one-line outcome. When crew tells you, or prints, to close the card for a row, close "
            "it with `cancel_request` and the reason, or with `ack_answer` when you acted on its answer. Only your own cards "
            f"are yours: leave every other card alone. The kits: {kits}.\n\n"
            f"{lost_card_how(cmd, label)}\n\n"
            "A card says what the user decides from, so they decide without opening anything. When it asks them to read "
            "something, it says it in the document's own words, cut by whole sentences and whole items, never reworded into "
            "a summary of yours. Its summary, the part Pending You shows first, begins with the link to the card's "
            "plannotator session, then names the bolt, then holds the document's opening sentences, as many whole ones as "
            "fit in Pending You's 400 characters. Its background begins with the same link, then holds the document's words "
            "for the card's kind: for a change, its Why as the proposal words it, then \"What it changes:\" and a line for "
            "each of its What Changes items, that item's lead sentence as written; for a "
            "report, a line for each finding, its severity and what it found in the report's words, then what you would do "
            f"about it. A proposal's card is what `{cmd} plan card <n> --label {label}` prints, its words, its picture and its "
            "text crew's own, and it links no session but when that says so. "
            "A landing card has nothing to read: it names its bolt and carries no link. No card carries a path, "
            "of a file, a folder or a report: none in its title, summary, background, trace, links or tried, no artifact of "
            "kind `path` or `file`, and an empty list as its files touched. Name a unit, a proposal or a report by its name; "
            "the link is how the user reaches it.\n\n"
            "A card carries an artifact only for a picture it needs or a document's substance it shows, so the user sees "
            f"each as it is; a proposal's card carries the picture and the text `{cmd} plan card` gives it. An image, a screenshot or a page image, is an artifact of kind `image` with `upload: true`, the "
            "file's name as its ref, never its path; the post returns an upload URL for it, and you put the file there with "
            "its content type, `curl -fsS -X PUT -H \"Content-Type: image/png\" --data-binary @<file> \"<url>\"` for a PNG. "
            "Never attach an image as kind `path`: the user sees only the path. A document's substance beyond the card's "
            "words is inline Markdown, an artifact of kind `code` with lang `markdown` and the text as its lines, never an "
            "uploaded file and never HTML, which Pending You shows as nothing or refuses. The whole document is reached "
            "through the card's plannotator link, never attached.\n\n"
            "A card that asks the user to read something, a batch's changes or a verify report, links a plannotator "
            "session on it, so the user can read and annotate it wherever they answer the card. A proposal's card links no "
            "session, since it holds the proposal whole, but for one of more than fifteen new units, whose card "
            f"`{cmd} plan card` says links its session, on the proposal's page. Before you post it, run "
            f"`{cmd} card session <key> --label {label}` with the row's card key, for a batch card `batch/<n>`, one session on "
            "the whole batch: crew starts the session without opening a browser, a batch's on the main level's host, and "
            "prints its link. Put that link first in the card's summary and in its background, as above, and as the card's "
            "one entry in its links, labelled \"Read and annotate it in plannotator\"; a batch card's summary says first "
            "what it is, and its link opens its background and is labelled as the planner's brief has it. The link is no "
            "artifact. When a "
            "card's link changes, update its summary, background and links together, with the `changeNote` \"New plannotator "
            f"link\". Then run `{cmd} card wait <key> --label {label}` as a background command. Its end is the user's answer "
            "in the session: "
            "approved is the card's approval, with any notes as the user's words; annotated is a note asking for changes, in "
            "the user's words as they wrote them; closed or ended with no decision leaves the card the user's to answer, so "
            "run the session again, update the card if its link changed, and wait again. When you have acted on a decision "
            "made in the session, withdraw the card with `cancel_request`, `answeredHere` true, and the reason that it was "
            "answered in its plannotator session. A batch card's session holds the batch's notes, so a decision in it is never "
            "the card's answer: the card stays open until the user sends it, as the planner's brief says. A wait that says "
            "crew ended the session means its card is closed, and "
            "nothing is left to do. At your start, for each of your open cards that links a session, run the session and the "
            "wait again: the session gives back the running link, or starts a new one, which you put on the card as a changed "
            "link. Never open a browser for a card, and "
            "never run `plannotator` yourself for one: crew starts the card's session, and ends it when you close the card.")


def kits_named(kits):
    """Kits as the card discipline names them, <name>: <owner>/<repo>."""
    return "; ".join(f"{k['name']}: {k['repo']}" for k in sorted(kits, key=lambda k: k["name"])) or "none yet"


# Who is speaking in an agent's pane, beside every brief's roster.
SENDERS = ("A message in your pane that begins `[crew tell from <name>]` was sent with crew tell by that agent, or by "
           "the user when the name is `<user>@<host>`; one that begins `[crew]` is crew's own; anything else typed there "
           "is the user.")

# How an agent reports results, the same in every brief that reports them.
RESULTS = ("## Test, check and proof results\n\n"
           "Whenever you report how tests, checks or proofs went (a suite you ran, a merge's checks, the bolt's verification, "
           "an `openspec validate`, a verify's checks, each item of a Proof in dev list), list them first, before any prose, "
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


def team_tokens(fleet, t, role, self_name):
    kit, bp, n, label = t["kit"], t["blueprints"], t["name"], t["label"]
    p = fleet["partitions"][label]
    slots = [f"`{n}-unit-{i}`" for i in range(1, t["units"] + 1)]
    tok = {
        "SELF": self_name or {"conductor": f"{n}-conductor", "ops": f"{n}-ops"}.get(role, f"{n}-unit-<n>"),
        "OPERATORS": ", ".join(f"`{label}-operator-{h}`" for h, v in sorted(fleet["hosts"].items()) if label in v.get("sessions", {})) or "none",
        "TEAM": n, "SYSTEM": t["system"], "LABEL": label, "KIT": kit["main"], "KIT_NAME": kit["name"], "KIT_DIR": kit["dir"],
        "BLUEPRINTS": bp["main"], "BLUEPRINTS_NAME": bp["name"], "BLUEPRINTS_REPO": bp["repo"], "SIGNALS_REPO": p["blueprints"][0], "STATE_REPO": p["state"],
        "CONDUCTOR": f"{n}-conductor", "OPS": f"{n}-ops", "UNITS": str(t["units"]), "SLOTS": ", ".join(slots),
        "TEAM_CMD": f"{HOME}/plugin/bin/crew", "DESIGN_AGENT": f"{label}-design", "PLANNER": f"{label}-planner",
        "MAIN_OPS": f"{label}-ops", "DISPATCHER": f"{label}-dispatch-{t['machine']}",
        "REPORTS": f"~/.local/state/{n}-team/reports", "SIGNAL": signal_how(f"{HOME}/plugin/bin/crew", label, p["state"]),
        "CARDS": cards_how(f"{HOME}/plugin/bin/crew", label, kits_named([kit])), "RESULTS": RESULTS,
        "NEEDS": needs_how(f"{HOME}/plugin/bin/crew", "proof" if role == "ops" else "stage"),
        "CREW": f"the `## Crew` section of {kit['name']}'s CLAUDE.md (`{kit['main']}/CLAUDE.md`)",
    }
    tok["ROSTER"] = (
        f"The team: `{n}-conductor` keeps the bolt's units moving through their stages and tells the user where the bolt stands; "
        f"`{n}-ops` does everything that touches a live system, the bolt's deploys and tests among it; and the unit slots "
        f"({', '.join(slots)}), each holding one unit or fix in flight, where every stage of it (construct, code, verify, settle, merge) "
        f"is a fresh agent in that unit's own worktree. Above the team, at {label}'s main level: `{label}-design`, the design agent, "
        f"answers design questions; `{label}-planner` plans the partition's bolts; `{label}-dispatch-{t['machine']}` gives this "
        f"host's teams their bolts; and `{label}-ops` lands a proven bolt on main. Agents outside the team are reached with "
        f"`{HOME}/plugin/bin/crew tell <agent> \"<text>\"`, wherever they run. {SENDERS}")
    return tok


def main_tokens(fleet, p, role, self_name):
    label, host, cmd = p["label"], this_host(), f"{HOME}/plugin/bin/crew"
    teams = [fleet["teams"][n] for n in sorted(p["teams"])]
    hosts = partition_hosts(fleet, label)
    here = [t for t in teams if t["machine"] == host]
    team_line = lambda t: (f"- `{t['name']}` builds {t['system']} in {t['kit']['name']}, from {t['blueprints']['repo']}'s plan, on "
                           f"{t['machine']} in session {t['session']} (account {fleet['hosts'][t['machine']]['sessions'][t['session']]['account']}), "
                           f"with {t['units']} unit slots; its conductor is `{t['name']}-conductor`")
    kits = sorted({t["kit"]["name"] for t in teams})
    names = {"design": f"{label}-design", "planner": f"{label}-planner", "main-ops": f"{label}-ops",
             "dispatcher": f"{label}-dispatch-{host}", "operator": f"{label}-operator-{host}", "reviewer": f"{label}-reviewer"}
    tok = {
        "SELF": self_name or names[role], "LABEL": label, "PARTITION": p["partition"], "HOST": host, "TEAM_CMD": cmd,
        "BLUEPRINTS_REPOS": ", ".join(f"`{b}`" for b in p["blueprints"]), "SIGNALS_REPO": p["blueprints"][0],
        "PLANS": f"`{label}/main` of {p['state']}", "STATE_REPO": p["state"], "SIGNAL": signal_how(cmd, label, p["state"]),
        "CARDS": cards_how(cmd, label, kits_named({t["kit"]["repo"]: t["kit"] for t in teams}.values())), "RESULTS": RESULTS,
        "LOST_CARD": lost_card_how(cmd, label), "CHECKOUT": p["checkout"], "MAIN_PLACE": f"session {p['session']} on {p['machine']}",
        "DESIGN_AGENT": f"{label}-design", "PLANNER": f"{label}-planner", "MAIN_OPS": f"{label}-ops",
        "REVIEWER": f"{label}-reviewer", "REVIEWS": f"~/.local/state/crew/{label}-main/reports",
        "DISPATCHER": f"{label}-dispatch-{host}", "KITS": ", ".join(kits) or "none yet",
        "KIT_CHECKOUTS": ", ".join(f"`{c}`" for c in kits_on(fleet, label, p["machine"])) or "none on this host",
        "TEAMS": "\n".join(team_line(t) for t in teams) or "- no team yet",
        "HOST_TEAMS": "\n".join(team_line(t) for t in here) or "- no team on this host",
        "DISPATCHERS": ", ".join(f"`{label}-dispatch-{h}` on {h}" for h in hosts) or "none yet",
        "OPERATORS": ", ".join(f"`{label}-operator-{h}` on {h}" for h, v in sorted(fleet["hosts"].items()) if label in v.get("sessions", {})),
        "TEAMS_OPERATORS": ", ".join(f"`{label}-operator-{h}`" for h, v in sorted(fleet["hosts"].items())
                                     if label in v.get("sessions", {}) and v.get("kind") == "darwin" and v.get("supervised")) or "none",
        "SHOWING": (f"{host} is a Mac: open the site the user picks in terminal-browser beside your pane, "
                    "`terminal-browser open <url> --split right`." if fleet["hosts"].get(host, {}).get("kind") == "darwin" else
                    f"{host} is a box, which can't open the dev.swancloud.net names: say so, and give the user the URL "
                    "`crew sites` marks to open from a Mac."),
    }
    tok["ROSTER"] = (
        f"{label}'s main level ({p['partition']}) runs in {tok['MAIN_PLACE']}, in the `{label}` workspace: `{label}-design`, the design "
        f"agent, keeps the design true on main and curates signals; `{label}-planner` plans the partition's bolts and posts its "
        f"review batches; `{label}-reviewer`, started fresh for each batch, summarizes its changes; `{label}-ops` lands "
        f"proven bolts on the user's approval of their landing cards. A dispatcher on each host the partition's teams run on gives that host's teams their bolts: "
        f"{tok['DISPATCHERS']}. The operator agent in each of the partition's operator sessions works for the user: {tok['OPERATORS'] or 'none'}. "
        f"The partition's teams:\n\n{tok['TEAMS']}\n\nAny of these is reached with `{cmd} tell <agent> \"<text>\"`, wherever it runs. "
        f"{SENDERS}")
    return tok


def brief(fleet, scope, role, self_name=""):
    """A definition's body, filled from the teams file for a team or for a partition's main level."""
    if scope in fleet["teams"]:
        role in TEAM_ROLES or fail(f"no definition '{role}' for a team. definitions: " + " ".join(TEAM_ROLES))
        tok = team_tokens(fleet, fleet["teams"][scope], role, self_name)
    else:
        role in MAIN_ROLES or fail(f"no definition '{role}' for a main level. definitions: " + " ".join(MAIN_ROLES))
        tok = main_tokens(fleet, partition_of(fleet, scope), role, self_name)
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


def resolve(fleet, scope, role, extra):
    """How a role starts, and with "resume" the session it picks up: its last conversation, in the folder that began
    it, which since a conductor moves into its bolt's worktree need not be where the role starts today."""
    l = launch(fleet, scope, role, None if extra == "resume" else extra)
    found = last_conversation(l["name"]) if extra == "resume" else None
    return (dict(l, cwd=found[1]), found[0]) if found else (l, None)


def launch_shell(fleet, scope, role, extra):
    """crew-role's start, as shell assignments: CWD, NAME, LABEL and the claude arguments in `args`. A resume with no
    conversation to pick up starts the role fresh."""
    l, session = resolve(fleet, scope, role, extra)
    args = ["--model", l["model"], "--effort", l["effort"], "--permission-mode", "bypassPermissions"]
    for d in l["dirs"]:
        args += ["--add-dir", d]
    args += ["--name", l["name"]]
    if session:
        args += ["--resume", session]
    args += ["--append-system-prompt", brief(fleet, scope, l["defn"], l["name"])]
    return (f"CWD={shlex.quote(l['cwd'])}\nNAME={shlex.quote(l['name'])}\nLABEL={shlex.quote(l['label'])}\n"
            f"args=({' '.join(shlex.quote(a) for a in args)})")


def env_main(fleet, label):
    p = partition_of(fleet, label)
    return shell(KIND="main", LABEL=label, MACHINE=p["machine"], SSH_TARGET=p["ssh"], SESSION=p["session"], CWD=p["checkout"],
                 STATE=f"$HOME/.local/state/crew/{label}-main", **reach(fleet, p["machine"]))


def env_dispatch(fleet, label, host):
    session = dispatch_place(fleet, label, host)
    bps = blueprints_on(fleet, label, host)
    return shell(KIND="dispatch", LABEL=label, HOST=host, MACHINE=host, SSH_TARGET=fleet["hosts"][host]["ssh"], SESSION=session,
                 CWD=bps[0] if bps else fleet["hosts"][host]["sessions"][session]["dir"], STATE=f"$HOME/.local/state/crew/{label}-dispatch",
                 **reach(fleet, host))


def env_operator(fleet, label, host):
    sess = operator_session(fleet, label, host)
    return shell(KIND="operator", LABEL=label, HOST=host, MACHINE=host, SSH_TARGET=fleet["hosts"][host]["ssh"], SESSION=label,
                 CWD=sess["dir"], STATE=f"$HOME/.local/state/crew/{label}-operator", **reach(fleet, host))


def here(fleet):
    """What crew runs on this host: its teams, the main levels whose session is here, the dispatchers of the
    partitions whose teams run here, and the operator agents of its operator sessions."""
    host, out = this_host(), []
    out += [("team", n) for n, t in sorted(fleet["teams"].items()) if t["machine"] == host]
    for label, p in sorted(fleet["partitions"].items()):
        if p["machine"] == host:
            out.append(("main", label))
        if host in partition_hosts(fleet, label):
            out.append(("dispatch", label))
        sess = fleet["hosts"].get(host, {}).get("sessions", {}).get(label)
        if sess and sess.get("partition") == p["partition"]:
            out.append(("operator", label))
    return out


def shell(**pairs):
    """Shell assignments; STATE is left for the shell to expand, on the host it runs on."""
    return "\n".join(f'{k}="{v}"' if k == "STATE" else f"{k}={shlex.quote(v)}" for k, v in pairs.items())


# ------------------------------------------------------------------------------------------ a team's slots and panes

def nap(seconds):
    """A pause between looks at a pane: the host's sleep, which crew's tests stub to return at once."""
    subprocess.run(["sleep", str(seconds)])


def working_said(agent):
    """What crew says of an agent it will not end because it works (teams.2)."""
    return f"{agent} is working; add --force to end it anyway."


def down_said(team):
    """What a stage refused on a team taken down says: it runs nothing until it is brought up."""
    return f"{team} is down; crew up {team} brings it back"


def slot_for(team, slots, held, name):
    """The slot a unit or fix runs in (teams.1): the one holding it, else the first of the team's slots that holds
    nothing, as (slot, whether it is newly taken); held is the slots file's lines, split. Refused, naming what each
    holds, when every slot is in flight."""
    for f in held:
        if f[2:3] == [name]:
            return f[0], False
    holding = {f[0] for f in held if len(f) > 2}
    free = [s for s in slots if s not in holding]
    free or fail(f"all {len(slots)} of {team}'s slots are in flight: " + "; ".join(f"{f[0]} holds {' '.join(f[2:3])}" for f in held))
    return free[0], True


def reaped(agent, team, name, stage, status):
    """What a team's read does with a slot (teams.1): ("free", what it says) once its work has merged, landed, been
    dropped from the plan or left the team's bolt and its agent is not working; ("keep", what it says, or None) while
    that agent works; (None, None) while its work goes on."""
    if stage not in ("merged", "landed", "dropped", "left"):
        return None, None
    if status == "working":
        return "keep", {"dropped": f"{agent} still holds {name}, dropped from the plan: its agent is working; it is freed once that settles",
                        "left": f"{agent} still holds {name}, which has left {team}'s bolt: its agent is working; it is freed once that "
                                "settles"}.get(stage)
    return "free", {"dropped": f"{agent} is free: {name} was dropped from the plan",
                    "left": f"{agent} is free: {name} has left {team}'s bolt"}.get(stage, f"{agent} is free: {name} has merged into its bolt")


def held_object(kind, name, bolt=""):
    """What a slot holds, as the run record names it (record.6): unit/<unit>, or a fix's fix/<bolt>/<name>, one given
    as fix/<name> before a fix's name held its bolt taking the bolt its branch tracks (bolt)."""
    if kind != "fix":
        return f"unit/{name}"
    if name.startswith("fix/") and "/" in name[4:]:
        return name
    return f"fix/{bolt[5:] if bolt.startswith('bolt/') else bolt}/{name[4:] if name.startswith('fix/') else name}"


def slot_pane_at(panes, live):
    """Where a slot's new pane opens in "<team> units": halving the newest slot pane open, to its right when an odd
    number are open and below it when an even number are, as (that pane, right or down); (None, None) when none is,
    and the workspace opens anew. panes is the panes file's (role, pane) in the order they opened; live(pane) whether
    a pane is there."""
    open_ = [p for role, p in panes if role.startswith("unit-") and live(p)]
    return (open_[-1], "right" if len(open_) % 2 else "down") if open_ else (None, None)


def started_said(name, pane, stage=None):
    """What crew says of a role it started, fresh at a stage or brought back with its conversation."""
    return f"{name} resumed in {pane}" if stage == "resume" else f"{name} started {stage} in {pane}" if stage else f"{name} started in {pane}"


TIMESTAMP = re.compile(r'"timestamp":"([^"]*)"')


def context_of(lines, window):
    """What crew status shows of a standing agent's session, from its transcript's lines: the context its last turn
    used, in thousands of tokens and as a share of the window; the compactions it has had; and when it began, its
    month, day and minute. The last turn is the last of the session's own records, not a subagent's, among the last 40
    that carry a usage."""
    usage, compactions, began = collections.deque(maxlen=40), 0, ""
    for line in lines:
        if '"usage"' in line:
            usage.append(line)
        compactions += '"isCompactSummary":true' in line
        if not began:
            m = TIMESTAMP.search(line)
            began = m.group(1)[5:16] if m else ""
    used = 0
    for line in usage:
        try:
            v = json.loads(line)
        except ValueError:
            continue
        u = v.get("message", {}).get("usage") if isinstance(v, dict) and not v.get("isSidechain") and isinstance(v.get("message"), dict) else None
        if isinstance(u, dict):
            used = sum(u.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    return f"{used // 1000}k", f"{used * 100 // window}%", str(compactions), began


def holds_said(s, line):
    """What crew status says a slot holds: from slot_stages' answer for it (s), its unit or fix and that work's stage,
    with its tasks done and total in code or verify; from the slots file's line alone, its work and that its stage is
    unknown; "" for a free slot."""
    if s:
        return f"{s['name']}  {s['stage']}" + (f" {s['counts']}" if s.get("counts") and s["stage"] in ("code", "verify") else "")
    return f"{line[2]}  unknown" if line and len(line) > 2 else ""


def status_row(*cells):
    return "%-26s %-8s %-9s %8s %5s %8s  %-12s %s" % cells


class Team:
    """A team's slots, panes and agents on its host, as one crew command acts on them there (code.3): the panes, layout
    and slots files of its state folder, each changed only by writing a new file over the old (teams.9), and its herdr
    session through the command's Herdr. A working agent is ended only when force is given (teams.2)."""

    def __init__(self, fleet, t, force=False):
        self.fleet, self.t, self.force = fleet, t, force
        self.name, self.label = t["name"], t["label"]
        self.state = pathlib.Path.home() / f".local/state/{t['name']}-team"
        self.herdr = herdr_in(t["session"])
        self.slots = [f"unit-{n}" for n in range(1, t["units"] + 1)]

    def ensure(self):
        self.state.mkdir(parents=True, exist_ok=True)
        for f in ("panes", "layout", "slots"):
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
        return f"{self.name}-{role}"

    def pane(self, role):
        return self.get("panes", role)

    def status(self, role, fresh=False):
        return self.herdr.status(self.pane(role), fresh)

    def holding(self, name):
        """The slot holding a unit or fix, or None."""
        return next((l[0] for l in self.lines("slots") if l[2:3] == [name]), None)

    def held(self, slot):
        """The slots file's line for a slot, split, or None."""
        return next((l for l in self.lines("slots") if l[0] == slot), None)

    def down(self):
        """Whether the team was taken down with crew down or close, and stays down until it is brought up."""
        return (self.state / "down").exists()

    def owes(self):
        """Whether the team's stages file owes any stage an end."""
        p = self.state / "stages"
        return p.exists() and p.stat().st_size > 0

    def answer(self, *args):
        """herdr's result for an act that answers with what it made; refused in herdr's words when it fails."""
        r = self.herdr.run(*args)
        try:
            return json.loads(r.stdout)["result"]
        except (ValueError, KeyError, TypeError):
            fail(f"herdr could not {args[1]} a {args[0]} in session {self.t['session']}: "
                 + ((r.stderr or "").strip().splitlines() or [f"exit {r.returncode}"])[-1])

    def stop(self, role, ending=None):
        """End a role's agent before anything else starts in its pane (teams.2): None once it is ended, or when none was
        up; else what crew says, refused while the agent works unless forced, or failed when it did not exit. A slot's
        stage, or ops's proof, still owed an end ends with it first, by ending(role)."""
        pane = self.pane(role)
        st = self.herdr.status(pane)
        if st == "working" and not self.force:
            return working_said(self.agent_of(role))
        if ending and (role.startswith("unit-") or role == "ops") and self.owes():
            ending(role)
        if not st:
            return None
        if self.herdr.run("agent", "prompt", pane, "/exit").returncode:
            self.herdr.run("pane", "send-keys", pane, "ctrl+c", "ctrl+c")
        for _ in range(30):
            if not self.herdr.status(pane, fresh=True):
                return None
            nap(1)
        # Still running means anything started next would be typed into it as a message. Say so and leave it be.
        self.herdr.run("pane", "send-keys", pane, "ctrl+c", "ctrl+c")
        nap(2)
        return f"{self.agent_of(role)} did not exit (busy or waiting on the user); it was left running" if self.herdr.status(pane, fresh=True) else None

    def start(self, role, stage=None):
        """Start a role fresh in its pane, at a stage for a slot (teams.2, teams.6): never over an agent still running.
        Its shell is cleared and moved to the folder the role runs in, which herdr keeps for the pane and Claude finds
        its conversation from; crew-role starts it there, it is given its name, and Claude's folder-trust question alone
        is answered for it, never the Bypass Permissions warning (teams.8). Returns whether it started, said on standard
        error when not."""
        pane, name = self.pane(role), self.agent_of(role)
        if self.herdr.status(pane):
            print(f"{name} is still running; not starting another over it", file=sys.stderr)
            return False
        try:
            cwd = resolve(self.fleet, self.name, role, stage)[0]["cwd"]
        except Refusal as e:
            print(e, file=sys.stderr)
            return False
        # A Claude that died badly leaves the pane reporting mouse movement, which types escape codes into the shell
        # and into whatever is run next. Clear the line and switch the reporting off first.
        self.herdr.run("pane", "send-keys", pane, "ctrl+c")
        self.herdr.run("pane", "run", pane, "printf '\\033[?1000l\\033[?1002l\\033[?1003l\\033[?1006l\\033[?1015l\\033[?2004l'; clear")
        nap(1)
        self.herdr.run("pane", "run", pane, f"cd {shlex.quote(cwd)} && bash {shlex.quote(str(HOME / 'plugin/bin/crew-role'))} "
                                            f"{self.name} {role}" + (f" {stage}" if stage else ""))
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

    def slot_pane(self, slot, path):
        """The slot's pane, opened in "<team> units" when it is not there (slot_pane_at); the workspace exists only while
        a slot is in flight."""
        if self.herdr.live(self.pane(slot)):
            return
        newest, way = slot_pane_at([(l[0], l[1]) for l in self.lines("panes") if len(l) > 1], self.herdr.live)
        if newest:
            p = self.answer("pane", "split", newest, "--direction", way, "--cwd", path, "--no-focus")["pane"]["pane_id"]
        else:
            made = self.answer("workspace", "create", "--cwd", path, "--label", f"{self.name} units", "--no-focus")
            self.put("layout", f"ws:{self.name}_units", made["workspace"]["workspace_id"])
            self.herdr.run("tab", "rename", made["tab"]["tab_id"], "units")
            p = made["root_pane"]["pane_id"]
        self.put("panes", slot, p)

    def take(self, kind, name, place):
        """The slot a unit or fix runs in, taken when it holds none yet (slot_for): (slot, whether newly taken)."""
        held = self.lines("slots")
        slot, new = slot_for(self.name, self.slots, held, name)
        if new:
            self.write("slots", held + [[slot, kind, name, place]])
        return slot, new

    def close_pane(self, role):
        pane = self.pane(role)
        if self.herdr.live(pane):
            self.herdr.run("pane", "close", pane)
        self.drop("panes", role)

    def free(self, slot, ending=None, bolt=""):
        """End a slot's agent, close its pane and give the slot back, recorded (teams.1); the units workspace goes with
        the last slot. None once it is free, else what crew says of the agent it could not end (stop). bolt is the bolt
        a fix given as fix/<name> is of, read from its branch when not given."""
        why = self.stop(slot, ending)
        if why:
            return why
        line = self.held(slot)
        self.drop("slots", slot)
        if line and len(line) > 2:
            if line[1] == "fix" and not bolt and not (line[2].startswith("fix/") and "/" in line[2][4:]):
                bolt = subprocess.run(["git", "-C", self.t["kit"]["main"], "for-each-ref", "--format=%(upstream:short)", f"refs/heads/{line[2]}"],
                                      capture_output=True, text=True).stdout.strip()
            import record as rec  # record imports this module
            rec.emit(self.label, "slot.free", [f"agent/{self.agent_of(slot)}", held_object(line[1], line[2], bolt)],
                     why=f"team({self.name}): free {self.agent_of(slot)}")
        if self.lines("slots"):
            self.close_pane(slot)
            return None
        w = self.get("layout", f"ws:{self.name}_units")
        if w:
            self.herdr.run("workspace", "close", w)
        self.drop("layout", f"ws:{self.name}_units")
        for s in self.slots:
            self.drop("panes", s)
        return None


def main(a):
    fleet = load()
    if a[:1] == ["teams"]:
        print("\n".join(fleet["teams"]))
    elif a[:1] == ["labels"]:
        print("\n".join(fleet["partitions"]))
    elif a[:1] == ["env"] and len(a) == 2:
        print(env(fleet, team_of(fleet, a[1])))
    elif a[:1] == ["brief"] and len(a) >= 3:
        sys.stdout.write(brief(fleet, a[1], a[2], a[3] if len(a) > 3 else ""))
    elif a[:1] == ["launch"] and len(a) >= 3:
        print(launch_shell(fleet, a[1], a[2], a[3] if len(a) > 3 else None))
    elif a[:1] == ["place"] and len(a) >= 3:
        l, session = resolve(fleet, a[1], a[2], a[3] if len(a) > 3 else None)
        if a[3:4] == ["resume"] and not session:
            print(f"{l['name']} has no conversation to resume; starting it fresh", file=sys.stderr)
        print(l["cwd"])
    elif a[:1] == ["env-main"] and len(a) == 2:
        print(env_main(fleet, a[1]))
    elif a[:1] == ["env-dispatch"] and len(a) in (2, 3):
        print(env_dispatch(fleet, a[1], a[2] if len(a) > 2 else this_host()))
    elif a[:1] == ["env-operator"] and len(a) == 2:
        print(env_operator(fleet, a[1], this_host()))
    elif a[:1] == ["hosts"] and len(a) == 2:
        # A partition with no teams has no dispatcher host, and prints nothing: an empty line would read as a host.
        for h in partition_hosts(fleet, a[1]):
            print(f"{h} {fleet['hosts'][h]['ssh']} {crew_at(fleet, h)}")
    elif a[:1] == ["here"]:
        print("\n".join(f"{k} {n}" for k, n in here(fleet)))
    elif a[:1] == ["crew-at"] and len(a) == 2:
        print(crew_at(fleet, a[1]))
    elif a[:1] == ["tell"] and len(a) in (3, 4) and a[3:] in ([], ["--taken"]):
        import record as rec  # record imports this module
        sys.exit(0 if tell(fleet, a[1], a[2], sender=rec.who(), taken=a[3:] == ["--taken"]) else 1)
    elif a[:1] == ["notice"] and len(a) == 3:
        sys.exit(0 if tell(fleet, a[1], a[2]) else 1)
    elif a[:1] == ["greet"] and (len(a) == 2 or (len(a) == 4 and a[2] == "--first")):
        greet(fleet, a[1], first=f"{a[3]} " if len(a) == 4 else "")
    elif a[:1] == ["greet-agent"] and len(a) in (2, 4) and a[2:3] in ([], ["--wait"]):
        len(a) == 2 or a[3].isdigit() or fail(f"--wait takes a number of seconds, not {a[3]}")
        greet_standing(fleet, a[1], int(a[3]) if len(a) == 4 else 90)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
