# A partition's main level and its operator through the crew command on the stubs (tests.11, record 0022), a part of
# the teams journey (t-journey-teams): crew main up starts the main level and a dispatcher on each host of the
# partition, each greeted once, one waiting on a question holding back no other; main status reaches every host; a
# tell records its length and never its text; the operator gets its tabs; and crew revive brings back what a restart
# left empty, leaving down what was taken down. What each agent is greeted with and where it runs are logic cases
# (tests/py/test_teams.py).
# Reads: plugin/hooks/ tests/teams.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/teams.sh"

# The main level, with the planner stopped on a question as it starts: the others are greeted meanwhile.
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
answer() {
  local i
  for i in $(seq 6000); do
    grep -q "agent prompt wldn-design '" "$CREW_TEST_LOG" && grep -q "agent prompt wldn-ops '" "$CREW_TEST_LOG" &&
      grep -q "^$box wldn-3 agent get wldn-planner\$" "$CREW_TEST_LOG" && break
    /bin/sleep 0.1
  done
  as $box herdr --session wldn-3 stub status wldn-planner idle
}
answer &
CREW_TEST_BLOCKED=wldn-planner expect_ok crew main up wldn
wait
for a in wldn-design wldn-planner wldn-ops wldn-dispatch-chuck-herdr-alpha wldn-dispatch-mac-studio; do has "$out" "$a started"; has "$out" "$a greeted"; done
has "$out" "wldn-planner is waiting on a question in its pane; answer it there and it will be greeted"
eq "$(herdr_state $box wldn-3 '[.workspaces[].label] | join(",")')" "wldn,wldn dispatch"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "design,planner,ops"
eq "$(herdr_state mac-studio wldn-5 '[.agents[].name] | map(select(startswith("wldn-"))) | join(",")')" "wldn-dispatch-mac-studio"
eq "$(jq -r 'select(.agent == "wldn-design") | "\(.host) \(.argv[1]) \(.argv[3])"' "$CREW_TEST_CLAUDE_LOG")" "$box claude-fable-5-1 xhigh"
eq "$(jq -r 'select(.agent == "wldn-dispatch-mac-studio") | "\(.host) \(.argv[3]) \(.cwd)"' "$CREW_TEST_CLAUDE_LOG")" "mac-studio medium $(space mac-studio willdan)/willdan-blueprints/main"
grep -q "^$box ssh mac-studio .*agent \(get\|prompt\) wldn-dispatch-mac-studio" "$CREW_TEST_LOG" && fail "mac-studio's dispatcher was greeted from another host"
at() { grep -n "$1" "$CREW_TEST_LOG" | head -1 | cut -d: -f1; }
answered=$(at "stub status wldn-planner idle")
(( $(at "agent prompt wldn-design '") < answered && answered < $(at "agent prompt wldn-planner '") )) ||
  fail "the planner's question held back the design agent, or the planner was greeted before it was answered"
eq "$(field $box main.up On agent/wldn-design)" "agent/wldn-design agent/wldn-planner agent/wldn-ops"
eq "$(field mac-studio main.up On)" "agent/wldn-dispatch-mac-studio"
expect_ok crew main up wldn
has "$out" "wldn-design is already up"; lacks "$out" "greeted"
eq "$(count $box main.up)" "2"
ok "crew main up starts the main level on its host and a dispatcher on each host of the partition, greeting each once, one waiting on a question once it is answered and holding back no other; a second starts and records nothing"

expect_ok crew main status wldn
for a in wldn-design wldn-planner wldn-ops wldn-dispatch-chuck-herdr-alpha wldn-dispatch-mac-studio; do has "$(grep "^$a " <<<"$out")" "idle"; done
crew tell wldn-planner "Secret words ZQXR" >/dev/null
eq "$(field mac-studio tell Chars)" "17"
[[ $(as mac-studio bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec') != *ZQXR* ]] || fail "a tell's text is in the run record"
expect_ok crew operator up wldn
has "$out" "wldn-operator-mac-studio started"; has "$out" "wldn-operator-mac-studio greeted"
eq "$(herdr_state mac-studio wldn '[.tabs[].label] | join(",")')" "operator,flow,rail,board"
grep -q "^mac-studio wldn pane run .*/crew _rail wldn'" "$CREW_TEST_LOG" || fail "the rail tab does not run wldn's rail"
(( $(grep -n -- "tab create .*--label rail" "$CREW_TEST_LOG" | head -1 | cut -d: -f1) < $(grep -n "agent prompt wldn-operator-mac-studio '" "$CREW_TEST_LOG" | head -1 | cut -d: -f1) )) ||
  fail "the operator agent was greeted before its rail tab was open"
: > "$CREW_TEST_LOG"
expect_ok crew operator up wldn
has "$out" "wldn-operator-mac-studio is already up"
grep -q "workspace create\|tab create\|pane run\|agent prompt" "$CREW_TEST_LOG" && fail "a second operator up made, ran or greeted something"
ok "main status reaches every host, a tell records its length and never its text, and the operator comes up with its flow, rail and board tabs, greeted once its rail is open"

# A restart: herdr brings each tab back as its shell alone. operator up, which the fleet runs every five minutes, runs
# each tab's command there again, and leaves a pane running something else.
pane() { awk -v r="$1" '$1 == r {print $2}' "$(home_of mac-studio)/.local/state/crew/wldn-operator/panes"; }
for t in flow rail board; do as mac-studio herdr --session wldn stub restore "$(pane $t)"; done
as mac-studio herdr --session wldn pane run "$(pane board)" "less notes" >/dev/null
: > "$CREW_TEST_LOG"
expect_ok crew operator up wldn
grep -q "^mac-studio wldn pane run $(pane flow) .*/crew events --follow --label wldn'" "$CREW_TEST_LOG" || fail "the flow tab's follow was not run again"
grep -q "^mac-studio wldn pane run $(pane rail) .*/crew _rail wldn'" "$CREW_TEST_LOG" || fail "the rail tab's loop was not run again"
grep -q "pane run $(pane board) " "$CREW_TEST_LOG" && fail "crew typed into a board tab running something else"
grep -q "workspace create\|tab create\|agent prompt" "$CREW_TEST_LOG" && fail "a restored operator workspace was opened again or greeted"
has "$out" "wldn's rail tab ($(pane rail)) held its shell alone; its rail runs there again"
has "$out" "wldn's board tab ($(pane board)) runs less notes, not crew's board; crew left it"
: > "$CREW_TEST_LOG"
expect_ok crew operator up wldn
grep -q "pane run" "$CREW_TEST_LOG" && fail "operator up ran a tab's command over one already running"
ok "after a restart, operator up runs each tab's command again in the shell herdr brought back, once, and leaves a tab running something else"

# After a restart: panes back with no agent in them are revived, resumed or fresh; a team taken down stays down.
gone() { local p; p=$(as $box herdr --session "$1" agent get "$2" | jq -r .result.agent.pane_id); as $box herdr --session "$1" agent prompt "$p" /exit >/dev/null; }
crew up swb-1 >/dev/null; crew up swb-2 >/dev/null; crew down swb-2 >/dev/null
CREW_TEST_NO_MESSAGE=1 crew restart swb-1 ops --no-greet >/dev/null  # an ops never spoken to, with no conversation
gone wldn-1 swb-1-conductor; gone wldn-1 swb-1-ops; gone wldn-3 wldn-design
: > "$CREW_TEST_CLAUDE_LOG"; : > "$CREW_TEST_LOG"
HOST=$box expect_ok crew revive
has "$out" "swb-1-conductor resumed"; has "$out" "wldn-design resumed"
has "$out" "swb-1-ops has no conversation to resume; starting it fresh"
has "$out" "swb-2 was taken down; it stays down"
for a in wldn-planner wldn-ops swb-2-conductor; do eq "$(jq -r --arg a $a 'select(.agent == $a)' "$CREW_TEST_CLAUDE_LOG" | wc -l | tr -d ' ')" "0"; done
eq "$(greetings $box wldn-1 swb-1-conductor)" "1"; eq "$(greetings $box wldn-3 wldn-design)" "1"; eq "$(greetings $box wldn-1 swb-1-ops)" "1"
grep -q "agent prompt wldn-planner '" "$CREW_TEST_LOG" && fail "an agent that came back by itself was greeted"
HOST=$box crew main down wldn >/dev/null
eq "$(herdr_state $box wldn-3 '.agents | length') $(herdr_state mac-studio wldn-5 '[.agents[].name] | map(select(startswith("wldn-dispatch"))) | length')" "0 0"
: > "$CREW_TEST_CLAUDE_LOG"
HOST=$box expect_ok crew revive
has "$out" "wldn was taken down; it stays down"
eq "$(wc -l < "$CREW_TEST_CLAUDE_LOG" | tr -d ' ')" "0"
echo mac-studio > "$T/down"
HOST=$box expect_fail "mac-studio port 22: Operation timed out" crew main up wldn
has "$out" "wldn-dispatch-$box started"; has "$out" "wldn-dispatch-$box greeted"
rm "$T/down"
ok "crew revive brings back the agents whose panes came back empty and greets each it brought back once, a team's ops it had to start fresh among them; a team or main level taken down stays down; main down reaches every host, and a host that does not answer fails main up once the others are up"
