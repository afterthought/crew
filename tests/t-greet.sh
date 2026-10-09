# A conductor is greeted to carry on with its bolt: by crew bolt give when it is up, by crew up when it starts,
# and once it is answered when it starts stopped on a question, whether herdr sees the question or crew's own hook
# saw it open. A conductor that is not up is told of, not an error.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
kit chuck-herdr-alpha willdan switchboard-kit >/dev/null
crew state init wldn >/dev/null
export CREW_LABEL=wldn
crew bolt new smoke "Prove the loop." --repo switchboard-kit >/dev/null
crew bolt new later "What comes next." --repo switchboard-kit >/dev/null
prompts() { grep "^chuck-herdr-alpha wldn-1 agent prompt $1-conductor " "$CREW_TEST_LOG" || true; }

expect_ok crew bolt give swb-2 later
has "$out" "swb-2-conductor is not up: crew up swb-2 starts and greets it"
ok "a bolt given to a team that is not up says crew up will greet its conductor"

p=$(as chuck-herdr-alpha herdr --session wldn-1 workspace create --cwd / --label swb-1 | jq -r .result.root_pane.pane_id)
as chuck-herdr-alpha herdr --session wldn-1 stub agent "$p" swb-1-conductor
: > "$CREW_TEST_LOG"
expect_ok crew bolt give swb-1 smoke
has "$out" "swb-1-conductor greeted"
eq "$(prompts swb-1 | wc -l | tr -d ' ')" "1"
has "$(prompts swb-1)" "Your team now holds the bolt smoke. Read where your bolt stands with"
ok "a bolt given to a team that is up greets its conductor once, with no bare notice of the write"

as chuck-herdr-alpha herdr --session wldn-1 stub status swb-1-conductor blocked
: > "$CREW_TEST_LOG"
( /bin/sleep 3; as chuck-herdr-alpha herdr --session wldn-1 stub status swb-1-conductor idle ) &
expect_ok crewpy greet swb-1
wait
has "$out" "swb-1-conductor is waiting on a question in its pane; answer it there and it will be greeted"
has "$out" "swb-1-conductor greeted"
eq "$(prompts swb-1 | wc -l | tr -d ' ')" "1"
ok "a conductor stopped on a question is greeted once it is answered"

box=chuck-herdr-alpha
sid=$(as $box herdr --session wldn-1 agent get swb-1-conductor | jq -r .result.agent.agent_session.value)
tx=$(transcript $box "$sid" <<'EOF'
{"type":"user","message":{"role":"user","content":"Go on with the bolt?"}}
EOF
)
printf '{"session_id":"%s","transcript_path":"%s","tool_name":"AskUserQuestion","tool_use_id":"toolu_g1","tool_input":{}}' "$sid" "$tx" |
  as $box env CREW_AGENT=swb-1-conductor python3 "$CREW/plugin/hooks/questions"
eq "$(as $box herdr --session wldn-1 agent get swb-1-conductor | jq -r .result.agent.agent_status)" "idle"
: > "$CREW_TEST_LOG"
( /bin/sleep 3
  echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"toolu_g1","content":"User has answered your questions"}]}}' >> "$tx" ) &
expect_ok crewpy greet swb-1
wait
eq "$(grep -c "swb-1-conductor is waiting on a question in its pane; answer it there and it will be greeted" <<<"$out")" "1"
has "$out" "swb-1-conductor greeted"
eq "$(prompts swb-1 | wc -l | tr -d ' ')" "1"
ok "a conductor herdr reports idle, with a question crew's hook saw it open, is greeted once the question is answered"
