# Proposal

## Why

A finding outside a unit's work is a signal, and waits for curation. But some findings are about the unit in hand, and stop it: a stage discovers that what it is building rests on something that is wrong or undecided. Sending those through a batch of curation would stall a bolt for days, and letting the unit merge anyway would land work the answer may undo. The user's ruling on the findings-to-design proposal covers both sizes:

> Finding that blocks a bolt's work should be handled in the bolt unit directly by amending the unit. The conductor should ask me. If it's a big change, it could go back out to curation and design and then get routed back in as a new unit that has to get merged before the current unit can complete.

and, for a design question only the user can answer, that it becomes a design item with the unit waiting, where "the answer might be something new getting planned but it could also be a direct answer that comes from design".

`unit-amendments` built the small case: the conductor runs construct again with the user's words. This change builds the large one. It is step 7 of the findings-to-design work (`openspec/explorations/findings-to-design/proposal.md`, "A finding that blocks the unit it was found in"; `roadmap.md`).

## What Changes

- **The conductor asks the user first.** Its brief says so: a finding that blocks a unit is put to the user in the words of whoever raised it. A small change amends the unit in place. Nothing below happens without the user saying the finding is big, or is a question for design.
- **`crew signal … --blocks <unit>`** records the finding as a signal and, in the same commit, marks the unit held by it (`Hold: signals/<id>` in the plan).
- **A held unit does not merge.** `crew unit run <unit> merge` is refused while a hold stands. Its other stages may go on, at the conductor's and the user's discretion. `crew bolts` and `crew agenda` show the hold.
- **The hold ends with whatever settles the signal**, in the same commit:
  - a move that leads nowhere (`attach`, `challenge`, `answered`, `drop`), or an item closed with a direct answer and no unit, lifts it, and crew tells the conductor the result;
  - an item that yields a new unit turns the hold into a dependency: when the unit enters the held unit's bolt, the held unit comes `After` it.
- **`After` is checked at merge.** A unit that has started, and then gains a dependency, cannot merge until that unit has merged into the bolt. Today `After` is checked only before a unit starts.
- **A unit that came of a blocking finding goes into the held unit's bolt.** A proposal that would put it elsewhere is refused, unless it releases the hold.
- **`crew unit release <unit> "<why>"`** lifts a unit's holds on the user's word.

## Capabilities

### New Capabilities

- `unit-holds`: how a finding that blocks its own unit is handled: the conductor's question, the hold a blocking signal places, what a held unit may and may not do, and how a hold ends.

### Modified Capabilities

- `bolt-plan`: a dependency stops a started unit from merging, not only an unstarted one from starting.
- `plan-proposals`: a proposal may hold `unit release`, and must put a unit that came of a blocking finding into the held unit's bolt.

## Impact

- `plugin/lib/plan.py`: `--blocks` on `crew signal`; the `Hold` mark in the plan's schema; the merge refusals for a hold and for an unmerged `After`; the lifting of holds inside deliveries, hand moves, replacements, `agenda close` and approvals; `crew unit release`; `crew bolts` and `crew agenda` showing holds.
- `plugin/roles/conductor.md` (the whole path), `curator.md`, `planner.md` and `design.md` (an item that holds a unit).
- `README.md`, `plugin/skills/crew/SKILL.md`, the usage header, `tests/`.
- Depends on `unit-amendments`, `checked-capture` and `curation-and-agenda`.

## Touches

`plugin/lib/plan.py`, `plugin/bin/crew`, `plugin/roles/conductor.md`, `plugin/roles/curator.md`, `plugin/roles/planner.md`, `plugin/roles/design.md`, `plugin/skills/crew/SKILL.md`, `README.md`, `tests/`.
