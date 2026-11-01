# A kit merges and lands only through sluice (teams.5, record 0026): crew starts a bolt only in a kit whose
# .config/sluice.toml on GitHub's main names the checks its bolt branches require, refusing, with the plan unchanged and no
# branch made, a kit with no policy or one naming no bolt branch checks, naming the file; a unit's and a fix's place on
# a started bolt merge into it only as Flume's submissions to sluice, crew fix having no --merge since crew
# merges nothing, and crew reads each merged from the runner's records and the bolt's verification from sluice's verdict
# at its head; and crew's own policy requires its check-full tasks of a bolt and of main, run open on the host and taking
# no replay (tests.5, tests.10). Each scenario of the bolt-teams spec on merging; which table and checks a policy names
# for a bolt branch is a logic case (tests/py/test_kit.py), and that the policy is read from main's commit, a contract
# case (tests/contract/test_git.py).
# Reads: .config/sluice.toml
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
flume_world
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
held() { git --git-dir "$(remote WilldanGroup/crew-state)" show wldn/main:plan.rec | recsel -t Bolt -e "Bolt = 'tenant-environments'" -P Path; }

git -C "$k" rm -q .config/sluice.toml; commit_all "$k" "chore: no policy"; push "$k"
expect_fail "switchboard-kit merges only through sluice, and has no $k/.config/sluice.toml on origin/main" crew bolt start tenant-environments
mkdir -p "$k/.config"; printf '[branches.main]\nrequired = ["#check-full"]\nremote = "origin"\n' > "$k/.config/sluice.toml"
commit_all "$k" "chore: a policy for main alone"; push "$k"
expect_fail "switchboard-kit merges only through sluice, and its $k/.config/sluice.toml names no checks for its bolt branches" crew bolt start tenant-environments
eq "$(held)" ""
git -C "$k" rev-parse --verify -q bolt/tenant-environments >/dev/null && fail "a refused start made the bolt's branch"
ok "a bolt is started only in a kit whose policy on main names its bolt branches' checks, a refusal naming the file and changing nothing"

# fix_lands <bolt> <name> <file>: what Flume does with a launched fix once its code has delivered, as flume_lands does
# with a unit or chore: its place, cut from the bolt on GitHub, commits the fix and submits it to the bolt through
# sluice, which lands it there as a merge commit carrying its verdict; then the runner on the box carries Flume's
# status of the place, landed at the bolt's new head
fix_lands() {
  local p=$T/flume/fix--$1--$2 head
  git -C "$k" fetch -q origin
  git -C "$k" worktree add -q -b "fix/$1/$2" "$p" "origin/bolt/$1"
  git -C "$p" branch -q --set-upstream-to "origin/bolt/$1"
  echo fixed > "$p/$3"; git -C "$p" add "$3"; git -C "$p" commit -qm "fix($2): $2"
  merge_as flume "$p" "bolt/$1" || fail "fix $2's submission to bolt/$1 failed"
  git -C "$k" fetch -q origin; head=$(git -C "$k" rev-parse "origin/bolt/$1")
  git -C "$k" worktree remove --force "$p"
  runner_writes $box "$(request_of "fix/$1/$2")" "$p" "$(landed_status "$p" "$head")"
}
landed() { git --git-dir "$(remote WilldanGroup/switchboard-kit)" log -1 --format='%an %s%n%(trailers:key=Sluice-Result,valueonly)' bolt/tenant-environments | grep .; }
printf '[branches."bolt/*"]\nrequired = ["#check-full"]\nremote = "origin"\n' >> "$k/.config/sluice.toml"; commit_all "$k" "chore: a policy for bolts"; push "$k"
expect_ok crew bolt start tenant-environments
eq "$(held)" "flume"
flume_lands $box unit a tenant-environments
eq "$(landed)" $'sluice chore(land): #1 unit/a\npassed (stub)'
eq "$(stage a)" "merged"
expect_ok crew fix tenant-environments edge-sign-in "The edge sign-in answers an object."
expect_fail "unrecognized arguments: --merge" crew fix tenant-environments edge-sign-in --merge
fix_lands tenant-environments edge-sign-in sign-in
eq "$(landed)" $'sluice chore(land): #2 fix/tenant-environments/edge-sign-in\npassed (stub)'
expect_ok crew bolts tenant-environments --json
eq "$(jq -r '.partitions[0].plans[0].bolts[0] | "\(.fixes[0].fix) \(.fixes[0].merged) \(.verification.state)"' <<<"$out")" \
  "fix/tenant-environments/edge-sign-in true green"
has "$(jq -r '.partitions[0].plans[0].bolts[0].verification.said' <<<"$out")" ": passed (stub)"
ok "a unit's and a fix's merge into a started bolt is Flume's submission to sluice, crew merging nothing, and crew reads each merged and the bolt's verification from sluice's verdict at its head"

policy() { python3 -c 'import sys, tomllib; sys.path.insert(0, sys.argv[1]); import kit
text = open(sys.argv[2]).read(); b = tomllib.loads(text)["branches"]
print(tomllib.loads(text)["executor"]["kind"], kit.bolt_checks(text, "crew"), b["main"]["required"], b["bolt/*"]["trust"], b["main"]["trust"])' "$CREW/plugin/lib" "$CREW/.config/sluice.toml"; }
eq "$(policy)" "open ['#check-full'] ['#check-full'] ['open'] ['open']"
ok "crew's own policy requires its check-full tasks of a bolt and of main, run open on the host, and takes no replay"
