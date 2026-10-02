# crew bolts: each unit's stage derived from its kit, one host call per host holding active bolts; planned bolts
# and queued work read from the plan alone; an unreachable host's units shown as unknown, with the host named.
. "$TESTS/lib.sh"
world
wb=$(blueprints WilldanGroup/willdan-blueprints)
k=$(kit chuck-herdr-alpha willdan switchboard-kit); kd=$(dirname "$k")
ak=$(kit mac-studio willdan atlas-kit)
crew plan init WilldanGroup/willdan-blueprints wldn >/dev/null
export CREW_AGENT=wldn-planner CREW_LABEL=wldn
crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
crew bolt new apex-zones "Apexes are zones." --repo switchboard-kit >/dev/null
crew bolt new atlas-maps "Atlas draws maps." --repo atlas-kit >/dev/null
for u in landed archived squashed verifying coding approved reviewing constructing ready-one; do
  crew unit add $u "Unit $u." --bolt tenant-environments >/dev/null 2>&1
done
crew unit add waits "Unit waits." --bolt tenant-environments --after coding >/dev/null 2>&1
crew unit add later "Later." --repo switchboard-kit --source signals/x/01-y >/dev/null 2>&1
crew unit add zone-one "Zone one." --bolt apex-zones >/dev/null 2>&1
crew unit add zone-two "Zone two." --bolt apex-zones --after zone-one >/dev/null 2>&1
crew unit add map-one "Map one." --bolt atlas-maps >/dev/null 2>&1
crew bolt give swb-1 tenant-environments >/dev/null 2>&1; crew bolt give atl-1 atlas-maps >/dev/null 2>&1

change "$k" landed 3 3; mkdir -p "$k/openspec/changes/archive"; change "$k" tmp 1 1
mv "$k/openspec/changes/tmp" "$k/openspec/changes/archive/2026-09-01-archived"; commit_all "$k" "feat: two units landed"
git -C "$kd/bolts/tenant-environments" merge -q --ff-only main
# A unit merged the way the merge stage does by default: squashed by wt merge, its worktree and branch removed.
ps=$(place "$k" tenant-environments squashed); change "$ps" squashed 2 2; commit_all "$ps" "feat(squashed): one"
echo two > "$ps/two"; commit_all "$ps" "feat(squashed): two"
if command -v wt >/dev/null; then (cd "$ps" && wt merge bolt/tenant-environments --yes >/dev/null 2>&1) || fail "wt merge failed"
else git -C "$kd/bolts/tenant-environments" merge -q --squash unit/squashed && commit_all "$kd/bolts/tenant-environments" "squashed"
  git -C "$k" worktree remove "$ps" && git -C "$k" branch -qD unit/squashed; fi
for _ in $(seq 100); do [[ -d $ps ]] || break; /bin/sleep 0.1; done  # wt removes the worktree in the background
[[ ! -d $ps ]] || fail "the squashed unit's worktree is still there"
eq "$(git -C "$k" rev-list --count bolt/tenant-environments ^main)" "1"
pv=$(place "$k" tenant-environments verifying); change "$pv" verifying 3 3; commit_all "$pv" "feat(verifying)"
pc=$(place "$k" tenant-environments coding); change "$pc" coding 4 9; commit_all "$pc" "feat(coding)"
pa=$(place "$k" tenant-environments approved); change "$pa" approved 0 2; commit_all "$pa" "docs(approved)"
git -C "$pa" commit -q --allow-empty -m "review(approved): approved" --trailer "Reviewed-by: Test User"
pr=$(place "$k" tenant-environments reviewing); change "$pr" reviewing 0 2; commit_all "$pr" "docs(reviewing)"
place "$k" tenant-environments constructing >/dev/null
git -C "$k" worktree add -q --track -b fix/edge-sign-in "$kd/places/fix-edge-sign-in" bolt/tenant-environments

: > "$CREW_TEST_LOG"
expect_ok crew bolts --json; j=$out
eq "$(grep -c ' ssh chuck-herdr-alpha ' "$CREW_TEST_LOG")" "1"
st() { jq -r --arg u "$1" '[.partitions[].plans[].bolts[].units[] | select(.unit == $u) | .stage] | first' <<<"$j"; }
for pair in landed:landed archived:landed squashed:merged verifying:verify coding:code approved:approved reviewing:review \
            constructing:construct ready-one:ready waits:waiting zone-one:ready zone-two:waiting map-one:ready; do
  eq "$(st "${pair%%:*}")" "${pair#*:}"
done
eq "$(jq -r '.partitions[0].plans[0].bolts[] | select(.bolt == "tenant-environments") | "\(.team) \(.host) \(.state)"' <<<"$j")" "swb-1 chuck-herdr-alpha active"
eq "$(jq -r '.partitions[0].plans[0].bolts[] | select(.bolt == "apex-zones") | "\(.team) \(.state)"' <<<"$j")" "null planned"
eq "$(jq -r '[.partitions[0].plans[0].bolts[].units[] | select(.unit == "coding") | .tasks] | first | join("/")' <<<"$j")" "4/9"
eq "$(jq -r '.partitions[0].plans[0].bolts[0].fixes[0].fix' <<<"$j")" "fix/edge-sign-in"
eq "$(jq -r '.partitions[0].plans[0].queue[0] | "\(.unit) \(.stage) \(.repo)"' <<<"$j")" "later queued switchboard-kit"
ok "every stage is read from the kits, a squashed merge reads merged, and each host is read once"

expect_ok crew bolts
has "$out" "tenant-environments  switchboard-kit  swb-1 @ chuck-herdr-alpha  active"
has "$out" "  coding                                   code 4/9     places/coding"
has "$out" "  fix/edge-sign-in                         fix          places/fix-edge-sign-in"
has "$out" $'queue  switchboard-kit\n  later                                    queued       signals/x/01-y'
expect_ok crew bolts apex-zones; has "$out" "apex-zones  switchboard-kit  no team  planned"; lacks "$out" "tenant-environments"
ok "the text view, and one bolt alone"

# No host is reached for a planned bolt or queued work.
: > "$CREW_TEST_LOG"; expect_ok crew bolts apex-zones; eq "$(grep -c ' ssh ' "$CREW_TEST_LOG" || true)" "0"

echo chuck-herdr-alpha > "$T/down"
expect_ok crew bolts --json; j=$out
eq "$(st coding)" "unknown"; eq "$(st map-one)" "ready"
has "$(jq -r '.unreachable["chuck-herdr-alpha"]' <<<"$j")" "timed out"
eq "$(jq -r '.partitions[0].plans[0].bolts[] | select(.bolt == "tenant-environments") | .state' <<<"$j")" "unknown"
expect_ok crew bolts; has "$out" "chuck-herdr-alpha did not answer"; has "$out" "the stages of its bolts are unknown"
rm "$T/down"
ok "an unreachable host's bolts are listed from the plan with every stage unknown, and the host named"

# A hand edit that leaves a duplicated key: crew refuses to read the plan, naming the commit and recfix's message.
w=$T/hand; git clone -q -b plan/wldn "$wb" "$w"
printf '\nUnit: coding\nRepo: switchboard-kit\nIntent: twice\n' >> "$w/plan.rec"; commit_all "$w" "plan: a hand edit"; git -C "$w" push -q origin plan/wldn
bad=$(git -C "$w" rev-parse --short HEAD)
expect_fail "plan/wldn of WilldanGroup/willdan-blueprints at $bad: plan.rec fails recfix --check" crew bolts
has "$out" "duplicated key"
ok "a plan that fails its schema is refused, naming the commit"
