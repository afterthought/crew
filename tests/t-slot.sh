# A host's tests run in its test slots (tests.9). With one slot, a second test waits while the first holds it and
# runs once it is let go; a test started inside another's slot, as t-suite's suites are, runs at once in it; a slot
# whose holder was killed is free again; the slot count is CREW_TEST_SLOTS, and a count that is not one is refused;
# with none given, it is the host's cores less two, at least two.
# Reads: tests/slot
. "${TESTS:?run crew tests through tests/run, which puts stub herdr, ssh and claude first}/lib.sh" || exit 2
# The stubs' sleep returns at once; the holders here wait with the real one.
zzz=$(type -a -P sleep | grep -vxF "$TESTS/stubs/sleep" | head -1)
[[ -x $zzz ]] || fail "no sleep on PATH but the stub's"
export CREW_TEST_SLOTS_DIR=$T/slots CREW_TEST_SLOTS=1
unset CREW_TEST_SLOT

# hold <name>: a test in a slot that marks itself started and holds its slot until $T/release-<name> exists
hold() {
  python3 "$TESTS/slot" bash -c 'echo "$CREW_TEST_SLOT" > "$1/started-$2"; while [ ! -e "$1/release-$2" ]; do "$3" 0.05; done' \
    _ "$T" "$1" "$zzz" &
}
# until_there <file>: wait for the file, with a limit that holds on a loaded host
until_there() { local _; for _ in $(seq 6000); do [[ -e $1 ]] && return; "$zzz" 0.05; done; fail "$1 never appeared"; }
# held: whether slot-0 is held by someone
held() { python3 -c 'import fcntl, os, sys
fd = os.open(sys.argv[1], os.O_RDWR)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    sys.exit(0)
sys.exit(1)' "$T/slots/slot-0"; }

hold first; first=$!
until_there "$T/started-first"
eq "$(cat "$T/started-first")" 0
held || fail "the first test does not hold slot-0"
hold second; second=$!
"$zzz" 0.5
[[ -e $T/started-second ]] && fail "the second test started while the first held the only slot"
kill -0 "$second" 2>/dev/null || fail "the second test ended instead of waiting for the slot"
touch "$T/release-first"; wait "$first"
until_there "$T/started-second"
touch "$T/release-second"; wait "$second"
held && fail "slot-0 is still held once both tests ended"
ok "with one slot, a second test waits while the first holds it, and runs once it is let go"

hold outer; outer=$!
until_there "$T/started-outer"
CREW_TEST_SLOT=0 python3 "$TESTS/slot" bash -c 'touch "$1/inner"' _ "$T" || fail "a test inside another's slot failed"
[[ -e $T/inner ]] || fail "a test inside another's slot did not run"
touch "$T/release-outer"; wait "$outer"
ok "a test started inside another's slot runs at once in it"

python3 "$TESTS/slot" "$zzz" 600 & killed=$!
for _ in $(seq 6000); do held && break; "$zzz" 0.05; done
held || fail "the test to be killed never took the slot"
kill -9 "$killed"; wait "$killed" 2>/dev/null || true
python3 "$TESTS/slot" bash -c 'touch "$1/after-kill"' _ "$T" || fail "no test ran after the holder was killed"
[[ -e $T/after-kill ]] || fail "the slot of a killed holder was not free again"
ok "a slot whose holder was killed is free again"

expect_fail "CREW_TEST_SLOTS is 'none', not a number of slots" env CREW_TEST_SLOTS=none python3 "$TESTS/slot" true
ok "a slot count that is not a number is refused"

# With no count given, a host's slots are its cores less two, at least two (tests.9, record 0021 as amended 2026-10-12).
count() { env -u CREW_TEST_SLOTS python3 -c 'import importlib.machinery, sys
print(importlib.machinery.SourceFileLoader("slot", sys.argv[1]).load_module().count())' "$TESTS/slot"; }
eq "$(count)" "$(python3 -c 'import os; print(max(2, (os.cpu_count() or 4) - 2))')"
ok "with no count given, a host's slots are its cores less two, at least two"
