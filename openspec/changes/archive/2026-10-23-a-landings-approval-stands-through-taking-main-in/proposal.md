# A landing's approval stands through taking main in

## Why

When the user ticks a bolt on a kit's landings card, crew ties that yes to the bolt's head as it stood. If sluice then refuses the landing because the bolt conflicts with main, the team takes main into the bolt with a fix, the bolt's head moves, and crew asks the user to approve the same bolt again, though nothing of its own work changed. On 2026-10-23 and 24 the user approved `bolts-live-on-github` four times in three hours this way (record 0031, as amended 2026-10-24). The user: "I shouldn't have to reapprove after an approved landing that had a merge conflict and then gets merged again" (wldn signal 2026-10-24-wldn-ops-2dd52ecd/01), and "it feels like I have to approve the same cards like ten fucking times" (signal 2026-10-24-swancloud-design-6ee99e08/01). Record 0031's amendment of 2026-10-24, accepted on the user's card, settles it: the approval is for the bolt's work, not its head.

## What Changes

- **A yes stands while the bolt's own work is unchanged.** When a bolt the user ticked moves to a new head only by taking main in, or by its host copy being brought level with GitHub's, crew keeps the user's send for it. Once sluice has proven the new head, main-level ops lands it on that send, and no card asks for it again.
- **What "its own work" means.** The bolt's own work is the set of non-merge commits its head holds that GitHub's main does not. Taking main in adds only merge commits, conflict resolutions included, so it leaves that set as it was. Any commit of the bolt's own added or gone between the head the user sent and the head now is a change of its work.
- **A changed bolt is asked again, saying what changed.** When the bolt's own work did change, it is a row of a landings card again, and the card says the head it moved from, the head it is at, and the commits it gained or lost since the user's send. When crew cannot tell, it asks again and says why it could not tell.
- **A refusal no longer drops the yes.** When sluice refuses a ticked bolt and the card closes, the close keeps the user's send for that bolt and says so: it lands once its team's fix has only taken main in and sluice has proven it.
- **Ops can read a standing send with no card open.** `crew card read land/<kit>` prints the bolts an earlier send still lands, and the command that lands them, even when no landings card of the kit is open. Before, it refused with no card held.
- **The briefs say it.** Main-level ops's brief says a send stands for a bolt that only took main in. The conductor's brief says a take-main fix on a ticked bolt leads to its landing, not a new card.
- README, the crew skill and `crew`'s usage say what `crew card read land/<kit>` now prints (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a ticked bolt's approval stands through a head move that leaves its own work unchanged; a refused bolt's send is kept when its card closes; a bolt whose own work changed is asked again with what changed.
- `main-level`: ops lands a bolt on a send that still stands, read from `crew card read land/<kit>` with or without an open card.

## Impact

- `plugin/lib/plan.py`: the landings card's decisions (`rows_unsent`, `sent_left`, `landings_step`), its raise (`raise_landings`), the read of what an earlier send lands (`landings_earlier`, `card_read`), and a new read of a bolt's own work between two heads, made where the kit's forecasts are made.
- `plugin/roles/main-ops.md`, `plugin/roles/conductor.md`: what a standing send means for ops and for a take-main fix.
- README, `plugin/skills/crew/SKILL.md`, `plugin/bin/crew`'s usage header.
- Tests in all three tiers: decisions in `tests/py/test_landings.py`, the git behaviour the work read rests on in `tests/contract/test_git.py`, and the journey in `tests/t-journey-land.sh`; `tests/t-briefs.sh` for the briefs' words.
- No rule is edited: `plan.19`'s details already record this reading of `plan.16`. Nothing the agents' bands draw changes (`code.8`). Nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/plan.py
plugin/roles/main-ops.md
plugin/roles/conductor.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
README.md
tests/**
```
