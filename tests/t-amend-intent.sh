# crew unit amend <unit> "<new intent>": a unit's intent replaced, by the user directly or by the planner only inside
# a proposal; a unit with a worktree is marked amended and its conductor told to run construct again; merged work is
# refused. A proposal shows an amendment as before and after. Each scenario of unit-amendments' bolt-plan and
# plan-proposals specs.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
props() { git --git-dir "$ws" show wldn/main:proposals.rec > "$T/p.rec"; recsel -C "$@" "$T/p.rec"; }
tip() { git --git-dir "$ws" rev-parse wldn/main; }
prompts() { grep "^$box wldn-1 agent prompt $1-conductor " "$CREW_TEST_LOG" || true; }
proposal() { printf '%s\n' "$@" > "$T/proposal.rec"; echo "$T/proposal.rec"; }
field() {
  as mac-studio python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and sys.argv[3] in e["On"]]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$1" "$3" | jq -r --arg f "$2" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'
}
crew bolt new tenant-environments "A tenant holds environments of its own." --repo switchboard-kit >/dev/null
for u in cfn-lint-treefmt the-deploy-is-logged merged-one; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null 2>&1; done
crew unit add queued-one "Later work." --repo switchboard-kit >/dev/null 2>&1
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
for u in cfn-lint-treefmt the-deploy-is-logged; do
  p=$(place "$k" tenant-environments $u); change "$p" $u 1 3; commit_all "$p" "docs($u): the change"
  git -C "$p" commit -q --allow-empty -m "review($u): approved" --trailer "Reviewed-by: Test User"
done
change "$kd/bolts/tenant-environments" merged-one 2 2; commit_all "$kd/bolts/tenant-environments" "feat(merged-one): merged"
c=$(as $box herdr --session wldn-1 workspace create --cwd / --label swb-1 | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-1 stub agent "$c" swb-1-conductor

: > "$CREW_TEST_LOG"; before=$(tip)
expect_ok crew unit amend queued-one "Later work, done another way."
eq "$(plan -t Unit -e "Unit = 'queued-one'" -P Intent,Amended)" "Later work, done another way."
eq "$(git --git-dir "$ws" diff "$before" wldn/main -- plan.rec | grep '^[-+][A-Z]')" $'-Intent: Later work.\n+Intent: Later work, done another way.'
eq "$(prompts swb-1)" ""
eq "$(field unit.amend On unit/queued-one)" "unit/queued-one"
ok "a queued unit's intent is replaced, and nothing else changes"

: > "$CREW_TEST_LOG"
expect_ok crew unit amend the-deploy-is-logged "The deploy writes a log the operator can search."
eq "$(plan -t Unit -e "Unit = 'the-deploy-is-logged'" -P Intent)" "The deploy writes a log the operator can search."
eq "$(plan -t Unit -e "Unit = 'the-deploy-is-logged'" -P Amended)" "intent"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "plan(tenant-environments): amend the-deploy-is-logged ($me@mac-studio)"
eq "$(stage the-deploy-is-logged)" "amended"
eq "$(prompts swb-1 | wc -l | tr -d ' ')" "1"
has "$(prompts swb-1)" "intent was amended by the user. Run construct again (crew unit run the-deploy-is-logged construct); it returns to the user"
ok "a unit in code amended by the user is marked amended, and its conductor is told to run construct again, once"

before=$(tip)
expect_fail "unit merged-one has merged into its bolt, so it is not amended: a defect in it is a fix, and new work is a new unit" \
  crew unit amend merged-one "Something else."
CREW_AGENT=wldn-planner expect_fail "the planner changes the plan through a proposal: crew plan propose, not crew unit amend" \
  crew unit amend cfn-lint-treefmt "Something else."
CREW_AGENT=swb-1-conductor expect_fail "swb-1-conductor does not write the plan with crew unit amend: tell wldn-planner" \
  crew unit amend cfn-lint-treefmt "Something else."
eq "$(tip)" "$before"
has "$(field unit.amend Refused unit/merged-one)" "has merged into its bolt"
ok "a merged unit is refused, and so is the planner's direct amendment and a conductor's"

# The planner proposes an amendment to a unit in code in the bolt swb-1 holds.
export CREW_AGENT=wldn-planner
: > "$CREW_TEST_LOG"; before=$(tip)
expect_ok crew plan propose "$(proposal 'Case: cfn-lint is already in treefmt; what the unit should do is fail the check on a warning.' \
  'Do: unit amend cfn-lint-treefmt "cfn-lint in treefmt fails the check on a warning as well as an error"')"
has "$out" "proposal 1 is open, waiting on swb-1-conductor, then the user"
eq "$(plan -t Unit -e "Unit = 'cfn-lint-treefmt'" -P Intent,Amended)" "Unit cfn-lint-treefmt."
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v '^runs/')" "proposals.rec"
has "$(prompts swb-1)" "Proposal 1 would change your bolt: unit amend cfn-lint-treefmt"
expect_ok crew plan proposed 1
has "$out" "1. **Amend unit \`cfn-lint-treefmt\`** in bolt \`tenant-environments\` (swb-1), now in code"
has "$out" "   Intent, as it stands: Unit cfn-lint-treefmt."
has "$out" "   Intent, as proposed:  cfn-lint in treefmt fails the check on a warning as well as an error"
has "$out" "   On approval: swb-1's conductor runs construct again, and the unit returns to your review."
has "$out" "- swb-1-conductor: \`crew plan agree 1 --label wldn\`"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "plan(proposal 1): propose: amend cfn-lint-treefmt (wldn-planner)"
ok "an amendment is proposed with the intent unchanged, its conductor is told, and its page shows both intents, the stage and what follows"

expect_fail "proposal 1 waits on the agreement of swb-1-conductor" crew plan approve 1
HOST=$box CREW_AGENT=swb-1-conductor expect_ok crew plan agree 1
expect_ok crew plan proposed 1; has "$out" "- agreed: swb-1"; lacks "$out" "- swb-1-conductor:"
: > "$CREW_TEST_LOG"
expect_ok crew plan approve 1
eq "$(plan -t Unit -e "Unit = 'cfn-lint-treefmt'" -P Intent)" "cfn-lint in treefmt fails the check on a warning as well as an error"
eq "$(plan -t Unit -e "Unit = 'cfn-lint-treefmt'" -P Amended)" "proposal/1"
eq "$(stage cfn-lint-treefmt)" "amended"
eq "$(prompts swb-1 | wc -l | tr -d ' ')" "1"
has "$(prompts swb-1)" "intent was amended by proposal 1. Run construct again (crew unit run cfn-lint-treefmt construct); it returns to the user"
eq "$(field unit.amend From unit/cfn-lint-treefmt)" "proposal/1"
has "$(field unit.amend Commit unit/cfn-lint-treefmt)" "WilldanGroup/crew-state@$(tip)"
expect_ok crew plan proposed 1; has "$out" "Closed"
ok "approval waits for the conductor, then replaces the intent, marks the unit amended by the proposal and tells its conductor"

# The conductor runs construct again, and the amended intent reaches the fresh construct agent.
export CREW_AGENT=swb-1-conductor
expect_ok crew unit run cfn-lint-treefmt construct
p1=$(herdr_state $box wldn-1 '.agents | to_entries[] | select(.value.name == "swb-1-unit-1") | .key')
has "$(grep "^$box wldn-1 agent prompt $p1 " "$CREW_TEST_LOG" | tail -1)" "/opsx:propose cfn-lint-treefmt cfn-lint in treefmt fails the check on a warning as well as an error This unit"
has "$(grep "^$box wldn-1 agent prompt $p1 " "$CREW_TEST_LOG" | tail -1)" "s intent was amended; revise the existing change to it."
eq "$(stage cfn-lint-treefmt)" "construct"
trace=$(crew trace unit/cfn-lint-treefmt)
eq "$(grep -v 'refused:' <<<"$trace" | awk '{print $3}' | tr '\n' ' ')" "unit.add plan.propose plan.agree plan.approve unit.amend stage.start "
ok "the conductor runs construct again, the fresh agent is told the intent was amended, and the trace shows the way there"
