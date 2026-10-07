# Proposal

## Why

Decisions reach the user from several panes, and nothing lists them. The user asked for "one place that showed me the list" to work down, the simplest thing crew can do today, and one that goes stale on its own: once a decision is answered it must leave the list without anyone clearing it. They also asked for "a column with the time/age so I know how old each is, and ordered" (`docs/adr/0002-what-waits-on-the-user-is-shown-whole-and-read-from-state.md`, "One list, read from state").

## What Changes

- **`crew rail [--label L]`, run on any host, prints everything that waits on the user, in four groups and always in this order:** open proposals, units in review, verify reports the user hasn't answered, and bolts ready to land. Every group heading is printed, with "none" under an empty one, so the list keeps its shape as it refreshes.
- **Each row says what it is, when it began to wait, and how long ago that was.** It also carries the command that answers it, written to be pasted. Rows are oldest first within each group, so the top of each group has waited longest.
  - An open proposal shows the conductors whose agreement it still needs. It carries the command that prints it, the command that opens it in plannotator for the user to read and annotate, and the command that approves it. It began to wait when its proposal was recorded in the run record, or on the day it was opened when that entry can't be found.
  - A unit in review carries the plannotator command that opens its whole change: proposal, design, specs and tasks. It also carries the command that approves it. It began to wait at the last commit on the unit's branch.
  - A unit in verify is listed once its newest verify report is newer than the unit's last commit. The row shows the report's path, the command that opens it, and a `crew tell` to its conductor for the user to finish in their own words. It began to wait when the report was written.
  - A bolt whose units have all merged and that hasn't landed shows its team. It carries a `crew tell` asking the partition's main-level ops to land it. It began to wait at the last merge into the bolt's branch.
- **Nothing is written to put a row on the list or take it off.** Every row and every time is read from the proposals, the plan, the kits on each team's host and the run record. A row is gone the moment its answer is recorded. A host that doesn't answer is named, as `crew bolts` names one.
- **`crew plan proposed <n> --open` opens a proposal in plannotator.** It writes the proposal, as `crew plan proposed <n>` prints it, to a file on the host it runs on and opens that file in plannotator beside the caller. A proposal lives on the flywheel's branch, not in a file, so this is what lets its row open it, from any host, as a unit in review's row opens its change.
- **The operator workspace gets a `rail` tab beside `flow`, split in two.** The list is on top. It is printed again every 30 seconds, and as soon as the run record gains an entry. A shell below has crew on its path, so the user can paste a row's command there.
- **The operator agent answers "what waits on me" from `crew rail`.** It also points the user to the rail tab for the commands.

## Capabilities

### New Capabilities

- `crew-rail`: the list of everything that waits on the user, read from state, with each row's time, age and answering command.

### Modified Capabilities

- `plan-proposals`: `crew plan proposed <n> --open` opens a proposal in plannotator.
- `operator-agent`: the operator agent answers what waits on the user from `crew rail`, and the operator workspace has a `rail` tab with the list above and a shell below.

## Impact

- `plugin/lib/plan.py`: a new `crew rail` command, and `--open` on `crew plan proposed <n>`. It reuses the plan and proposal reads and the kits survey, and reads run-record entries through `record.py`'s existing gather.
- `plugin/lib/gather.py`: each unit worktree's head time, each bolt branch's head time, and each team's newest verify report per unit, all read in the same call that already reads the kits.
- `plugin/bin/crew`: `rail` dispatched to `plan.py`, the usage text, the `rail` tab opened by `crew operator up`, and the loop that refreshes it.
- `plugin/roles/operator.md`: "Where things stand" reads `crew rail`.
- `README.md` and the crew skill (`plugin/skills/crew/SKILL.md`): `crew rail`, the rail tab and `crew plan proposed <n> --open`.
- Tests: a new `tests/t-rail.sh`; a new stub `tests/stubs/plannotator-tui`; the tab in `tests/t-record-team.sh`; the brief in `tests/t-briefs.sh`.
- The operator agents take the brief at their next fresh start, or when told what changed. The tab opens at the next `crew operator up`.

## Touches

`plugin/lib/plan.py` (a new rail command, its parser entry and the `COMMANDS` table, `survey()`'s request, and `plan_proposed()` with the `proposed` parser entry and the module docstring's usage line for `--open`), `plugin/lib/gather.py` (`place()` and `kit()`), `plugin/bin/crew` (the usage header, the command `case`, `ensure_flow`'s neighbour and `operator up`), `plugin/roles/operator.md` ("Where things stand"), `README.md` ("The main level and the operator agent", and the plan's `crew plan proposed` lines), `plugin/skills/crew/SKILL.md` (its table), `tests/t-rail.sh` (new), `tests/stubs/plannotator-tui` (new), `tests/t-record-team.sh`, `tests/t-briefs.sh`, `openspec/specs/operator-agent/spec.md` (by delta), `openspec/specs/plan-proposals/spec.md` (by delta), and `openspec/specs/crew-rail/spec.md` (new, by delta).
