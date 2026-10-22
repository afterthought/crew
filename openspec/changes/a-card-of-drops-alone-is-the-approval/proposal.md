# Proposal

## Why

A proposal's card today makes every row of the change a box: a new unit ticked, a dropped one unticked as "Keep <unit>", an amended one unticked as "Keep <unit>'s old intent". A proposal that only drops units is then a list whose every box is cleared as proposed, and Pending You will not send a list back with nothing ticked. On 2026-10-19 the user could not send proposal 148's card, three drops, as it stood, and wrote the answer as a note instead: "I can't submit this fucking card with all of them unchecked and that's the whole fucking point of this" (signal 2026-10-19-swancloud-planner-66f77ec4/01). The rule already says what the card should be: a proposal's card is an approval with the change drawn and in text "and a choice per new unit or chore to leave it out" (`briefs.13`); the builder asks more than that.

## What Changes

- A proposal's card asks a choice only for each unit or chore the proposal makes new to a bolt or the queue, ticked, to leave out. Drops, amendments, moves, orders and new bolts are drawn on the card's face, its picture and its text, and apply with it; none of them is a box.
- A proposal with no new unit or chore, drops alone, or drops with moves, orders and amendments, is raised as the hold-to-approve of low risk, reversible, with its change drawn and no boxes. The user approves it as it is, or declines it with a note when they want to keep something it drops or amends.
- A card with new units or chores asks only those: one of them is the choice of adding it or leaving it out, up to five are one list, more are lists of at most five, and more than fifteen are a hold-to-approve linking the proposal's reading session, as today.
- The card's summary tells the user what to do: on a hold-to-approve that drops or amends, that declining with a note keeps what they want kept; on a card of new units, that what else it changes applies with it.
- **BREAKING** for answers: `crew plan answer` takes only the boxes the card now asks. A dropped unit "kept" or an amendment "kept as it was" is no longer an answer, and `crew plan approve`'s internal keep path goes with it.
- The planner's brief, the crew skill and README say the card's new shape.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plan-proposals`: the card's boxes are its new units and chores only; a proposal with none is a plain approval; a card's answers apply with no kept drop or amendment.

## Impact

`plugin/lib/cards.py` (`proposal_rows`, `proposal_form`, `proposal_card`); `plugin/lib/plan.py` (`proposal_reads`, `answered`, `as_they_stand`, `approved_words`, `plan_approve`, `plan_answer`'s docstring); `plugin/roles/planner.md` *Cards*; `plugin/skills/crew/SKILL.md`; `README.md`; `tests/py/test_proposal_card.py`, `test_proposal_life.py`, `test_cards.py`; `tests/t-briefs.sh`. Proposal cards open when this lands keep the boxes they were posted with (design, *Migration Plan*).

## Touches

```
plugin/lib/cards.py
plugin/lib/plan.py
plugin/roles/planner.md
plugin/skills/crew/SKILL.md
README.md
tests/py/test_proposal_card.py
tests/py/test_proposal_life.py
tests/py/test_cards.py
tests/t-briefs.sh
```
