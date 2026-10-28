## 1. The split

- [x] 1.1 `bolt_time` gives each minute of a bolt's life to one holder in the fixed order, with its age, its shares, who holds it now and since when, and stalled after five minutes of nobody (design, Decision 1; Task notes 1.1); passes `tests/py/test_bolt_time.py` in the logic tier, `tests/suite logic`.
- [x] 1.2 `bolt_facts` reads the give, the stages, the bolt's cards, the host's holds and the bolt's submissions from the run record and sluice's submissions, and says why when the give or the history can't be read (design, Decisions 2 and 4; Task notes 1.2); passes `tests/py/test_bolt_time.py` in the logic tier, `tests/suite logic`.

## 2. sluice's record of the bolt's submissions

- [ ] 2.1 A kit's gather reads each asked bolt's and main's decided submissions with `sluice status --all --json`, and each standing submission's submitted time and start of checks, every field guarded (design, Decisions 3 and 7; Task notes 2.1); passes `tests/py/test_bolt_submissions.py` in the logic tier and `tests/contract/test_gather.py` in the contract tier, `tests/suite contract`.
- [ ] 2.2 The follower's refresh on a queue's move keeps the last gather's history and counts a submission that left the queue as it last stood until the line's time (design, Decision 7; Task notes 2.2); passes `tests/py/test_board.py`, `tests/suite logic`.

## 3. The rows

- [ ] 3.1 Each held bolt's head line on the board, in its JSON and in every band that draws it, shows its age, its shares and its holder now (design, Decision 5; Task notes 3.1); passes `tests/py/test_board.py`, `tests/suite logic`, and the mod's cases, `tests/suite mod`.
- [ ] 3.2 Each bolt's line on its kit's landings row on the rail ends with the same age, shares and holder as the board's (design, Decision 5; Task notes 3.2); passes `tests/py/test_rail.py`, `tests/suite logic`.

## 4. The landing's entry

- [ ] 4.1 `bolt.land` records `Age` and `Split` to the landing's decision, and neither when a fact can't be read, the landing going on (design, Decision 6; Task notes 4.1); passes `tests/py/test_landing.py`, `tests/suite logic`, and `tests/suite t-journey-land` ends with "0 failed".

## 5. Docs and the suite

- [ ] 5.1 README and the crew skill say what a bolt's head line and land line show (design, Decision 5; Task notes 5.1); `tests/suite t-docs` ends with "0 failed".
- [ ] 5.2 `tests/moon.yml` is in step with the tests and the change's affected tests pass (Task notes 5.2); Verify `tests/suite --affected` ends with "0 failed".
