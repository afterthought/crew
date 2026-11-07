# Tasks

## 1. A forecast reads what a unit already took

- [x] 1.1 A later unit is forecast against one ahead of it from the newest of that one's work it holds: nothing when it holds that one's head, the head its place took only while that one's line was rewritten and nothing newer is shared, else their merge base (design, Decisions 1 and 2; Task notes 1.1). Passes `tests/py/test_forecast.py` (`tests/suite logic`).
- [x] 1.2 What a unit holds is read from git in the kit's main checkout, and a unit that merged the one ahead of it in its place is forecast no conflict and starts no settle (design, Decision 1; Task notes 1.2). Passes `tests/contract/test_git.py` (`tests/suite contract`).
- [x] 1.3 README says what a forecast between two units is read from (Task notes 1.3). Verify `tests/suite t-docs` ends with "0 failed".

## 2. The change's tests

- [x] 2.1 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
