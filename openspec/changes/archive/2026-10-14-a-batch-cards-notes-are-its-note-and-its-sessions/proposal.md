# A batch card's notes are its note and its session

## Why

The first batch reached the user as two cards, each asking them to pick which units needed notes, and they could not send a card back without picking one even when nothing needed notes. The user's words, on that batch: "Splitting a batch into two cards, I thought, goes against what we're trying to do here. I don't like having to choose which ones I want to leave notes on because it's a bad UX", "I have no feedback on any of these three but I'm only allowed to submit if I check one", and "Leave notes where? It's fucking stupid. I do have feedback but it's awkward to leave it this way" (signals 2026-10-11-swancloud-planner-ab370c3e/01 and 7c9208ad/01). Each unit's summary came as a code block that scrolled sideways on the phone (ab370c3e/02), and the reading session's files did not open when clicked (ab370c3e/04).

On batch 6's card the user asked for one reading session, not one per unit: "I think the batch review card needs to be a summary in the pending view and then a single planotator. That single planotator is a more extensive summary plus each of the individual OpenSpec changes for everything in the batch" (2026-10-12-swancloud-planner-9ddc53be/01). And the card did not say what it was: "What kind of card is this actually? Is this the batch review for units that have been coded already?" (e445bc04/01).

The design agent ruled what a batch card is (`briefs.9`, `briefs.12` and `briefs.13` as amended; record 0005, its bullets "A batch is one card that asks nothing, and says where notes go" and "A batch card is a summary and one reading session, and says what it is"): one card for the whole batch, never split by five, naming every unit; it says first what it is; it asks nothing, since every Pending You question is required, and closes on one tap; its summary is prose the phone wraps, never a code block; it links one reading session on the batch, which opens the reviewer's summary whole and every unit's whole change as one review; the batch's notes are that session's annotations and the card's own note, and the card says so in plain words. No card of crew's asks a required question in words.

## What Changes

- **A batch is one card.** However many units a batch holds, the planner posts one card for it, keyed `batch/<n>`, naming every unit with its team. The rail shows one row per batch. A batch is never split by five.
- **The card says what it is, and asks nothing.** Its first words say it is the partition's batch of the changes written or rewritten since the last batch, already being built, read for notes and approving nothing. It is a Pending You notice the user sends back with one tap: no choice of units, no question in words, no approval. Units go on building whatever the user does with it, as they already do.
- **One reading session for the whole batch.** The card links one plannotator session, which opens the reviewer's summary and then every unit's whole change, as read at its commit, as one review in that order. crew gathers those files into the batch's own folder on the main level's host, each named for its unit, and starts the one session on them. The session opens every file whole, never a folder whose files the user must click open.
- **Notes come from where the user writes them.** The annotations the user sends from the session go at once, word for word, to the team of each unit they speak of. The card's own note goes the same way when the user sends the card. Words that speak of no unit the planner can tell go to every unit's team, saying so, so no words the user wrote reach nobody. Approving the session with no annotations means every unit is fine as far as the session goes, and leaves the card open.
- **The card's summary reads on the phone.** The card carries, for each unit, its name, its team and the short opening paragraph the reviewer writes for it, as prose that wraps, never a code block or an attachment. The reviewer writes the whole summary that way, with what a change touches named in words rather than as paths. The fuller summary is in the session.
- **crew refuses a batch card in another form**, as it does for a proposal's, a verify report's and a landing's: a choice, a pick-several, an approval, a question in words, steps, an attachment, a code block in its words, more than one link, or a card that leaves out one of the batch's units is refused before it reaches Pending You, naming the form to use. **No card of crew's may ask a question in words**, whatever its row.
- A batch card posted before this lands, under the old `batch/<n>-<k>` keys, keeps its one session per unit and is read and closed as it was, except that each unit's session now opens that change's files as one review rather than its folder, so its files open too.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `review-batches`: a batch is one card that says what it is and asks nothing; the reviewer writes a short opening paragraph per unit and no code; the batch's notes are its session's annotations and the card's own note.
- `rail-cards`: a batch's row and key are one per batch, `batch/<n>`; a batch's card has its own form, with one link, which crew enforces; no crew card asks a question in words.
- `card-sessions`: a batch card under `batch/<n>` has one session, on the batch's folder holding the summary and every change, opened as one review; its decision is the batch's notes, never the card's answer.

## Impact

- `plugin/lib/plan.py`: the batch's one rail row and key, the planner's key check, the batch's folder and its one session, the card commands' reading of `batch/<n>` with no unit, and the old keys read with their per-unit sessions until their cards close.
- `plugin/hooks/cards`: the batch card's form, its one link, the batch's units named on it, no question in words on any card, and a `batch/<n>` card's close ending its one session.
- `plugin/roles/planner.md` *Batches* and *Cards*, `plugin/roles/reviewer.md` *The summary*, `plugin/lib/crew.py` `cards_how`, and, for `crew card`'s changed arguments, `README.md`, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew` together (`docs.2`).
- `tests/t-batch-cards.sh`, `tests/t-batches.sh`, `tests/t-cards.sh`, `tests/t-card-sweep.sh`, `tests/t-briefs.sh`, and `tests/moon.yml` if a test's inputs change.
- `openspec/changes/units-build-at-once-and-are-reviewed-in-batches/` has landed but is not archived, so `review-batches` and the batch parts of `rail-cards` and `card-sessions` are still deltas there; this change's deltas modify the requirements it adds and must be archived after it.
- It takes in the work of `a-cards-reading-session-opens-its-files`, as record 0005 has it: every session crew starts on a change gives plannotator the files themselves rather than a folder, the batch's one session and an old batch card's per-unit sessions alike, and patches nothing of plannotator's.
- Rules relied on: `briefs.9`, `briefs.11`, `briefs.12`, `briefs.13`, `roles.3`, `read.1`, `code.3`. Clearing `briefs.13`'s not-built clause and the `_open.md` item is the design agent's after landing (`docs.7`).

## Touches

```
plugin/lib/plan.py
plugin/hooks/cards
plugin/lib/crew.py
plugin/bin/crew
plugin/roles/planner.md
plugin/roles/reviewer.md
plugin/skills/crew/SKILL.md
README.md
tests/t-batch-cards.sh
tests/t-batches.sh
tests/t-cards.sh
tests/t-card-sweep.sh
tests/t-briefs.sh
tests/moon.yml
```
