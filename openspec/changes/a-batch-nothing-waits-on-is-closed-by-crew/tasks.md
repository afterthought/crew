# Tasks

## 1. crew reads a batch that waits on nothing closed and records why

- [x] 1.1 A decision beside `batch_closed` gives each batch card key whose every unit has landed or is held by a later batch, with the words saying why, proved by its cases in `tests/py/test_batches.py` (design, Task notes 1.1).
- [x] 1.2 Such a batch is no rail row, its card's withdrawal carries its words, `crew review --wait` raises no card for it, and the landing still waits only on the user's answers, proved by cases in `tests/py/test_rail.py` and `tests/py/test_batches.py` (design, Task notes 1.2).
- [ ] 1.3 The rail's sweep on the partition's main-level host records crew's close of each such batch once, as `batch.close` in the planner's name, before it reaches Pending You, and withdraws a card open under it with the same words, proved by the sweep's cases in `tests/py/test_rail.py` (design, Task notes 1.3).
- [ ] 1.4 The rail's sweep lines name a close with no card as such, proved by a `rail_text` case in `tests/py/test_rail.py` (design, Task notes 1.4).
- [ ] 1.5 The logic tier is green: `devenv shell -- moon run tests:logic`.

## 2. The documents say it

- [ ] 2.1 README and the planner's brief say a batch's row and card end when the user answers or when the batch waits on nothing, and README lists `batch.close` among the run record's acts, proved by `tests/suite briefs docs` passing (design, Task notes 2.1).
- [ ] 2.2 `tests/suite --affected` passes once the change is done.
