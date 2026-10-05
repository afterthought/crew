# crew fix <team> <name> "<what is wrong>": fix/<name> from the team's bolt at places/fix-<name>, a fresh code
# agent in a free slot with the words given, and a merge into the bolt like a unit's. No change, no plan record.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
command -v wt >/dev/null || fail "this test needs worktrunk's wt"
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn CREW_AGENT=swb-1-conductor
CREW_AGENT= crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
CREW_AGENT= crew bolt give swb-1 >/dev/null 2>&1
plan_tip=$(git --git-dir "$ws" rev-parse wldn/main)

expect_fail "swb-2 holds no bolt" crew fix swb-2 edge-sign-in "x"
expect_fail "a fix is named with lowercase words and dashes" crew fix swb-1 Edge_Sign "x"
expect_ok crew fix swb-1 edge-sign-in "The edge sign-in answers an object where the spec says a string."
has "$out" "swb-1-unit-1 has fix/edge-sign-in: code, in $kd/places/fix-edge-sign-in"
eq "$(git -C "$kd/places/fix-edge-sign-in" branch --show-current)" "fix/edge-sign-in"
eq "$(git -C "$k" rev-parse fix/edge-sign-in)" "$(git -C "$k" rev-parse bolt/tenant-environments)"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' refs/heads/fix/edge-sign-in)" "bolt/tenant-environments"
eq "$(tail -1 "$CREW_TEST_CLAUDE_LOG" | jq -r '"\(.argv[1]) \(.argv[3]) \(.agent) \(.cwd)"')" "claude-opus-5-5[1m] xhigh swb-1-unit-1 $kd/places/fix-edge-sign-in"
grep -q "agent prompt .* 'Fix: The edge sign-in answers an object where the spec says a string.'" "$CREW_TEST_LOG" || fail "the fix's words were not sent"
eq "$(git --git-dir "$ws" rev-parse wldn/main)" "$plan_tip"
expect_ok crew status swb-1; has "$out" "fix/edge-sign-in  fix"
expect_ok crew bolts; has "$out" "fix/edge-sign-in                         fix          places/fix-edge-sign-in"
ok "a fix gets its own place from the bolt and a fresh code agent in a free slot, and no plan record"

echo fixed > "$kd/places/fix-edge-sign-in/sign-in"; commit_all "$kd/places/fix-edge-sign-in" "fix: the edge sign-in answers a string"
expect_ok crew fix swb-1 edge-sign-in --merge
grep -q "agent prompt .* 'Merge fix/edge-sign-in into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'" "$CREW_TEST_LOG" || fail "no merge prompt"
eq "$(tail -1 "$CREW_TEST_CLAUDE_LOG" | jq -r '.argv[3]')" "xhigh"
(cd "$kd/places/fix-edge-sign-in" && wt merge bolt/tenant-environments --no-squash --no-remove >/dev/null 2>&1) || fail "wt merge failed"
expect_ok crew status swb-1
has "$out" "swb-1-unit-1 is free: fix/edge-sign-in has merged into its bolt"
[[ ! -d $kd/places/fix-edge-sign-in ]] || fail "the fix's place is still there"
eq "$(git -C "$kd/bolts/tenant-environments" show HEAD:sign-in)" "fixed"
expect_fail "swb-1 has no fix edge-sign-in in flight" crew fix swb-1 edge-sign-in --merge
ok "a fix merges into the bolt like a unit, and its place and slot go"
