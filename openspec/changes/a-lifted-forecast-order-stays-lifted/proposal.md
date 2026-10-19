# A lifted forecast order stays lifted

## Why

When crew forecasts that two unfinished units will conflict when they merge, it puts the later one after the earlier at once, before anyone has looked at whether the conflict is real. When the later unit's settle then finds nothing to change, the unit is finished but held behind the other's merge, and the only way out today is a proposal to lift the order: a card for the user each time. In wldn's swb-1 on 2026-10-15, two of the day's five cards for one bolt were such proposals (346 and 347), and the user, approving 347, asked: "Approved but this is like the tenth time I've seen this. Why does this keep coming back at me?"

Worse, a lift does not stick. After the user approved proposal 346, lifting the order crew had put on an-image-is-built-once-per-digest, the next forecast on new heads wrote the same order back, under the conductor's name, while the unit's merge ran (signal 2026-10-15-swancloud-planner-9bc1342c/01). Nothing records that the order was lifted or that the settle found the conflict empty, and the forecast asks only whether the unit already comes after the other.

The rules already say what must hold instead (`plan.13`, `teams.12`, `teams.14`, amended 2026-10-15); this change builds it.

## What Changes

- A forecast conflict between two unmerged units no longer orders them. The forecast still reaches the later unit, with the same words, in the same ways (told, carried in its next prompt, or as a settle stage).
- crew puts the later unit after the earlier one only when the later unit's settle delivers a commit that takes the earlier unit's work, at most once for a pair, in the conductor's name, and only while both are unmerged. A settle that finds nothing to change orders nothing.
- An order crew wrote from a forecast whose settle then ended with no commit, and whose branch does not hold the other's work, is lifted by crew itself: when the conductor's wait sees that settle end, and again on each wait after, so orders crew wrote before this change are cleared the same way.
- An order crew wrote that someone else lifted (the user by proposal, or the conductor by hand) is never written back.
- The conductor's and planner's briefs say crew orders and lifts its own forecast orders: no proposal and no card asks the user to undo one.
- The run record says, on crew's own order writes, which pair was ordered or lifted and why.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a forecast conflict between two units orders them only once the later unit's settle takes the earlier's work; crew lifts an order of its own whose settle found nothing to change; an order someone else lifted stays lifted.
- `bolt-plan`: a unit's `After` names a unit a settle took the work of after a forecast conflict, not one a forecast alone put it after.

## Impact

- `plugin/lib/plan.py`: the conductor's wait (`reach`) stops writing `After` at a forecast; one decision says, from the run record and the plan, which pairs crew orders and which it lifts; the wait applies it at a settle's end and at the start of every wait.
- `plugin/roles/conductor.md`, `plugin/roles/planner.md`: say how crew orders and lifts, and that nobody proposes lifting crew's own order.
- README, the crew skill and `crew unit wait`'s usage (`docs.2`): how a forecast and a settle order two units, and the run-record fields crew's order writes carry. The rules' not-built clauses and `_open.md` are left to the design agent after the landing (`docs.7`).
- Tests: the logic tier for the decision, and the slots and merge journeys for the wait.
- Every conductor picks this up at its next wait; nothing to restart. A standing planner or conductor learns the brief's new words at its next fresh start.

## Touches

```
plugin/lib/plan.py
plugin/roles/conductor.md
plugin/roles/planner.md
tests/py/test_forecast.py
tests/t-journey-slots.sh
tests/t-journey-merge.sh
tests/t-briefs.sh
tests/moon.yml
README.md
plugin/bin/crew
plugin/skills/crew/SKILL.md
openspec/specs/bolt-teams/spec.md
openspec/specs/bolt-plan/spec.md
```
