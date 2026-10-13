# A bolt landed through sluice, through the crew command on the stubs (tests.11, record 0022), a part of the units
# journey (t-journey-units): a unit merges into the bolt by a submission, and crew bolts reads the bolt's verification
# from sluice's verdict on it; crew bolt submit lands the bolt by a submission to main from a short-lived worktree,
# naming a conflict for the team and moving nothing; a fix takes main into the bolt by a submission to the bolt, and
# the landing then lands, bringing the kit's main checkout level; the bolt lands in the plan once every unit has,
# recording the commit main holds and removing its branch, and its conductor is told which cards to close; a bolt no
# team holds lands once its unit's change is on main; and dropping a held bolt removes its branch and places.
# Whether each stage may start, what it delivers, what its prompt says and every other decision on the way are logic
# cases (tests/py/); how git and worktrunk behave for them, contract cases (tests/contract/). Each step checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world '[unit(u, "tenant-environments") for u in "abe"]; unit("c", "console-pages")
p.insert(plan.Rec("Bolt", [("Bolt", "console-pages"), ("Repo", "switchboard-kit"), ("Goal", "The console lists them.")]))'
# a's change merged into the bolt by its submission, as its merge stage runs it, its place and branch gone; b built in a
# slot; c placed in console-pages. The bolt and main each change the title.
pa=$(place "$k" tenant-environments a); change "$pa" a 1 1; commit_all "$pa" "feat(a): its change, done"
echo "# switchboard-kit, the bolt's" > "$pa/README.md"; commit_all "$pa" "docs(a): the bolt's title"
(cd "$pa" && SLUICE_AGENT=swb-1-unit-1 wt submit bolt/tenant-environments --no-remove >/dev/null 2>&1) || fail "a's submission failed"
git -C "$k" worktree remove "$pa"; git -C "$k" branch -qD unit/a
CREW_AGENT=swb-1-conductor crew unit run b construct >/dev/null
crew bolt give swb-2 console-pages >/dev/null 2>&1; place "$k" console-pages c >/dev/null
echo "# switchboard-kit, main's" > "$k/README.md"; commit_all "$k" "docs: main's title"
expect_ok crew bolts --label wldn
has "$out" "verification: green, sluice's verdict on its last landing, $(short bolt/tenant-environments): passed (stub)"
ok "a unit merges into the bolt by a submission, and crew bolts reads the bolt's verification from sluice's verdict on it"

# The bolt lands once its units have: b and e are dropped, and the bolt submitted to main, which conflicts on the title.
expect_fail "unit a has not landed on main: it is merged" crew bolt land tenant-environments
by_hand 'p.remove(p.unit("e"))'
expect_ok crew unit drop b "folded into a"
has "$out" "swb-1-unit-1 is free: b was dropped from the plan"
eq "$(herdr_state $box wldn-1 '[.workspaces[].label] | join(",")')" "swb-1"
main_before=$(git -C "$k" rev-parse main) land=$kd/places/land-tenant-environments
: > "$CREW_TEST_LOG"
expect_fail "bolt/tenant-environments did not land: sluice refused it or found a conflict, and main is where it was" crew bolt submit tenant-environments
has "$out" "sluice: bolt/tenant-environments conflicts with main"
eq "$(calls | grep "^$box wt submit ")" "$box wt submit main --no-remove from $land as $me@mac-studio"
eq "$(git -C "$k" rev-parse main)" "$main_before"
[[ ! -e $land ]] || fail "the landing's worktree is still there"
ok "crew bolt submit lands a bolt by a submission to main from a short-lived worktree, and a conflict lands nothing and is named for the team"

# The team takes main into the bolt: a fix merges main in its place, resolving the title, and submits to the bolt.
tm=fix/tenant-environments/take-main tmp=$kd/places/fix-tenant-environments--take-main
export CREW_AGENT=swb-1-conductor
expect_ok crew fix swb-1 take-main "Take main into the bolt: the landing conflicts on README.md."
git -C "$tmp" merge -q main >/dev/null 2>&1 && fail "taking main did not stop on the title"
echo "# switchboard-kit, main's and the bolt's" > "$tmp/README.md"; git -C "$tmp" add README.md
GIT_EDITOR=true git -C "$tmp" commit -q --no-edit || fail "the merge of main did not commit"
expect_ok crew fix swb-1 take-main --wait
expect_ok crew fix swb-1 take-main --merge
(cd "$tmp" && SLUICE_AGENT=swb-1-unit-1 wt submit bolt/tenant-environments --no-remove >/dev/null 2>&1) || fail "the fix's submission failed"
expect_ok crew fix swb-1 take-main --wait
has "$out" "delivered merge of $tm: bolt/tenant-environments holds it at $(short bolt/tenant-environments)"
unset CREW_AGENT
expect_ok crew bolt submit tenant-environments
has "$out" "bolt/tenant-environments landed on switchboard-kit's main at $(short main): push main, then crew bolt land tenant-environments."
eq "$(git -C "$k" log -1 --format='%an %P' main)" "sluice $main_before $(git -C "$k" rev-parse bolt/tenant-environments)"
eq "$(cat "$k/README.md")" "# switchboard-kit, main's and the bolt's"
eq "$(git -C "$k" status --porcelain)" ""
[[ ! -e $land ]] || fail "the landing's worktree is still there"
eq "$(field mac-studio bolt.submit On)" "bolt/tenant-environments"
ok "a fix takes main into the bolt by a submission to the bolt; the landing then lands, its worktree removed and the kit's main checkout brought level"

: > "$CREW_TEST_LOG"
expect_ok crew bolt land tenant-environments
has "$out" "tenant-environments has landed at switchboard-kit's $(git -C "$k" rev-parse --short=7 main) and swb-1 holds no bolt"
has "$out" "bolt/tenant-environments is removed: bolt tenant-environments is in no plan; it was at"
grep -qF "agent prompt swb-1-conductor '[crew] plan(tenant-environments): land the bolt ($me@mac-studio). Close any Pending You card you have open for land/tenant-environments.'" \
  "$CREW_TEST_LOG" || fail "the conductor was not told to close its cards:"$'\n'"$(calls)"
eq "$(plan -t Unit -e "Bolt = 'tenant-environments'" -c)" "0"
git -C "$k" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "bolt/tenant-environments is still there"
eq "$(field mac-studio bolt.land On) $(field mac-studio bolt.land Commit)" "bolt/tenant-environments unit/a WilldanGroup/crew-state@$(git --git-dir "$ws" rev-parse wldn/main)"
eq "$(field mac-studio bolt.land Repo) $(field mac-studio bolt.land Head)" "switchboard-kit $(git -C "$k" rev-parse main)"
ok "a drop frees the last slot and closes the units workspace; the bolt lands once every unit has, recording the commit main holds, removing its branch and what is over, and its conductor is told which cards to close"

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
has "$out" "bolt/console-pages is removed: bolt console-pages is in no plan; it was at"
has "$out" "$kd/places/c and unit/c are removed; the branch was at"
eq "$(git --git-dir "$ws" log -1 --format=%b wldn/main | head -1)" "the portal lists them"
ok "dropping a held bolt removes its branch and its units' places, with the reason in the commit"
