# Tasks

## 1. What crew reads of main

- [x] 1.1 Each kit's read names the revision of main it read at, `main_at`, from the `rev-parse` it already makes (design, Decision 2; Task notes 1.1); passes `tests/contract/test_gather.py`, `tests/suite contract` ending with "0 failed".
- [x] 1.2 The landings card's forecast hands back the revision of main it forecast against, or none when it could not fetch or read it (design, Decision 1; Task notes 1.2); passes `tests/py/test_landings.py`, `tests/suite logic` ending with "0 failed".

## 2. A row forecast to conflict with main takes main first

- [x] 2.1 A decision reads, from the run record, the conflict with main recorded for a bolt at its present head, by a wait or by a raise, and none for an older head, a queued submission or an unread forecast (design, Decision 3; Task notes 2.1); passes `tests/py/test_forecast.py`, `tests/suite logic` ending with "0 failed".
- [x] 2.2 A row forecast to conflict with main, by the card's forecast or the record, or carrying a take-main fix, is held with no box saying it takes main first, and a conflict only with a row above holds nothing (design, Decision 3; Task notes 2.2); passes `tests/py/test_landings.py`, `tests/suite logic` ending with "0 failed".
- [x] 2.3 The card's raise forecasts every row against main first, holds those taking main first, forecasts the rest among themselves, and keeps the revision it forecast against on the main level's host (design, Decisions 2 and 3; Task notes 2.3); passes `tests/py/test_landings.py`, `tests/suite logic` ending with "0 failed".

## 3. The conductor is told the fix

- [x] 3.1 A row newly taking main first by the raise's forecast tells its conductor the take-main fix once for the same bolt head and revision of main, whichever forecast recorded it first, with `--bolt` while the team holds two, and records the forecast only once the tell went through (design, Decision 4; Task notes 3.1); passes `tests/py/test_landings.py`, `tests/suite logic` ending with "0 failed".

## 4. Main moving raises the card

- [x] 4.1 A decision names the kits whose open landings card was forecast at a revision of main other than the one the survey read, and says a kit whose read names none (design, Decision 2; Task notes 4.1); passes `tests/py/test_landings.py`, `tests/suite logic` ending with "0 failed".
- [ ] 4.2 The rail's read with its sweep, on the partition's main machine, raises each such kit's card again and says so, fetching and raising nothing for a kit whose main has not moved (design, Decision 2; Task notes 4.2); passes `tests/py/test_rail.py`, `tests/suite logic` ending with "0 failed".

## 5. The rail and the wait

- [ ] 5.1 The rail's land row says a bolt with a conflict with main recorded at its present head takes main first, and leaves it out of the tell that lands, while a conflict at an older head holds nothing (design, Decision 5; Task notes 5.1); passes `tests/py/test_rail.py`, `tests/suite logic` ending with "0 failed".
- [ ] 5.2 A wait that records a bolt forecast to conflict with what main has landed raises its kit's landings card at once, and one with a queued submission raises nothing (design, Decision 6; Task notes 5.2); passes `tests/py/test_forecast.py`, `tests/suite logic` ending with "0 failed".

## 6. The send stands

- [ ] 6.1 After the user's send, a ticked bolt held only to take main in keeps the send standing and the card is left, while a ticked bolt held for any other fix or for sluice's refusal is held as before (design, Decision 7; Task notes 6.1); passes `tests/py/test_landings.py`, `tests/suite logic` ending with "0 failed".

## 7. The command's wiring

- [ ] 7.1 On the stubs, main moving under a proven row makes `crew rail` on the main level's host raise the kit's card holding the row as taking main first and tell its conductor the take-main fix, and a second `crew rail` tells and raises nothing, with `tests/moon.yml` in step with the test's reads (design, Decisions 2 to 4; Task notes 7.1); verify `tests/suite t-journey-land` ends with "0 failed".

## 8. The words

- [ ] 8.1 The conductor's and main-level ops's briefs, README and the crew skill say a waiting bolt is forecast again when main moves and a row conflicting with main takes main first, its conductor told the fix (design, Decision 4; Task notes 8.1); verify `tests/suite t-docs` ends with "0 failed".

## 9. The change as a whole

- [ ] 9.1 Every test the change affects passes; verify `tests/suite --affected` ends with "0 failed".
