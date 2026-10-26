---
status: proposed
date: 2026-10-26
decision-makers: the user, swancloud-design
consulted: madswan-planner, swancloud-planner, trc-1-conductor, fww-2-conductor
---

# A unit in a slot put after unconstructed work goes back to waiting, its branch kept

Status: proposed to the user on 2026-10-26, as `briefs.15` has it; accepted only on their yes.

Deciders: the user, on this record's card; written by the design agent from madswan-planner's and the conductors' findings of 2026-10-25 and 2026-10-26.
Amends: `plan.md` (adds a clause to `plan.13`); `teams.1` stands unamended.
Sources: swancloud signals 2026-10-25-swancloud-operator-84d19ee2/01 and 2026-10-26-swancloud-operator-4656d145/01; madswan signal 2026-10-25-trc-1-conductor-6fc138fe/01; records 0003, 0033 (rejected) and 0034 (rejected); `plan.py` `stage_refusal`, `run_check`, `take`; `crew.py` `slot_for`, `reaped`.

## Context and problem statement

A slot is taken when a unit's first stage starts and freed when the unit merges or is dropped (`teams.1`, the `bolt-teams` spec *Units run in slots*); the user rejected record 0033, a unit yielding its slot while it waits, on 2026-10-19, and that design holds. A dependent's construct starts only once each unit or chore it comes after has finished construct (`plan.13`), and work with no place reads `waiting` until then.

Two findings met where those rules do not reach. On trc-1 (2026-10-25), an approved amendment put status-on-any-machine, already in a slot with a place, after a new unit with no change yet; crew did not hold its construct, since it holds a construct for its After only when the unit reads `waiting`, which a unit with a place never does, and ran the taking instead. On fww-2 (2026-10-26), a chore every unit of the bolt needs, an OpenSpec root, was added ahead of the units while every slot held a unit that now came after it: no unit can merge before the chore, the chore gets no slot while they hold every one, and `crew unit free` refuses a unit in the bolt. The only way out was dropping a unit and adding it back, by hand.

The plan is what the bolt builds, in the file's order and its `After` (`plan.13`). An amendment that puts in-flight work after work not yet constructed re-plans that work: its construct runs again anyway (`plan.6`), and until the work it now comes after exists there is nothing for it to build on. The slot it holds is capacity the plan's new order needs elsewhere.

## Decision outcome

Option 1. A unit holding a slot that a plan write puts after work whose change is not yet committed, a unit not through construct or a chore whose code has not delivered, goes back to `waiting` as that write's own act, whether the write is a proposal applied, `crew unit after`, or a unit or chore added before it: its place is removed, its branch kept when it holds commits the bolt lacks and named (`plan.10`, record 0003), its slot freed as a dropped unit's is (`teams.1`), and the run record says which write sent it back and what it comes after. It starts construct again, from the kept branch when there is one, in a free slot once each unit or chore it comes after has finished construct, taking their heads as a first construct does (`plan.13`); its stage reads `waiting` until then, and `crew unit run <unit> construct` before then is refused naming the work whose change is not committed, as it is for a unit with no place. The same holds for a unit that reads `waiting` by this rule when its After is lifted: it is planned again and starts in a free slot.

Nothing yields: a unit in a slot keeps it from its first stage to its merge or drop, and this rule adds no third way out; the write that re-planned the unit is what ended its stage.

## Considered options

1. The write sends the unit back to waiting, its branch kept. Chosen: the plan is the plan, the unit's construct runs again either way (`plan.6`), the work is kept as a drop keeps it (record 0003), and the slot goes to the work the new order needs first; no deadlock can form, since no slot is held by work that cannot start.
2. Refuse the write while a unit it would put after unconstructed work holds a slot. Rejected: it refuses the plan the planner and the user want, and leaves the way out they took on fww-2 as the only one, by hand, a drop and an add back, which is option 1 done slowly.
3. A unit waiting on unconstructed work yields its slot and takes it back. Rejected by the user as record 0033 on 2026-10-19; a slot is held from first stage to merge or drop.
4. Leave it: a unit put after unconstructed work keeps its slot and waits for another slot to free. The reading of 2026-10-25 in `plan.13`'s rationale; rejected here, since a team whose slots all hold such units never frees one, and the deadlock is the plan write's to avoid, as the merge's was its own (record 0034's reading).

## Consequences

- `plan.13` gains the clause; `teams.1` and the `bolt-teams` spec stand.
- A crew unit builds it: the plan writes (`unit after`, `unit add --before`, `chore add --before`, a proposal's apply) end the stage of a unit they put after unconstructed work, remove its place through the drop's own path keeping its branch, free its slot, and record it; `Stages` reads such a unit `waiting`; `stage_refusal` holds a construct for its After on any unit whose After is not built on, not only one with no place (the chore proposed 2026-10-25 folds into this unit); `make_place` already starts from a kept branch (record 0003).
- A unit sent back whose kept branch holds work takes none of its After units' heads at its next construct, since TAKE takes only into a place that holds nothing beyond the bolt; what it comes after is then taken by hand, the open question `plan.13`'s rationale already names (`_open.md`).
- Until it is built, the way out is the planner's: drop the unit and add it back under the same name, which starts from the kept branch.
