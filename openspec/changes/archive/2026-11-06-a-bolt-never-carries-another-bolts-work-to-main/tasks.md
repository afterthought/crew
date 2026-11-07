# Tasks

## 1. A bolt never carries another bolt's work to main

- [x] 1.1 A kit's read says what each bolt carries of another bolt's own work beyond main, read from the branches alone, or why it can't (design, Decisions 1 and 2; Task notes 1.1). Passes `tests/py/test_landings.py` (`tests/suite logic`) and `tests/contract/test_gather.py` (`tests/suite contract`).
- [x] 1.2 A bolt that carries another bolt's work main lacks is held on its landings row with no box and no card, on the rail's land line and in `crew bolts`, naming that bolt and its landings (design, Decision 2; Task notes 1.2). Passes `tests/py/test_landings.py`, `tests/py/test_rail.py` and `tests/py/test_bolt_submissions.py` (`tests/suite logic`).
- [x] 1.3 `crew bolt submit` submits nothing of a bolt whose head carries another bolt's work main lacks, read after one fetch, naming that bolt and its landings, and refuses when that can't be read (design, Decision 3; Task notes 1.3). Passes `tests/py/test_landing.py`, `tests/py/test_pane_landing.py` and `tests/py/test_kit.py` (`tests/suite logic`) and `tests/contract/test_git.py` (`tests/suite contract`).
- [x] 1.4 A unit's, chore's or fix's merge is refused while its branch carries another bolt's work main and its bolt lack, naming it and the way on (design, Decision 4; Task notes 1.4). Passes `tests/py/test_stage_rules.py` (`tests/suite logic`) and `tests/contract/test_git.py` (`tests/suite contract`).
- [x] 1.5 The coder's brief names its bolt as the one its branch tracks and says no other bolt's branch is its to build on (design, Decision 5; Task notes 1.5). Verify `tests/suite t-briefs` ends with "0 failed".
- [x] 1.6 A moved unit is rebased from the bolt it leaves onto the bolt it joins, each read where it lives after a fetch, and carries nothing of the bolt it leaves (design, Decision 6; Task notes 1.6). Passes `tests/contract/test_git.py` (`tests/suite contract`).
- [x] 1.7 A slot that built one bolt's unit cuts the next bolt's unit from that bolt on GitHub with nothing of the first (design, Context; Task notes 1.7). Passes `tests/contract/test_git.py` (`tests/suite contract`).

## 2. The docs and the change's tests

- [x] 2.1 README, the crew skill and `crew`'s usage header say a bolt carrying another bolt's work does not land and a merge carrying it is refused (`docs.2`; Task notes 2.1). Verify `tests/suite t-docs` ends with "0 failed".
- [x] 2.2 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
