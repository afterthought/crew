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
  crew.py tell <agent> "<text>"       prompt an agent wherever it runs, the text marked [crew tell from <sender>]
  crew.py here                        what runs on this host, one per line: team <name>, main <label>,
                                      dispatch <label> and operator <label>

Each role is an agent definition, roles/<role>.md: frontmatter naming its model and effort, which a team's or a
partition's `roles` in the teams file may override, and its brief as the body, with its {{TOKENS}} filled. Every token is built here from the team's
data; a token with no builder, or data a builder needs and the team lacks, is an error, never blank text."""
import functools, itertools, json, os, pathlib, re, shlex, subprocess, sys, time

LIB = pathlib.Path(__file__).resolve().parent
HOME = LIB.parent.parent
HOSTS = pathlib.Path.home() / ".config/swancloud/herdr-hosts.json"
TEAMS = pathlib.Path.home() / ".config/crew/teams.json"
VERSION = 2
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
# The roles a team's entry may override, and those a partition's entry may: each is a definition in roles/.
TEAM_ROLES = ("conductor", "ops", "construct", "coder", "verify")
MAIN_ROLES = ("design", "planner", "main-ops", "dispatcher", "operator")


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


def load():
    """The partitions and teams, written by the machine's own configuration (swancloud's lib/crew-teams.nix),
    never by crew. Every entry is checked here, against the hosts file, before any is used."""
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
    """The host crew runs on, as `hostname -s` names it: the same name the hosts file and the teams file use."""
    return subprocess.run(["hostname", "-s"], capture_output=True, text=True, check=True).stdout.strip()


def on_machine(fleet, host, argv, input=None):
    """Run a command on a host: here when it is this host, else over ssh, never prompting. A host that does not
    answer exits 255, as ssh does."""
    if host == this_host():
        return subprocess.run(argv, input=input, capture_output=True, text=True)
    return subprocess.run(["ssh", "-o", "BatchMode=yes", fleet["hosts"][host]["ssh"], shlex.join(argv)],
                          input=input, capture_output=True, text=True)


def place_of_agent(fleet, name):
    """The host and herdr session an agent crew starts runs in, from its name alone."""
    for t in fleet["teams"].values():
        if name in (f"{t['name']}-conductor", f"{t['name']}-ops") or re.match(rf"^{re.escape(t['name'])}-unit-[1-9][0-9]*$", name):
            return t["machine"], t["session"]
    for p in fleet["partitions"].values():
        l = p["label"]
        if name in (f"{l}-design", f"{l}-planner", f"{l}-ops"):
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
    for t in fleet["teams"].values():
        if name in (f"{t['name']}-conductor", f"{t['name']}-ops") or re.match(rf"^{re.escape(t['name'])}-unit-[1-9][0-9]*$", name):
            return t["label"]
    for l in fleet["partitions"]:
        if name in (f"{l}-design", f"{l}-planner", f"{l}-ops") or re.match(rf"^{re.escape(l)}-(dispatch|operator)-.+$", name):
            return l
    return None


def tell(fleet, name, text, record=True, sender=None):
    """Send an agent a prompt wherever it runs, marked as crew's: `[crew tell from <sender>]` for what crew tell
    carries for someone, `[crew]` for crew's own greetings and notices, so the recipient, and crew reading its
    transcript, never take it for the user's typing. An agent that is not up is reported, not an error. A tell is in
    the run record of the recipient's partition, with its length and never its text."""
    host, session = place_of_agent(fleet, name)
    mark = f"[crew tell from {sender}]" if sender else "[crew]"
    r = on_machine(fleet, host, ["herdr", "--session", session, "agent", "prompt", name, f"{mark} {text}"])
    if r.returncode:
        print(f"could not tell {name} on {host}: " + (r.stderr.strip() or "it is not up"), file=sys.stderr)
    elif record:
        import record as rec  # record imports this module
        rec.emit(label_of_agent(fleet, name), "tell", on=[f"agent/{name}"], why=f"tell {name}", Chars=len(text))
    return r.returncode == 0


def agent_get(fleet, name):
    """An agent crew starts, as herdr's agent get answers wherever it runs, or None when it is not up."""
    host, session = place_of_agent(fleet, name)
    r = on_machine(fleet, host, ["herdr", "--session", session, "agent", "get", name])
    try:
        a = json.loads(r.stdout)["result"]["agent"] if r.returncode == 0 else None
    except (ValueError, KeyError, TypeError):
        return None
    return a if isinstance(a, dict) else None


def agent_status(fleet, name):
    """An agent crew starts, as herdr sees it wherever it runs: idle, done, working, blocked, or None when it is not up."""
    a = agent_get(fleet, name)
    return a.get("agent_status") if a else None


GREETING = ("Read where your bolt stands with `crew bolts`, tell me in a few lines, then carry on with it: "
            "start each stage that is ready.")


def greet(fleet, team, first="", wait=90):
    """Get a team's conductor going: once it is up and settled, tell it to read where its bolt stands and carry
    on. One stopped on a question in its pane, such as a first run's consent, is greeted once that is answered,
    for up to five minutes. Returns whether it was greeted; a conductor that is not up is reported, not an error."""
    t = team_of(fleet, team)
    name, text = f"{t['name']}-conductor", first + GREETING
    deadline, asked = time.monotonic() + wait, False
    while (s := agent_status(fleet, name)) not in ("idle", "done"):
        if s == "blocked" and not asked:
            print(f"{name} is waiting on a question in its pane; answer it there and it will be greeted", file=sys.stderr)
            asked, deadline = True, time.monotonic() + 300
        if time.monotonic() >= deadline:
            print(f"{name} is not up: crew up {t['name']} starts and greets it" if s is None
                  else f"{name} was not ready to greet; once it is: crew tell {name} \"{text}\"", file=sys.stderr)
            return False
        time.sleep(2)
    if not tell(fleet, name, text, record=False):
        return False
    import record as rec  # record imports this module
    rec.emit(t["label"], "greet", on=[f"agent/{name}", f"team/{t['name']}"], why=f"team({t['name']}): greet {name}")
    print(f"{name} greeted")
    return True


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
    r = subprocess.run([sys.executable, str(LIB / "plan.py"), "_bolt-of", t["name"]], capture_output=True, text=True)
    if r.returncode:
        why = (r.stderr or r.stdout).strip()
        if "holds no bolt" not in why:
            print(f"{t['name']}'s bolt could not be read ({why}); starting in {t['kit']['main']}", file=sys.stderr)
        return None
    bolt = r.stdout.strip().partition("=")[2].strip("'\"")
    path = f"{t['kit']['dir']}/bolts/{bolt}"
    return path if bolt and pathlib.Path(path).is_dir() else None


# A unit's stages and the definition each is started from.
STAGES = {"construct": "construct", "code": "coder", "verify": "verify", "merge": "coder", "fix": "coder"}
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
        if role in ("design", "planner", "ops"):
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
            fail(f"no role '{role}' at {label}'s main level. roles: design planner ops dispatcher operator")
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


def env(t):
    pairs = {
        "TEAM": t["name"], "SYSTEM": t["system"], "MACHINE": t["machine"], "SSH_TARGET": t["ssh"], "SESSION": t["session"],
        "LABEL": t["label"], "CREW_HOME": str(HOME), "KIT": t["kit"]["main"], "KIT_DIR": t["kit"]["dir"], "KIT_NAME": t["kit"]["name"],
        "BLUEPRINTS": t["blueprints"]["main"], "UNITS": str(t["units"]), "HOST_KIND": t.get("kind", ""),
    }
    return "\n".join(f"{k}={shlex.quote(v)}" for k, v in pairs.items()) + f'\nSTATE="$HOME/.local/state/{t["name"]}-team"'


# How an agent records a finding, the same in every brief that records one.
def signal_how(cmd, label, state):
    return (f"`{cmd} signal <slug> \"<what it asserts, in a sentence>\" --excerpt \"<the exact words the user said or the tool "
            f"printed>\" --kind constraint|ask|question|commitment|reaction`. Copy the excerpt, never reword it: crew looks for it "
            f"in your own session's transcript, and a refusal means the words were reworded. crew writes the signal under "
            f"`signals/` on `{label}/main` of {state}.")


# How a stage's agent, or ops during a proof, stops short, the same in every brief that runs a stage: work is "stage"
# or "proof".
def needs_how(cmd, work):
    return (f"When you cannot finish without something only someone else can give (a decision, a fact about a live system, "
            f"the user's word), run `{cmd} needs \"<what you tried and what you need>\"` and end your turn. crew ends your "
            f"{work} there and gives your words to the conductor, who gets the answer and starts the {work} again with it. "
            "Never ask in your pane: nobody watches it. Ending a turn to wait on something you started in the background is "
            f"fine: crew knows your {work} is over only when what it delivers is there.")


# How an agent keeps one Pending You card for each rail row it owns, the same in the planner's brief and the conductor's.
def cards_how(cmd, label, kits):
    return ("When your session has Pending You's tools, every decision of yours the rail lists gets one card, and only those. "
            "A question you ask in your pane gets no card. Take the row's card key from the `card:` line under its row in "
            f"`{cmd} rail --label {label}`, and post the card with that key as its `idempotencyKey`. That way a retry never "
            "makes a second card, and the rail knows the card is the row's. At your start, call `whoami` with your crew name "
            "and one line on your role. Then call `list_pending` with that name, and act on any card the user has answered. "
            "Post a card for any row of yours that has none open. Ask every card in your crew name, with this host as the "
            "session's machine and your worktree as its folder. File it in the area of its kit, found with `match_area` from "
            "the kit's git remote. When there is none, create it with `create_area`, named for the kit, in the group "
            f"`{label}`, with the key `create-area:<owner>/<kit>`. Never make a group: if `{label}` isn't one of the user's "
            "groups, the area is left ungrouped, and you say so once. Title it with what you ask and its bolt. Put what the "
            "user would read on it, and give it the row's answers as its options, with `blocking` false. You hear an answer "
            "by being woken in your pane. Never run `npx pendingyou` or `pendingyou hold`: the `pendingyou` on the path is the "
            "fleet's, and the wake needs neither. Act on the user's answer as if they had said it in your pane, then close the "
            "card with `ack_answer` and a one-line outcome. When crew tells you, or prints, to close the card for a row, close "
            "it with `cancel_request` and the reason, or with `ack_answer` when you acted on its answer. Only your own cards "
            f"are yours: leave every other card alone. The kits: {kits}.")


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
        f"({', '.join(slots)}), each holding one unit or fix in flight, where every stage of it (construct, code, verify, merge) "
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
             "dispatcher": f"{label}-dispatch-{host}", "operator": f"{label}-operator-{host}"}
    tok = {
        "SELF": self_name or names[role], "LABEL": label, "PARTITION": p["partition"], "HOST": host, "TEAM_CMD": cmd,
        "BLUEPRINTS_REPOS": ", ".join(f"`{b}`" for b in p["blueprints"]), "SIGNALS_REPO": p["blueprints"][0],
        "PLANS": f"`{label}/main` of {p['state']}", "STATE_REPO": p["state"], "SIGNAL": signal_how(cmd, label, p["state"]),
        "CARDS": cards_how(cmd, label, kits_named({t["kit"]["repo"]: t["kit"] for t in teams}.values())), "RESULTS": RESULTS,
        "CHECKOUT": p["checkout"], "MAIN_PLACE": f"session {p['session']} on {p['machine']}",
        "DESIGN_AGENT": f"{label}-design", "PLANNER": f"{label}-planner", "MAIN_OPS": f"{label}-ops",
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
        f"agent, keeps the design true on main and curates signals; `{label}-planner` plans the partition's bolts; `{label}-ops` lands "
        f"proven bolts and deploys main. A dispatcher on each host the partition's teams run on gives that host's teams their bolts: "
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
                 STATE=f"$HOME/.local/state/crew/{label}-main")


def env_dispatch(fleet, label, host):
    session = dispatch_place(fleet, label, host)
    bps = blueprints_on(fleet, label, host)
    return shell(KIND="dispatch", LABEL=label, HOST=host, MACHINE=host, SSH_TARGET=fleet["hosts"][host]["ssh"], SESSION=session,
                 CWD=bps[0] if bps else fleet["hosts"][host]["sessions"][session]["dir"], STATE=f"$HOME/.local/state/crew/{label}-dispatch")


def env_operator(fleet, label, host):
    sess = operator_session(fleet, label, host)
    return shell(KIND="operator", LABEL=label, HOST=host, MACHINE=host, SSH_TARGET=fleet["hosts"][host]["ssh"], SESSION=label,
                 CWD=sess["dir"], STATE=f"$HOME/.local/state/crew/{label}-operator")


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


def main(a):
    fleet = load()
    if a[:1] == ["teams"]:
        print("\n".join(fleet["teams"]))
    elif a[:1] == ["labels"]:
        print("\n".join(fleet["partitions"]))
    elif a[:1] == ["env"] and len(a) == 2:
        print(env(team_of(fleet, a[1])))
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
    elif a[:1] == ["tell"] and len(a) == 3:
        import record as rec  # record imports this module
        sys.exit(0 if tell(fleet, a[1], a[2], sender=rec.who()) else 1)
    elif a[:1] == ["greet"] and len(a) == 2:
        greet(fleet, a[1])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
