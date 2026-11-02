# crew's suite runs as moon tasks. With the shell's real moon, in a scratch repository holding crew's
# .moon/workspace.yml, tests/suite and tests/moon-tasks, a stand-in tests/run (it fails a test when plugin/bin/ holds
# red-<name>) and three stand-in tests: a first run runs every test side by side and replays none; a second replays
# all; a test-only edit reruns that test alone; an edit to crew's command core reruns all, and one to a plugin/ path
# outside it reruns only the test naming it on its # Reads: line (tests.10); a red test is named on one FAIL line with
# its output while the others still run, the exit is non-zero, and it runs again on the next run; __pycache__ under
# plugin/ changes no hash; --force replays nothing; the live test gets no task and never runs; a new test with no
# task, and a test reading a file of crew's its task doesn't name, refuse the run before anything runs; a second
# checkout replays the first's passes; --affected runs only the tests a branch's edits touch, uncommitted ones
# counted, and with none says so and passes.
# Reads: .moon/workspace.yml tests/suite tests/moon-tasks
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
[[ $(moon --version 2>/dev/null) == "moon 2."* ]] || fail "this test needs moon 2 from crew's toolchain (.prototools), not: $(moon --version 2>&1)"
gitconfig "$HOME"
# The stubs' sleep returns at once; the stand-in waits with the real one.
zzz=$(type -a -P sleep | grep -vxF "$TESTS/stubs/sleep" | head -1)
[[ -x $zzz ]] || fail "no sleep on PATH but the stub's"

r=$T/repo
mkdir -p "$r/.moon" "$r/tests/stubs" "$r/plugin/bin" "$r/plugin/lib" "$r/plugin/roles"
cp "$CREW/.moon/workspace.yml" "$r/.moon/"; cp "$CREW/tests/suite" "$CREW/tests/moon-tasks" "$r/tests/"
printf '.moon/cache/\n__pycache__/\n' > "$r/.gitignore"
touch "$r/devenv.nix" "$r/devenv.lock" "$r/tests/lib.sh" "$r/tests/slot" "$r/tests/stubs/herdr" "$r/README.md"
touch "$r/plugin/bin/crew" "$r/plugin/lib/"{crew,record,gather,transcript,questions}.py "$r/plugin/roles/coder.md"
echo 'print(1)' > "$r/plugin/lib/plan.py"
# The stand-in tests/run: each run is logged in $T/ran.log. With $T/barrier, each test waits until all three have
# started, so a run that is not side by side fails.
cat > "$r/tests/run" <<EOF
#!/bin/sh
n=\${1#t-}; n=t-\${n%.sh}
echo "\$n" >> "$T/ran.log"
if [ -e "$T/barrier" ]; then
  mkdir -p "$T/started"; touch "$T/started/\$n"; i=0
  while [ "\$(ls "$T/started" | wc -l)" -lt 3 ]; do
    i=\$((i + 1)); [ \$i -gt 600 ] && { echo "FAIL  \$n   (never ran beside the others)"; exit 1; }; "$zzz" 0.1
  done
fi
if [ -e "plugin/bin/red-\$n" ]; then echo "FAIL  \$n   (scratch kept: none)"; echo "      \$n is red"; echo "0 passed, 1 failed"; exit 1; fi
echo "ok    \$n"; echo "1 passed, 0 failed"
EOF
chmod +x "$r/tests/run"
for n in a b c; do echo "# t-$n: a stand-in test." > "$r/tests/t-$n.sh"; done
echo "# Reads: plugin/roles/" >> "$r/tests/t-c.sh"
(cd "$r" && tests/moon-tasks) || fail "tests/moon-tasks could not write the tasks"
git init -q "$r"; commit_all "$r" "chore: start"
# link <checkout>: its archives a link into the git common dir, as crew's devenv shell makes it
link() {
  local common; common=$(git -C "$1" rev-parse --path-format=absolute --git-common-dir)
  mkdir -p "$common/moon-outputs" "$1/.moon/cache"; ln -s "$common/moon-outputs" "$1/.moon/cache/outputs"
}
link "$r"
: > "$T/ran.log"
# suite [args...]: tests/suite in the repository; its output is in $out and its exit in $rc
suite() { rc=0; out=$(cd "$r" && tests/suite "$@" 2>&1) || rc=$?; }
# ran: the tests run since the last call, one name per line, in order
ran() { sort "$T/ran.log" | tr '\n' ' ' | sed 's/ $//'; : > "$T/ran.log"; }

touch "$T/barrier"
MOON_CONCURRENCY=3 suite
rm "$T/barrier"
eq "$rc" 0
has "$out" "ok    t-a"$'\n'"ok    t-b"$'\n'"ok    t-c"$'\n'"3 passed (0 replayed), 0 failed"
lacks "$out" "(replayed)"
eq "$(ran)" "t-a t-b t-c"
ok "a first run runs every test side by side and replays none"

suite
eq "$rc" 0
has "$out" "ok    t-a   (replayed)"; has "$out" "ok    t-b   (replayed)"; has "$out" "ok    t-c   (replayed)"
has "$out" "3 passed (3 replayed), 0 failed"
eq "$(ran)" ""
ok "a second run on the same tree replays every test"

echo "echo edited" >> "$r/tests/t-b.sh"
suite
eq "$rc" 0
has "$out" "ok    t-a   (replayed)"$'\n'"ok    t-b"$'\n'"ok    t-c   (replayed)"$'\n'"3 passed (2 replayed), 0 failed"
eq "$(ran)" "t-b"
ok "an edit to one test reruns that test alone"

echo 'print(2)' > "$r/plugin/lib/plan.py"
suite
eq "$rc" 0; has "$out" "3 passed (0 replayed), 0 failed"
eq "$(ran)" "t-a t-b t-c"
ok "an edit to crew's command core reruns every test"

echo "edited" >> "$r/plugin/roles/coder.md"
suite
eq "$rc" 0; has "$out" "ok    t-a   (replayed)"$'\n'"ok    t-b   (replayed)"$'\n'"ok    t-c"$'\n'"3 passed (2 replayed), 0 failed"
eq "$(ran)" "t-c"
ok "an edit to a plugin/ path outside the core reruns only the test that names it"

touch "$r/plugin/bin/red-t-b"
suite
eq "$rc" 1
has "$out" "ok    t-a"$'\n'"FAIL  t-b"$'\n'"ok    t-c"$'\n'
has "$out" "── t-b failed:"$'\n'"      FAIL  t-b   (scratch kept: none)"$'\n'"            t-b is red"
has "$out" "2 passed (0 replayed), 1 failed"
eq "$(grep -c '^FAIL  ' <<<"$out")" 1
eq "$(ran)" "t-a t-b t-c"
ok "a red test is named on one FAIL line with its output, the others still run, and the run fails"

suite
eq "$rc" 1
has "$out" "ok    t-a   (replayed)"$'\n'"FAIL  t-b"$'\n'"ok    t-c   (replayed)"$'\n'
has "$out" "2 passed (2 replayed), 1 failed"
eq "$(ran)" "t-b"
ok "a test that failed runs again on the next run, never replayed"

rm "$r/plugin/bin/red-t-b"
suite
eq "$rc" 0; has "$out" "ok    t-a   (replayed)"$'\n'"ok    t-b"$'\n'"ok    t-c   (replayed)"$'\n'"3 passed (2 replayed), 0 failed"
eq "$(ran)" "t-b"
ok "back on a tree that passed, the others replay and the test that last failed here runs"

mkdir -p "$r/plugin/lib/__pycache__"; echo junk > "$r/plugin/lib/__pycache__/plan.cpython.pyc"
suite
eq "$rc" 0; has "$out" "3 passed (3 replayed), 0 failed"
eq "$(ran)" ""
ok "__pycache__ under plugin/ changes no hash"

suite --force
eq "$rc" 0; has "$out" "3 passed (0 replayed), 0 failed"
eq "$(ran)" "t-a t-b t-c"
suite b
eq "$rc" 0; has "$out" "ok    t-b   (replayed)"$'\n'"1 passed (1 replayed), 0 failed"
ok "--force runs every test without the cache, and named tests run alone"

echo "# t-sites-live: the live test." > "$r/tests/t-sites-live.sh"
(cd "$r" && tests/moon-tasks) || fail "tests/moon-tasks could not write the tasks"
lacks "$(cat "$r/tests/moon.yml")" "t-sites-live"
CREW_TEST_LIVE=1 suite
eq "$rc" 0; has "$out" "3 passed (3 replayed), 0 failed"; lacks "$out" "t-sites-live"
suite sites-live
eq "$rc" 2; has "$out" "t-sites-live is no task"
eq "$(ran)" ""
ok "the live test gets no task and never runs, CREW_TEST_LIVE set or not"

echo "# t-d: a new test." > "$r/tests/t-d.sh"
suite
eq "$rc" 2; has "$out" "t-d has no task in tests/moon.yml"; has "$out" "run tests/moon-tasks and commit tests/moon.yml"
lacks "$out" "passed"
# Written through %s, so tests/moon-tasks reading this file finds no read of README.md here.
printf '# t-d: a new test.\ncat "$%s/README.md"\n' CREW > "$r/tests/t-d.sh"
(cd "$r" && tests/moon-tasks) >/dev/null 2>&1 && fail "tests/moon-tasks wrote the tasks of a test reading what it doesn't name"
suite
eq "$rc" 2; has "$out" "t-d reads README.md, which its task's inputs don't name"
lacks "$out" "passed"
eq "$(ran)" ""
rm "$r/tests/t-d.sh"
ok "a test with no task, or reading a file its task doesn't name, refuses the run before anything runs"

# A second checkout of the tree the first passed replays the first's passes.
commit_all "$r" "chore: the tree that passed"
git -C "$r" worktree add -q -b second "$T/second" HEAD; link "$T/second"
rc=0; out=$(cd "$T/second" && tests/suite 2>&1) || rc=$?
eq "$rc" 0; has "$out" "3 passed (3 replayed), 0 failed"
eq "$(ran)" ""
ok "a second checkout replays the passes of the first"

git -C "$r" checkout -q -b unit/x
suite --affected
eq "$rc" 0; has "$out" "no test is affected"; has "$out" "0 passed (0 replayed), 0 failed"
echo "echo edited" >> "$r/tests/t-c.sh"; commit_all "$r" "test: edit t-c"
echo "echo edited" >> "$r/tests/t-a.sh"
suite --affected
eq "$rc" 0
has "$out" "ok    t-a"$'\n'"ok    t-c"$'\n'"2 passed (0 replayed), 0 failed"; lacks "$out" "t-b"
eq "$(ran)" "t-a t-c"
ok "--affected runs only the tests a branch's edits touch, uncommitted ones counted, and with none says so"
