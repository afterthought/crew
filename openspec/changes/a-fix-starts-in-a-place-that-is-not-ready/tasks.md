# Tasks

## 1. A fix starts on a place that is not ready

- [x] 1.1 `make_place` returns what failed instead of refusing when asked, `fix_place` asks and still refuses a place not the fix's own, and `kit.unready_said` and `plan.fix_prompt` say it to the fix's agent on one line; `tests/py/test_fix.py`'s `TestUnready` (`tests/suite logic`) proves the prompt with a ready place and with one whose `moon setup` failed (`teams.3`, `code.7`).
- [x] 1.2 `crew fix` starts the fix's agent in a place whose runner's setup fails, its prompt naming the step, and records the start with no refusal; `tests/t-journey-fix.sh` (`tests/suite journey-fix`) proves it, and `tests/suite --affected` ends with "0 failed" (`teams.3`, `plan.17`, `tests.4`).
- [x] 1.3 `crew`'s usage, the README, `teams.3` and `plan.17` say a fix starts in a place that is not ready and a unit's or chore's stage does not; `tests/t-docs.sh` (`tests/suite docs`) proves the usage and README still name every command (`docs.2`).
