# Tasks

## 1. crew reads a gate's step

- [x] 1.1 A user's step whose words are one link alone is read as a gate, and its card's facts carry the link and the commit; proved by new cases in `tests/py/test_ops.py` (design, *Task notes* 1.1).
- [x] 1.2 A gate's rail row says the deploy waits at its gate for the user, with the link; proved by a case in `tests/py/test_ops.py` (design, *Task notes* 1.2).
- [x] 1.3 Each waiting operation in `ops.environments` says whether it is a gate and gives its link; proved by a case in `tests/py/test_ops.py` (design, *Task notes* 1.3).

## 2. The gate's card

- [x] 2.1 A gate's card is the user's `do` asking them to approve the deploy at its gate, its one step and its where the gate's link, and every other step's card is unchanged; proved by new cases in `tests/py/test_cards.py` (design, *Decisions* and *Task notes* 2.1).

## 3. The views

- [x] 3.1 The board's Operation lane and main-level ops's view say a gate's step waits at its gate, not that it comes after its commit; proved by cases in `tests/py/test_board.py` (design, *Task notes* 3.1).

## 4. The brief

- [x] 4.1 Main-level ops's *Deploying main* says how a gate is recorded, that no offer is posted for it, and how its step ends; proved by its words in `tests/t-briefs.sh` (design, *Task notes* 4.1).

## 5. Checks

- [ ] 5.1 The logic tier, `t-briefs` and the affected tests are green (design, *Task notes* 5.1).
