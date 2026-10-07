# crew fix <team> <name> "<what is wrong>": fix/<bolt>/<name> from the team's bolt at places/fix-<bolt>--<name>, a
# fresh code agent in a free slot with the words given, and a merge into the bolt like a unit's. No change, no plan
# record.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
command -v wt >/dev/null || fail "this test needs worktrunk's wt"
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn CREW_AGENT=swb-1-conductor
CREW_AGENT= crew bolt new tenant-environments "Tenants hold environments." --repo switchboard-kit >/dev/null
CREW_AGENT= crew bolt give swb-1 >/dev/null 2>&1
plan_tip=$(git --git-dir "$ws" rev-parse wldn/main)
fb=fix/tenant-environments/edge-sign-in; fp=$kd/places/fix-tenant-environments--edge-sign-in
# field <act> <field> <object>: a field of the box's last entry of the act naming the object
field() {
  as $box python3 -c 'import glob, os, sys; sys.path.insert(0, sys.argv[1]); import record
es = [e for f in sorted(glob.glob(os.path.expanduser("~/.local/state/crew/wldn/runs/*/*.rec"))) for e in record.parse(open(f).read())
      if e["Act"] == sys.argv[2] and sys.argv[4] in e["On"]]
v = es[-1].get(sys.argv[3], "") if es else ""
print(" ".join(v) if isinstance(v, list) else v)' "$CREW/plugin/lib" "$@"
}
refused() { field fix.start Refused "$1"; }
slots_of() { as $box cat ".local/state/$1-team/slots"; }

expect_fail "swb-2 holds no bolt" crew fix swb-2 edge-sign-in "x"
expect_fail "a fix is named with lowercase words and dashes" crew fix swb-1 Edge_Sign "x"
expect_ok crew fix swb-1 edge-sign-in "The edge sign-in answers an object where the spec says a string."
has "$out" "swb-1-unit-1 has $fb: code, in $fp"
eq "$(git -C "$fp" branch --show-current)" "$fb"
eq "$(git -C "$k" rev-parse $fb)" "$(git -C "$k" rev-parse bolt/tenant-environments)"
eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' "refs/heads/$fb")" "bolt/tenant-environments"
eq "$(tail -1 "$CREW_TEST_CLAUDE_LOG" | jq -r '"\(.argv[1]) \(.argv[3]) \(.agent) \(.cwd)"')" "claude-opus-5-5[1m] xhigh swb-1-unit-1 $fp"
grep -q "agent prompt .* 'Fix: The edge sign-in answers an object where the spec says a string.'" "$CREW_TEST_LOG" || fail "the fix's words were not sent"
eq "$(git --git-dir "$ws" rev-parse wldn/main)" "$plan_tip"
expect_ok crew status swb-1; has "$out" "$fb  fix"
expect_ok crew bolts; has "$out" "$fb     fix          places/fix-tenant-environments--edge-sign-in"
ok "a fix gets its own place from the bolt and a fresh code agent in a free slot, and no plan record"

expect_ok crew fix swb-1 edge-sign-in "It still answers an object."
has "$out" "swb-1-unit-1 has $fb: code, in $fp"
eq "$(as $box cat .local/state/swb-1-team/slots)" "unit-1 fix $fb $fp"
ok "a fix in flight run again starts again in its own slot and place"

echo fixed > "$fp/sign-in"; commit_all "$fp" "fix: the edge sign-in answers a string"
expect_ok crew fix swb-1 edge-sign-in --merge
grep -q "agent prompt .* 'Merge $fb into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'" "$CREW_TEST_LOG" || fail "no merge prompt"
eq "$(tail -1 "$CREW_TEST_CLAUDE_LOG" | jq -r '.argv[3]')" "xhigh"
(cd "$fp" && wt merge bolt/tenant-environments --no-squash --no-remove >/dev/null 2>&1) || fail "wt merge failed"
expect_ok crew status swb-1
has "$out" "swb-1-unit-1 is free: $fb has merged into its bolt"
has "$out" "$fp and $fb are removed; the branch was at"
[[ ! -d $fp ]] || fail "the fix's place is still there"
git -C "$k" rev-parse --verify -q "refs/heads/$fb" >/dev/null && fail "the fix's branch is still there"
eq "$(git -C "$kd/bolts/tenant-environments" show HEAD:sign-in)" "fixed"
expect_fail "swb-1 has no fix edge-sign-in in flight" crew fix swb-1 edge-sign-in --merge
ok "a fix merges into the bolt like a unit, and its place and slot go"
eq "$(field fix.start Why "$fb")" "fix(edge-sign-in): start fix"
eq "$(field stage.end Why "$fb")" "fix(edge-sign-in): merge ended"
eq "$(field slot.free On "$fb")" "agent/swb-1-unit-1 $fb"
ok "the run record names the fix fix/<bolt>/<name>, and its reasons give the fix's own name"

# A fix started as fix/<name>, before a fix's branch and place named its bolt, as its slot recorded them.
old=$kd/places/fix-old-sign-in
git -C "$k" worktree add -q --track -b fix/old-sign-in "$old" bolt/tenant-environments
as $box bash -c 'echo "unit-2 fix fix/old-sign-in $1" >> .local/state/swb-1-team/slots' _ "$old"
echo old > "$old/old"; commit_all "$old" "fix: the old sign-in"
expect_ok crew fix swb-1 old-sign-in --merge
has "$out" "swb-1-unit-2 has fix/old-sign-in: merge, in $old"
grep -q "agent prompt .* 'Merge fix/old-sign-in into bolt/tenant-environments: wt merge bolt/tenant-environments --no-squash --no-remove'" "$CREW_TEST_LOG" || fail "no merge prompt for the old fix"
eq "$(field fix.merge On fix/tenant-environments/old-sign-in)" "fix/tenant-environments/old-sign-in bolt/tenant-environments agent/swb-1-unit-2"
eq "$(field fix.merge Why fix/tenant-environments/old-sign-in)" "fix(old-sign-in): start merge"
(cd "$old" && wt merge bolt/tenant-environments --no-squash --no-remove >/dev/null 2>&1) || fail "wt merge of the old fix failed"
expect_ok crew status swb-1
has "$out" "swb-1-unit-2 is free: fix/old-sign-in has merged into its bolt"
has "$out" "$old and fix/old-sign-in are removed; the branch was at"
[[ ! -d $old ]] || fail "the old fix's place is still there"
git -C "$k" rev-parse --verify -q refs/heads/fix/old-sign-in >/dev/null && fail "the old fix's branch is still there"
eq "$(git -C "$kd/bolts/tenant-environments" show HEAD:old)" "old"
eq "$(field stage.end Why fix/tenant-environments/old-sign-in)" "fix(old-sign-in): merge ended"
eq "$(field slot.free On fix/tenant-environments/old-sign-in)" "agent/swb-1-unit-2 fix/tenant-environments/old-sign-in"
ok "a fix started as fix/<name> merges from the place its slot recorded, and its place, branch and slot go"

CREW_AGENT= crew bolt new console-pages "The console lists them." --repo switchboard-kit >/dev/null
CREW_AGENT= crew bolt give swb-2 console-pages >/dev/null 2>&1
expect_ok crew fix swb-1 bolt-takes-main "Bring main into the bolt."
has "$out" "swb-1-unit-1 has fix/tenant-environments/bolt-takes-main: code, in $kd/places/fix-tenant-environments--bolt-takes-main"
CREW_AGENT=swb-2-conductor expect_ok crew fix swb-2 bolt-takes-main "Bring main into the bolt."
has "$out" "swb-2-unit-1 has fix/console-pages/bolt-takes-main: code, in $kd/places/fix-console-pages--bolt-takes-main"
for b in tenant-environments console-pages; do
  eq "$(git -C "$kd/places/fix-$b--bolt-takes-main" branch --show-current)" "fix/$b/bolt-takes-main"
  eq "$(git -C "$k" for-each-ref --format='%(upstream:short)' "refs/heads/fix/$b/bolt-takes-main")" "bolt/$b"
done
expect_ok crew status swb-1; has "$out" "fix/tenant-environments/bolt-takes-main  fix"; lacks "$out" "console-pages"
expect_ok crew status swb-2; has "$out" "fix/console-pages/bolt-takes-main  fix"; lacks "$out" "tenant-environments"
ok "two teams' fixes of one name in one kit each get a branch from their own bolt, in a place of their own"

launched=$(launches | wc -l); before=$(slots_of swb-1)
git -C "$k" branch -q fix/tenant-environments/leftover bolt/tenant-environments
expect_fail "fix/tenant-environments/leftover already has a branch that no slot of swb-1 holds, though no place at $kd/places/fix-tenant-environments--leftover: name this fix differently" \
  crew fix swb-1 leftover "x"
eq "$(refused fix/tenant-environments/leftover)" "fix/tenant-environments/leftover already has a branch that no slot of swb-1 holds, though no place at $kd/places/fix-tenant-environments--leftover: name this fix differently"
mkdir "$kd/places/fix-tenant-environments--stray"
expect_fail "fix/tenant-environments/stray already has a place at $kd/places/fix-tenant-environments--stray that no slot of swb-1 holds: name this fix differently" \
  crew fix swb-1 stray "x"
has "$(refused fix/tenant-environments/stray)" "already has a place at $kd/places/fix-tenant-environments--stray"
eq "$(slots_of swb-1)" "$before"; eq "$(launches | wc -l)" "$launched"
ok "a new fix whose branch or place is already there is refused and recorded, and takes no slot"

p=$kd/places/fix-tenant-environments--bolt-takes-main
git -C "$p" switch -q -c elsewhere
expect_fail "$p is on elsewhere, made from no bolt, not fix/tenant-environments/bolt-takes-main from bolt/tenant-environments: crew starts a fix only in its own place" \
  crew fix swb-1 bolt-takes-main "Again."
has "$(refused fix/tenant-environments/bolt-takes-main)" "$p is on elsewhere"
git -C "$k" worktree add -q --track -b fix/shared "$kd/places/fix-shared" bolt/tenant-environments
as $box bash -c 'echo "unit-2 fix fix/shared $1" >> .local/state/swb-2-team/slots' _ "$kd/places/fix-shared"
expect_fail "$kd/places/fix-shared is on fix/shared, made from bolt/tenant-environments, not fix/shared from bolt/console-pages: crew starts a fix only in its own place" \
  crew fix swb-2 shared "Bring main into the bolt."
has "$(refused fix/console-pages/shared)" "made from bolt/tenant-environments"
eq "$(slots_of swb-1)" "$before"; eq "$(launches | wc -l)" "$launched"
has "$(slots_of swb-2)" "unit-2 fix fix/shared $kd/places/fix-shared"
ok "a fix in flight whose place is on another branch, or whose branch is from another team's bolt, is refused and keeps its slot"
expect_fail "$kd/places/fix-shared is on fix/shared, made from bolt/tenant-environments, not fix/shared from bolt/console-pages: crew starts a fix only in its own place" \
  crew fix swb-2 shared --merge
has "$(field fix.merge Refused fix/console-pages/shared)" "made from bolt/tenant-environments"
eq "$(launches | wc -l)" "$launched"; has "$(slots_of swb-2)" "unit-2 fix fix/shared $kd/places/fix-shared"
ok "a fix's merge is refused when its branch is from another team's bolt, and keeps its slot"

git -C "$k" branch -q fix/tenant-environments/deep/x bolt/tenant-environments
expect_fail "refs/heads/fix/tenant-environments/deep" crew fix swb-1 deep "x"
has "$(refused fix/tenant-environments/deep)" "on $box: "
eq "$(slots_of swb-1)" "$before"; eq "$(launches | wc -l)" "$launched"
ok "a fix whose branch git cannot make is refused in git's words and recorded, and gives its slot back"

pc=$kd/places/fix-console-pages--bolt-takes-main
echo fix > "$pc/main-line"; commit_all "$pc" "fix: main's line"
echo bolt > "$kd/bolts/console-pages/main-line"; commit_all "$kd/bolts/console-pages" "feat: the bolt's line"
git -C "$pc" rebase bolt/console-pages >/dev/null 2>&1 && fail "the rebase did not stop"
eq "$(git -C "$pc" branch --show-current)" ""
CREW_AGENT=swb-2-conductor expect_ok crew fix swb-2 bolt-takes-main --merge
has "$out" "swb-2-unit-1 has fix/console-pages/bolt-takes-main: merge, in $pc"
ok "a fix's merge stopped partway through its rebase starts again in its own place"
