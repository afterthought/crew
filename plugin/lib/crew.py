#!/usr/bin/env python3
"""crew.py: read the teams file and answer from it.

  crew.py teams                       every team's name
  crew.py labels                      every partition's label
  crew.py env <team>                  the team's settings as shell assignments
  crew.py brief <team|label> <definition> [name]
                                      a definition's brief for a team or a partition's main level; name is the agent's own
  crew.py launch <team|label> <role> [stage|resume]
                                      how crew-role starts the role, as shell assignments

Each role is an agent definition, roles/<role>.md: frontmatter naming its model and effort, which a team's or a
partition's `roles` in the teams file may override, and its brief as the body, with its {{TOKENS}} filled. Every token is built here from the team's
data; a token with no builder, or data a builder needs and the team lacks, is an error, never blank text."""
import functools, json, pathlib, re, shlex, subprocess, sys

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
                           partition=pname, ssh=host["ssh"], dir=sess["dir"], roles=roles_of(t, what, TEAM_ROLES),
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


def tell(fleet, name, text):
    """Send an agent a prompt wherever it runs. An agent that is not up is reported, not an error."""
    host, session = place_of_agent(fleet, name)
    r = on_machine(fleet, host, ["herdr", "--session", session, "agent", "prompt", name, text])
    if r.returncode:
        print(f"could not tell {name} on {host}: " + (r.stderr.strip() or "it is not up"), file=sys.stderr)
    return r.returncode == 0


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


# A unit's stages and the definition each is started from.
STAGES = {"construct": "construct", "code": "coder", "verify": "verify", "merge": "coder", "fix": "coder"}
# The definitions being retired with the bolt model; their briefs still print until they go.
RETIRING = ("fable", "explorer", "verifier")


def launch(fleet, scope, role, extra=None):
    """How crew-role starts a role: its folder, agent name, partition, the definition it comes from, the
    folders it may also reach, and the model and effort after the teams file's override."""
    if scope in fleet["teams"]:
        t = fleet["teams"][scope]
        label, roles, kit, bp = t["label"], t["roles"], t["kit"], t["blueprints"]
        if role in ("conductor", "ops"):
            spec = dict(defn=role, name=f"{t['name']}-{role}", cwd=kit["main"], dirs=[kit["dir"], bp["main"]])
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


def names(t):
    n = {r: f"{t['name']}-{r}" for r in ("conductor", "fable", "explorer", "ops", "verifier")}
    n["coders"] = [f"{t['name']}-coder-{i}" for i in range(1, t["units"] + 1)]
    return n
def reports(t):
    return f"~/.local/state/{t['name']}-team/reports"
def env(t):
    pairs = {
        "TEAM": t["name"], "SYSTEM": t["system"], "MACHINE": t["machine"], "SSH_TARGET": t["ssh"], "SESSION": t["session"],
        "LABEL": t["label"], "CREW_HOME": str(HOME), "KIT": t["kit"]["main"], "KIT_DIR": t["kit"]["dir"], "KIT_NAME": t["kit"]["name"],
        "BLUEPRINTS": t["blueprints"]["main"], "UNITS": str(t["units"]),
        "DESIGN": t["blueprints"]["main"], "CODERS": str(t["units"]), "REPORTS": reports(t), "BASE": "main",
    }
    return "\n".join(f"{k}={shlex.quote(v)}" for k, v in pairs.items()) + f'\nSTATE="$HOME/.local/state/{t["name"]}-team"'
def team_tokens(t, self_name):
    n, kit, design = names(t), t["kit"], t["blueprints"]
    coders = ", ".join(f"`{c}`" for c in n["coders"])
    tok = {
        "SELF": self_name or "", "TEAM": t["name"], "SYSTEM": t["system"], "KIT": kit["main"], "KIT_NAME": kit["name"],
        "DESIGN": design["main"], "DESIGN_NAME": design["name"], "CONDUCTOR": n["conductor"], "FABLE": n["fable"],
        "EXPLORER": n["explorer"], "OPS": n["ops"], "VERIFIER": n["verifier"], "CODER_NAMES": coders,
        "CODERS": str(len(n["coders"])), "TEAM_CMD": f"{HOME}/plugin/bin/crew", "REPORTS": reports(t), "BASE": "main",
        "CREW": f"the `## Crew` section of {kit['name']}'s CLAUDE.md (`{kit['main']}/CLAUDE.md`)",
    }
    tok["ROSTER"] = (
        f"The team: `{n['conductor']}` (Opus) keeps the coders building and reports where things stand; `{n['fable']}` (Fable) owns "
        f"{t['system']}'s design and reviews each change before it is built; `{n['explorer']}` (Opus) is started for one OpenSpec "
        f"command or lookup at a time in {kit['name']}; the coders ({coders}, Opus) each build one whole change at a time in that change's own worktree; "
        f"`{n['verifier']}` (Opus) is started only to run OpenSpec's verify on a finished change; and `{n['ops']}` (Opus) does everything "
        f"that touches a live system: dev AWS, GitHub, the vendors' consoles and APIs, sign-in, debugging and proofs in dev.")
    return tok
def main_tokens(fleet, p, self_name):
    return {"SELF": self_name or "", "LABEL": p["label"], "PARTITION": p["partition"], "HOST": this_host(),
            "TEAM_CMD": f"{HOME}/plugin/bin/crew"}


def brief(fleet, scope, role, self_name=""):
    """A definition's body, filled from the teams file for a team or for a partition's main level."""
    if scope in fleet["teams"]:
        role in TEAM_ROLES + RETIRING or fail(f"no definition '{role}' for a team. definitions: " + " ".join(TEAM_ROLES))
        tok = team_tokens(fleet["teams"][scope], self_name)
    else:
        role in MAIN_ROLES or fail(f"no definition '{role}' for a main level. definitions: " + " ".join(MAIN_ROLES))
        tok = main_tokens(fleet, partition_of(fleet, scope), self_name)
    def fill(m):
        k = m.group(1)
        if k not in tok:
            fail(f"roles/{role}.md needs {{{{{k}}}}} and crew.py builds no such token")
        return tok[k]
    text = definition(role)[1]
    for _ in range(2):  # a token's text may itself carry tokens
        text = re.sub(r"\{\{([A-Z_]+)\}\}", fill, text)
    return text


def launch_shell(fleet, scope, role, extra):
    """crew-role's start, as shell assignments: CWD, NAME, LABEL and the claude arguments in `args`."""
    l = launch(fleet, scope, role, None if extra == "resume" else extra)
    args = ["--model", l["model"], "--effort", l["effort"], "--permission-mode", "bypassPermissions"]
    for d in l["dirs"]:
        args += ["--add-dir", d]
    args += ["--name", l["name"]]
    if extra == "resume":
        args += ["--resume", l["name"]]
    args += ["--append-system-prompt", brief(fleet, scope, l["defn"], l["name"])]
    return (f"CWD={shlex.quote(l['cwd'])}\nNAME={shlex.quote(l['name'])}\nLABEL={shlex.quote(l['label'])}\n"
            f"args=({' '.join(shlex.quote(a) for a in args)})")


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
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
