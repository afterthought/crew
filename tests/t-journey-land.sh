# A bolt carried onto main and landed, through the crew command on the stubs (tests.11, record 0022), a part of the units
# journey (t-journey-units): when the landing's rebase onto main conflicts, a fix carries the bolt onto main, becomes its
# head with no merge stage and the kit's post-merge hooks run on it; the bolt lands once every unit has, recording the
# commit main holds and removing its worktree, and its conductor is told which cards to close; a bolt no team holds
# lands once its unit's change is on main; and dropping a held bolt removes its worktree and places.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world '[unit(u, "tenant-environments") for u in "abe"]; unit("c", "console-pages")
p.insert(plan.Rec("Bolt", [("Bolt", "console-pages"), ("Repo", "switchboard-kit"), ("Goal", "The console lists them.")]))'
# a's change merged into the bolt by hand, as worktrunk merges it, its place and branch gone; b built in a slot; c placed in console-pages.
pa=$(place "$k" tenant-environments a); change "$pa" a 1 1; commit_all "$pa" "feat(a): its change, done"
git -C "$bolt" merge -q --ff-only unit/a; git -C "$k" worktree remove "$pa"; git -C "$k" branch -qD unit/a
CREW_AGENT=swb-1-conductor crew unit run b construct >/dev/null
crew bolt give swb-2 console-pages >/dev/null 2>&1; place "$k" console-pages c >/dev/null
# The landing's rebase onto main conflicts on README.md, and a fix carries the bolt onto main: the bolt's commits
# replayed there with the conflict resolved. crew moves the bolt's branch to the fix's head and runs the kit's
# post-merge hooks on it, approved on the box.
echo "# switchboard-kit, the bolt's" > "$bolt/README.md"; commit_all "$bolt" "docs: the bolt's title"
mkdir -p "$k/.config"; printf '[post-merge]\nmark = "echo {{ target }} $(git rev-parse HEAD) > %s/hook-ran"\n' "$T" > "$k/.config/wt.toml"
echo "# switchboard-kit, main's" > "$k/README.md"; commit_all "$k" "docs: main's title, and a post-merge hook"
as $box bash -c 'cd "$1" && wt config approvals add --yes >/dev/null 2>&1' _ "$k" || fail "wt config approvals add failed"
n=$(git -C "$k" rev-list --count main..bolt/tenant-environments)
cm=fix/tenant-environments/carry-main cmp=$kd/places/fix-tenant-environments--carry-main
export CREW_AGENT=swb-1-conductor
expect_ok crew fix swb-1 carry-main "Carry the bolt onto main: the landing stopped on README.md."
git -C "$cmp" rebase main >/dev/null 2>&1 && fail "the replay did not stop on the title"
echo "# switchboard-kit, main's and the bolt's" > "$cmp/README.md"; git -C "$cmp" add README.md
GIT_EDITOR=true GIT_COMMITTER_DATE=$(ago -1) git -C "$cmp" rebase --continue >/dev/null 2>&1 || fail "the replay did not finish"
old=$(git -C "$k" rev-parse bolt/tenant-environments) new=$(git -C "$k" rev-parse "$cm")
: > "$CREW_TEST_LOG"
expect_ok crew fix swb-1 carry-main --merge
has "$out" "bolt/tenant-environments moved from ${old:0:7} to ${new:0:7}: $cm carries the bolt's $n commits onto main (1 changed by the resolution)"
has "$out" "the bolt's checks are running on ${new:0:7}; prove the bolt again before it lands"
eq "$(git -C "$bolt" rev-parse HEAD)" "$new"
until_ok test -s "$T/hook-ran" || fail "the post-merge hook never ran"
eq "$(cat "$T/hook-ran")" "bolt/tenant-environments $new"
has "$(field $box fix.carry From "$cm")" "agent/swb-1-unit-"
grep -q "agent prompt .* 'Merge $cm" "$CREW_TEST_LOG" && fail "a carrying fix was sent a merge prompt"
has "$out" "is free: $cm has merged into its bolt"
has "$out" "$cmp and $cm are removed; the branch was at"
ok "a fix that carries the bolt onto main becomes its head, with no merge stage, and the kit's post-merge hooks run on it; the read after frees it, and removes a merged place once its stray file goes"

# The bolt lands once its units have: b and e are dropped, and a's change reaches main.
unset CREW_AGENT
expect_fail "unit a has not landed on main: it is merged" crew bolt land tenant-environments
by_hand 'p.remove(p.unit("e"))'
expect_ok crew unit drop b "folded into a"
has "$out" "swb-1-unit-1 is free: b was dropped from the plan"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1"
git -C "$k" merge -q --ff-only bolt/tenant-environments
: > "$CREW_TEST_LOG"
expect_ok crew bolt land tenant-environments
has "$out" "tenant-environments has landed at switchboard-kit's $(git -C "$k" rev-parse --short=7 main) and swb-1 holds no bolt"
has "$out" "$bolt and bolt/tenant-environments are removed; the branch was at"
grep -qF "agent prompt swb-1-conductor '[crew] plan(tenant-environments): land the bolt ($me@mac-studio). Close any Pending You card you have open for verify/a or land/tenant-environments.'" \
  "$CREW_TEST_LOG" || fail "the conductor was not told to close its cards:"$'\n'"$(calls)"
eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -c)" "0"
git -C "$k" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "bolt/tenant-environments is still there"
eq "$(field mac-studio bolt.land On) $(field mac-studio bolt.land Commit)" "bolt/tenant-environments unit/a WilldanGroup/crew-state@$(git --git-dir "$ws" rev-parse wldn/main)"
eq "$(field mac-studio bolt.land Repo) $(field mac-studio bolt.land Head)" "switchboard-kit $(git -C "$k" rev-parse main)"
ok "a drop frees the last slot and closes the units workspace; the bolt lands once every unit has, recording the commit main holds, removing its worktree and what is over, and its conductor is told which cards to close"

# A bolt built outside a team: no team holds it, and it lands once its unit's change is on the kit's main.
crew bolt new done-outside "Built outside a team." --repo switchboard-kit >/dev/null
crew unit add done-x "Unit done-x." --bolt done-outside >/dev/null
expect_fail "unit done-x has not landed on main: it is ready" crew bolt land done-outside
mkdir -p "$k/openspec/changes/archive/2026-10-12-done-x"; echo "# done-x" > "$k/openspec/changes/archive/2026-10-12-done-x/proposal.md"
commit_all "$k" "chore(openspec): archive done-x"
expect_ok crew bolt land done-outside
eq "$(tail -1 <<<"$out")" "done-outside has landed at switchboard-kit's $(git -C "$k" rev-parse main | cut -c1-7); no team held it"
eq "$(field mac-studio bolt.land Head bolt/done-outside) $(plan -t Bolt -e "Bolt = 'done-outside'" -c)" "$(git -C "$k" rev-parse main) 0"
ok "a bolt no team holds lands once its unit's change is on its kit's main, recording the commit main holds"

expect_ok crew bolt drop console-pages "the portal lists them"
has "$out" "$kd/bolts/console-pages and bolt/console-pages are removed; the branch was at"
has "$out" "$kd/places/c and unit/c are removed; the branch was at"
eq "$(git --git-dir "$ws" log -1 --format=%b wldn/main | head -1)" "the portal lists them"
ok "dropping a held bolt removes its worktree and its units' places, with the reason in the commit"
