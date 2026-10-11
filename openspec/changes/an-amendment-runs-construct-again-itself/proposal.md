# Proposal

## Why

When the user approves a change to what a unit builds, nothing makes the unit start again. crew marks it amended and sends its conductor a one-off message asking it to run construct. If that message is lost, the unit just sits there and its old review card stays open. That happened on madswan on 2026-10-10: proposal 6 was approved at 00:58:53Z, construct never ran again, and when the conductor was restarted at 01:40 the pending run was forgotten (signal 2026-10-10-madswan-design-3d7ef799/01). Rule `plan.15` now says the approval itself starts the work again, and nothing should depend on anyone remembering to.

## What Changes

- **Approving an amendment starts the unit's construct again, as part of the approval.** This covers a proposal approved through `crew plan approve` and the user's own `crew unit amend`. Once crew has written the new intent, it runs `crew unit run <unit> construct` on the team's host, in the approver's name. The fresh construct agent is told the intent was amended, who amended it, and, for a proposal, the planner's case that the user approved.
- **Anyone who approves an amendment may start its construct.** crew no longer refuses to start construct on an amended unit because of who is asking: the user's approval already decided it. The usual check on who asked still applies when running construct is what marks the unit amended in the first place.
- **The old card is withdrawn by the conductor that owns it.** When construct starts on an amended unit, crew names the card that unit had open (its review card, or its verify card) to the team's conductor. The conductor is told when someone else started the construct, and sees it in the output when it ran the construct itself. When the construct could not start, crew's message about the amendment names that card instead.
- **The conductor is told what is happening, not asked to do it.** If construct started, the conductor is told to wait for it and take the unit through review again. If it could not start (the team is down, the host stopped answering, or the slot's agent is still working), the conductor is told why and to run construct once it can. The approval stands, and the unit shows as `amended`. If the team's host does not answer when crew reads where the unit stands, crew cannot tell what the amendment would end, so it refuses the amendment and writes nothing (`read.1`).
- **A conductor that is brought back finds amended units and starts them.** The greeting crew gives a conductor on `crew up`, `rebuild`, `restart` and `revive` names each unit of its bolt that shows as `amended`, which means no construct has run since the amendment, and tells it to start them. `crew resume` sends no greeting, so it sends the same line as a crew notice when there is such a unit. The conductor's brief now says: any unit of your bolt that `crew bolts` shows as `amended` gets its construct run.
- **The proposal page says what approval now does:** "On approval: construct runs again at once in swb-1's slot, and the unit returns to your review."

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-plan`: amending a unit with a worktree starts its construct again on the team's host, as part of the amendment, and its conductor is told what started or why nothing did.
- `bolt-teams`: an amended intent from an approved proposal starts construct with no step left to the conductor. A conductor brought back is told which units are amended and starts them. Anyone may start construct on an amended unit.
- `plan-proposals`: an amendment's page says that approving it starts construct at once in the team's slot.

## Impact

- `plugin/lib/plan.py`: `op_unit_amend`'s follow-up after the write, `run_check` (who may start construct, the wording of the prompt, the card it closes), the amendment's line on the proposal page, and a new internal read of a team's amended units for the greeting.
- `plugin/bin/crew`: `greet_conductor` and `resume` pass the amended units on.
- `plugin/lib/crew.py`: `greet` and its command line take the lead-in line crew passes.
- `plugin/roles/conductor.md`: the amendment paragraph and the brought-back rule.
- `README.md`, `plugin/skills/crew/SKILL.md`, the usage header of `plugin/bin/crew` and its `crew unit amend` line in `plan.py` (`docs.2`), `docs/architecture/plan.md` (`plan.15`'s details) and `_open.md`.
- Tests: `t-amend-intent.sh`, `t-amend.sh`, `t-greet.sh`, `t-briefs.sh`.
- `concurrent-units`, which has not been built, also modifies the `bolt-teams` requirement "A unit in flight goes back through construct and review" and the `plan-proposals` requirement "An amendment is read as before and after". Whichever of the two changes is archived second has to carry the other's wording for those two requirements.

## Touches

```
openspec/changes/an-amendment-runs-construct-again-itself/**
plugin/lib/plan.py
plugin/lib/crew.py
plugin/bin/crew
plugin/roles/conductor.md
plugin/skills/crew/SKILL.md
README.md
docs/architecture/plan.md
docs/architecture/_open.md
tests/t-amend-intent.sh
tests/t-amend.sh
tests/t-greet.sh
tests/t-briefs.sh
```

At archive, the deltas also edit `openspec/specs/bolt-plan/spec.md`, `openspec/specs/bolt-teams/spec.md` and `openspec/specs/plan-proposals/spec.md`, which `concurrent-units` also modifies.
