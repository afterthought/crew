# A kit opts into sluice by a flag in its config, `sluice = true` in its main checkout's .config/crew.toml: a unit's and
# a fix's merge stage then submits with wt submit bolt/<bolt>, and otherwise merges with wt merge, one at a time; a
# flag crew can't read refuses the merge, naming the file. Each scenario of the bolt-teams spec on merging.
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew bolt give swb-1 >/dev/null 2>&1
export CREW_AGENT=swb-1-conductor
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | grep -v "/exit" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
for u in a b; do crew unit run $u construct >/dev/null; change "$kd/places/$u" $u 2 2; commit_all "$kd/places/$u" "feat($u): done"; done

expect_ok crew unit run a merge
eq "$(prompt_to swb-1-unit-1)" "'Merge a into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'"
ok "a kit that has not opted into sluice merges with wt merge"

mkdir -p "$k/.config"; printf '# crew reads this kit flag\nsluice = true\n' > "$k/.config/crew.toml"; commit_all "$k" "chore: merge through sluice"
expect_ok crew unit run b merge
eq "$(prompt_to swb-1-unit-2)" "'Merge b into bolt/tenant-environments: wt submit bolt/tenant-environments'"
crew fix swb-1 edge-sign-in "The edge sign-in answers an object." >/dev/null
fp=$kd/places/fix-tenant-environments--edge-sign-in
echo fixed > "$fp/sign-in"; commit_all "$fp" "fix: the edge sign-in answers a string"
: > "$CREW_TEST_LOG"
expect_ok crew fix swb-1 edge-sign-in --merge
grep -q "agent prompt .* 'Merge fix/tenant-environments/edge-sign-in into bolt/tenant-environments: wt submit bolt/tenant-environments'" "$CREW_TEST_LOG" \
  || fail "the fix was not submitted:"$'\n'"$(calls)"
ok "a kit that opts into sluice submits a unit's and a fix's merge with wt submit"

printf 'sluice = "yes"\n' > "$k/.config/crew.toml"
expect_fail "can't tell whether switchboard-kit merges through sluice: $k/.config/crew.toml: 'sluice' is true or false, not \"yes\"" crew unit run b merge
printf 'sluice = \n' > "$k/.config/crew.toml"
expect_fail "$k/.config/crew.toml can't be read" crew unit run b merge
ok "a flag crew can't read refuses the merge, naming the file"
