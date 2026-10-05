# A dropped unit leaves nothing behind: crew unit drop frees its slot and removes its worktree and branch. A slot still
# holding a unit the plan no longer has, because its agent was working when the unit was dropped, is freed with
# crew unit free, which refuses a unit still in the plan and a worktree with uncommitted changes.
. "$TESTS/lib.sh"
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
CREW_AGENT=wldn-planner crew bolt new biome "The shell and the check run one biome." --repo switchboard-kit >/dev/null
for u in pin-biome follows-the-shell clean-drop; do CREW_AGENT=wldn-planner crew unit add $u "Unit $u." --bolt biome >/dev/null; done
crew bolt give swb-1 >/dev/null 2>&1
export CREW_AGENT=swb-1-conductor
slots=$(home_of $box)/.local/state/swb-1-team/slots
for u in pin-biome follows-the-shell clean-drop; do crew unit run $u construct >/dev/null; done
pane_of_slot() { awk -v s="$1" '$1==s{print $2}' "$(home_of $box)/.local/state/swb-1-team/panes"; }
held() { awk -v u="$1" '$3==u{print $1}' "$slots"; }

expect_ok crew unit drop clean-drop "not wanted"
has "$out" "is free"; has "$out" "$kd/places/clean-drop and unit/clean-drop are removed; the branch was at"
eq "$(held clean-drop)" ""; [[ ! -d $kd/places/clean-drop ]] || fail "clean-drop's worktree is still there"
git -C "$k" rev-parse --verify -q unit/clean-drop >/dev/null && fail "unit/clean-drop is still there"
ok "drop frees the unit's slot and removes its worktree and branch"

slot=$(held pin-biome)
as $box herdr --session wldn-1 stub status "$(pane_of_slot "$slot")" working
CREW_AGENT=wldn-planner expect_ok crew unit drop pin-biome "a duplicate of follows-the-shell"
has "$out" "pin-biome's slot on swb-1 was not freed"
eq "$(held pin-biome)" "$slot"; [[ -d $kd/places/pin-biome ]] || fail "pin-biome's worktree went with its agent still working"
ok "a unit dropped while its stage works keeps its slot, worktree and branch"

expect_fail "no team on this host holds pin-biome in a slot; name its team: crew unit free pin-biome --team <team>" crew unit free pin-biome
expect_fail "unit follows-the-shell is in plan/wldn of WilldanGroup/willdan-blueprints: drop it with crew unit drop" crew unit free follows-the-shell --team swb-1
expect_fail "is working; add --force to end it anyway" crew unit free pin-biome --team swb-1
as $box herdr --session wldn-1 stub status "$(pane_of_slot "$slot")" idle
echo half-done > "$kd/places/pin-biome/note"
expect_fail "$kd/places/pin-biome has uncommitted changes: they are the user's to keep or discard" crew unit free pin-biome --team swb-1
eq "$(held pin-biome)" "$slot"
ok "free refuses a unit still in the plan, a working agent, and a worktree with uncommitted changes"

rm "$kd/places/pin-biome/note"
HOST=$box expect_ok crew unit free pin-biome
has "$out" "swb-1-$slot is free"; has "$out" "$kd/places/pin-biome and unit/pin-biome are removed; the branch was at"
eq "$(held pin-biome)" ""; [[ ! -d $kd/places/pin-biome ]] || fail "pin-biome's worktree is still there"
git -C "$k" rev-parse --verify -q unit/pin-biome >/dev/null && fail "unit/pin-biome is still there"
eq "$(held follows-the-shell)" "unit-2"
ok "free on the team's host finds the slot, ends its agent and removes the worktree and branch"
