# Proposal

## Why

When the rail is read, it retries a batch card's reading, and a long proposal card's, if the card is still waiting on the user without one. It tries at most once every ten minutes per card and changes the card to carry the new link. It does not do this for a landing card. A landing card raised without its reading stays that way until its conductor runs `crew card session land/<bolt>` or `crew card wait land/<bolt>`, and nothing reminds the conductor to. `briefs.9` says every reading card carries its session's link, landing cards included. The card-sessions spec has a landing's session started again whenever its card is posted again. (Signal 2026-10-22-swancloud-planner-968cd584/01. The change that built the batch and proposal retry, `every-reading-cards-session-is-tried-every-time`, left the landing card out and named the gap.)

## What Changes

- **The rail's read tries a landing card's reading too.** The rail's sweep finds each landing card posted on this host that waits on the user and that the run record shows standing without its reading. When the card's last post, change or try of its reading was ten minutes ago or more, the sweep tries the reading the way `crew card session land/<bolt>` does: on the team's host, with the bolt's landing read afresh. It then changes the card to carry the link. A try that fails is left for a later read, ten minutes on. The rail lists what the sweep did with each card, as it already does for batch and proposal cards.
- **A later try of a landing's reading is recorded.** `crew card session land/<bolt>`, the landing's wait and the sweep record one `card.reading` entry for each try that starts a reading or is refused, in the conductor's name, as a batch's or a proposal's try already does. This gives the sweep its ten minutes to count from, and keeps why a try failed.
- **A running reading still reaches its card.** `crew card session land/<bolt>` changes the card to carry the link when the card stands without its reading, even when the session is already running, as a batch's and a proposal's already do. Without this, a try whose session started but whose card change failed would never put the link on the card.
- **A landing card raised without its reading says the rail tries again**, as a batch card's and a proposal card's already say, beside the conductor's own command.
- README, the crew skill, the command's usage and the conductor's brief say this together (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `card-sessions`: the rail's read tries a landing card's missing reading; a landing's later try is recorded; `crew card session land/<bolt>` changes a card standing without its reading even when its session runs; and a landing card raised without its reading says the rail tries again.

## Impact

- `plugin/lib/plan.py`: `sweep_judged` (landing keys among the cards to try), `SweepActs.reading_again` (a landing key goes the landing's way), `land_session` (records each try, takes a `say` so the rail prints no link, and relinks a card standing without its reading), `unopened` (the landing's words), and the usage text.
- README's card-session paragraph and list of acts, the crew skill's rows for `crew rail` and `crew card session`, `plugin/bin/crew`'s usage, and `plugin/roles/conductor.md`.
- Tests: `tests/py/test_rail.py`, `tests/py/test_cards.py`, and `tests/t-briefs.sh` for the conductor's words.
- No change to how a batch's or a proposal's reading is tried, to the landing card's raise or wait, or to who answers a card.

## Touches

```
plugin/lib/plan.py
plugin/bin/crew
plugin/roles/conductor.md
plugin/skills/crew/SKILL.md
README.md
tests/py/test_rail.py
tests/py/test_cards.py
tests/t-briefs.sh
tests/t-journey-land.sh
```
