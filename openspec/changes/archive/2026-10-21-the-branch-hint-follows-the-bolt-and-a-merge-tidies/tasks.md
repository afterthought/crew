# Tasks

## 1. The branch follows the bolt

- [x] 1.1 A start records `CREW_BRANCH`, empty after herdr's bare resume. Verify `tests/suite t-session-hook` ends with "0 failed".
- [x] 1.2 `crew.branch_due` says a conductor or ops is due when its team's bolt is no longer the one it carries, and `crew _renew` reads the branch once and tells the agent why. Verify `tests/suite logic` ends with "0 failed".
- [x] 1.3 A landing hands the conductor and ops their restart at their next stop. Verify `tests/suite t-journey-land` ends with "0 failed".

## 2. Nothing is left behind a landing

- [x] 2.1 A merge's wait frees its slot and removes its place and branch as it lands. Verify `tests/suite logic t-journey-merge` ends with "0 failed".
- [x] 2.2 The design agent's and operator's briefs submit with `wt submit main` and remove nothing by hand. Verify `tests/suite t-briefs` ends with "0 failed".
