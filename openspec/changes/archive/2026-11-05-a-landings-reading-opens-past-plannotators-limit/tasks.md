# Tasks

## 1. The reading holds a diff of any size

- [x] 1.1 A bolt's diff splits into parts at its files' changes, in git's order, each part within the 2 MB plannotator opens in one file, a file whose own change passes it named in its place with its size and cut nowhere (design, Decisions 1 and 2; Task notes 1.1). Passes `tests/py/test_landing.py` (`tests/suite logic`).
- [x] 1.2 A landing's reading names its parts `<nn>-<bolt>-diff-<k>-of-<m>.txt` when there are several, its page saying how many and naming each file left out with its size, their count, GitHub's compare view and the git command on the team's host (design, Decisions 1 and 2; Task notes 1.2). Passes `tests/py/test_landing.py` (`tests/suite logic`).
- [x] 1.3 A landing's reading past the limit is written as files each within it on disk (design, Decision 1; Task notes 1.3). Passes `tests/py/test_landing.py` (`tests/suite logic`).
- [x] 1.4 crew's stub of plannotator refuses a file over 2 MiB as plannotator 0.28.48 does, and a landing's reading still opens on it (design, Decision 3; Task notes 1.4). Verify `tests/suite t-journey-land` ends with "0 failed".

## 2. The docs

- [x] 2.1 README says how a landing's reading holds a diff past plannotator's limit (design, Not changed; Task notes 2.1; `docs.2`). Verify `tests/suite t-docs` ends with "0 failed".

## 3. The change's tests

- [x] 3.1 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
