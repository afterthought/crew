# crew main up|down|status <label>: the "<label>" workspace with design, planner and ops tabs in the main level's
# session, and a dispatcher in "<label> dispatch" on each host with a team of the partition: in the main level's
# session on its own host, else in the session of the host's first team by name. Each agent it starts is greeted once,
# marked as crew's, side by side: one waiting on a question is greeted once it is answered, holding back no other.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
mkdir -p "$(space mac-studio willdan)/willdan-blueprints/main"
agents=("$box wldn-3 wldn-design" "$box wldn-3 wldn-planner" "$box wldn-3 wldn-ops" "$box wldn-3 wldn-dispatch-$box"
        "mac-studio wldn-5 wldn-dispatch-mac-studio")
# greetings <host> <session> <agent>: the greetings crew has typed into the agent's pane there
greetings() { grep -c "^$1 $2 agent prompt $3 '\[crew\] Read where wldn stands" "$CREW_TEST_LOG" || true; }
# greets <host> <agent>: the greet entries on the agent in wldn's run record on that host
greets() {
  as "$1" python3 -c 'import glob, os, sys; sys.path.insert(0, sys.argv[1]); import record
print(sum(1 for f in glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec")) for e in record.parse(open(f).read())
          if e["Act"] == "greet" and "agent/" + sys.argv[2] in e["On"]))' "$CREW/plugin/lib" "$2"
}
each_greeted() {  # each_greeted <n>: every agent of wldn's main level greeted n times so far, each in its host's run record
  local a h s n
  for a in "${agents[@]}"; do read -r h s n <<<"$a"; eq "$(greetings "$h" "$s" "$n")" "$1"; eq "$(greets "$h" "$n")" "$1"; done
}

expect_ok crew main up wldn
for a in wldn-design wldn-planner wldn-ops wldn-dispatch-chuck-herdr-alpha wldn-dispatch-mac-studio; do has "$out" "$a started"; done
eq "$(herdr_state $box wldn-3 '[.workspaces[].label] | join(",")')" "wldn,wldn dispatch"
eq "$(herdr_state $box wldn-3 '[.tabs[] | select(.workspace == "w1") | .label] | join(",")')" "design,planner,ops"
eq "$(herdr_state $box wldn-3 '[.agents[].name] | sort | join(",")')" "wldn-design,wldn-dispatch-chuck-herdr-alpha,wldn-ops,wldn-planner"
eq "$(herdr_state mac-studio wldn-5 '[.workspaces[].label] | join(",")')" "wldn dispatch"
eq "$(herdr_state mac-studio wldn-5 '[.agents[].name] | join(",")')" "wldn-dispatch-mac-studio"
[[ ! -e $(home_of $box)/.stub-herdr/wldn-1.json ]] || fail "the main level touched a team's session"
eq "$(jq -r 'select(.agent == "wldn-design") | "\(.host) \(.argv[1]) \(.argv[3])"' "$CREW_TEST_CLAUDE_LOG")" "$box claude-fable-5-1 xhigh"
eq "$(jq -r 'select(.agent == "wldn-dispatch-mac-studio") | "\(.host) \(.argv[3]) \(.cwd)"' "$CREW_TEST_CLAUDE_LOG")" "mac-studio medium $(space mac-studio willdan)/willdan-blueprints/main"
ok "the main level comes up in wldn-3 on the box, with a dispatcher on the box and one on mac-studio"

for a in wldn-design wldn-planner wldn-ops wldn-dispatch-chuck-herdr-alpha wldn-dispatch-mac-studio; do has "$out" "$a greeted"; done
each_greeted 1
prompt() { grep "agent prompt $1 " "$CREW_TEST_LOG"; }
has "$(prompt wldn-design)" "curate the signals that have no move"
has "$(prompt wldn-planner)" "crew plan proposed"
has "$(prompt wldn-ops)" "land nothing until it comes"
has "$(prompt wldn-dispatch-mac-studio)" "Read where wldn stands on mac-studio with"
grep -q "^$box ssh mac-studio .*agent \(get\|prompt\) wldn-dispatch-mac-studio" "$CREW_TEST_LOG" &&
  fail "mac-studio's dispatcher was greeted from another host"
ok "each agent the main level starts is greeted once with its role's greeting, in the run record of its own host"

expect_ok crew main up wldn
for a in wldn-design wldn-planner wldn-ops wldn-dispatch-chuck-herdr-alpha wldn-dispatch-mac-studio; do has "$out" "$a is already up"; done
eq "$(herdr_state $box wldn-3 '.workspaces | length')" "2"
lacks "$out" "greeted"; each_greeted 1
ok "a second main up starts nothing and greets nobody"

expect_ok crew main status wldn
for a in wldn-design wldn-planner wldn-ops wldn-dispatch-chuck-herdr-alpha wldn-dispatch-mac-studio; do has "$(grep "^$a " <<<"$out")" "idle"; done
expect_ok crew main down wldn
eq "$(herdr_state $box wldn-3 '.agents | length')" "0"; eq "$(herdr_state mac-studio wldn-5 '.agents | length')" "0"
expect_ok crew main status wldn; eq "$(grep -c 'not up' <<<"$out")" "5"
ok "main status and down reach every host"

expect_ok crew main up wldn
each_greeted 2
expect_ok crew main down wldn
ok "a main level brought up again after it was taken down greets each agent once more"

# madswan: its main level and its one team are on mac-studio, so the dispatcher shares the main level's session.
mkdir -p "$(space mac-studio madswan)/blueprints/main"
: > "$CREW_TEST_LOG"
expect_ok crew main up madswan
eq "$(herdr_state mac-studio madswan-1 '[.workspaces[].label] | join(",")')" "madswan,madswan dispatch"
eq "$(herdr_state mac-studio madswan-1 '[.agents[].name] | sort | join(",")')" "madswan-design,madswan-dispatch-mac-studio,madswan-ops,madswan-planner"
grep -q " ssh " "$CREW_TEST_LOG" && fail "madswan's main level needed no other host"
expect_fail "no partition 'nope'" crew main up nope
ok "a dispatcher on the main level's host runs in its session"

: > "$CREW_TEST_LOG"
CREW_TEST_TRUST=1 expect_ok crew main up wldn
eq "$(grep -c " agent send-keys w[0-9]*:p[0-9]* down enter" "$CREW_TEST_LOG")" "5"
ok "the folder-trust question is answered for the design agent, the planner, ops and both dispatchers"

: > "$CREW_TEST_LOG"
expect_ok crew main status swancloud
has "$out" "swancloud-planner"
lacks "$out" "did not answer"
lacks "$out" "swancloud-dispatch"
ok "a partition with no teams has no dispatcher, and its status asks no host for one"

# The planner stops on a question as it starts. The design agent and ops are greeted meanwhile; the planner's question
# is answered only once they are, and once its greeting has seen the question.
HOST=$box crew main down wldn >/dev/null
: > "$CREW_TEST_LOG"
answer() {
  local i
  for i in $(seq 300); do
    grep -q "agent prompt wldn-design '" "$CREW_TEST_LOG" && grep -q "agent prompt wldn-ops '" "$CREW_TEST_LOG" &&
      grep -q "^$box wldn-3 agent get wldn-planner\$" "$CREW_TEST_LOG" && break
    /bin/sleep 0.1
  done
  as $box herdr --session wldn-3 stub status wldn-planner idle
}
answer &
CREW_TEST_BLOCKED=wldn-planner expect_ok crew main up wldn
wait
has "$out" "wldn-planner is waiting on a question in its pane; answer it there and it will be greeted"
has "$out" "wldn-planner greeted"
eq "$(grep -c "agent prompt wldn-planner '" "$CREW_TEST_LOG")" "1"
at() { grep -n "$1" "$CREW_TEST_LOG" | head -1 | cut -d: -f1; }
answered=$(at "stub status wldn-planner idle")
(( $(at "agent prompt wldn-design '") < answered && $(at "agent prompt wldn-ops '") < answered )) ||
  fail "the design agent and ops waited on the planner's question"
(( answered < $(at "agent prompt wldn-planner '") )) || fail "the planner was greeted before its question was answered"
ok "an agent waiting on a question is greeted once it is answered, and holds back no other agent's greeting"

# The box's dispatcher, the first host's, stops on a question as it starts: mac-studio's is started and greeted meanwhile.
HOST=$box crew main down wldn >/dev/null
: > "$CREW_TEST_LOG"
answer() {
  local i
  for i in $(seq 300); do
    grep -q "agent prompt wldn-dispatch-mac-studio '" "$CREW_TEST_LOG" &&
      grep -q "^$box wldn-3 agent get wldn-dispatch-$box\$" "$CREW_TEST_LOG" && break
    /bin/sleep 0.1
  done
  as $box herdr --session wldn-3 stub status wldn-dispatch-$box idle
}
answer &
CREW_TEST_BLOCKED=wldn-dispatch-$box expect_ok crew main up wldn
wait
has "$out" "wldn-dispatch-$box is waiting on a question in its pane; answer it there and it will be greeted"
has "$out" "wldn-dispatch-$box greeted"; has "$out" "wldn-dispatch-mac-studio greeted"
eq "$(grep -c "agent prompt wldn-dispatch-$box '" "$CREW_TEST_LOG")" "1"
answered=$(at "stub status wldn-dispatch-$box idle")
(( $(at "agent prompt wldn-dispatch-mac-studio '") < answered )) || fail "mac-studio's dispatcher waited on the box's question"
(( answered < $(at "agent prompt wldn-dispatch-$box '") )) || fail "the box's dispatcher was greeted before its question was answered"
ok "a dispatcher waiting on a question holds back no other host's dispatcher"

HOST=$box crew main down wldn >/dev/null
echo mac-studio > "$CREW_TEST_ROOT/down"
HOST=$box expect_fail "mac-studio port 22: Operation timed out" crew main up wldn
has "$out" "wldn-dispatch-$box started"; has "$out" "wldn-dispatch-$box greeted"
rm "$CREW_TEST_ROOT/down"
ok "a host that does not answer fails main up, once every other host's dispatcher is up and greeted"

as $box herdr --session wldn-3 stub status wldn-design working
before=$(greets $box wldn-design)
: > "$CREW_TEST_LOG"
HOST=$box expect_ok crewpy greet-agent wldn-design --wait 2
has "$out" "wldn-design was not ready to greet; once it is: crew tell wldn-design 'Read where wldn stands with"
grep -q "agent prompt" "$CREW_TEST_LOG" && fail "an agent that never settled was sent its greeting"
eq "$(greets $box wldn-design)" "$before"
ok "an agent that never settles is reported with the crew tell that would greet it, and nothing is sent"
