# crew plan propose|proposed|agree|approve|drop: every change the planner makes to the plan is a proposal the user
# approves, with the agreement of the conductor of any bolt in flight it touches; what was approved is exactly what
# is applied, in one commit. Each scenario of the plan-proposals spec.
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
prompts() { grep "^$box wldn-1 agent prompt $1-conductor " "$CREW_TEST_LOG" || true; }
proposal() { printf '%s\n' "$@" > "$T/proposal.rec"; echo "$T/proposal.rec"; }
# The user plans the bolts the proposals are made against: one held by swb-1, one planned, and a queued unit.
crew bolt new tenant-environments "A tenant holds environments of its own." --repo switchboard-kit >/dev/null
crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
crew unit add the-deploy-names-its-host-tenant "The deploy writes the host tenant." --bolt tenant-environments >/dev/null
crew unit add the-deploy-is-logged "The deploy writes a log." --bolt tenant-environments >/dev/null
crew unit add queued-one "Later work." --repo switchboard-kit >/dev/null
crew bolt give swb-1 tenant-environments >/dev/null 2>&1
p=$(as $box herdr --session wldn-1 workspace create --cwd / --label swb-1 | jq -r .result.root_pane.pane_id)
as $box herdr --session wldn-1 stub agent "$p" swb-1-conductor

export CREW_AGENT=wldn-planner
before=$(tip)
expect_ok crew plan propose "$(proposal \
  'Case: Two findings about the deploy belong together. They start a bolt of their own,' \
  '+ and the queued work joins it.' \
  'Do: bolt new deploy-checks "The deploy is checked before it runs." --repo switchboard-kit' \
  'Do: unit add a-plan-only-deploy-is-checked "A plan-only deploy is checked." --bolt deploy-checks' \
  'Do: unit move queued-one deploy-checks')"
has "$out" "proposal 1 is open, waiting on the user"
eq "$(plan -t Bolt -P Bolt)" $'tenant-environments\nconsole-pages'
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v "^runs/")" "proposals.rec"
eq "$(props -t Proposal -P Proposal,State,By)" $'1\nopen\nwldn-planner'
eq "$(props -t Proposal -e "Proposal = 1" -P Do | head -1)" 'bolt new deploy-checks "The deploy is checked before it runs." --repo switchboard-kit'
eq "$(props -t Proposal -e "Proposal = 1" -P Do | wc -l | tr -d ' ')" "3"
recfix --check "$T/p.rec" || fail "proposals.rec fails recfix --check"
eq "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "plan(proposal 1): propose: new bolt deploy-checks, add a-plan-only-deploy-is-checked to deploy-checks, move queued-one to deploy-checks (wldn-planner)"
ok "a proposal is written open with its case and commands in order, and the plan is unchanged"

before=$(tip)
expect_fail "a proposal holds only the plan's commands" crew plan propose "$(proposal 'Case: x' 'Do: bolt give swb-1')"
expect_fail '`unit move nobody console-pages`: no unit nobody in wldn/main' crew plan propose "$(proposal 'Case: x' 'Do: unit move nobody console-pages')"
expect_fail '`unit add x "x" --bolt nowhere`: no bolt nowhere in wldn/main' crew plan propose "$(proposal 'Case: x' 'Do: unit add x "x" --bolt nowhere')"
change "$k" taken; commit_all "$k" "feat: taken"
expect_fail "switchboard-kit's main already has a change named taken" crew plan propose "$(proposal 'Case: x' 'Do: unit add taken "x" --repo switchboard-kit')"
expect_fail '`unit add x "x" --boltt console-pages`' crew plan propose "$(proposal 'Case: x' 'Do: unit add x "x" --boltt console-pages')"
expect_fail "holds 0 records" crew plan propose "$(proposal '')"
eq "$(tip)" "$before"
CREW_AGENT=swb-1-conductor expect_fail "swb-1-conductor does not write proposals: tell wldn-planner" crew plan propose "$(proposal 'Case: x' 'Do: unit order queued-one --first')"
ok "a command a proposal can't hold, or one refused as run directly, refuses the proposal and writes nothing"

expect_ok crew plan proposed
has "$out" "wldn 1"; has "$out" "Two findings about the deploy belong together."; has "$out" "waiting on the user"
expect_ok crew plan proposed 1
has "$out" "# Proposal 1 — open, by wldn-planner"
has "$out" "1. **New bolt \`deploy-checks\`** in switchboard-kit"
has "$out" "Goal: The deploy is checked before it runs."
has "$out" "2. **New unit \`a-plan-only-deploy-is-checked\`** in bolt \`deploy-checks\` (new in this proposal)"
has "$out" "3. **Move unit \`queued-one\`** from the queue to bolt \`deploy-checks\` (new in this proposal)"
has "$out" "Intent: Later work."
has "$out" 'Runs: `crew bolt new deploy-checks "The deploy is checked before it runs." --repo switchboard-kit`'
has "$out" 'Runs: `crew unit move queued-one deploy-checks`'
has "$out" "the user, to approve it or say what to change"
lacks "$out" "crew plan approve"
eq "$(crew plan proposed 1 --json | jq -r '.changes[2].do')" "unit move queued-one deploy-checks"
ok "a proposal reads as the user would read it, from a host that holds no team: each change with its command, and who it waits on in words"

# A unit a held bolt needs before it can land goes into that bolt, marked; anywhere else it is refused.
expect_fail "zone-first unblocks bolt tenant-environments, so it goes into that bolt, ahead of what waits on it, not into the queue" \
  crew plan propose "$(proposal 'Case: x' 'Do: unit add zone-first "The zone exists." --repo switchboard-kit --unblocks tenant-environments')"
expect_fail "not into bolt zones" crew plan propose "$(proposal 'Case: x' 'Do: bolt new zones "Zones." --repo switchboard-kit' \
  'Do: unit add zone-first "The zone exists." --bolt zones --unblocks tenant-environments')"
expect_fail "which no team holds" crew plan propose "$(proposal 'Case: x' 'Do: unit add zone-first "The zone exists." --bolt console-pages --unblocks console-pages')"
: > "$CREW_TEST_LOG"
expect_ok crew plan propose "$(proposal 'Case: The tenant bolt cannot land until its zone exists.' \
  'Do: unit add zone-first "The tenant'"'"'s zone exists." --bolt tenant-environments --unblocks tenant-environments')"
has "$out" "proposal 2 is open, waiting on swb-1-conductor, then the user"
has "$(prompts swb-1)" "Proposal 2 would change your bolt: unit add zone-first"
has "$(prompts swb-1)" "crew plan agree 2 --label wldn"
expect_ok crew plan proposed 2
has "$out" "Unblocks: bolt \`tenant-environments\`"
has "$out" "held by swb-1"
has "$out" "Bolt's goal: A tenant holds environments of its own."
has "$out" "swb-1-conductor, to agree, or tell wldn-planner why not"
lacks "$out" "crew plan agree"
ok "work a held bolt needs to land is proposed into that bolt, marked, and its conductor is told"

expect_fail "proposal 2 waits on the agreement of swb-1-conductor" crew plan approve 2
CREW_AGENT=swb-2-conductor expect_fail "proposal 2 touches no bolt swb-2 holds" crew plan agree 2
CREW_AGENT=wldn-design expect_fail "wldn-design does not agree to proposals" crew plan agree 2
HOST=$box CREW_AGENT=swb-1-conductor expect_ok crew plan agree 2
eq "$(props -t Proposal -e "Proposal = 2" -P Agreed)" "swb-1"
before=$(tip)
HOST=$box CREW_AGENT=swb-1-conductor expect_ok crew plan agree 2
has "$out" "already has the agreement of swb-1"; eq "$(tip)" "$before"
expect_ok crew plan approve 2
eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -P Unit)" $'zone-first\nthe-deploy-names-its-host-tenant\nthe-deploy-is-logged'
eq "$(props -t Proposal -e "Proposal = 2" -P State)" "approved"
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v '^runs/')" $'plan.rec\nproposals.rec'
eq "$(git --git-dir "$ws" rev-list --count "$before"..wldn/main)" "1"
ok "approval waits for the conductor's recorded agreement, then applies the proposal ahead of what waits, in one commit"

before=$(tip)
expect_ok crew plan approve 1
eq "$(git --git-dir "$ws" rev-list --count "$before"..wldn/main)" "1"
has "$(git --git-dir "$ws" log -1 --format=%s wldn/main)" "plan(proposal 1): approve: new bolt deploy-checks"
eq "$(plan -t Unit -e "Bolt = 'deploy-checks'" -P Unit)" $'a-plan-only-deploy-is-checked\nqueued-one'
eq "$(props -t Proposal -e "Proposal = 1" -P State)" "approved"
expect_fail "proposal 1 is approved" crew plan approve 1
ok "a proposal that makes a bolt and adds to it is one commit: no reader sees the bolt without its units"

# The plan moves between propose and approve; a bolt given after the proposal was written.
crew plan propose "$(proposal 'Case: The console starts with a page.' 'Do: unit add a-page "The console has a page." --bolt console-pages')" >/dev/null
CREW_AGENT= crew bolt give swb-2 console-pages >/dev/null 2>&1
expect_fail "proposal 3 waits on the agreement of swb-2-conductor" crew plan approve 3
crew plan propose "$(proposal 'Case: The logged deploy goes later.' 'Do: unit move the-deploy-is-logged deploy-checks')" >/dev/null
HOST=$box CREW_AGENT=swb-1-conductor crew plan agree 4 >/dev/null
CREW_AGENT= crew unit drop the-deploy-is-logged "not needed" >/dev/null 2>&1
expect_fail '`unit move the-deploy-is-logged deploy-checks`: no unit the-deploy-is-logged in wldn/main' crew plan approve 4
eq "$(props -t Proposal -e "Proposal = 4" -P State)" "open"
ok "approval is refused when the plan has moved: a bolt given since needs its conductor, a dropped unit names its commit"

: > "$CREW_TEST_LOG"
CREW_AGENT= expect_ok crew plan drop 3 "the console waits"
eq "$(props -t Proposal -e "Proposal = 3" -P State,Reason)" $'dropped\nthe console waits'
expect_fail "proposal 3 is dropped: the console waits" crew plan approve 3
grep -q "agent prompt wldn-planner '\[crew\] Proposal 3 was dropped by" "$CREW_TEST_LOG" || fail "the planner was not told"
expect_ok crew plan propose --replaces 4 "$(proposal 'Case: Nothing to move after all; order the queue instead.' 'Do: unit order zone-first --first')"
has "$out" "proposal 4 is dropped, replaced by proposal 5"
eq "$(props -t Proposal -e "Proposal = 4" -P State,Reason)" $'dropped\nreplaced by proposal 5'
eq "$(props -t Proposal -e "Proposal = 5" -P Replaces,State)" $'4\nopen'
eq "$(props -t Proposal -e "Proposal = 5" -P Agreed)" ""
expect_ok crew plan proposed
lacks "$out" "wldn 3 "; lacks "$out" "wldn 4 "; has "$out" "wldn 5"
ok "a proposal is dropped with a reason, or replaced; agreements don't carry over"

# A unit from a signal: the route move is in the approval's commit.
sig=2026-10-06-standup/01-plans-are-checked
w=$T/wbc; clone WilldanGroup/willdan-blueprints "$w"; mkdir -p "$w/signals/${sig%/*}"
printf -- '---\nsignal: %s\nkind: ask\nwho: user\n---\n\nThe user wants plans checked before they run.\n\n> "check the plan first"\n' "$sig" > "$w/signals/$sig.md"
commit_all "$w" "signals: a capture"; git -C "$w" push -q origin main
crew plan propose "$(proposal 'Case: The user asked for it.' "Do: unit add plans-are-checked \"A plan is checked before it runs.\" --repo switchboard-kit --signal $sig")" >/dev/null
expect_ok crew plan proposed 6
has "$out" "From: signals/$sig: \"The user wants plans checked before they run.\""
has "$out" 'Excerpt: > "check the plan first"'
before=$(tip)
expect_ok crew plan approve 6
eq "$(git --git-dir "$ws" diff --name-only "$before" wldn/main | grep -v '^runs/')" $'moves.rec\nplan.rec\nproposals.rec'
git --git-dir "$ws" show wldn/main:moves.rec > "$T/moves.rec"
eq "$(recsel -t Move -e "Signal = '$sig'" -P Move,Target "$T/moves.rec")" $'route\nunit/plans-are-checked'
ok "a unit from a signal is added with its route move, in the approval's commit"

# A unit with a worktree moves by a rebase prepared before the push; a later conflict undoes the earlier rebase.
pz=$(place "$k" tenant-environments zone-first); echo z > "$pz/z-file"; commit_all "$pz" "feat(zone-first): z"
pt=$(place "$k" tenant-environments the-deploy-names-its-host-tenant); echo t > "$pt/same-file"; commit_all "$pt" "feat: same file"
echo console > "$kd/bolts/console-pages/same-file"; commit_all "$kd/bolts/console-pages" "feat: same file, otherwise"
ztip=$(git -C "$k" rev-parse unit/zone-first); ttip=$(git -C "$k" rev-parse unit/the-deploy-names-its-host-tenant)
crew plan propose "$(proposal 'Case: Both belong with the console.' 'Do: unit move zone-first console-pages' \
  'Do: unit move the-deploy-names-its-host-tenant console-pages')" >/dev/null
n=$(props -t Proposal -P Proposal | tail -1)
HOST=$box CREW_AGENT=swb-1-conductor crew plan agree "$n" >/dev/null; HOST=$box CREW_AGENT=swb-2-conductor crew plan agree "$n" >/dev/null
before=$(tip)
expect_fail "rebasing the-deploy-names-its-host-tenant onto bolt/console-pages conflicts" crew plan approve "$n"
eq "$(tip)" "$before"; eq "$(props -t Proposal -e "Proposal = $n" -P State)" "open"
eq "$(git -C "$k" rev-parse unit/zone-first)" "$ztip"; eq "$(git -C "$k" rev-parse unit/the-deploy-names-its-host-tenant)" "$ttip"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/zone-first)" "bolt/tenant-environments"
ok "an approval's rebases are prepared before the push, and a conflict undoes them and writes nothing"

# The run record: each step names the proposal, and an approval's changes name it as where they came from.
field() { as mac-studio python3 -c 'import glob, json, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and (len(sys.argv) < 4 or sys.argv[3] in e["On"])]
print(json.dumps(es[-1] if es else {}))' "$CREW/plugin/lib" "$1" "${3:-}" | jq -r --arg f "$2" 'if (.[$f] | type) == "array" then .[$f] | join(" ") else .[$f] // "" end'; }
eq "$(field plan.propose On proposal/1)" "proposal/1 bolt/deploy-checks unit/a-plan-only-deploy-is-checked unit/queued-one"
lacks "$(as mac-studio bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec')" "Two findings about the deploy"
lacks "$(as mac-studio bash -c 'cat "$HOME"/.local/state/crew/wldn/runs/*/*.rec')" "A plan-only deploy is checked."
eq "$(field unit.add From unit/zone-first)" "proposal/2"
has "$(field unit.add Commit unit/zone-first)" "WilldanGroup/crew-state@"
trace=$(crew trace unit/zone-first)
eq "$(grep -v 'refused:' <<<"$trace" | awk '{print $3}' | head -4 | tr '\n' ' ')" "plan.propose plan.agree plan.approve unit.add "
has "$trace" "refused: proposal 2 waits on the agreement of swb-1-conductor"
lacks "$trace" "unit/the-deploy-is-logged"
ok "each step of a proposal is in the run record, and a unit's trace shows the proposal, the agreement and the approval"

# A command holding a backtick is fenced so it reads whole.
expect_ok crew plan propose "$(proposal 'Case: The x command is checked.' 'Do: unit add ticks "The `x` command works." --repo switchboard-kit')"
n=$(props -t Proposal -P Proposal | tail -1)
expect_ok crew plan proposed "$n"
has "$out" 'Runs: ``crew unit add ticks "The `x` command works." --repo switchboard-kit``'
ok "a command that holds a backtick is shown in a code span fenced longer than it"
