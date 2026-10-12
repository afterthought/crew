# A chore from its add to its slot's freeing, through the crew command on the stubs (tests.11, record 0022), a part of
# the units journey (t-journey-units): crew chore add writes a Unit record marked Kind: chore; code takes a slot in
# places/chore-<name> on chore/<name> from the bolt and is sent the chore's words; its wait ends at a commit; verify ends
# at its report; a merge is refused while a commit lacks the chore's trailer, and merges once none does, its wait ending
# once the bolt holds the trailer; crew bolts reads each stage from the kit; the team's read frees the slot and removes
# the place; crew unit run on a chore is refused naming its kind; and crew trace finds it by its bare name.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/test_chores.py); how git reads a chore's trailer, contract cases (tests/contract/). Each step checks
# the command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world 'unit("a", "tenant-environments")'
cp=$kd/places/chore-bump
stage_of() { crew bolts | awk -v c=bump '$1 == c {print $2, $3}'; }
expect_ok crew chore add bump "Biome follows the shell ZQXT." --bolt tenant-environments
has "$out" "plan(tenant-environments): add chore bump ($me@mac-studio)"
eq "$(plan -t Unit -e "Unit = 'bump'" -P Kind)" "chore"
eq "$(field mac-studio chore.add On)" "chore/bump bolt/tenant-environments"
eq "$(stage_of)" "chore ready"
ok "crew chore add writes a Unit record marked Kind: chore and records chore.add on it; crew bolts reads it ready"

export CREW_AGENT=swb-1-conductor
expect_fail "bump is a chore, which has no construct" crew unit run bump construct
has "$(field $box stage.start On stage/bump/construct)" "chore/bump"
expect_fail "no stage 'construct' for a chore; stages: code verify merge" crew chore run bump construct
eq "$(cat "$slots")" ""
expect_ok crew chore run bump code
has "$out" "swb-1-unit-1 has chore bump: code, in $cp"
eq "$(cat "$slots")" "unit-1 chore bump $cp"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/chore/bump)" "bolt/tenant-environments"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $cp"
eq "$(prompt_to swb-1-unit-1)" "'Chore bump: Biome follows the shell ZQXT.'"
eq "$(field $box stage.start On stage/bump/code)" "stage/bump/code chore/bump agent/swb-1-unit-1"
eq "$(stage_of)" "chore code"
ok "a chore runs no construct; its code takes a slot in its own place from the bolt and is sent the chore's words"

echo pinned > "$cp/biome"; commit_all "$cp" "chore: biome follows the shell"
expect_ok crew chore wait bump
eq "$out" "swb-1-unit-1 delivered code on chore bump: its branch is at $(short chore/bump)"
eq "$(field $box stage.end Delivered stage/bump/code)" "chore/bump@$(short chore/bump)"
eq "$(stage_of)" "chore verify"
expect_ok crew chore run bump verify
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort high | swb-1-unit-1 | $cp"
eq "$(prompt_to swb-1-unit-1)" "'Verify chore bump: Biome follows the shell ZQXT.'"
mkdir -p "$reports"; report=$reports/verify-bump-20261012-1600.md; echo "the report" > "$report"
expect_ok crew chore wait bump
eq "$out" "swb-1-unit-1 delivered verify on chore bump: the report is $report"
ok "code ends at a commit on the chore's branch; verify is sent its words and ends at its report"

expect_fail "chore bump merges only once every commit beyond bolt/tenant-environments carries \`Chore: bump\`" crew chore run bump merge
has "$out" "$(short chore/bump) (chore: biome follows the shell) does not"
git -C "$cp" commit -q --amend --no-edit --trailer "Chore: bump"
expect_ok crew chore run bump merge
eq "$(prompt_to swb-1-unit-1)" "'Merge bump into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'"
has "$out" "Close your Pending You card for verify/bump, if one is open, with what was done."
(cd "$cp" && wt merge bolt/tenant-environments --no-squash --no-remove >/dev/null 2>&1) || fail "wt merge of the chore failed"
expect_ok crew chore wait bump
has "$out" "swb-1-unit-1 delivered merge on chore bump: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
eq "$(stage_of)" "chore merged"
ok "a merge is refused while a commit lacks the chore's trailer; once none does it merges through worktrunk, and its wait ends once the bolt holds the trailer"

expect_ok crew status swb-1
has "$out" "swb-1-unit-1 is free: bump has merged into its bolt"
has "$out" "$cp and chore/bump are removed; the branch was at"
[[ ! -d $cp ]] || fail "the chore's place is still there"
eq "$(field $box slot.free On)" "agent/swb-1-unit-1 chore/bump"
[[ $(record_of $box)$(record_of mac-studio) != *ZQXT* ]] || fail "a chore's words are in the run record"
expect_ok crew trace bump
has "$out" "chore.add"; has "$out" "stage/bump/merge chore/bump"
ok "the team's read frees a merged chore's slot and removes its place; the record holds none of its words, and crew trace finds it by its bare name"
