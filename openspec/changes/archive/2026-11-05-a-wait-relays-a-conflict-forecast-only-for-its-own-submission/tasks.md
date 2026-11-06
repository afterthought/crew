# Tasks

## 1. A forecast is relayed for its own head

- [x] 1.1 A bolt's forecast against main names the bolt's head it is of, in the wait's words and in the landings card's tell (design, Decision 1; Task notes 1.1). Passes `tests/py/test_forecast.py` and `tests/py/test_landings.py` (`tests/suite logic`).
- [x] 1.2 `forecasts_moved` says of each forecast a wait said as it began whose bolt moved from that head that it is not the bolt's now and nothing is taken in for it, of one whose head crew can't read that it can't tell and why, and nothing of one still at its head (design, Decision 2; Task notes 1.2). Passes `tests/py/test_forecast.py` (`tests/suite logic`).
- [x] 1.3 A wait's answer says those words before its own line, the bolts read where they live after a fetch (design, Decisions 2 and 3; Task notes 1.3). Verify `tests/suite t-journey-main-forecast` ends with "0 failed".

## 2. The conductor and the docs

- [x] 2.1 The conductor's brief has it take nothing in for a forecast the wait's answer says the bolt moved from, and README, the crew skill and `crew`'s usage header say what the wait says (design, Decision 4; Task notes 1.4; `docs.2`, `tests.6`). Verify `tests/suite t-briefs t-docs` ends with "0 failed".

## 3. The change's tests

- [x] 3.1 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
