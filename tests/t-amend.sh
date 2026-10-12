# A unit in flight goes back through construct: the plan's Amended mark, the stage it gives a unit whatever its tasks
# say until construct has committed again, construct run again at any stage before merge, code, verify and merge
# refused while the mark counts, and the unit going on from its tasks once construct has committed, with no approval
# asked. Construct on a unit whose intent was amended is anyone's to start, sends the amendment's words read from the
# mark, and names the card of the verify row the unit held before. Each scenario of the bolt-plan and bolt-teams specs
# on amending a unit in flight, and of an-amendment-runs-construct-again-itself's bolt-teams.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
tip() { git --git-dir "$ws" rev-parse wldn/main; }
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
mark() { by_hand "p.unit('$1').set('Amended', '$2')"; }
# approved_by_hand <n> <case> <do>: proposals.rec on the branch holds proposal n, approved, as an approval leaves it
approved_by_hand() {
  local w=$T/hand; rm -rf "$w"; git clone -q -b wldn/main "$ws" "$w"
  printf '\nProposal: %s\nCase: %s\nDo: %s\nState: approved\nOpened: 2026-10-10\nBy: wldn-planner\nClosed: 2026-10-10\n' "$1" "$2" "$3" >> "$w/proposals.rec"
  recfix --check "$w/proposals.rec" || fail "proposal $1 by hand fails recfix --check"
  commit_all "$w" "plan: by hand"; git -C "$w" push -q origin wldn/main
}
old_schema='old = {plan.declares(q): q for q in plan.Plan(plan.HEADER.replace(" Amended", "")).paras if plan.declares(q)}; p.paras = [old.get(plan.declares(x), x) for x in p.paras]'

# A branch started before the mark was allowed: it reads, and state init or any write brings its descriptors in step.
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
by_hand "$old_schema"
lacks "$(plan -t Unit -c; cat "$T/plan.rec")" "Amended"
expect_ok crew bolts; has "$out" "tenant-environments"
expect_ok crew state init wldn
has "$out" "brought the plan's record descriptors in step with crew's"
plan -t Unit -c >/dev/null; has "$(grep '^%allowed: Unit' "$T/plan.rec")" "Amended"
expect_ok crew state init wldn; has "$out" "nothing to do"
by_hand "$old_schema"
crew unit add coding "Unit coding." --bolt tenant-environments >/dev/null 2>&1
plan -t Unit -c >/dev/null; has "$(grep '^%allowed: Unit' "$T/plan.rec")" "Amended"
mark coding proposal/4
plan -t Unit -c >/dev/null; recfix --check "$T/plan.rec" || fail "a plan holding Amended: proposal/4 fails recfix --check"
eq "$(plan -t Unit -e "Unit = 'coding'" -P Amended)" "proposal/4"
by_hand "p.unit('coding').drop('Amended')"
ok "a plan from before the mark still reads, and state init or the next write brings its descriptors in step"

# Units with ticked tasks in each state of the mark, beside one never amended.
for u in m-proposal m-intent m-started m-committed; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null 2>&1; done
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
for u in coding m-proposal m-intent m-started m-committed; do
  p=$(place "$k" tenant-environments $u); change "$p" $u 2 3; commit_all "$p" "docs($u): the change"
done
rewrite "$kd/places/m-intent/openspec/changes/m-intent/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/m-intent" "feat(m-intent): the last task"
started=$(git -C "$k" rev-parse unit/m-started); committed=$(git -C "$k" rev-parse unit/m-committed)
git -C "$kd/places/m-committed" commit -q --allow-empty -m "docs(m-committed): the change again"
mark m-proposal proposal/4; mark m-intent intent; mark m-started "$started"; mark m-committed "$committed"
expect_ok crew bolts --json; j=$out
st() { jq -r --arg u "$1" '[.partitions[].plans[].bolts[].units[] | select(.unit == $u) | .stage] | first' <<<"$j"; }
for pair in coding:code m-proposal:amended m-intent:amended m-started:construct m-committed:code; do eq "$(st "${pair%%:*}")" "${pair#*:}"; done
expect_ok crew bolts
has "$out" "  m-proposal                               amended      places/m-proposal"
has "$out" "  m-started                                construct    places/m-started"
has "$out" "  m-committed                              code 2/3     places/m-committed"
has "$out" "  coding                                   code 2/3     places/coding"
ok "a marked unit reads amended, construct while its head is where construct started, and from its tasks once construct has committed"

# Construct run again, by the conductor and by the user.
last() {
  as "$1" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and all(o in e["On"] for o in sys.argv[3:])]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "${@:2}"
}
# field <host> <act> <field> [object...]: a field of the last entry of the act naming every object given
field() { local h=$1 a=$2 f=$3; shift 3; last "$h" "$a" "$@" | jq -r --arg f "$f" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'; }
last_launch() { tail -1 "$CREW_TEST_CLAUDE_LOG" | jq -r '([.argv | to_entries[] | select(.value == "--name") | .key][0]) as $i | "\(.argv[0:4] | join(" ")) | \(.argv[$i + 1]) | \(.cwd)"'; }
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
pane() { herdr_state $box wldn-1 ".agents | to_entries[] | select(.value.name == \"$1\") | .key"; }
export CREW_AGENT=swb-1-conductor

head=$(git -C "$k" rev-parse unit/coding)
expect_ok crew unit run coding construct "Use the words the user gave."
has "$out" "swb-1-unit-1 has coding: construct, in $kd/places/coding"
eq "$(plan -t Unit -e "Unit = 'coding'" -P Amended)" "$head"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "plan(tenant-environments): coding amended, construct runs again (swb-1-conductor)"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort high | swb-1-unit-1 | $kd/places/coding"
eq "$(prompt_to swb-1-unit-1)" "'/opsx:propose coding Unit coding. Use the words the user gave.'"
as $box herdr --session wldn-1 stub status "$(pane swb-1-unit-1)" working  # writing, as a stage agent is until it settles
eq "$(stage coding)" "construct"
eq "$(field $box stage.start Amended stage/coding/construct)" "yes"
eq "$(field $box stage.start Commit stage/coding/construct)" "WilldanGroup/crew-state@$(tip)"
has "$(git --git-dir "$ws" log -1 --format=%B wldn/main)" "Crew-Entry: $(field $box stage.start Id stage/coding/construct)"
ok "construct on a unit in code marks it amended at its head, in the conductor's write, and starts a fresh agent with the user's words"

expect_fail "unit coding was amended and its change is being written again, and has not been committed" crew unit run coding code
has "$(field $box stage.start Refused stage/coding/code)" "unit coding was amended and its change is being written again"
echo "Written again." >> "$kd/places/coding/openspec/changes/coding/design.md"; commit_all "$kd/places/coding" "docs(coding): written again"
eq "$(stage coding)" "code"
as $box herdr --session wldn-1 stub status "$(pane swb-1-unit-1)" idle
expect_ok crew unit wait coding
has "$out" "swb-1-unit-1 delivered construct on coding: its change is committed at $(git -C "$k" rev-parse --short unit/coding)"
eq "$(field $box stage.end Result stage/coding/construct)" "code"
eq "$(field $box stage.end Ended stage/coding/construct)" "delivered"
eq "$(plan -t Unit -e "Unit = 'coding'" -P Amended)" ""
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "plan(tenant-environments): coding constructed again, its mark cleared (swb-1-conductor)"
git --git-dir "$ws" show "wldn/main:runs/$box/$(date -u +%F).rec" | grep -q "^Act: stage.end" || fail "the write that clears the mark carries no construct end"
expect_ok crew unit run coding code
eq "$(prompt_to swb-1-unit-1)" "'/opsx:apply coding'"
ok "code, verify and merge are refused entries while construct runs again; once it commits the unit goes on from its tasks, nobody asked to approve, and the write carrying construct's end clears the mark"

# A planned unit, sent back by the user at a shell.
unset CREW_AGENT
crew unit add fresh "Unit fresh." --bolt tenant-environments >/dev/null 2>&1
pf=$(place "$k" tenant-environments fresh); change "$pf" fresh 0 2; commit_all "$pf" "docs(fresh): the change"
eq "$(stage fresh)" "planned"
CREW_AGENT=swb-2-conductor expect_fail "unit fresh is in planned, so construct run again marks it amended: a plan write only swb-1-conductor or the user makes" \
  crew unit run fresh construct
eq "$(plan -t Unit -e "Unit = 'fresh'" -P Amended)" ""
expect_ok crew unit run fresh construct "The user wants a table."
eq "$(plan -t Unit -e "Unit = 'fresh'" -P Amended)" "$(git -C "$k" rev-parse unit/fresh)"
has "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "fresh amended, construct runs again ($me@mac-studio)"
eq "$(stage fresh)" "construct"
echo table >> "$pf/openspec/changes/fresh/design.md"; commit_all "$pf" "docs(fresh): a table"
eq "$(stage fresh)" "planned"
eq "$(plan -t Unit -e "Unit = 'fresh'" -P Amended)" "$(git -C "$k" rev-parse unit/fresh~1)"
HOST=$box crew status swb-1 >/dev/null 2>&1
eq "$(plan -t Unit -e "Unit = 'fresh'" -P Amended)" ""
ok "the user sends a planned unit back to construct, which marks it, and it is planned again once construct commits; the team's next read clears the mark"

# An intent amended, by the user, of a unit that was in verify: the conductor brought back runs its construct, told
# why it runs and shown the card the amendment ended.
export CREW_AGENT=swb-1-conductor
: > "$CREW_TEST_LOG"
expect_ok crew unit run m-intent construct
has "$out" "Close your Pending You card for verify/m-intent, if one is open, with what was done."
has "$(prompt_to swb-1-unit-3)" "/opsx:propose m-intent Unit m-intent. This unit"
has "$(prompt_to swb-1-unit-3)" "s intent was amended by the user; revise the existing change to it.'"
eq "$(plan -t Unit -e "Unit = 'm-intent'" -P Amended)" "$(git -C "$k" rev-parse unit/m-intent)"
eq "$(stage m-intent)" "construct"
: > "$CREW_TEST_LOG"; before=$(tip)
expect_ok crew unit run m-intent construct --force
eq "$(tip)" "$before"
eq "$(field $box stage.start Amended stage/m-intent/construct)" ""
lacks "$out" "Close your Pending You card"
ok "an amended intent waits for construct, which is told the intent was amended by the user and names the verify card; run again before it commits, nothing is marked again"

# Merged work is not amended.

# An intent amended by an approved proposal: anyone may start its construct, the user having approved it, and the
# fresh agent is given the planner's case; the mark moves in the starter's name.
approved_by_hand 4 "The operator reads the deploy's log first." 'unit amend m-proposal "Unit m-proposal, amended."'
by_hand "p.unit('m-proposal').set('Intent', 'Unit m-proposal, amended.')"
export CREW_AGENT=wldn-planner
expect_ok crew unit run m-proposal construct
has "$out" "swb-1-unit-4 has m-proposal: construct"
eq "$(prompt_to swb-1-unit-4)" "'/opsx:propose m-proposal Unit m-proposal, amended. This unit'\"'\"'s intent was amended by proposal 4; revise the existing change to it. The planner'\"'\"'s case, as the user approved it: The operator reads the deploy'\"'\"'s log first.'"
eq "$(plan -t Unit -e "Unit = 'm-proposal'" -P Amended)" "$(git -C "$k" rev-parse unit/m-proposal)"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "plan(tenant-environments): m-proposal amended, construct runs again (wldn-planner)"
eq "$(field $box stage.start Amended stage/m-proposal/construct)" "yes"
eq "$(stage m-proposal)" "construct"
ok "a planner starts construct on a unit an approved proposal amended, and its agent is given the planner's case"
