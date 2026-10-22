# Tasks

## 1. The console

- [x] 1.1 `crew console up <label>` opens the flow, rail (with its shell) and board tabs in the `console` workspace of this host's `<label>` session and starts no agent; a second run opens nothing; after a restart it runs each tab's command again in a shell herdr brought back and leaves a tab running anything else; `crew console down <label>` closes them. Verify `tests/suite t-journey-main` ends with "0 failed".
- [x] 1.2 `crew operator up <label>` opens the console and says it is `crew console up` now. Verify `tests/suite t-journey-main` ends with "0 failed".
- [x] 1.3 The console's up ends the operator agent its host ran before record 0035 once it is not working, and closes the panes crew recorded in its workspace, leaving a tab of the user's. Verify `tests/suite t-journey-main` ends with "0 failed".
- [x] 1.4 The board tab's empty frame and crew's mod name `crew console up`. Verify `tests/suite logic mod` ends with "0 failed".
