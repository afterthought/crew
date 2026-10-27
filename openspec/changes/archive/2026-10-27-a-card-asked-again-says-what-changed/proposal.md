# A card asked again says what changed

## Why

The user feels they handle the same cards over and over: from 2026-10-22 to 24 crew posted 263 cards under 188 keys, 33 of them more than once, and a card that came back after the user had answered it looked exactly like the one they had already answered (signal 2026-10-24-swancloud-design-6ee99e08/01: "it sometimes seems like i'm handling the same cards multiple times"). Record 0031, as amended 2026-10-24 and accepted on the user's card, settles what changes: a card that follows one the user answered says first that they answered it, when and with what, and what has changed since; and a follow-on that cannot say what changed is not posted, the earlier answer standing.

## What Changes

- Every card crew posts that follows a card the user answered opens its summary with one paragraph, before anything else the card says: "You answered the card before this one, posted 2026-10-23 13:10 UTC, by 14:02 UTC: approved. Since then: revised at 4be21c0, …". The same paragraph opens the card's details.
- crew keeps what the user answered. When crew closes a card the user answered, the run record's close of it holds the answer in crew's own words, made from names alone (approved, declined, the bolts ticked and left, the option picked, done, skipped, "with a note"), never the user's typed words (`record.3`). The follow-on reads it from there, with the times the run record holds for the earlier card's post and close.
- Each raise that posts a follow-on hands crew what changed since the answer, in sentences: a record's new commit; a proposal's rewrite, read against the proposal it replaces (units added, units no longer in it, intents rewritten, its case rewritten); a deploy's newer head; a step's place after the deploy or the step before it; the landings card's own account of what the user's send landed, held and left, and of bolts proven or moved since.
- A follow-on with nothing to say changed is not posted. crew records it as a post it refused, in its own words naming the earlier card and that its answer stands, so the rail's card line shows it, and the rail's sweep stops raising that row's card until an event raises it again with something new.
- A bolt the user left unticked on the landings card is still shown again on the card that follows, as they want (record 0031 as amended 2026-10-24, *What stays*): that it was left on their send, and still waits, is what the follow-on says changed.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a card the user answered is followed by a new version that says first what they answered, when, and what changed since; a follow-on with nothing changed is not posted and the earlier answer stands; the close of an answered card records the answer.

## Impact

- `plugin/lib/cards.py`: the answer in crew's words, the opening paragraph, what a proposal's rewrite and a deploy's newer head changed, and the check that refuses a follow-on with nothing changed, all decisions on plain facts (`code.7`).
- `plugin/lib/plan.py`: `card_posted` puts the opening on every follow-on of an answered card or refuses it; `card_closed`, `row_card_change` and `followed_closed` record the answer; `row_card_change`, `raise_record`, `raise_proposal_at`, `raise_landings` and the sweep hand or honour what changed.
- `plugin/lib/ops.py`: the deploy's and the step's raises hand what changed.
- `plugin/lib/record.py`: the run record's entries may carry `Answer`.
- The board and the agents' bands draw nothing new: a withheld follow-on reaches them as a refused post's words, which they already show (`code.8`).
- Beside this unit, in the same bolt: `a-landings-approval-stands-through-taking-main-in` decides when a landing asks again at all; this change decides what any card asked again says.

## Touches

```
plugin/lib/cards.py
plugin/lib/plan.py
plugin/lib/ops.py
plugin/lib/record.py
tests/py/**
```
