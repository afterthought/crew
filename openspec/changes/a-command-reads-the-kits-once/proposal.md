# Proposal

## Why

A `crew` command is several `plan.py` runs, and each run reads the kits and fetches the state branch again. Reading a kit starts the `openspec` command line twice for every unit in flight, about 0.65 s a unit, so `crew status` on a team with three units in flight pays about 2 s for every read and reads two or three times. The same cost is most of the test suite's twenty minutes: in its two slowest tests, 23 and 29 kit reads took about half the time (`openspec/explorations/command-cost/reading.md`). The rule is already written as `plan.12`; crew does not hold to it yet.

## What Changes

- **A command reads each kit once and fetches the state branch once, on each host it runs on, however many steps it has.** The first step that reads keeps what it read for the command's later steps. A step that changes a kit (making a unit's or fix's place, removing a finished worktree) makes the next step read that kit again. A plan write starts from the tip the command already holds, and fetches again only when its push is refused because the branch moved, as every write already does.
- **Waiting and watching still read afresh.** `crew unit wait`, `crew fix … --wait`, `crew prove … --wait`, the rail tab's loop and `crew events --follow` look again each time they look, as they do now.
- **crew reads a unit's tasks and whether its planning is complete from the change's files, without `openspec`,** by the same rules `openspec` 1.14 uses: which lines count as tasks, which count as done, and which files make a change's planning complete. A change that names a workflow other than OpenSpec's standard one, or a kit that redefines the standard one, is read through `openspec` as now, for that unit alone.
- **A test holds the two readings to each other.** On the same worktrees, crew's reading and `openspec`'s give the same task counts and the same planning answer, across the task styles and change layouts `openspec` treats differently. The suite needs `openspec` installed to run, and says so when it isn't.
- **The test harness's stub `herdr` costs about half what it does now**, behaving exactly as before.
- No command's output or behaviour changes, other than how fast it answers.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-plan`: a unit's tasks and planning mean what OpenSpec means by them, read by crew from the change's files and held to `openspec`'s reading by a test; a command reads each kit and the plan once on each host it runs on.

## Impact

- `crew status`, `crew unit run`, `crew fix`, `crew prove`, `crew rebuild`, `crew unit free` and the internal steps they run answer faster; their output is unchanged.
- Every test that runs those commands gets faster. The suite's total time is measured at the bolt's verification and again once landed.
- `openspec` stays required on every host: a change naming another workflow is still read with it, and the suite's agreement test runs it.
- `crew status` with no team named forwards to each team's host once per team, so two teams of one kit on another host still read that kit once each. Folding that into one forward per host is not this change's.
- Folding a command's several `plan.py` runs into one Python run (the reading's other lever) is not this change's.

## Touches

- `plugin/lib/gather.py` (the direct reading of tasks and planning, every bolt branch read)
- `plugin/lib/plan.py` (the command's reading: `fetch`, `land`, `survey`, `make_place`, `tidy`, `deliverable`, `ticks`, `run_check`, `stage_wait`)
- `plugin/bin/crew` (the command's reading made, shared with nested runs and removed; none for the rail loop or an exec'd single run)
- `tests/run` (requires `openspec`), shared by every test
- `tests/stubs/herdr`, shared by every test
- new `tests/t-stage-facts.sh` and `tests/t-reads-once.sh`
- `docs/architecture/plan.md`, `docs/architecture/_open.md`
