# After holds a dependent's construct and its merge, never its code: a unit after one whose change is not committed
# is waiting and refused construct; once that change is committed, construct is accepted though the unit it comes
# after has not merged; and the dependent's merge is refused, naming it, until it has merged into the bolt. Each
# scenario of the bolt-plan spec "The file's order and dependencies are the plan".
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew unit add a "Unit a." --bolt tenant-environments >/dev/null
crew unit add b "Unit b." --bolt tenant-environments --after a >/dev/null
crew bolt give swb-1 >/dev/null 2>&1
export CREW_AGENT=swb-1-conductor
bolt=$kd/bolts/tenant-environments

expect_ok crew unit run a construct
eq "$(stage b)" "waiting"
expect_fail "unit b is waiting: it comes after a, whose change is not committed yet" crew unit run b construct
[[ ! -d $kd/places/b ]] || fail "b's place was made"
ok "a dependency still in construct holds its dependent's construct"

change "$kd/places/a" a 0 2; commit_all "$kd/places/a" "docs(a): the change"
rewrite "$kd/places/a/openspec/changes/a/tasks.md" 's/- \[ \] 1.1/- [x] 1.1/'; commit_all "$kd/places/a" "feat(a): task 1"
eq "$(stage a)" "code"; eq "$(stage b)" "ready"
expect_ok crew unit run b construct
has "$out" "has b: construct, in $kd/places/b"
ok "a dependency whose change is committed, in code and not merged, lets its dependent's construct start"

change "$kd/places/b" b 2 2; commit_all "$kd/places/b" "feat(b): done"
eq "$(stage b)" "verify"
expect_fail "unit b merges after a, not yet merged into bolt/tenant-environments" crew unit run b merge
has "$(crew events --label wldn --about stage/b/merge 2>&1)" "unit b merges after a"
rewrite "$kd/places/a/openspec/changes/a/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/a" "feat(a): done"
git -C "$bolt" merge -q --no-ff -m "merge a" unit/a
eq "$(stage a)" "merged"
expect_ok crew unit run b merge
eq "$(grep -c "agent prompt .* 'Merge b into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'" "$CREW_TEST_LOG")" "1"
ok "a dependent's merge is refused, naming the unit it comes after, until that unit has merged into the bolt"
