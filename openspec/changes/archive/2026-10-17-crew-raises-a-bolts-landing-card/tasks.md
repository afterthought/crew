# Tasks

## 1. The landing card

- [x] 1.1 The merge's end and the rail read post the landing card when the bolt reads proven, no fix in flight on it, change it when the head moves, `crew fix` withdraws it on a defect, and `crew bolt land` closes it in record 0032's words (`no-worktree-holds-main-or-a-bolt-branch` 4.2). Logic: `tests/py/test_landing.py` and `tests/py/test_rail.py` `TestRows`, when a bolt reads proven and which act follows. Journey: `tests/t-journey-land.sh` (`plan.16`, record 0025).
- [x] 1.2 `conductor.md` says crew raises the landing card once the bolt reads proven, the conductor adopting it by the line its merge's end prints or `crew tell` brings, telling main-level ops on a yes and starting a fix on a defect note; it no longer posts or closes the landing card. Journey: `tests/t-briefs.sh` pins the words (`tests.6`, `plan.16`).

## 2. The suite

- [x] 2.1 `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).
