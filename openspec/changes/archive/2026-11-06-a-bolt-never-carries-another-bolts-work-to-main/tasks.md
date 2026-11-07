# Tasks

## 1. A bolt never carries another bolt's work to main

- [x] 1.1 A kit's read says what each bolt carries of another bolt's own work beyond main, read from the branches alone, a ref gone mid-read left out, or why it can't (design, Decisions 1 and 2; Task notes 1.1). Passes `tests/py/test_landings.py` (`tests/suite logic`) and `tests/contract/test_gather.py` (`tests/suite contract`).
- [x] 1.2 A bolt that carries another bolt's work main lacks is held on its landings row with no box, on the rail's land line and in `crew bolts`, naming that bolt and its landings (design, Decision 2; Task notes 1.2). Passes `tests/py/test_landings.py`, `tests/py/test_rail.py` and `tests/py/test_bolt_submissions.py` (`tests/suite logic`).
- [x] 1.3 `crew bolt submit` submits nothing of a bolt whose head carries another bolt's work main lacks, read after one fetch that prunes nothing, naming that bolt and its landings, and refuses when that can't be read (design, Decision 3; Task notes 1.3). Passes `tests/py/test_landing.py`, `tests/py/test_pane_landing.py` and `tests/py/test_kit.py` (`tests/suite logic`) and `tests/contract/test_git.py` (`tests/suite contract`).

## 2. The docs and the change's tests

- [x] 2.1 README, the crew skill and `crew`'s usage header say a bolt carrying another bolt's work does not land (`docs.2`; Task notes 2.1). Verify `tests/suite t-docs` ends with "0 failed".
- [x] 2.2 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
