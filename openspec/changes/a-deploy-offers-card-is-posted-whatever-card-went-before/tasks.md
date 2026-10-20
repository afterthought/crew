# Tasks

## 1. What a card follows

- [x] 1.1 A card follows only a card posted in its own owner's name, and a deploy's card follows only its environment's declined deploy card; proved by cases in `tests/py/test_cards.py` (design, *Decisions* 1 and *Task notes* 1.1).
- [x] 1.2 The run record of 2026-10-19 23:54Z to 2026-10-20 00:16Z, as a case: deneb's deploy at `ddcf2cb` follows no card, and a post Pending You refuses is recorded refused in its words; proved by a case in `tests/py/test_cards.py` (design, *Context* and *Task notes* 1.2).

## 2. The offer again

- [x] 2.1 An offer of the commit already offered, with the same files, posts its card when main-level ops holds none open, and writes no second offer; proved by cases in `tests/py/test_ops.py` (design, *Decisions* 2 and *Task notes* 2.1).

## 3. A row owing its card

- [x] 3.1 The board's text, its JSON and every agent's view say that a row with no card open owes its card because its last post was refused; proved by cases in `tests/py/test_board.py` (design, *Decisions* 3 and *Task notes* 3.1).
- [x] 3.2 The page's marker says the same, with Pending You's words in its title; proved by a case in `tests/py/test_page.py` (design, *Decisions* 3 and *Task notes* 3.2).

## 4. The words

- [x] 4.1 README says an offer again posts a card that was refused, that a marker says a refused post, and that a deploy card follows no landing card; proved by `tests/t-docs.sh` (design, *Task notes* 4.1).

## 5. Checks

- [ ] 5.1 The logic tier and the end-to-end tests this change affects are green (design, *Task notes* 5.1).
