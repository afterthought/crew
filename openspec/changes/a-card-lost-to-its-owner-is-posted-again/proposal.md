# A card lost to its owner is posted again

## Why

A Pending You card belongs to the sign-in of the host its owner posted it from. When a host signs in again, every card posted before reads "not found" to the agent that posted it, while the user still sees it and can still answer it, to nobody. On 2026-10-11 the planner found its two oldest open cards, proposals 17 and 99, gone so, and posting again under the rows' keys made second cards the user could not tell from the first (signal 2026-10-11-swancloud-planner-291133cb/01). ADR 0005, amended that day, rules that each owner posts its open rows' cards again, each new card's summary saying the older copy is dead, and that the dead copies are the user's to dismiss in the app. The card discipline crew gives its agents says nothing of a lost card today, and the rail keeps showing the dead copy as the row's open card.

## What Changes

- An agent that owns a rail row and finds the row's card "not found" in Pending You, whether a tool answered so or a check it makes at its start or after calling `whoami` again found it, posts the row's card again under the row's own key, in the row's form, with its usual words. Its summary, after the link and the bolt, says in plain words that an older copy of this card is dead, to dismiss it in the app, and that this one is the one to answer. This holds for the planner's and the conductors' rows, through the card discipline crew writes into their briefs, and for main-level ops's operations rows, in its brief.
- A lost card whose row is gone is posted again by nobody: its owner does nothing more with it.
- `crew rail` prints, on a row's card line, the id of the open card, so an owner started afresh can check its card with Pending You by that id.
- When an owner posts a second card under a row's key while its first is still open in the run record, the rail takes the newer as the row's card and the older as lost: the older is no longer shown as the row's open card, and is not listed among the open cards with no row, since its owner cannot close it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a row's card that reads not found to its owner is posted again under the row's key, saying the older copy is dead; the rail names the open card's id and takes a newer card under a key as the row's, the older as lost.

## Impact

- `plugin/lib/crew.py`: the card discipline (`cards_how`) gains the lost card.
- `plugin/roles/main-ops.md`: *Deploying main* gains the lost card for its operations rows.
- `plugin/lib/plan.py`: `rail_record` takes a newer post under a key as replacing the older open card of the same owner; `rail_text` prints the open card's id.
- README and the crew skill: the rail's card line names the open card's id, and the lost card. `crew`'s usage header already says only that the rail shows each row's card, and is unchanged.
- `tests/t-briefs.sh`, `tests/t-rail.sh`.

## Touches

```
plugin/lib/crew.py
plugin/lib/plan.py
plugin/roles/main-ops.md
README.md
plugin/skills/crew/SKILL.md
tests/t-briefs.sh
tests/t-rail.sh
```
