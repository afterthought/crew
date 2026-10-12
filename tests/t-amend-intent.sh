# An amendment through a proposal, and one whose team is down: the planner proposes amending units in code and in
# verify, the proposal shows each as before and after, its conductor agrees, and approval replaces each intent and
# runs each construct again in the approver's name, with the planner's case; an amendment while the team is down
# stands, the unit reading amended, and every stage on a team taken down is refused before anything is written. What
# an amendment does to the plan, who may write one, and what its conductor is told are logic cases
# (tests/py/test_amend.py); one the user runs directly, the journey's (t-journey-units).
# Reads: plugin/hooks/
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
for u in cfn-lint-treefmt the-deploy-is-logged in-verify; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null 2>&1; done
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
for u in cfn-lint-treefmt the-deploy-is-logged; do
  p=$(place "$k" tenant-environments $u); change "$p" $u 1 3; commit_all "$p" "docs($u): the change"
done
p=$(place "$k" tenant-environments in-verify); change "$p" in-verify 3 3; commit_all "$p" "docs(in-verify): the change"
c=$(as $box herdr --session wldn-1 workspace create --cwd / --label swb-1 | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-1 stub agent "$c" swb-1-conductor

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
has "$out" "swb-1-unit-1 has cfn-lint-treefmt: construct, in $kd/places/cfn-lint-treefmt"
has "$out" "swb-1-unit-2 has in-verify: construct, in $kd/places/in-verify"
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

has "$(prompt_to swb-1-unit-1)" "/opsx:propose cfn-lint-treefmt cfn-lint in treefmt fails the check on a warning as well as an error This unit"
has "$(prompt_to swb-1-unit-1)" "s intent was amended by proposal 1; revise the existing change to it. The planner"
has "$(prompt_to swb-1-unit-1)" "s case, as the user approved it: cfn-lint is already in treefmt; what the unit should do is fail the check on a warning."
has "$(prompts swb-1)" "Unit cfn-lint-treefmt"
has "$(prompts swb-1)" "intent was amended by proposal 1, and construct runs again on it in swb-1-unit-1: wait for it (crew unit wait cfn-lint-treefmt); once it has committed, the unit goes on from its tasks."
has "$(prompts swb-1)" "intent was amended by proposal 1, and construct runs again on it in swb-1-unit-2: wait for it (crew unit wait in-verify)"
has "$(prompts swb-1)" "wldn-planner ran construct on unit in-verify. Close your Pending You card for verify/in-verify, if one is open, with what was done."
lacks "$(prompts swb-1)" "verify/cfn-lint-treefmt"
trace=$(crew trace unit/cfn-lint-treefmt)
# in-verify's amendment is reached through proposal 1, as a sibling's history is
eq "$(grep -v 'refused:' <<<"$trace" | grep -v ' unit/in-verify ← ' | awk '{print $3}' | tr '\n' ' ')" "unit.add plan.propose plan.agree plan.approve unit.amend stage.start "
has "$(grep ' stage.start ' <<<"$trace")" "wldn-planner"
ok "each fresh construct agent is given the new intent and the planner's case, the conductor is told to wait and to close the verify card the amendment ended, and the trace shows the way there"

# The construct cannot start because its team is down: cfn-lint-treefmt's construct has committed again, so it goes on
# from its tasks, in code, and then the team is taken down, its conductor with it.
unset CREW_AGENT
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
