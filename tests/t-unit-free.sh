# A dropped unit leaves nothing behind: crew unit drop frees its slot and removes its worktree and branch. A slot still
# holding a unit the plan no longer has, because its agent was working when the unit was dropped, is freed by the
# next read of the team once that agent settles, or by the user with crew unit free, which refuses a unit still in
# the team's bolt and a worktree with uncommitted changes. A unit that leaves the team's bolt, queued again or moved to
# another bolt, leaves its slot the same way, and crew rebuild keeps only the slots of work still in the bolt.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new biome "The shell and the check run one biome." --repo switchboard-kit >/dev/null
for u in pin-biome follows-the-shell clean-drop half-done; do crew unit add $u "Unit $u." --bolt biome >/dev/null; done
crew bolt give swb-1 >/dev/null 2>&1
export CREW_AGENT=swb-1-conductor
slots=$(home_of $box)/.local/state/swb-1-team/slots
for u in pin-biome follows-the-shell clean-drop half-done; do crew unit run $u construct >/dev/null; done
pane_of_slot() { awk -v s="$1" '$1==s{print $2}' "$(home_of $box)/.local/state/swb-1-team/panes"; }
held() { awk -v u="$1" '$3==u{print $1}' "$slots"; }

CREW_AGENT= expect_ok crew unit drop clean-drop "not wanted"
has "$out" "is free"; has "$out" "$kd/places/clean-drop and unit/clean-drop are removed; the branch was at"
eq "$(held clean-drop)" ""; [[ ! -d $kd/places/clean-drop ]] || fail "clean-drop's worktree is still there"
git -C "$k" rev-parse --verify -q unit/clean-drop >/dev/null && fail "unit/clean-drop is still there"
ok "drop frees the unit's slot and removes its worktree and branch"

slot=$(held pin-biome)
as $box herdr --session wldn-1 stub status "$(pane_of_slot "$slot")" working
CREW_AGENT= expect_ok crew unit drop pin-biome "a duplicate of follows-the-shell"
has "$out" "swb-1-$slot still holds pin-biome, dropped from the plan: its agent is working; it is freed once that settles"
eq "$(held pin-biome)" "$slot"; [[ -d $kd/places/pin-biome ]] || fail "pin-biome's worktree went with its agent still working"
ok "a unit dropped while its stage works keeps its slot, worktree and branch"

expect_ok crew status swb-1
has "$out" "swb-1-$slot still holds pin-biome, dropped from the plan: its agent is working; it is freed once that settles"
has "$out" "pin-biome  dropped"
eq "$(held pin-biome)" "$slot"; [[ -d $kd/places/pin-biome ]] || fail "pin-biome's worktree went with its agent still working"
as $box herdr --session wldn-1 stub status "$(pane_of_slot "$slot")" idle
expect_ok crew status swb-1
has "$out" "swb-1-$slot is free: pin-biome was dropped from the plan"
has "$out" "$kd/places/pin-biome and unit/pin-biome are removed; the branch was at"
eq "$(held pin-biome)" ""; [[ ! -d $kd/places/pin-biome ]] || fail "pin-biome's worktree is still there"
git -C "$k" rev-parse --verify -q unit/pin-biome >/dev/null && fail "unit/pin-biome is still there"
ok "once its agent settles, the next crew status frees the slot and removes the worktree and branch"

slot=$(held half-done)
as $box herdr --session wldn-1 stub status "$(pane_of_slot "$slot")" working
CREW_AGENT= crew unit drop half-done "folded into follows-the-shell" >/dev/null 2>&1
expect_fail "no team on this host holds half-done in a slot; name its team: crew unit free half-done --team <team>" crew unit free half-done
expect_fail "unit follows-the-shell is in bolt biome, which swb-1 holds: drop it with crew unit drop" crew unit free follows-the-shell --team swb-1
expect_fail "is working; add --force to end it anyway" crew unit free half-done --team swb-1
as $box herdr --session wldn-1 stub status "$(pane_of_slot "$slot")" idle
echo half-done > "$kd/places/half-done/note"
expect_fail "$kd/places/half-done has uncommitted changes: they are the user's to keep or discard" crew unit free half-done --team swb-1
eq "$(held half-done)" "$slot"
ok "free refuses a unit still in the team's bolt, a working agent, and a worktree with uncommitted changes"

rm "$kd/places/half-done/note"
HOST=$box expect_ok crew unit free half-done
has "$out" "swb-1-$slot is free"; has "$out" "$kd/places/half-done and unit/half-done are removed; the branch was at"
eq "$(held half-done)" ""; [[ ! -d $kd/places/half-done ]] || fail "half-done's worktree is still there"
git -C "$k" rev-parse --verify -q unit/half-done >/dev/null && fail "unit/half-done is still there"
eq "$(held follows-the-shell)" "unit-2"
ok "free on the team's host finds the slot, ends its agent and removes the worktree and branch"

slots2=$(home_of $box)/.local/state/swb-2-team/slots
held2() { awk -v u="$1" '$3==u{print $1}' "$slots2"; }
pane_of_slot2() { awk -v s="$1" '$1==s{print $2}' "$(home_of $box)/.local/state/swb-2-team/panes"; }
CREW_AGENT= crew bolt new fmt-pass "One fmt pass." --repo switchboard-kit >/dev/null
for u in fmt-moved fmt-busy fmt-idle; do CREW_AGENT= crew unit add $u "Unit $u." --bolt fmt-pass >/dev/null; done
CREW_AGENT= crew bolt give swb-2 fmt-pass >/dev/null 2>&1
crew unit run fmt-moved construct >/dev/null
slot=$(held2 fmt-moved)
CREW_AGENT= crew unit move fmt-moved biome >/dev/null
eq "$(held2 fmt-moved)" "$slot"
expect_ok crew unit free fmt-moved --team swb-2
has "$out" "swb-2-$slot is free"
eq "$(held2 fmt-moved)" ""; [[ -d $kd/places/fmt-moved ]] || fail "fmt-moved's worktree went with the slot it left"
ok "free frees a slot whose unit moved to another bolt, and its worktree stays with the unit"

for u in fmt-busy fmt-idle; do
  crew unit run $u construct >/dev/null
  git -C "$k" worktree remove --force "$kd/places/$u"; git -C "$k" branch -q -D "unit/$u"  # a queued unit has none
done
busy=$(held2 fmt-busy) idle=$(held2 fmt-idle)
as $box herdr --session wldn-1 stub status "$(pane_of_slot2 "$busy")" working
CREW_AGENT= expect_ok crew bolt drop fmt-pass "folded into biome" --requeue
has "$out" "swb-2-$idle is free: fmt-idle has left swb-2's bolt"
has "$out" "swb-2-$busy still holds fmt-busy, which has left swb-2's bolt: its agent is working; it is freed once that settles"
eq "$(held2 fmt-idle)" ""; eq "$(held2 fmt-busy)" "$busy"
ok "a unit requeued by bolt drop leaves its slot at once, or once its agent settles"

expect_ok crew status swb-2
has "$out" "swb-2-$busy still holds fmt-busy, which has left swb-2's bolt: its agent is working; it is freed once that settles"
has "$out" "fmt-busy  left"
expect_fail "is working; add --force to end it anyway" crew unit free fmt-busy --team swb-2
expect_ok crew rebuild swb-2
has "$out" "swb-2-$busy is free: fmt-busy has left swb-2's bolt"
eq "$(awk NF "$slots2")" ""
ok "rebuild ends the agent of a unit that left the bolt and frees its slot"

expect_ok crew rebuild swb-1
lacks "$out" "is free"
eq "$(held follows-the-shell)" "unit-2"
ok "rebuild keeps the slot of a unit still in the team's bolt"
