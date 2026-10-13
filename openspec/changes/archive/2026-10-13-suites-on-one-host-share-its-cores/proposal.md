Recorded on 2026-10-13, after the build, from the commits that built it: d8edf3d, 761d87e and fd0d3d8, with record 0021 as amended.

# Proposal

## Why

On 2026-10-10 mac-studio's load reached 247 while crw-1's verification ran 48 of 50 tests unreplayed as moon tasks side by side, beside crw-2's coders running crew's tests and a swancloud flake check (signal 2026-10-10-swancloud-design-c0b2ca89/01); on 2026-10-11 it reached 386. Each suite sized its parallelism as if it were alone on the host, so two teams' suites loaded the host past its cores and a busy host reddened verifications for reasons that were not the bolt's (`tests.9`).

## What Changes

- Every crew test on a host, whichever worktree, team or suite runs it, takes one of the host's test slots first and holds it until the test ends: a lock file under `~/.cache/crew/test-slots`, held with `flock`, let go by the system when the test ends, killed or not (`tests/slot`, run by `tests/run`). A test that finds no slot free waits its turn.
- The host has `CREW_TEST_SLOTS` slots, else its cores less two, at least two: each test keeps about a core busy starting processes, and two are left for the agents and the user beside them. A count that is not a number is refused.
- A suite started inside a test's slot, as `t-suite`'s are, runs in that slot rather than waiting on another its own test holds.

## Capabilities

### Modified Capabilities

- `test-suite`: every suite on a host shares the host's test slots.

## Impact

`tests/slot`, `tests/run`, `CLAUDE.md`, README, `docs/architecture/tests.md` (`tests.9`), record 0021; `tests/t-slot.sh`.

## Touches

```
tests/slot
tests/run
tests/t-slot.sh
```
