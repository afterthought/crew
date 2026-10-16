# crew raises a bolt's landing card

## Why

Record 0031 makes a bolt's landing card crew's own: raised in its conductor's name once the bolt reads proven, changed in place when a fix moves its head, withdrawn when a note names a defect, and closed when main-level ops lands it. No landing card has posted since 2026-10-11: the conductor builds it by hand with a flag Pending You refuses on an approval, under a key that carries the head, so each head is a new card.

**Waits on the record of who keeps which folders** (the recovery session's next design talk): what a landing closes on, and so the words its card closes with, depends on it. This change is built once that record is accepted, and its close's words are the record's.

## What Changes

- The merge's end and the rail's read raise the landing card, keyed `land/<bolt>`, once every unit and chore of the bolt has merged, every unit's latest change has been in a batch and sluice's verdict at its head is green; whichever reads it first posts, and the other finds the card by its key.
- The card links sluice's pull request when the submission at the head has one.
- A fix that moves the head changes the card in place; `crew fix` started on a defect note withdraws it, "held for a fix: …", and a new card follows it once the bolt reads proven again.
- `crew bolt land` closes the card with the landing's outcome, in the words the record of who keeps which folders settles.
- The conductor's brief says crew raises the landing card, how the conductor adopts it, and what it does on the answer: the tell to main-level ops on a yes, a fix on a defect note; it posts and closes no landing card.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: the landing card raised by crew once the bolt reads proven, keyed by the bolt alone, with sluice's pull request, withdrawn on a defect and raised again.

## Impact

- Follows `crew-builds-every-card-from-its-facts`, whose landing builder, `follows_of` and act it calls, and `the-rail-shows-and-sweeps-every-card`, whose read posts a row's card that has none through the raise this change gives the landing; and waits on the record of who keeps which folders.

## Touches

```
plugin/lib/plan.py
plugin/hooks/cards
tests/py/test_landing.py
tests/py/test_rail.py
tests/t-journey-land.sh
plugin/roles/conductor.md
tests/t-briefs.sh
tests/moon.yml
```

`plan.py` changes the landing's row in `rail_rows` (keyed `land/<bolt>`, there once the bolt reads proven), `unit_wait` and `record_end` (the merge's end), `fix_cmd`, `bolt_land`, the landing's pattern in `CARD_KEYS` and the conductor's branch of `card_refusal`, and gains `landing_facts` and `raise_land`. The card hook changes only its `KEYS` line for a landing's key. `plugin/roles/conductor.md` changes *Cards*' landing paragraph and its answer's, step 5 of *The building loop* and *Talking to the user*'s line on the landing card, and `tests/t-briefs.sh` their words; `tests/moon.yml` is regenerated.
