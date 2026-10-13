# Tasks

## 1. A fix is dropped

- [x] 1.1 `fix_drop_why` refuses a merged fix and one nothing holds, `own_place` names a drop, `tidy_over` counts a dropped fix's work over, and `fix_branch_kept` keeps a branch git cherry finds commits of its own on or can't compare; `tests/py/test_fix.py`'s `TestDrop` and `tests/py/test_tidy.py`'s `TestOver` (`tests/suite logic`) prove them (`teams.3`, `plan.9`, `plan.10`, `code.7`).
- [x] 1.2 `crew fix <team> <name> --drop [--force]` refuses a merged fix and a working agent without `--force`, recorded; frees the slot, removes the place and a branch holding nothing beyond the bolt; and of a fix with no slot that holds a commit of its own keeps the place while it holds a stray file, then keeps and names the branch, its mark unset; `tests/t-journey-fix.sh` (`tests/suite journey-fix`) proves it, and `tests/suite --affected` ends with "0 failed" (`teams.3`, `teams.2`, `plan.10`, `tests.4`).
- [x] 1.3 `crew`'s usage, the README, the conductor's role, `teams.3`, `plan.9` and `plan.10` say the drop; `tests/t-docs.sh` and `tests/t-roles.sh` (`tests/suite docs roles`) prove the usage, the README and the role still hold (`docs.2`).
