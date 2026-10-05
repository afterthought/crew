# crew's SessionStart hook records a crew agent's session; when herdr resumes that session without crew's
# environment, the agent gets CREW_AGENT and CREW_LABEL back through CLAUDE_ENV_FILE and its pane its name.
# Any other session, a subagent's, or input the hook can't read is left alone, and the hook always exits 0.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
hook() { python3 "$CREW/plugin/hooks/session-start"; }
record="$HOME/.local/state/crew/sessions/sid-1"

hooks=$(jq -r '.hooks.SessionStart[0].hooks[0].command' "$CREW/plugin/hooks/hooks.json")
has "$hooks" '${CLAUDE_PLUGIN_ROOT}/hooks/session-start'
ok "the plugin's hooks.json runs the session-start hook"

echo '{"session_id":"sid-1","source":"startup","cwd":"/work/kit/bolts/b"}' | CREW_AGENT=swb-1-conductor CREW_LABEL=wldn hook
eq "$(cat "$record")" $'CREW_AGENT=swb-1-conductor\nCREW_LABEL=wldn\nCREW_CWD=/work/kit/bolts/b'
ok "a crew agent's start records its session and the folder it began in"

p=$(herdr workspace create --cwd / --label swb-1 | jq -r .result.root_pane.pane_id)
herdr stub agent "$p"
echo '{"session_id":"sid-1","source":"resume"}' | CLAUDE_ENV_FILE="$T/env" HERDR_ENV=1 HERDR_PANE_ID="$p" HERDR_BIN_PATH="$TESTS/stubs/herdr" hook
eq "$(cat "$T/env")" "export CREW_AGENT=swb-1-conductor CREW_LABEL=wldn"
for _ in $(seq 50); do [[ $(herdr agent get "$p" | jq -r .result.agent.name) == swb-1-conductor ]] && break; /bin/sleep 0.1; done
eq "$(herdr agent get "$p" | jq -r .result.agent.name)" "swb-1-conductor"
eq "$(env -i HOME="$HOME" PATH="$PATH" bash -c ". '$T/env'; echo \$CREW_AGENT \$CREW_LABEL")" "swb-1-conductor wldn"
ok "a session herdr resumed gets its crew identity back and its pane renamed"

: > "$CREW_TEST_LOG"; : > "$T/env"
echo '{"session_id":"sid-2","source":"startup"}' | CLAUDE_ENV_FILE="$T/env" HERDR_ENV=1 HERDR_PANE_ID="$p" HERDR_BIN_PATH="$TESTS/stubs/herdr" hook
echo '{"session_id":"sid-1","agent_id":"a1"}' | CLAUDE_ENV_FILE="$T/env" HERDR_ENV=1 HERDR_PANE_ID="$p" HERDR_BIN_PATH="$TESTS/stubs/herdr" hook
echo '{"session_id":"../../x"}' | CLAUDE_ENV_FILE="$T/env" hook
echo 'not json' | hook
eq "$(cat "$T/env")" ""
eq "$(calls)" ""
eq "$(ls "$HOME/.local/state/crew/sessions")" "sid-1"
ok "a session crew never started, a subagent, a bad session id and unreadable input are left alone"

chmod 000 "$record"
expect_ok bash -c "echo '{\"session_id\":\"sid-1\"}' | python3 '$CREW/plugin/hooks/session-start'"
has "$out" "crew session-start:"
chmod 644 "$record"
ok "a hook that fails says so and still exits 0"
