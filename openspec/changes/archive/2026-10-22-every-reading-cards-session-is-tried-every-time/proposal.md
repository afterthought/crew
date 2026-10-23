# Proposal

## Why

A landing card's reading is now tried more than once. The raise tries it twice before giving up, and the conductor's wait starts it when none runs. A batch card's reading, and a long proposal card's, are still tried once. If that one start fails, the card stands without its reading until someone happens to run `crew card session` by hand. Nothing tells the planner that this is its job, and nothing puts the link on the card afterwards: only a landing card is changed to carry a link started after its raise. (Signal 2026-10-20-swancloud-planner-13d15a99/01.)

`briefs.9` says every card that asks the user to read something it cannot hold whole carries the link to its reading. A batch card or a long proposal's card without its link breaks that, and one failed start should not be enough to cause it.

The reason a start failed is now kept for every kind of card, as `Unread` on the card's post or change (`a-landing-card-is-raised-with-its-session-every-time` made that general). A try made later, which posts and changes no card, has nowhere to keep its reason yet.

## What Changes

- **The raise tries twice.** When a batch card's or a long proposal card's reading will not open, crew tries once more before raising the card without it. Every point that raises or changes these cards gets this: `crew review --wait`, a proposal's accept, rewrite and agree, and the rail's sweep. Only when both starts fail is the card raised without its reading, with the second start's reason on the card, in the command's output and in the run record.
- **The card names who starts it.** A batch card or a long proposal's card raised without its reading says that crew tries again when the rail is read, and that the planner can start it with `crew card session <key>`, after which the card carries its link. The command is written as the planner's act, not a step for the user (`briefs.13`).
- **Starting it changes the card.** `crew card session batch/<n>` and `crew card session proposal/<n>`, when they start the reading anew, change the open card in place to carry the new link while it waits on the user, as `crew card session land/<bolt>` already does. A card the user has answered is left as it is.
- **The batch's wait starts a missing reading.** `crew card wait batch/<n>`, when the planner's card is open and no reading runs, starts the reading as `crew card session` does and then waits on the card and the reading together. When the reading still will not open, the wait says why once, naming `crew card session batch/<n>`, and goes on waiting on the card alone, since the user can still send the card back with a tap.
- **The rail's read tries again.** When the rail's sweep finds a batch card or a long proposal's card open on this host, waiting on the user, whose run record shows it stands without its reading, it tries the reading as `crew card session` does and changes the card to carry the link. A try that fails is left for a later read, ten minutes on, as a refused post already is. The rail lists what the sweep did with each.
- **Every later try keeps its reason.** A try of a batch's or a proposal's reading that is not part of a post or a change (by `crew card session`, the batch's wait or the rail's sweep) records one `card.reading` entry in the run record. It is either done, or refused with crew's own message.
- The planner's brief, the crew skill, the command's usage (`plugin/bin/crew` and `plan.py`'s) and README say all of this, together (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `card-sessions`: the requirement that a card whose session could not start is raised all the same now covers the batch's and the long proposal's second try and their words naming `crew card session`. New requirements: starting a batch's or a proposal's reading changes its card; the batch's wait starts a missing reading; the rail's read tries a reading a card stands without; and a later try is recorded.

## Impact

- `plugin/lib/plan.py`: `card_built` and `unopened`; `card_session` for `batch/` and `proposal/` keys, sharing `land_session`'s relink; `raise_batch` and `proposal_act` gaining a relink note; `batch_wait`; `sweep_judged` and `sweep_cards`, with `SweepActs`; the usage text.
- `plugin/lib/record.py`: the comment listing the card acts gains `card.reading`.
- `plugin/roles/planner.md`, `plugin/skills/crew/SKILL.md`, README's card-session paragraph and its list of acts, and `plugin/bin/crew`'s usage.
- Tests: `tests/py/test_cards.py`, `tests/py/test_batches.py`, `tests/py/test_proposal_card.py`, `tests/py/test_rail.py`, `tests/t-journey-review.sh`, and `tests/t-briefs.sh` if the brief's checked words move.
- No change to the landing card, which keeps its own two tries and wait, to what a card asks, or to who answers it.

## Touches

```
plugin/bin/crew
plugin/lib/plan.py
plugin/lib/record.py
plugin/roles/planner.md
plugin/skills/crew/SKILL.md
README.md
tests/py/test_cards.py
tests/py/test_batches.py
tests/py/test_proposal_card.py
tests/py/test_rail.py
tests/t-journey-review.sh
tests/t-briefs.sh
tests/t-cards.sh
tests/moon.yml
```
