# A batch card's notes are its note and its sessions

## Why

The first batch reached the user as two cards, each asking them to pick which units needed notes, and they could not send a card back without picking one even when nothing needed notes. The user's words, on that batch: "Splitting a batch into two cards, I thought, goes against what we're trying to do here. I don't like having to choose which ones I want to leave notes on because it's a bad UX", "I have no feedback on any of these three but I'm only allowed to submit if I check one", and "Leave notes where? It's fucking stupid. I do have feedback but it's awkward to leave it this way" (signals 2026-10-11-swancloud-planner-ab370c3e/01 and 7c9208ad/01). Each unit's summary came as a code block that scrolled sideways on the phone: "attaching the summary as code in the markdown code viewer forces horizontal scrolling, which is not readable" (ab370c3e/02).

The design agent ruled what a batch card is (`briefs.13` as amended 2026-10-11; record 0005, "A batch is one card that asks nothing, and says where notes go"): one card for the whole batch, however many units, never split by five, naming every unit; it asks nothing, since every Pending You question is required, and closes on one tap; a unit's notes are the annotations the user sends from that unit's reading session and the card's own note, and the card says so in plain words; its summary is prose the phone wraps, never a code block. No card of crew's asks a required question in words.

## What Changes

- **A batch is one card.** However many units a batch holds, the planner posts one card for it, keyed `batch/<n>`, naming every unit. The rail shows one row per batch. A batch is never split by five.
- **The card asks nothing.** It is a Pending You notice the user sends back with one tap: no choice of units, no question in words, no approval. Units go on building whatever the user does with it, as they already do.
- **Notes come from where the user writes them.** The annotations the user sends from a unit's reading session go to that unit's team at once, word for word. The card's own note, written beside the tap, goes word for word to the team of each unit it speaks of; a note that names no unit goes to every unit's team, so no words the user wrote reach nobody. Approving a unit's session means that unit is fine, and leaves the card open.
- **The card says so in plain words.** Its first lines tell the user there is nothing to answer, how to leave notes on a unit (in its reading session, or in the card's note naming the unit), and to tap once when they are done.
- **The summary reads on the phone.** Each unit's summary is in the card's words as prose and plain lists that wrap, never a code block or an attachment. The reviewer writes its summary that way, with the files a change touches named in words rather than as paths.
- **crew refuses a batch card in another form**, as it does for a proposal's, a verify report's and a landing's: a choice, a pick-several, an approval, a question in words, steps, an attachment, a code block in its words, or a card that leaves out one of the batch's units is refused before it reaches Pending You, naming the form to use. **No card of crew's may ask a question in words**, whatever its row.
- A batch card posted before this lands, under the old `batch/<n>-<k>` keys, is read and closed as it was.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `review-batches`: a batch is one card that asks nothing; a unit's notes are its session's annotations and the card's own note.
- `rail-cards`: a batch's row and key are one per batch, `batch/<n>`; a batch's card has its own form, which crew enforces; no crew card asks a question in words.
- `card-sessions`: a batch card's sessions are started, waited on and ended by `batch/<n>` and the unit.

## Impact

- `plugin/lib/plan.py`: a batch's one rail row and key, the planner's key check, the card commands' reading of a batch's units, and the old keys read until their cards close.
- `plugin/hooks/cards`: the batch card's form, the batch's units named on it, and no question in words on any card.
- `plugin/roles/planner.md` *Batches* and *Cards*, `plugin/roles/reviewer.md` *The summary*, `plugin/lib/crew.py` `cards_how`, `README.md`.
- `tests/t-batch-cards.sh`, `tests/t-batches.sh`, `tests/t-cards.sh`, `tests/t-briefs.sh`.
- `openspec/changes/units-build-at-once-and-are-reviewed-in-batches/` has landed but is not archived, so `review-batches` and the batch parts of `rail-cards` and `card-sessions` are still deltas there; this change's deltas modify the requirements it adds and must be archived after it.
- Rules relied on: `briefs.13`, `briefs.9`, `briefs.11`, `briefs.12`, `roles.3`, `read.1`. Where `briefs.12` still says cards of at most five units, each asking which need notes and for the notes, this change follows `briefs.13` as amended, the later ruling. Clearing `briefs.13`'s not-built clause and `_open.md` is the design agent's after landing (`docs.7`).

## Touches

```
plugin/lib/plan.py
plugin/hooks/cards
plugin/lib/crew.py
plugin/roles/planner.md
plugin/roles/reviewer.md
README.md
tests/t-batch-cards.sh
tests/t-batches.sh
tests/t-cards.sh
tests/t-briefs.sh
```
