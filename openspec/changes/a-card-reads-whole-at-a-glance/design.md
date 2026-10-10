# Design

## Context

Why is in `proposal.md`; what becomes true is in the `rail-cards` delta.

Today the planner's and the conductor's card discipline is one token, `CARDS`, built by `cards_how()` in `plugin/lib/crew.py`. On what a card says it has one sentence, "Put what the user would read on it", and on the link one paragraph that puts it "on the card as its artifact of kind `url`, titled "Read and annotate it in plannotator", in place of a file or a path". The conductor's *Review with the user* asks for "two or three plain sentences" on what the unit would make true, and its *Cards* list says what each of its cards links. The planner's *Cards* says the proposal card links the session on the page `crew plan proposed <n>` prints.

Read on 2026-10-09 (ADR 0005, "A card reads whole at a glance"): crw-1's two review cards each had a two-sentence summary and the link only as an artifact of kind `url`; the session answered on its port, so the link worked but sat where the user does not look.

Pending You's card, from its `post_request` schema as this session's tools load it (read 2026-10-09):

- `title`, at most 140 characters, "the question itself, read cold".
- `summary`, at most 400 characters, "one or two sentences: what's going on, why you stopped". It is what the card shows first.
- `context`, required, with `background` (a string with no stated limit), `links` (`{label, url}` items), `trace` (`{state, text}` items), `filesTouched` (strings) and `tried` (strings); all five are required, so an empty list is how a card has none.
- `artifacts`, at most eight, of kind `image`, `diff`, `url`, `file`, `draft`, `code`, or `path` (a file on a machine, by full path).
- `options`, two to five, each a `label` of at most 80 characters and a `detail` and `consequence` of at most 200.

What a proposal's page holds, from README and `plan.py` `plan_proposed`: the case, then each change in plain words, with the command approval runs under each. What a verify report holds: OpenSpec's verify scorecard and its issues, each CRITICAL, WARNING or SUGGESTION, saved whole by the verify stage (`plugin/roles/verify.md`). What a change's proposal holds: *Why*, then *What Changes* as bullets each led by a bold sentence, as crew's own changes are written.

Rules this design rests on: `briefs.9` (what it builds), `briefs.4` (a decision shown whole, answered in words), `briefs.13` (a row's card has the row's form, which this leaves as it is), `briefs.8` (plain English), `roles.3` (when a check is owed), `docs.4`, `docs.5`. Pages whose areas it touches: `briefs.md` (the roles and the card discipline in `crew.py`'s tokens), `teams.md` (`crew.py`), `tests.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**

- The user decides from the card without opening anything, and opens the link only to read more or annotate.
- What the card says is the document's words, so the card and the document never disagree.

**Non-Goals:**

- A check in crew that refuses a thin card or a card with a path. The agents broke no rule their brief stated: the brief told them to put the link as an artifact and to write two or three sentences. `roles.3` asks for a check when an agent breaks a rule its brief already states; this is the brief's first statement of it. crew's card hook stays a recorder here; refusals of a card's form are `a-rows-card-has-the-rows-form`'s and `a-teams-cards-are-its-conductors`'s.
- The batch card of `briefs.12`, which is not built (`concurrent-units`); when it is, it carries each unit's words by this same discipline.
- What a landing card asks beyond naming its bolt; `a-teams-cards-are-its-conductors` gives it the proof's step for the user.
- Any change to `crew card session`, `crew card wait`, the hook, Pending You or plannotator.

## Decisions

### 1. The summary opens with the link, then the bolt, then the decision

The summary is the card's first words and the only ones with a hard budget, 400 characters. It reads: the link, then the bolt, then the opening sentences of the document's own case, as many whole sentences as fit. A link is about 45 characters (`http://mac-studio.ts.swancloud.net:19432`), the bolt's name a few words, so about 300 characters are left for the case, two or three sentences of a crew proposal's Why.

Why the link first and not last: the user named the link as what they look for, and a summary cut to fit loses its end, never its start. Why in the summary and not only the background: the summary is what Pending You shows on the card's face and in Herdr's popup; the background is behind it.

### 2. The background holds the rest, in the document's words

The background begins with the same link, then holds, for each kind of card:

- **Review**: the change's Why as the proposal words it, then "What it changes:" and one line per What Changes item, its bold lead sentence as written.
- **Proposal**: the case as the page words it, then one line per change, as the page heads it in plain words (the command approval runs is left out: `briefs.4` forbids reciting it, and the card's approval is the answer).
- **Verify**: one line per finding the report raised, its severity and what it found in the report's words, followed by what the conductor would do about it in a few words of its own; the options carry the conductor's choices as they do now.

The cut is by whole sentences and whole items, never by rewording. The background has no stated limit in Pending You's schema; crew sets none either, since a Why and one line per change is already bounded by how crew writes changes.

Why the document's words rather than the agent's: a card in the agent's own words is a second account of the change that can disagree with it, which is the staleness ADR 0005 guards against, and "the document's own words" is what the record rules.

### 3. The link is in the links and is no artifact

The link is the card's one entry in `context.links`, labelled "Read and annotate it in plannotator". It is no longer an artifact: the record allows it as one only beside its place in the words, and carrying it three times on a card the user reads at a glance adds nothing. `artifacts` is left empty for a review, proposal or verify card. When the link changes (a session started again), the owner updates the summary, the background and the link together, with the `changeNote` "New plannotator link", as the discipline already says it updates the card's link.

### 4. No path, anywhere on a card

No path in any field: the title, summary, background, trace, the links, `filesTouched`, `tried`, and no artifact of kind `path` or `file`. `filesTouched` is an empty list. A unit, a report or a proposal is named by its name, and reached by the link. The conductor's pane message keeps the change folder's path, since the pane is not a card and a reader at the terminal uses it.

### 5. The conductor's pane message is the card's words

*Review with the user* asks for what the card says, the change's Why and its changes in the proposal's words, in place of "two or three plain sentences". One account, two places.

## Risks / Trade-offs

- [A summary of 400 characters still cuts a long Why short] → the background holds all of it, and the summary ends on a whole sentence.
- [An agent rewords anyway] → the briefs say "in the document's own words, never reworded"; if agents break it once it is stated, `roles.3` calls for a check, which is new work for the planner.
- [A long change makes a long background] → crew's changes have one Why and a handful of What Changes items; a change with many is a sign it is too big, and the card shows that honestly.

## Migration Plan

None beyond landing: each planner and conductor reads the new discipline at its next fresh start. A card already open keeps its old form until it is closed or updated.

## Proof in dev

None. crew has nothing to deploy; its proof before landing is the suite on the bolt.

## Proof on real work

Once the bolt has landed and every host has pulled, with the planner and the conductors started fresh:

- The next review card a conductor posts: its summary begins with the plannotator link, names the bolt, and goes on with the unit's Why in the proposal's words; its background holds the Why and one line per change; its links hold the same link; it has no artifact and no path. The user reads it at a glance on the phone and in Herdr's popup.
- The next proposal card the planner posts, and the next verify card: the same shape, with the case and each change, or each finding and what the conductor would do.

## Task notes

### 1.1

In `cards_how()` (`plugin/lib/crew.py`), replace "Put what the user would read on it" with what a card says, as Decisions 1 to 4 put it, in the discipline's plain second person: the summary begins with the session's link, then the bolt, then the document's own opening sentences, as many whole ones as fit in Pending You's 400 characters; the background begins with the same link, then the document's words for the card's kind (a change's Why and the lead sentence of each of its What Changes items; a proposal's case and each change in a line; a report's findings each in a line, with what you would do about it); cut by whole sentences, never reworded. In the plannotator paragraph, the link goes into the summary and the background first and into the card's links labelled "Read and annotate it in plannotator", and the sentence putting it "as its artifact of kind `url`" goes. Add that no card carries a path, in any of its fields, its files touched empty, and that a card whose link changes is updated in its summary, background and links together. A landing card names its bolt and links nothing (the conductor's *Cards* already says it carries no link).

### 1.2

In `plugin/roles/conductor.md`: in *Review with the user*, "in two or three plain sentences what it would make true" becomes what its card says, the change's Why and its changes in the proposal's words; keep the change folder's path in that pane message. In *Cards*, the review bullet says its card's words are the change's Why and each What Changes item's lead sentence, the verify bullet that its words are each finding with what you would do about it, and the landing bullet that it names the bolt and carries no path; drop the change folder's path from the review bullet's wording of what the card carries (the session is on the change; the card shows no path). In `plugin/roles/planner.md` *Cards*, the proposal card's words are the case and each change in a line, as `crew plan proposed <n>` words them, with no command.

### 1.3

In `tests/t-briefs.sh`, the conductor's and the planner's checks drop "as its artifact of kind" if any check holds it, and hold phrases of the new discipline: the link first in the summary, "in the document's own words", "never reworded", "No card carries a path", and the links' label; the conductor's brief lacks "two or three plain sentences". Keep the existing checks that still hold.

### 2.1

In `docs/architecture/briefs.md`, `briefs.9`'s detail drops its last sentence ("The card discipline puts the link only as an artifact … until `a-card-reads-whole-at-a-glance` lands: `_open.md`."); in `docs/architecture/_open.md`, the `briefs.9 as amended` line goes. In README's paragraph on a card's plannotator link, add one sentence: the link is the first thing in the card's words and is among its links, the card's words say what the user decides from in the document's own words, and no card carries a path.
