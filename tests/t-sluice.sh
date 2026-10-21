# A kit merges and lands only through sluice (teams.5, record 0026): crew gives a bolt only in a kit whose
# .config/sluice.toml on main names the checks its bolt branches require, refusing, with the plan unchanged and no
# branch made, a kit with no policy or one naming no bolt branch checks, naming the file; and a unit's and a fix's merge
# stage submits with sluice submit bolt/<bolt> --no-wait, waited on with sluice wait; and crew's own policy requires its check-full tasks of a bolt and of main,
# run open on the host and taking no replay (tests.5, tests.10). Each scenario of the bolt-teams spec on merging; which table and checks a
# policy names for a bolt branch is a logic case (tests/py/test_kit.py), and that the policy is read from main's
# commit, a contract case (tests/contract/test_git.py).
# Reads: plugin/hooks/ .config/sluice.toml
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
held() { git --git-dir "$(remote WilldanGroup/crew-state)" show wldn/main:plan.rec | recsel -t Bolt -e "Bolt = 'tenant-environments'" -P Team; }

git -C "$k" rm -q .config/sluice.toml; commit_all "$k" "chore: no policy"
expect_fail "switchboard-kit merges only through sluice, and has no $k/.config/sluice.toml on main" crew bolt give swb-1
mkdir -p "$k/.config"; printf '[branches.main]\nrequired = ["#check-full"]\n' > "$k/.config/sluice.toml"; commit_all "$k" "chore: a policy for main alone"
expect_fail "switchboard-kit merges only through sluice, and its $k/.config/sluice.toml names no checks for its bolt branches" crew bolt give swb-1
eq "$(held)" ""
git -C "$k" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "a refused give made the bolt's branch"
ok "a bolt is given only in a kit whose policy on main names its bolt branches' checks, a refusal naming the file and changing nothing"

printf '[branches."bolt/*"]\nrequired = ["#check-full"]\n' >> "$k/.config/sluice.toml"; commit_all "$k" "chore: a policy for bolts"
expect_ok crew bolt give swb-1
eq "$(held)" "swb-1"
export CREW_AGENT=swb-1-conductor
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | grep -v "/exit" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
crew unit run a construct >/dev/null; change "$kd/places/a" a 2 2; commit_all "$kd/places/a" "feat(a): done"
expect_ok crew unit run a merge
eq "$(prompt_to swb-1-unit-1)" "'Merge a into bolt/tenant-environments: sluice submit bolt/tenant-environments --no-wait --json'"
crew fix swb-1 edge-sign-in "The edge sign-in answers an object." >/dev/null
fp=$kd/places/fix-tenant-environments--edge-sign-in
echo fixed > "$fp/sign-in"; commit_all "$fp" "fix: the edge sign-in answers a string"
: > "$CREW_TEST_LOG"
expect_ok crew fix swb-1 edge-sign-in --merge
grep -q "agent prompt .* 'Merge fix/tenant-environments/edge-sign-in into bolt/tenant-environments: sluice submit bolt/tenant-environments --no-wait --json'" "$CREW_TEST_LOG" \
  || fail "the fix was not submitted:"$'\n'"$(calls)"
ok "a unit's and a fix's merge into the bolt is a submission, sluice submit bolt/<bolt> --no-wait"

policy() { python3 -c 'import sys, tomllib; sys.path.insert(0, sys.argv[1]); import kit
text = open(sys.argv[2]).read(); b = tomllib.loads(text)["branches"]
print(tomllib.loads(text)["executor"]["kind"], kit.bolt_checks(text, "crew"), b["main"]["required"], b["bolt/*"]["trust"], b["main"]["trust"])' "$CREW/plugin/lib" "$CREW/.config/sluice.toml"; }
eq "$(policy)" "open ['#check-full'] ['#check-full'] ['open'] ['open']"
ok "crew's own policy requires its check-full tasks of a bolt and of main, run open on the host, and takes no replay"
