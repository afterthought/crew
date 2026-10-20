# Tasks

## 1. The landing's reading

- [x] 1.1 The files of a landing's session, a cover page, each unit's change and the bolt's diff against main as text, are a function of facts; proved by new cases in `tests/py/test_landing.py` (design, *Decisions* 2 and *Task notes* 1.1).
- [x] 1.2 A landing's session is written from the kit on the team's host into its head's folder and opened there, the same facts read for it as for the card, and refused off that host naming it; proved by the rewritten session-words case in `tests/py/test_cards.py` (design, *Decisions* 1, 2, 4 and *Task notes* 1.2).

## 2. The card

- [x] 2.1 A landing card built with a link opens its details with it, says the reading lands nothing, and leads its links with it, and one built without is as today; proved by cases in `tests/py/test_cards.py` (design, *Decisions* 3 and *Task notes* 2.1).
- [x] 2.2 A landing card is raised with its session started first, raised all the same saying so when it could not open, and its close ends the session; proved by the rewritten reading cases in `tests/py/test_cards.py` (design, *Decisions* 3, 6 and *Task notes* 2.2).

## 3. The commands

- [x] 3.1 `crew card session land/<bolt>` prints the running session's link, or starts it anew and changes the open card in place to carry the new link while the card waits on the user, and refuses a bolt that does not read proven; proved by a case in `tests/py/test_cards.py` (design, *Decisions* 4 and *Task notes* 3.1).
- [x] 3.2 `crew card wait land/<bolt>` prints the session's annotations as notes on the landing card and an approval as landing nothing, then forgets the decided session; proved by cases in `tests/py/test_cards.py` (design, *Decisions* 5 and *Task notes* 3.2).

## 4. The words

- [x] 4.1 The conductor's brief says the landing card links a reading, how its notes reach the conductor and that it lands nothing; proved by its words in `tests/t-briefs.sh` (design, *Task notes* 4.1).
- [x] 4.2 README, the crew skill and `plugin/bin/crew`'s usage describe the landing's session together; proved by `tests/t-docs.sh` (design, *Task notes* 4.2).

## 5. The journey

- [ ] 5.1 A landing's session is started with its card, given again by `crew card session`, ended and started again by a fix, and ended by the landing, on the stubs; proved by `tests/t-journey-land.sh` (design, *Task notes* 5.1).

## 6. Checks

- [ ] 6.1 The logic tier and the end-to-end tests this change affects are green (design, *Task notes* 6.1).
