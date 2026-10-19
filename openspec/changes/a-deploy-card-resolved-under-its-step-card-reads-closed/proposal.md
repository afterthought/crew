# Proposal

## Why

On 2026-10-19 mac-studio's deploy card stopped reaching the user. The user approved it, and when the deploy finished crew raised the after-deploy step's card following it. Pending You treats a card that follows an answered one as picking that card up, and marks the answered card `resolved`. crew does not know that status. It went on holding the deploy card as open. The deploy's end tried to close it and Pending You refused, "This request is already closed", and the rail's sweep tried 28 more times over the next five hours. The next offer to mac-studio, d35fbf2, went in as a change to that resolved card, which the user could not see or answer ("This was already answered"). deneb's offer of the same commit got a new card and was deployed. The card was recorded closed by hand six hours after the deploy ended, and only then could mac-studio be offered again (signal 2026-10-19-swancloud-ops-5b7775dd/01).

The fix that went in earlier that day (5eebfa74) reads a card as ended when Pending You reports it `closed`, `cancelled` or `expired`. Pending You never reports `closed`. It reports `resolved`, and that is the status this card had.

## What Changes

- crew reads Pending You's `resolved` as ended, alongside `cancelled` and `expired`. It drops `closed`, which Pending You never reports. A resolved card is recorded closed, and a cancelled or expired one withdrawn. When crew next goes to change or close such a card, it records it so and sends nothing more.
- When crew posts a card that follows one of its own cards still recorded open, it reads that card again straight after the post. If Pending You has ended it, crew records it closed then. So a deploy card picked up by its step card reads closed from that moment.
- At the deploy's end crew then holds no open deploy card, so it closes nothing and Pending You refuses nothing. The rail shows the environment's row with no open card. The next offer to that environment gets a new card, following the resolved one, that the user can answer.
- When crew withdraws a question whose asker has ended, it reads the card's status the same way. A question Pending You already ended is recorded closed and nothing more is sent.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: crew reads a card that Pending You ended, whether picked up by the card that follows it or closed by another hand, as closed. It changes and closes it no more, and posts the card's next version as a new card.

## Impact

- `plugin/lib/cards.py`: the statuses read as ended, the state each is recorded as, and the decision of which open card a new post follows.
- `plugin/lib/plan.py`: `card_posted` reads the card it followed; `row_card_change`, `card_closed` and `question_close` record an ended card's close from that decision.
- `tests/py/test_cards.py`, `tests/py/test_card_commands.py`, `tests/py/test_rail.py`: logic-tier cases, including mac-studio's sequence from 2026-10-19.
- `tests/stubs/pendingyou`: picks up the answered card a post follows, and refuses to cancel a card already ended, as Pending You does.
- `openspec/specs/rail-cards/spec.md`, through this change's delta.
- No change to the board's views, the mod, the run record's shape or any command's arguments.

## Touches

```
plugin/lib/cards.py
plugin/lib/plan.py
tests/py/test_cards.py
tests/py/test_card_commands.py
tests/py/test_rail.py
tests/stubs/pendingyou
```
