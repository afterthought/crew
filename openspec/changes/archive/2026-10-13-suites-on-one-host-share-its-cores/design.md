Recorded on 2026-10-13, after the build, from the commits that built it.

# Design

Relies on `tests.9` (a host's tests are bounded by its cores, shared by every team), `tests.5` (one moon task per test, side by side) and `tests.8` (a busy host never reddens a verification). Touches `tests.md`'s area. Record 0021 decides it.

The bound is a property of the host, not of a suite, so it lives where every test passes, `tests/run`, and not in moon's own parallelism, which knows one suite at a time. A slot is a lock file held with `flock` for as long as the test or anything it leaves running holds the file open, so a killed test frees its slot without anyone cleaning up. macOS has no `flock` command, so `tests/slot` is a short Python script that takes the first free slot, polling, sets `CREW_TEST_SLOT` and execs the test; a test started with `CREW_TEST_SLOT` set runs in that slot.

The count began as the cores less two (d8edf3d), was halved the same day when eight tests at once left mac-studio no idle CPU (761d87e), and returned to the cores less two on 2026-10-12 (fd0d3d8), on the user's word, once the suite was in three tiers and a whole run with nothing replayed took 109 s with eight slots against 146 s with five.

## After deploy

None: crew is pulled, not deployed, and a host's next test takes its slots.
