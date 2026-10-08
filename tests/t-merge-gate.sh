# crew's merges are gated by its suite. With the real wt, in a scratch repository holding crew's .config/ and a
# stand-in suite whose t-b fails when the tree holds a file named red: a unit's, a fix's and a bolt's merge is
# refused while the suite is red, naming t-b, with the target unmoved, and lands once it is green; the live test
# stays out of the gate whatever the merging shell has set.
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
command -v wt >/dev/null || fail "this test needs worktrunk's wt"
gitconfig "$HOME"
# worktrunk keeps its approvals under the scratch HOME, never the user's; and a wt merge that runs this test as its
# own gate hands nothing of its own to the merges here.
export XDG_CONFIG_HOME=$HOME/.config TMPDIR=$T/tmp
unset $(env | sed -n 's/^\(WORKTRUNK_[A-Z_]*\)=.*/\1/p')
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
cat > "$r/tests/run" <<'EOF'
#!/bin/sh
echo "live=[${CREW_TEST_LIVE-unset}]"
echo "ok    t-a"
if [ -e red ]; then echo "FAIL  t-b   (scratch kept: none)"; echo "1 passed, 1 failed"; exit 1; fi
echo "ok    t-b"; echo "2 passed, 0 failed"
EOF
chmod +x "$r/tests/run"; commit_all "$r" "chore: start"
git -C "$r" branch bolt/b
git -C "$r" worktree add -q "$T/crew/bolts/b" bolt/b; bw=$T/crew/bolts/b

(cd "$r" && wt config approvals add --yes >/dev/null 2>&1) || fail "wt config approvals add failed"
approvals=$XDG_CONFIG_HOME/worktrunk/approvals.toml
[[ -f $approvals ]] || fail "worktrunk's approvals are not in the scratch HOME"
grep -qF 'devenv shell -- env CREW_TEST_LIVE= tests/run' "$approvals" || fail "the gate is not approved:"$'\n'"$(cat "$approvals")"

rev() { git -C "$r" rev-parse "$1"; }
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
has "$out" "2 passed, 0 failed"
eq "$(rev bolt/b)" "$(rev unit/x)"
ok "a green suite lets the unit's merge land"

# A fix's merge into its bolt.
f=$T/crew/places/fix-b--y
git -C "$r" worktree add -q -b fix/b/y "$f" bolt/b
commit "$f" add red
before=$(rev bolt/b)
expect_fail "FAIL  t-b" merge "$f" bolt/b
eq "$(rev bolt/b)" "$before"
commit "$f" rm red
expect_ok merge "$f" bolt/b
eq "$(rev bolt/b)" "$(rev fix/b/y)"
ok "a fix's merge is gated the same way"

# The bolt's merge onto main, from the bolt's worktree.
commit "$bw" add red
before=$(rev main)
expect_fail "FAIL  t-b" merge "$bw" main
eq "$(rev main)" "$before"
ok "a red suite refuses the bolt's merge onto main, with main unmoved"

commit "$bw" rm red
expect_ok merge "$bw" main
eq "$(rev main)" "$(rev bolt/b)"
ok "a green bolt lands on main"
