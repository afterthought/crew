# Tasks

## 1. Every team read removes the worktrees whose work is over

- [x] 1.1 `plan.py _tidy <team>` removes, on the team's host, each worktree crew made in the team's kit checkout whose work is over and that no slot holds, keeps and names one with uncommitted changes or a lock, touches nothing else, and removes nothing when a plan can't be read (design.md, Task notes 1.1). Verify a new `tests/t-tidy.sh` passes, covering each case in the note.
- [x] 1.2 `reap` frees a slot whose unit or fix the plan has dropped, as it frees merged ones, then runs the tidy in place of `remove_place`, and a hidden `crew _tidy <team>` runs that on the team's host (design.md, Task notes 1.2). Verify `tests/t-unit-free.sh`, updated so that a slot left by a working agent is freed by the next idle `crew status`, passes.
- [x] 1.3 A merged unit's or fix's place goes at the next idle read, and one with a stray file is kept and named on each read until the file goes (design.md, Task notes 1.3). Verify `tests/t-merge.sh` and `tests/t-fix.sh`, with the new cases, pass.

## 2. Dropping and landing tidy at once

- [x] 2.1 `crew bolt drop` tidies the bolt's team's host after its write, so the bolt's worktree and branch and its units' and fixes' places, branches and slots go, and `--requeue` refuses a unit that has a worktree (design.md, Task notes 2.1). Verify `tests/t-bolt.sh`, with the new drop and requeue cases, passes.
- [x] 2.2 `crew unit drop` and `crew bolt land` tidy the team's host after their writes, and a land whose bolt worktree is kept still lands (design.md, Task notes 2.2). Verify `tests/t-bolt.sh`, `tests/t-unit.sh` and `tests/t-unit-free.sh` pass.

## 3. Briefs and docs

- [x] 3.1 The conductor's, main-level ops' and planner's briefs, `README.md` and the usage text say when worktrees go, what keeps one, and that requeue refuses a unit with a worktree (design.md, Task notes 3.1). Verify `devenv shell -- tests/run` ends with "0 failed".
