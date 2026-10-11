# Tasks

## 1. Reading whether a prompt was taken

- [x] 1.1 `transcript.py` says where a session's transcript ends and whether it received a given prompt past that point, runnable on the agent's host (design.md, Task notes 1.1). Verify `tests/suite t-transcript` ends with "0 failed".
- [ ] 1.2 The stub herdr writes each prompt it is sent into the stub session's transcript, and can be told to leave prompts typed and untaken until a `ctrl+c` clears them (design.md, Task notes 1.2). Verify `tests/suite t-greet t-unit-run t-fix t-stage-ends` ends with "0 failed".

## 2. One sending that is taken or sent again

- [ ] 2.1 crew sends a prompt only once the agent is ready for input, reads its transcript, clears and sends once more when it was not taken, and answers taken, never or unread, with `crew.py stage-prompt` on the command line (design.md, Task notes 2.1). Verify `tests/suite t-prompt-taken` ends with "0 failed".
- [ ] 2.2 A greeting not taken is sent once more, and when the second is not taken either, nothing is left typed, no greeting is recorded, and crew says so with the `crew tell` that would greet it (design.md, Task notes 2.2). Verify `tests/suite t-greet t-main` ends with "0 failed".

## 3. A stage begins or crew says it did not

- [ ] 3.1 Every stage `run_stage` starts begins only when its prompt is taken, and is otherwise recorded as refused, owed no end, and reported as never started with how to run it again (design.md, Task notes 3.1). Verify `tests/suite t-unit-run t-fix t-stage-ends` ends with "0 failed".
- [ ] 3.2 Ops's proof request is taken or sent again, and a proof whose request is not taken is reported as never started with no proof owed (design.md, Task notes 3.2). Verify `tests/suite t-stage-ends` ends with "0 failed".

## 4. The docs and the rule

- [ ] 4.1 README, the crew skill and `plugin/bin/crew`'s usage say a stage and a greeting are taken or sent again, `teams.15`'s details name what builds it, and `_open.md` no longer lists it (design.md, Task notes 4.1). Verify `tests/suite --affected` ends with "0 failed".
