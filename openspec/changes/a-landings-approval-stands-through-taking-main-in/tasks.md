# Tasks

## 1. The decisions take the bolt's own work as a fact

- [x] 1.1 `send_stands` holds a send when the heads match or the bolt's own commits are the same at both, and `work_said` says what a bolt gained or lost, or why crew can't tell (design, Decision 4; Task notes 1.1); passes `tests/py/test_landings.py` in `tests/suite logic`.
- [x] 1.2 `rows_unsent` keeps off the card a moved bolt whose send stands and returns, with its words, one whose work changed (design, Decision 4; Task notes 1.2); passes `tests/py/test_landings.py` in `tests/suite logic`.
- [x] 1.3 `landings_step` leaves an answered card for a ticked bolt that only took main in, keeps a held ticked bolt's send in its close or follow, saying so, and asks again with what changed for one whose work changed (design, Decision 4; Task notes 1.3); passes `tests/py/test_landings.py` in `tests/suite logic`.
- [ ] 1.4 `sent_left` lists a sent bolt at its head now when its send stands and sluice did not refuse it there, and names those whose head it can't read (design, Decision 4; Task notes 1.4); passes `tests/py/test_landings.py` in `tests/suite logic`.

## 2. The reads and acts

- [x] 2.1 `bolt_work` reads each bolt's gained and lost commits of its own between two heads where the forecasts are made, naming why when it can't, and the git behaviour it rests on is pinned (design, Decisions 1 to 3; Task notes 2.1); passes `tests/py/test_landings.py` in `tests/suite logic` and `tests/contract/test_git.py` in `tests/suite contract`.
- [ ] 2.2 `raise_landings` reads the card before its rows, makes one work read for the bolts that moved, posts no card for a bolt whose send stands, says what changed on a card that asks again, and keeps a held bolt's send on its close (design, Decision 5; Task notes 2.2); passes `tests/py/test_landings.py` in `tests/suite logic`.
- [ ] 2.3 `crew card read land/<kit>` prints what an earlier send still lands at each bolt's head now, with or without an open card, leaving out and naming a bolt it can't tell of (design, Decision 6; Task notes 2.3); passes `tests/py/test_landings.py` in `tests/suite logic`.

## 3. The briefs and docs

- [ ] 3.1 Main-level ops's brief says a send stands for a bolt that only took main in, read with `crew card read` with or without a card, and so do the user's words in its pane; the conductor's says a take-main fix on a ticked bolt leads to its landing (design, Decision 7; Task notes 3.1); passes `tests/suite t-briefs`.
- [ ] 3.2 README, the crew skill and `crew`'s usage say `crew card read land/<kit>` prints what an earlier send still lands with no card open (design, Decision 6; Task notes 3.2; `docs.2`); passes `tests/suite t-docs`.

## 4. The journey

- [ ] 4.1 A ticked bolt sluice refused takes main in by its fix, is asked for on no card, is read by ops with no card open and lands on the same send (design, Decisions 5 and 6; Task notes 4.1); passes `tests/suite t-journey-land`.

## 5. The affected tests

- [ ] 5.1 After `tests/moon-tasks` is run and `tests/moon.yml` committed for any test whose reads changed, `tests/suite --affected` ends with "0 failed".
