# A stage ends at its deliverable, never at a quiet pane (teams.4): what each stage delivers, read since the stage
# began; the wait that returns with it and records its end; the stuck clock, which runs only while the agent waits on
# nothing of its own and says when it could not read that; a stop-short through crew needs, carried to the waiting
# wait or told to the conductor and never put in the run record; a gone agent; a fix's wait; and ops's proof.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
command -v wt >/dev/null || fail "this test needs worktrunk's wt"
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b c; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew up swb-1 >/dev/null 2>&1
crew bolt give swb-1 >/dev/null 2>&1
export CREW_AGENT=swb-1-conductor
stages=$(home_of $box)/.local/state/swb-1-team/stages
reports=$(home_of $box)/.local/state/swb-1-team/reports
pane() { herdr_state $box wldn-1 ".agents | to_entries[] | select(.value.name == \"$1\") | .key"; }
status() { as $box herdr --session wldn-1 stub status "$(pane "$1")" "$2"; }
last() {
  as $box python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and all(o in e["On"] for o in sys.argv[3:])]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$@"
}
# field <act> <field> [object...]: a field of the box's last entry of the act naming every object given
field() { local a=$1 f=$2; shift 2; last "$a" "$@" | jq -r --arg f "$f" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'; }
record_of() { as $box bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec'; }
ends() { record_of | grep -c "^Ended: " || true; }
short() { git -C "$k" rev-parse --short "$1"; }
second() { python3 -c 'import time; time.sleep(1.1)'; }  # what was committed before a stage is in an earlier second

expect_ok crew unit run a construct
expect_ok crew unit wait a --stuck 0 --timeout 0
eq "$out" "swb-1-unit-1 is stuck in construct on a: quiet for 0 minutes, with nothing committed and nothing it needs said; crew could not read whether it waits on work of its own (no transcript for its session sid-$(pane swb-1-unit-1))"
eq "$(ends)" "0"
has "$(cat "$stages")" "unit-1 a construct "
ok "a construct quiet past its limit with nothing committed is stuck, saying its session has no transcript to read; nothing is recorded"

change "$kd/places/a" a 0 2; commit_all "$kd/places/a" "docs(a): the change"
status swb-1-unit-1 working
expect_ok crew unit wait a --stuck 0 --timeout 0
eq "$out" "construct on a is still running after the wait's 0 ms: swb-1-unit-1 is working; nothing is recorded yet"
status swb-1-unit-1 idle
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered construct on a: its change is committed at $(short unit/a), ready for review"
eq "$(field stage.end Ended stage/a/construct)" "delivered"
eq "$(field stage.end Delivered stage/a/construct)" "unit/a@$(short unit/a)"
eq "$(field stage.end Result stage/a/construct)" "review"
eq "$(field stage.end Observed stage/a/construct)" ""
eq "$(cat "$stages")" ""
expect_ok crew unit wait a
eq "$out" "construct on a has ended: swb-1-unit-1 delivered unit/a@$(short unit/a)"
ok "a committed change ends construct only once its agent stops working, and the wait records it with the head it delivered"

crew unit approve a >/dev/null
expect_ok crew unit run a code
rewrite "$kd/places/a/openspec/changes/a/tasks.md" 's/- \[ \] 1.1/- [x] 1.1/'; commit_all "$kd/places/a" "feat(a): task 1"
expect_ok crew unit wait a --stuck 0 --timeout 0
has "$out" "swb-1-unit-1 is stuck in code on a: quiet for 0 minutes, with 1 of 2 tasks ticked at its head and nothing it needs said"
expect_ok crew status swb-1
expect_ok crew status swb-1
eq "$(ends)" "1"
rewrite "$kd/places/a/openspec/changes/a/tasks.md" 's/- \[ \] 1.2/- [x] 1.2/'; commit_all "$kd/places/a" "feat(a): task 2"
expect_ok crew status swb-1
expect_ok crew status swb-1
eq "$(ends)" "2"
eq "$(field stage.end Ended stage/a/code)" "delivered"
eq "$(field stage.end Delivered stage/a/code)" "unit/a@$(short unit/a)"
eq "$(field stage.end Observed stage/a/code)" "late"
eq "$(field stage.end Tasks stage/a/code)" "2/2"
ok "code quiet with a task open has not ended, and no read records it; once every task is ticked its end is recorded late, once"

second
expect_ok crew unit run a code "Fix these findings from the verify report: the footer."
expect_ok crew unit wait a --timeout 0
eq "$out" "code on a is still running after the wait's 0 ms: swb-1-unit-1 has been quiet for 0 minutes, under the limit of 15 minutes; nothing is recorded yet"
expect_ok crew status swb-1
eq "$(ends)" "2"
echo fixed > "$kd/places/a/footer"; commit_all "$kd/places/a" "fix(a): the footer"
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered code on a: every task is ticked (2/2) at $(short unit/a)"
ok "code run again on a ticked change ends only at a commit made since it began"

mkdir -p "$reports"; old=$reports/verify-a-20260101-0000.md
echo "an old report" > "$old"; touch -t 202601010000 "$old"
expect_ok crew unit run a verify
sid=sid-$(pane swb-1-unit-1)
long=$(ago 30)
transcript $box "$sid" >/dev/null <<EOF
{"type":"assistant","timestamp":"$long","message":{"content":[{"type":"tool_use","name":"Bash"}]}}
{"type":"user","timestamp":"$long","toolUseResult":{"stdout":"","backgroundTaskId":"b8y1gomwj"}}
EOF
expect_ok crew unit wait a --stuck 60000 --timeout 0
eq "$out" "verify on a is still running after the wait's 0 ms: swb-1-unit-1 is waiting on 1 background task of its own; nothing is recorded yet"
transcript $box "$sid" >/dev/null <<EOF
{"type":"assistant","timestamp":"$long","message":{"content":[{"type":"tool_use","name":"Bash"}]}}
{"type":"user","timestamp":"$long","toolUseResult":{"stdout":"","backgroundTaskId":"b8y1gomwj"}}
{"type":"queue-operation","timestamp":"$long","operation":"enqueue","content":"<task-notification>\n<task-id>b8y1gomwj</task-id>\n<status>completed</status>\n</task-notification>"}
EOF
expect_ok crew unit wait a --stuck 60000 --timeout 0
eq "$out" "swb-1-unit-1 is stuck in verify on a: quiet for 30 minutes, with no report saved and nothing it needs said"
ok "a quiet verify waiting on suites it started is not stuck; once told they are over, its clock runs from its transcript's last record"

report=$reports/verify-a-20261008-1412.md
echo "the report" > "$report"
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered verify on a: the report is $report"
eq "$(field stage.end Delivered stage/a/verify)" "report/verify-a-20261008-1412.md"
expect_ok crew trace report/verify-a-20261008-1412.md
has "$out" "stage.end"; has "$out" "stage/a/verify unit/a agent/swb-1-unit-1 → verify 2/2, delivered report/verify-a-20261008-1412.md"
ok "an older report is not this verify's; the one it saves ends it, named in the run record and found by crew trace"

expect_ok crew unit run b construct
CREW_AGENT=swb-1-unit-2 expect_ok crew needs "a decision on which table holds tenants ZQXN"
eq "$out" "construct on b is ended, stopped short: swb-1-conductor is told what you need"
grep -qF "agent prompt swb-1-conductor '[crew tell from swb-1-unit-2] swb-1-unit-2 stopped short in construct on b. It needs: a decision on which table holds tenants ZQXN'" "$CREW_TEST_LOG" \
  || fail "the conductor was not told the agent's words, marked as from it"
eq "$(field stage.end Ended stage/b/construct)" "short"
eq "$(field stage.end Delivered stage/b/construct)" ""
eq "$(field stage.end Why stage/b/construct)" "unit(b): construct stopped short"
eq "$(cat "$stages")" ""
expect_ok crew unit wait b
eq "$out" "construct on b has ended: swb-1-unit-2 stopped short, and swb-1-conductor was told what it needs"
n=$(ends)
CREW_AGENT=swb-1-unit-2 expect_fail "swb-1-unit-2 runs no stage crew is waiting on" crew needs "x"
expect_fail "swb-1-conductor runs no stage crew is waiting on" crew needs "x"
CREW_AGENT=swb-1-unit-2 expect_fail 'crew needs "<what you tried and what you need>"' crew needs " "
eq "$(field stage.end Refused agent/swb-1-conductor)" "swb-1-conductor runs no stage crew is waiting on"
eq "$(ends)" "$n"
ok "with no wait running, a stop-short ends the stage and tells the conductor the words, marked as from the agent; the conductor and an agent with no stage owed are refused"

expect_ok crew unit run b construct
crew unit wait b --stuck 3600000 --timeout 120000 > "$T/wait.out" 2>&1 &
waiting=$!
lock=$(home_of $box)/.local/state/swb-1-team/waits/unit-2.lock
for _ in $(seq 100); do
  python3 -c 'import fcntl, sys; f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)' "$lock" 2>/dev/null || break
  python3 -c 'import time; time.sleep(0.2)'
done
expect_fail "a wait on swb-1-unit-2's stage is already running: its answer is the one to read" crew unit wait b
CREW_AGENT=swb-1-unit-2 expect_ok crew needs "the user's word ZQXM"
eq "$out" "construct on b is ended, stopped short: swb-1-conductor's wait has what you need"
wait $waiting || fail "the wait failed: $(cat "$T/wait.out")"
eq "$(cat "$T/wait.out")" "swb-1-unit-2 stopped short in construct on b. It needs: the user's word ZQXM"
grep -q "agent prompt swb-1-conductor .*ZQXM" "$CREW_TEST_LOG" && fail "the conductor was told words its wait already had"
eq "$(field stage.end Ended stage/b/construct)" "short"
[[ $(record_of) != *ZQXN* && $(record_of) != *ZQXM* ]] || fail "a stop-short's words are in the run record"
ok "with a wait running, a stop-short's words are its answer and nobody else's; no stop-short's words are in the run record"

expect_ok crew unit run c construct
as $box herdr --session wldn-1 agent prompt "$(pane swb-1-unit-3)" /exit >/dev/null
n=$(ends)
expect_ok crew unit wait c
eq "$out" "swb-1-unit-3 is no longer running: construct on c delivered nothing and said nothing it needs"
eq "$(ends)" "$n"
has "$(cat "$stages")" "unit-3 c construct "
expect_ok crew unit run c construct
eq "$(field stage.end Ended stage/c/construct)" "stopped"
eq "$(field stage.end Observed stage/c/construct)" ""
eq "$(ends)" "$((n + 1))"
ok "a wait on a gone agent says so and records nothing; the stage run again records the old one stopped"

fb=fix/tenant-environments/tidy; fp=$kd/places/fix-tenant-environments--tidy
expect_ok crew fix swb-1 tidy "The banner flickers."
expect_ok crew fix swb-1 tidy --wait --timeout 0
eq "$out" "fix $fb is still running after the wait's 0 ms: swb-1-unit-4 has been quiet for 0 minutes, under the limit of 15 minutes; nothing is recorded yet"
echo steady > "$fp/banner"; commit_all "$fp" "fix: the banner holds still"
expect_ok crew fix swb-1 tidy --wait
eq "$out" "swb-1-unit-4 delivered fix $fb: its branch is at $(short $fb)"
eq "$(field stage.end Delivered $fb)" "$fb@$(short $fb)"
expect_ok crew fix swb-1 tidy --merge
(cd "$fp" && wt merge bolt/tenant-environments --no-squash --no-remove >/dev/null 2>&1) || fail "wt merge failed"
expect_ok crew fix swb-1 tidy --wait
eq "$out" "swb-1-unit-4 delivered merge of $fb: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
eq "$(field stage.end Delivered $fb)" "bolt/tenant-environments@$(short bolt/tenant-environments)"
eq "$(field stage.end Why $fb)" "fix(tidy): merge ended"
ok "a fix waits the same way: its commits end its code, and the bolt holding it ends its merge"

expect_ok crew unit run a merge
expect_ok crew unit wait a --stuck 0 --timeout 0
has "$out" "swb-1-unit-1 is stuck in merge on a: quiet for "
has "$out" " minutes, with bolt/tenant-environments not yet holding it and nothing it needs said"
status swb-1-unit-1 working
(cd "$kd/places/a" && wt merge bolt/tenant-environments --no-squash --no-remove >/dev/null 2>&1) || fail "wt merge failed"
expect_ok crew unit wait a --timeout 0
eq "$out" "merge on a is still running after the wait's 0 ms: swb-1-unit-1 is working; nothing is recorded yet"
status swb-1-unit-1 idle
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered merge on a: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
eq "$(field stage.end Ended stage/a/merge)" "delivered"
eq "$(field stage.end Delivered stage/a/merge)" "bolt/tenant-environments@$(short bolt/tenant-environments)"
lacks "$(cat "$stages")" "unit-1 a merge "
ok "a unit's merge ends once its bolt holds the change, recorded with the bolt's head"

expect_fail "swb-2 holds no bolt" crew prove swb-2
has "$(field stage.start Refused agent/swb-2-ops)" "swb-2 holds no bolt"
expect_ok crew prove swb-1
has "$out" "swb-1-ops is asked to prove bolt/tenant-environments"
grep -qF "agent prompt swb-1-ops '[crew tell from swb-1-conductor] Deploy the bolt and work the Proof in dev list of each of its units.'" "$CREW_TEST_LOG" \
  || fail "ops was not asked for the proof, marked as from the conductor"
eq "$(field stage.start On stage/tenant-environments/proof)" "stage/tenant-environments/proof bolt/tenant-environments agent/swb-1-ops"
eq "$(field stage.start Why stage/tenant-environments/proof)" "bolt(tenant-environments): start proof"
has "$(cat "$stages")" "ops tenant-environments proof "
expect_ok crew prove swb-1 --wait --timeout 0
eq "$out" "the proof of tenant-environments is still running after the wait's 0 ms: swb-1-ops has been quiet for 0 minutes, under the limit of 15 minutes; nothing is recorded yet"
proof=$reports/proof-tenant-environments-20261008-1630.md
echo "- ✅ sign-in: passed" > "$proof"
expect_ok crew prove swb-1 --wait
eq "$out" "swb-1-ops delivered the proof of tenant-environments: $proof"
eq "$(field stage.end On stage/tenant-environments/proof)" "stage/tenant-environments/proof bolt/tenant-environments agent/swb-1-ops"
eq "$(field stage.end Delivered stage/tenant-environments/proof)" "proof/proof-tenant-environments-20261008-1630.md"
eq "$(field stage.end Why stage/tenant-environments/proof)" "bolt(tenant-environments): proof ended"
ok "crew prove asks ops for the proof and owes its end, and its wait returns with the proof file ops saved"

touch -t 202601010000 "$proof"
expect_ok crew prove swb-1 "Only the sign-in this time."
grep -qF "Deploy the bolt and work the Proof in dev list of each of its units. Only the sign-in this time.'" "$CREW_TEST_LOG" || fail "the proof's words were not sent"
CREW_AGENT=swb-1-ops expect_ok crew needs "the word of the user to deploy over the bolt of swb-2"
grep -qF "[crew tell from swb-1-ops] swb-1-ops stopped short in the proof of tenant-environments. It needs: the word of the user to deploy over the bolt of swb-2'" "$CREW_TEST_LOG" \
  || fail "the conductor was not told what ops needs"
eq "$(field stage.end Ended stage/tenant-environments/proof)" "short"
expect_ok crew prove swb-1
CREW_AGENT= expect_ok crew restart swb-1 ops
eq "$(field stage.end Ended stage/tenant-environments/proof)" "stopped"
lacks "$(cat "$stages")" "ops tenant-environments proof"
as $box herdr --session wldn-1 agent prompt swb-1-ops /exit >/dev/null
expect_fail "swb-1-ops is not up" crew prove swb-1
has "$(field stage.start Refused stage/tenant-environments/proof)" "swb-1-ops is not up"
ok "ops stops a proof short through crew needs; restarting ops ends an owed proof as stopped; a proof is refused while ops is not up"
