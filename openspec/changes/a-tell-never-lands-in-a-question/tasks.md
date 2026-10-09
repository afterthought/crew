# Tasks

## 1. crew knows when an agent is waiting on a question

- [ ] 1.1 Stub herdr refuses a prompt to a blocked agent with `agent_blocked` and types nothing, as herdr 0.9.3 does (design.md, Task notes 1.1). Verify `tests/suite t-greet t-notify` ends with "0 failed".
- [ ] 1.2 crew's PreToolUse hook leaves a mark when a crew agent opens a question or a plan for the user, and a session's start clears its mark (design.md, Task notes 1.2). Verify `tests/suite t-session-hook` ends with "0 failed".
- [ ] 1.3 A stdlib-only reader, run on the agent's host, says whether a session's mark is open, answered or unreadable (design.md, Task notes 1.3). Proved by 2.1's tests.

## 2. A tell is a prompt or nothing

- [ ] 2.1 `tell` types nothing, fails and says the agent is waiting on a question when herdr reports it blocked, when its mark is open, or when herdr refuses with `agent_blocked`, and refuses naming what it could not read when it can't tell (design.md, Task notes 2.1). Verify `tests/suite t-notify` ends with "0 failed".
- [ ] 2.2 A greeting waits on a question crew's mark shows as it waits on one herdr shows, and is sent once (design.md, Task notes 2.2). Verify `tests/suite t-greet` ends with "0 failed".

## 3. The docs and the rule

- [ ] 3.1 The usage of `plugin/bin/crew`, README and the crew skill say a tell is refused while its agent waits on a question (design.md, Task notes 3.1). Verify `tests/suite t-docs t-briefs` ends with "0 failed".
- [ ] 3.2 `teams.11`'s details name the two readings and the hook, and `_open.md` no longer lists it as unbuilt (design.md, Task notes 3.2). Verify `tests/suite --affected` ends with "0 failed".
