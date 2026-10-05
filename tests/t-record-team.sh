# Team, main-level and operator commands record what they do to agents, on the host where they run, naming who asked
# from wherever they asked; tells record their length, never their text. A stage's start is an entry, and its end is
# one too: when crew unit wait sees it settle, or late, once, when the next command reads the team. Refusals that
# would have moved work are entries. The operator workspace follows the run record in a flow tab.
. "$TESTS/lib.sh"
team_world
box=chuck-herdr-alpha
mkdir -p "$(space mac-studio willdan)/willdan-blueprints/main"
last() {
  as "$1" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and all(o in e["On"] for o in sys.argv[3:])]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "${@:2}"
}
# field <host> <act> <field> [object...]: a field of the last entry of the act naming every object given
field() { local h=$1 a=$2 f=$3; shift 3; last "$h" "$a" "$@" | jq -r --arg f "$f" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'; }
count() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null' | grep -c "^Act: $2\$" || true; }
record_of() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null'; }
user=$(python3 -c 'import getpass; print(getpass.getuser())')
export CREW_LABEL=wldn

expect_ok crew operator up wldn
eq "$(field mac-studio operator.up On)" "agent/wldn-operator-mac-studio"
eq "$(field mac-studio operator.up By)" "$user@mac-studio"
eq "$(herdr_state mac-studio wldn '[.tabs[] | select(.label == "flow")] | length')" "1"
grep -q "^mac-studio wldn pane run .* events --follow --label wldn" "$CREW_TEST_LOG" || fail "the flow tab does not follow wldn's run record"
expect_ok crew operator up wldn
eq "$(herdr_state mac-studio wldn '[.tabs[] | select(.label == "flow")] | length')" "1"
eq "$(count mac-studio operator.up)" "1"
ok "operator up records the agent it starts and opens one flow tab following the run record; a second run does neither"

op=$(herdr_state mac-studio wldn '.agents | to_entries[] | select(.value.name == "wldn-operator-mac-studio") | .key')
CREW_AGENT=wldn-operator-mac-studio crew up swb-1 >/dev/null 2>&1
eq "$(field $box team.up On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
eq "$(field $box team.up By)" "wldn-operator-mac-studio"
eq "$(field $box team.up Session)" "mac-studio:sid-$op"
eq "$(field mac-studio team.up On)" ""
eq "$(field $box greet On)" "agent/swb-1-conductor team/swb-1"
eq "$(count $box tell)" "0"
ok "a command run on the team's host records there, naming the agent that asked on mac-studio and its session; a greeting is one entry"

expect_ok crew main up wldn
eq "$(field $box main.up On agent/wldn-design)" "agent/wldn-design agent/wldn-planner agent/wldn-ops"
eq "$(field $box main.up On agent/wldn-dispatch-$box)" "agent/wldn-dispatch-$box"
eq "$(field mac-studio main.up On)" "agent/wldn-dispatch-mac-studio"
expect_ok crew main up wldn
eq "$(count $box main.up)" "2"; eq "$(count mac-studio main.up)" "1"
ok "main up records the agents it starts on each host, and a second main up that starts nothing records nothing"

crew tell wldn-planner "Secret words ZQXR" >/dev/null
eq "$(field mac-studio tell On)" "agent/wldn-planner"
eq "$(field mac-studio tell Chars)" "17"
eq "$(field mac-studio tell By)" "$user@mac-studio"
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b c e; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew bolt give swb-1 >/dev/null 2>&1
eq "$(field mac-studio bolt.give On)" "bolt/tenant-environments team/swb-1"
eq "$(field $box agent.restart On agent/swb-1-conductor)" "team/swb-1 agent/swb-1-conductor"
eq "$(field $box agent.restart By agent/swb-1-ops)" "$user@mac-studio"
crew unit add f "Unit f." --bolt tenant-environments >/dev/null 2>&1
eq "$(field mac-studio tell On agent/swb-1-conductor)" "agent/swb-1-conductor"
[[ $(record_of mac-studio; record_of $box) != *ZQXR* ]] || fail "a tell's text is in the run record"
ok "a tell records the recipient and its length, never its text, and so do the tells a write sends; a give's restarts are recorded"

export CREW_AGENT=swb-1-conductor
expect_ok crew unit run a construct
s1=$(herdr_state $box wldn-1 '.agents | to_entries[] | select(.value.name == "swb-1-unit-1") | .key')
as $box herdr --session wldn-1 stub status "$s1" working  # building, as a stage agent is until it settles
eq "$(field $box stage.start On stage/a/construct)" "stage/a/construct unit/a agent/swb-1-unit-1"
eq "$(field $box stage.start By stage/a/construct)" "swb-1-conductor"
stages=$(home_of $box)/.local/state/swb-1-team/stages
[[ $(cat "$stages") == "unit-1 a construct "*" unit/a" ]] || fail "the stages file does not owe construct's end: $(cat "$stages")"
change "$kd/places/a" a 0 2; commit_all "$kd/places/a" "docs(a): the change"
expect_fail "unit a is in review: code waits until the user approves it" crew unit run a code
eq "$(field $box stage.start On stage/a/code)" "unit/a stage/a/code"
has "$(field $box stage.start Refused stage/a/code)" "unit a is in review"
ok "a stage's start is recorded with its slot's agent and owed an end; code before the approval is a refused entry"

as $box herdr --session wldn-1 stub status "$s1" idle
expect_ok crew unit wait a
has "$out" "swb-1-unit-1 settled: a is in review"
eq "$(field $box stage.end On stage/a/construct)" "stage/a/construct unit/a agent/swb-1-unit-1"
eq "$(field $box stage.end Result stage/a/construct)" "review"
eq "$(field $box stage.end Head stage/a/construct)" "$(git -C "$k" rev-parse --short unit/a)"
eq "$(field $box stage.end Observed stage/a/construct)" ""
eq "$(cat "$stages")" ""
crew unit approve a >/dev/null
expect_ok crew unit run a code
s1=$(herdr_state $box wldn-1 '.agents | to_entries[] | select(.value.name == "swb-1-unit-1") | .key')
as $box herdr --session wldn-1 stub status "$s1" working
expect_ok crew unit wait a --timeout 10
has "$out" "swb-1-unit-1 is still working on a"
eq "$(count $box stage.end)" "1"
ok "crew unit wait records the stage's end with what it reached and the branch's head; a wait that times out records nothing"

expect_fail "swb-1-unit-1 is working; add --force to end it anyway" crew unit run a code
has "$(field $box stage.start Refused stage/a/code agent/swb-1-unit-1)" "swb-1-unit-1 is working"
sed -i '' 's/- \[ \] 1.1/- [x] 1.1/' "$kd/places/a/openspec/changes/a/tasks.md"; commit_all "$kd/places/a" "feat(a): task 1"
expect_fail "unit a is in code, with these tasks still open: 1.2 task 2" crew unit run a verify
eq "$(field $box stage.start Refused stage/a/verify)" "unit a is in code, with 1 task still open"
[[ $(record_of $box) != *"task 2"* ]] || fail "an open task's title is in the run record"
as $box herdr --session wldn-1 stub status "$s1" idle
expect_ok crew status swb-1
expect_ok crew status swb-1
eq "$(count $box stage.end)" "2"
eq "$(field $box stage.end Observed stage/a/code)" "late"
eq "$(field $box stage.end Result stage/a/code)" "code"
eq "$(field $box stage.end Tasks stage/a/code)" "1/2"
ok "a working agent without --force and verify before every task are refused entries; an unwaited end is recorded late, once"

expect_ok crew fix swb-1 tidy "The banner flickers ZQXS"
eq "$(field $box fix.start On)" "fix/tenant-environments/tidy bolt/tenant-environments agent/swb-1-unit-2"
expect_ok crew fix swb-1 tidy --merge
eq "$(field $box fix.merge On)" "fix/tenant-environments/tidy bolt/tenant-environments agent/swb-1-unit-2"
eq "$(field $box stage.end On fix/tenant-environments/tidy)" "fix/tenant-environments/tidy agent/swb-1-unit-2"
eq "$(field $box stage.end Observed fix/tenant-environments/tidy)" "late"
[[ $(record_of $box) != *ZQXS* ]] || fail "a fix's words are in the run record"
crew unit run b construct >/dev/null; crew unit run c construct >/dev/null
expect_fail "all 4 of swb-1's slots are in flight" crew unit run e construct
has "$(field $box stage.start Refused stage/e/construct)" "all 4 of swb-1's slots are in flight"
ok "a fix's start and merge are recorded, the fix's words are not, and a stage with no free slot is a refused entry"

unset CREW_AGENT
expect_ok crew restart swb-1 ops
eq "$(field $box agent.restart On agent/swb-1-ops)" "team/swb-1 agent/swb-1-ops"
expect_ok crew clear swb-1 ops
eq "$(field $box agent.clear On)" "team/swb-1 agent/swb-1-ops"
expect_ok crew down swb-1 --force
has "$(field $box team.down On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
has "$(field $box team.down On)" "agent/swb-1-unit-1"
expect_ok crew resume swb-1
eq "$(count $box agent.resume)" "2"
eq "$(field $box agent.resume On agent/swb-1-conductor)" "team/swb-1 agent/swb-1-conductor"
expect_ok crew main down wldn
eq "$(field $box main.down On agent/wldn-design)" "agent/wldn-design agent/wldn-planner agent/wldn-ops"
ok "restart, clear, down, resume and main down each record the agents they acted on"

expect_ok crewpy brief swb-1 conductor
has "$out" "unit wait <unit>"; lacks "$out" "herdr agent wait"
expect_ok crewpy brief wldn operator
has "$out" "trace"; lacks "$out" "{{"
ok "the conductor waits for a stage through crew, and the operator answers what happened from crew trace"
