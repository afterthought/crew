# Tasks

## 1. The card asks only its new units

- [x] 1.1 A proposal's card has a box only for each unit or chore new to a bolt or the queue, and a proposal with none is a hold-to-approve whose summary says how to keep what it drops or amends (design, Decisions 1 to 3; Task notes 1.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_proposal_card.py`.
- [x] 1.2 Whether a proposal's card links its reading session is read from its new units alone (design, Decision 2; Task notes 1.2). Verify `tests/py/test_cards.py` passes in the logic tier.

## 2. Answers carry no kept drop or amendment

- [ ] 2.1 `crew plan answer` and `crew plan approve` apply a proposal with only its cleared new units left out, and nothing of keeping a drop or an amendment is left in `plan.py` (design, Decision 4; Task notes 2.1). Verify `tests/py/test_proposal_life.py` passes in the logic tier.

## 3. The planner, the skill and README say the card's shape

- [ ] 3.1 The planner's brief says a proposal's card asks only its new units and that a proposal with none is a hold-to-approve the user declines with a note to keep something (Task notes 3.1). Verify `tests/suite t-briefs` ends with "0 failed".
- [ ] 3.2 README and the crew skill say the same (Task notes 3.2). Verify `tests/suite t-docs` ends with "0 failed".

## 4. Integration

- [ ] 4.1 The proposal journeys still pass with the card's new shape. Verify `tests/suite logic t-cards t-journey-plan` and then `tests/suite --affected` each end with "0 failed".
