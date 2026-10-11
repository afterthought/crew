# Tasks

## 1. The sources reach the construct, and govern what it builds

- [x] 1.1 The signal-recording line every brief shares says to name, in the signal's sentence, where anything the words point at lives, in a form another agent can open (design.md, Task notes 1.1). Verify `crewpy brief wldn planner` prints it, through `tests/run t-briefs`.
- [x] 1.2 The planner's and the design agent's briefs say a unit from a signal names with `--source` what the signal points at (design.md, Task notes 1.2). Verify through `tests/run t-briefs`.
- [ ] 1.3 The construct's brief says to read every source as it stands on main and what each points at, a signal with `crew signal show`, to stop and ask through crew when one can't be opened, to write the change from the sources where the intent says more or otherwise, and to open the final message with the difference (design.md, Task notes 1.3). Verify `crewpy brief swb-1 construct` prints the new bullets with no token unfilled, through `tests/run t-briefs`.
- [ ] 1.4 `tests/t-briefs.sh` pins the new phrases in the recording line, the planner's, the design agent's and the construct's briefs (design.md, Task notes 1.4). Verify `tests/suite t-briefs` ends with "0 failed".
- [ ] 1.5 `docs/architecture/_open.md` lists only the spike as not built under `briefs.14` (design.md, Task notes 1.5). Verify `tests/suite --affected` ends with "0 failed".
