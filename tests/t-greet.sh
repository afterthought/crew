# A conductor is greeted to carry on with its bolt: by crew bolt give when it is up, by crew up when it starts,
# and once it is answered when it starts stopped on a question, whether herdr sees the question or crew's own hook
# saw it open. A conductor that is not up is told of, not an error. A conductor brought back is told which units of
# its bolt wait amended: its greeting opens with them, and crew resume, which greets nobody, sends them as crew's
# notice; a unit whose construct runs already is not named, and a plan crew cannot read is said.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
k=$(kit chuck-herdr-alpha willdan switchboard-kit)
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


ws=$(remote WilldanGroup/crew-state)
# by_hand <python>: plan.rec edited on the branch by hand, the python statement changing `p`, a plan.Plan
by_hand() {
  local w=$T/hand; rm -rf "$w"; git clone -q -b wldn/main "$ws" "$w"
  python3 - "$CREW/plugin/lib" "$w/plan.rec" "$1" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
exec(sys.argv[3])
open(f, "w").write(p.text())
PY
  commit_all "$w" "plan: by hand"; git -C "$w" push -q origin wldn/main
}
for u in amended-one running-one; do
  crew unit add $u "Unit $u." --bolt later >/dev/null 2>&1
  p=$(place "$k" later $u); change "$p" $u 1 3; commit_all "$p" "docs($u): the change"
done
by_hand "p.unit('amended-one').set('Amended', 'intent'); p.unit('running-one').set('Amended', '$(git -C "$k" rev-parse unit/running-one)')"
eq "$(stage amended-one)" "amended"; eq "$(stage running-one)" "construct"
: > "$CREW_TEST_LOG"
expect_ok crew up swb-2
has "$out" "swb-2-conductor greeted"
eq "$(prompts swb-2 | wc -l | tr -d ' ')" "1"
has "$(prompts swb-2)" "'[crew] Unit amended-one was amended and no construct runs on it: run construct on it now (crew unit run amended-one construct). Read where your bolt stands with"
lacks "$(prompts swb-2)" "running-one"
: > "$CREW_TEST_LOG"
expect_ok crew restart swb-2 conductor
eq "$(prompts swb-2 | wc -l | tr -d ' ')" "1"
has "$(prompts swb-2)" "'[crew] Unit amended-one was amended and no construct runs on it: run construct on it now (crew unit run amended-one construct). Read where your bolt stands with"
ok "crew up and crew restart greet a conductor once, opening with the unit that waits amended and not the one whose construct runs"

crew down swb-2 >/dev/null; : > "$CREW_TEST_LOG"
expect_ok crew resume swb-2 conductor
eq "$(prompts swb-2)" "chuck-herdr-alpha wldn-1 agent prompt swb-2-conductor '[crew] Unit amended-one was amended and no construct runs on it: run construct on it now (crew unit run amended-one construct).'"
by_hand "p.unit('amended-one').drop('Amended')"
crew down swb-2 >/dev/null; : > "$CREW_TEST_LOG"
expect_ok crew resume swb-2 conductor
eq "$(prompts swb-2)" ""
: > "$CREW_TEST_LOG"
expect_ok crew resume swb-2 conductor
has "$out" "swb-2-conductor is already up"
eq "$(prompts swb-2)" ""
ok "crew resume sends a conductor it brought back the amended unit once, as crew's notice, and nothing when none waits or it was up"

by_hand "p.unit('amended-one').set('Amended', 'proposal/3')"
mv "$ws" "$ws.away"
: > "$CREW_TEST_LOG"
expect_ok crew restart swb-2 conductor
mv "$ws.away" "$ws"
eq "$(prompts swb-2 | wc -l | tr -d ' ')" "1"
has "$(prompts swb-2)" "'[crew] crew could not read whether a unit of your bolt waits amended (wldn/main of WilldanGroup/crew-state could not be read: could not fetch wldn/main"
has "$(prompts swb-2)" "): read crew bolts. Read where your bolt stands with"
ok "a greeting whose plan cannot be read says so, rather than name no unit"
