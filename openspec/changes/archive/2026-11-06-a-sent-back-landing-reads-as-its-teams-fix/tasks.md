# Tasks

## 1. A sent-back landing reads as its team's fix

- [x] 1.1 A refusal sluice made for the bolt's own content stands at its head through every later submit that submitted nothing there, and no reader says a stop over it (design, Decision 1; Task notes 1.1). Passes `tests/py/test_landing.py` and `tests/py/test_landings.py` (`tests/suite logic`).
- [x] 1.2 `crew bolt submit` submits nothing at a head sluice sent back, naming what failed from sluice's record, the team's fix with its command and the submit once that fix has merged (design, Decisions 2 and 3; Task notes 1.2). Passes `tests/py/test_landing.py` (`tests/suite logic`); verify `tests/suite t-journey-land` ends with "0 failed".
- [x] 1.3 A landing sluice sends back tells ops the team's fix and the submit once it has merged, never to submit again as it is (design, Decision 3; Task notes 1.3). Passes `tests/py/test_landing.py` (`tests/suite logic`).
- [x] 1.4 The landings card's row, the rail's land line and `crew bolts` say the sent-back landing is its team's fix and ops submits it again once that fix has merged (design, Decision 4; Task notes 1.4). Passes `tests/py/test_landings.py`, `tests/py/test_rail.py`, `tests/py/test_bolt_submissions.py` and `tests/py/test_bolt_commands.py` (`tests/suite logic`).

## 2. The docs and the change's tests

- [x] 2.1 README, the crew skill and `crew`'s usage header say a sent-back landing is its team's fix (`docs.2`; Task notes 2.1). Verify `tests/suite t-docs` ends with "0 failed".
- [x] 2.2 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
