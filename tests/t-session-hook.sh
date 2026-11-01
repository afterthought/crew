# crew's SessionStart hook records a crew agent's session; when herdr resumes that session without crew's
# environment, the agent gets CREW_AGENT, CREW_LABEL and SLUICE_AGENT back through CLAUDE_ENV_FILE and its pane its name;
# a resume, and a compaction of a session crew-role started, give no brief back (t-roles has the one a compaction gives).
# A start that loads crew's plugin records the commit and version of crew it loaded, and crew-role's launch digest; a
# compaction keeps them, and herdr's resume records what it loaded anew beside the launch it began with (teams.19).
# The record names the herdr session and pane the session started in, at herdr's resume the pane it resumed in.
# Every agent crew starts is a main level's (Decision 10 of the-team-machinery-leaves), so the hook runs here on wldn's
# main level's host. Any other session, a subagent's, or input the hook can't read is left alone, and the hook always
# exits 0, a session recorded as a team's agent before teams left among them, whose brief can't be built.
# crew's PreToolUse hook marks a question or a plan a crew agent opens for the user, and a session's start clears it.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
cp -R "$(home_of chuck-herdr-alpha)/.config" "$HOME/"
export CREW_TEST_HOST=chuck-herdr-alpha
hook() { python3 "$CREW/plugin/hooks/session-start"; }
record="$HOME/.local/state/crew/sessions/sid-1"

hooks=$(jq -r '.hooks.SessionStart[0].hooks[0].command' "$CREW/plugin/hooks/hooks.json")
has "$hooks" '${CLAUDE_PLUGIN_ROOT}/hooks/session-start'
ok "the plugin's hooks.json runs the session-start hook"

commit=$(git -C "$CREW" rev-parse HEAD)
described=$(git -C "$CREW" describe --tags --long --match 'v[0-9]*' --abbrev=40 HEAD)
version=${described%-*-g*}; past=${described%-g*}; past=${past##*-}; [[ $past == 0 ]] || version+="+$past"
echo '{"session_id":"sid-1","source":"startup","cwd":"/work/blueprints"}' | CREW_AGENT=wldn-planner CREW_LABEL=wldn CREW_ROLE=planner CREW_LAUNCH=d1 SLUICE_BRANCH=bolt/b HERDR_SESSION=s HERDR_PANE_ID=w1:p2 hook
eq "$(cat "$record")" "CREW_AGENT=wldn-planner
CREW_LABEL=wldn
CREW_CWD=/work/blueprints
CREW_ROLE=planner
CREW_HERDR_SESSION=s
CREW_PANE=w1:p2
CREW_COMMIT=$commit
CREW_VERSION=$version
CREW_LAUNCH=d1"
ok "a crew agent's start records its session, the definition its brief comes from, the folder it began in, the herdr session and pane it started in, and the crew and launch it loaded, and no branch for sluice"

rewrite "$record" "s/^CREW_COMMIT=.*/CREW_COMMIT=old/; s/^CREW_VERSION=.*/CREW_VERSION=v0.1.0/"
echo '{"session_id":"sid-1","source":"compact","cwd":"/work/blueprints"}' | CREW_AGENT=wldn-planner CREW_LABEL=wldn CREW_ROLE=planner CREW_LAUNCH=d1 HERDR_SESSION=s HERDR_PANE_ID=w1:p2 hook
has "$(cat "$record")" $'CREW_ROLE=planner\nCREW_HERDR_SESSION=s\nCREW_PANE=w1:p2\nCREW_COMMIT=old\nCREW_VERSION=v0.1.0\nCREW_LAUNCH=d1'
echo '{"session_id":"sid-1","source":"resume"}' | HERDR_SESSION=s2 HERDR_PANE_ID=w3:p1 hook
has "$(cat "$record")" "CREW_HERDR_SESSION=s2
CREW_PANE=w3:p1
CREW_COMMIT=$commit
CREW_VERSION=$version
CREW_LAUNCH=d1"
has "$(cat "$record")" "CREW_ROLE=planner"
lacks "$(cat "$record")" "w1:p2"; lacks "$(cat "$record")" "CREW_BRANCH"
eq "$(grep -c '^CREW_HERDR_SESSION=' "$record") $(grep -c '^CREW_PANE=' "$record")" "1 1"
ok "a compaction keeps the crew the session loaded, and herdr's bare resume records the crew it loads anew with the launch it began with, and the herdr session and pane it resumed in, not the old"

out=$(echo '{"session_id":"sid-1","source":"compact","cwd":"/work/blueprints"}' | CREW_AGENT=wldn-planner CREW_LABEL=wldn CREW_ROLE=planner hook)
eq "$out" ""
ok "a compaction of a session crew-role started, which carries its brief in its arguments, is given none"

p=$(herdr workspace create --cwd / --label wldn | jq -r .result.root_pane.pane_id)
herdr stub agent "$p"
out=$(echo '{"session_id":"sid-1","source":"resume"}' | CLAUDE_ENV_FILE="$T/env" HERDR_ENV=1 HERDR_PANE_ID="$p" HERDR_BIN_PATH="$TESTS/stubs/herdr" hook)
eq "$out" ""
eq "$(cat "$T/env")" "export CREW_AGENT=wldn-planner CREW_LABEL=wldn SLUICE_AGENT=wldn-planner"
for _ in $(seq 6000); do [[ $(herdr agent get "$p" | jq -r .result.agent.name) == wldn-planner ]] && break; /bin/sleep 0.1; done
eq "$(herdr agent get "$p" | jq -r .result.agent.name)" "wldn-planner"
eq "$(env -i HOME="$HOME" PATH="$PATH" bash -c ". '$T/env'; echo \$CREW_AGENT \$CREW_LABEL \$SLUICE_AGENT")" "wldn-planner wldn wldn-planner"
calls | grep -q " hint \| report-metadata " && fail "the resume told the pane a branch for sluice"
ok "a session herdr resumed gets its crew identity back and its pane renamed, and no brief, which its transcript keeps"

printf 'CREW_AGENT=swb-1-conductor\nCREW_LABEL=wldn\nCREW_ROLE=conductor\n' > "$HOME/.local/state/crew/sessions/sid-6"
expect_ok bash -c "echo '{\"session_id\":\"sid-6\",\"source\":\"compact\"}' | python3 '$CREW/plugin/hooks/session-start'"
has "$out" "crew session-start: no agent swb-1-conductor: crew starts none by that name"
lacks "$out" "additionalContext"
rm "$HOME/.local/state/crew/sessions/sid-6"
ok "a compaction of a session recorded as a team's conductor, whose brief can't be built, says why, gives no context and still exits 0"

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

echo '{"session_id":"sid-5","source":"startup","cwd":"/work"}' | CREW_AGENT=wldn-ops CREW_LABEL=wldn hook
has "$(cat "$HOME/.local/state/crew/sessions/sid-5")" $'CREW_ROLE=\nCREW_HERDR_SESSION=\nCREW_PANE=\n'
ok "a crew agent's start outside herdr records no herdr session and no pane"

qhook() { python3 "$CREW/plugin/hooks/questions"; }
marks="$HOME/.local/state/crew/questions"
asked() { printf '{"session_id":"%s","transcript_path":"/t/%s.jsonl","tool_name":"%s","tool_use_id":"%s","tool_input":{}%s}' "$@"; }

eq "$(jq -r '.hooks.PreToolUse[0].matcher' "$CREW/plugin/hooks/hooks.json")" "AskUserQuestion|ExitPlanMode"
has "$(jq -r '.hooks.PreToolUse[0].hooks[0].command' "$CREW/plugin/hooks/hooks.json")" '${CLAUDE_PLUGIN_ROOT}/hooks/questions'
ok "the plugin's hooks.json runs the questions hook before a question or a plan is opened"

out=$(asked sid-1 sid-1 AskUserQuestion toolu_01 "" | qhook)
eq "$out" ""
eq "$(jq -c . "$marks/sid-1")" '{"tool_use_id":"toolu_01","transcript_path":"/t/sid-1.jsonl"}'
asked sid-3 sid-3 ExitPlanMode toolu_02 "" | CREW_AGENT=wldn-ops qhook
eq "$(jq -c . "$marks/sid-3")" '{"tool_use_id":"toolu_02","transcript_path":"/t/sid-3.jsonl"}'
asked sid-1 sid-1 AskUserQuestion toolu_03 "" | qhook
eq "$(jq -r .tool_use_id "$marks/sid-1")" "toolu_03"
ok "a crew agent's question or plan leaves a mark naming the call and its transcript, and a later one replaces it"

asked sid-2 sid-2 AskUserQuestion toolu_04 "" | qhook
asked sid-1 sid-1 AskUserQuestion toolu_05 ',"agent_id":"a1"' | qhook
asked ../../x x AskUserQuestion toolu_06 "" | CREW_AGENT=wldn-ops qhook
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
expect_ok bash -c "$(declare -f asked); asked sid-3 sid-3 AskUserQuestion toolu_07 '' | CREW_AGENT=wldn-ops python3 '$CREW/plugin/hooks/questions'"
chmod 700 "$marks"
has "$out" "crew questions:"
eq "$(jq -r .tool_use_id "$marks/sid-3")" "toolu_02"
ok "a questions hook that fails says so and still exits 0"
