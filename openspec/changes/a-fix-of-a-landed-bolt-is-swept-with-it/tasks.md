# Tasks

## 1. A fix is read from its branch

- [x] 1.1 `gather.py` reads each fix branch's bolt from either upstream form, whether it has merged at the ref it tracks, whether the kit's main holds its tip and whether it has moved, for fixes with a place and, as `fix_branches`, for those without (design.md, Task notes 1.1). Verify `tests/suite contract` ends with "0 failed".
- [x] 1.2 A slot's fix reads `landed`, `merged`, `dropped`, `fix` or `none` by one decision on those facts, from its place or else its branch, and nothing is read dropped or landed by the plan while the plan is unread (design.md, Task notes 1.2). Verify `tests/suite logic` ends with "0 failed".

## 2. A fix's end frees its slot and sweeps its branch

- [x] 2.1 The tidy ends a landed fix's place with its branch, reads a fix tracking `origin/bolt/<bolt>` as crew's, and removes each fix branch no worktree or slot holds once it has merged or landed, leaving any other (design.md, Task notes 2.1). Verify `tests/suite logic` ends with "0 failed".
- [ ] 2.2 A slot freed for landed work says it has landed on main (design.md, Task notes 2.2). Verify `tests/suite logic` ends with "0 failed".

## 3. The command, end to end

- [ ] 3.1 A fix whose place was removed after its merge has its slot freed and its branch removed by the team's next `crew status` (design.md, Task notes 3.1). Verify `tests/suite t-journey-land t-journey-fix` ends with "0 failed", then `tests/suite --affected` ends with "0 failed".
