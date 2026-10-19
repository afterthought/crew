---
number: 33
title: A unit waiting to merge yields its slot to the work it waits on
status: rejected
date: 2026-10-19
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# A unit waiting to merge yields its slot to the work it waits on

Status: rejected by the user on 2026-10-19, on their card: "What the goddamn fuck is this? How is this a fucking ADR? You're not paying attention to the goddamn design". The design as written holds: a slot is taken when a unit's first stage starts and freed when the unit merges or is dropped (`bolt-teams` spec, *Units run in slots*; `teams.1`), and the deadlock's cause is the merge that stopped short for archives its own stage could make, which record 0034 rules; with that cause gone there is no chore to wait for and no slot to yield. `teams.1` stands unamended.

Deciders: swancloud-design, on wldn-planner's finding (2026-10-19, signal 2026-10-19-swancloud-planner-e9298b79/01: "a team with one unit slot cannot build a chore its bolt needs to land ... A unit waiting on an unblocker should not hold the slot the unblocker needs, or an --unblocks chore should run outside the slot count. For now the user is asked for a second awb-1 slot."); the user, on this card.
Amends: `teams.1`.
Sources, read on 2026-10-19: `teams.1`, `teams.2`, `teams.5`, `teams.12`, `teams.14`, `teams.16`, `plan.5`, `plan.9`, `plan.10`, `plan.11`; record 0001 (`--unblocks`), record 0020; crew's main at e91f51f: `plan.py` `run_unit_stage` ("all N of the team's slots are in flight"), `slot_stage`, the status read that frees a slot "whose work has merged, been dropped or left the team's bolt, once its agent is not working"; `tests/py/test_slots.py`.

## Context and problem statement

A slot is held by a unit from its first stage until its work has merged (`teams.1`), and between stages no agent of the unit runs (`teams.2`, `teams.4`): a unit that has delivered its verify and waits for the units ahead of it in the bolt's merge order (`teams.5`) holds a slot that does no work. Work a held bolt needs before it can land goes into that bolt ahead of its first unmerged unit, marked `--unblocks` (`plan.5`). On a team whose slots are all held by units waiting to merge, the unblocker ahead of them can never start: wldn's awb-1, with one slot, holds `the-production-class-account-is-seeded` at verify, its merge waits on the chore `the-seeds-specs-are-archived-before-it` placed ahead of it by the approved proposal 409, and crew refuses the chore's code stage for want of a slot. The bolt is stuck for as long as nobody adds a slot, and the same stands for a four-slot team whose four units all wait on one chore.

The question is which gives: the slot count, which bounds how many stages run at once on a host (`teams.1`, `tests.9`), or the waiting unit's hold on a slot that runs nothing.

## Decision drivers

- A slot bounds load: how many stages run at once. A unit waiting to merge runs nothing, so its hold on a slot bounds nothing.
- No lane of its own for `--unblocks`: a special count for one kind of chore is the hard-coded case the user has turned down elsewhere (record 0020, record 0019's sources).
- A second slot is the user's choice for throughput (`teams.16`), not the remedy for a deadlock in crew's bookkeeping.
- A unit's verified work is kept: its place and branch stay, as `plan.9` and `plan.10` keep unmerged work, and nothing is requeued (`teams.1` rules out a slot kept for a requeued unit).
- The waiting unit is not starved: once what it waited on has merged, it merges before a unit behind it starts.

## Considered options

1. **The waiting unit yields its slot.** A unit that has delivered its verify, and its fix round when one ran, and waits only on work ahead of it in the merge order gives up its slot when that work has none and the team has none free; its place and branch stay and its merge is owed; it takes the first slot freed, ahead of any unit behind it.
2. **An `--unblocks` chore runs outside the slot count.** The count no longer bounds load, a one-slot team runs two stages, and a unit waiting on a unit ahead of it (not a chore) stays stuck the same way.
3. **A second slot, added by the user.** What wldn asked for meanwhile: a cost per team and a card for a deadlock crew made.
4. **The waiting unit is dropped and requeued.** Loses a verified change and the slot rule rules it out.

## Decision outcome

Option 1.

1. **A slot bounds stages, not units.** A team never runs more than `units` stages at once. A unit or chore holds a slot while one of its stages runs or may start; between its verify's delivery and its merge, while its merge waits on work ahead of it in the bolt's merge order (`teams.5`), it holds a slot only as long as that work has one of its own or the team has a slot free.
2. **The waiting unit yields.** When the work ahead has no slot and the team has none free, the waiting unit's slot goes to it: the unit's place and branch stay as they are, its stage reads as waiting to merge with its merge owed, and crew's status says which unit yielded to which. The unit's agent is already stopped at that point (`teams.2`); nothing of its work is touched.
3. **The yielded unit comes first.** The first slot the team frees goes to a unit that yielded, before any unit behind it in the merge order starts a stage, so a yield delays a merge and never loses its turn. A settle stage that reaches a yielded unit (`teams.12`, `teams.14`) runs once it has a slot again, under the same claim.
4. **Nothing else changes.** `plan.5` still places the unblocker ahead of the first unmerged unit; a chore's and a fix's slots are as `plan.11` and `teams.3` have them; the carrying fix of a proven bolt still takes a slot (`teams.16`); the slot count is still the teams file's and the user's.

Once accepted: `teams.1` reads as amended below; the unit the planner proposed for wldn's finding on proposal 156 builds it in crew, with this record as its source; wldn's second slot, if given, is the user's to keep or take back.

## Consequences

Good: no bolt waits on a slot that runs nothing; a one-slot team can land a bolt that needs an unblocker; the slot count keeps its meaning as the bound on load. Bad: a slot can change hands between a unit's verify and its merge, so a status read and a conductor's wait have one more state to show, waiting to merge with no slot. Neutral: nothing lands or merges sooner; the unblocker still runs code, verify and merge in its turn.
