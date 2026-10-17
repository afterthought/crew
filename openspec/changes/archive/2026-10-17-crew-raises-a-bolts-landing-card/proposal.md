# crew raises a bolt's landing card

## Why

Record 0031 makes a bolt's landing card crew's own: raised in its conductor's name once the bolt reads proven, changed in place when a fix moves its head, withdrawn when a note names a defect, and closed when main-level ops lands it. No landing card has posted since 2026-10-11: the conductor builds it by hand with a flag Pending You refuses on an approval, under a key that carries the head, so each head is a new card. Record 0032 settles the close's words, which `crew bolt land` already closes the card with (`no-worktree-holds-main-or-a-bolt-branch`, 4.2).

## What Changes

- The merge's end and the rail's read raise the landing card, keyed `land/<bolt>`, once every unit and chore of the bolt has merged, every unit's latest change has been in a batch, sluice's verdict at its head is green and no fix is in flight on it; whichever reads it first posts, and the other finds the card by its key.
- The card links sluice's pull request when the submission at the head has one.
- A fix that moves the head changes the card in place; `crew fix` started on a defect note withdraws it, "held for a fix: …", and a new card follows it once the bolt reads proven again.
- `crew bolt land` closes the card with the landing's outcome, in record 0032's words.
- The conductor's brief says crew raises the landing card, how the conductor adopts it, and what it does on the answer: the tell to main-level ops on a yes, a fix on a defect note; it posts and closes no landing card, and a write that ends its bolt no longer tells it to close one.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: the landing card raised by crew once the bolt reads proven, keyed by the bolt alone, with sluice's pull request, withdrawn on a defect and raised again.

## Impact

- Follows `crew-builds-every-card-from-its-facts`, whose landing builder, `follows_of` and act it calls, and `the-rail-shows-and-sweeps-every-card`, whose read posts a row's card that has none through the raise this change gives the landing; and `no-worktree-holds-main-or-a-bolt-branch`, whose 4.2 closes the card at `crew bolt land` in record 0032's words.

## Touches

```
plugin/lib/plan.py
plugin/hooks/cards
tests/py/test_landing.py
tests/py/test_rail.py
tests/py/test_cards.py
tests/py/test_review.py
tests/t-journey-land.sh
tests/t-cards.sh
tests/t-journey-review.sh
plugin/roles/conductor.md
plugin/lib/crew.py
README.md
tests/t-briefs.sh
tests/moon.yml
```

`plan.py` keys the landing's row in `rail_rows` by the bolt, `land/<bolt>`, there as before once every unit has merged and saying why it can't land yet, a fix in flight among the reasons; raises the card at the merge's end in `stage_wait` and withdraws it at a fix's start in `fix_run`; keys the landing's pattern in `CARD_KEYS` and the conductor's branch of `card_refusal` by the bolt, an older head's key still read; drops the tell to close a landing's card from `notices`; and gains `landing_act`, `landing_unready`, `landing_facts`, `pull_of`, `raise_land`, `landing_held` and `landing_after_merge`. `bolt_land`'s close is `no-worktree-holds-main-or-a-bolt-branch`'s. The card hook changes only its `KEYS` line for a landing's key. `plugin/roles/conductor.md` changes *Cards*' landing paragraph and its answer's, step 5 of *The building loop*, a fix's and the conflict's fix's lines and *Talking to the user*'s line on the landing card; the card discipline `crew.py` gives the planner and the conductor loses its sentence on a landing's key changing with its head; README says crew raises, changes, withdraws and closes the landing card; and `tests/t-briefs.sh` pins the words; `t-cards` shows the card commands' wiring on a second team's landing key and `t-journey-review` the refusal's words; `tests/moon.yml` is regenerated.
