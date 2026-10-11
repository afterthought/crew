# crew's merges are gated by its suite. With the real wt, in a scratch repository holding crew's .config/ and a
# stand-in suite whose t-b fails when the tree holds a file named red: a unit's, a fix's and a bolt's merge is
# refused while the suite is red, naming t-b, with the target unmoved, and lands once it is green; the live test
# stays out of the gate whatever the merging shell has set.
#
# After each merge into the bolt, its verification runs on a frozen copy of the bolt's new head, made a git
# repository of one commit whose tree is the head's, its archives linked to the repository's moon-outputs, and
# bolt-status.sh reads it: green, and red naming t-b (the stand-in's t-b also fails in the verification's copy of a
# tree holding copy-red, so such a merge passes its gate and fails its verification); two runs side by side
# each keep their own revision's outcome; a merge onto main starts none; a dead run reads interrupted, a head with
# no run not verified, and a record that can't be read is named; a hand rerun is refused while a run of the head is
# alive and starts after a cut-off. The suite a verification runs never inherits BOLT_VERIFY_REV, so a test that
# merges into a bolt of its own, as this one does, verifies that bolt, not the one under verification.
# Reads: .config/
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
command -v wt >/dev/null || fail "this test needs worktrunk's wt"
gitconfig "$HOME"
# worktrunk keeps its approvals under the scratch HOME, never the user's; the verification's copies go under $T.
export XDG_CONFIG_HOME=$HOME/.config TMPDIR=$T/tmp
mkdir -p "$TMPDIR" "$T/bin"

# A stand-in devenv first on PATH: `devenv shell -- <command>` runs the command.
cat > "$T/bin/devenv" <<'EOF'
#!/bin/sh
[ "$1" = shell ] && [ "$2" = -- ] || { echo "stand-in devenv: only shell -- <command>" >&2; exit 2; }
shift 2; exec "$@"
EOF
chmod +x "$T/bin/devenv"; export PATH="$T/bin:$PATH"

# The repository, laid out as crew's is: main at crew/main, the bolt's worktree at crew/bolts/b, places beside them.
r=$T/crew/main
git init -q "$r"; cp -R "$CREW/.config" "$r/"; mkdir -p "$r/tests"
# The stand-in suite. In a verification's copy, made under $TMPDIR, it says what the copy is, and waits while
# $T/hold exists, so a verification can be caught mid-run while the gates go on.
cat > "$r/tests/suite" <<EOF
#!/bin/sh
copy=; case \$(pwd -P) in "$TMPDIR"/crew-verify.*) copy=1 ;; esac
while [ -e "$T/hold" ] && [ -n "\$copy" ]; do /bin/sleep 0.1; done
echo "live=[\${CREW_TEST_LIVE-unset}]"
echo "verify-rev=[\${BOLT_VERIFY_REV-unset}]"
if [ -n "\$copy" ]; then
  echo "copy-commits=[\$(git rev-list --count HEAD)] copy-tree=[\$(git rev-parse HEAD^{tree})] copy-status=[\$(git status --porcelain)]"
  echo "copy-outputs=[\$(readlink .moon/cache/outputs)]"
fi
echo "ok    t-a"
if [ -e red ] || { [ -e copy-red ] && [ -n "\$copy" ]; }; then echo "FAIL  t-b"; echo "1 passed (0 replayed), 1 failed"; exit 1; fi
echo "ok    t-b"; echo "2 passed (0 replayed), 0 failed"
EOF
chmod +x "$r/tests/suite"; printf '.moon/cache/\n' > "$r/.gitignore"; commit_all "$r" "chore: start"
git -C "$r" branch bolt/b
git -C "$r" worktree add -q "$T/crew/bolts/b" bolt/b; bw=$T/crew/bolts/b

(cd "$r" && wt config approvals add --yes >/dev/null 2>&1) || fail "wt config approvals add failed"
approvals=$XDG_CONFIG_HOME/worktrunk/approvals.toml
[[ -f $approvals ]] || fail "worktrunk's approvals are not in the scratch HOME"
grep -qF 'devenv shell -- env CREW_TEST_LIVE= tests/suite' "$approvals" || fail "the gate is not approved:"$'\n'"$(cat "$approvals")"

rev() { git -C "$r" rev-parse "$1"; }
vd=$r/.git/bolt-verify/b
# status: bolt-status.sh in the bolt's worktree; its output is in $out and its exit in $rc
status() { rc=0; out=$(cd "$bw" && sh .config/hooks/bolt-status.sh 2>&1) || rc=$?; }
# until_state <rev> <state>: wait until that revision's record reads the state
until_state() {
  local _
  for _ in $(seq 6000); do [[ $(sed -n 's/^State: //p' "$vd/$1.rec" 2>/dev/null) == "$2" ]] && return; /bin/sleep 0.1; done
  fail "the run of $1 never read $2:"$'\n'"$(cat "$vd/$1.rec" 2>&1)"
}
verify() { (cd "$bw" && devenv shell -- sh .config/hooks/bolt-verify.sh 2>&1); }
# merge <worktree> <target>: what a merge stage, a fix's merge or main-level ops runs there
merge() { (cd "$1" && wt merge "$2" --no-squash --no-remove </dev/null 2>&1); }
# commit <worktree> <add|rm> <file>: one commit adding or removing a file
commit() {
  if [[ $2 == add ]]; then touch "$1/$3"; git -C "$1" add "$3"; else git -C "$1" rm -q "$3"; fi
  git -C "$1" commit -qm "chore: $2 $3"
}

# A unit's merge into its bolt.
p=$T/crew/places/x
git -C "$r" worktree add -q -b unit/x "$p" bolt/b
commit "$p" add red
before=$(rev bolt/b)
export CREW_TEST_LIVE=1
expect_fail "FAIL  t-b" merge "$p" bolt/b
has "$out" "live=[]"; lacks "$out" "live=[1]"
eq "$(rev bolt/b)" "$before"
ok "a red suite refuses a unit's merge, naming the failing test, with the bolt unmoved and the live test kept out"

commit "$p" rm red
expect_ok merge "$p" bolt/b
has "$out" "2 passed (0 replayed), 0 failed"
eq "$(rev bolt/b)" "$(rev unit/x)"
ok "a green suite lets the unit's merge land"

r1=$(rev bolt/b)
until_state "$r1" green
status; eq "$rc" 0
has "$out" "State: green"; has "$out" "Rev: $r1"; has "$out" "Subject: chore: rm red"; has "$out" "Ended: "
[[ -z $(ls "$TMPDIR") ]] || fail "the run left its copy: $(ls "$TMPDIR")"
grep -qxF "verify-rev=[unset]" "$vd/$r1.log" || fail "the verification's suite inherited BOLT_VERIFY_REV:"$'\n'"$(cat "$vd/$r1.log")"
grep -qxF "copy-commits=[1] copy-tree=[$(git -C "$r" rev-parse "$r1^{tree}")] copy-status=[]" "$vd/$r1.log" ||
  fail "the verification's copy is not one commit holding the bolt's tree:"$'\n'"$(cat "$vd/$r1.log")"
grep -qxF "copy-outputs=[$r/.git/moon-outputs]" "$vd/$r1.log" || fail "the copy's archives are not the repository's:"$'\n'"$(cat "$vd/$r1.log")"
[[ -d $r/.git/moon-outputs ]] || fail "the verification made no $r/.git/moon-outputs"
ok "the merge's verification ends green at the bolt's head, in a copy of one commit holding the head's tree with the shared archives, its suite inherits no BOLT_VERIFY_REV, and its copy is removed"

# A fix's merge into its bolt.
f=$T/crew/places/fix-b--y
git -C "$r" worktree add -q -b fix/b/y "$f" bolt/b
commit "$f" add red
before=$(rev bolt/b)
expect_fail "FAIL  t-b" merge "$f" bolt/b
eq "$(rev bolt/b)" "$before"
commit "$f" rm red; commit "$f" add copy-red
expect_ok merge "$f" bolt/b
eq "$(rev bolt/b)" "$(rev fix/b/y)"
ok "a fix's merge is gated the same way"

r2=$(rev bolt/b)
until_state "$r2" red
status; eq "$rc" 1
has "$out" "State: red"; has "$out" "Rev: $r2"; has "$out" "Failed: t-b"; lacks "$out" "Failed: t-a"; has "$out" "Log: $vd/$r2.log"
grep -q "^FAIL  t-b" "$vd/$r2.log" || fail "the log does not hold the failure"
[[ ! -e $vd/$r1.rec && ! -e $vd/$r1.log ]] || fail "the ended run of $r1 was kept"
ok "a red verification names the failing test and its log, and the bolt's ended runs go"

# Two merges in a row while the first run is held: two runs side by side, each of its own revision.
touch "$T/hold"
z=$T/crew/places/z; git -C "$r" worktree add -q -b unit/z "$z" bolt/b
commit "$z" rm copy-red
expect_ok merge "$z" bolt/b; r3=$(rev bolt/b)
until_state "$r3" running
w=$T/crew/places/w; git -C "$r" worktree add -q -b unit/w "$w" bolt/b
commit "$w" add copy-red
expect_ok merge "$w" bolt/b; r4=$(rev bolt/b)
until_state "$r4" running
[[ $(sed -n 's/^State: //p' "$vd/$r3.rec") == running ]] || fail "the run of $r3 did not run beside $r4's"
status; eq "$rc" 1; has "$out" "State: running"; has "$out" "Rev: $r4"
rm "$T/hold"
until_state "$r3" green; until_state "$r4" red
status; eq "$rc" 1; has "$out" "State: red"; has "$out" "Rev: $r4"
ok "two runs side by side each finish on their own revision and keep their own outcome"

# A run cut off reads interrupted; a hand rerun of the head starts, and is refused while it is alive.
v=$T/crew/places/v; git -C "$r" worktree add -q -b unit/v "$v" bolt/b
commit "$v" rm copy-red
expect_ok merge "$v" bolt/b; r5=$(rev bolt/b)
until_state "$r5" green
sh -c 'exit 0' & dead=$!; wait "$dead"
rewrite "$vd/$r5.rec" "s/^State: .*/State: running/; s/^Pid: .*/Pid: $dead/; /^Ended: /d"
sum=$(cksum < "$vd/$r5.rec")
status; eq "$rc" 1; has "$out" "State: interrupted"; has "$out" "Rev: $r5"
eq "$(cksum < "$vd/$r5.rec")" "$sum"
ok "a run whose process is gone reads interrupted, and the reading writes nothing"

touch "$T/hold"
expect_ok verify; has "$out" "verifying bolt/b at $(git -C "$r" rev-parse --short "$r5") in the background"
for _ in $(seq 6000); do status; [[ $out == *"State: running"* ]] && break; /bin/sleep 0.1; done
eq "$rc" 1; has "$out" "State: running"; has "$out" "Rev: $r5"
expect_fail "a run of bolt/b at $(git -C "$r" rev-parse --short "$r5") is in progress" verify
rm "$T/hold"
until_state "$r5" green
status; eq "$rc" 0
ok "a hand rerun after a cut-off verifies the head again, and is refused while that run is alive"

echo "not a record" > "$vd/$r5.rec"
status; eq "$rc" 2; has "$out" "cannot read $vd/$r5.rec"; lacks "$out" "green"
expect_fail "cannot read $vd/$r5.rec" verify
eq "$(cat "$vd/$r5.rec")" "not a record"
ok "a record that can't be read is named, never read green, and left as it is"

# The bolt's merge onto main, from the bolt's worktree.
commit "$bw" add red
status; eq "$rc" 1; has "$out" "not verified: $(rev bolt/b)"; has "$out" "The newest recorded run, of "
ok "a head with no recorded run reads not verified"

before=$(rev main)
expect_fail "FAIL  t-b" merge "$bw" main
eq "$(rev main)" "$before"
ok "a red suite refuses the bolt's merge onto main, with main unmoved"

commit "$bw" rm red
expect_ok merge "$bw" main
eq "$(rev main)" "$(rev bolt/b)"
ok "a green bolt lands on main"

for _ in $(seq 6000); do grep -rqs "not verifying main" "$r/.git/wt/logs" && break; /bin/sleep 0.1; done
grep -rqs "not verifying main" "$r/.git/wt/logs" || fail "the post-merge hook of the landing never ran"
eq "$(ls "$r/.git/bolt-verify")" "b"
[[ ! -e $vd/$(rev main).rec ]] || fail "the landing on main was verified"
[[ -z $(ls "$TMPDIR") ]] || fail "a run left its copy: $(ls "$TMPDIR")"
ok "a merge onto main starts no verification"
