# The plan changed through proposals, and the writes that race on its branch, through the crew command on the stubs
# (tests.11, record 0022), every team's work running in Flume places (Decision 1 of the-team-machinery-leaves): a give
# fetches the bolt's branch sluice made and launches its units; the planner proposes and crew raises its card, one
# touching a held bolt waits for its recorded agreement, the user approves, leaves units out on the card and answers
# it, each closing the card, a proposal is dropped and replaced, its card withdrawn or changed in place, one resting on
# a record its kit's main does not hold accepted is refused, a unit from a signal is routed, a move of launched work is
# refused, an amendment of a launched unit, approved or the user's own, retries its construct with its words, and two
# writes racing on one branch, or on two branches of one repository, both land. Whether a proposal holds, whom it
# waits on, what its page and card say, who may write the plan and what a write asks of the runner are logic cases
# (tests/py/test_proposals.py, test_proposal_life.py, test_proposal_card.py, test_plan_roles.py, test_cross.py); each
# step here checks a command's wiring once.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
world
blueprints WilldanGroup/willdan-blueprints >/dev/null
ws=$(remote WilldanGroup/crew-state)
k=$(kit chuck-herdr-alpha willdan switchboard-kit)
crew state init wldn >/dev/null
flume_world
export CREW_LABEL=wldn
box=chuck-herdr-alpha
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
props() { git --git-dir "$ws" show wldn/main:proposals.rec > "$T/p.rec"; recsel -C "$@" "$T/p.rec"; }
# requests <recsel args...>: requests.rec's records at wldn/main as recsel selects them
requests() { git --git-dir "$ws" show wldn/main:requests.rec | recsel -t Request "$@"; }
row() { grep . | paste -sd ' ' -; }
tip() { act_tip; }
last() { props -t Proposal -P Proposal | tail -1; }
told_planner() { grep -F "agent prompt wldn-planner '[crew] $1" "$CREW_TEST_LOG" || true; }
proposal() { printf '%s\n' "$@" > "$T/proposal.rec"; echo "$T/proposal.rec"; }
record_of() { as "$1" bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec 2>/dev/null'; }
# field <host> <act> <field> <object>: a field of that host's last entry of the act naming the object
field() {
  as "$1" python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and sys.argv[3] in e["On"]]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$2" "$4" | jq -r --arg f "$3" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'
}
# live <place> <stage>: Flume's status of a live place running that stage, as runner_writes takes it
live() { printf '{"status":{"places":[{"place":"%s","phase":"live","current":"%s","stages":[{"name":"%s","state":"running"}]}]}}' "$1" "$2" "$2"; }
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
commit_all "$w" "plan: by hand"; push_state "$w"
# sluice makes the bolt's branch on GitHub pushing as its app, which moves no tracking ref; the give fetches it.
touch "$T/sluice-leaves-copy"
expect_ok crew bolt give swb-1 tenant-environments
rm "$T/sluice-leaves-copy"
made=$(git --git-dir "$(remote WilldanGroup/switchboard-kit)" rev-parse bolt/tenant-environments)
eq "$(git -C "$k" rev-parse refs/remotes/origin/bolt/tenant-environments)" "$made"
has "$out" "the runner on $box launches unit/the-deploy-names-its-host-tenant (request 1), unit/the-deploy-is-logged (request 2), unit/in-verify (request 3) in stream wldn"
eq "$(plan -t Bolt -e "Bolt = 'tenant-environments'" -P Team,Path | row)" "swb-1 flume"
ok "a give fetches the bolt's branch sluice made on GitHub, marks the bolt Path: flume and launches each of its units"
# The runner on the box launched two of them: Flume's status of their places, carried on its branch, has one in code
# and the other in verify.
p1=/flume/places/change--the-deploy-names-its-host-tenant p3=/flume/places/change--in-verify
runner_writes $box 1 "$p1" "$(live "$p1" code)" 3 "$p3" "$(live "$p3" verify)"
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
has "$out" "card proposal/1: req_stub-1 https://www.pendingyou.com/app/r/req_stub-1"
eq "$(tail -1 <<<"$out")" "call get_request (requestId req_stub-1, name wldn-planner)"
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v "^runs/")" "proposals.rec"
eq "$(props -t Proposal -P Proposal,State,By)" $'1\nopen\nwldn-planner'
eq "$(git --git-dir "$ws" log -1 --format=%s "$(act_tip)")" "plan(proposal 1): propose: new bolt deploy-checks, add a-plan-only-deploy-is-checked to deploy-checks, move queued-one to deploy-checks (wldn-planner)"
expect_ok crew plan proposed 1
has "$out" "# Proposal 1 — open, by wldn-planner"
has "$out" 'Runs: `crew unit move queued-one deploy-checks`'
expect_ok crew plan proposed
has "$out" "wldn 1"; has "$out" "waiting on the user"
ok "a proposal is written open, the plan unchanged, crew raises its card in the planner's name with the line that adopts it, and it reads as the user would read it"

# The planner on its own host, where its card is posted and changed, proposes work for the bolt swb-1 holds.
: > "$CREW_TEST_LOG"
HOST=$box expect_ok crew plan propose "$(proposal 'Case: The tenant bolt cannot land until its zone exists.' \
  'Do: unit add zone-first "The tenant'"'"'s zone exists." --bolt tenant-environments --unblocks tenant-environments')"
has "$out" "proposal 2 is open, waiting on swb-1-conductor, then the user"
expect_fail "proposal 2 waits on the agreement of swb-1-conductor" crew plan approve 2
: > "$CREW_TEST_LOG"
HOST=$box CREW_AGENT= expect_ok crew plan agree 2
eq "$(props -t Proposal -e "Proposal = 2" -P Agreed)" "swb-1"
[[ -n $(told_planner "swb-1 agrees to proposal 2.") ]] || fail "the planner was not told of the agreement"
has "$out" "card proposal/2: req_stub-1 changed, now version 2"
before=$(tip); : > "$CREW_TEST_LOG"
HOST=$box expect_ok crew plan approve 2
eq "$(tail -1 <<<"$out")" "card proposal/2: req_stub-1 withdrawn"
grep -q "agent prompt wldn-planner" "$CREW_TEST_LOG" && fail "the planner was told of its own approval"
eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -P Unit | head -1)" "zone-first"
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v '^runs/')" $'plan.rec\nproposals.rec\nrequests.rec'
eq "$(acts_since "$before")" "1"
eq "$(requests -e "Work = 'unit/zone-first'" -P Act,Base,Stream | row)" "launch bolt/tenant-environments wldn"
ok "a proposal touching a held bolt waits for its recorded agreement, changing its card, and is applied in one commit, which launches the unit it adds"

before=$(tip); : > "$CREW_TEST_LOG"
CREW_AGENT= expect_ok crew plan approve 1
has "$(told_planner "Proposal 1 was approved by $me@mac-studio.")" "Applied: added a-plan-only-deploy-is-checked and queued-one; 1 other change."
has "$out" "card proposal/1: req_stub-1 withdrawn"
eq "$(acts_since "$before")" "1"
eq "$(plan -t Unit -e "Bolt = 'deploy-checks'" -P Unit)" $'a-plan-only-deploy-is-checked\nqueued-one'
eq "$(field $box unit.add From unit/zone-first)" "proposal/2"
has "$(field $box unit.add Commit unit/zone-first)" "WilldanGroup/crew-state@"
trace=$(crew trace unit/zone-first)
eq "$(grep -v 'refused:' <<<"$trace" | awk '{print $3}' | head -7 | tr '\n' ' ')" "plan.propose card.post plan.agree card.update plan.approve unit.add card.close "
has "$trace" "refused: proposal 2 waits on the agreement of swb-1-conductor"
ok "the user's approval tells the planner what was applied and closes its card; each step is recorded, and a unit's trace shows the proposal, the agreement and the approval, each with its card's act"

: > "$CREW_TEST_LOG"
crew plan propose "$(proposal 'Case: The console starts with a page.' 'Do: unit add a-page "The console has a page." --bolt console-pages')" >/dev/null
CREW_AGENT= expect_ok crew plan drop 3 "the console waits"
eq "$(props -t Proposal -e "Proposal = 3" -P State,Reason)" $'dropped\nthe console waits'
[[ -n $(told_planner "Proposal 3 was dropped by $me@mac-studio: the console waits.") ]] || fail "the planner was not told of the drop"
has "$out" "card proposal/3: req_stub-2 withdrawn"
crew plan propose "$(proposal 'Case: The zone goes later.' 'Do: unit order zone-first --last')" >/dev/null
expect_ok crew plan propose --replaces 4 "$(proposal 'Case: Order the queue instead.' 'Do: unit order a-drop --first')"
has "$out" "proposal 4 is dropped, replaced by proposal 5"
has "$out" "card proposal/4: req_stub-3 changed, now version 2"
eq "$(props -t Proposal -e "Proposal = 4" -P State,Reason)" $'dropped\nreplaced by proposal 5'
ok "a proposal is dropped with a reason, the planner told and its card withdrawn, or replaced by another, its card changed in place"

# A refused proposal is recorded naming its command, never the words typed in it. Each day's file is read on its own,
# as crew reads them: every one declares Entry, which one recsel over two days' files refuses as a duplicated set.
expect_fail '`unit add y "Typed ZQXA." --bolt nowhere`: no bolt nowhere in wldn/main' \
  crew plan propose "$(proposal 'Case: x' 'Do: unit add y "Typed ZQXA." --bolt nowhere')"
has "$(as mac-studio bash -c 'for f in "$HOME"/.local/state/crew/wldn/runs/*/*.rec; do recsel -t Entry -e "Act = '"'plan.propose'"'" -P Refused "$f"; done' | grep . | tail -1)" \
  '`unit add y`: no bolt nowhere in wldn/main'
[[ $(record_of mac-studio) != *ZQXA* ]] || fail "a refused proposal's entry holds typed text"
n=$(grep -c "^Refused:" <<<"$(record_of mac-studio)")
expect_fail "the planner changes the plan through a proposal: crew plan propose, not crew unit add" crew unit add d "Unit d." --repo switchboard-kit
eq "$(grep -c "^Refused:" <<<"$(record_of mac-studio)")" "$((n + 1))"
ok "a refused proposal and a refused direct write each leave a Refused entry holding nothing typed"

# A new unit resting on a record the kit's main on GitHub holds proposed is refused, nothing written and no card raised;
# once main holds it accepted, the same proposal is written.
wk=$T/kit-record; clone WilldanGroup/switchboard-kit "$wk"; mkdir -p "$wk/docs/adr"
printf -- '---\nstatus: proposed\n---\n# 1. A record\n\nThe kit decides something.\n' > "$wk/docs/adr/0001-a-record.md"
commit_all "$wk" "docs(adr): propose record 0001"; git -C "$wk" push -q origin HEAD:main
rests=$(proposal 'Case: The record decides it.' \
  'Do: unit add rests-on-a-record "A unit resting on a record." --repo switchboard-kit --source docs/adr/0001-a-record.md')
before=$(tip); : > "$CREW_TEST_LOG"
expect_fail "unit rests-on-a-record names record 0001 of switchboard-kit: switchboard-kit's main holds it proposed" crew plan propose "$rests"
has "$out" "crew refuses the proposal: it rests on records the user has not accepted."
eq "$(tip)" "$before"
lacks "$(calls)" "pendingyou post_request"
rewrite "$wk/docs/adr/0001-a-record.md" 's/^status: proposed$/status: accepted/'
commit_all "$wk" "docs(adr): accept record 0001"; git -C "$wk" push -q origin HEAD:main
expect_ok crew plan propose "$rests"
has "$out" "proposal $(last) is open"
CREW_AGENT= crew plan drop "$(last)" "the record's work waits" >/dev/null
ok "a proposal whose new unit rests on a proposed record is refused naming it, and is written once main holds it accepted"

# The user leaves a new unit out, approving directly and through the card's answers.
crew plan propose "$(proposal 'Case: Two units replace one.' 'Do: unit drop a-drop "Replaced."' \
  'Do: unit add b-keep "Kept." --bolt clears' 'Do: unit add c-clear "Cleared." --bolt clears' 'Do: unit order c-clear --first')" >/dev/null
n=$(last); before=$(tip)
expect_ok crew plan approve "$n" --clear c-clear
has "$out" "proposal $n is approved and applied, without c-clear"
eq "$(acts_since "$before")" "1"
eq "$(plan -t Unit -e "Bolt = 'clears'" -P Unit)" "b-keep"
eq "$(props -t Proposal -e "Proposal = $n" -P Cleared)" "c-clear"
has "$(git --git-dir "$ws" log -1 --format=%b "$(act_tip)")" "Left out: c-clear"
crew plan propose "$(proposal 'Case: Two more units.' 'Do: unit add f-1 "One." --bolt clears' 'Do: unit add f-2 "Two." --bolt clears')" >/dev/null
n=$(last)
expect_ok crew plan answer "$n" rows-1 add:f-1 --note "split f-1 in two later"
has "$out" "proposal $n is approved and applied, without f-2"
eq "$(tail -1 <<<"$out")" "The user's note beside the approval of proposal $n: \"split f-1 in two later\". Propose what it asks as a new proposal."
eq "$(plan -t Unit -e "Bolt = 'clears'" -P Unit | tail -1)" "f-1"
[[ ! -e $(home_of mac-studio)/.local/state/crew/cards/wldn/proposal/$n/answers.json ]] || fail "the answers stayed after the approval"
ok "an approval leaves the units the user cleared out, in one commit, and the card's answers apply it with its boxes as they stand"

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

# A move of launched work out of its bolt is refused at the proposal, naming its place and the drop and add that would
# do it: nothing is written and no card raised.
before=$(tip); : > "$CREW_TEST_LOG"
expect_fail "unit zone-first is launched as Flume place zone-first on bolt/tenant-environments (request 4), whose base and order are fixed at its launch, so it is not moved to console-pages: drop it (crew unit drop zone-first) and add it again as it should be (crew unit add)" \
  crew plan propose "$(proposal 'Case: It belongs with the console.' 'Do: unit move zone-first console-pages')"
eq "$(tip)" "$before"
lacks "$(calls)" "pendingyou post_request"
ok "a proposal moving launched work out of its bolt is refused naming the drop and add, and writes nothing"

# The planner proposes amending a unit in code and one in verify, each launched in a place; the approval appends a
# retry of each one's construct with its amended intent and the planner's case.
crew plan propose "$(proposal 'Case: The deploy should fail on a warning as well.' \
  'Do: unit amend the-deploy-names-its-host-tenant "The deploy writes the host tenant, and fails on a warning."' \
  'Do: unit amend in-verify "in-verify reads its intent from the plan"')" >/dev/null
n=$(last)
expect_ok crew plan proposed "$n"
has "$out" "   Intent, as it stands: The deploy writes the host tenant."
has "$out" "**Amend unit \`in-verify\`** in bolt \`tenant-environments\` (swb-1), now in verify"
CREW_AGENT= crew plan agree "$n" >/dev/null
before=$(tip)
expect_ok crew plan approve "$n"
eq "$(acts_since "$before")" "1"
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v '^runs/')" $'plan.rec\nproposals.rec\nrequests.rec'
eq "$(requests -e "Act = 'retry'" -P Work,Of,Stage | row)" "unit/the-deploy-names-its-host-tenant 1 construct unit/in-verify 3 construct"
eq "$(requests -e "Act = 'retry' && Work = 'unit/in-verify'" -P Words)" \
  "in-verify reads its intent from the plan This unit's intent was amended by proposal $n; revise the existing change to it. The planner's case, as the user approved it: The deploy should fail on a warning as well."
eq "$(plan -t Unit -e "Unit = 'in-verify'" -P Intent)" "in-verify reads its intent from the plan"
eq "$(launches)" ""
ok "an approved amendment of units launched in places appends, in its commit, a retry of each one's construct with the amended intent and the planner's case, starting no agent"

# The user amends a launched unit directly: its construct is retried with the user's words.
unset CREW_AGENT
before=$(tip)
expect_ok crew unit amend in-verify "in-verify reads its intent from the plan, once."
eq "$(acts_since "$before")" "1"
eq "$(plan -t Unit -e "Unit = 'in-verify'" -P Intent)" "in-verify reads its intent from the plan, once."
eq "$(requests -e "Act = 'retry' && Work = 'unit/in-verify'" -P Of,Stage,Words | tail -3 | row)" \
  "3 construct in-verify reads its intent from the plan, once. This unit's intent was amended by the user; revise the existing change to it."
ok "the user's own amendment of a launched unit retries its construct with the user's words"

# Two writes race on the branch: the user on mac-studio moves a unit while the user on the box splits another.
before=$(tip)
race WilldanGroup/crew-state chuck-herdr-alpha "" unit split queued-one "Later work, first." --into queued-rest "Later work, the rest."
expect_ok crew unit move a-plan-only-deploy-is-checked console-pages
[[ ! -f $T/race ]] || fail "the competing write never ran"
eq "$(git --git-dir "$ws" log --format='%s' "$before"..wldn/main | grep -v '^runs' | head -2)" \
  "plan(console-pages): move a-plan-only-deploy-is-checked from deploy-checks ($me@mac-studio)"$'\n'"plan(deploy-checks): split queued-one into queued-rest ($me@chuck-herdr-alpha)"
eq "$(git --git-dir "$ws" rev-list --merges wldn/main | wc -l | tr -d ' ')" "0"
race WilldanGroup/crew-state chuck-herdr-alpha "" unit drop b-keep "the portal does it"
expect_fail "no unit b-keep in wldn/main of WilldanGroup/crew-state" crew unit move b-keep console-pages
has "$out" "$(git --git-dir "$ws" log -1 --format='%h %s' "$(act_tip)") removed it"
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
eq "$(sort "$T/pushes" | uniq -c | awk '{print $1, $2}')" $'2 refs/heads/madswan/main\n2 refs/heads/swancloud/main'
eq "$(git -C "$(home_of mac-studio)/.cache/crew/git/afterthought/crew-state.git" for-each-ref --format='%(refname)' refs/crew/)" "refs/crew/madswan/main"
ok "two flywheels in one repository write at the same moment, each pushing its write and then its entry, neither replayed for the other nor fetching its branch"
