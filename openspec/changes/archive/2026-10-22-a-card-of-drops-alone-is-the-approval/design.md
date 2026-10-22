# Design

## Context

Why is in `proposal.md`. What the card must be is in `briefs.13`: a proposal's card is "an approval with the change drawn and in text and a choice per new unit or chore to leave it out". The builder, `cards.proposal_card`, makes a box of every row `cards.proposal_rows` returns, and that function returns three kinds: a new unit or chore (`add:<unit>`, ticked), a dropped one (`keep:<unit>`, "Keep <unit>", unticked) and an amended one (`old:<unit>`, "Keep <unit>'s old intent", unticked). `cards.proposal_form` picks the card's form from the count of those rows: a hold-to-approve when there are none or the card would link its reading session, a choice for one, one `multi` list up to five (`BOXES`), lists of questions beyond. So a proposal of three drops is a `multi` list of three unticked boxes, which is what the user could not send.

On the answer side, `plan.card_asks` reads the questions off the card crew builds now, `plan.card_answer` checks the planner's answer against them, `plan.answered` turns the held answers into the units left out (`cleared`) and the units kept as they were (`keep`), and `plan.plan_approve` applies the proposal through `as_they_stand`, leaving out each cleared unit's commands and each kept unit's drop or amendment, and says what happened through `approved_words`. `plan.proposal_reads` decides from the commands alone whether the card links a reading session, counting drops and amendments among the rows.

The intent names `plugin/hooks/cards` `FORMS` as a source. That table is gone from main: crew e112a98e narrowed the hook to an agent's own question (record 0031 §2), so the hook no longer checks a row's card against a form, and nothing in it changes here.

Rules relied on: `briefs.13` (the card's form), `briefs.9` (more than fifteen new units link the reading session), `code.7` (`proposal_rows`, `proposal_form` and `proposal_reads` stay functions of the commands alone), `tests.11` and `tests.4` (each case in the logic tier), `docs.2` (README and the skill follow a change to what `crew plan answer` takes), `docs.4` (the spec changes through this delta), `docs.6` and `docs.7` (no rule page or record is edited here). Pages whose areas the change touches: `plan.md` (`plugin/lib/plan.py`), `briefs.md` (`plugin/roles/`, `plugin/skills/`), `tests.md` (`tests/`), `docs.md` (`README.md`, `openspec/`). `code.8`: the agents' views and `status.js` draw no proposal card's boxes, so nothing they draw moves.

## Goals / Non-Goals

**Goals:**
- Only a unit or chore new to a bolt or the queue is a box on a proposal's card, and a proposal with none is the hold-to-approve, so every card can be sent back as it stands.
- The card tells the user how to object to what is not a box.
- No code path is left that applies a "kept" drop or amendment.

**Non-Goals:**
- How a user keeps one dropped unit on a card that also asks new units: that card applies its drops with the boxes, and the user's note beside it reaches the planner only after it is applied (`A note beside an approval goes to the planner after it`). The design does not say what that card should offer; it is named for the design agent.
- A card with new units every one of which the user clears: whether Pending You sends a list back with nothing ticked is the same question as the signal's, and is not changed here.
- Record 0031 §5 still draws the card as every row a box. Amending it is the design agent's (`docs.7`).

## Decisions

**1. The rows are the new units and chores alone.** `proposal_rows` returns one `("new", argv)` per unit or chore `new_units` names, in the order the commands first name it, and nothing for a drop or an amendment. `new_units` is unchanged: a `unit move` or `chore move` into a bolt is new to that bolt, and its box is "Move <unit> in", as today. *Alternative:* keep a box per drop but ticked, "Drop <unit>", so the card sent as it stands is never empty. Rejected: `briefs.13` gives the card a choice per new unit or chore only, and a drops-alone card would still be a list to tick through rather than the approval the intent asks for.

**2. The form follows from the count of new units.** `proposal_form`: `"approve"` when there is no new unit or chore or more than `CARD_NEW` (fifteen); `"choice"` for one; `"multi"` up to `BOXES` (five); `"lists"` beyond. The bound `len(rows) > BOXES * GROUPS` goes, since fifteen new units fill at most three lists of five and a card holds four. `plan.proposal_reads` becomes `len(new_units(argvs)) > cards.CARD_NEW`, as `proposal_card`'s `session` does. A rewrite still compares the replaced proposal's form with its successor's, both now read by this rule (`raise_proposal_at`).

**3. The builder keeps the face and changes the boxes and the words.** `proposal_card` builds a box only for a new row; the lone row's other side is always "Leave <unit> out". The face keeps a paragraph for each new and each dropped unit, the picture and the text are as they are, and the title's counts still name every kind. The summary's second sentence, `how`, becomes:
- a hold-to-approve whose commands drop or amend a unit and that links no reading session: "Hold to apply it whole; to keep a unit it drops or amends, decline with a note.";
- any other hold-to-approve: "Hold to apply it whole." as today;
- a choice: "Its one new unit is set as proposed; pick the other side and send to leave it out.";
- one list or lists: "Each new unit below is ticked; clear any to leave it out, and send.";
- and, on a choice or list whose commands also drop or amend a unit, followed by "What it drops or amends applies with it."

The handed-back `boxes` hold only `is: "new"` entries, every one ticked.

**4. The keep path goes.** No card asks to keep a drop or an amendment, so `plan.answered` returns `(waits, cleared)`; `as_they_stand` is replaced by `kept(argvs, cleared, n)` where `plan_approve` called it; `approved_words` loses its `keep` argument and its "Kept on your word" and "Kept the old intent" sentences; `plan_approve` loses `keep`, its `left` (now `cleared`), its "Kept as it was" body line and its "keeping …" words, and its docstring the paragraph about keep; `plan_answer`'s docstring says a new unit unticked is left out and no more. A proposal approved before this lands keeps the `Cleared` it recorded, read as it was.

**5. The hook is not touched.** Context says why.

## Risks / Trade-offs

- [A drop on a card that also asks new units can no longer be refused on the card] → The summary says the drop applies with it; the user who wants it kept does not send and tells the planner, or the planner splits its drops from its additions. Named for the design agent (Non-Goals).
- [A card still open when this lands keeps the boxes it was posted with: a "Keep" box, or a list where crew now builds a hold-to-approve] → `crew plan answer` checks against the card crew builds now, so an answer naming `keep:<unit>` or `old:<unit>`, or `rows-1` for a card now built as `plan`, is refused naming what the card asks now, and nothing is recorded or applied. *Migration Plan* says what the planner does with it.
- [A rewrite with `--replaces` of such a card can keep its old questions] → both forms are now read by the new rule, so a card of three Keep boxes rewritten to the same drops reads as no change of form and is changed in place, its old boxes left as they were (`cards.CHANGED`). The planner drops and proposes again instead, which withdraws the old card and posts a new one.

## Migration Plan

Nothing is migrated in code: the proposals and their cards are the plan's and Pending You's, and crew keeps no copy of a card's questions.

## After deploy

- When this lands, main-level ops lists each partition's open proposals (`crew plan proposed --label <label>`) and tells each partition's planner which of them drop or amend a unit, since those cards were posted with Keep boxes or as a list crew no longer builds. For each, when the user answers: an answer that ticks no Keep box is given to `crew plan answer` without the `keep:` and `old:` ids, or as `plan approve` for a card now built as a hold-to-approve; an answer that keeps something is the user's word, and the planner drops the proposal (`crew plan drop`) and proposes again without what was kept. Doer: main-level ops, then the planner; it waits on the landing. No check can be code: it reads cards posted before the code existed.

## Task notes

**1.1** In `plugin/lib/cards.py`: `proposal_rows(argvs)` keeps its loop's first branch alone (a unit in `new_units` and not yet seen gives `("new", a)`) and its docstring says so. `proposal_form` per Decision 2, its docstring naming the forms by the count of new units. `proposal_card` per Decision 3: drop the `dropped` and `amended` branches of the row loop, keep `units[a.unit] = a` for each dropped unit's `a` so its paragraph is still written (walk the `drop` commands for those), `session = len(new) > CARD_NEW`, the `other` side `f"Leave {r['unit']} out"`, the `how` words exactly as listed, and the docstring's sentence about every row's box rewritten to say only a new unit or chore is a box, ticked, and a proposal with none a hold-to-approve. `named` for the markdown title still reads new and dropped from the paragraphs' units, not from the rows. In `tests/py/test_proposal_card.py`: `TestBuiltDropAmendAdd`'s list is `add:e-fifth` and `add:<LONG>`, both ticked, `multi` `{"min": 0, "max": 2}`, summary "The third unit is not needed. Each new unit below is ticked; clear any to leave it out, and send. What it drops or amends applies with it. It waits on swb-2-conductor to agree.", its face still holding the `c-third` drop paragraph; `test_a_lone_row_…`'s dropped case becomes a hold-to-approve whose summary ends "decline with a note."; the form parametrization's drop-and-amend row becomes `"approve"`, and add one row of a drop beside one add, `"choice"`. Add a case of three drops alone: `approve`, no `options`, `boxes == []`, a paragraph per drop.

**1.2** In `plugin/lib/plan.py`, `proposal_reads` per Decision 2 and its docstring. In `tests/py/test_cards.py`'s `test_a_proposal_of_more_than_fifteen_new_units_or_more_rows_than_its_lists_hold_has_a_reading`, rename it for fifteen new units alone and assert that sixteen adds read, fifteen do not, and fifteen adds with any number of drops do not.

**2.1** In `plugin/lib/plan.py` per Decision 4. In `tests/py/test_proposal_life.py` `TestAnswers`: `sent` unpacks `(waits, cleared)` and returns `(dos, cleared, words)`; `DROP_ADD`'s asks are `{"rows-1": ["add:b", "add:c", "add:d"]}` and sent as it stands words "Applied: added b, c and d; dropped a."; the "how to object to a drop" case becomes a drops-alone proposal whose asks are `{"plan": None}`, approve applying every drop and decline nothing; the amendment case sends `["add:b"]` and gets "Applied: added b; amended x. Left out on your word: c."; the refusal case's words are "rows-1 holds add:b, add:c or add:d, not add:zz", plus `keep:a` refused the same way; the seven-unit case compares `answered` with `(["rows-2"], [])` and `([], ["s-5"])`. Check the words against what `approved_words` prints and keep the order it gives.

**3.1** In `plugin/roles/planner.md` *Cards*: the sentence beginning "The card is one checkbox list" says the card asks only the units and chores new to a bolt or the queue, each a box ticked as proposed that the user clears to leave it out, what else it changes drawn on its face and applied with it; a lone new unit is the choice of its two sides; and a proposal with none, drops, amendments, moves and orders alone, a hold-to-approve, which the user declines with a note to keep something. The *When the user answers it* paragraph's "a new unit unticked left out, a dropped one ticked kept, an amendment ticked not applied" becomes "a new unit unticked left out". `tests/t-briefs.sh` swaps its `"a dropped one unticked as \"Keep <unit>\""` and the "applies the change with the boxes as they stand, …" strings for the new words, and adds `lacks "$out" "Keep <unit>"`.

**3.2** `README.md` lines on `crew plan propose` and `crew plan answer`, and `plugin/skills/crew/SKILL.md`'s "every row of the change set as proposed", say the same as 3.1 in their own voice. `plugin/bin/crew`'s usage already says only new units are left out, so it stays (`docs.2`).
