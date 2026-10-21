# Tasks

## 1. A conductor carries its bolt for sluice

- [x] 1.1 `crew.hint_branch` names `bolt/<bolt>` for a conductor or ops whose team holds one and nothing for a unit slot, and `crew.hint_args` reports it with no time to live or clears it. Verify `tests/suite logic` ends with "0 failed".
- [x] 1.2 `crew-role` exports `SLUICE_BRANCH` from the launch's `BRANCH`, and a start reports the pane's token. Verify `tests/suite t-journey-teams t-roles` ends with "0 failed".
- [x] 1.3 herdr's bare resume gets the token back through the SessionStart hook. Verify `tests/suite t-journey-teams t-session-hook` ends with "0 failed".
- [x] 1.4 A landing clears the token on the conductor's and ops's panes. Verify `tests/suite t-journey-land` ends with "0 failed".
