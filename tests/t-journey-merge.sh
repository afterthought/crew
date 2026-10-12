# A verified unit settled and merged, through the crew command on the stubs (tests.11, record 0022), a part of the units
# journey (t-journey-units): a forecast against the bolt starts a verified unit's settle stage; a dependent holding
# that unit's work as its place took it is not forecast against the unit for the settle's revision of it; the unit
# merges through worktrunk; the merge's wait rebases a dependent onto the bolt and undoes a rebase that conflicts; and
# the next read frees the merged unit's slot and removes its place.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world 'unit("a", "tenant-environments"); unit("b", "tenant-environments", "a"); unit("c", "tenant-environments", "a")'
export CREW_AGENT=swb-1-conductor
crew unit run a construct >/dev/null
change "$kd/places/a" a 3 3; commit_all "$kd/places/a" "feat(a): its change, done"
crew unit wait a >/dev/null; crew unit run a verify >/dev/null
mkdir -p "$reports"; echo "the report" > "$reports/verify-a-20261008-1412.md"; crew unit wait a >/dev/null
crew unit run b construct >/dev/null; change "$kd/places/b" b 0 2; commit_all "$kd/places/b" "docs(b): the change"; crew unit wait b >/dev/null
printf 'one\ntwo, as a has it\nthree\n' > "$kd/places/a/shared.txt"; commit_all "$kd/places/a" "feat(a): its line"
crew unit run c construct >/dev/null; change "$kd/places/c" c 0 2
printf 'one\ntwo, as c has it\nthree\n' > "$kd/places/c/shared.txt"; commit_all "$kd/places/c" "docs(c): the change"; crew unit wait c >/dev/null
# The bolt takes a line of shared.txt that a, verified and waiting to merge, also changed: the next wait forecasts it,
# and starts a's settle stage.
printf 'one\ntwo, as the bolt has it\nthree\n' > "$bolt/shared.txt"; commit_all "$bolt" "feat: the bolt's own line"
: > "$CREW_TEST_LOG"
expect_ok crew unit wait b --timeout 0
eq "$(field $box forecast Reached unit/a bolt/tenant-environments)" "settle"
has "$(prompt_to swb-1-unit-1)" "'Settle a: Your branch is forecast to conflict with bolt/tenant-environments on shared.txt. Rebase your place onto the bolt (git rebase bolt/tenant-environments)"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(field $box stage.start By stage/a/settle)" "swb-1-conductor"
git -C "$kd/places/a" rebase -q bolt/tenant-environments >/dev/null 2>&1 && fail "a's rebase onto the bolt did not conflict"
printf 'one\ntwo, as a has it, and as the bolt has it\nthree\n' > "$kd/places/a/shared.txt"; git -C "$kd/places/a" add shared.txt
GIT_EDITOR=true git -C "$kd/places/a" rebase --continue >/dev/null 2>&1 || fail "a's rebase did not continue"
# The settle also revises a's design, which b's place holds as it took it: from the bolt both started on, git sees b and
# a change it two ways; from the head b took, b adds nothing to it, and b, after a, is forecast nothing against a.
printf '# Design\n\nz, as it stands on the bolt\n' > "$kd/places/a/openspec/changes/a/design.md"; commit_all "$kd/places/a" "docs(a): its design on the bolt"
expect_ok crew unit wait a
has "$out" "swb-1-unit-1 delivered settle on a: its branch is at $(short unit/a), ready to merge"
eq "$(field $box forecast Heads unit/b unit/a)" ""
expect_ok crew unit run a merge
eq "$(prompt_to swb-1-unit-1)" "'Merge a into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'"
has "$out" "Close your Pending You card for verify/a, if one is open, with what was done."
(cd "$kd/places/a" && wt merge bolt/tenant-environments --no-squash --no-remove >/dev/null 2>&1) || fail "wt merge failed"
b_before=$(git -C "$k" rev-parse unit/b) c_before=$(git -C "$k" rev-parse unit/c)
expect_ok crew unit wait a
has "$out" "swb-1-unit-1 delivered merge on a: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
has "$out" "rebasing c onto bolt/tenant-environments conflicts: its place is as it was, and it is told"
git -C "$k" merge-base --is-ancestor bolt/tenant-environments unit/b || fail "b was not rebased onto the bolt: $out"
[[ $(git -C "$k" rev-parse unit/b) != "$b_before" ]] || fail "b did not move"
eq "$(git -C "$k" rev-parse unit/c)" "$c_before"
eq "$(field $box unit.rebase From unit/b)" "unit/a"
ok "a forecast against the bolt starts a verified unit's settle stage, a dependent is forecast nothing for the unit's own work its place took, and the unit merges, each a fresh agent ended at its deliverable; the merge names the verify row's card, and its wait rebases a dependent onto the bolt and undoes a rebase that conflicts"

expect_ok crew status swb-1
has "$out" "swb-1-unit-1 is free: a has merged into its bolt"
has "$out" "$kd/places/a and unit/a are removed; the branch was at"
[[ ! -d $kd/places/a ]] || fail "a's place is still there"
ok "the next read frees a merged unit's slot and removes its place"
