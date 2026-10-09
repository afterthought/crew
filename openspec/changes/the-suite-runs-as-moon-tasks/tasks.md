# Tasks

## 1. The suite runs as moon tasks

- [x] 1.1 crew's devenv shell has moon 2.5.x and links each checkout's `.moon/cache/outputs` to `<git common dir>/moon-outputs`, and `.moon/cache/` is ignored; a fresh shell shows both (design: Decisions "The archives are shared"; Task notes 1.1).
- [x] 1.2 `.moon/workspace.yml` and a generated `tests/moon.yml` give every test but the live one a task whose inputs name everything it reads, and `tests/moon-tasks --check` refuses a test with no task, a task with no test, a stale task or an undeclared read (design: Decisions "One project, one task per test file"; Task notes 1.2).
- [x] 1.3 `tests/suite` runs every task, the named ones, the affected ones or every one without the cache, side by side, and reports in `tests/run`'s words with replayed tests marked, refusing first when the tasks are out of step (design: Decisions "`tests/suite` is the one way"; Task notes 1.3).
- [ ] 1.4 `tests/t-suite.sh` shows, with the real moon in a scratch repository, a first run, a full replay, a one-test rerun, a `plugin/` rerun, a failure that stops nothing and is never replayed, `--affected`, the refusals, no live task, `__pycache__` ignored, and a second checkout replaying the first (design: Task notes 1.4).

## 2. The gate and the bolt's verification run it

- [ ] 2.1 The merge gate runs `tests/suite`, and the bolt's verification runs it in its frozen copy made a one-commit git repository linked to the shared archives, so a tree the gate passed replays (design: Decisions "The verification's copy", "The gate runs `tests/suite`"; Task notes 2.1).
- [ ] 2.2 `tests/t-merge-gate.sh` holds the gate and the verification to the new command and copy, and passes (design: Task notes 2.2).

## 3. The tests don't collide

- [ ] 3.1 A serial `tests/run` and two parallel `tests/suite --force` runs all print `0 failed` in this worktree, with any test that failed only in parallel fixed (design: Decisions "Proving the tests don't collide"; Task notes 3.1).

## 4. What agents are told, and the rules

- [ ] 4.1 CLAUDE.md and README say an agent runs only the tests its change affects with `tests/suite`, never the whole suite by hand, and how to regenerate the tasks (design: Decisions "Agents run only the tests their change affects"; Task notes 4.1).
- [ ] 4.2 The coder's, verify's and construct's briefs each say so in one sentence, and `tests/t-briefs.sh` pins all three (design: Task notes 4.2).
- [ ] 4.3 `code.1` allows moon in devenv, and `tests.5` is no longer listed as not built (design: Decisions "The rules and the record"; Task notes 4.3).

## 5. The suite

- [ ] 5.1 `tests/suite --affected` prints `0 failed` in this worktree and a second run replays every test (design: Task notes 5.1).
