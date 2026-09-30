#!/usr/bin/env python3
"""crew.py: read the teams file and answer from it.

  crew.py teams                       every team's name
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


def load():
    """The teams, written by the machine's own configuration (swancloud's lib/crew-teams.nix), never by crew."""
    if not TEAMS.exists():
        sys.exit(f"{TEAMS} is missing; the machine's configuration writes it")
    return json.loads(TEAMS.read_text())


def host_of(name, machine, session):
    """The machine's entry in swancloud's generated list of herdr hosts, which owns every ssh name and session."""
    if not HOSTS.exists():
        sys.exit(f"{HOSTS} is missing; swancloud's home-manager writes it")
    hosts = json.loads(HOSTS.read_text())["hosts"]
    host = hosts.get(machine) or sys.exit(f"team {name} runs on {machine}, which {HOSTS} does not list. hosts: " + " ".join(hosts))
    if session not in host["sessions"]:
        sys.exit(f"team {name} uses herdr session {session}, which {HOSTS} does not list on {machine}. sessions: " + " ".join(host["sessions"]))
    return host


def team_of(data, name):
    for t in data["teams"]:
        if t["name"] == name:
            host = host_of(name, t["machine"], t["session"])
            root = host["sessions"][t["session"]]["dir"]
            kit, design = t["repos"]
            return dict(t, base=t.get("base") or "main", ssh=host["ssh"],
                        kit={"name": kit, "abs": f"{root}/{kit}/main"}, design={"name": design, "abs": f"{root}/{design}/main"})
    sys.exit(f"no team '{name}'. teams: " + " ".join(t["name"] for t in data["teams"]))
def names(t):
    n = {r: f"{t['name']}-{r}" for r in ("conductor", "fable", "explorer", "ops", "verifier")}
    n["coders"] = [f"{t['name']}-coder-{i}" for i in range(1, int(t.get("coders", 1)) + 1)]
    return n
def reports(t):
    return f"~/.local/state/{t['name']}-team/reports"
def env(t):
    pairs = {
        "TEAM": t["name"], "SYSTEM": t["system"], "MACHINE": t["machine"], "SSH_TARGET": t["ssh"], "SESSION": t["session"],
        "CREW_HOME": str(HOME), "KIT": t["kit"]["abs"], "KIT_NAME": t["kit"]["name"], "DESIGN": t["design"]["abs"],
        "CODERS": str(int(t.get("coders", 1))), "REPORTS": reports(t), "BASE": t["base"],
    }
    return "\n".join(f"{k}={shlex.quote(v)}" for k, v in pairs.items()) + f'\nSTATE="$HOME/.local/state/{t["name"]}-team"'
def build_tokens(t, self_name):
    n, kit, design = names(t), t["kit"], t["design"]
    coders = ", ".join(f"`{c}`" for c in n["coders"])
    tok = {
        "SELF": self_name or "", "TEAM": t["name"], "SYSTEM": t["system"], "KIT": kit["abs"], "KIT_NAME": kit["name"],
        "DESIGN": design["abs"], "DESIGN_NAME": design["name"], "CONDUCTOR": n["conductor"], "FABLE": n["fable"],
        "EXPLORER": n["explorer"], "OPS": n["ops"], "VERIFIER": n["verifier"], "CODER_NAMES": coders,
        "CODERS": str(len(n["coders"])), "TEAM_CMD": f"{HOME}/plugin/bin/crew", "REPORTS": reports(t), "BASE": t["base"],
        "CREW": f"the `## Crew` section of {kit['name']}'s CLAUDE.md (`{kit['abs']}/CLAUDE.md`)",
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
        sys.exit(f"no role '{role}'. roles: " + " ".join(ROLES))
    tok = build_tokens(t, self_name)
    def fill(m):
        k = m.group(1)
        if k not in tok:
            sys.exit(f"roles/{role}.md needs {{{{{k}}}}} and crew.py builds no such token")
        return tok[k]
    text = (LIB.parent / "roles" / f"{role}.md").read_text()
    for _ in range(2):  # a token's text may itself carry tokens
        text = re.sub(r"\{\{([A-Z_]+)\}\}", fill, text)
    return text


if __name__ == "__main__":
    a = sys.argv[1:]
    data = load()
    if a[:1] == ["teams"]:
        print("\n".join(t["name"] for t in data["teams"]))
    elif a[:1] == ["env"] and len(a) == 2:
        print(env(team_of(data, a[1])))
    elif a[:1] == ["brief"] and len(a) >= 3:
        sys.stdout.write(brief(team_of(data, a[1]), a[2], a[3] if len(a) > 3 else ""))
    else:
        sys.exit(__doc__)
