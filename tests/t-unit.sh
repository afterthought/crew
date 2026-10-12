# crew unit add|split|order|after|move|drop wired through the command: the commit a write makes, a unit's stage read from
# its place, a move that rebases a unit's branch, and a drop that removes its place. What each command does to the
# plan, and every refusal it makes there, are logic cases (tests/py/test_unit_commands.py).
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
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
expect_ok crew unit add later "Later work." --repo switchboard-kit
eq "$(plan -t Unit -e "Unit = 'later'" -P Bolt)" ""
ok "add puts a unit at the end of its bolt or before a named one, or in its repo's queue"

pa=$(place "$k" tenant-environments a); mkdir -p "$pa/openspec/changes/a"; printf '# Proposal\n\n## Why\n\nx\n' > "$pa/openspec/changes/a/proposal.md"
commit_all "$pa" "docs(a): proposal"
eq "$(stage a)" "construct"; eq "$(stage b)" "waiting"
change "$pa" a 0 3; commit_all "$pa" "docs(a): the change"
eq "$(stage a)" "planned"; eq "$(stage b)" "ready"
rewrite "$pa/openspec/changes/a/tasks.md" 's/- \[ \] 1.1/- [x] 1.1/'; commit_all "$pa" "feat(a): one task done"
eq "$(stage a)" "code"; eq "$(stage b)" "ready"
ok "a unit after one still in construct is waiting, and ready once that one's change is committed, never waiting on its merge"

pd=$(place "$k" tenant-environments d); mkdir -p "$pd/openspec/changes/d"; printf '# Proposal\n\n## Why\n\nx\n' > "$pd/openspec/changes/d/proposal.md"
commit_all "$pd" "docs(d): proposal"
eq "$(stage d)" "construct"
pc=$(place "$k" tenant-environments c); change "$pc" c 0 2; commit_all "$pc" "docs(c): the change"
eq "$(stage c)" "planned"
expect_fail "invalid choice: 'approve'" crew unit approve c
ok "a unit whose change's planning is complete is planned, and one whose isn't is in construct; there is no approval to give"

# The bolt moves on, and the planned unit is rebased onto it.
echo more > "$kd/bolts/tenant-environments/bolt-work"; commit_all "$kd/bolts/tenant-environments" "feat: bolt work"
git -C "$pc" rebase -q bolt/tenant-environments
git -C "$pc" merge-base --is-ancestor bolt/tenant-environments unit/c || fail "c was not rebased"
eq "$(stage c)" "planned"
ok "a planned unit is still planned after a rebase onto a newer bolt tip"

expect_ok crew unit move c console-pages
has "$out" "plan(console-pages): move c from tenant-environments"
eq "$(plan -t Unit -e "Unit = 'c'" -P Bolt)" "console-pages"
git -C "$pc" merge-base --is-ancestor bolt/console-pages unit/c || fail "c was not rebased onto console-pages"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/unit/c)" "bolt/console-pages"
git -C "$k" merge-base --is-ancestor bolt/tenant-environments unit/c && fail "c still carries tenant-environments' commits"
eq "$(stage c)" "planned"
ok "moving a unit with a worktree rebases its branch onto the new bolt"

echo d > "$pd/same-file"; commit_all "$pd" "feat(d): same file"
echo console > "$kd/bolts/console-pages/same-file"; commit_all "$kd/bolts/console-pages" "feat: same file, otherwise"
dtip=$(git -C "$k" rev-parse unit/d)
expect_fail "rebasing d onto bolt/console-pages conflicts: the move is abandoned and the plan is unchanged" crew unit move d console-pages
eq "$(plan -t Unit -e "Unit = 'd'" -P Bolt)" "tenant-environments"; eq "$(git -C "$k" rev-parse unit/d)" "$dtip"
git -C "$pd" status --porcelain | grep -q . && fail "d's worktree was left mid-rebase"
ok "a rebase conflict aborts the move and leaves the plan unchanged"

expect_ok crew unit drop d "the portal shows them; no console page is wanted"
has "$out" "$kd/places/d and unit/d are removed; the branch was at"
[[ ! -d $kd/places/d ]] || fail "d's worktree is still there"
eq "$(git --git-dir "$ws" log -1 --format=%b wldn/main | head -1)" "the portal shows them; no console page is wanted"
eq "$(plan -t Unit -e "Unit = 'd'" -c)" "0"
ok "drop removes a unit with the reason in the commit, and its worktree and branch"
