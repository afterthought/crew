# A fix is dropped

## Why

Record 0028, point 2. `crew fix` has start, `--merge` and `--wait`, and a fix ends only by its merge or with its bolt, so a fix that is not wanted, or one refused before its agent started, leaves its branch and place standing on the host until someone removes them by hand (wldn, awb-1, 2026-10-13, signal 2026-10-13-swancloud-planner-2e24fc2d/01).

## What Changes

- **`crew fix <team> <name> --drop [--force]` ends a fix.** Its slot is freed and its agent ended when one is up, a working one only with `--force` (`teams.2`); its branch is marked dropped in the kit's git config, and the team's read that follows removes its place and branch as a dropped unit's go, through the kit's `wt remove`.
- **A dropped fix's branch with commits of its own beyond the bolt is kept and named**, judged by `git cherry` against the bolt (`plan.10`); one holding nothing beyond it is deleted.
- **A fix with no slot whose branch or place stands is dropped the same way**, its place refused when it is not the fix's own (`read.4`).
- **A fix that has merged into its bolt is not dropped**, and the refusal says a new fix undoes it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: "Fixes during a bolt are built beside its units" gains the drop; "A worktree goes when its work is over" counts a dropped fix's work over and keeps its branch when it holds commits beyond the bolt.

## Impact

- `plugin/lib/plan.py` (`fix_cmd`, `fix_run`, `fix_drop`, `fix_drop_why`, `own_place`, `tidy`, `tidy_over`, `fixes_dropped`, `fix_branch_kept`, `fix_branch_gone`, the `_fix-run` parser), `plugin/bin/crew` (`crew fix ... --drop` and its usage), `plugin/roles/conductor.md`, `README.md`, `docs/architecture/teams.md`, `docs/architecture/plan.md`, `docs/architecture/_open.md`, `tests/py/test_fix.py`, `tests/py/test_tidy.py`, `tests/t-journey-fix.sh`.

## Touches

```
plugin/lib/plan.py
plugin/bin/crew
plugin/roles/conductor.md
README.md
docs/architecture/teams.md
docs/architecture/plan.md
docs/architecture/_open.md
tests/py/test_fix.py
tests/py/test_tidy.py
tests/t-journey-fix.sh
```
