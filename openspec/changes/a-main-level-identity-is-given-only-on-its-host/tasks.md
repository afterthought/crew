# Tasks

## 1. A main level's identity stays on its host

- [x] 1.1 crew tells from a session's record alone whether it names a main level's agent, and says what a session off that main level's host is told, proved by cases in `tests/py/test_teams.py` (design, Task notes 1.1).
- [x] 1.2 `crew-role` refuses to start a main level's design agent, planner, ops, operator or reviewer, fresh or resumed, off the host the teams file names for it, naming that host, proved by cases in `tests/t-roles.sh` (design, Task notes 1.2).
- [x] 1.3 crew's SessionStart hook gives a main level's agent resumed off its host no identity, pane name or brief, leaves its record alone and tells it where the main level runs, and says why when it can't read the teams file, proved by cases in `tests/t-roles.sh` (design, Task notes 1.3).
- [x] 1.4 The logic tier is green: `devenv shell -- moon run tests:logic`; and `tests/suite roles session-hook` passes.

## 2. The documents say it

- [x] 2.1 README's resume paragraph and `crew-role`'s usage comment say a main level's agent starts and gets its identity back only on its main level's host, proved by `tests/suite docs` passing (design, Task notes 2.1).
- [ ] 2.2 `tests/suite --affected` passes once the change is done.
