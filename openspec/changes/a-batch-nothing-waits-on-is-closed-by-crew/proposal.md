# A batch nothing waits on is closed by crew

## Why

On 2026-10-20 crew on wldn's box posted 23 batch cards in wldn-planner's name, for batches 1 to 15, 36, 37 and 39 to 41, most of them for bolts that had landed days before; the user had asked for four (signal 2026-10-20-swancloud-planner-1703a4ae/02). crew reads a batch as a rail row until the run record holds a close of its card, so a batch answered in the pane, or before crew raised its own cards, never closes, and the rail's sweep posts a card for it however long ago its work landed. The planner cannot withdraw them either: a `batch/<n>` card is crew's (`briefs.11`). `briefs.12` already rules such a card out and leaves the fix to this unit.

## What Changes

- A batch waits on nothing once each of its units has landed, been dropped from the plan since the batch was made, or been held by a later batch, whose card then carries that unit to the user. crew reads such a batch closed from the run record alone, at every rail read, the board's among them, so it is no row and its card is never posted.
- A batch with even one unit that has not landed, was not dropped and that no later batch holds stays a row, exactly as today, until the user answers its card.
- The rail's sweep, on the partition's main-level host, records crew's close of each such batch once, in the planner's name, with words that say why: which units have landed, which were dropped, and which later batch holds the others.
- A card still open under such a batch's key is withdrawn by the sweep with the same words, so the 23 open in wldn close themselves on the next read after this lands.
- crew does not raise a card for such a batch when the planner's `crew review --wait` returns, and the rail's sweep text says what it closed.
- The landing's rule is unchanged: crew's close is not the user's answer, and a bolt still lands only once each unit's latest change has been in a batch the user answered.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `review-batches`: a batch that waits on nothing is closed by crew, with why, and no card is posted for it.
- `rail-cards`: a batch's row, the new-style one and each older `batch/<n>-<k>` one, lasts until its card closes or the batch waits on nothing.

## Impact

- `plugin/lib/plan.py`: the batch reading (a new decision beside `batch_closed`), `record_reading`, `rail_rows`, `row_gone`, `sweep_judged`, `sweep_cards`, `batch_facts` and the sweep's lines in `rail_text`.
- `tests/py/test_batches.py`, `tests/py/test_rail.py`: the logic tier's cases.
- `README.md` and the planner's brief, `plugin/roles/planner.md`: where they say a batch's row and card last until the user answers, and the run record's acts (`docs.2`).
- No change to what the board or the agents' bands draw: a batch row is gone sooner, in the shape it has now (`code.8`).

## Touches

```
README.md
plugin/lib/plan.py
plugin/roles/planner.md
tests/py/test_batches.py
tests/py/test_rail.py
```
