# A team's and a main level's agents through the crew command on the stubs (tests.11, record 0022): crew up starts a
# team's conductor and ops on its host in one workspace, greeted once and recorded, and status, down, resume,
# restart, clear, rebuild and close act on them; a bolt given to a team that is up is cut from GitHub's main and
# restarts them in its worktree; a role resumes where its conversation began; crew main up starts the main level and a
# dispatcher on each host of the partition, each greeted once, one waiting on a question holding back no other; the
# operator gets its tabs; and crew revive brings back what a restart left empty, leaving down what was taken down.
# What each agent is greeted with, where it runs and resumes, and what a conductor brought back is told are logic
# cases (tests/py/test_teams.py); how git cuts a bolt from GitHub's main, contract cases (tests/contract/test_git.py).
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
clone WilldanGroup/willdan-blueprints "$(space mac-studio willdan)/willdan-blueprints/main"
kit mac-studio willdan atlas-kit >/dev/null
# The kit's GitHub, and another clone that pushes to it.
r=$(remote WilldanGroup/switchboard-kit); git clone -q --bare "$k" "$r"
git -C "$k" remote add origin https://github.com/WilldanGroup/switchboard-kit; git -C "$k" fetch -q origin
other=$T/elsewhere; git clone -q "$r" "$other"
pushed() { git -C "$other" pull -q --rebase origin main; echo "$1" > "$other/$1"; commit_all "$other" "feat: $1"; git -C "$other" push -q origin main; }
# field <host> <act> <field> [object]: a field of that host's last entry of the act naming the object
field() {
  as "$1" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and (len(sys.argv) < 4 or sys.argv[3] in e["On"])]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$2" ${4:+"$4"} | jq -r --arg f "$3" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'
}
count() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null' | grep -c "^Act: $2\$" || true; }
launched() { jq -r --arg a "$1" 'select(.agent == $a) | "\(.cwd) \(.argv | index("--resume") as $i | if $i then "resumed" else "fresh" end)"' "$CREW_TEST_CLAUDE_LOG" | tail -1; }
greetings() { grep -c "^$1 $2 agent prompt $3 '\[crew\]" "$CREW_TEST_LOG" || true; }

expect_ok crew up swb-1
has "$out" "swb-1-conductor started"; has "$out" "swb-1-ops started"; has "$out" "swb-1-conductor greeted"
grep -q "^mac-studio ssh $box " "$CREW_TEST_LOG" || fail "crew up did not run on the team's host"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1"
eq "$(herdr_state $box wldn-1 '[.tabs[].label] | join(",")')" "conductor"
eq "$(herdr_state $box wldn-1 '[.agents[].name] | sort | join(",")')" "swb-1-conductor,swb-1-ops"
eq "$(launched swb-1-conductor)" "$k fresh"
eq "$(greetings $box wldn-1 swb-1-conductor)" "1"
eq "$(field $box team.up On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
eq "$(field $box team.up By)" "$me@mac-studio"
eq "$(field $box greet On)" "agent/swb-1-conductor team/swb-1"
[[ -d $(home_of $box)/.local/state/swb-1-team && ! -d $(home_of mac-studio)/.local/state/swb-1-team ]] || fail "the team's state is not on its host"
expect_fail "swb-1-conductor is already up" crew up swb-1
expect_ok crew status swb-1
has "$out" "swb-1-conductor"; has "$out" "swb-1-ops"; eq "$(grep -c ' free ' <<<"$out")" "4"
pane_cwd() { herdr_state $box wldn-1 ".panes[\"$(awk -v r="$1" '$1==r{print $2}' "$(home_of $box)/.local/state/swb-1-team/panes")\"].cwd"; }
eq "$(pane_cwd conductor)" "$k"
ok "crew up starts a team's conductor and ops on its host, in one workspace with a conductor tab and in the kit's main checkout, greets the conductor once and records it; status lists them and four free slots"

crew bolt new smoke "Prove the loop." --repo switchboard-kit >/dev/null
pushed from-a-mac
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew bolt give swb-1 smoke
has "$out" "main fast-forwarded 1 commit to GitHub's"
eq "$(git -C "$k" rev-parse bolt/smoke)" "$(git -C "$other" rev-parse main)"
eq "$(launched swb-1-conductor)" "$kd/bolts/smoke fresh"; eq "$(launched swb-1-ops)" "$kd/bolts/smoke fresh"
eq "$(pane_cwd conductor)" "$kd/bolts/smoke"
eq "$(greetings $box wldn-1 swb-1-conductor)" "1"
has "$(grep "agent prompt swb-1-conductor '" "$CREW_TEST_LOG")" "Your team now holds the bolt smoke. Read where your bolt stands"
eq "$(field $box agent.restart By agent/swb-1-ops)" "$me@mac-studio"
ok "a bolt given to a team that is up is cut from GitHub's main, fetched first, and restarts its conductor and ops in the bolt's worktree, then greets the conductor once"

first=$(jq -r 'select(.agent == "swb-1-ops") | .session' "$CREW_TEST_CLAUDE_LOG" | tail -1)
expect_ok crew down swb-1
eq "$(herdr_state $box wldn-1 '.agents | length')" "0"
has "$(field $box team.down On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
: > "$CREW_TEST_LOG"; : > "$CREW_TEST_CLAUDE_LOG"
expect_ok crew resume swb-1
has "$out" "swb-1-conductor resumed"; has "$out" "swb-1-ops resumed"
eq "$(launched swb-1-ops)" "$kd/bolts/smoke resumed"
eq "$(jq -r 'select(.agent == "swb-1-ops") | .argv | .[index("--resume") + 1]' "$CREW_TEST_CLAUDE_LOG")" "$first"
eq "$(count $box agent.resume)" "2"
grep -q "agent prompt swb-1-conductor '" "$CREW_TEST_LOG" && fail "crew resume greeted the conductor"
CREW_TEST_TRUST=1 expect_ok crew restart swb-1 ops
has "$out" "swb-1-ops started"; lacks "$out" "conductor"
eq "$(grep -c "^$box wldn-1 agent send-keys w[0-9]*:p[0-9]* down enter" "$CREW_TEST_LOG")" "1"
expect_fail "no role 'fable' here; roles: conductor ops" crew restart swb-1 fable
: > "$CREW_TEST_LOG"
CREW_TEST_BYPASS=1 expect_ok crew restart swb-1 ops
eq "$(grep -c "agent send-keys" "$CREW_TEST_LOG")" "0"
expect_ok crew clear swb-1 ops
eq "$(field $box agent.clear On)" "team/swb-1 agent/swb-1-ops"
expect_ok crew rebuild swb-1
eq "$(herdr_state $box wldn-1 '[.agents[].name] | sort | join(",")')" "swb-1-conductor,swb-1-ops"
expect_ok crew close swb-1
eq "$(herdr_state $box wldn-1 '.workspaces | length')" "0"
ok "down, resume (in the folder the conversation began in, greeting nobody), restart with the folder-trust question answered and never the Bypass warning, clear, rebuild and close act on the conductor and ops, each recorded, the pane's shell in the role's folder"

for gone in "assign swb-1 coder-1 x" "opsx swb-1 explorer /opsx:propose x"; do
  if out=$(crew $gone 2>&1); then fail "crew $gone still works"; fi
  has "$out" "A team builds one bolt at a time"
done
expect_ok crew up atl-1
eq "$(herdr_state mac-studio wldn-5 '[.tabs[].label] | join(",")')" "conductor,git"
ok "assign and opsx are gone, and a team on a Mac has a git tab"

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

# After a restart: panes back with no agent in them are revived, resumed or fresh; a team taken down stays down.
gone() { local p; p=$(as $box herdr --session "$1" agent get "$2" | jq -r .result.agent.pane_id); as $box herdr --session "$1" agent prompt "$p" /exit >/dev/null; }
crew up swb-1 >/dev/null; crew up swb-2 >/dev/null; crew down swb-2 >/dev/null
gone wldn-1 swb-1-conductor; gone wldn-3 wldn-design
: > "$CREW_TEST_CLAUDE_LOG"; : > "$CREW_TEST_LOG"
HOST=$box expect_ok crew revive
has "$out" "swb-1-conductor resumed"; has "$out" "wldn-design resumed"
has "$out" "swb-2 was taken down; it stays down"
for a in swb-1-ops wldn-planner wldn-ops swb-2-conductor; do eq "$(jq -r --arg a $a 'select(.agent == $a)' "$CREW_TEST_CLAUDE_LOG" | wc -l | tr -d ' ')" "0"; done
eq "$(greetings $box wldn-1 swb-1-conductor)" "1"; eq "$(greetings $box wldn-3 wldn-design)" "1"
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
ok "crew revive brings back the agents whose panes came back empty and greets each it brought back once; a team or main level taken down stays down; main down reaches every host, and a host that does not answer fails main up once the others are up"

# A unit of swb-2's bolt waits amended: the conductor brought back is told so, by its greeting or, on resume, as crew's notice.
crew bolt new later "What comes next." --repo switchboard-kit >/dev/null
crew unit add amended-one "Unit amended-one." --bolt later >/dev/null
crew bolt give swb-2 later >/dev/null 2>&1
p=$(place "$k" later amended-one); change "$p" amended-one 1 3; commit_all "$p" "docs(amended-one): the change"
w=$T/hand; git clone -q -b wldn/main "$ws" "$w"
python3 - "$CREW/plugin/lib" "$w/plan.rec" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
p.unit("amended-one").set("Amended", "intent")
open(f, "w").write(p.text())
PY
commit_all "$w" "plan: by hand"; git -C "$w" push -q origin wldn/main
: > "$CREW_TEST_LOG"
expect_ok crew up swb-2
has "$(grep "agent prompt swb-2-conductor '" "$CREW_TEST_LOG")" "'[crew] Unit amended-one was amended and no construct runs on it: run construct on it now (crew unit run amended-one construct). Read where your bolt stands with"
crew down swb-2 >/dev/null; : > "$CREW_TEST_LOG"
expect_ok crew resume swb-2 conductor
eq "$(grep "agent prompt swb-2-conductor '" "$CREW_TEST_LOG")" "$box wldn-1 agent prompt swb-2-conductor '[crew] Unit amended-one was amended and no construct runs on it: run construct on it now (crew unit run amended-one construct).'"
ok "a conductor brought back is told the unit that waits amended: in its greeting by crew up, as crew's notice by crew resume"

# A landing is refused while the kit's main is behind GitHub's.
change "$k" amended-one 3 3; commit_all "$k" "feat: amended-one"; git -C "$kd/bolts/later" merge -q --ff-only main
pushed later-from-a-mac
expect_fail "switchboard-kit's main on chuck-herdr-alpha is 1 commit behind GitHub's" crew bolt land later
ok "a landing reads how far the kit's main is behind GitHub's, and is refused while it is"
