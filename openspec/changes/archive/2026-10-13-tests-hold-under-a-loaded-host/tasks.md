Recorded on 2026-10-13, after the build: each task names the commit that built it and the check that proves it.

# Tasks

## 1. Waits that hold under load

- [x] 1.1 `until_ok` in `tests/lib.sh` waits on a condition for up to ten minutes and ends as soon as it holds; every polling loop's limit is ten minutes and a background wait's thirty (34588ca). Proved by the end-to-end tests that wait through it, each passing only once its condition holds: `tests/t-journey-ops.sh` (the test slot held), `tests/t-journey-state.sh`, `tests/t-journey-prompts.sh`, `tests/t-journey-units.sh` and `tests/t-journey-land.sh`.
- [x] 1.2 `crew events --follow`'s test waits for its follower's tails to start and to go rather than sleeping (34588ca). Proved by `tests/t-journey-state.sh`: "crew events --follow never started its tails" and "a tail outlived crew events --follow" are its failures.
- [x] 1.3 A commit needed in an earlier second is backdated rather than slept for (34588ca). Proved by `tests/t-journey-land.sh`, whose carrying fix commits at `ago -1`, and `tests/t-journey-board.sh` and `tests/t-journey-review.sh`, whose commits are made at a time given (`commit_at`).
- [x] 1.4 The prompts journey's stop-short is said once the stage's wait has made its first look (0908779). Proved by `tests/t-journey-prompts.sh`: "the wait never looked at c" is its failure.
