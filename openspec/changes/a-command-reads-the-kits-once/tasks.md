# Tasks

## 1. A command reads the kits once

- [x] 1.1 `gather.py` reads a place's tasks, open tasks and planning from its change's files by `openspec` 1.14's rules for the spec-driven schema, and through `openspec` for any other schema, a redefined spec-driven, or metadata it does not read (design: *Stage facts are read from the change's files*; Task notes 1.1; `read.1`, `code.1`).
- [x] 1.2 `ticks()` and construct's deliverable use the same reading, so every reader of a unit's tasks and planning agrees (Task notes 1.2).
- [x] 1.3 A kit's answer holds every local `bolt/*` branch, so one answer serves every step of a command (design: *Every bolt branch of a kit is read*; Task notes 1.3).
- [x] 1.4 Within one command on one host, the state branch is fetched once and each kit gathered once; a write starts from the held tip, fetches afresh only after a refused push, and the reading then holds its commit (design: *Each command keeps one reading on each host*; Task notes 1.4; `plan.1`, `state.1`).
- [x] 1.5 Making a place or removing a worktree drops that kit's answer, so the next step reads it again (Task notes 1.5).
- [x] 1.6 `plugin/bin/crew` makes the command's reading for every command that runs more than one step, shares it with nested runs on the same host, removes it however the command ends, and makes none for the rail loop, `crew events` or an exec'd single run; a wait reads afresh at every look (design: *Waits and loops read afresh*; Task notes 1.6; `state.4`).
- [x] 1.7 The stub `herdr` answers each call in about half its current time, with the same state, log lines and answers (design: *The stub herdr*; Task notes 1.7; `tests.4`).
- [x] 1.8 `tests/run` refuses to start without `openspec`, and `tests/t-stage-facts.sh` fails on any case where crew's reading and `openspec`'s differ on the same worktree (design: *How the rule is tested*; Task notes 1.8; `tests.1`, `tests.2`).
- [x] 1.9 `tests/t-reads-once.sh` proves one fetch, one gather and no `openspec` start on the team's host for `crew status` with three units in flight and for `crew unit run`, a raced write that replays, and no reading left after a command or a refused one (Task notes 1.9).
- [x] 1.10 `plan.12` leaves `_open.md` and names its sources and the schema rule (Task notes 1.10; `docs.5`).
- [ ] 1.11 `devenv shell -- tests/run` ends with "0 failed", and its wall time is given in the summary (Task notes 1.11).
