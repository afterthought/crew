# A host's hold and crew's updates reaching its agents through the crew command on the stubs (teams.19), on wldn's
# main level, the standing agents its host runs: crew hold holds the host it names, tells each standing agent up there
# to finish its step, and records it; while it holds, crew starts no agent there; hold status says what still works;
# hold wait, once the host is quiet, ends every crew agent there with its pane kept; crew go lifts the hold and brings
# each back with its conversation, greeted; crew update hands each standing agent an update made due its restart, which
# brings it back on crew as it now is, told so; crew's Stop hook does the same at the end of a due agent's turn; --now
# ends every agent at once; and a standing agent whose role now runs as its kind is passed over by crew update and
# ended at its turn's end, never started again.
# What makes an agent due, what keeps a host from being quiet, when a due agent may be restarted and what the bands
# say are logic cases (tests/py/test_hold.py).
# Reads: plugin/hooks/ plugin/lib/board.py plugin/lib/hold.py plugin/lib/ops.py tests/teams.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/teams.sh"

# wldn's main level runs on the box, in its session wldn-3; mains says which of its agents herdr holds there.
here="wldn-design,wldn-operator,wldn-ops,wldn-planner"
mains() { herdr_state $box wldn-3 '[.agents[].name | select(startswith("wldn-dispatch") | not)] | sort | join(",")'; }
expect_ok crew main up wldn
: > "$CREW_TEST_LOG"
expect_ok crew hold $box "herdr 0.9.6"
has "$out" "$box is held: crew starts no agent here until crew go $box"
eq "$(jq -r .why "$(home_of $box)/.local/state/crew/hold")" "herdr 0.9.6"
for a in ${here//,/ }; do
  grep -q "^$box wldn-3 agent prompt $a '\[crew\] $box is held by $me@mac-studio: herdr 0.9.6. Finish the step you are in" "$CREW_TEST_LOG" ||
    fail "$a was not told the hold"
done
eq "$(field $box host.hold On)" "host/$box"
[[ $(as $box bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec') != *"herdr 0.9.6"* ]] || fail "the hold's words are in the run record"
expect_fail "$box is held by $me@mac-studio" crew main up wldn
HOST=$box expect_fail "$box is held by $me@mac-studio" crew revive
eq "$(mains)" "$here"
ok "crew hold holds the host it names, tells each standing agent up there, records it without its words, and crew starts no agent there meanwhile"

as $box herdr --session wldn-3 stub status wldn-design working >/dev/null
expect_ok crew hold status $box
has "$out" "$box is held by $me@mac-studio"; has "$out" "wldn-design is working"
as $box herdr --session wldn-3 stub status wldn-design idle >/dev/null
expect_ok crew hold status $box
has "$out" "quiet: $(herdr_state $box wldn-3 '.agents | length') crew agents up, none at work; crew hold wait $box ends them"
expect_ok crew hold wait $box --timeout 60000
has "$out" "wldn-design is ended"; has "$out" "every crew agent is down. herdr can be restarted"
eq "$(herdr_state $box wldn-3 '[.agents[].name] | join(",")')" ""
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "design,planner,ops,operator"
eq "$(field $box host.down On agent/wldn-design)" "agent/wldn-design agent/wldn-planner agent/wldn-ops agent/wldn-operator"
ok "hold status says what still works, and hold wait ends every crew agent once the host is quiet, keeping its panes"

: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew go $box
has "$out" "$box is no longer held"
[[ -e $(home_of $box)/.local/state/crew/hold ]] && fail "go left the hold"
eq "$(mains)" "$here"
for a in ${here//,/ }; do
  eq "$a $(launched $a | cut -d' ' -f2)" "$a resumed"
  eq "$a $(greetings $box wldn-3 $a)" "$a 1"
done
eq "$(field $box host.go On)" "host/$box"
ok "crew go lifts the hold and brings each agent back with its conversation, each greeted"

# An update: wldn-ops's start was made of another brief than crew would start it with now.
rec() { as $box bash -c "grep -l '^CREW_AGENT=$1\$' \"\$HOME\"/.local/state/crew/sessions/* | xargs ls -t | head -1"; }
ops=$(rec wldn-ops); rewrite "$ops" "s/^CREW_LAUNCH=.*/CREW_LAUNCH=stale/"
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew update $box
has "$out" "wldn-ops is due (its brief, model, effort or folders changed): it is restarted on crew"
lacks "$out" "wldn-design is due"
log=$(home_of $box)/.local/state/crew/renew/wldn-ops.log
until_ok grep -q "wldn-ops is restarted on crew" "$log" || fail "wldn-ops was not restarted: $(cat "$log")"
eq "$(launched wldn-ops | cut -d' ' -f2)" "resumed"
grep -q "^$box wldn-3 agent prompt wldn-ops '\[crew\] crew restarted you on crew " "$CREW_TEST_LOG" || fail "wldn-ops was not told its restart"
[[ $(sed -n 's/^CREW_LAUNCH=//p' "$(rec wldn-ops)") != stale ]] || fail "the restart did not record its launch"
eq "$(field $box agent.renew On)" "agent/wldn-ops"
ok "crew update hands an agent an update made due its restart, which resumes it on crew as it now is and tells it so"

# Slow to exit: wldn-ops is still up when its stop has looked for its exit and given up, and goes a few looks later.
rewrite "$(rec wldn-ops)" "s/^CREW_LAUNCH=.*/CREW_LAUNCH=stale/"
as $box herdr --session wldn-3 stub linger wldn-ops 40 >/dev/null
: > "$log"; : > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew update $box
until_ok grep -q "wldn-ops is restarted on crew" "$log" || fail "wldn-ops was not restarted once it exited: $(cat "$log")"
has "$(cat "$log")" "wldn-ops did not exit at once; crew watches for its exit"
eq "$(launched wldn-ops | cut -d' ' -f2)" "resumed"
grep -q "^$box wldn-3 agent prompt wldn-ops '\[crew\] crew restarted you on crew " "$CREW_TEST_LOG" || fail "wldn-ops was not told its restart"
[[ -e $(home_of $box)/.local/state/crew/renew/wldn-ops.exiting ]] && fail "the restart left its mark once it started wldn-ops"
ok "a restart whose agent exits after its stop gave up watches for the exit and resumes it on crew as it now is, told so"

# Never exits: wldn-ops is still up when the restart has watched for its exit for ten minutes.
rewrite "$(rec wldn-ops)" "s/^CREW_LAUNCH=.*/CREW_LAUNCH=stale/"
as $box herdr --session wldn-3 stub linger wldn-ops 200 >/dev/null
: > "$log"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew update $box
until_ok grep -q "runs on as it was" "$log" || fail "the restart did not say wldn-ops runs on: $(cat "$log")"
has "$(cat "$log")" "wldn-ops did not exit (busy or waiting on the user); it was left running; it runs on as it was, still due: the end of its next turn hands it back"
eq "$(mains)" "$here"
eq "$(launches)" ""
eq "$(cat "$(home_of $box)/.local/state/crew/renew/wldn-ops.exiting")" "$(basename "$(rec wldn-ops)")"
ok "a restart whose agent never exits leaves it running as it was, starts nothing in its pane, and says so"

# Exits after the restart gave up: the exit that restart typed ends wldn-ops later, its pane kept, and its next turn's
# end hands its restart back.
as $box herdr --session wldn-3 stub linger wldn-ops 0 >/dev/null
eq "$(mains)" "$here"
: > "$log"; : > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
as $box bash -c "echo '{\"session_id\":\"$(basename "$(rec wldn-ops)")\"}' | python3 '$CREW/plugin/hooks/stop'"
until_ok grep -q "wldn-ops is restarted on crew" "$log" || fail "wldn-ops was not restarted once it exited late: $(cat "$log")"
has "$(cat "$log")" "wldn-ops was ended by the exit an earlier restart typed; crew starts it"
eq "$(launched wldn-ops | cut -d' ' -f2)" "resumed"
grep -q " agent prompt [^ ]* /exit$" "$CREW_TEST_LOG" && fail "the restart typed an exit to an agent that had exited"
grep -q "^$box wldn-3 agent prompt wldn-ops '\[crew\] crew restarted you on crew " "$CREW_TEST_LOG" || fail "wldn-ops was not told its restart"
ok "a later restart starts an agent the exit an earlier restart typed ended, with no stop, resumed and told so"

# The Stop hook, at the end of the planner's turn, once an update made it due.
planner=$(rec wldn-planner); rewrite "$planner" "s/^CREW_LAUNCH=.*/CREW_LAUNCH=stale/"
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
as $box bash -c "echo '{\"session_id\":\"$(basename "$planner")\"}' | python3 '$CREW/plugin/hooks/stop'"
log=$(home_of $box)/.local/state/crew/renew/wldn-planner.log
until_ok grep -q "wldn-planner is restarted on crew" "$log" || fail "the planner was not restarted: $(cat "$log" 2>/dev/null)"
eq "$(launched wldn-planner | cut -d' ' -f2)" "resumed"
grep -q "^$box wldn-3 agent prompt wldn-planner '\[crew\] crew restarted you on crew " "$CREW_TEST_LOG" || fail "wldn-planner was not told its restart"
eq "$(jq -r '.hooks.Stop[0].hooks[0].command' "$CREW/plugin/hooks/hooks.json")" 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/stop"'
: > "$CREW_TEST_CLAUDE_LOG"
as $box bash -c "echo '{\"session_id\":\"$(basename "$(rec wldn-planner)")\"}' | python3 '$CREW/plugin/hooks/stop'"
echo '{"session_id":"nobody"}' | as $box python3 "$CREW/plugin/hooks/stop"
echo 'not json' | as $box python3 "$CREW/plugin/hooks/stop"
eq "$(launches)" ""
ok "the Stop hook hands a due agent its restart at the end of its turn, resumed and told so, and leaves one not due and a session crew never started alone"

: > "$CREW_TEST_LOG"
expect_ok crew hold --all "reboot" --now
has "$out" "$box: wldn-design is ended"; has "$out" "mac-studio: mac-studio is held"
eq "$(herdr_state $box wldn-3 '[.agents[].name] | join(",")')" ""
expect_ok crew go --all
eq "$(mains)" "$here"
ok "crew hold --all --now holds every host crew runs agents on and ends every agent there at once, and crew go --all brings them back"

# wldn's planner stands, then its partition comes to run it as its kind (design Decision 14): crew update passes it
# over, and at the end of its turn the Stop hook hands it its end, given once it is idle, its pane left with nothing
# started in it and its log saying why; nothing starts it again.
HOST=$box expect_ok crew main up wldn
planner=$(rec wldn-planner)
role_stream wldn planner wldn-main
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
rm -f "$(home_of $box)/.local/state/crew/renew/wldn-planner.log"  # its restart's above
expect_ok crew update $box
has "$out" "wldn-planner is passed over, never restarted: its role now runs as its kind, in Flume runs of its own"
[[ -e $(home_of $box)/.local/state/crew/renew/wldn-planner.log ]] && fail "crew update handed wldn-planner to crew _renew"
as $box bash -c "echo '{\"session_id\":\"$(basename "$planner")\"}' | python3 '$CREW/plugin/hooks/stop'"
log=$(home_of $box)/.local/state/crew/renew/wldn-planner.log
until_ok grep -q "wldn-planner is ended" "$log" || fail "wldn-planner was not ended: $(cat "$log" 2>/dev/null)"
has "$(cat "$log")" "wldn-planner is ended: its role now runs as its kind, in Flume runs of its own, so nothing starts it again; its pane is left"
eq "$(herdr_state $box wldn-3 '[.agents[].name] | map(select(. == "wldn-planner")) | length')" "0"
eq "$(herdr_state $box wldn-3 '[.tabs[].label] | map(select(. == "planner")) | length')" "1"
eq "$(field $box agent.end On)" "agent/wldn-planner"
expect_ok crew update $box
HOST=$box expect_ok crew revive
eq "$(launches)" ""
ok "a standing planner whose role now runs as its kind is passed over by crew update and ended at the end of its turn, its pane left, and nothing starts it again"
