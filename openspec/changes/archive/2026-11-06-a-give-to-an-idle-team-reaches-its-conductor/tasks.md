# Tasks

## 1. A give reaches its conductor

- [x] 1.1 A give on today's path hands its conductor's notice to the team's host before anything else starts, which owes it there or says and records it refused where the conductor is not up, and the giver says and records it refused where the host could not take it (design, Decision 1; Task notes 1.1). Passes `tests/py/test_teams.py` (`tests/suite logic`).
- [x] 1.2 `crew _renew` gives an owed notice at once when the conductor is idle, by its restart's greeting or by crew's notice while its restart waits on background work of its own, keeps it for the end of its turn when it works, and records it refused when it is not up or not taken (design, Decision 2; Task notes 1.2). Passes `tests/py/test_hold.py` (`tests/suite logic`).
- [x] 1.3 crew's Stop hook hands back a restart `crew _renew` gave up on and a notice not yet given, one for a bolt its team no longer holds among them (design, Decision 3; Task notes 1.3). Passes `tests/py/test_hold.py` (`tests/suite logic`); verify `tests/suite t-hold` ends with "0 failed".
- [x] 1.4 A give to a team that held no bolt restarts its ops at once and its conductor on its host, its greeting naming the bolt (design, Decision 4; Task notes 1.4). Verify `tests/suite t-journey-teams` ends with "0 failed".
- [x] 1.5 A bolt whose conductor was not told of its give is said on its head line, in the attention line and on `crew rail` until a notice or a greeting tells it, and the box's case, an idle conductor whose restart waits on its own background work, is told beside a waiting bolt (design, Decision 5; Task notes 1.5). Passes `tests/py/test_teams.py` (`tests/suite logic`); verify `tests/suite t-journey-land` ends with "0 failed".
- [x] 1.6 README, the skill and the usage say what a give tells its conductor and what the rail lists (Task notes 1.6). Verify `tests/suite t-docs` ends with "0 failed".

## 2. The change's tests

- [x] 2.1 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
