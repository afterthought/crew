# A batch's card left on another host is raised again

## Why

A batch's card belongs to the Pending You sign-in of the host it was posted from. Batches 13, 14 and 15 were posted from mac-studio, and the partition's main level has since moved to deneb. On deneb nobody can reach those cards: the planner's wait holds no card of them there, crew records them neither lost nor answered, and the rail never raises them again, because the run record still shows each one open. So the user's approval on those cards closed nothing, and the bolts of crw-4, crw-5 and swc-3 waiting on them were never offered for landing (signal 2026-10-22-swancloud-planner-3b6cb27a/01). The same wait also drops an answer the user did give where crew can see it: when the user sends a batch's reading session and no card of the batch is held on the main level's host, the wait ends the session and records nothing, so the batch still holds every landing it holds (`briefs.12`).

## What Changes

- At the rail's next read on the main level's host, a batch whose card the planner can't reach there is raised again: its card was posted from another host, or it was recorded lost to the planner there, and no newer card under its key was posted since. crew posts the batch's card again on the main level's host under `batch/<n>`, its summary opening with the words that say an older copy is dead and to dismiss it in the app, and the rail takes the new card as the row's. A card on another host that this host's rail can't reach is never asked after or closed from here; it is only replaced.
- When the user sends a batch's reading session, crew records the batch read whether or not a card of it is held on the main level's host: with no card to close, or one that is lost or whose close Pending You refuses, the wait records crew's close of the batch in the planner's name with what was read ("Read; no notes", "Read; 2 notes sent to their teams"), so the batch stops holding any bolt's landing.
- A batch closed so is closed everywhere crew reads batches: the rail drops its row, its landing rows stop naming it, and no card is raised for it again until a newer card is posted under its key.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a batch's card posted from a host other than the main level's, or lost to the planner there, is posted again on the main level's host at the rail's next read, saying the older copy is dead.
- `review-batches`: a batch whose reading session the user sends is recorded read with or without a card held on the main level's host, and that record answers the batch for its bolts' landing.

## Impact

- `plugin/lib/cards.py`: a decision reading, from the run record, the planner's copy of a key's card that the main level's host can't reach.
- `plugin/lib/plan.py`: `sweep_judged` and `sweep_cards` raise such a batch's card again; `raise_batch` posts it with the dead-copy summary; `batch_wait` records the batch read when no card was closed; `batch_closed` reads that record.
- README, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage header: the rail's sweep and `crew card wait batch/<n>` (`docs.2`).
- Tests: `tests/py/test_rail.py`, `tests/py/test_batches.py`, `tests/py/test_cards.py`, `tests/t-cards.sh`.

## Touches

```
plugin/lib/cards.py
plugin/lib/plan.py
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/py/test_rail.py
tests/py/test_batches.py
tests/py/test_cards.py
tests/t-cards.sh
```
