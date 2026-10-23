# Tasks

## 1. crew reads and judges a split bolt

- [x] 1.1 `BOLT_SPLIT` reads the bolt's branch on the remote the host's tip names, fetching it once, and says whether it holds the host's tip and how many merges it lacks, or that it is absent, or git's words when it can't be read; `kit.bolt_split` reads that output and refuses what it can't (design, Decision 2; Task notes 1.1, 1.4). Verify `tests/suite contract` ends with "0 failed", its new cases in `tests/contract/test_git.py` among them.
- [x] 1.2 `split_refusal` refuses a merge into a split bolt in Decision 4's words, naming the unit, chore or fix, and refuses one it can't judge, and lets a held, equal or absent copy through (design, Decisions 1 and 4; Task notes 1.2). Passes `tests/py/test_bolt_commands.py` (`tests/suite logic`).
- [ ] 1.3 `kit.split_remote` names the remote to read only when the host has its own `bolt/<bolt>` whose tip's policy names one, and `kit.bolt_split` reads each of its outputs (design, Decision 3; Task notes 1.3). Passes `tests/py/test_kit.py` (`tests/suite logic`).

## 2. A merge into a split bolt is refused

- [ ] 2.1 A unit's and a chore's merge stage and `crew fix merge` run `bolt_split_check` and refuse through `split_refusal` before the place is made again, the carried changes are read or the merge command is handed out, a fix's refusal recorded as `fix.merge` (design, Decision 3; Task notes 2.1). Verify `tests/suite logic` ends with "0 failed".
- [ ] 2.2 Every test the change affects passes: verify `tests/suite --affected` ends with "0 failed".
