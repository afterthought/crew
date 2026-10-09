# Every read of a team removes, with its branch, each worktree crew made in the team's kit checkout whose work is
# over and that no slot holds: a bolt's once no plan has it, a unit's once it has merged or landed or no plan has
# it. One with uncommitted changes, or a lock, is kept and named on each read. Nothing crew didn't make is touched,
# and nothing is removed while a plan the kit's work goes in can't be read. Each removal goes through the kit's own
# wt remove, so its remove hooks run; one whose pre-remove hook fails, whose hooks wait for the user's approval on
# the host, or with no wt on the host's path, is kept with its branch and named, never with wt's advice to skip.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
team_world
box=chuck-herdr-alpha
export CREW_LABEL=wldn
printf 'node_modules/\n' > "$k/.gitignore"; commit_all "$k" "chore: ignore installed dependencies"
crew bolt new in-flight "A bolt in flight." --repo switchboard-kit >/dev/null
for u in merged-one stray; do crew unit add $u "Unit $u." --bolt in-flight >/dev/null; done
crew unit add still-planned "Still planned." --bolt in-flight >/dev/null
crew bolt give swb-1 >/dev/null 2>&1
bd=$kd/bolts/in-flight
for u in merged-one stray; do place "$k" in-flight $u >/dev/null; change "$bd" $u 2 2; done
commit_all "$bd" "feat: merged-one and stray merged"
place "$k" in-flight still-planned >/dev/null

# Leftovers no read has removed yet, and worktrees crew never made.
git -C "$k" worktree add -q -b bolt/gone "$kd/bolts/gone" main; echo gone > "$kd/bolts/gone/gone"; commit_all "$kd/bolts/gone" "feat: gone"
gone=$(git -C "$k" rev-parse --short bolt/gone)
place "$k" in-flight ignored-only >/dev/null; mkdir -p "$kd/places/ignored-only/node_modules/x"; echo dep > "$kd/places/ignored-only/node_modules/x/index.js"
echo note > "$kd/places/stray/note"
git -C "$k" worktree add -q --track -b unit/locked-one "$kd/places/locked-one" bolt/in-flight; git -C "$k" worktree lock "$kd/places/locked-one"
git -C "$k" worktree add -q --track -b unit/held-one "$kd/places/held-one" bolt/in-flight
as $box bash -c 'mkdir -p .local/state/swb-2-team && echo "unit-1 unit held-one $1" >> .local/state/swb-2-team/slots' _ "$kd/places/held-one"
git -C "$k" worktree add -q -b mine "$kd/mine" main
git -C "$k" worktree add -q --track -b unit/x "$kd/x" bolt/in-flight
git -C "$k" worktree add -q -b bolt/elsewhere "$kd/bolts/not-elsewhere" main
git -C "$k" worktree add -q --detach "$kd/places/detached" bolt/in-flight
tidy() { crew _tidy swb-1; }
untouched() {
  local p; for p in "$k" "$bd" "$kd/mine" "$kd/x" "$kd/bolts/not-elsewhere" "$kd/places/detached" "$kd/places/held-one" "$kd/places/still-planned"; do
    [[ -d $p ]] || fail "$p was removed"
  done
  git -C "$k" rev-parse --verify -q unit/held-one >/dev/null || fail "unit/held-one was removed"
}

mv "$ws" "$ws.away"
expect_ok tidy
has "$out" "no worktree was removed: wldn/main of WilldanGroup/crew-state could not be read: "
eq "$(wc -l <<<"$out" | tr -d ' ')" "1"
for p in bolts/gone places/merged-one places/stray places/ignored-only places/locked-one; do [[ -d $kd/$p ]] || fail "$p went while the plan could not be read"; done
untouched
mv "$ws.away" "$ws"
ok "nothing is removed while a plan the kit's work goes in can't be read"

# A flywheel whose state repository can't even be named: said in the same one line, and the tidy still succeeds.
unnamed() {
  as $box python3 - "$CREW/plugin/lib" <<'PY'
import argparse, sys
sys.path.insert(0, sys.argv[1])
import crew, plan
fleet = crew.load()
del fleet["partitions"]["wldn"]
plan.tidy(fleet, argparse.Namespace(team="swb-1"))
PY
}
expect_ok unnamed
has "$out" "no worktree was removed: the plan of wldn could not be read: no partition 'wldn'"
eq "$(wc -l <<<"$out" | tr -d ' ')" "1"
for p in bolts/gone places/merged-one places/stray places/ignored-only places/locked-one; do [[ -d $kd/$p ]] || fail "$p went while the plan could not be named"; done
untouched
ok "a plan whose state repository can't be named is said, not raised, and nothing is removed"

expect_ok tidy
has "$out" "$kd/bolts/gone and bolt/gone are removed; the branch was at $gone"
has "$out" "$kd/places/merged-one and unit/merged-one are removed; the branch was at"
has "$out" "$kd/places/ignored-only and unit/ignored-only are removed; the branch was at"
has "$out" "$kd/places/stray is kept, and unit/stray with it: unit stray has merged into bolt/in-flight, and it has uncommitted changes, which are the user's to keep or discard"
has "$out" "$kd/places/locked-one is kept, and unit/locked-one with it: it is locked"
for p in bolts/gone places/merged-one places/ignored-only; do [[ ! -d $kd/$p ]] || fail "$p is still there"; done
for b in bolt/gone unit/merged-one unit/ignored-only; do git -C "$k" rev-parse --verify -q "$b" >/dev/null && fail "$b is still there"; done
[[ -d $kd/places/stray && -d $kd/places/locked-one ]] || fail "a kept worktree was removed"
git -C "$k" rev-parse --verify -q unit/stray >/dev/null || fail "unit/stray went without its place"
untouched
lacks "$out" "held-one"; lacks "$out" "still-planned"; lacks "$out" "detached"; lacks "$out" "$kd/mine"
ok "a bolt in no plan, a merged place no slot holds and one with only ignored files go with their branches"
ok "one with uncommitted changes or a lock is kept and named, and nothing crew didn't make, held or planned is touched"

expect_ok crew status swb-1
has "$out" "$kd/places/stray is kept, and unit/stray with it"
has "$out" "$kd/places/locked-one is kept, and unit/locked-one with it: it is locked"
[[ -d $kd/places/stray ]] || fail "the stray place went on the next read"
ok "a kept worktree is named again on the next read"

rm "$kd/places/stray/note"
git -C "$k" worktree unlock "$kd/places/locked-one"
expect_ok tidy
has "$out" "$kd/places/stray and unit/stray are removed; the branch was at"
has "$out" "$kd/places/locked-one and unit/locked-one are removed; the branch was at"
[[ ! -d $kd/places/stray && ! -d $kd/places/locked-one ]] || fail "a cleared worktree is still there"
untouched
expect_ok tidy
lacks "$out" "removed"; lacks "$out" "kept"
ok "once its file goes, or its lock, the next read removes it, and a read with nothing over says nothing"

# A kit whose worktree config has merge hooks only: a finished place goes as before, and no approval is asked.
mkdir -p "$k/.config"; printf '[pre-merge]\ngate = "true"\n' > "$k/.config/wt.toml"; commit_all "$k" "chore: gate merges"
for u in merge-hooked hooked toolless; do change "$bd" $u 2 2; done; commit_all "$bd" "feat: merge-hooked, hooked and toolless merged"
place "$k" in-flight merge-hooked >/dev/null
expect_ok tidy
has "$out" "$kd/places/merge-hooked and unit/merge-hooked are removed; the branch was at"
lacks "$out" "approval"
ok "a kit with merge hooks only sees its place go as before, with no approval asked"

# A kit whose remove hooks tear down what it stood up for a worktree: its pre-remove hook logs whether the place's
# files are there and fails while the box holds a marker for it; its post-remove hook logs whether they are still there.
log=$T/hooks.log
cat > "$k/.config/wt.toml" <<TOML
[pre-merge]
gate = "true"

[pre-remove]
teardown = "echo pre {{ worktree_name }} \$(test -e README.md && echo present || echo absent) >> $log; test ! -e \$HOME/fail-{{ worktree_name }}"

[post-remove]
after = "echo post {{ worktree_name }} \$(test -e {{ worktree_path }} && echo present || echo absent) >> $log"
TOML
commit_all "$k" "chore: tear down what a worktree stood up"
place "$k" in-flight hooked >/dev/null
over="unit hooked has merged into bolt/in-flight"
expect_ok tidy
has "$out" "$kd/places/hooked is kept, and unit/hooked with it: $over, and the kit's remove hooks wait for the user's approval on $box: wt config approvals add, in $k"
lacks "$out" "--yes"; lacks "$out" "↳"
[[ -d $kd/places/hooked ]] || fail "the place went before its hooks were approved"
git -C "$k" rev-parse --verify -q unit/hooked >/dev/null || fail "unit/hooked went before its hooks were approved"
[[ ! -e $log ]] || fail "a hook ran before it was approved:"$'\n'"$(cat "$log")"
ok "remove hooks not approved on the host run nothing, and the place is kept with its branch, naming the approval"

# The test stands in for the user, approving the kit's hooks on the box.
as $box wt -C "$k" config approvals add --yes >/dev/null 2>&1 || fail "wt config approvals add failed"
touch "$(home_of $box)/fail-hooked"
for _ in 1 2; do
  expect_ok tidy
  has "$out" "$kd/places/hooked is kept, and unit/hooked with it: $over, and the kit's wt remove refused it: pre-remove command failed"
  lacks "$out" "--no-hooks"; lacks "$out" "↳"
  [[ -d $kd/places/hooked ]] || fail "the place went though its pre-remove hook failed"
  git -C "$k" rev-parse --verify -q unit/hooked >/dev/null || fail "unit/hooked went though its place's hook failed"
done
eq "$(grep -c '^pre hooked present$' "$log")" "2"
ok "a pre-remove hook that fails keeps the place and its branch, named without wt's advice to skip it, on every read"

rm "$(home_of $box)/fail-hooked"
expect_ok tidy
has "$out" "$kd/places/hooked and unit/hooked are removed; the branch was at"
[[ ! -d $kd/places/hooked ]] || fail "the place is still there once its hook passed"
git -C "$k" rev-parse --verify -q unit/hooked >/dev/null && fail "unit/hooked is still there"
eq "$(grep -c '^pre hooked present$' "$log")" "3"
grep -q '^pre .* absent$' "$log" && fail "a pre-remove hook ran without the place's files:"$'\n'"$(cat "$log")"
# wt runs the post-remove hook in the background once the place is gone; the stub sleep returns at once.
for _ in $(seq 100); do grep -q '^post hooked' "$log" && break; python3 -c 'import time; time.sleep(0.1)'; done
grep -qx 'post hooked absent' "$log" || fail "the post-remove hook never ran, or ran with the place there:"$'\n'"$(cat "$log")"
ok "once the cause is cleared the next read runs the hooks, the place's files there before and gone after, and removes it and its branch"

place "$k" in-flight toolless >/dev/null
nowt() ( PATH=$(path_without wt); tidy )
expect_ok nowt
has "$out" "$kd/places/toolless is kept, and unit/toolless with it: unit toolless has merged into bolt/in-flight, and wt, the kit's worktree tool, is not on $box's path"
[[ -d $kd/places/toolless ]] || fail "the place went with no wt to remove it"
git -C "$k" rev-parse --verify -q unit/toolless >/dev/null || fail "unit/toolless went with no wt"
ok "with no wt on the host's path the place is kept with its branch, and named"
