# Units merge in their order, each with its own change, through the crew command on the stubs (tests.11, record 0022),
# a part of the units journey (t-journey-units), on wldn's case of 2026-10-13 (swb-4, signals 51c2c852/01 and
# 45f551aa/01): d comes after s and the plan lists d first. s's code is told nothing of d, and d's is told of s
# (teams.12); s's merge, its branch holding d's work, is refused, naming d (teams.17); merged by hand as the old crew
# let it, s carries d's change onto the bolt open, and d has not merged: crew status names it carried by another's
# merge, the team's read keeps its place, and its merge, its place made again from the bolt once it is gone, archives
# the change there and delivers once the bolt holds it archived (teams.17, plan.9).
# Which unit is ahead, what a merge carries, and how a carried unit's stage and slot read are logic cases
# (tests/py/test_touches.py, test_forecast.py, test_stage_rules.py, test_chores.py, test_tidy.py, test_slots.py); how
# gather reads a bolt's archived and open changes, a contract case (tests/contract/test_gather.py). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world 'unit("d", "tenant-environments", "s"); unit("s", "tenant-environments")'
export CREW_AGENT=swb-1-conductor
crew unit run s construct >/dev/null; change "$kd/places/s" s 0 2; commit_all "$kd/places/s" "docs(s): the change"
touches s src/boundary.ts; crew unit wait s >/dev/null
crew unit run d construct >/dev/null; change "$kd/places/d" d 0 2; commit_all "$kd/places/d" "docs(d): the change"
touches d src/boundary.ts; crew unit wait d >/dev/null
expect_ok crew unit run s code
s_slot=$(awk '$3 == "s" {print $1}' "$slots"); d_slot=$(awk '$3 == "d" {print $1}' "$slots")
lacks "$(prompt_to "swb-1-$s_slot")" "Its Touches overlap"
expect_ok crew unit run d code
has "$(prompt_to "swb-1-$d_slot")" "Its Touches overlap those of s, ahead of it in the bolt and not merged, on src/boundary.ts"
ok "a dependency listed after its dependent is told nothing of it, and the dependent is told of the dependency ahead of it"

change "$kd/places/s" s 2 2; commit_all "$kd/places/s" "feat(s): done"; crew unit wait s >/dev/null
change "$kd/places/d" d 2 2; commit_all "$kd/places/d" "feat(d): done"; crew unit wait d >/dev/null
git -C "$kd/places/s" merge -q --no-ff -m "merge d, as the note once asked" unit/d
expect_fail "unit s does not merge while unit/s holds the change of d open, which bolt/tenant-environments does not hold archived" crew unit run s merge
has "$out" "d comes after s: take that work out of unit/s"
ok "a merge whose branch holds another unit's change open, which the bolt does not hold archived, is refused before it starts, naming it"

# s merged by hand, as the old crew let it: its own change archived, d's carried onto the bolt open.
mkdir -p "$kd/places/s/openspec/changes/archive"; git -C "$kd/places/s" mv openspec/changes/s openspec/changes/archive/2026-10-13-s
git -C "$kd/places/s" commit -qm "docs(openspec): archive s"
merge_as "swb-1-$s_slot" "$kd/places/s" bolt/tenant-environments || fail "s's submission failed"
git -C "$k" cat-file -e "bolt/tenant-environments:openspec/changes/d/tasks.md" || fail "d's change is not open on the bolt"
expect_ok crew status swb-1
has "$out" "d  verify 2/2  carried by another's merge, its own merge owed"
has "$out" "is free: s has merged into its bolt"
[[ -d $kd/places/d ]] || fail "d's place was removed though d has not merged"
ok "a unit whose change its bolt holds open has not merged: crew status names it carried, and its place and slot are kept"

# Its place gone, as the old crew's read removed it: the merge makes it again from the bolt.
git -C "$k" worktree remove --force "$kd/places/d"; git -C "$k" branch -q -D unit/d
expect_ok crew status swb-1
has "$out" "d  verify 2/2  carried by another's merge, its own merge owed"
expect_ok crew unit run d merge
[[ -d $kd/places/d ]] || fail "d's place was not made again"
eq "$(git -C "$kd/places/d" rev-parse HEAD)" "$(git -C "$k" rev-parse bolt/tenant-environments)"
eq "$(prompt_to "swb-1-$d_slot")" "'Merge d into bolt/tenant-environments: sluice submit bolt/tenant-environments --no-wait --json'"
mkdir -p "$kd/places/d/openspec/changes/archive"; git -C "$kd/places/d" mv openspec/changes/d openspec/changes/archive/2026-10-13-d
git -C "$kd/places/d" commit -qm "docs(openspec): archive d"
merge_as "swb-1-$d_slot" "$kd/places/d" bolt/tenant-environments || fail "d's submission failed"
expect_ok crew unit wait d
has "$out" "delivered merge on d: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
eq "$(crew bolts | awk '$1 == "d" {print $2}')" "merged"
ok "a carried unit's merge makes its place again from the bolt, archives its change there, and delivers once the bolt holds it archived"
