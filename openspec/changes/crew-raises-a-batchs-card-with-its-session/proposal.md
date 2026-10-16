# crew raises a batch's card with its session

## Why

Record 0031 makes a batch's card crew's own: raised in the planner's name when the reviewer delivers the batch's summary, with one plannotator session behind it, and closed on the user's tap or the session's send. Today the planner starts the session and posts the card by hand, and a card nobody closed has left sessions running: eight were found on 2026-10-14. What the user holds this card to is the session: "it stays running, it closes when it's supposed to once we're done, it's accessible" (the card trials, 2026-10-15).

## What Changes

- When the reviewer delivers a batch's summary and the planner's `crew review --wait` returns, crew starts the batch's one reading session and raises its one card, keyed `batch/<n>`, in the planner's name; the planner writes nothing of it.
- crew starts a plannotator session only when it raises a batch's card or a proposal's of more than fifteen new units, and puts its link first in the card's words and among its links; a card whose session could not start is raised all the same, saying so.
- `crew card wait batch/<n>` returns on the tap or the session's send, prints the card's note and every annotation word for word, closes the card with the outcome and ends the session.
- The session ends when crew closes or withdraws its card; `crew card session <key>` prints a running session's link again and refuses any other key.
- The planner's brief says crew raises the batch's card and session, how the planner adopts the card, and that it reads the notes with `crew card wait`; it starts no session and posts and closes no batch card.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `review-batches`: a batch's card raised by crew when the reviewer delivers its summary, closed on the tap or the session's send.
- `card-sessions`: a session for a batch and a long proposal alone, started by crew with the card, ended by crew's close.
- `rail-cards`: what a card carries, a batch's link among it; the batch's card a notice crew raises.

## Impact

- Follows `crew-builds-every-card-from-its-facts`, whose builder and act it calls and whose act it gives the session's start and end. Built beside `crew-raises-a-proposals-card`, `crew-raises-the-deploy-and-step-cards`, `crew-record-raises-a-records-card` and `the-rail-shows-and-sweeps-every-card`, none of which changes a function this one changes.
- The planner's *Cards* section opens with one paragraph on its proposal and batch rows, whose batch sentences this change rewrites and whose proposal sentences `crew-raises-a-proposals-card` does; whichever lands second rebases on the other.

## Touches

```
plugin/lib/plan.py
tests/py/test_batches.py
tests/py/test_cards.py
tests/t-cards.sh
plugin/roles/planner.md
tests/t-briefs.sh
tests/moon.yml
```

`plan.py` changes `review_wait`, the act's `row_card_post` and `row_card_close` (a session started before a batch's or a long proposal's card is built, and ended when crew closes or withdraws it), `card_session`, `session_refusal`, `card_of`, `card_wait`, `waited`, `end_session` and `batch_folder_write`, and gains `batch_facts` and `raise_batch`. `plugin/roles/planner.md` changes *Batches*, steps 2 and 3 and the old batch card's paragraph, and the batch's sentences of *Cards*' opening paragraph. `tests/py/test_cards.py` gains `TestSessions`; `tests/t-cards.sh` gains the batch's and the session's journeys and `tests/t-briefs.sh` the planner's words; `tests/moon.yml` is regenerated.
