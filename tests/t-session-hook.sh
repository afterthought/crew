# crew's SessionStart hook records a crew agent's session; when herdr resumes that session without crew's
# environment, the agent gets CREW_AGENT and CREW_LABEL back through CLAUDE_ENV_FILE and its pane its name.
# Any other session, a subagent's, or input the hook can't read is left alone, and the hook always exits 0.
# crew's PreToolUse hook marks a question or a plan a crew agent opens for the user, and a session's start clears it.
# Reads: plugin/hooks/
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
for _ in $(seq 6000); do [[ $(herdr agent get "$p" | jq -r .result.agent.name) == swb-1-conductor ]] && break; /bin/sleep 0.1; done
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

qhook() { python3 "$CREW/plugin/hooks/questions"; }
marks="$HOME/.local/state/crew/questions"
asked() { printf '{"session_id":"%s","transcript_path":"/t/%s.jsonl","tool_name":"%s","tool_use_id":"%s","tool_input":{}%s}' "$@"; }

eq "$(jq -r '.hooks.PreToolUse[0].matcher' "$CREW/plugin/hooks/hooks.json")" "AskUserQuestion|ExitPlanMode"
has "$(jq -r '.hooks.PreToolUse[0].hooks[0].command' "$CREW/plugin/hooks/hooks.json")" '${CLAUDE_PLUGIN_ROOT}/hooks/questions'
ok "the plugin's hooks.json runs the questions hook before a question or a plan is opened"

out=$(asked sid-1 sid-1 AskUserQuestion toolu_01 "" | qhook)
eq "$out" ""
eq "$(jq -c . "$marks/sid-1")" '{"tool_use_id":"toolu_01","transcript_path":"/t/sid-1.jsonl"}'
asked sid-3 sid-3 ExitPlanMode toolu_02 "" | CREW_AGENT=swb-1-ops qhook
eq "$(jq -c . "$marks/sid-3")" '{"tool_use_id":"toolu_02","transcript_path":"/t/sid-3.jsonl"}'
asked sid-1 sid-1 AskUserQuestion toolu_03 "" | qhook
eq "$(jq -r .tool_use_id "$marks/sid-1")" "toolu_03"
ok "a crew agent's question or plan leaves a mark naming the call and its transcript, and a later one replaces it"

asked sid-2 sid-2 AskUserQuestion toolu_04 "" | qhook
asked sid-1 sid-1 AskUserQuestion toolu_05 ',"agent_id":"a1"' | qhook
asked ../../x x AskUserQuestion toolu_06 "" | CREW_AGENT=swb-1-ops qhook
echo '{"session_id":"sid-1","tool_name":"AskUserQuestion"}' | qhook
echo 'not json' | qhook
eq "$(jq -r .tool_use_id "$marks/sid-1")" "toolu_03"
eq "$(ls -A "$marks" | tr '\n' ' ')" "sid-1 sid-3 "
ok "a session crew never started, a subagent's call, a bad session id, input naming no call and unreadable input write nothing"

echo '{"session_id":"sid-1","source":"resume"}' | hook
[[ -e $marks/sid-1 ]] && fail "a session's start left its mark"
echo '{"session_id":"sid-4","source":"startup"}' | hook
eq "$(ls -A "$marks")" "sid-3"
ok "a session's start removes its own mark and no other"

chmod 500 "$marks"
expect_ok bash -c "$(declare -f asked); asked sid-3 sid-3 AskUserQuestion toolu_07 '' | CREW_AGENT=swb-1-ops python3 '$CREW/plugin/hooks/questions'"
chmod 700 "$marks"
has "$out" "crew questions:"
eq "$(jq -r .tool_use_id "$marks/sid-3")" "toolu_02"
ok "a questions hook that fails says so and still exits 0"
