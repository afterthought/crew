# Tasks

## 1. One results section in six briefs

- [x] 1.1 `crew.py` builds the results section once, as `RESULTS` beside `SENDERS`, and both the team's and the main level's tokens fill `{{RESULTS}}` with it (design: *What the section says*; Task notes 1.1).
- [x] 1.2 The conductor, ops, main-ops, construct, coder and verify briefs each carry `{{RESULTS}}` once, where the design places it, and every brief still prints with no token unfilled (design: *Where each brief carries it*; Task notes 1.2).
- [x] 1.3 `tests/t-briefs.sh` pins the section's phrases in each of the six briefs and fails unless the section reads the same in all six (Task notes 1.3; `tests.6`).
- [x] 1.4 `briefs.7` names its sources and is no longer listed in `_open.md` as accepted but not built (design: *The rule's record*; Task notes 1.4).
- [x] 1.5 `devenv shell -- tests/run` ends with "0 failed".
