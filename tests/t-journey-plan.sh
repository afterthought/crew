# The plan changed through proposals, and the writes that race on its branch, through the crew command on the stubs
# (tests.11, record 0022): the planner proposes, a held bolt's conductor is told and agrees, the user approves, leaves
# units out on the card and answers it, a proposal is dropped and replaced, a unit from a signal is routed, an
# approval's rebases are undone when one conflicts, amendments start their constructs, and two writes racing on one
# branch, or on two branches of one repository, both land. Whether a proposal holds, whom it waits on, what its page and
# card say and who may write the plan are logic cases (tests/py/test_proposals.py, test_proposal_life.py,
# test_proposal_card.py, test_plan_roles.py); each step here checks a command's wiring once.
# Reads: plugin/hooks/ plugin/lib/picture.py plugin/lib/font.py
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
ws=$(remote WilldanGroup/crew-state)
k=$(kit chuck-herdr-alpha willdan switchboard-kit); kd=$(dirname "$k")
crew state init wldn >/dev/null
export CREW_LABEL=wldn
box=chuck-herdr-alpha
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
props() { git --git-dir "$ws" show wldn/main:proposals.rec > "$T/p.rec"; recsel -C "$@" "$T/p.rec"; }
tip() { git --git-dir "$ws" rev-parse wldn/main; }
last() { props -t Proposal -P Proposal | tail -1; }
prompts() { grep "^$box wldn-1 agent prompt $1-conductor " "$CREW_TEST_LOG" || true; }
told_planner() { grep -F "agent prompt wldn-planner '[crew] $1" "$CREW_TEST_LOG" || true; }
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
proposal() { printf '%s\n' "$@" > "$T/proposal.rec"; echo "$T/proposal.rec"; }
record_of() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null'; }
# field <host> <act> <field> <object>: a field of that host's last entry of the act naming the object
field() {
  as "$1" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and sys.argv[3] in e["On"]]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$2" "$4" | jq -r --arg f "$3" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'
}
# The user's plan, written by hand in one commit: a bolt swb-1 will hold, a planned one, a bolt to clear units from,
# and a queued unit.
w=$T/hand; git clone -q -b wldn/main "$ws" "$w"
python3 - "$CREW/plugin/lib" "$w/plan.rec" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import plan
f = sys.argv[2]; p = plan.Plan(open(f).read())
for b, goal in (("tenant-environments", "A tenant holds environments of its own."), ("console-pages", "The console lists them."),
                ("clears", "Units can be left out.")):
    p.insert(plan.Rec("Bolt", [("Bolt", b), ("Repo", "switchboard-kit"), ("Goal", goal)]))
for u, b, intent in (("the-deploy-names-its-host-tenant", "tenant-environments", "The deploy writes the host tenant."),
                     ("the-deploy-is-logged", "tenant-environments", "The deploy writes a log."), ("in-verify", "tenant-environments", "Unit in-verify."),
                     ("a-drop", "clears", "Dropped."), ("queued-one", None, "Later work.")):
    p.insert(plan.Rec("Unit", [("Unit", u), ("Repo", "switchboard-kit")] + ([("Bolt", b)] if b else []) + [("Intent", intent)]))
open(f, "w").write(p.text())
PY
commit_all "$w" "plan: by hand"; git -C "$w" push -q origin wldn/main
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
for u in the-deploy-names-its-host-tenant in-verify; do p=$(place "$k" tenant-environments $u); done
change "$kd/places/the-deploy-names-its-host-tenant" the-deploy-names-its-host-tenant 1 3; commit_all "$kd/places/the-deploy-names-its-host-tenant" "docs: the change"
change "$kd/places/in-verify" in-verify 3 3; commit_all "$kd/places/in-verify" "docs(in-verify): the change"
c=$(as $box herdr --session wldn-1 workspace create --cwd / --label swb-1 | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-1 stub agent "$c" swb-1-conductor
p=$(as $box herdr --session wldn-3 workspace create --cwd / --label wldn | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-3 stub agent "$p" wldn-planner

export CREW_AGENT=wldn-planner
before=$(tip)
expect_ok crew plan propose "$(proposal \
  'Case: Two findings about the deploy belong together. They start a bolt of their own,' \
  '+ and the queued work joins it.' \
  'Do: bolt new deploy-checks "The deploy is checked before it runs." --repo switchboard-kit' \
  'Do: unit add a-plan-only-deploy-is-checked "A plan-only deploy is checked." --bolt deploy-checks' \
  'Do: unit move queued-one deploy-checks')"
has "$out" "proposal 1 is open, waiting on the user"
eq "$(tail -1 <<<"$out")" "Post your Pending You card for proposal/1."
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v "^runs/")" "proposals.rec"
eq "$(props -t Proposal -P Proposal,State,By)" $'1\nopen\nwldn-planner'
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "plan(proposal 1): propose: new bolt deploy-checks, add a-plan-only-deploy-is-checked to deploy-checks, move queued-one to deploy-checks (wldn-planner)"
expect_ok crew plan proposed 1
has "$out" "# Proposal 1 — open, by wldn-planner"
has "$out" 'Runs: `crew unit move queued-one deploy-checks`'
expect_ok crew plan proposed
has "$out" "wldn 1"; has "$out" "waiting on the user"
ok "a proposal is written open, the plan unchanged, the planner shown to post its card, and it reads as the user would read it"

: > "$CREW_TEST_LOG"
expect_ok crew plan propose "$(proposal 'Case: The tenant bolt cannot land until its zone exists.' \
  'Do: unit add zone-first "The tenant'"'"'s zone exists." --bolt tenant-environments --unblocks tenant-environments')"
has "$out" "proposal 2 is open, waiting on swb-1-conductor, then the user"
has "$(prompts swb-1)" "Proposal 2 would change your bolt: unit add zone-first"
has "$(prompts swb-1)" "crew plan agree 2 --label wldn"
expect_fail "proposal 2 waits on the agreement of swb-1-conductor" crew plan approve 2
: > "$CREW_TEST_LOG"
HOST=$box CREW_AGENT=swb-1-conductor expect_ok crew plan agree 2
eq "$(props -t Proposal -e "Proposal = 2" -P Agreed)" "swb-1"
has "$(told_planner "swb-1 agrees to proposal 2.")" "Update your Pending You card for proposal/2: it no longer waits on swb-1-conductor."
before=$(tip); : > "$CREW_TEST_LOG"
expect_ok crew plan approve 2
eq "$(tail -1 <<<"$out")" "Close your Pending You card for proposal/2, if one is open, with what was done."
grep -q "agent prompt wldn-planner" "$CREW_TEST_LOG" && fail "the planner was told of its own approval"
eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -P Unit | head -1)" "zone-first"
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v '^runs/')" $'plan.rec\nproposals.rec'
eq "$(git --git-dir "$ws" rev-list --count "$before"..wldn/main)" "1"
ok "a proposal touching a held bolt tells its conductor, waits for its recorded agreement, and is applied in one commit"

before=$(tip); : > "$CREW_TEST_LOG"
CREW_AGENT= expect_ok crew plan approve 1
has "$(told_planner "Proposal 1 was approved by $me@mac-studio.")" "Close your Pending You card for proposal/1, if one is open, with what was done."
eq "$(git --git-dir "$ws" rev-list --count "$before"..wldn/main)" "1"
eq "$(plan -t Unit -e "Bolt = 'deploy-checks'" -P Unit)" $'a-plan-only-deploy-is-checked\nqueued-one'
eq "$(field mac-studio unit.add From unit/zone-first)" "proposal/2"
has "$(field mac-studio unit.add Commit unit/zone-first)" "WilldanGroup/crew-state@"
trace=$(crew trace unit/zone-first)
eq "$(grep -v 'refused:' <<<"$trace" | awk '{print $3}' | head -4 | tr '\n' ' ')" "plan.propose plan.agree plan.approve unit.add "
has "$trace" "refused: proposal 2 waits on the agreement of swb-1-conductor"
ok "the user's approval tells the planner to close its card; each step is recorded, and a unit's trace shows the proposal, the agreement and the approval"

: > "$CREW_TEST_LOG"
crew plan propose "$(proposal 'Case: The console starts with a page.' 'Do: unit add a-page "The console has a page." --bolt console-pages')" >/dev/null
CREW_AGENT= expect_ok crew plan drop 3 "the console waits"
eq "$(props -t Proposal -e "Proposal = 3" -P State,Reason)" $'dropped\nthe console waits'
has "$(told_planner "Proposal 3 was dropped by $me@mac-studio: the console waits.")" "Close your Pending You card for proposal/3"
crew plan propose "$(proposal 'Case: The zone goes later.' 'Do: unit order zone-first --last')" >/dev/null
expect_ok crew plan propose --replaces 4 "$(proposal 'Case: Order the queue instead.' 'Do: unit order a-drop --first')"
has "$out" "proposal 4 is dropped, replaced by proposal 5"
eq "$(props -t Proposal -e "Proposal = 4" -P State,Reason)" $'dropped\nreplaced by proposal 5'
ok "a proposal is dropped with a reason, the planner told to close its card, or replaced by another"

# A refused proposal is recorded naming its command, never the words typed in it.
expect_fail '`unit add y "Typed ZQXA." --bolt nowhere`: no bolt nowhere in wldn/main' \
  crew plan propose "$(proposal 'Case: x' 'Do: unit add y "Typed ZQXA." --bolt nowhere')"
has "$(as mac-studio bash -c 'recsel -t Entry -e "Act = '"'plan.propose'"'" -P Refused "$HOME"/.local/state/crew/wldn/runs/*/*.rec' | grep . | tail -1)" \
  '`unit add y`: no bolt nowhere in wldn/main'
[[ $(record_of mac-studio) != *ZQXA* ]] || fail "a refused proposal's entry holds typed text"
n=$(grep -c "^Refused:" <<<"$(record_of mac-studio)")
expect_fail "the planner changes the plan through a proposal: crew plan propose, not crew unit add" crew unit add d "Unit d." --repo switchboard-kit
eq "$(grep -c "^Refused:" <<<"$(record_of mac-studio)")" "$((n + 1))"
ok "a refused proposal and a refused direct write each leave a Refused entry holding nothing typed"

# The user leaves a new unit out, approving directly and through the card's answers.
crew plan propose "$(proposal 'Case: Two units replace one.' 'Do: unit drop a-drop "Replaced."' \
  'Do: unit add b-keep "Kept." --bolt clears' 'Do: unit add c-clear "Cleared." --bolt clears' 'Do: unit order c-clear --first')" >/dev/null
n=$(last); before=$(tip)
expect_ok crew plan approve "$n" --clear c-clear
has "$out" "proposal $n is approved and applied, without c-clear"
eq "$(git --git-dir "$ws" rev-list --count "$before"..wldn/main)" "1"
eq "$(plan -t Unit -e "Bolt = 'clears'" -P Unit)" "b-keep"
eq "$(props -t Proposal -e "Proposal = $n" -P Cleared)" "c-clear"
has "$(git --git-dir "$ws" log -1 --format=%b wldn/main)" "Left out: c-clear"
crew plan propose "$(proposal 'Case: Two more units.' 'Do: unit add f-1 "One." --bolt clears' 'Do: unit add f-2 "Two." --bolt clears')" >/dev/null
n=$(last)
expect_ok crew plan card "$n"
eq "$(jq -r .card.title <<<"$out")" "Approve the change to clears: 2 new?"
pic=$(jq -r .picture <<<"$out")
eq "$pic" "$(home_of mac-studio)/.local/state/crew/cards/wldn/proposal/$n/proposal-$n.png"
[[ -s $pic ]] || fail "the card's picture was not written"
before=$(tip)
expect_ok crew plan answer "$n" plan approve
eq "$out" "proposal $n waits on units-1: nothing is applied"
eq "$(tip)" "$before"
expect_ok crew plan answer "$n" units-1 f-1 --note "split f-1 in two later"
has "$out" "proposal $n is approved and applied, without f-2"
eq "$(tail -1 <<<"$out")" "The user's note beside the approval of proposal $n: \"split f-1 in two later\". Propose what it asks as a new proposal."
eq "$(plan -t Unit -e "Bolt = 'clears'" -P Unit | tail -1)" "f-1"
[[ ! -e $(home_of mac-studio)/.local/state/crew/cards/wldn/proposal/$n/answers.json ]] || fail "the answers stayed after the approval"
ok "an approval leaves the units the user cleared out, in one commit; the card is drawn with its picture, and its answers wait for every question, then apply it"

# A unit from a signal: the route move is in the approval's commit.
sig=2026-10-06-standup/01-plans-are-checked
w=$T/wbc; clone WilldanGroup/willdan-blueprints "$w"; mkdir -p "$w/signals/${sig%/*}"
printf -- '---\nsignal: %s\nkind: ask\nwho: user\n---\n\nThe user wants plans checked before they run.\n\n> "check the plan first"\n' "$sig" > "$w/signals/$sig.md"
commit_all "$w" "signals: a capture"; git -C "$w" push -q origin main
crew plan propose "$(proposal 'Case: The user asked for it.' "Do: unit add plans-are-checked \"A plan is checked before it runs.\" --repo switchboard-kit --signal $sig")" >/dev/null
n=$(last); before=$(tip)
expect_ok crew plan approve "$n"
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v '^runs/')" $'moves.rec\nplan.rec\nproposals.rec'
git --git-dir "$ws" show wldn/main:moves.rec > "$T/moves.rec"
eq "$(recsel -t Move -e "Signal = '$sig'" -P Move,Target "$T/moves.rec")" $'route\nunit/plans-are-checked'
ok "a unit from a signal is added with its route move, in the approval's commit"

# Two units with worktrees move to a bolt swb-2 holds; the second's rebase conflicts, and the first's is undone.
CREW_AGENT= crew bolt give swb-2 console-pages >/dev/null 2>&1
pz=$(place "$k" tenant-environments zone-first); echo z > "$pz/z-file"; commit_all "$pz" "feat(zone-first): z"
pt=$kd/places/the-deploy-names-its-host-tenant; echo t > "$pt/same-file"; commit_all "$pt" "feat: same file"
echo console > "$kd/bolts/console-pages/same-file"; commit_all "$kd/bolts/console-pages" "feat: same file, otherwise"
ztip=$(git -C "$k" rev-parse unit/zone-first); ttip=$(git -C "$k" rev-parse unit/the-deploy-names-its-host-tenant)
crew plan propose "$(proposal 'Case: Both belong with the console.' 'Do: unit move zone-first console-pages' \
  'Do: unit move the-deploy-names-its-host-tenant console-pages')" >/dev/null
n=$(last)
CREW_AGENT= crew plan agree "$n" >/dev/null
before=$(tip)
expect_fail "rebasing the-deploy-names-its-host-tenant onto bolt/console-pages conflicts" crew plan approve "$n"
eq "$(tip)" "$before"; eq "$(props -t Proposal -e "Proposal = $n" -P State)" "open"
eq "$(git -C "$k" rev-parse unit/zone-first)" "$ztip"; eq "$(git -C "$k" rev-parse unit/the-deploy-names-its-host-tenant)" "$ttip"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/zone-first)" "bolt/tenant-environments"
CREW_AGENT= crew plan drop "$n" "they stay" >/dev/null
ok "an approval's rebases are prepared before its push, and a conflict undoes them and writes nothing"

# The planner proposes amending a unit in code and one in verify; the approval runs each one's construct again.
: > "$CREW_TEST_LOG"
crew plan propose "$(proposal 'Case: The deploy should fail on a warning as well.' \
  'Do: unit amend the-deploy-names-its-host-tenant "The deploy writes the host tenant, and fails on a warning."' \
  'Do: unit amend in-verify "in-verify reads its intent from the plan"')" >/dev/null
n=$(last)
has "$(prompts swb-1)" "Proposal $n would change your bolt: unit amend the-deploy-names-its-host-tenant"
expect_ok crew plan proposed "$n"
has "$out" "   Intent, as it stands: The deploy writes the host tenant."
has "$out" "**Amend unit \`in-verify\`** in bolt \`tenant-environments\` (swb-1), now in verify"
HOST=$box CREW_AGENT=swb-1-conductor crew plan agree "$n" >/dev/null
: > "$CREW_TEST_LOG"
expect_ok crew plan approve "$n"
has "$out" "swb-1-unit-1 has the-deploy-names-its-host-tenant: construct, in $kd/places/the-deploy-names-its-host-tenant"
has "$out" "swb-1-unit-2 has in-verify: construct, in $kd/places/in-verify"
eq "$(plan -t Unit -e "Unit = 'in-verify'" -P Amended)" "$(git -C "$k" rev-parse unit/in-verify)"
has "$(prompt_to swb-1-unit-2)" "s intent was amended by proposal $n; revise the existing change to it. The planner"
eq "$(field $box stage.start By stage/in-verify/construct)" "wldn-planner"
has "$(prompts swb-1)" "intent was amended by proposal $n, and construct runs again on it in swb-1-unit-2: wait for it (crew unit wait in-verify)"
has "$(prompts swb-1)" "wldn-planner ran construct on unit in-verify. Close your Pending You card for verify/in-verify, if one is open, with what was done."
ok "an approved amendment marks each unit and runs its construct again in the approver's name, with the planner's case, and the conductor is told to wait and which card it ended"

# With its team taken down, an amendment stands and every stage is refused before anything is written.
unset CREW_AGENT
echo "Written again." >> "$kd/places/in-verify/openspec/changes/in-verify/design.md"; commit_all "$kd/places/in-verify" "docs(in-verify): written again"
expect_ok crew down swb-1 --force
[[ -z $(herdr_state $box wldn-1 ".agents[\"$c\"] // empty") ]] || as $box herdr --session wldn-1 agent prompt "$c" /exit >/dev/null
expect_ok crew unit amend in-verify "in-verify reads its intent from the plan, once."
has "$out" "construct did not start on unit in-verify: swb-1 is down; crew up swb-1 brings it back"
has "$out" "swb-1-conductor is not up: unit in-verify waits, amended, for construct to be run again"
eq "$(plan -t Unit -e "Unit = 'in-verify'" -P Intent,Amended)" $'in-verify reads its intent from the plan, once.\nintent'
before=$(tip); : > "$CREW_TEST_LOG"
expect_fail "swb-1 is down; crew up swb-1 brings it back" crew unit run the-deploy-is-logged code
eq "$(tip)" "$before"
grep -q "agent prompt" "$CREW_TEST_LOG" && fail "a pane was sent something while swb-1 is down"
has "$(field $box stage.start Refused stage/the-deploy-is-logged/code)" "swb-1 is down"
ok "an amendment whose team is down stands, the unit marked; a stage on a team taken down is refused before anything is written"

# Two writes race on the branch: the user on mac-studio moves a unit while swb-1's conductor on the box narrows another.
before=$(tip)
race WilldanGroup/crew-state chuck-herdr-alpha swb-1-conductor unit split the-deploy-is-logged "The deploy writes a log line." \
  --into the-deploy-is-searchable "The log can be searched."
expect_ok crew unit move a-plan-only-deploy-is-checked console-pages
[[ ! -f $T/race ]] || fail "the competing write never ran"
eq "$(git --git-dir "$ws" log --format='%s' "$before"..wldn/main | grep -v '^runs' | head -2)" \
  "plan(console-pages): move a-plan-only-deploy-is-checked from deploy-checks ($me@mac-studio)"$'\n'"plan(tenant-environments): split the-deploy-is-logged into the-deploy-is-searchable (swb-1-conductor)"
eq "$(git --git-dir "$ws" rev-list --merges wldn/main | wc -l | tr -d ' ')" "0"
race WilldanGroup/crew-state chuck-herdr-alpha "" unit drop b-keep "the portal does it"
expect_fail "no unit b-keep in wldn/main of WilldanGroup/crew-state" crew unit move b-keep console-pages
has "$out" "$(git --git-dir "$ws" log -1 --format='%h %s' wldn/main) removed it"
eq "$(git -C "$(home_of mac-studio)/.cache/crew/git/WilldanGroup/crew-state.git" rev-parse --is-bare-repository)" "true"
ok "two racing writes both land, one after the other, never merged; a write whose unit was dropped meanwhile is refused, naming that commit"

# madswan and swancloud share afterthought/crew-state, each on its own branch: neither is replayed for the other.
blueprints afterthought/blueprints >/dev/null; blueprints agentplot/blueprints >/dev/null; as=$(remote afterthought/crew-state)
crew state init madswan >/dev/null; HOST=$box crew state init swancloud >/dev/null
greeting=2026-10-06-standup/01-a-greeting
w=$T/abs; clone afterthought/blueprints "$w"; mkdir -p "$w/signals/${greeting%/*}"; printf -- '---\nsignal: %s\n---\n' "$greeting" > "$w/signals/$greeting.md"
commit_all "$w" "signals: a capture"; git -C "$w" push -q origin main
printf '#!/usr/bin/env bash\nwhile read -r old new ref; do echo "$ref" >> "$CREW_TEST_ROOT/pushes"; done\n' > "$as/hooks/post-receive"
chmod +x "$as/hooks/post-receive"; : > "$T/pushes"
race afterthought/crew-state chuck-herdr-alpha swancloud-design signal move "$greeting" drop --reason "a greeting" --label swancloud
expect_ok crew bolt new flywheel-loop "The loop runs." --repo flywheel-next --label madswan
[[ ! -f $T/race ]] || fail "swancloud's write never ran"
eq "$(sort "$T/pushes" | uniq -c | awk '{print $1, $2}')" $'1 refs/heads/madswan/main\n1 refs/heads/swancloud/main'
eq "$(git -C "$(home_of mac-studio)/.cache/crew/git/afterthought/crew-state.git" for-each-ref --format='%(refname)' refs/crew/)" "refs/crew/madswan/main"
ok "two flywheels in one repository write at the same moment, each pushing once, neither fetching the other's branch"
