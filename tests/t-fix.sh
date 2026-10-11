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
eq "$(field stage.end Ended "$fb")" "delivered"
eq "$(field stage.end Delivered "$fb")" "bolt/tenant-environments@$(git -C "$k" rev-parse --short bolt/tenant-environments)"
eq "$(field stage.end Observed "$fb")" "late"
eq "$(field slot.free On "$fb")" "agent/swb-1-unit-1 $fb"
ok "the run record names the fix fix/<bolt>/<name>, its reasons give the fix's own name, and its merge's end names the bolt's commit holding it"

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

# A landing's rebase conflicted, and the team's fix carries the bolt onto main: the bolt's own commits replayed onto
# the kit's main, the conflict resolved, and nothing else. crew moves the bolt's branch to the fix's head and runs the
# kit's post-merge hooks there, as after a merge into the bolt; the bolt is proven again before it lands.
bt=bolt/tenant-environments; bd=$kd/bolts/tenant-environments
echo one > "$bd/one"; commit_all "$bd" "feat: one"
echo "# switchboard-kit, the bolt's" > "$bd/README.md"; seq 1 12 > "$bd/two"; commit_all "$bd" "feat: two"
echo three > "$bd/three"; commit_all "$bd" "feat: three"
mkdir -p "$k/.config"; printf '[post-merge]\nmark = "echo {{ target }} $(git rev-parse HEAD) > %s/hook-ran"\n' "$T" > "$k/.config/wt.toml"
echo "# switchboard-kit, main's" > "$k/README.md"; commit_all "$k" "docs: main's title"
n=$(git -C "$k" rev-list --count "main..$bt")
# replay <place> <title>: the fix's agent replays the bolt onto main, resolving the title's conflict to <title>; its
# last commit is made after the stage began, so the fix stage reads delivered
replay() {
  git -C "$1" rebase main >/dev/null 2>&1 && fail "the replay did not stop on the title"
  echo "$2" > "$1/README.md"; git -C "$1" add README.md
  GIT_EDITOR=true GIT_COMMITTER_DATE=$(ago -1) git -C "$1" rebase --continue >/dev/null 2>&1 || fail "the replay did not finish"
}
merge_prompts() { grep -c "agent prompt .* 'Merge $1 into $bt" "$CREW_TEST_LOG" || true; }
cm=fix/tenant-environments/carry-main; cmp=$kd/places/fix-tenant-environments--carry-main
expect_ok crew fix swb-1 carry-main "Carry the bolt onto main: the landing stopped on README.md."
replay "$cmp" "# switchboard-kit, main's and the bolt's"
old=$(git -C "$k" rev-parse "$bt"); new=$(git -C "$k" rev-parse "$cm")
launched=$(launches | wc -l)

echo note > "$bd/stray-note"
expect_fail "bolt/tenant-environments is not moved: its worktree $bd has uncommitted changes (stray-note); commit or remove them, then run crew fix swb-1 carry-main --merge again" \
  crew fix swb-1 carry-main --merge
has "$(field fix.carry Refused "$cm")" "has uncommitted changes (stray-note)"
eq "$(git -C "$k" rev-parse "$bt")" "$old"; eq "$(merge_prompts "$cm")" "0"; eq "$(launches | wc -l)" "$launched"
rm "$bd/stray-note"
git -C "$bd" rebase main >/dev/null 2>&1 && fail "the bolt's own rebase did not stop"
expect_fail "bolt/tenant-environments is not moved: its worktree $bd has a rebase in progress; finish or abort it, then run crew fix swb-1 carry-main --merge again" \
  crew fix swb-1 carry-main --merge
has "$(field fix.carry Refused "$cm")" "has a rebase in progress"
eq "$(git -C "$k" rev-parse "$bt")" "$old"; eq "$(merge_prompts "$cm")" "0"; eq "$(launches | wc -l)" "$launched"
git -C "$bd" rebase --abort
ok "a fix that carries the bolt moves nothing while the bolt's worktree has untracked files or a rebase in progress, starts no merge, and the refusal is recorded"

expect_ok crew fix swb-1 carry-main --merge
has "$out" "bolt/tenant-environments moved from ${old:0:7} to ${new:0:7}: $cm carries the bolt's $n commits onto main (1 changed by the resolution)"
has "$out" "the bolt's checks did not start: Cannot prompt for approval in non-interactive environment; ask ops to run the bolt's verification again, then prove the bolt again before it lands"
has "$out" "swb-1-unit-2 is free: $cm has merged into its bolt"
eq "$(git -C "$k" rev-parse "$bt")" "$new"; eq "$(git -C "$bd" rev-parse HEAD)" "$new"; eq "$(git -C "$bd" status --porcelain)" ""
eq "$(git -C "$bd" show HEAD:README.md)" "# switchboard-kit, main's and the bolt's"
git -C "$k" merge-base --is-ancestor main "$bt" || fail "the bolt is not on main"
[[ ! -e $T/hook-ran ]] || fail "a hook not approved ran"
ok "a fix that carries the bolt becomes its head, and a kit whose checks are not approved says so in worktrunk's words"
eq "$(field fix.carry Why "$cm")" "fix(carry-main): moved bolt/tenant-environments from ${old:0:7} to ${new:0:7}"
eq "$(field fix.carry On "$cm")" "$cm bolt/tenant-environments"
eq "$(field fix.carry From "$cm")" "agent/swb-1-unit-2"
eq "$(field fix.carry Refused "$cm")" ""
eq "$(field stage.end Ended "$cm")" "delivered"
eq "$(merge_prompts "$cm")" "0"; eq "$(launches | wc -l)" "$launched"
expect_ok crew status swb-1
lacks "$out" "$cm"; [[ ! -d $cmp ]] || fail "the fix's place is still there"
git -C "$k" rev-parse --verify -q "refs/heads/$cm" >/dev/null && fail "the fix's branch is still there"
ok "the carry is recorded as fix.carry, no merge stage starts, and the fix's slot, place and branch go as after a merge"

as $box bash -c 'cd "$1" && wt config approvals add --yes >/dev/null 2>&1' _ "$k"
echo "# switchboard-kit, main's again" > "$k/README.md"; commit_all "$k" "docs: main's title again"
ca=fix/tenant-environments/carry-again
expect_ok crew fix swb-1 carry-again "Carry the bolt onto main: the landing stopped on README.md again."
replay "$kd/places/fix-tenant-environments--carry-again" "# switchboard-kit, main's again and the bolt's"
old=$(git -C "$k" rev-parse "$bt"); new=$(git -C "$k" rev-parse "$ca")
expect_ok crew fix swb-1 carry-again --merge
has "$out" "bolt/tenant-environments moved from ${old:0:7} to ${new:0:7}: $ca carries the bolt's $n commits onto main (1 changed by the resolution)"
has "$out" "the bolt's checks are running on ${new:0:7}; prove the bolt again before it lands"
python3 -c 'import os, sys, time
for _ in range(300):
    if os.path.exists(sys.argv[1]) and os.path.getsize(sys.argv[1]):
        break
    time.sleep(0.1)' "$T/hook-ran"
eq "$(cat "$T/hook-ran" 2>/dev/null)" "$bt $new"
eq "$(git -C "$bd" rev-parse HEAD)" "$new"; eq "$(merge_prompts "$ca")" "0"
ok "the kit's post-merge hooks run on the bolt's new head, with the bolt as their target"

rm "$k/.config/wt.toml" "$T/hook-ran"
echo "# switchboard-kit, main's once more" > "$k/README.md"; commit_all "$k" "docs: main's title once more"
seq 1 20 > "$k/twenty"; commit_all "$k" "docs: twenty lines"  # the bolt holds them too once this carry puts it on main
nh=fix/tenant-environments/no-hooks
expect_ok crew fix swb-1 no-hooks "Carry the bolt onto main: the landing stopped on README.md once more."
replay "$kd/places/fix-tenant-environments--no-hooks" "# switchboard-kit, main's once more and the bolt's"
old=$(git -C "$k" rev-parse "$bt"); new=$(git -C "$k" rev-parse "$nh")
expect_ok crew fix swb-1 no-hooks --merge
has "$out" "bolt/tenant-environments moved from ${old:0:7} to ${new:0:7}: $nh carries the bolt's $n commits onto main (1 changed by the resolution)"
has "$out" "the kit has no post-merge hooks, so no checks run on ${new:0:7}; prove the bolt again before it lands"
lacks "$out" "the bolt's checks"
eq "$(git -C "$bd" rev-parse HEAD)" "$new"; eq "$(merge_prompts "$nh")" "0"
[[ ! -e $T/hook-ran ]] || fail "a hook ran for a kit with no post-merge hooks"
ok "a kit with no post-merge hooks moves the bolt and says no checks run on it"

# A replay whose context main rewrote: the bolt changes line 10 of twenty, main rewrites the lines around it, and the
# faithful replay is too unlike the original for range-diff to pair them at its defaults. crew judges by the commits,
# so the fix carries the bolt, and range-diff's view is printed beside the judgment as the reading.
seq 1 20 | sed 's/^10$/ten/' > "$bd/twenty"; commit_all "$bd" "feat: ten"
seq 1 20 | sed -E 's/^(7|8|9|11|12|13)$/main &/' > "$k/twenty"; commit_all "$k" "docs: main's lines around ten"
cx=fix/tenant-environments/context; cxp=$kd/places/fix-tenant-environments--context
expect_ok crew fix swb-1 context "Carry the bolt onto main: the landing stopped on twenty."
git -C "$cxp" rebase main >/dev/null 2>&1 && fail "the replay did not stop on twenty"
seq 1 20 | sed -E 's/^(7|8|9|11|12|13)$/main &/; s/^10$/ten/' > "$cxp/twenty"; git -C "$cxp" add twenty
GIT_EDITOR=true GIT_COMMITTER_DATE=$(ago -1) git -C "$cxp" rebase --continue >/dev/null 2>&1 || fail "the replay did not finish"
old=$(git -C "$k" rev-parse "$bt"); new=$(git -C "$k" rev-parse "$cx"); n=$(git -C "$k" rev-list --count "main..$bt")
expect_ok crew fix swb-1 context --merge
has "$out" "git range-diff main..$bt main..$cx, the reading, which judges nothing: crew judges by each commit's message and author, in order"
has "$out" "$n:  ${old:0:7} < -:  ------- feat: ten"
has "$out" "-:  ------- > $n:  ${new:0:7} feat: ten"
has "$out" "bolt/tenant-environments moved from ${old:0:7} to ${new:0:7}: $cx carries the bolt's $n commits onto main (1 changed by the resolution)"
eq "$(git -C "$k" rev-parse "$bt")" "$new"; eq "$(git -C "$bd" rev-parse HEAD)" "$new"
eq "$(git -C "$bd" show HEAD:twenty | sed -n 9,11p | tr '\n' ' ')" "main 9 ten main 11 "
eq "$(merge_prompts "$cx")" "0"
ok "a replay whose context main rewrote carries the bolt though range-diff leaves it unpaired, and range-diff is printed as the reading"

# A fix that rewords one of the bolt's commits, or gives it another author, holds a commit that is not the bolt's: it
# merges as a fix, naming the bolt's commit that is not in it and its own in that place, though range-diff pairs the
# two. Run again with that commit as the bolt has it, the fix carries the bolt, and frees its slot.
# amend <fix> <git commit --amend's options>: the fix's last commit amended, after its stage began
amend() { GIT_COMMITTER_DATE=$(ago -1) git -C "$kd/places/fix-tenant-environments--${1##*/}" commit -q --amend "${@:2}"; }
rw=fix/tenant-environments/reworded
expect_ok crew fix swb-1 reworded "Carry the bolt onto main."
amend "$rw" -m "feat: ten" -m "Line ten is the bolt's."
expect_ok crew fix swb-1 reworded --merge
has "$out" "$rw does not carry the bolt onto main (the bolt's commit $(git -C "$k" rev-parse --short=7 "$bt") (feat: ten) is not in it; its commit $(git -C "$k" rev-parse --short=7 "$rw") (feat: ten) is none of the bolt's): merging it as a fix"
has "$out" "$n:  ${new:0:7} ! $n:  $(git -C "$k" rev-parse --short=7 "$rw") feat: ten"
eq "$(merge_prompts "$rw")" "1"; eq "$(git -C "$k" rev-parse "$bt")" "$new"
ra=fix/tenant-environments/re-authored
expect_ok crew fix swb-1 re-authored "Carry the bolt onto main."
amend "$ra" --no-edit --author "Someone Else <else@example.com>"
expect_ok crew fix swb-1 re-authored --merge
has "$out" "$ra does not carry the bolt onto main (the bolt's commit $(git -C "$k" rev-parse --short=7 "$bt") (feat: ten) is not in it; its commit $(git -C "$k" rev-parse --short=7 "$ra") (feat: ten) is none of the bolt's): merging it as a fix"
eq "$(merge_prompts "$ra")" "1"; eq "$(git -C "$k" rev-parse "$bt")" "$new"
ok "a fix that rewords or re-authors one of the bolt's commits merges as a fix, naming that commit both ways"
for f in "$rw" "$ra"; do
  expect_ok crew fix swb-1 "${f##*/}" "Carry the bolt onto main, each commit with the bolt's message and author."
  amend "$f" -m "feat: ten" --reset-author
  old=$(git -C "$k" rev-parse "$bt"); new=$(git -C "$k" rev-parse "$f")
  expect_ok crew fix swb-1 "${f##*/}" --merge
  has "$out" "bolt/tenant-environments moved from ${old:0:7} to ${new:0:7}: $f carries the bolt's $n commits onto main (0 changed by the resolution)"
done
ok "run again with the commit as the bolt has it, each carries the bolt, none changed by the resolution"

# A fix that replays the bolt's commits in another order holds every one of them, but not each in its place: it merges
# as a fix, saying so. Run again with them in the bolt's order, it carries the bolt and frees its slot.
# swap <fix>: the fix's last two commits swapped, the last replayed onto the one before both and the other picked after
# it, after its stage began
swap() {
  local p=$kd/places/fix-tenant-environments--${1##*/} first
  first=$(git -C "$p" rev-parse HEAD~1)
  GIT_COMMITTER_DATE=$(ago -1) git -C "$p" rebase -q --onto HEAD~2 HEAD~1
  GIT_COMMITTER_DATE=$(ago -1) git -C "$p" cherry-pick "$first" >/dev/null
}
sw=fix/tenant-environments/swapped
expect_ok crew fix swb-1 swapped "Carry the bolt onto main."
swap "$sw"
eq "$(git -C "$k" log --format=%s -2 "$sw" | tr '\n' ' ')" "feat: three feat: ten "
expect_ok crew fix swb-1 swapped --merge
has "$out" "$sw does not carry the bolt onto main (its commits are the bolt's in another order): merging it as a fix"
eq "$(merge_prompts "$sw")" "1"; eq "$(git -C "$k" rev-parse "$bt")" "$new"
expect_ok crew fix swb-1 swapped "Carry the bolt onto main, its commits in the bolt's order."
swap "$sw"
old=$(git -C "$k" rev-parse "$bt"); new=$(git -C "$k" rev-parse "$sw")
expect_ok crew fix swb-1 swapped --merge
has "$out" "bolt/tenant-environments moved from ${old:0:7} to ${new:0:7}: $sw carries the bolt's $n commits onto main (0 changed by the resolution)"
eq "$(merge_prompts "$sw")" "1"
ok "a fix that holds the bolt's commits in another order merges as a fix, saying so, and carries the bolt once in its order"

# The reading comes before the judgment, whatever it is. A fix with no commits beyond main merges as a fix, with
# range-diff's lines above it, or git's words without the usage git prints after them. When range-diff itself fails,
# crew names it in git's words and judges the same: the fix that carries the bolt still moves it.
echo read > "$k/read"; commit_all "$k" "docs: main moves past the bolt"
nb=fix/tenant-environments/nothing-beyond
expect_ok crew fix swb-1 nothing-beyond "Carry the bolt onto main."
git -C "$kd/places/fix-tenant-environments--nothing-beyond" rebase -q --onto main "$bt"
expect_ok crew fix swb-1 nothing-beyond --merge
has "$out" "git range-diff main..$bt main..$nb"
lacks "$out" "usage: git range-diff"
has "$out" "$nb does not carry the bolt onto main (it has no commits beyond main): merging it as a fix"
eq "$(merge_prompts "$nb")" "1"; eq "$(git -C "$k" rev-parse "$bt")" "$new"
mkdir -p "$T/range-diff-fails"
printf '#!/usr/bin/env bash\nfor a; do [[ $a == range-diff ]] && { echo "fatal: range-diff refused by this test" >&2; exit 128; }; done\nexec %q "$@"\n' \
  "$(command -v git)" > "$T/range-diff-fails/git"
chmod +x "$T/range-diff-fails/git"
rf=fix/tenant-environments/range-fails
expect_ok crew fix swb-1 range-fails "Carry the bolt onto main."
GIT_COMMITTER_DATE=$(ago -1) git -C "$kd/places/fix-tenant-environments--range-fails" rebase -q main
old=$(git -C "$k" rev-parse "$bt"); new=$(git -C "$k" rev-parse "$rf")
PATH=$T/range-diff-fails:$PATH expect_ok crew fix swb-1 range-fails --merge
has "$out" "git range-diff main..$bt main..$rf could not be read: fatal: range-diff refused by this test"
lacks "$out" "the reading, which judges nothing"
has "$out" "bolt/tenant-environments moved from ${old:0:7} to ${new:0:7}: $rf carries the bolt's $n commits onto main (0 changed by the resolution)"
eq "$(git -C "$k" rev-parse "$bt")" "$new"; eq "$(merge_prompts "$rf")" "0"
ok "a fix with nothing beyond main is read too, and a range-diff that fails is named in git's words and the judgment holds"

echo more > "$k/more"; commit_all "$k" "docs: more on main"
own=fix/tenant-environments/own-commit; op=$kd/places/fix-tenant-environments--own-commit
expect_ok crew fix swb-1 own-commit "Carry the bolt onto main."
git -C "$op" rebase -q main; echo own > "$op/own"; commit_all "$op" "fix: one of its own"
expect_ok crew fix swb-1 own-commit --merge
has "$out" "$own does not carry the bolt onto main (its commit $(git -C "$k" rev-parse --short=7 "$own") (fix: one of its own) is none of the bolt's): merging it as a fix"
has "$out" "git range-diff main..$bt main..$own, the reading, which judges nothing"
has "$out" "-:  ------- > $((n + 1)):  $(git -C "$k" rev-parse --short=7 "$own") fix: one of its own"
eq "$(merge_prompts "$own")" "1"; eq "$(git -C "$k" rev-parse "$bt")" "$new"
drop=fix/tenant-environments/drops-one; dp=$kd/places/fix-tenant-environments--drops-one
expect_ok crew fix swb-1 drops-one "Carry the bolt onto main."
git -C "$dp" rebase -q main; git -C "$dp" rebase -q --onto "$drop~3" "$drop~2"
expect_ok crew fix swb-1 drops-one --merge
has "$out" "$drop does not carry the bolt onto main (the bolt's commit $(git -C "$k" rev-parse --short=7 "$bt~2") (feat: two) is not in it): merging it as a fix"
eq "$(merge_prompts "$drop")" "1"; eq "$(git -C "$k" rev-parse "$bt")" "$new"
stays=fix/tenant-environments/never-replayed
expect_ok crew fix swb-1 never-replayed "Carry the bolt onto main."
expect_ok crew fix swb-1 never-replayed --merge
has "$out" "$stays does not carry the bolt onto main (it holds the bolt's head): merging it as a fix"
has "$out" "swb-1-unit-4 has $stays: merge, in $kd/places/fix-tenant-environments--never-replayed"
eq "$(merge_prompts "$stays")" "1"; eq "$(git -C "$k" rev-parse "$bt")" "$new"
ok "a fix with a commit of its own, one that drops one of the bolt's commits, and one never replayed merge as fixes, saying why"
