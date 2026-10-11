# crew unit amend <unit> "<new intent>": a unit's intent replaced, by the user directly or by the planner only inside
# a proposal; a unit with a worktree is marked amended, and the amendment itself runs its construct again on its
# team's host in the applier's name and tells its conductor what started, or why nothing did and the card it ended;
# merged work is refused. A proposal shows an amendment as before and after. Each scenario of unit-amendments' and
# an-amendment-runs-construct-again-itself's bolt-plan, bolt-teams and plan-proposals specs.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
props() { git --git-dir "$ws" show wldn/main:proposals.rec > "$T/p.rec"; recsel -C "$@" "$T/p.rec"; }
tip() { git --git-dir "$ws" rev-parse wldn/main; }
prompts() { grep "^$box wldn-1 agent prompt $1-conductor " "$CREW_TEST_LOG" || true; }
proposal() { printf '%s\n' "$@" > "$T/proposal.rec"; echo "$T/proposal.rec"; }
pane() { herdr_state $box wldn-1 ".agents | to_entries[] | select(.value.name == \"$1\") | .key"; }
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
# field <host> <act> <field> <object>: a field of the last entry of the act naming the object, in that host's run record
field() {
  as "$1" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and sys.argv[3] in e["On"]]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$2" "$4" | jq -r --arg f "$3" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'
}
crew bolt new tenant-environments "A tenant holds environments of its own." --repo switchboard-kit >/dev/null
for u in cfn-lint-treefmt the-deploy-is-logged in-verify merged-one; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null 2>&1; done
crew unit add queued-one "Later work." --repo switchboard-kit >/dev/null 2>&1
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
for u in cfn-lint-treefmt the-deploy-is-logged; do
  p=$(place "$k" tenant-environments $u); change "$p" $u 1 3; commit_all "$p" "docs($u): the change"
done
p=$(place "$k" tenant-environments in-verify); change "$p" in-verify 3 3; commit_all "$p" "docs(in-verify): the change"
change "$kd/bolts/tenant-environments" merged-one 2 2; commit_all "$kd/bolts/tenant-environments" "feat(merged-one): merged"
c=$(as $box herdr --session wldn-1 workspace create --cwd / --label swb-1 | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-1 stub agent "$c" swb-1-conductor

: > "$CREW_TEST_LOG"; before=$(tip)
expect_ok crew unit amend queued-one "Later work, done another way."
eq "$(plan -t Unit -e "Unit = 'queued-one'" -P Intent,Amended)" "Later work, done another way."
eq "$(git --git-dir "$ws" diff "$before" wldn/main -- plan.rec | grep '^[-+][A-Z]')" $'-Intent: Later work.\n+Intent: Later work, done another way.'
eq "$(prompts swb-1)" ""
eq "$(field mac-studio unit.amend On unit/queued-one)" "unit/queued-one"
grep -q "unit run" "$CREW_TEST_LOG" && fail "an amendment to a queued unit ran something"
ok "a queued unit's intent is replaced, and nothing else changes"

: > "$CREW_TEST_LOG"
expect_ok crew unit amend the-deploy-is-logged "The deploy writes a log the operator can search."
has "$out" "swb-1-unit-1 has the-deploy-is-logged: construct, in $kd/places/the-deploy-is-logged"
eq "$(plan -t Unit -e "Unit = 'the-deploy-is-logged'" -P Intent)" "The deploy writes a log the operator can search."
eq "$(git --git-dir "$ws" log -2 --format=%s wldn/main)" "plan(tenant-environments): the-deploy-is-logged amended, construct runs again ($me@mac-studio)
plan(tenant-environments): amend the-deploy-is-logged ($me@mac-studio)"
eq "$(plan -t Unit -e "Unit = 'the-deploy-is-logged'" -P Amended)" "$(git -C "$k" rev-parse unit/the-deploy-is-logged)"
eq "$(stage the-deploy-is-logged)" "construct"
eq "$(prompt_to swb-1-unit-1)" "'/opsx:propose the-deploy-is-logged The deploy writes a log the operator can search. This unit'\"'\"'s intent was amended by the user; revise the existing change to it.'"
eq "$(field $box stage.start By stage/the-deploy-is-logged/construct)" "$me@mac-studio"
eq "$(field $box stage.start Amended stage/the-deploy-is-logged/construct)" "yes"
has "$(prompts swb-1)" "intent was amended by the user, and construct runs again on it in swb-1-unit-1: wait for it (crew unit wait the-deploy-is-logged); once it has committed, the unit goes on from its tasks."
lacks "$(prompts swb-1)" "Close your Pending You card"
ok "a unit in code amended by the user has its construct started by the amendment, in the user's name, and its conductor is told to wait for it"

# Construct ran and committed, so the unit goes on from its tasks, and they are all ticked: it is in verify. The slot's
# agent is still working when it is amended again.
as $box herdr --session wldn-1 stub status "$(pane swb-1-unit-1)" working
echo "Written again." >> "$kd/places/the-deploy-is-logged/openspec/changes/the-deploy-is-logged/design.md"
rewrite "$kd/places/the-deploy-is-logged/openspec/changes/the-deploy-is-logged/tasks.md" 's/- \[ \]/- [x]/'
commit_all "$kd/places/the-deploy-is-logged" "docs(the-deploy-is-logged): written again"
eq "$(stage the-deploy-is-logged)" "verify"
: > "$CREW_TEST_LOG"; before=$(tip)
expect_ok crew unit amend the-deploy-is-logged "The deploy writes a log the operator can search, kept for a year."
has "$out" "construct did not start on unit the-deploy-is-logged: swb-1-unit-1 is working; add --force to end it anyway"
eq "$(plan -t Unit -e "Unit = 'the-deploy-is-logged'" -P Intent,Amended)" $'The deploy writes a log the operator can search, kept for a year.\nintent'
eq "$(git --git-dir "$ws" rev-parse wldn/main~1)" "$before"
eq "$(stage the-deploy-is-logged)" "amended"
grep -qE "agent prompt ($(pane swb-1-unit-1)|swb-1-unit-1) " "$CREW_TEST_LOG" && fail "the working agent in the slot was sent something"
has "$(field $box stage.start Refused stage/the-deploy-is-logged/construct)" "swb-1-unit-1 is working"
eq "$(prompts swb-1 | wc -l | tr -d ' ')" "1"
has "$(prompts swb-1)" "intent was amended by the user, and construct did not start: swb-1-unit-1 is working; add --force to end it anyway. Run it once it can (crew unit run the-deploy-is-logged construct); once it has committed, the unit goes on from its tasks."
has "$(prompts swb-1)" "Close your Pending You card for verify/the-deploy-is-logged, if one is open, with what was done.'"
ok "an amendment whose construct cannot start, the slot's agent working, stands: the unit reads amended, and its conductor is told why and the card it ended"

before=$(tip)
expect_fail "unit merged-one has merged into its bolt, so it is not amended: a defect in it is a fix, and new work is a new unit" \
  crew unit amend merged-one "Something else."
CREW_AGENT=wldn-planner expect_fail "the planner changes the plan through a proposal: crew plan propose, not crew unit amend" \
  crew unit amend cfn-lint-treefmt "Something else."
CREW_AGENT=swb-1-conductor expect_fail "swb-1-conductor does not write the plan with crew unit amend: tell wldn-planner" \
  crew unit amend cfn-lint-treefmt "Something else."
eq "$(tip)" "$before"
has "$(field mac-studio unit.amend Refused unit/merged-one)" "has merged into its bolt"
ok "a merged unit is refused, and so is the planner's direct amendment and a conductor's"

# The planner proposes amending a unit in code and one in verify, in the bolt swb-1 holds.
export CREW_AGENT=wldn-planner
: > "$CREW_TEST_LOG"; before=$(tip)
expect_ok crew plan propose "$(proposal 'Case: cfn-lint is already in treefmt; what the unit should do is fail the check on a warning.' \
  'Do: unit amend cfn-lint-treefmt "cfn-lint in treefmt fails the check on a warning as well as an error"' \
  'Do: unit amend in-verify "in-verify reads its intent from the plan"')"
has "$out" "proposal 1 is open, waiting on swb-1-conductor, then the user"
eq "$(plan -t Unit -e "Unit = 'cfn-lint-treefmt'" -P Intent,Amended)" "Unit cfn-lint-treefmt."
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v '^runs/')" "proposals.rec"
has "$(prompts swb-1)" "Proposal 1 would change your bolt: unit amend cfn-lint-treefmt"
expect_ok crew plan proposed 1
has "$out" "1. **Amend unit \`cfn-lint-treefmt\`** in bolt \`tenant-environments\` (swb-1), now in code"
has "$out" "   Intent, as it stands: Unit cfn-lint-treefmt."
has "$out" "   Intent, as proposed:  cfn-lint in treefmt fails the check on a warning as well as an error"
has "$out" "   On approval: construct runs again at once in swb-1's slot, and once that has committed the unit goes on from its tasks with no approval asked, its revised change due for the next batch."
has "$out" "2. **Amend unit \`in-verify\`** in bolt \`tenant-environments\` (swb-1), now in verify"
has "$out" "- swb-1-conductor, to agree, or tell wldn-planner why not"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "plan(proposal 1): propose: amend cfn-lint-treefmt, amend in-verify (wldn-planner)"
ok "an amendment is proposed with the intent unchanged, its conductor is told, and its page shows both intents, the stage and what follows"

expect_fail "proposal 1 waits on the agreement of swb-1-conductor" crew plan approve 1
HOST=$box CREW_AGENT=swb-1-conductor expect_ok crew plan agree 1
expect_ok crew plan proposed 1; has "$out" "- agreed: swb-1"; lacks "$out" "- swb-1-conductor, to agree"
: > "$CREW_TEST_LOG"
expect_ok crew plan approve 1
has "$out" "swb-1-unit-2 has cfn-lint-treefmt: construct, in $kd/places/cfn-lint-treefmt"
has "$out" "swb-1-unit-3 has in-verify: construct, in $kd/places/in-verify"
approval=$(git --git-dir "$ws" log --format=%H --grep='^plan(proposal 1): approve' -1 wldn/main)
eq "$(git --git-dir "$ws" show "$approval:plan.rec" | recsel -t Unit -e "Unit = 'cfn-lint-treefmt'" -P Intent,Amended)" \
  $'cfn-lint in treefmt fails the check on a warning as well as an error\nproposal/1'
eq "$(plan -t Unit -e "Unit = 'cfn-lint-treefmt'" -P Amended)" "$(git -C "$k" rev-parse unit/cfn-lint-treefmt)"
eq "$(stage cfn-lint-treefmt)" "construct"
eq "$(stage in-verify)" "construct"
eq "$(field mac-studio unit.amend From unit/cfn-lint-treefmt)" "proposal/1"
eq "$(field mac-studio unit.amend Commit unit/cfn-lint-treefmt)" "WilldanGroup/crew-state@$approval"
for u in cfn-lint-treefmt in-verify; do
  eq "$(field $box stage.start By stage/$u/construct)" "wldn-planner"
  eq "$(field $box stage.start Amended stage/$u/construct)" "yes"
done
expect_ok crew plan proposed 1; has "$out" "Closed"
ok "approval waits for the conductor, then replaces each intent, and starts each unit's construct in the approver's name"

has "$(prompt_to swb-1-unit-2)" "/opsx:propose cfn-lint-treefmt cfn-lint in treefmt fails the check on a warning as well as an error This unit"
has "$(prompt_to swb-1-unit-2)" "s intent was amended by proposal 1; revise the existing change to it. The planner"
has "$(prompt_to swb-1-unit-2)" "s case, as the user approved it: cfn-lint is already in treefmt; what the unit should do is fail the check on a warning."
has "$(prompts swb-1)" "Unit cfn-lint-treefmt"
has "$(prompts swb-1)" "intent was amended by proposal 1, and construct runs again on it in swb-1-unit-2: wait for it (crew unit wait cfn-lint-treefmt); once it has committed, the unit goes on from its tasks."
has "$(prompts swb-1)" "intent was amended by proposal 1, and construct runs again on it in swb-1-unit-3: wait for it (crew unit wait in-verify)"
has "$(prompts swb-1)" "wldn-planner ran construct on unit in-verify. Close your Pending You card for verify/in-verify, if one is open, with what was done."
lacks "$(prompts swb-1)" "verify/cfn-lint-treefmt"
trace=$(crew trace unit/cfn-lint-treefmt)
# in-verify's amendment is reached through proposal 1, as a sibling's history is
eq "$(grep -v 'refused:' <<<"$trace" | grep -v ' unit/in-verify ← ' | awk '{print $3}' | tr '\n' ' ')" "unit.add plan.propose plan.agree plan.approve unit.amend stage.start "
has "$(grep ' stage.start ' <<<"$trace")" "wldn-planner"
ok "each fresh construct agent is given the new intent and the planner's case, the conductor is told to wait and to close the verify card the amendment ended, and the trace shows the way there"

# The construct cannot start because its team's host does not answer. A host down from the start leaves the unit's
# stage unread, so nothing is written (read.1). One that drops once the stage is read, before the amendment's run of
# construct reaches it, leaves the amendment standing: in-verify's construct has committed again, so it goes on from
# its tasks, all ticked: it is in verify.
unset CREW_AGENT
echo "Written again." >> "$kd/places/in-verify/openspec/changes/in-verify/design.md"
commit_all "$kd/places/in-verify" "docs(in-verify): written again"
eq "$(stage in-verify)" "verify"
echo "$box" > "$T/down"; before=$(tip)
expect_fail "cannot tell unit in-verify's stage: $box did not answer" crew unit amend in-verify "in-verify reads its intent from the plan, once."
rm "$T/down"
eq "$(tip)" "$before"
mkdir -p "$T/drops"
printf '#!/usr/bin/env bash\n[[ "$*" == *"/crew unit run "* ]] && { echo "ssh: connect to host %s port 22: Operation timed out" >&2; exit 255; }\nexec %q "$@"\n' \
  "$box" "$TESTS/stubs/ssh" > "$T/drops/ssh"
chmod +x "$T/drops/ssh"
: > "$CREW_TEST_LOG"
PATH="$T/drops:$PATH" expect_ok crew unit amend in-verify "in-verify reads its intent from the plan, once."
has "$out" "construct did not start on unit in-verify: $box did not answer (ssh: connect to host $box port 22: Operation timed out)"
eq "$(plan -t Unit -e "Unit = 'in-verify'" -P Intent,Amended)" $'in-verify reads its intent from the plan, once.\nintent'
eq "$(stage in-verify)" "amended"
grep -qE "agent prompt ($(pane swb-1-unit-3)|swb-1-unit-3) " "$CREW_TEST_LOG" && fail "in-verify's slot was sent something"
eq "$(prompts swb-1 | wc -l | tr -d ' ')" "1"
has "$(prompts swb-1)" "intent was amended by the user, and construct did not start: $box did not answer (ssh: connect to host $box port 22: Operation timed out). Run it once it can (crew unit run in-verify construct); once it has committed, the unit goes on from its tasks."
has "$(prompts swb-1)" "Close your Pending You card for verify/in-verify, if one is open, with what was done.'"
ok "an amendment whose team's host does not answer is refused unread, and one whose host drops before its construct runs stands: the unit reads amended, and its conductor is told why and the card it ended"

# The construct cannot start because its team is down: cfn-lint-treefmt's construct has committed again, so it goes on
# from its tasks, in code, and then the team is taken down, its conductor with it.
echo "Written again." >> "$kd/places/cfn-lint-treefmt/openspec/changes/cfn-lint-treefmt/design.md"
commit_all "$kd/places/cfn-lint-treefmt" "docs(cfn-lint-treefmt): written again"
eq "$(stage cfn-lint-treefmt)" "code"
expect_ok crew down swb-1 --force
[[ -z $(herdr_state $box wldn-1 ".agents[\"$c\"] // empty") ]] || as $box herdr --session wldn-1 agent prompt "$c" /exit >/dev/null
: > "$CREW_TEST_LOG"
expect_ok crew unit amend cfn-lint-treefmt "cfn-lint in treefmt fails the check on any finding."
has "$out" "construct did not start on unit cfn-lint-treefmt: swb-1 is down; crew up swb-1 brings it back"
has "$out" "swb-1-conductor is not up: unit cfn-lint-treefmt waits, amended, for construct to be run again"
eq "$(plan -t Unit -e "Unit = 'cfn-lint-treefmt'" -P Intent,Amended)" $'cfn-lint in treefmt fails the check on any finding.\nintent'
eq "$(stage cfn-lint-treefmt)" "amended"
eq "$(herdr_state $box wldn-1 '.agents | length')" "0"
eq "$(prompts swb-1)" ""
has "$(field $box stage.start Refused stage/cfn-lint-treefmt/construct)" "swb-1 is down"
expect_fail "swb-1 is down; crew up swb-1 brings it back" crew unit run the-deploy-is-logged construct
ok "an amendment whose team is down stands: no stage starts on a team taken down, the unit reads amended, and with its conductor down too crew says it is not up and what waits"

# Every stage is refused on a team taken down, not construct alone, before anything is written.
: > "$CREW_TEST_LOG"; before=$(tip)
expect_fail "swb-1 is down; crew up swb-1 brings it back" crew unit run the-deploy-is-logged code
eq "$(tip)" "$before"
grep -q "agent prompt" "$CREW_TEST_LOG" && fail "a pane was sent something while swb-1 is down"
has "$(field $box stage.start Refused stage/the-deploy-is-logged/code)" "swb-1 is down"
ok "code on a team taken down is refused before anything is written: the plan's tip stays, no slot is prompted, and the refusal is recorded"
