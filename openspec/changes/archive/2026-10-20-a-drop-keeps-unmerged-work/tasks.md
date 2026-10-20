# Tasks

## 1. A branch is removed only when its bolt, or main, holds its work

- [x] 1.1 `branch_target` decides what a unit's, chore's or fix's branch is compared with (its bolt while it exists, else the kit's main now; a fix's bolt or nothing) and `branch_kept`, which `fix_branch_kept` becomes, keeps a branch git cherry finds a `+` commit on or cannot compare; cases in `tests/py/test_tidy.py` and `tests/py/test_fix.py` pass (`tests/suite logic`) (design: Task notes 1.1; `plan.10`, `code.7`).
- [x] 1.2 The tidy removes a unit's or chore's branch only through `branch_gone`, which `fix_branch_gone` becomes, keeping and naming a branch that holds work its target lacks and writing one `branch.kept` run-record entry for it, and a dropped fix's branch goes the same way; `tests/suite logic` passes (design: Task notes 1.2; `plan.9`, `plan.10`, `read.1`).
- [x] 1.3 Contract cases pin git cherry across a rebase, its silence on merge commits, and a deleted bolt's upstream; `tests/suite contract` passes (design: Task notes 1.3; `tests.11`).

## 2. A unit added again starts from its kept branch

- [x] 2.1 A unit's or chore's new place made on an existing branch tracks the bolt it was given and its stage's start names the kept branch and its commit; a contract case in `tests/contract/test_git.py` proves `PLACE` sets the upstream and prints the commit, and `tests/suite contract logic` passes (design: Task notes 2.1; record 0003).

## 3. The commands say it

- [x] 3.1 `crew unit drop` and `crew unit free` on a unit whose branch holds its own commit keep and name the branch in their output and the run record, and a unit added again under its name starts on it; the journey in `tests/t-journey-fix.sh` (or the one that fits) proves it, with every expectation of a removed branch that now holds a commit updated, and `tests/suite --affected` ends with "0 failed" (design: Task notes 3.1; `tests.4`, `tests.10`).

## 4. The docs say it

- [x] 4.1 README and `plugin/roles/planner.md` say a drop keeps, named, a branch holding work its bolt lacks, and that a unit added again under its name starts from it; `tests/suite docs briefs` passes (design: Task notes 4.1; `docs.2`).
