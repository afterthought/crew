# A fix and the plan moving under a team, through the crew command on the stubs (tests.11, record 0022), a part of the
# units journey (t-journey-units): a fix takes a slot in its own place from the bolt, writes no plan and merges through
# sluice as a stage does; a moved unit's branch is rebased onto its new bolt; the team's reads free the slots a
# moved unit, a merged fix and a dropped unit leave, keeping a place that holds a stray file; a dropped unit's branch
# that holds a commit of its own is kept, named and recorded, and a unit added again under its name starts from it; a
# fix whose place could not be made ready starts all the same, told what failed; a fix not wanted is dropped, its
# branch kept when it holds a commit of its own, while a merged one is not; a merged fix whose place was removed by
# hand is read from its branch, its slot freed and its branch removed; and a team holding two bolts names a fix's bolt
# with --bolt.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world '[unit(u, "tenant-environments") for u in "abcd"]
p.insert(plan.Rec("Bolt", [("Bolt", "console-pages"), ("Repo", "switchboard-kit"), ("Goal", "The console lists them.")]))'
export CREW_AGENT=swb-1-conductor
for u in a b c d; do crew unit run $u construct >/dev/null; done
echo "a's own" > "$kd/places/a/own"; commit_all "$kd/places/a" "feat(a): written before the drop"; aat=$(short unit/a)
CREW_AGENT= expect_ok crew unit drop a "not this one"; mkdir -p "$reports"
has "$out" "$kd/places/a is removed, and unit/a is kept at $aat: unit a is in no plan, and it holds 1 commit whose patch origin/bolt/tenant-environments lacks (git cherry), the user's to keep or delete; a unit added as a starts from it"
eq "$(short unit/a)" "$aat"
eq "$(field $box branch.kept Head unit/a team/swb-1)" "$aat"
eq "$(field $box branch.kept Count unit/a)" "1"
eq "$(field $box branch.kept From unit/a)" "bolt/tenant-environments"
fb=fix/tenant-environments/tidy fp=$kd/places/fix-tenant-environments--tidy
expect_ok crew fix swb-1 tidy "The banner flickers ZQXS."
has "$out" "swb-1-unit-1 has $fb: code, in $fp"
eq "$(prompt_to swb-1-unit-1)" "'Fix: The banner flickers ZQXS.'"
eq "$(field $box fix.start On)" "$fb bolt/tenant-environments agent/swb-1-unit-1"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' "refs/heads/$fb")" "origin/bolt/tenant-environments"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $fp"
plan_tip=$(act_tip)
expect_ok crew fix swb-1 tidy "It flickers still."
has "$out" "swb-1-unit-1 has $fb: code, in $fp"
has "$(cat "$slots")" "unit-1 fix $fb $fp"
eq "$(act_tip)" "$plan_tip"
echo steady > "$fp/banner"; commit_all "$fp" "fix: the banner holds still"
expect_ok crew fix swb-1 tidy --wait
has "$out" "swb-1-unit-1 delivered fix $fb: its branch is at $(short $fb)"
expect_ok crew fix swb-1 tidy --merge
eq "$(prompt_to swb-1-unit-1)" "'Merge $fb into bolt/tenant-environments: sluice submit bolt/tenant-environments --no-wait --json'"
merge_as swb-1-unit-1 "$fp" bolt/tenant-environments || fail "the fix's submission failed"
echo stray > "$fp/note"  # a file nobody committed, which keeps the merged fix's place
expect_ok crew fix swb-1 tidy --wait
has "$out" "swb-1-unit-1 delivered merge of $fb: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
# The merge's wait frees the slot as it lands, and removes the place and branch but for the stray file.
has "$out" "swb-1-unit-1 is free: $fb has merged into its bolt"
has "$out" "$fp is kept, and $fb with it: $fb has merged into bolt/tenant-environments, and it has uncommitted changes, which are the user's to keep or discard"
expect_fail "$fb has merged into bolt/tenant-environments, so it is not dropped" crew fix swb-1 tidy --drop
has "$(field $box fix.drop Refused "$fb")" "so it is not dropped"
[[ $(record_of $box) != *ZQXS* ]] || fail "a fix's words are in the run record"
ok "a fix takes a slot in its own place from the bolt and writes no plan, starts again there, ends at its commit, merges through sluice as a stage does and ends once the bolt holds it, its slot freed as it lands, and is not dropped then"

# The user moves c to another team's bolt and drops d while its agent works, with the merged fix's place holding a file
# nobody committed: the reads that follow free each slot once its agent settles, remove d's place, and keep the fix's.
unset CREW_AGENT
expect_ok crew bolt give swb-2 console-pages
said=$out
expect_ok crew unit move c console-pages
has "$out" "plan(console-pages): move c from tenant-environments"
said+=$'\n'$out
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/c)" "origin/bolt/console-pages"
git -C "$k" merge-base --is-ancestor bolt/console-pages unit/c || fail "c was not rebased onto console-pages"
status swb-1-unit-4 working
expect_ok crew unit drop d "not wanted"
has "$out" "swb-1-unit-4 still holds d, dropped from the plan: its agent is working; it is freed once that settles"
said+=$'\n'$out
[[ -d $kd/places/d ]] || fail "d's place went with its agent working"
expect_fail "is working; add --force to end it anyway" crew unit free d --team swb-1
status swb-1-unit-4 idle
echo "d's own" > "$kd/places/d/own"; commit_all "$kd/places/d" "feat(d): its own"; dat=$(short unit/d)
HOST=$box expect_ok crew unit free d
has "$out" "swb-1-unit-4 is free"
has "$out" "$kd/places/d is removed, and unit/d is kept at $dat: unit d is in no plan, and it holds 1 commit whose patch origin/bolt/tenant-environments lacks (git cherry)"
eq "$(field $box branch.kept Head unit/d)" "$dat"
export CREW_AGENT=swb-1-conductor
expect_ok crew status swb-1
said+=$'\n'$out
has "$said" "swb-1-unit-3 is free: c has left swb-1's bolt"
has "$said" "$fp is kept, and $fb with it: $fb has merged into bolt/tenant-environments, and it has uncommitted changes, which are the user's to keep or discard"
[[ -d $kd/places/c ]] || fail "c's place went with the slot it left"
[[ -d $fp ]] || fail "the fix's place went with its stray file"
eq "$(awk '{print $1, $3}' "$slots")" "unit-2 b"
rm "$fp/note"
ok "a moved unit's branch is rebased onto its new bolt; the team's reads free the slot it left and a merged fix's, keeping a merged place holding a stray file, and crew unit free a dropped unit's once its agent settles, keeping and naming its branch holding a commit of its own"

# A bolt whose own toolchain fails: a fix's agent starts in its place all the same, told the step that failed, since a
# fix is how the bolt is repaired (teams.3, record 0028).
touch "$T/moon-fails"
xf=fix/tenant-environments/repair xp=$kd/places/fix-tenant-environments--repair
expect_ok crew fix swb-1 repair "Take main into the bolt."
has "$out" "$xp is made but not ready: moon setup exited 1; swb-1-unit-"
xs=$(awk -v f="$xf" '$3 == f {print $1}' "$slots")
has "$(prompt_to "swb-1-$xs")" "'Fix: Take main into the bolt. Your place $xp could not be made ready, so the kit"
has "$(prompt_to "swb-1-$xs")" "moon setup exited 1"
eq "$(field $box fix.start Refused "$xf")" ""
rm "$T/moon-fails"
ok "a fix whose place could not be made ready starts all the same, its agent told what failed"

# The conductor drops the repair while its agent works, then with --force: its slot is freed and its place and branch
# go, holding nothing beyond the bolt. A fix whose branch and place stand with no slot, holding a commit of their own,
# is dropped too: its place, holding a stray file, is kept until the file goes, and its branch then kept and named
# (teams.3, plan.9, plan.10, record 0028).
status "swb-1-$xs" working
expect_fail "swb-1-$xs is working; add --force to end it anyway" crew fix swb-1 repair --drop
has "$(field $box fix.drop Refused "$xf")" "is working"
expect_ok crew fix swb-1 repair --drop --force
has "$out" "swb-1-$xs is free: $xf is dropped"
has "$out" "$xp and $xf are removed; the branch was at"
eq "$(field $box fix.drop On "$xf")" "$xf bolt/tenant-environments agent/swb-1-$xs"
[[ ! -d $xp ]] || fail "the dropped fix's place stayed"
lacks "$(cat "$slots")" "$xf"
of=fix/tenant-environments/old op=$kd/places/fix-tenant-environments--old
git -C "$k" worktree add -q --track -b "$of" "$op" bolt/tenant-environments || fail "the standing fix's place was not made"
echo kept > "$op/kept"; commit_all "$op" "fix: a commit of its own"
at=$(short "$of")
echo stray > "$op/note"
expect_ok crew fix swb-1 old --drop
has "$out" "$op is kept, and $of with it: $of was dropped, and it has uncommitted changes"
rm "$op/note"
expect_ok crew status swb-1
has "$out" "$op is removed, and $of is kept at $at: it was dropped, and it holds 1 commit whose patch bolt/tenant-environments lacks"
[[ ! -d $op ]] || fail "the standing fix's place stayed"
eq "$(short "$of")" "$at"
eq "$(git -C "$k" config "branch.$of.crew")" ""
expect_fail "swb-1 has no fix fix/tenant-environments/gone: no slot, place or branch holds it" crew fix swb-1 gone --drop
ok "a fix not wanted is dropped, its slot freed and its working agent ended only with --force, its place and branch removed, a place with a stray file kept until it goes, and a branch with a commit of its own kept and named"

# A fix merged into its bolt whose place was removed by hand, its branch left, as swb-3's were on the box on 2026-10-20:
# the merge's wait, which reads the team as the merge lands, reads it merged from its branch, frees its slot and
# removes the branch (teams.1, teams.3).
gb=fix/tenant-environments/gap gp=$kd/places/fix-tenant-environments--gap
expect_ok crew fix swb-1 gap "The gap shows."
gs=swb-1-$(awk -v f="$gb" '$3 == f {print $1}' "$slots")
echo shut > "$gp/gap"; commit_all "$gp" "fix: the gap is shut"
expect_ok crew fix swb-1 gap --wait
expect_ok crew fix swb-1 gap --merge
merge_as $gs "$gp" bolt/tenant-environments || fail "the gap fix's submission failed"
at=$(short "$gb")
git -C "$k" worktree remove "$gp" || fail "the gap fix's place was not removed"
expect_ok crew fix swb-1 gap --wait
has "$out" "$gs delivered merge of $gb"
has "$out" "$gs is free: $gb has merged into its bolt"
has "$out" "$gb is removed: it has merged into bolt/tenant-environments; it was at $at"
lacks "$(cat "$slots")" "$gb"
git -C "$k" rev-parse --verify -q "refs/heads/$gb" >/dev/null && fail "the gap fix's branch stayed"
ok "a merged fix whose place was removed by hand is read from its branch: the merge's wait frees its slot and removes its branch, saying the commit it was at"

# The dropped unit a, added again under its name to another team's bolt: its place is made on the kept unit/a as it
# stood, which then tracks the new bolt, and its construct's start says so (record 0003, plan.10).
unset CREW_AGENT
crew up swb-2 >/dev/null
expect_ok crew unit add a "Unit a, again." --bolt console-pages
CREW_AGENT=swb-2-conductor expect_ok crew unit run a construct
has "$out" "$kd/places/a starts from the kept unit/a, at $aat"
eq "$(git -C "$kd/places/a" rev-parse --short HEAD)" "$aat"
eq "$(cat "$kd/places/a/own")" "a's own"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/a)" "origin/bolt/console-pages"
ok "a dropped unit's branch holding a commit of its own is kept, named and recorded, and a unit added again under its name starts from it, tracking its new bolt"

# A team holding a bolt that waits to land beside the one it builds (teams.16): a new fix naming no bolt is refused,
# naming both, and one naming its bolt with --bolt is made from that bolt.
export CREW_AGENT=swb-1-conductor
by_hand 'p.insert(plan.Rec("Bolt", [("Bolt", "ssh-fix"), ("Repo", "switchboard-kit"), ("Goal", "Hosts reach each other."), ("Team", "swb-1")]))'
git -C "$k" push -q origin main:refs/heads/bolt/ssh-fix && git -C "$k" branch -q --no-track bolt/ssh-fix main  # as sluice's branch create makes it on GitHub (plan.19)
expect_fail "swb-1 holds tenant-environments and ssh-fix: name the fix's bolt with --bolt" crew fix swb-1 edge "The edge drops a host."
sf=fix/ssh-fix/edge sp=$kd/places/fix-ssh-fix--edge
expect_ok crew fix swb-1 edge "The edge drops a host." --bolt ssh-fix
has "$out" "has $sf: code, in $sp"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' "refs/heads/$sf")" "origin/bolt/ssh-fix"
ok "a fix on a team holding two bolts names its bolt with --bolt, and one naming none is refused"
