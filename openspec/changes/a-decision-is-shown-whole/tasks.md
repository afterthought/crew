# Tasks

## 1. The briefs show decisions whole

- [x] 1.1 The conductor's brief has it tell the user a unit is ready, where its change is and what it would make true, ask for the answer in words and open nothing, and show a proposal it raises with the user whole (design.md, Task notes 1.1). Verify the changed `swb-1 conductor` checks in `tests/t-briefs.sh` pass.
- [x] 1.2 The planner's brief has it show a proposal as `plan proposed <n>` prints it, never by number alone, and ask for the answer in words without reciting a command (design.md, Task notes 1.2). Verify the new `wldn planner` checks in `tests/t-briefs.sh` pass.
- [x] 1.3 The operator's brief has it show each open proposal whole when it says what waits on the user, ask for answers in words, and run either approval only on the user's word (design.md, Task notes 1.3). Verify the `wldn operator` checks in `tests/t-briefs.sh` pass.

## 2. The rendering shows the commands

- [ ] 2.1 `crew plan proposed <n>` prints under each change the `crew` command approval runs for it, and names who it waits on in words without answering commands (design.md, Task notes 2.1). Verify the changed checks in `tests/t-proposals.sh` pass.
- [ ] 2.2 The README's description of `crew plan proposed <n>` says it shows each change's command and who it waits on, in words (design.md, Task notes 2.2). Verify `devenv shell -- tests/run` ends with "0 failed".
