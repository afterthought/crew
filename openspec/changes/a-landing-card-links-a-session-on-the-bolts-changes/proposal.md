# Proposal

## Why

The user, on the-box-works-in-wldn-prod's landing card: "add plannotator review for bolt branch use tailnet" (signal 2026-10-19-swc-2-conductor-74b9f52d/01). A landing card today names what lands but gives the user nothing to read before they approve it, and `crew card session land/<bolt>` refuses with "a landing card has nothing to read". Record 0031, as amended and accepted on 2026-10-19, rules that a landing's card links one reading of the bolt; that bolt's landing waits for it.

## What Changes

- When crew raises a bolt's landing card, in its conductor's name on the team's host, it first starts one plannotator session there on what the bolt brings to main: a short page naming the bolt, its head and what lands, then each unit's change as the bolt holds it archived, whole, then the bolt's diff against main. The session is reached over the tailnet, as a batch's session is.
- The card carries the session's link in its own words first and among its links, and says the reading lands nothing: approving the card is still the word to land (`plan.16`). A session that could not open is said on the card, which is raised all the same.
- When a merge moves the bolt's head, the session on the old head ends and one on the new head starts, and the card, changed in place, carries the new link.
- `crew card session land/<bolt>` prints the running session's link, or starts the session anew when it no longer runs, and then changes the open card in place to carry the new link while it waits on the user. It runs on the team's host and is refused elsewhere, naming that host.
- What the user sends from the session reaches the conductor through `crew card wait land/<bolt>`: annotations are notes on the landing card, a defect among them held for a fix as any note is; an approval sent from the session is said to land nothing.
- crew ends the session when it closes the card: when the bolt lands, when a fix holds it, and on a rail read once the card is closed or its row gone.
- The conductor's brief says the card links the reading and how its notes reach the conductor.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `card-sessions`: a landing's card has a session, on the bolt's changes against main, started on the team's host; it is started with the card, restarted with a new head, and its decision reaches the conductor as notes and never as the word to land.
- `rail-cards`: a landing's card carries its session's link, offered beside its approval.

## Impact

- `plugin/lib/plan.py`: the landing's reading written and opened (`reading_open`, `session_refusal`, `card_session`, `card_wait`, `READING`, `reading_of`), and `raise_land`'s facts shared with `crew card session`.
- `plugin/lib/cards.py`: `landing_card` takes the session's link.
- `plugin/roles/conductor.md`, `plugin/skills/crew/SKILL.md`, `plugin/bin/crew`'s usage, `README.md`: the landing's session described.
- Tests: `tests/py/test_cards.py`, `tests/py/test_landing.py`, `tests/t-journey-land.sh`, `tests/t-briefs.sh`.
- Nothing crew models changes shape: no new object, stage or field reaches the agents' views (`code.8`).

## Touches

```
plugin/lib/plan.py
plugin/lib/cards.py
plugin/roles/conductor.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
README.md
tests/py/test_cards.py
tests/py/test_landing.py
tests/t-journey-land.sh
tests/t-briefs.sh
tests/moon.yml
```
