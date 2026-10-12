# Team, main-level and operator commands record what they do to agents, on the host where they run, naming who asked
# from wherever they asked; tells record their length, never their text. The operator workspace follows the run record
# in a flow tab, keeps what waits on the user in a rail tab, with a shell below it, and draws the board in a board tab
# after it. What a stage's start and end record is the journey's (t-journey-units).
# Reads: plugin/hooks/ plugin/roles/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
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
eq "$(herdr_state mac-studio wldn '[.tabs[] | select(.label == "rail")] | length')" "1"
rail=$(herdr_state mac-studio wldn '.tabs | to_entries[] | select(.value.label == "rail") | .key')
eq "$(herdr_state mac-studio wldn "[.panes[] | select(.tab == \"$rail\")] | length")" "2"
grep -q "^mac-studio wldn pane run .*/crew _rail wldn'" "$CREW_TEST_LOG" || fail "the rail tab does not run wldn's rail"
grep -qF "export PATH=$CREW/plugin/bin:\$PATH" "$CREW_TEST_LOG" || fail "the rail tab's shell does not have crew on its path"
eq "$(herdr_state mac-studio wldn '[.tabs[] | select(.label == "board")] | length')" "1"
eq "$(herdr_state mac-studio wldn '[.tabs[] | select(.label == "rail" or .label == "board") | .label] | join(" ")')" "rail board"
board=$(herdr_state mac-studio wldn '.tabs | to_entries[] | select(.value.label == "board") | .key')
eq "$(herdr_state mac-studio wldn "[.panes[] | select(.tab == \"$board\")] | length")" "1"
grep -q "^mac-studio wldn pane run .*/crew _board wldn'" "$CREW_TEST_LOG" || fail "the board tab does not draw wldn's board"
: > "$CREW_TEST_LOG"
expect_ok crew operator up wldn
eq "$(herdr_state mac-studio wldn '[.tabs[] | select(.label == "flow")] | length')" "1"
eq "$(herdr_state mac-studio wldn '[.tabs[] | select(.label == "rail")] | length')" "1"
eq "$(herdr_state mac-studio wldn '[.tabs[] | select(.label == "board")] | length')" "1"
grep -q "pane run\|pane split\|tab create" "$CREW_TEST_LOG" && fail "a second operator up opened or ran something"
eq "$(count mac-studio operator.up)" "1"
ok "operator up records the agent it starts and opens one flow tab following the run record, one rail tab, the list above a shell, and one board tab after it drawing the board; a second run does none of it"

op=$(herdr_state mac-studio wldn '.agents | to_entries[] | select(.value.name == "wldn-operator-mac-studio") | .key')
CREW_AGENT=wldn-operator-mac-studio crew up swb-1 >/dev/null 2>&1
eq "$(field $box team.up On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
eq "$(field $box team.up By)" "wldn-operator-mac-studio"
eq "$(field $box team.up Session)" "mac-studio:sid-${op//:/-}"
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
crew unit add a "Unit a." --bolt tenant-environments >/dev/null
crew bolt give swb-1 >/dev/null 2>&1
eq "$(field mac-studio bolt.give On)" "bolt/tenant-environments team/swb-1"
eq "$(field $box agent.restart On agent/swb-1-conductor)" "team/swb-1 agent/swb-1-conductor"
eq "$(field $box agent.restart By agent/swb-1-ops)" "$user@mac-studio"
crew unit add f "Unit f." --bolt tenant-environments >/dev/null 2>&1
eq "$(field mac-studio tell On agent/swb-1-conductor)" "agent/swb-1-conductor"
[[ $(record_of mac-studio; record_of $box) != *ZQXR* ]] || fail "a tell's text is in the run record"
ok "a tell records the recipient and its length, never its text, and so do the tells a write sends; a give's restarts are recorded"

unset CREW_AGENT
expect_ok crew restart swb-1 ops
eq "$(field $box agent.restart On agent/swb-1-ops)" "team/swb-1 agent/swb-1-ops"
expect_ok crew clear swb-1 ops
eq "$(field $box agent.clear On)" "team/swb-1 agent/swb-1-ops"
expect_ok crew down swb-1 --force
has "$(field $box team.down On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
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
