# The settle stage: a fresh agent in the slot of a unit that has delivered its verify and waits to merge, started from
# the coder's brief with what reached it; refused for a unit that has not delivered its verify, or with nothing said of
# what reached it. It ends at a commit on the unit's branch made since it began, or when its agent stops short saying
# nothing needs to change, and the unit then merges with no verify run again. Each scenario of the bolt-teams spec
# "A unit waiting to merge settles".
# Reads: plugin/hooks/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
for u in a b; do crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null; done
crew bolt give swb-1 >/dev/null 2>&1
export CREW_AGENT=swb-1-conductor
reports=$(home_of $box)/.local/state/swb-1-team/reports; mkdir -p "$reports"
last_launch() { tail -1 "$CREW_TEST_CLAUDE_LOG" | jq -r '([.argv | to_entries[] | select(.value == "--name") | .key][0]) as $i | "\(.argv[0:4] | join(" ")) | \(.argv[$i + 1]) | \(.cwd)"'; }
prompt_to() { grep "^$box wldn-1 agent prompt $1 " "$CREW_TEST_LOG" | grep -v "/exit" | tail -1 | sed "s/^$box wldn-1 agent prompt $1 //"; }
for u in a b; do crew unit run $u construct >/dev/null; change "$kd/places/$u" $u 1 2; commit_all "$kd/places/$u" "docs($u): the change"; crew unit wait $u >/dev/null; done

expect_fail "unit a is in code: settle runs only for a unit that has delivered its verify and waits to merge" crew unit run a settle "The bolt moved."
rewrite "$kd/places/a/openspec/changes/a/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/a" "feat(a): done"
expect_fail "unit a is in verify, and has not delivered its verify: settle runs only for a unit that has delivered its verify and waits to merge" \
  crew unit run a settle "The bolt moved."
crew unit run a verify >/dev/null; echo "# Verify a" > "$reports/verify-a-$(date +%Y%m%d-%H%M).md"
crew unit wait a >/dev/null
expect_fail "settle a with what reached it" crew unit run a settle
ok "settle is refused for a unit in code, one in verify that has not delivered its verify, and with nothing said of what reached it"

: > "$CREW_TEST_LOG"
expect_ok crew unit run a settle "Your branch is forecast to conflict with bolt/tenant-environments on x."
has "$out" "swb-1-unit-1 has a: settle, in $kd/places/a"
eq "$(last_launch)" "--model claude-opus-5-5[1m] --effort xhigh | swb-1-unit-1 | $kd/places/a"
eq "$(prompt_to swb-1-unit-1)" "'Settle a: Your branch is forecast to conflict with bolt/tenant-environments on x.'"
expect_ok crew unit wait a --stuck 0 --timeout 0
has "$out" "swb-1-unit-1 is stuck in settle on a: quiet for 0 minutes, with nothing committed since it began"
echo resolved > "$kd/places/a/x"; commit_all "$kd/places/a" "fix(a): keep both intents"
expect_ok crew unit wait a
eq "$out" "swb-1-unit-1 delivered settle on a: its branch is at $(git -C "$k" rev-parse --short unit/a), ready to merge"
expect_ok crew unit run a merge
has "$(prompt_to swb-1-unit-1)" "'Merge a into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'"
ok "a verified unit's settle starts fresh from the coder's brief with what reached it, ends at its commit, and the unit merges with no verify again"

rewrite "$kd/places/b/openspec/changes/b/tasks.md" 's/- \[ \]/- [x]/'; commit_all "$kd/places/b" "feat(b): done"
crew unit run b verify >/dev/null; echo "# Verify b" > "$reports/verify-b-$(date +%Y%m%d-%H%M).md"; crew unit wait b >/dev/null
crew unit run b settle "a's change was revised." >/dev/null
CREW_AGENT=swb-1-unit-2 expect_ok crew needs "Nothing needs to change: b already keeps both intents."
expect_ok crew unit wait b
has "$out" "settle on b has ended: swb-1-unit-2 stopped short"
expect_ok crew unit run b merge
ok "a settle whose agent says nothing needs to change ends short, and the unit goes on to merge"
