# Proposal

## Why

On 2026-10-19 the planner put proposal 161 before the user: a new crew bolt whose two units each cited a decision record, 0033 and 0034, that the user had not yet accepted. The user dropped it: "I don't understand why a plan is being shown to me before any design work is fucking done. What happened to the fucking designer?" (signal 2026-10-19-swancloud-planner-e269e093/01). The design agent's brief already says a unit is never queued from, or sourced on, a record still proposed (`briefs.15`), but nothing stops a proposal that does it. When an agent breaks a rule its brief states, crew adds a check that refuses the act (`roles.3`).

## What Changes

- `crew plan propose` reads every decision record named as a source by the bolts the proposal creates and the units and chores it makes new to a bolt (the units its card asks the user about: those it adds, and those it moves into a bolt). It reads each record on its kit's main as GitHub holds it now.
- A record counts as accepted only when its file there says `status: accepted` and holds no amendment still marked proposed, the same reading `crew record` uses.
- When any named record is not accepted, the proposal is refused and nothing is written, so no card is raised. The refusal names each unit or bolt, the record's number and kit, and what main holds: proposed, rejected, accepted with an amendment still proposed, no status, no such record, or more than one file with that number.
- A record crew cannot read, because the kit's main cannot be fetched, refuses the proposal too, naming what could not be read (`read.1`).
- A record is recognised in a source by its path, `docs/adr/<number>` with or without the rest of the file name. On its own it is a record of the unit's or bolt's kit; with `<owner>/<name>:` (or `<owner>/<name> `) before it, it is a record of that repository.
- Bolts and units already in the plan that the proposal only reorders, amends or drops are not read. Neither are approvals, nor direct writes to the plan.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plan-proposals`: a proposal is refused when a bolt it creates, or a unit or chore it makes new to a bolt, names as a source a decision record not accepted on its kit's main.

## Impact

- `plugin/lib/plan.py`: `plan_propose` gains the check; the status reading inside `record_facts` moves into a function both use, so `crew record` and the proposal check read a record's status the same way.
- `tests/py/test_proposals.py`: logic cases for finding records in sources and judging their status. `tests/t-journey-plan.sh`: one step proving the wiring, a proposal refused on a proposed record and written once it is accepted.
- `README.md`: the line on how `crew plan propose` checks a proposal says it also checks the records.
- Nothing changes for the plan's files, the board's views, or the mod.

## Touches

```
plugin/lib/plan.py
tests/py/test_proposals.py
tests/t-journey-plan.sh
README.md
```
