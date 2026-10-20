# Tasks

## 1. A landed bolt's work is judged against main

- [ ] 1.1 `LANDING` marks a crew-marked bolt branch `landed` in the kit's git config once sluice has landed it and main moved, and says when it could not; the contract landing case and a `landing_said` logic case prove it, and `tests/suite logic contract` passes (design: Task notes 1.1; record 0003, `read.4`).
- [ ] 1.2 `branch_target` compares a unit's, chore's or fix's branch with main now when its bolt is marked landed or its bolt's branch is gone, and with the bolt only while the bolt stands unlanded; cases in `tests/py/test_tidy.py` pass (`tests/suite logic`) (design: Task notes 1.2; `plan.10`, `code.7`).
- [ ] 1.3 A landed bolt's branch whose bolt no plan has goes only when git cherry finds nothing of it main lacks, and is otherwise kept, named, unmarked and recorded as `branch.kept`, a legacy bolt worktree's branch going the same way; a dropped bolt's branch goes as today; cases in `tests/py/test_tidy.py` pass (`tests/suite logic`) (design: Task notes 1.3; `plan.9`, `plan.10`, `read.1`).

## 2. The landing says it

- [ ] 2.1 `tests/t-journey-land.sh` proves the submission's mark and `crew bolt land`'s line that the bolt's branch went because main holds every commit of it, and `tests/suite --affected` ends with "0 failed" (design: Task notes 2.1; `tests.12`).

## 3. The docs say it

- [ ] 3.1 README and `plugin/roles/main-ops.md` say a landed bolt's branch, and each branch of its work, goes only when main holds every commit of it and is otherwise kept and named; `tests/suite docs briefs` passes (design: Task notes 3.1; `docs.2`).
