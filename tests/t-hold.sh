# A host's hold and crew's updates reaching its agents through the crew command on the stubs (teams.19): crew hold
# holds the host it names, tells each standing agent up there to finish its step, and records it; while it holds,
# crew starts no agent there; hold status says what still works; hold wait, once the host is quiet, ends every crew
# agent there with its pane kept; crew go lifts the hold and brings each back with its conversation, greeted; crew
# update hands each standing agent an update made due its restart, which brings it back on crew as it now is, told
# so; crew's Stop hook does the same at the end of a due agent's turn; and --now ends every agent at once.
# What makes an agent due, what keeps a host from being quiet, when a due agent may be restarted and what the bands
# say are logic cases (tests/py/test_hold.py).
# Reads: plugin/hooks/ plugin/lib/hold.py plugin/lib/ops.py tests/teams.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/teams.sh"

expect_ok crew up swb-1
: > "$CREW_TEST_LOG"
expect_ok crew hold $box "herdr 0.9.6"
has "$out" "$box is held: crew starts no agent here until crew go $box"
eq "$(jq -r .why "$(home_of $box)/.local/state/crew/hold")" "herdr 0.9.6"
for a in swb-1-conductor swb-1-ops; do
  grep -q "^$box wldn-1 agent prompt $a '\[crew\] $box is held by $me@mac-studio: herdr 0.9.6. Finish the step you are in" "$CREW_TEST_LOG" ||
    fail "$a was not told the hold"
done
eq "$(field $box host.hold On)" "host/$box"
[[ $(as $box bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec') != *"herdr 0.9.6"* ]] || fail "the hold's words are in the run record"
expect_fail "$box is held by $me@mac-studio" crew up swb-2
expect_fail "$box is held by $me@mac-studio" crew main up wldn
eq "$(herdr_state $box wldn-1 '[.agents[].name] | sort | join(",")')" "swb-1-conductor,swb-1-ops"
ok "crew hold holds the host it names, tells each standing agent up there, records it without its words, and crew starts no agent there meanwhile"

as $box herdr --session wldn-1 stub status swb-1-conductor working >/dev/null
expect_ok crew hold status $box
has "$out" "$box is held by $me@mac-studio"; has "$out" "swb-1-conductor is working"
as $box herdr --session wldn-1 stub status swb-1-conductor idle >/dev/null
expect_ok crew hold status $box
has "$out" "quiet: 2 crew agents up, none at work; crew hold wait $box ends them"
expect_ok crew hold wait $box --timeout 60000
has "$out" "swb-1-conductor is ended"; has "$out" "every crew agent is down. herdr can be restarted"
eq "$(herdr_state $box wldn-1 '[.agents[].name] | join(",")')" ""
eq "$(herdr_state $box wldn-1 '[.tabs[].label] | join(",")')" "conductor"
eq "$(field $box host.down On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
ok "hold status says what still works, and hold wait ends every crew agent once the host is quiet, keeping its panes"

: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew go $box
has "$out" "$box is no longer held"
[[ -e $(home_of $box)/.local/state/crew/hold ]] && fail "go left the hold"
eq "$(herdr_state $box wldn-1 '[.agents[].name] | sort | join(",")')" "swb-1-conductor,swb-1-ops"
eq "$(launched swb-1-conductor | cut -d' ' -f2) $(launched swb-1-ops | cut -d' ' -f2)" "resumed resumed"
eq "$(greetings $box wldn-1 swb-1-conductor)" "1"
eq "$(field $box host.go On)" "host/$box"
ok "crew go lifts the hold and brings each agent back with its conversation, the conductor greeted"

# An update: swb-1-ops's start was made of another brief than crew would start it with now.
rec() { as $box bash -c "grep -l '^CREW_AGENT=$1\$' \"\$HOME\"/.local/state/crew/sessions/* | xargs ls -t | head -1"; }
ops=$(rec swb-1-ops); rewrite "$ops" "s/^CREW_LAUNCH=.*/CREW_LAUNCH=stale/"
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew update $box
has "$out" "swb-1-ops is due (its brief, model, effort or folders changed): it is restarted on crew"
lacks "$out" "swb-1-conductor is due"
log=$(home_of $box)/.local/state/crew/renew/swb-1-ops.log
until_ok grep -q "swb-1-ops is restarted on crew" "$log" || fail "swb-1-ops was not restarted: $(cat "$log")"
eq "$(launched swb-1-ops | cut -d' ' -f2)" "resumed"
grep -q "^$box wldn-1 agent prompt swb-1-ops '\[crew\] crew restarted you on crew " "$CREW_TEST_LOG" || fail "swb-1-ops was not told its restart"
[[ $(sed -n 's/^CREW_LAUNCH=//p' "$(rec swb-1-ops)") != stale ]] || fail "the restart did not record its launch"
eq "$(field $box agent.renew On)" "team/swb-1 agent/swb-1-ops"
ok "crew update hands an agent an update made due its restart, which resumes it on crew as it now is and tells it so"

# The Stop hook, at the end of the conductor's turn, once an update made it due.
cond=$(rec swb-1-conductor); rewrite "$cond" "s/^CREW_LAUNCH=.*/CREW_LAUNCH=stale/"
: > "$CREW_TEST_CLAUDE_LOG"
as $box bash -c "echo '{\"session_id\":\"$(basename "$cond")\"}' | python3 '$CREW/plugin/hooks/stop'"
log=$(home_of $box)/.local/state/crew/renew/swb-1-conductor.log
until_ok grep -q "swb-1-conductor is restarted on crew" "$log" || fail "the conductor was not restarted: $(cat "$log" 2>/dev/null)"
eq "$(launched swb-1-conductor | cut -d' ' -f2)" "fresh"
eq "$(jq -r '.hooks.Stop[0].hooks[0].command' "$CREW/plugin/hooks/hooks.json")" 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/stop"'
: > "$CREW_TEST_CLAUDE_LOG"
as $box bash -c "echo '{\"session_id\":\"$(basename "$(rec swb-1-conductor)")\"}' | python3 '$CREW/plugin/hooks/stop'"
echo '{"session_id":"nobody"}' | as $box python3 "$CREW/plugin/hooks/stop"
echo 'not json' | as $box python3 "$CREW/plugin/hooks/stop"
eq "$(launches)" ""
ok "the Stop hook hands a due conductor a fresh start at the end of its turn, and leaves one not due and a session crew never started alone"

: > "$CREW_TEST_LOG"
expect_ok crew hold --all "reboot" --now
has "$out" "$box: swb-1-conductor is ended"; has "$out" "mac-studio: mac-studio is held"
eq "$(herdr_state $box wldn-1 '[.agents[].name] | join(",")')" ""
expect_ok crew go --all
eq "$(herdr_state $box wldn-1 '[.agents[].name] | sort | join(",")')" "swb-1-conductor,swb-1-ops"
ok "crew hold --all --now holds every host crew runs agents on and ends every agent there at once, and crew go --all brings them back"
