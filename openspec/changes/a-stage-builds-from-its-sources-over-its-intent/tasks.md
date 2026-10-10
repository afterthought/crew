# Tasks

## 1. The construct builds from its sources over its intent

- [ ] 1.1 The construct's brief says to read each source as committed on its repository's main when the stage starts, never the worktree's copy, to write the change from the sources where the intent says more or otherwise, and to open the final message with the difference (design.md, Task notes 1.1). Verify `crewpy brief swb-1 construct` prints the new bullets with no token unfilled, through `tests/run t-briefs`.
- [ ] 1.2 `tests/t-briefs.sh` pins the new rule's phrases in the construct's brief (design.md, Task notes 1.2). Verify `tests/suite t-briefs` ends with "0 failed".
- [ ] 1.3 `docs/architecture/_open.md` lists only the spike as not built under `briefs.14` (design.md, Task notes 1.3). Verify `tests/suite --affected` ends with "0 failed".
