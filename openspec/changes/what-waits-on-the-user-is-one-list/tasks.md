# Tasks

## 1. The kit read carries the times

- [x] 1.1 The kit read on each host also gives each unit worktree's head time, each bolt branch's head time and each unit's newest verify report with its time, in the same call (design.md, Task notes 1.1). Verify `devenv shell -- tests/run t-bolts t-sites` ends with "0 failed".

## 2. crew rail

- [x] 2.1 `crew rail [--label L]` prints the four groups in order, each row with its time, age and commands, oldest first, read from the plan, the proposals and the kits, with an unreachable host named (design.md, Task notes 2.1). Verify `tests/t-proposals.sh` still passes.
- [x] 2.2 A proposal's row is timed by its `plan.propose` entry in the run record, or by its `Opened` date when none is found (design.md, Task notes 2.2).
- [x] 2.3 `crew plan proposed <n> --open` opens the proposal in plannotator from any host, and a proposal's row carries it (design.md, Task notes 2.3).
- [x] 2.4 A review or verify row's open command is `plannotator-tui herdr open` on the team's own host, and `ssh -t <host> plannotator-tui` from any other (design.md, Task notes 2.4).
- [ ] 2.5 `tests/t-rail.sh` holds every group, the order, the times, the commands on each host, opening a proposal, the row leaving once answered, the read writing nothing, and an unreachable host (design.md, Task notes 2.5). Verify `devenv shell -- tests/run t-rail` ends with "0 failed".

## 3. The rail tab, the brief and the docs

- [ ] 3.1 `crew operator up <label>` opens a `rail` tab once, with the list above (refreshed every 30 seconds and on each run-record entry) and a shell below with crew on its path, and `crew rail` is in crew's usage (design.md, Task notes 3.1). Verify the new checks in `tests/t-record-team.sh` and `tests/t-operator.sh` pass.
- [ ] 3.2 The operator's brief has it answer what waits on the user from `crew rail` and point the user to the `rail` tab for the commands (design.md, Task notes 3.2). Verify the `wldn operator` checks in `tests/t-briefs.sh` pass.
- [ ] 3.3 The README and the crew skill describe `crew rail`, the `rail` tab and `crew plan proposed <n> --open` (design.md, Task notes 3.3). Verify `devenv shell -- tests/run` ends with "0 failed".
