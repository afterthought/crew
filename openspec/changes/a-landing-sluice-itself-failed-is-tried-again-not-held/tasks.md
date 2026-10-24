# Tasks

## 1. crew tells the bolt's refusals from stops

- [x] 1.1 crew judges a landing's end the bolt's only from sluice's record of the submission, a conflict or a check that ran and failed or was cut off, and gives any other end words saying what stopped it, against a fixture of sluice 0.36.4's failed records (design, Decision 1; Task notes 1.1). Passes `tests/py/test_landing.py`.
- [ ] 1.2 `crew bolt submit`'s judgment of what a landing came to reads that blame from the wait's record and from sluice's listing after exit 3, the bolt's words unchanged and a stop's telling ops to submit it again once cleared, with no new word (Decision 1 and 4; Task notes 1.2). Passes `tests/py/test_landing.py`.
- [ ] 1.3 A stop is recorded as `bolt.submit` with its head, its words and `Outcome: stopped`, and no refusal, and crew reads each bolt's last stop from the run record (Decision 2; Task notes 1.3). Passes `tests/py/test_landing.py`.

## 2. A stopped bolt keeps its row and its word

- [ ] 2.1 A bolt stopped at its head keeps its box on its kit's landings row and the rail's line says what stopped it and that ops submits it again, the tell naming it (Decision 3; Task notes 2.1). Passes `tests/py/test_landings.py` and `tests/py/test_rail.py`.
- [ ] 2.2 The landings card's row says the stop on its face and in its box's detail (Decision 3; Task notes 2.2). Passes `tests/py/test_cards.py`.
- [ ] 2.3 An answered landings card is left while a ticked bolt is stopped, a card that follows names it as still landing with what stopped it, and `crew card read` prints the stop beside it (Decision 3; Task notes 2.3). Passes `tests/py/test_landings.py`.

## 3. End to end, the brief and the docs

- [ ] 3.1 The stub sluice records a failed check's result, checks it could not run and a conflict's paths as sluice 0.36.4 does, and a landing whose checks could not run keeps its box and lands on a second `crew bolt submit` with no new word (Decision 6; Task notes 3.1). Verify `tests/suite t-journey-land` ends with "0 failed".
- [ ] 3.2 Main-ops's brief, README, the crew skill and `crew`'s usage header say a stop keeps its box and is submitted again once cleared, and only the bolt's own refusals are held (Decision 5; Task notes 3.2, `docs.2`). Verify `tests/suite t-docs` ends with "0 failed".

## 4. The affected tests

- [ ] 4.1 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
