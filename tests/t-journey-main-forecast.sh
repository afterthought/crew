# The bolt forecast against its kit's main on each conductor's wait, through the crew command on the stubs (tests.11,
# record 0022), a part of the units journey (t-journey-units): with a sluice that can't forecast a branch no worktree
# holds, the wait says so once for the bolt's head; with one that can, a conflict with what main has landed is said once,
# with the take-main fix to start now, and one with a submission queued on main as one to wait out (teams.19, record
# 0036). What each forecast says and when it is said again are logic cases (tests/py/test_forecast.py); this checks the
# command's wiring once.
# Reads: plugin/hooks/ tests/units.sh
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
. "$TESTS/units.sh"
units_world 'unit("a", "tenant-environments")'
export CREW_AGENT=swb-1-conductor
crew unit run a construct >/dev/null
bolt=$(git -C "$k" rev-parse bolt/tenant-environments)
check=$T/sluice-check-bolt-tenant-environments.json
rm "$check"  # this host's sluice has no forecast of a branch, until the part below gives it one

: > "$CREW_TEST_LOG"
expect_ok crew unit wait a --timeout 0
has "$out" "no forecast of bolt/tenant-environments against main: this host's sluice can't forecast a branch no worktree holds (sluice submit --check --head), which a newer sluice can"
has "$(calls)" "$box sluice submit main --check --head bolt/tenant-environments --json in $(cd "$k" && pwd -P)"
eq "$(field $box forecast Heads bolt/tenant-environments)" "bolt/tenant-environments@${bolt:0:7}"
expect_ok crew unit wait a --timeout 0
lacks "$out" "no forecast of bolt/tenant-environments"
ok "a wait whose sluice can't forecast the bolt against main says so once for the bolt's head"

main=$(git -C "$k" rev-parse main)
printf '{"conflict":{"paths":["shared.txt"],"with":[]},"head":"%s","onto":"%s","ahead":[]}\n' "$bolt" "$main" > "$check"
expect_ok crew unit wait a --timeout 0
has "$out" "bolt/tenant-environments is forecast to conflict with main on shared.txt: main has landed work on them since the bolt took it. Take main into the bolt now, while the conflict is small, by a fix as when wldn-ops says a landing conflicts: crew fix swb-1 take-main-${main:0:7} \"Take main into the bolt: it is forecast to conflict on shared.txt\""
eq "$(field $box forecast Heads bolt/tenant-environments)" "bolt/tenant-environments@${bolt:0:7} main@${main:0:7}"
eq "$(field $box forecast Reached bolt/tenant-environments)" "wait"
expect_ok crew unit wait a --timeout 0
lacks "$out" "is forecast to conflict with main"
ok "a conflict with what main has landed is said to the conductor once, with the take-main fix to start now"

printf '{"conflict":{"paths":["shared.txt"],"with":[{"id":7,"from":{"agent":"wldn-design","worktree":"design/x"}}]},"head":"%s","onto":"%s","ahead":[7]}\n' "$bolt" "$main" > "$check"
expect_ok crew unit wait a --timeout 0
has "$out" "bolt/tenant-environments is forecast to conflict on shared.txt with #7 (design/x), queued on main ahead of it. Take nothing in for it"
printf '{"conflict":null,"head":"%s","onto":"%s","ahead":[7]}\n' "$bolt" "$main" > "$check"
expect_ok crew unit wait a --timeout 0
lacks "$out" "forecast to conflict"
ok "a conflict with a submission queued on main is said as one to wait out, and a clean forecast says nothing"
