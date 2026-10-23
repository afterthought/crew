# Tasks

## 1. Where a bolt is read

- [x] 1.1 One pure decision says where a bolt is read, GitHub's copy when the host holds it and its own policy names a remote, else the host's branch, with the policy matching moved into gather.py and kit.py using it unchanged in what it decides (design, Decision 1; Task notes 1.1); passes `tests/py/test_bolt_commands.py` and `tests/py/test_kit.py`, verified by `tests/suite logic` ending with "0 failed".
- [x] 1.2 gather reads every bolt's head, verdict, changes and chores, a chore's place's own commits and a fix's merge at that ref, and a bolt whose policy crew can't read is unknown in the stages (design, Decision 2; Task notes 1.2); passes `tests/contract/test_gather.py` and the logic case, verified by `tests/suite contract` and `tests/suite logic` each ending with "0 failed".
- [x] 1.3 Every other read of a bolt in plan.py, the landing card's base, the verify's undeclared paths, a forecast's and a rebase's words, a dependent's rebase and take, and where a unit landed on its bolt, reads at that ref (design, Decision 2; Task notes 1.3); passes `tests/contract/test_git.py` and `tests/py/test_forecast.py`, verified by `tests/suite contract` and `tests/suite logic` each ending with "0 failed".

## 2. When a bolt on GitHub is fetched

- [x] 2.1 `crew bolts` and a give's proven check fetch the kit's origin once before reading, a fetch that fails reads the kit unknown with git's words, and every other read fetches nothing (design, Decision 3; Task notes 2.1); passes `tests/py/test_bolt_commands.py` and `tests/contract/test_gather.py`, verified by `tests/suite logic` and `tests/suite contract` each ending with "0 failed".
- [x] 2.2 Each look a wait takes at a merge stage fetches before it reads the bolt, and a fetch that fails delivers nothing and says why (design, Decision 3; Task notes 2.2); passes `tests/py/test_stage_ends.py`, verified by `tests/suite logic` ending with "0 failed".
- [x] 2.3 A give fetches the bolt's branch sluice made before its plan write (design, Decision 3; Task notes 2.3); verified by `tests/suite t-journey-plan` ending with "0 failed".

## 3. Proved end to end, and said

- [ ] 3.1 The stub sluice can land a bolt's merge on GitHub leaving the host's copy and tracking ref behind, and with it a unit's wait returns delivered and `crew bolts` shows it merged (design, Decision 4; Task notes 3.1); verified by `tests/suite t-journey-units` ending with "0 failed".
- [ ] 3.2 README and the crew skill say where a bolt on GitHub is read and when crew fetches it (design, Decision 3; Task notes 3.2); verified by `tests/suite t-docs` ending with "0 failed".
- [ ] 3.3 The tests the change affects pass; verified by `tests/suite --affected` ending with "0 failed".
