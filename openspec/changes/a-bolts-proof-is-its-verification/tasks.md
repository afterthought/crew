# Tasks

## 1. The proof goes

- [x] 1.1 `crew prove`, its parser entry, its owed end and its delivery go; a proof line a stages file holds from before is dropped, owed nothing: `tests/py/test_parser.py`, `tests/py/test_stage_ends.py`, `tests/py/test_wait.py`, `tests/t-journey-fix.sh` (design: *The proof's stage goes, and old lines are dropped*; `teams.4`, `briefs.1`).

## 2. The landing waits on the verification

- [x] 2.1 The rail's land row carries the tell that lands a bolt only once its verification is green, and says the verification with no command until then; `crew bolts` shows each held bolt's verification: `tests/py/test_rail.py`, `tests/t-journey-land.sh` (design: *The rail's land row waits on the verification*; `plan.16`, `tests.5`, `code.7`).
- [x] 2.2 The card hook's landing form refuses steps: `tests/py/test_cards.py` (design: *The landing card has no steps*; `briefs.11`, `briefs.13`).

## 3. The briefs and docs

- [x] 3.1 The conductor posts the landing card once the verification is green, asking only for the landing; ops proves and deploys nothing and tells the conductor what it waits on; main-level ops checks the verification before it submits; README, CLAUDE.md and the skill say so: `tests/t-briefs.sh`, `tests/t-docs.sh`, and `tests/suite --affected` ends with "0 failed" (`briefs.1`, `briefs.3`, `briefs.11`, `plan.16`, `tests.6`).
