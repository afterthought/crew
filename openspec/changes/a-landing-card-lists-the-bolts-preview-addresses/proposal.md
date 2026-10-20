# Proposal

## Why

The user, answering the landing-card amendment on 2026-10-19: "while we are at it, i'd like each landing bolt to also use sluice preview to generate test urls that i can use over tailnet as well" (signal 2026-10-20-swancloud-design-2a0b2a51/01). A landing card today lets the user read the bolt (once `a-landing-card-links-a-session-on-the-bolts-changes` is built) but not try it running. sluice can now bring up a running copy of any revision a branch has landed and hand back its addresses (sluice record 0021). Record 0031 §3, amended and accepted on 2026-10-20, rules that a landing's card lists the addresses of a sluice preview of the bolt's head.

## What Changes

- When crew raises a bolt's landing card, in a kit whose sluice policy at the bolt's head declares `[preview]`, it first asks sluice, on the team's host, for a preview of that head (`sluice preview bolt/<bolt> <head>`). The ask is handed to a process of its own, since sluice may wait for room on the host and the stack takes time to come up; the card is raised once sluice has named the preview's addresses, without waiting for the stack.
- The card lists each address under the name the kit's policy gives it (`web`, `api`), beside the reading's link, says the preview is coming up and lands nothing, and that approving the card is still the word to land (`plan.16`).
- A preview that cannot be asked, or whose stack fails to come up, is said on the card, with sluice's reason, and holds nothing: the card is raised, or changed in place, saying so, and the landing goes on as before. A kit whose policy declares no `[preview]` gets a card exactly as today.
- When a merge moves the bolt's head while the card is open, crew releases the old head's preview, asks for one at the new head, and the card, changed in place as it already is for the head, lists the new addresses.
- When the card closes, landed, held for a fix or declined, crew releases the preview; the rail's sweep releases one whose card closed elsewhere or whose row is gone. crew releases only previews it asked for.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a landing's card lists the addresses of a sluice preview of the bolt's head when its kit declares one, follows the head with it, says a preview that failed, and releases it when the card closes.

## Impact

- `plugin/lib/kit.py`: whether a policy declares `[preview]`.
- `plugin/lib/plan.py`: the preview asked, followed and released around the landing card (`raise_land`, `row_card_close`, `card_sweep`, `CardActs`), and the handed ask, a new internal command `crew _preview`.
- `plugin/lib/cards.py`: `landing_card` takes the preview.
- `plugin/bin/crew`: `_preview` routed to Python.
- `plugin/roles/conductor.md`, `README.md`: what the landing card now carries.
- Tests: `tests/py/test_landing.py`, `tests/py/test_cards.py`, `tests/py/test_kit.py`, `tests/t-journey-land.sh`, the stub `tests/stubs/sluice`, `tests/t-briefs.sh`.
- Nothing crew models changes shape: no new object, stage or field reaches the agents' views (`code.8`).

## Touches

```
plugin/lib/kit.py
plugin/lib/plan.py
plugin/lib/cards.py
plugin/bin/crew
plugin/roles/conductor.md
README.md
tests/py/test_landing.py
tests/py/test_cards.py
tests/py/test_kit.py
tests/t-journey-land.sh
tests/t-briefs.sh
tests/stubs/sluice
tests/moon.yml
```
