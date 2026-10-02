# The merge stage runs wt merge bolt/<bolt> --no-squash --no-remove from the unit's place. Once the bolt holds
# the change, crew removes the place and frees the slot: the unit reads merged.
. "$TESTS/lib.sh"
command -v wt >/dev/null || fail "this test needs worktrunk's wt"
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn CREW_AGENT=swb-1-conductor
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew unit add a "Unit a." --bolt tenant-environments >/dev/null
crew unit add b "Unit b." --bolt tenant-environments >/dev/null
crew bolt give swb-1 >/dev/null 2>&1
crew unit run a construct >/dev/null; crew unit run b construct >/dev/null
change "$kd/places/a" a 0 2; commit_all "$kd/places/a" "docs(a): the change"; crew unit approve a >/dev/null
sed -i '' 's/- \[ \]/- [x]/' "$kd/places/a/openspec/changes/a/tasks.md"; commit_all "$kd/places/a" "feat(a): built"
expect_ok crew unit run a merge
slot=$(herdr_state $box wldn-1 '.agents | to_entries[] | select(.value.name == "swb-1-unit-1") | .key')

# What the merge stage's agent does, in the unit's place.
as $box herdr --session wldn-1 stub status "$slot" working
(cd "$kd/places/a" && wt merge bolt/tenant-environments --no-squash --no-remove >/dev/null 2>&1) || fail "wt merge failed"
[[ -d $kd/places/a ]] || fail "--no-remove should keep the place for crew to remove"
expect_ok crew status swb-1; has "$out" "swb-1-unit-1"; has "$out" "a  merged"
[[ -d $kd/places/a ]] || fail "a working merge agent's place was removed"
ok "while the merge agent works, its slot is left alone"

as $box herdr --session wldn-1 stub status "$slot" idle
expect_ok crew status swb-1
has "$out" "swb-1-unit-1 is free: a has merged into its bolt"
[[ ! -d $kd/places/a ]] || fail "the merged unit's place is still there"
git -C "$k" rev-parse --verify -q unit/a >/dev/null && fail "unit/a is still there"
eq "$(awk '$1 == "unit-1"' "$(home_of $box)/.local/state/swb-1-team/slots")" ""
eq "$(grep "^swb-1-unit-1 " <<<"$out" | tail -1 | awk '{print $3}')" "free"
eq "$(stage a)" "merged"
git -C "$k" ls-tree -d --name-only bolt/tenant-environments openspec/changes/ | grep -qx openspec/changes/a || fail "the bolt does not hold a's change"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1 units"
ok "once the bolt holds the change, the place is removed, the slot freed, and the unit reads merged"

crew unit drop b "not wanted after all" >/dev/null
eq "$(herdr_state $box wldn-1 '.workspaces | length')" "0"
eq "$(awk NF "$(home_of $box)/.local/state/swb-1-team/slots")" ""
ok "dropping the last unit in flight frees its slot and closes the units workspace"
