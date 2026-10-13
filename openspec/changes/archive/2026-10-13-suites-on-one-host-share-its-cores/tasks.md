Recorded on 2026-10-13, after the build: each task names the commit that built it and the check that proves it.

# Tasks

## 1. The host's test slots

- [x] 1.1 `tests/run` runs every test in one of the host's slots, `tests/slot`, a lock held with `flock` until the test ends, killed or not, a test with none free waiting its turn, and a test started inside another's slot running in it (d8edf3d). Proved by `tests/t-slot.sh`: "with one slot, a second test waits while the first holds it, and runs once it is let go", "a test started inside another's slot runs at once in it", "a slot whose holder was killed is free again".
- [x] 1.2 A host's slots are `CREW_TEST_SLOTS`, else its cores less two, at least two, and a count that is not a number is refused (d8edf3d, 761d87e, fd0d3d8). Proved by `tests/t-slot.sh`: "with no count given, a host's slots are its cores less two, at least two", added with this record, and "a slot count that is not a number is refused".
