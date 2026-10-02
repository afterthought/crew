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
unset CREW_AGENT CREW_LABEL HERDR_PANE_ID HERDR_WORKSPACE_ID HERDR_TAB_ID HERDR_ENV GIT_DIR GIT_WORK_TREE
HOST=${HOST:-mac-studio}
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"

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
      "machine": "chuck-herdr-alpha", "session": "wldn-3" },
    { "label": "madswan", "partition": "business", "blueprints": ["afterthought/blueprints", "agentplot/blueprints"],
      "machine": "mac-studio", "session": "madswan-1" },
    { "label": "swancloud", "partition": "personal", "blueprints": ["afterthought/blueprints"],
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
  for h in mac-studio chuck-herdr-alpha; do mkdir -p "$(home_of $h)" "$T/hosts/$h/work"; gitconfig "$(home_of $h)"; done
  fixtures "${1:-2}"
  mkdir -p "$(space chuck-herdr-alpha willdan)/crew" "$(space mac-studio madswan)/crew"
  ln -s "$CREW" "$(space chuck-herdr-alpha willdan)/crew/main"
  ln -s "$CREW" "$(space mac-studio madswan)/crew/main"
}

commit_all() { git -C "$1" add -A && git -C "$1" commit -qm "${2:-wip}"; }

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
# Curation moves — append-only. One record per curated signal.

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
