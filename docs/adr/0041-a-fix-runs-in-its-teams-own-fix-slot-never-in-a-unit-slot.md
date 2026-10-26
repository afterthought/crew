---
status: proposed
date: 2026-10-26
decision-makers: the user, swancloud-design
consulted: madswan-planner, swancloud-planner
---

# A fix runs in its team's own fix slot, never in a unit slot

Status: proposed to the user on 2026-10-26, as `briefs.15` has it; accepted only on their yes.

Deciders: the user, on this record's card; written by the design agent from madswan-planner's finding of 2026-10-26.
Amends: `teams.1`, `teams.3` and `teams.16` (a fix's slot); the `bolt-teams` spec, *Units run in slots*, gains the fix slot.
Sources: madswan signal 2026-10-26-madswan-planner-7afa4cff/01, swancloud's 2026-10-26-swancloud-operator-942ec4f8/01; records 0001 (a fix is the conductor's answer to its bolt, with no plan record), 0033 (rejected: no unit yields its slot), 0034 (rejected: a deadlock is the act's to avoid that made it) and 0040 (a plan write that re-plans a unit frees its slot); `crew.py` `slot_for`, `reaped`; `plan.py` `fix_cmd`, the take-main fix (`teams.21`, `plan.8`).

## Context and problem statement

A slot is held from a unit's first stage to its merge or drop (`teams.1`; record 0033 rejected), a team never has more than `units` in flight, and a fix, the conductor's answer to something broken on its bolt (record 0001), runs in a unit slot like a unit (`slot_for`, `teams.16`'s "a carrying fix's slot"). On tailrace-sync-and-serve (six slots), every slot held a unit whose committed change waited to merge behind the take-main fix the forecast called for (`teams.21`), and crew refused the fix for want of a slot: the bolt could not move until a unit was dropped by proposal. Nothing in the plan made this; the bolt's own health, a fix, waited on the plan's capacity, which the units had used as the plan meant them to.

A fix is not plan work: it carries no plan record, it is placed by no one, and it answers the bolt, a conflict with main, a landing's defect, a stage's breakage, which every unit of the bolt waits on. A thing every unit waits on must not wait on the units.

## Decision outcome

Each team has one fix slot beside its unit slots, `<team>-fix`, with its own pane in the team's workspace, and a fix runs there and never in a unit slot: the take-main fix, a landing's held fix and any fix the conductor starts. One fix runs at a time; a second waits for the first, named, since fixes of one bolt build on one another. The fix slot is freed as a unit slot is (`teams.1`), when its fix has merged or been dropped and its agent has stopped, and the proven bolt keeps it with its ops for its landing (`teams.16`). `units` counts units and chores alone, and a team never has more than `units` of them in flight; a fix stands beside them. A fix already running in a unit slot when this lands finishes there.

## Considered options

1. A fix slot of its own per team (chosen): a fix never competes with the plan's work for capacity, so the bolt can always be mended, and nothing yields.
2. A fix borrows a unit slot whose unit waits on the fix. Rejected: that is a unit yielding its slot, which the user rejected as record 0033.
3. Drop a unit to free a slot, by proposal, as madswan-planner did. Rejected as the way: a plan change and a card for the bolt's own repair, and the dropped unit's work waits on a kept branch for nothing the plan wanted.
4. Leave a slot free by rule, `units` minus one for units. Rejected: it taxes every team always for a fix that runs sometimes, and a team with one slot could never build.

## Consequences

- `teams.1`, `teams.3` and `teams.16` gain the clauses, marked proposed.
- A crew unit builds it: the team's workspace gets the fix pane and crew's slots file the fix slot; `slot_for` gives a fix the fix slot or refuses naming the fix that holds it; `reaped` frees it; the take-main fix and `crew fix` run there; the status and the board show it; `tests/py/test_slots.py` and the journeys prove it.
- A team's herdr session shows one more pane per team.
