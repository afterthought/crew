# The units journey's world, which each of its parts sources after lib.sh: a team world whose kit declares its toolchain
# and the moon runner in .config/sluice.toml, beside its bolt branches' checks, and holds a file the units share; the
# team's state files on the box; and the helpers the parts read it with. The kit's toolchain, tools/print, puts the
# kit's own stand-in moon on PATH, which no other PATH holds, so a moon the log shows ran inside the toolchain crew kept
# for that worktree: it logs "<where> <args> <the worktree the toolchain was printed for>" to $T/moon.log, prints moon
# 2.6.1 for --version, and fails setup while $T/moon-fails exists.
command -v wt >/dev/null || fail "this test needs worktrunk's wt"
team_world
box=chuck-herdr-alpha
mkdir -p "$k/.config" "$k/tools/bin"
printf '[tests]\ntoolchain = ["sh", "tools/print"]\nrunner = "moon"\n' >> "$k/.config/sluice.toml"
cat > "$k/tools/print" <<'PRINT'
#!/bin/sh
echo "export PATH=\"$(pwd -P)/tools/bin:\$PATH\" TOOLCHAIN_FROM=\"$(pwd -P)\""
PRINT
cat > "$k/tools/bin/moon" <<MOON
#!/bin/sh
echo "\$(pwd -P) \$* \${TOOLCHAIN_FROM:-none}" >> "$T/moon.log"
[ "\$1" = --version ] && { echo "moon 2.6.1"; exit 0; }
[ -e "$T/moon-fails" ] && { echo "stand-in moon: setup failed" >&2; exit 1; }
exit 0
MOON
chmod +x "$k/tools/print" "$k/tools/bin/moon"; printf 'one\ntwo\nthree\n' > "$k/shared.txt"
commit_all "$k" "chore: the kit's toolchain and runner, and a file the units share"; push "$k"
# ready <worktree>: how many times moon setup ran in that worktree, inside the toolchain printed for it
ready() { local w; w=$(cd "$1" && pwd -P); grep -c "^$w setup $w\$" "$T/moon.log" || true; }
export CREW_LABEL=wldn
slots=$(home_of $box)/.local/state/swb-1-team/slots
stages=$(home_of $box)/.local/state/swb-1-team/stages
reports=$(home_of $box)/.local/state/swb-1-team/reports
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
subject() { git --git-dir "$ws" log -1 --format=%s "$(act_tip)"; }
short() { git -C "$k" rev-parse --short "$1"; }
pane() { herdr_state $box wldn-1 ".agents | to_entries[] | select(.value.name == \"$1\") | .key"; }
status() { as $box herdr --session wldn-1 stub status "$(pane "$1")" "$2"; }
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | grep -v " /exit$" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
sent() { grep -cF "$box wldn-1 agent prompt $1 $2" "$CREW_TEST_LOG" || true; }
told() { grep "^$box wldn-1 agent prompt $1 '\[crew" "$CREW_TEST_LOG" || true; }
last_launch() { tail -1 "$CREW_TEST_CLAUDE_LOG" | jq -r '([.argv | to_entries[] | select(.value == "--name") | .key][0]) as $i | "\(.argv[0:4] | join(" ")) | \(.argv[$i + 1]) | \(.cwd)"'; }
# field <host> <act> <field> [object...]: a field of that host's last entry of the act naming every object given
field() {
  local h=$1 a=$2 f=$3; shift 3
  as "$h" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and all(o in e["On"] for o in sys.argv[3:])]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$a" "$@" | jq -r --arg f "$f" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'
}
record_of() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null'; }
hands=0
# by_hand <python>: plan.rec changed on the branch in one commit, the python statement changing p, a plan.Plan
by_hand() {
  local w=$T/hand-$((hands += 1)); git clone -q -b wldn/main "$ws" "$w"
  python3 - "$CREW/plugin/lib" "$w/plan.rec" "$1" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
unit = lambda name, bolt, *after: p.insert(plan.Rec("Unit", [("Unit", name), ("Repo", "switchboard-kit"), ("Bolt", bolt),
                                                         ("Intent", f"Unit {name}.")] + [("After", x) for x in after]))
exec(sys.argv[3])
open(f, "w").write(p.text())
PY
  commit_all "$w" "plan: by hand"; git -C "$w" push -q origin wldn/main
}
# touches <unit> <entries...>: the unit's proposal ends with a Touches block holding the entries, committed in its place
touches() {
  local u=$1 f=$kd/places/$1/openspec/changes/$1/proposal.md; shift
  printf '# Proposal\n\n## Why\n\nx\n\n## What Changes\n\n- y\n\n## Touches\n\n```\n' > "$f"; printf '%s\n' "$@" >> "$f"; echo '```' >> "$f"
  commit_all "$kd/places/$u" "docs($u): touches"
}
tick() { rewrite "$kd/places/$1/openspec/changes/$1/tasks.md" "s/- \[ \] $2/- [x] $2/"; commit_all "$kd/places/$1" "feat($1): task $2"; }

# Shims ahead of the real git, python3 and openspec log, per host, each fetch of a state branch, each gather.py piped to
# a host and each openspec run, on a PATH with $T/shim first; reads <what>: how many the box logged.
mkdir -p "$T/shim"
shim() {  # shim <command> <bash test of "$@" that logs <what>> <what>
  printf '#!/usr/bin/env bash\nif %s; then echo "${CREW_TEST_HOST:-?} %s" >> %q; fi\nexec %q "$@"\n' "$2" "$3" "$T/reads.log" "$(command -v "$1")" > "$T/shim/$1"
  chmod +x "$T/shim/$1"
}
shim git '[[ " $* " == *" fetch "*refs/crew/* ]]' fetch
shim python3 '[[ ${1:-} == - && ${2:-} == "{"* ]]' gather
shim openspec true openspec
reads() { grep -c "^$box $1\$" "$T/reads.log" || true; }
# units_world <python>: swb-1 up, holding tenant-environments, whose units by_hand's python adds; the stub sluice
# forecasts the bolt against main with no conflict (teams.21) until a part writes another forecast or removes it
units_world() {
  crew up swb-1 >/dev/null
  by_hand 'p.insert(plan.Rec("Bolt", [("Bolt", "tenant-environments"), ("Repo", "switchboard-kit"), ("Goal", "Tenants hold environments.")]))
'"$1"
  crew bolt give swb-1 >/dev/null
  clean_forecast
}
# clean_forecast: sluice forecasts tenant-environments against main with no conflict
clean_forecast() {
  printf '{"conflict":null,"head":"%s","onto":"%s","ahead":[]}\n' "$(git -C "$k" rev-parse bolt/tenant-environments)" \
    "$(git -C "$k" rev-parse main)" > "$T/sluice-check-bolt-tenant-environments.json"
}
