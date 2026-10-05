# crew unit add|split|order|after|move|drop|approve, and each scenario of the bolt-plan spec they answer.
. "$TESTS/lib.sh"
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
ws=$(remote WilldanGroup/crew-state)
k=$(kit chuck-herdr-alpha willdan switchboard-kit); kd=$(dirname "$k")
crew state init wldn >/dev/null
plan() { git --git-dir "$ws" show wldn/main:plan.rec > "$T/plan.rec"; recsel -C "$@" "$T/plan.rec"; }
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
crew bolt new apex-zones "Apexes are zones." --repo switchboard-kit >/dev/null
crew bolt give swb-1 tenant-environments >/dev/null 2>&1; crew bolt give swb-2 console-pages >/dev/null 2>&1

crew unit add a "Unit a." --bolt tenant-environments --source books/x.md >/dev/null 2>&1
crew unit add b "Unit b." --bolt tenant-environments --after a >/dev/null 2>&1
crew unit add c "Unit c." --bolt tenant-environments >/dev/null 2>&1
expect_ok crew unit add d "Unit d." --bolt tenant-environments --before b
has "$out" "plan(tenant-environments): add d ($me@mac-studio)"
eq "$(plan -t Unit -P Unit)" $'a\nd\nb\nc'
change "$k" taken; commit_all "$k" "feat: taken"
expect_fail "switchboard-kit's main already has a change named taken" crew unit add taken "x" --bolt tenant-environments
expect_fail "wldn/main already has unit a" crew unit add a "again" --bolt tenant-environments
expect_ok crew unit add later "Later work." --repo switchboard-kit
eq "$(plan -t Unit -e "Unit = 'later'" -P Bolt)" ""
ok "add puts a unit at the end of its bolt or before a named one, or in its repo's queue"

expect_ok crew unit after c a; eq "$(plan -t Unit -e "Unit = 'c'" -P After)" "a"
expect_fail "cycle" crew unit after a c
crew unit add elsewhere "Elsewhere." --bolt console-pages >/dev/null 2>&1
expect_fail "comes after elsewhere, which is in console-pages, not tenant-environments" crew unit after c elsewhere
expect_ok crew unit after c --none; eq "$(plan -t Unit -e "Unit = 'c'" -P After)" ""
ok "after sets and clears a dependency, refusing a cycle or a unit of another bolt"

expect_ok crew unit order c --first; eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -P Unit)" $'c\na\nd\nb'
expect_ok crew unit order c --before b; eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -P Unit)" $'a\nd\nc\nb'
expect_ok crew unit order a --last; eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -P Unit)" $'d\nc\nb\na'
expect_fail "is not in tenant-environments with a" crew unit order a --before elsewhere
ok "order moves a unit within its bolt"

pa=$(place "$k" tenant-environments a); change "$pa" a 1 3; commit_all "$pa" "feat(a): change, one task done"
eq "$(stage a)" "code"; eq "$(stage b)" "waiting"
ok "a unit after one in code is waiting"

expect_fail "unit a is in code, so it is no longer split; add the remainder as a new unit instead" crew unit split a "Narrower." --into a-rest "The rest."
expect_ok crew unit split c "Unit c, narrowed." --into c-rest "The rest of c." --into c-more "More of c."
eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -P Unit)" $'d\nc\nc-rest\nc-more\nb\na'
eq "$(plan -t Unit -e "Unit = 'c'" -P Intent)" "Unit c, narrowed."
ok "split narrows a unit and adds the remainder right after it, and is refused once the unit is in code"

pd=$(place "$k" tenant-environments d); mkdir -p "$pd/openspec/changes/d"; printf '# Proposal\n\n## Why\n\nx\n' > "$pd/openspec/changes/d/proposal.md"
commit_all "$pd" "docs(d): proposal"
eq "$(stage d)" "construct"
expect_fail "its change's planning is not complete" crew unit approve d
pc=$(place "$k" tenant-environments c); change "$pc" c 0 2; commit_all "$pc" "docs(c): the change"
eq "$(stage c)" "review"
expect_ok crew unit approve c; has "$out" "unit c approved"
eq "$(git -C "$pc" log -1 --format=%s)" "review(c): approved"
has "$(git -C "$pc" log -1 --format='%(trailers:key=Reviewed-by,valueonly)')" "Test User <test@example.com>"
eq "$(git -C "$pc" diff HEAD~1 --stat)" ""
eq "$(stage c)" "approved"
ok "approve is an empty Reviewed-by commit, refused before planning is complete"

# The bolt moves on, and the approved unit is rebased onto it.
echo more > "$kd/bolts/tenant-environments/bolt-work"; commit_all "$kd/bolts/tenant-environments" "feat: bolt work"
git -C "$pc" rebase -q bolt/tenant-environments
git -C "$pc" merge-base --is-ancestor bolt/tenant-environments unit/c || fail "c was not rebased"
eq "$(stage c)" "approved"
ok "the approval survives a rebase onto a newer bolt tip"

expect_fail "a queued unit has none" crew unit move c queue
expect_fail "bolt apex-zones is held by no team, so it has no branch to rebase c onto" crew unit move c apex-zones
expect_ok crew unit move c console-pages
has "$out" "plan(console-pages): move c from tenant-environments"
eq "$(plan -t Unit -e "Unit = 'c'" -P Bolt)" "console-pages"
git -C "$pc" merge-base --is-ancestor bolt/console-pages unit/c || fail "c was not rebased onto console-pages"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/c)" "bolt/console-pages"
git -C "$k" merge-base --is-ancestor bolt/tenant-environments unit/c && fail "c still carries tenant-environments' commits"
eq "$(stage c)" "approved"
ok "moving a unit with a worktree rebases its branch onto the new bolt, approval and all"

echo d > "$pd/same-file"; commit_all "$pd" "feat(d): same file"
echo console > "$kd/bolts/console-pages/same-file"; commit_all "$kd/bolts/console-pages" "feat: same file, otherwise"
dtip=$(git -C "$k" rev-parse unit/d)
expect_fail "rebasing d onto bolt/console-pages conflicts: the move is abandoned and the plan is unchanged" crew unit move d console-pages
eq "$(plan -t Unit -e "Unit = 'd'" -P Bolt)" "tenant-environments"; eq "$(git -C "$k" rev-parse unit/d)" "$dtip"
git -C "$pd" status --porcelain | grep -q . && fail "d's worktree was left mid-rebase"
ok "a rebase conflict aborts the move and leaves the plan unchanged"

expect_ok crew unit move b apex-zones; eq "$(plan -t Unit -e "Unit = 'b'" -P Bolt)" "apex-zones"; eq "$(plan -t Unit -e "Unit = 'b'" -P After)" ""
expect_ok crew unit move later tenant-environments; eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -P Unit | tail -1)" "later"
expect_fail "is already in tenant-environments" crew unit move later tenant-environments
ok "a unit with no worktree moves to the end of any bolt of its repo, or to the queue"

# Merged work: the bolt holds the unit's change.
crew unit add e "Unit e." --bolt tenant-environments >/dev/null 2>&1
change "$kd/bolts/tenant-environments" e 2 2; commit_all "$kd/bolts/tenant-environments" "feat(e): merged"
eq "$(stage e)" "merged"
expect_fail "unit e has merged into its bolt, so it can't be dropped" crew unit drop e "not wanted"
expect_fail "unit e has merged into tenant-environments, so it can't move" crew unit move e console-pages
expect_fail "unit e is in merged" crew unit split e "x" --into e2 "y"
crew unit after later e >/dev/null 2>&1
expect_ok crew unit drop d "the portal shows them; no console page is wanted"
has "$out" "$kd/places/d and unit/d are removed; the branch was at"
[[ ! -d $kd/places/d ]] || fail "d's worktree is still there"
eq "$(git --git-dir "$ws" log -1 --format=%b wldn/main | head -1)" "the portal shows them; no console page is wanted"
eq "$(plan -t Unit -e "Unit = 'd'" -c)" "0"
ok "drop removes a unit with the reason in the commit, and its worktree and branch, and refuses merged work"
