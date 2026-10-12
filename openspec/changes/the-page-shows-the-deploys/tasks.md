# Tasks

## 1. The deploys, read from the record

- [x] 1.1 `ops.environments` folds the ops entries and the landings into each environment's deploys and the operations waiting, and `ops.carried` gives the bolts a deploy carried or the commit the record can't place, with logic cases in `tests/py/test_ops.py` (design: *A deploy, folded from the entries*, *What a deploy carried*; `plan.14`, `read.1`, `code.7`).

## 2. The board

- [x] 2.1 `rail_record` hands the board the entries; the Operation lane, `crew board --json`'s `environments` and the operator's view show the deploys and the operations waiting with their markers, with logic cases in `tests/py/test_board.py` and one wiring step in `tests/t-journey-board.sh` (design: *The board and the agents' views*; `state.4`, `code.8`).

## 3. The page

- [x] 3.1 The page's data holds the deploys with each carried bolt's release notes, its board view draws the environments in the Operation lane, and its deploys view draws each environment's timeline, with logic cases in `tests/py/test_page.py` and the page's JSON checked in `tests/t-journey-board.sh` (design: *The deploys view*).
- [x] 3.2 README and SKILL.md say what the Operation lane and the deploys view show, and `tests/t-docs.sh` passes (`docs.2`).
