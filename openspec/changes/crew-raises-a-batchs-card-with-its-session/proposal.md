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
plugin/bin/crew
plugin/roles/planner.md
plugin/skills/crew/SKILL.md
README.md
tests/py/test_batches.py
tests/py/test_cards.py
tests/py/test_review.py
tests/t-cards.sh
tests/t-journey-review.sh
tests/t-briefs.sh
tests/moon.yml
```

`plan.py` changes `review_wait`, `batch_due_said` (the planner told the wait raises the card), the act's `CardActs`, `row_card_post`, `row_card_change` and `row_card_close` (a session started before a batch's or a long proposal's card is built, and ended when crew closes or withdraws it), `card_session`, `session_refusal`, `card_result` (plannotator's count of annotations), `card_wait`, `end_session` and `batch_folder_write`, and gains `summary_paragraph`, `subject`, `batch_subjects`, `batch_facts`, `raise_batch`, `proposal_reads`, `session_open`, `reading_open`, `batch_wait`, `batch_waited`, `read_outcome`, `reading_of`, `unopened`, `card_built` and `card_closed`. `plugin/roles/planner.md` changes *Batches*, steps 1 to 3 and the old batch card's paragraph, and the batch's sentences of *Cards*' opening paragraph; README, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage header change `crew review --wait`'s and `crew card session` and `wait`'s words (`docs.2`). `tests/py/test_cards.py` gains cases in `TestSessions`, `tests/py/test_batches.py` `TestBatchFacts`, and `tests/py/test_review.py` the planner's new words; `tests/t-cards.sh` gains the batch's and the session's journeys, `tests/t-journey-review.sh` takes the batch's card from `crew review --wait` and a long proposal's session, and `tests/t-briefs.sh` the planner's words; `tests/moon.yml` is regenerated.
