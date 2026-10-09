# Tasks

## 1. A removal goes through the kit's remove hooks

- [x] 1.1 `tidy` removes each finished worktree with the kit's `wt remove`, from the kit's main, leaving the branch to its own step, and keeps and names one wt refuses (design.md, Task notes 1.1). Verify with the tests of 1.2.
- [ ] 1.2 `tests/t-tidy.sh` proves a kit's remove hooks run, that a failed or unapproved hook keeps the worktree and its branch named without wt's skip hints, that the next read removes it once cleared, and that a missing wt keeps it (design.md, Task notes 1.2). Verify `tests/suite t-tidy t-merge t-fix t-bolt t-unit t-unit-free` ends with "0 failed".

## 2. Briefs and docs

- [ ] 2.1 The conductor's and main-level ops' briefs, README's Teams paragraph and `crew status`'s usage say a worktree goes through the kit's remove hooks and what keeps one, and `plan.9`'s open item and its details' note go (design.md, Task notes 2.1). Verify `tests/suite t-briefs t-docs` ends with "0 failed".
