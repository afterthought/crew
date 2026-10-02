#!/usr/bin/env python3
"""crew.py: read the teams file and answer from it.

  crew.py teams                       every team's name
  crew.py labels                      every partition's label
  crew.py env <team>                  the team's settings as shell assignments
  crew.py brief <team> <role> [name]  the role's brief for that team; name is the agent's own name

A brief is roles/<role>.md with its {{TOKENS}} filled. Every token is built here from the team's
data; a token with no builder, or data a builder needs and the team lacks, is an error, never blank text."""
import json, pathlib, re, shlex, sys

LIB = pathlib.Path(__file__).resolve().parent
HOME = LIB.parent.parent
ROLES = ("conductor", "fable", "explorer", "ops", "coder", "verifier")
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
def build_tokens(t, self_name):
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
def brief(t, role, self_name):
    if role not in ROLES:
        fail(f"no role '{role}'. roles: " + " ".join(ROLES))
    tok = build_tokens(t, self_name)
    def fill(m):
        k = m.group(1)
        if k not in tok:
            fail(f"roles/{role}.md needs {{{{{k}}}}} and crew.py builds no such token")
        return tok[k]
    text = (LIB.parent / "roles" / f"{role}.md").read_text()
    for _ in range(2):  # a token's text may itself carry tokens
        text = re.sub(r"\{\{([A-Z_]+)\}\}", fill, text)
    return text


def main(a):
    fleet = load()
    if a[:1] == ["teams"]:
        print("\n".join(fleet["teams"]))
    elif a[:1] == ["labels"]:
        print("\n".join(fleet["partitions"]))
    elif a[:1] == ["env"] and len(a) == 2:
        print(env(team_of(fleet, a[1])))
    elif a[:1] == ["brief"] and len(a) >= 3:
        sys.stdout.write(brief(team_of(fleet, a[1]), a[2], a[3] if len(a) > 3 else ""))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Refusal as e:
        sys.exit(str(e))
