# Proposal

## Why

The user can't decide from a Pending You card at a glance. On crw-1's two review cards on 2026-10-09 the card said two sentences about the change, and its plannotator link sat only as an attached artifact, where the user doesn't look: "the pending you isn't showing me enough detail about the OpenSpec proposal. I expect the "For" (what it shows me) to be glanceable, and for "Pending You" to include a link to a running Planitator" (signal `2026-10-09-swancloud-operator-mac-studio-351110ee/01-review-card-too-thin-to-glance`). The agents did what their card discipline told them: it says only "put what the user would read on it" and puts the link on the card as an artifact of kind `url`, and the conductor's brief asks for two or three sentences. The design has already ruled what a card says (`docs/adr/0005-the-rail-is-answered-through-pending-you-cards.md`, "A card reads whole at a glance, and its link is in its words"; `briefs.9`); this change makes the briefs say it.

## What Changes

- **A card's words carry what the user decides from, in the document's own words.** A review card says what the unit makes true and what it changes: the change's Why and each What Changes item's lead sentence, as the proposal words them. A proposal card says the proposal's case and each change it would make, a line each, as `crew plan proposed <n>` words them. A verify card says each finding in a line, with what the conductor would do about it. Each is cut to the card's budget, sentence by sentence, never reworded into a summary of the agent's own.
- **The card's opening words name the link and the bolt.** The card's summary, the part Pending You shows first, begins with the plannotator link, then names the bolt, then says what the user decides; its background begins with the same link and holds the rest. The link is also the card's one entry in its links, labelled "Read and annotate it in plannotator". The link is no longer an attached artifact.
- **No card carries a path.** No file, folder or report path on a card: not in its words, its links, its files touched or its artifacts. The landing card, which has nothing to read, names its bolt and carries no link and no path either.
- **The conductor tells the user the same words in its pane.** Its "ready for review" message says what the card says, in place of two or three sentences of its own.
- **The rule is marked built.** `briefs.9`'s note that the card discipline still puts the link only as an artifact, and its entry among what is not yet built, are removed.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: three new requirements: a card's words are the document's own; its plannotator link and its bolt come first, and the link is among its links and is no artifact; no card carries a path.

## Impact

- `plugin/lib/crew.py`: `cards_how()`, the card discipline the planner's and the conductor's briefs share.
- `plugin/roles/conductor.md`: *Review with the user* and *Cards*, what each of its cards says.
- `plugin/roles/planner.md`: *Cards*, what the proposal card says.
- `docs/architecture/briefs.md` and `docs/architecture/_open.md`: `briefs.9` is built.
- `README.md`: the paragraph on a card's plannotator link.
- `tests/t-briefs.sh`: the briefs say it.
- Nothing changes in Pending You, plannotator, `crew card session` or the card hook.

## Touches

`plugin/lib/crew.py` (`cards_how()`), `plugin/roles/conductor.md`, `plugin/roles/planner.md`, `docs/architecture/briefs.md`, `docs/architecture/_open.md`, `README.md`, `tests/t-briefs.sh`, `openspec/specs/rail-cards/spec.md` (by delta).
