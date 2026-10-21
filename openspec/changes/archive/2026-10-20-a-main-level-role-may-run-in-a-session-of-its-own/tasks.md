# Tasks

## 1. The teams file names a session per main-level role

- [x] 1.1 `crew.load` takes `roles.<role>.session` for a partition, refusing a session of another partition or machine, an empty one, and a dispatcher's; a team's roles take none. Verify `tests/suite logic` ends with "0 failed".
- [x] 1.2 `place_of_agent` and the main level's Agents place each role in its session, the reviewer beside the planner. Verify `tests/suite logic` ends with "0 failed".

## 2. The main level in each of its sessions

- [x] 2.1 `crew main up|down|status`, `crew review` and `crew revive` act on each session's workspace; up refuses while a moved role's agent runs where it stood, and down ends it there. Verify `tests/suite t-journey-main` ends with "0 failed".
- [x] 2.2 A state folder's panes recorded in another session are set aside and said. Verify `tests/suite logic` ends with "0 failed".
- [x] 2.3 Every main-level brief names where each role runs and on which account. Verify `tests/suite logic t-briefs` ends with "0 failed".
