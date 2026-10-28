# Tasks

## 1. Which bolts are left

- [x] 1.1 A decision gives a kit's left bolts from its card, the user's ticks, the heads and the run record, and a reader gives them from the run record alone, a tick, a moved head or a landing on the user's words ending one (design, Decision 1; Task notes 1.1); passes `tests/py/test_landings.py`, `tests/suite logic` ending with "0 failed".
- [x] 1.2 The card's raise marks every left bolt unticked and records the kit's left set only when it changes (design, Decision 1; Task notes 1.2); passes `tests/py/test_landings.py`, `tests/suite logic` ending with "0 failed".

## 2. A left row says it would take main first

- [x] 2.1 A left bolt forecast to conflict with main keeps its box, its row saying it would take main first once ticked, while a left bolt with a fix in flight or sluice's refusal is held as before (design, Decision 2; Task notes 2.1); passes `tests/py/test_landings.py` and `tests/py/test_cards.py`, `tests/suite logic` ending with "0 failed".

## 3. No fix while left

- [x] 3.1 The card's raise tells no take-main fix for a left bolt, records its forecast once as found while left and changes a waiting card in place the first time, and tells the fix at the same heads once the bolt is ticked (design, Decision 3; Task notes 3.1); passes `tests/py/test_landings.py`, `tests/suite logic` ending with "0 failed".

## 4. A stop in ops's pane

- [x] 4.1 `crew bolt leave <bolt>... --excerpt` records a stop only on words crew reads as the user's in the caller's transcript, holding none of the words, refuses as `crew bolt submit --excerpt` refuses, and raises the kit's card (design, Decision 4; Task notes 4.1); passes `tests/py/test_pane_landing.py` and `tests/py/test_parser.py`, `tests/suite logic` ending with "0 failed".

## 5. The conductor's wait

- [x] 5.1 A conductor's wait says a left bolt's conflict with main once, gives no fix and records it as found while left, and gives the fix at the same heads once the bolt is ticked (design, Decision 5; Task notes 5.1); passes `tests/py/test_forecast.py`, `tests/suite logic` ending with "0 failed".

## 6. Reading the send

- [x] 6.1 `crew card read` of an answered landings card raises it first, so a ticked bolt that was left and conflicts is held taking main first and its conductor told the fix, and leaves that bolt out of the command it prints, saying the send stands for it (design, Decision 6; Task notes 6.1); passes `tests/py/test_card_commands.py`, `tests/suite logic` ending with "0 failed".

## 7. The rail

- [x] 7.1 The rail's land row says a left bolt in conflict with main takes main first once ticked and leaves it out of the tell that lands (design, Decision 7; Task notes 7.1); passes `tests/py/test_rail.py`, `tests/suite logic` ending with "0 failed".

## 8. The command's wiring

- [ ] 8.1 On the stubs, main moving under a left bolt keeps its row and tells its conductor nothing, and a send ticking it then read by `crew card read` tells the take-main fix and submits nothing of it, with `tests/moon.yml` in step with the test's reads (design, Decisions 1 to 6; Task notes 8.1); verify `tests/suite t-journey-land` ends with "0 failed".

## 9. The words

- [x] 9.1 The usage, README, the crew skill and the conductor's and main-level ops's briefs say a left bolt is forecast with no fix until ticked and name `crew bolt leave` (design, Decisions 4 to 6; Task notes 9.1); verify `tests/suite t-docs` ends with "0 failed".

## 10. The change as a whole

- [ ] 10.1 Every test the change affects passes; verify `tests/suite --affected` ends with "0 failed".
