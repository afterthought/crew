# Tasks

## 1. An approval answers once its write is made

- [x] 1.1 `construct_again` names the hand-off entry with the team, the unit, what amended it and `--force` past construct, and `handed_state` reads a marker as nothing handed, starting, failed or gone; `tests/py/test_amend.py`'s `TestConstructAgain` and `TestHanded` (`tests/suite logic`) prove them (`plan.15`, `code.9`, `code.7`).
- [x] 1.2 An approved amendment and the user's own answer once their constructs are handed to the team's host, which starts each again and tells the conductor; a team taken down is said at the hand-off; `tests/t-journey-plan.sh` and `tests/t-journey-prompts.sh` (`tests/suite journey-plan journey-prompts`) prove it, waiting on the conductor's word rather than the clock (`plan.15`, `code.9`, `tests.8`).
- [x] 1.3 A stage of a unit whose handed construct is starting is refused naming the wait, and a wait on one that failed says why and clears its marker; `tests/t-journey-prompts.sh` proves both from a marker it writes, and `tests/suite --affected` ends with "0 failed" (`plan.15`, `tests.4`).
- [x] 1.4 The README, the conductor's role, `plan.15` and `code.9` say the hand-off; `tests/t-docs.sh` and `tests/t-roles.sh` (`tests/suite docs roles`) prove they still hold (`docs.2`).
