# A unit's stages from the bolt's give, through the crew command on the stubs (tests.11, record 0022): give makes the
# bolt's worktree; each stage of a unit takes a slot, starts a fresh agent in the unit's place and sends its prompt;
# the waits end each stage at its deliverable and record it; the team's read records an end nobody waited on, fetching
# and gathering once; verify's report ends it; and code's prompt names an unmerged unit's overlapping Touches. The
# units journey's other parts: t-journey-slots, t-journey-merge, t-journey-prompts, t-journey-fix, t-journey-land.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
expect_ok crew up swb-1
eq "$(field $box team.up On)" "team/swb-1 agent/swb-1-conductor agent/swb-1-ops"
eq "$(field $box team.up By)" "$me@mac-studio"
expect_ok crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit --source books/x.md
has "$out" "plan(tenant-environments): add the bolt ($me@mac-studio)"
by_hand 'old = {plan.declares(q): q for q in plan.Plan(plan.HEADER.replace(" Amended", "")).paras if plan.declares(q)}
p.paras = [old.get(plan.declares(x), x) for x in p.paras]'
expect_ok crew unit add a "Unit a." --bolt tenant-environments --source books/x.md --source switchboard-kit:docs/y.md
has "$out" "plan(tenant-environments): add a ($me@mac-studio)"
eq "$(plan -t Unit -e "Unit = 'a'" -P Source)" $'books/x.md\nswitchboard-kit:docs/y.md'
has "$(grep '^%allowed: Unit' "$T/plan.rec")" "Amended"
by_hand 'unit("b", "tenant-environments", "a"); [unit(u, "tenant-environments") for u in "cde"]
p.insert(plan.Rec("Bolt", [("Bolt", "console-pages"), ("Repo", "switchboard-kit"), ("Goal", "The console lists them.")]))'
expect_ok crew bolt give swb-1
has "$out" "swb-1 holds tenant-environments: bolt/tenant-environments at $bolt on $box"
eq "$(plan -t Bolt -e "Bolt = 'tenant-environments'" -P Team)" "swb-1"
eq "$(git -C "$k" rev-parse bolt/tenant-environments)" "$(git -C "$k" rev-parse main)"
eq "$(cat "$bolt/.prepared")" "$k"
eq "$(field mac-studio bolt.give On) $(field mac-studio bolt.give Commit)" "bolt/tenant-environments team/swb-1 WilldanGroup/crew-state@$(git --git-dir "$ws" rev-parse wldn/main)"
ok "crew up records the team's agents; bolt new and unit add each commit to the plan in the asker's name, a write bringing an older plan's descriptors in step; give makes the bolt's branch from main and its prepared worktree on the team's host"

# The conductor runs the stages on the team's host.
export CREW_AGENT=swb-1-conductor
expect_ok crew unit run a construct
has "$out" "swb-1-unit-1 has a: construct, in $kd/places/a"
eq "$(cat "$slots")" "unit-1 unit a $kd/places/a"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/a)" "bolt/tenant-environments"
eq "$(cat "$kd/places/a/.prepared")" "$k"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort high | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to swb-1-unit-1)" "'/opsx:propose a Unit a. Sources: books/x.md; switchboard-kit:docs/y.md.'"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1,swb-1 units"
eq "$(field $box stage.start On stage/a/construct)" "stage/a/construct unit/a agent/swb-1-unit-1"
eq "$(field $box stage.start By stage/a/construct)" "swb-1-conductor"
has "$(cat "$stages")" "unit-1 a construct "
ok "construct takes a free slot, makes the unit's prepared place from the bolt, starts a fresh agent sent its prompt in the units workspace, and records the start it owes an end"

expect_fail "unit b is waiting: it comes after a, whose change is not committed yet" crew unit run b construct
eq "$(wc -l < "$slots" | tr -d ' ')" "1"
[[ ! -d $kd/places/b ]] || fail "b's place was made"
has "$(field $box stage.start Refused stage/b/construct)" "unit b is waiting"
eq "$(ls -A "$(home_of $box)/.cache/crew/reads" "$(home_of mac-studio)/.cache/crew/reads" 2>/dev/null | grep -v '^/\|^$' || true)" ""
ok "a stage refused takes no slot, makes no place, leaves no reading, and is recorded refused"

change "$kd/places/a" a 0 3; commit_all "$kd/places/a" "docs(a): the change"
status swb-1-unit-1 working
expect_ok crew unit wait a --stuck 0 --timeout 0
eq "$out" "construct on a is still running after the wait's 0 ms: swb-1-unit-1 is working; nothing is recorded yet"
status swb-1-unit-1 idle
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered construct on a: its change is committed at $(short unit/a)"
eq "$(field $box stage.end Ended stage/a/construct)" "delivered"
eq "$(field $box stage.end Delivered stage/a/construct)" "unit/a@$(short unit/a)"
eq "$(field $box stage.end Result stage/a/construct)" "planned"
eq "$(cat "$stages")" ""
ok "a wait reads the stage still running while its agent works, then records its end with what it delivered"

echo a > "$kd/places/a/a-work"; commit_all "$kd/places/a" "feat(a): its own work"; tick a 1.1
expect_ok crew unit run b construct
has "$out" "swb-1-unit-2 has b: construct, in $kd/places/b"
git -C "$k" merge-base --is-ancestor unit/a unit/b || fail "b's place does not hold a's work"
eq "$(field $box stage.start Took stage/b/construct)" "a@$(git -C "$k" rev-parse --short=7 unit/a)"
expect_ok crew unit run a code
grep -q "^$box wldn-1 agent prompt $(pane swb-1-unit-1) /exit\|^$box wldn-1 agent prompt swb-1-unit-1 /exit" "$CREW_TEST_LOG" || fail "a's construct agent was not ended"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to swb-1-unit-1)" "'/opsx:apply a'"
ok "a dependent's construct takes its After unit's head; code ends the slot's agent and starts a fresh one at its own effort"

# The team's read on its host: an end nobody waited on recorded late, the state branch fetched and the kit gathered once.
tick a 1.2; tick a 1.3
stale=$(home_of $box)/.cache/crew/reads/OLDOLDOL; mkdir -p "$stale"; echo $box > "$stale/host"; touch -t 202601010000 "$stale"
: > "$T/reads.log"
PATH="$T/shim:$PATH" CREW_TEST_READS=$T/reads.log expect_ok crew status swb-1
for want in "swb-1-conductor" "swb-1-ops" "a  verify 3/3" "b  construct"; do has "$out" "$want"; done
eq "$(reads fetch) $(reads gather) $(reads openspec)" "1 1 0"
eq "$(ls -A "$(home_of $box)/.cache/crew/reads" 2>/dev/null)" ""
eq "$(field $box stage.end Ended stage/a/code)" "delivered"
eq "$(field $box stage.end Observed stage/a/code)" "late"
eq "$(field $box stage.end Tasks stage/a/code)" "3/3"
ok "crew status lists the roles and each slot's stage, fetches and gathers once, leaves no reading and removes one a day old, and records a delivered end nobody waited on, late"

expect_ok crew unit run a verify
eq "$(prompt_to swb-1-unit-1)" "'/opsx:verify a Changed and not declared in its Touches: a-work.'"
mkdir -p "$reports"; report=$reports/verify-a-20261008-1412.md; echo "the report" > "$report"
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered verify on a: the report is $report"
expect_ok crew trace report/verify-a-20261008-1412.md
has "$out" "stage/a/verify unit/a agent/swb-1-unit-1 → verify 3/3, delivered report/verify-a-20261008-1412.md"
ok "verify's prompt names what the unit changed and did not declare; the report it saves ends it, and crew trace finds it"

change "$kd/places/b" b 0 2; commit_all "$kd/places/b" "docs(b): the change"
touches b 'src/b/**' src/a/x
expect_ok crew unit run b code
eq "$(prompt_to swb-1-unit-2)" "'/opsx:apply b Its Touches overlap those of a, ahead of it in the bolt and not merged, on src/a/x against src/a/**; a'\"'\"'s change is $kd/places/a/openspec/changes/a/.'"
looks() { grep -c " agent get swb-1-unit-2$" "$CREW_TEST_LOG" || true; }
n=$(looks)
crew unit wait b --stuck 3600000 --timeout 1800000 > "$T/wait.out" 2>&1 &
waiting=$!
until_ok eval '(( $(looks) > n ))' || fail "the wait never looked at b"
kill -0 $waiting 2>/dev/null || fail "the wait returned before b's tasks were ticked: $(cat "$T/wait.out")"
tick b 1.1; tick b 1.2
wait $waiting || fail "the wait failed: $(cat "$T/wait.out")"
eq "$(tail -1 "$T/wait.out")" "swb-1-unit-2 delivered code on b: every task is ticked (2/2) at $(short unit/b)"
ok "code's prompt names the Touches it overlaps of an unmerged unit ahead of it, and a wait that saw a task open sees it ticked at its next look"

