# Sourced by every test, in its scratch directory $T. `world` builds the fleet the fixtures describe:
#
#   mac-studio (darwin)         chuck-herdr-alpha (nixos, the box)
#     wldn, wldn-5                wldn, wldn-1, wldn-2, wldn-3      clients/willdan (label wldn)
#     madswan, madswan-1, -2                                         business (label madswan)
#     swancloud, swancloud-1                                         personal (label swancloud)
#
# Teams: swb-1 (4 units) and swb-2 (2) in wldn-1 and brd-1 in wldn-2 on the box; atl-1 in wldn-5 and apk-1 in
# madswan-2 on mac-studio. Each host has its own HOME under hosts/<host>/home and its sessions' folders under
# hosts/<host>/work/<space>. Commands run as mac-studio unless HOST says otherwise.
set -euo pipefail
CREW=$(cd "$TESTS/.." && pwd -P)
export CREW_TEST_ROOT=$T CREW_TEST_LOG=$T/calls.log CREW_TEST_CLAUDE_LOG=$T/claude.log
export PATH="$TESTS/stubs:$PATH" GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
unset CREW_AGENT CREW_LABEL HERDR_PANE_ID HERDR_WORKSPACE_ID HERDR_TAB_ID HERDR_ENV HERDR_BIN_PATH HERDR_SOCKET_PATH GIT_DIR GIT_WORK_TREE
# A wt merge running the suite as its gate hands its hooks worktrunk's own variables, among them the file its shell
# wrapper reads a cd from: a test's wt never writes there, or the merge ends trying to cd into a removed scratch dir.
unset $(env | sed -n 's/^\(WORKTRUNK_[A-Za-z0-9_]*\)=.*/\1/p')
HOST=${HOST:-mac-studio}
# The user at a shell, as crew names them in what it writes: <me>@<host>.
me=$(python3 -c 'import getpass; print(getpass.getuser())')
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
# The test's own commands (making kits and remotes) run with a scratch HOME too, never the user's.
export HOME=$T/home; mkdir -p "$HOME"

home_of() { echo "$T/hosts/$1/home"; }
space() { echo "$T/hosts/$1/work/$2"; }
as() { local h=$1; shift; (export CREW_TEST_HOST=$h HOME; HOME=$(home_of "$h"); cd "$HOME" && "$@"); }
crew() { as "$HOST" "$CREW/plugin/bin/crew" "$@"; }
crewpy() { as "$HOST" python3 "$CREW/plugin/lib/crew.py" "$@"; }
remote() { echo "$T/remotes/$1.git"; }

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "ok: $*"; }
# expect_ok <cmd...>: it succeeds; its output is in $out
expect_ok() { out=$("$@" 2>&1) || fail "expected success: $*"$'\n'"$out"; }
# expect_fail <text> <cmd...>: it fails, saying <text>; its output is in $out
expect_fail() {
  local want=$1; shift
  if out=$("$@" 2>&1); then fail "expected failure: $*"$'\n'"$out"; fi
  [[ $out == *"$want"* ]] || fail "expected '$want' from: $*"$'\n'"$out"
}
has() { [[ $1 == *"$2"* ]] || fail "expected '$2' in:"$'\n'"$1"; }
lacks() { [[ $1 != *"$2"* ]] || fail "did not expect '$2' in:"$'\n'"$1"; }
eq() { [[ $1 == "$2" ]] || fail "expected '$2', got '$1'"; }
calls() { cat "$CREW_TEST_LOG"; }
launches() { cat "$CREW_TEST_CLAUDE_LOG"; }

fixtures() {  # the teams file (version $1, default 2) and the hosts file, written into every host's HOME
  local v=${1:-2} h
  for h in mac-studio chuck-herdr-alpha; do
    mkdir -p "$(home_of $h)/.config/crew" "$(home_of $h)/.config/swancloud"
    hosts_json > "$(home_of $h)/.config/swancloud/herdr-hosts.json"
    if [[ $v == 1 ]]; then teams_v1; else teams_json; fi > "$(home_of $h)/.config/crew/teams.json"
  done
}

teams_json() { cat <<'EOF'
{ "version": 2,
  "partitions": [
    { "label": "wldn", "partition": "clients/willdan", "blueprints": ["WilldanGroup/willdan-blueprints"],
      "state": "WilldanGroup/crew-state",
      "machine": "chuck-herdr-alpha", "session": "wldn-3" },
    { "label": "madswan", "partition": "business", "blueprints": ["afterthought/blueprints", "agentplot/blueprints"],
      "state": "afterthought/crew-state",
      "machine": "mac-studio", "session": "madswan-1" },
    { "label": "swancloud", "partition": "personal", "blueprints": ["afterthought/blueprints"],
      "state": "afterthought/crew-state",
      "machine": "mac-studio", "session": "swancloud-1" } ],
  "teams": [
    { "name": "swb-1", "system": "Switchboard", "machine": "chuck-herdr-alpha", "session": "wldn-1",
      "units": 4, "repos": ["switchboard-kit", "willdan-blueprints"] },
    { "name": "swb-2", "system": "Switchboard", "machine": "chuck-herdr-alpha", "session": "wldn-1",
      "units": 2, "repos": ["switchboard-kit", "willdan-blueprints"] },
    { "name": "brd-1", "system": "Breadboard", "machine": "chuck-herdr-alpha", "session": "wldn-2",
      "units": 2, "repos": ["breadboard-kit", "willdan-blueprints"] },
    { "name": "atl-1", "system": "Atlas", "machine": "mac-studio", "session": "wldn-5",
      "units": 2, "repos": ["atlas-kit", "willdan-blueprints"] },
    { "name": "apk-1", "system": "Flywheel", "machine": "mac-studio", "session": "madswan-2",
      "units": 4, "repos": ["flywheel-next", "blueprints"] } ] }
EOF
}

teams_v1() { cat <<'EOF'
{"teams":[{"coders":4,"machine":"chuck-herdr-alpha","name":"swb-1","repos":["switchboard-kit","willdan-blueprints"],"session":"wldn-1","system":"Switchboard"}],"version":1}
EOF
}

hosts_json() {
  python3 - "$T" <<'EOF'
import json, sys
T = sys.argv[1]
def sess(host, space, partition, repos, account="ia"):
    return {"dir": f"{T}/hosts/{host}/work/{space}", "account": account, "partition": partition, "repos": repos}
box_repos = ["afterthought/crew", "WilldanGroup/atlas-kit", "WilldanGroup/breadboard-kit",
             "WilldanGroup/switchboard-kit", "WilldanGroup/willdan-blueprints"]
mac_willdan = ["WilldanGroup/atlas-kit", "WilldanGroup/breadboard-kit", "WilldanGroup/switchboard-kit",
               "WilldanGroup/willdan-blueprints"]
mac_madswan = ["afterthought/blueprints", "afterthought/crew", "afterthought/swancloud"]
mac_agentplot = ["agentplot/blueprints", "agentplot/flywheel-next"]
box = "chuck-herdr-alpha"
hosts = {
  box: {"kind": "nixos", "ssh": box, "home": f"{T}/hosts/{box}/home", "supervised": True, "roamgate": True, "registered": True,
        "sessions": {"willdan": sess(box, "willdan", None, box_repos, "credits"),
                     "wldn": sess(box, "willdan", "clients/willdan", box_repos, "willdan-alex"),
                     "wldn-1": sess(box, "willdan", "clients/willdan", box_repos),
                     "wldn-2": sess(box, "willdan", "clients/willdan", box_repos, "willdan-alex"),
                     "wldn-3": sess(box, "willdan", "clients/willdan", box_repos, "credits")}},
  "mac-studio": {"kind": "darwin", "ssh": "mac-studio", "home": f"{T}/hosts/mac-studio/home", "supervised": True, "roamgate": True,
        "registered": True,
        "sessions": {"agentplot": sess("mac-studio", "agentplot", None, mac_agentplot, "credits"),
                     "wldn": sess("mac-studio", "willdan", "clients/willdan", mac_willdan, "willdan-alex"),
                     "wldn-5": sess("mac-studio", "willdan", "clients/willdan", mac_willdan),
                     "madswan": sess("mac-studio", "madswan", "business", mac_madswan, "madswan"),
                     "madswan-1": sess("mac-studio", "madswan", "business", mac_madswan, "madswan"),
                     "madswan-2": sess("mac-studio", "agentplot", "business", mac_agentplot, "madswan"),
                     "swancloud": sess("mac-studio", "madswan", "personal", mac_madswan, "madswan"),
                     "swancloud-1": sess("mac-studio", "madswan", "personal", mac_madswan, "madswan")}},
}
print(json.dumps({"version": 1, "hosts": hosts}, indent=1))
EOF
}

gitconfig() {  # every host's git: an identity, and github.com over https rewritten to the bare remotes here
  cat > "$1/.gitconfig" <<EOF
[user]
	name = Test User
	email = test@example.com
[init]
	defaultBranch = main
[advice]
	detachedHead = false
[protocol "file"]
	allow = always
[url "file://$T/remotes/"]
	insteadOf = https://github.com/
EOF
}

world() {  # hosts, fixtures, crew's checkout where each host's spaces keep it
  local h
  gitconfig "$HOME"
  for h in mac-studio chuck-herdr-alpha; do mkdir -p "$(home_of $h)" "$T/hosts/$h/work"; gitconfig "$(home_of $h)"; done
  fixtures "${1:-2}"
  mkdir -p "$(space chuck-herdr-alpha willdan)/crew" "$(space mac-studio madswan)/crew"
  ln -s "$CREW" "$(space chuck-herdr-alpha willdan)/crew/main"
  ln -s "$CREW" "$(space mac-studio madswan)/crew/main"
  state_repo WilldanGroup/crew-state; state_repo afterthought/crew-state
}

# state_repo <owner/name>: an empty bare remote, as a state repository is before crew state init
state_repo() { local r; r=$(remote "$1"); mkdir -p "$(dirname "$r")"; [ -d "$r" ] || git init -q --bare "$r"; }

commit_all() { git -C "$1" add -A && git -C "$1" commit -qm "${2:-wip}"; }
# rewrite <file> <sed script>: the file edited in place, alike under macOS's sed and the GNU sed devenv's shell puts first
rewrite() { sed -e "$2" "$1" > "$1.new" && mv "$1.new" "$1"; }

# kit <host> <space> <name>: a kit's main checkout at <space>/<name>/main, with OpenSpec set up
kit() {
  local d; d=$(space "$1" "$2")/$3/main
  mkdir -p "$d/openspec/changes/archive" "$d/openspec/specs"
  git init -q "$d"; printf 'schema: spec-driven\n' > "$d/openspec/config.yaml"
  touch "$d/openspec/changes/archive/.keep" "$d/openspec/specs/.keep"; echo "# $3" > "$d/README.md"
  commit_all "$d" "chore: start $3"
  echo "$d"
}

# blueprints <owner/name>: a bare remote with signals/moves.rec and .gitattributes on main
blueprints() {
  local r w; r=$(remote "$1"); w=$T/seed-${1//\//-}
  mkdir -p "$(dirname "$r")"; git init -q --bare "$r"
  git init -q "$w"; mkdir -p "$w/signals"
  cat > "$w/signals/moves.rec" <<'EOF'
# One move per signal, appended through crew.

%rec: Move
%mandatory: Signal Move Date By
%allowed: Signal Move Target Reason Date By
%type: Move enum attach challenge new-territory answered drop route
%type: Date date
%key: Signal
%doc: A curation move over one signal, stored with its inputs.
EOF
  printf 'signals/moves.rec merge=union\n' > "$w/.gitattributes"
  commit_all "$w" "chore: start" && git -C "$w" push -q "$r" main
  echo "$r"
}

# clone <owner/name> <dir>: a checkout of a bare remote, as a session's space keeps it
clone() { git clone -q "$(remote "$1")" "$2"; }

# change <dir> <name> [done] [total]: an OpenSpec change with planning complete and <done> of <total> tasks ticked
change() {
  local c=$1/openspec/changes/$2 i n=${4:-3} d=${3:-0}
  mkdir -p "$c/specs/x"
  printf '# Proposal\n\n## Why\n\nx\n\n## What Changes\n\n- y\n' > "$c/proposal.md"
  printf '# Design\n\nz\n' > "$c/design.md"
  printf '## ADDED Requirements\n\n### Requirement: X\nThe system SHALL x.\n\n#### Scenario: s\n- **WHEN** a\n- **THEN** b\n' > "$c/specs/x/spec.md"
  { echo "## 1. Work"; echo; for ((i = 1; i <= n; i++)); do if ((i <= d)); then echo "- [x] 1.$i task $i"; else echo "- [ ] 1.$i task $i"; fi; done; } > "$c/tasks.md"
}

# path_without <cmd>: this PATH less every directory holding <cmd>, with the tools crew needs kept by link
path_without() {
  local keep=$T/keep-$1 d c p=
  mkdir -p "$keep"
  for c in bash env python3 git jq awk sed grep tr cat head tail sort cut mkdir mktemp rm mv ls dirname basename seq; do
    d=$(command -v "$c" 2>/dev/null) && [[ $d == /* ]] && ln -sf "$d" "$keep/$c"
  done
  local IFS=:
  for d in $PATH; do [[ -x $d/$1 ]] || p=$p:$d; done
  echo "$keep$p"
}

# edit <teams|hosts> <python>: change a fixture on every host; the python statement changes `d` in place
edit() {
  local f h
  for h in mac-studio chuck-herdr-alpha; do
    case $1 in teams) f=$(home_of $h)/.config/crew/teams.json ;; hosts) f=$(home_of $h)/.config/swancloud/herdr-hosts.json ;; esac
    python3 -c 'import json, sys
f = sys.argv[1]; d = json.load(open(f))
exec(sys.argv[2])
json.dump(d, open(f, "w"), indent=1)' "$f" "$2"
  done
}
team() { echo "[t for t in d['teams'] if t['name'] == '$1'][0]"; }
part() { echo "[p for p in d['partitions'] if p['label'] == '$1'][0]"; }

# race <owner/name> <host> <agent> <crew args...>: the next push to that remote first lets this crew write land,
# run as <agent> on <host> from the remote's pre-receive hook, so the push in flight finds the branch moved.
race() {
  local r; r=$(remote "$1"); shift
  local host=$1 who=$2; shift 2
  printf 'CREW_TEST_HOST=%q HOME=%q CREW_AGENT=%q %q' "$host" "$(home_of "$host")" "$who" "$CREW/plugin/bin/crew" > "$T/race"
  printf ' %q' "$@" >> "$T/race"
  cat > "$r/hooks/pre-receive" <<'HOOK'
#!/usr/bin/env bash
refs=$(cat)
# With $CREW_TEST_ROOT/race.ref, only a push to that ref lets the competing write in.
if [ -f "$CREW_TEST_ROOT/race.ref" ] && ! grep -q " $(cat "$CREW_TEST_ROOT/race.ref")\$" <<<"$refs"; then exit 0; fi
if [ -f "$CREW_TEST_ROOT/race" ]; then
  cmd=$(cat "$CREW_TEST_ROOT/race"); rm "$CREW_TEST_ROOT/race"
  (unset $(env | sed -n 's/^\(GIT_[A-Z_]*\)=.*/\1/p'); cd /; eval "$cmd") >> "$CREW_TEST_ROOT/race.log" 2>&1
fi
exit 0
HOOK
  chmod +x "$r/hooks/pre-receive"
}

# place <kit main> <bolt> <unit>: the unit's worktree, made the way construct makes it
place() {
  local kd; kd=$(dirname "$1")
  git -C "$1" worktree add -q --track -b "unit/$3" "$kd/places/$3" "bolt/$2"
  echo "$kd/places/$3"
}
# stage <unit> [label]: the unit's stage as crew bolts reads it
stage() { crew bolts --label "${2:-wldn}" --json | jq -r --arg u "$1" '[.partitions[].plans[].bolts[].units[] | select(.unit == $u) | .stage] | first // "none"'; }

# transcript <host> <session> [account folder]: a Claude Code transcript of that session on the host, its JSON lines
# read from standard input, in the account's folder (~/.claude unless named); prints its path
transcript() {
  local d; d=$(home_of "$1")/${3:-.claude}/projects/-work
  mkdir -p "$d"; cat > "$d/$2.jsonl"; echo "$d/$2.jsonl"
}

# ago <minutes>: the UTC time that many minutes ago, as a transcript's records carry it
ago() { python3 -c 'import datetime, sys; t = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=float(sys.argv[1])); print(t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z")' "$1"; }

# herdr_state <host> <session> <jq>: what the stub herdr holds there
herdr_state() { jq -r "$3" "$(home_of "$1")/.stub-herdr/$2.json"; }
# team_world: the box's switchboard-kit and willdan-blueprints checkouts, and the plan with swb-1 holding a bolt
team_world() {
  world
  wb=$(blueprints WilldanGroup/willdan-blueprints); ws=$(remote WilldanGroup/crew-state)
  k=$(kit chuck-herdr-alpha willdan switchboard-kit); kd=$(dirname "$k")
  clone WilldanGroup/willdan-blueprints "$(space chuck-herdr-alpha willdan)/willdan-blueprints/main"
  crew state init wldn >/dev/null
}
