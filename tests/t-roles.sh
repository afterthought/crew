# Each of a partition's main-level roles starts from its agent definition: the model and effort in its frontmatter,
# unless the teams file overrides them for the partition, and its brief appended to Claude Code's system prompt; crew-role
# starts no team's conductor, ops or slot (Decision 10 of the-team-machinery-leaves); its name is in
# CREW_AGENT, and in SLUICE_AGENT for sluice, and its definition in CREW_ROLE. A session herdr resumes without crew's
# environment is given that same brief back by crew's SessionStart hook at each compaction. A main level's role is
# started only on its main level's host, and a main level's session herdr resumes on any other host is given no
# identity, pane name or brief, its record left as it was, and told where the main level runs, or why crew can't tell.
# A role its partition runs as its kind is started by crew-role on no host, which names crew role open.
# Reads: plugin/hooks/ plugin/roles/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
box=$(space chuck-herdr-alpha willdan); mac=$(space mac-studio madswan)
mkdir -p "$box"/{switchboard-kit,willdan-blueprints,breadboard-kit,atlas-kit}/main "$mac/blueprints/main"

role() {  # role <host> <scope> <role> [stage]: start it with the stub claude, print and keep its launch
  : > "$CREW_TEST_CLAUDE_LOG"
  as "$1" "$CREW/plugin/bin/crew-role" "${@:2}" || fail "crew-role ${*:2} failed"
  launch=$(python3 -c 'import json, sys
l = json.loads(open(sys.argv[1]).read())
a = l["argv"]; i = a.index("--append-system-prompt")
print(" ".join(a[:i]), "| cwd", l["cwd"], "| agent", l["agent"], "| sluice", l["sluice"], "| label", l["label"], "| role", l["role"], "| brief", len(a[i + 1]), "chars")' "$CREW_TEST_CLAUDE_LOG")
  echo "${*:2}: $launch"
}
# compacted <host>: what crew's SessionStart hook gives the last role started there at a compaction once herdr has
# resumed it, without crew's environment; brief: the brief that role was started with
compacted() {
  local sid; sid=$(jq -r .session "$CREW_TEST_CLAUDE_LOG")
  as "$1" env -u CREW_AGENT -u CREW_LABEL -u CREW_ROLE python3 "$CREW/plugin/hooks/session-start" <<<"{\"session_id\":\"$sid\",\"source\":\"compact\"}" |
    jq -r '.hookSpecificOutput | select(.hookEventName == "SessionStart") | .additionalContext'
}
brief() { python3 -c 'import json, sys; a = json.loads(open(sys.argv[1]).read())["argv"]; sys.stdout.write(a[a.index("--append-system-prompt") + 1])' "$CREW_TEST_CLAUDE_LOG"; }

opus='--model claude-opus-5-5[1m]'; fable='--model claude-fable-5-1'
role chuck-herdr-alpha wldn design;         has "$launch" "$fable --effort xhigh"; has "$launch" "--name wldn-design"
first=$(jq -r .session "$CREW_TEST_CLAUDE_LOG")
has "$launch" "cwd $box/willdan-blueprints/main"; has "$launch" "--add-dir $box/atlas-kit/main --add-dir $box/breadboard-kit/main --add-dir $box/switchboard-kit/main"
has "$launch" "agent wldn-design | sluice wldn-design | label wldn"
role chuck-herdr-alpha wldn planner;        has "$launch" "$fable --effort xhigh"; has "$launch" "--name wldn-planner"
role chuck-herdr-alpha wldn ops;            has "$launch" "$opus --effort high"; has "$launch" "--name wldn-ops"
role chuck-herdr-alpha wldn reviewer;       has "$launch" "$opus --effort high"; has "$launch" "--name wldn-reviewer"
has "$launch" "cwd $box/willdan-blueprints/main"
expect_fail "no role 'dispatcher' at wldn's main level. roles: design planner ops reviewer operator" as chuck-herdr-alpha "$CREW/plugin/bin/crew-role" wldn dispatcher
role chuck-herdr-alpha wldn operator;       has "$launch" "$opus --effort medium"; has "$launch" "--name wldn-operator"
has "$launch" "cwd $box/willdan-blueprints/main"
role mac-studio madswan planner;            has "$launch" "$fable --effort xhigh"; has "$launch" "cwd $mac/blueprints/main"
ok "every role starts on its definition's model and effort"

role chuck-herdr-alpha wldn ops;            has "$launch" "role main-ops"
ctx=$(compacted chuck-herdr-alpha)
has "${ctx%%$'\n\n'*}" "[crew] This is your brief as wldn-ops"
eq "${ctx#*$'\n\n'}" "$(brief)"
ok "a session herdr resumed is given back at a compaction the brief its role was started with"

edit teams "$(part wldn)['roles'] = {'planner': {'effort': 'max'}, 'operator': {'model': 'claude-opus-5-5'}}"
role chuck-herdr-alpha wldn planner;        has "$launch" "$fable --effort max"
role mac-studio madswan planner;            has "$launch" "$fable --effort xhigh"
role chuck-herdr-alpha wldn operator;       has "$launch" "--model claude-opus-5-5 --effort medium"
role chuck-herdr-alpha wldn ops;            has "$launch" "$opus --effort high"
ok "an override changes its role for that partition only"

role chuck-herdr-alpha wldn design resume;  has "$launch" "--name wldn-design --resume $first"
role mac-studio madswan design resume;   has "$launch" "--name madswan-design"; lacks "$launch" "--resume"
: > "$CREW_TEST_CLAUDE_LOG"
expect_fail "no partition 'swb-1'" as chuck-herdr-alpha "$CREW/plugin/bin/crew-role" swb-1 conductor
expect_fail "no partition 'swb-1'" as chuck-herdr-alpha "$CREW/plugin/bin/crew-role" swb-1 unit-2 code
expect_fail "no role 'conductor' at wldn's main level" as chuck-herdr-alpha "$CREW/plugin/bin/crew-role" wldn conductor
expect_fail "no role 'fable' at wldn's main level" as chuck-herdr-alpha "$CREW/plugin/bin/crew-role" wldn fable
eq "$(launches)" ""
ok "a team's conductor, ops or slot, and an unknown role, are refused, and no Claude starts"

: > "$CREW_TEST_CLAUDE_LOG"
expect_fail "wldn's main level runs on chuck-herdr-alpha, not mac-studio, and crew starts wldn-planner only there" as mac-studio "$CREW/plugin/bin/crew-role" wldn planner
expect_fail "wldn's main level runs on chuck-herdr-alpha, not mac-studio, and crew starts wldn-design only there" as mac-studio "$CREW/plugin/bin/crew-role" wldn design resume
eq "$(launches)" ""
ok "a main level's role, fresh or resumed, is refused off its main level's host, naming that host, and no Claude starts"

role_stream madswan planner madswan-main
expect_fail "madswan's planner runs as its kind, so crew starts no standing agent of it: it is opened with crew role open planner --label madswan" \
  as mac-studio "$CREW/plugin/bin/crew-role" madswan planner
expect_fail "madswan's planner runs as its kind" as mac-studio "$CREW/plugin/bin/crew-role" madswan planner resume
eq "$(launches)" ""
role_stream madswan planner false
ok "a role its partition runs as its kind, fresh or resumed, is refused, naming crew role open, and no Claude starts"

# replayed <source>: what crew's SessionStart hook gives, on mac-studio, the wldn planner's session copied there from the
# box, as herdr's session restore replays a saved pane on a host that once ran the main level: without crew's environment
replayed() {
  : > "$T/env"; : > "$CREW_TEST_LOG"
  as mac-studio env -u CREW_AGENT -u CREW_LABEL -u CREW_ROLE CLAUDE_ENV_FILE="$T/env" HERDR_ENV=1 HERDR_PANE_ID="$p" \
    HERDR_BIN_PATH="$TESTS/stubs/herdr" python3 "$CREW/plugin/hooks/session-start" <<<"{\"session_id\":\"$sid\",\"source\":\"$1\"}" |
    jq -r '.hookSpecificOutput | select(.hookEventName == "SessionStart") | .additionalContext'
}
role chuck-herdr-alpha wldn planner;        has "$launch" "role planner"
sid=$(jq -r .session "$CREW_TEST_CLAUDE_LOG"); rec="$(home_of mac-studio)/.local/state/crew/sessions/$sid"
mkdir -p "$(dirname "$rec")"; cp "$(home_of chuck-herdr-alpha)/.local/state/crew/sessions/$sid" "$rec"; cp "$rec" "$T/kept"
p=$(as mac-studio herdr workspace create --cwd / --label swancloud | jq -r .result.root_pane.pane_id)
as mac-studio herdr stub agent "$p"
elsewhere="[crew] This session was wldn-planner, and crew gives it no identity here: wldn's main level runs on chuck-herdr-alpha, not mac-studio, and crew starts wldn-planner only there. In this session you are no agent of crew's"
ctx=$(replayed resume)
has "$ctx" "$elsewhere"
eq "$(cat "$T/env")" ""; lacks "$(calls)" "rename"; cmp -s "$rec" "$T/kept" || fail "the replayed session's record changed"
eq "$(as mac-studio herdr agent get "$p" | jq -r .result.agent.name)" "null"
eq "$(replayed compact)" "$ctx"
eq "$(cat "$T/env")" ""; lacks "$(calls)" "rename"; cmp -s "$rec" "$T/kept" || fail "the compacted session's record changed"
ok "a main level's agent herdr resumed off its host gets no identity, pane name or brief, its record left, and is told where the main level runs"

mv "$(home_of mac-studio)/.config/crew/teams.json" "$T/teams.json"
ctx=$(replayed resume)
has "$ctx" "[crew] This session was wldn-planner, and crew gives it no identity here: it can't tell where wldn's main level runs, $(home_of mac-studio)/.config/crew/teams.json is missing"
has "$ctx" "In this session you are no agent of crew's"
eq "$(cat "$T/env")" ""; cmp -s "$rec" "$T/kept" || fail "the record changed with no teams file"
mv "$T/teams.json" "$(home_of mac-studio)/.config/crew/teams.json"
ok "with no teams file to tell where its main level runs, it gets no identity either, and is told why"

ctx=$(compacted chuck-herdr-alpha)
has "${ctx%%$'\n\n'*}" "[crew] This is your brief as wldn-planner"
eq "${ctx#*$'\n\n'}" "$(brief)"
ok "on its main level's host the same session is given its brief back at a compaction"
