# Tasks

## 1. A landing's close never waits on its own lock

- [x] 1.1 The tidy a landing's close runs on the team's host reads no landing, so a read that closes a bolt ends while it holds the bolt's lock, even when the tidy reads the plan from before the close (design, Decision 1; Task notes 1.1). Passes `tests/py/test_landing.py` (`tests/suite logic`).

## 2. The change's tests

- [x] 2.1 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
