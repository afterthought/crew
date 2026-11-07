# Tasks

## 1. A landing beside reads as the verdict that covers it

- [x] 1.1 A kit's gather gives each bolt's head its `Sluice-Result` and, for a head that names a submission and no `Sluice-Tested`, sluice's record of that submission read by one `sluice status <n> --json`, or why it can't be read (design, Decisions 1 and 3; Task notes 1.1). Passes `tests/contract/test_gather.py` (`tests/suite contract`).
- [x] 1.2 A bolt's verification for a head landed beside is green only on sluice's record of it landed beside as the head with a covering verdict that passed, naming that verdict's counts, and unknown, saying why, on anything else (design, Decision 1; Task notes 1.2). Passes `tests/py/test_kit.py` (`tests/suite logic`).
- [x] 1.3 Every read of a bolt's proof passes the record, so such a bolt reads proven, its row can land on its kit's landings card and `crew bolts` shows the covering verdict (design, Decision 2; Task notes 1.3). Passes `tests/py/test_rail.py`, `tests/py/test_landing.py` and `tests/py/test_bolt_commands.py` (`tests/suite logic`).

## 2. The docs and the change's tests

- [x] 2.1 README and the crew skill say a landing beside reads as the verdict that covers it, and unknown where sluice's record names none (`docs.2`; Task notes 2.1). Verify `tests/suite t-docs` ends with "0 failed".
- [x] 2.2 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
