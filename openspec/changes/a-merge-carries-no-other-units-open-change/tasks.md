# Tasks

## 1. A merge carries no other unit's open change

- [x] 1.1 `carried_in` decides which of a branch's open changes its merge would carry, and `carried_refusal` names each with what to do, a later unit's work taken out and any other merged first. Checked by `tests/py/test_stage_rules.py` `TestCarried` (`teams.17`, `plan.13`, `code.7`).
- [x] 1.2 `merge_carries` reads the branch's open changes on the team's host and the bolt's archived ones, and `run_check` and `chore_check` refuse a merge with it before it starts. Checked by `tests/t-journey-carried.sh`, "a merge whose branch holds another unit's change open, which the bolt does not hold archived, is refused before it starts, naming it" (`teams.17`, `read.1`).

## 2. The docs say so

- [x] 2.1 The conductor's brief, README, the crew skill and the usage header say it. Checked by `tests/t-briefs.sh` and `tests/t-docs.sh` (`docs.2`, `tests.6`).
