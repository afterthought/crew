# Tasks

## 1. The raise tries twice

- [ ] 1.1 A batch card's or a long proposal card's raise tries its reading a second time when the first refuses, and builds the card without it only on the second refusal, with that reason. The cases pass in `tests/py/test_cards.py` (design, Decision 1; Task notes 1.1).
- [ ] 1.2 Such a card raised without its reading says crew tries again when the rail is read and names `crew card session <key>` as the planner's act, in its words and in the command's output. The cases pass in the logic tier (design, Decision 2; Task notes 1.2).
- [ ] 1.3 `raise_batch` whose first start fails and second opens posts the card with its link and no `Unread`. The case passes in `tests/py/test_batches.py` (Task notes 1.3).

## 2. Starting a reading changes its card

- [ ] 2.1 One function opens a batch's or a proposal's reading, records the try, and changes the waiting card to carry the link, sharing the landing's relink. `proposal_act` answers a relink, and its case passes (design, Decision 3; Task notes 2.1).
- [ ] 2.2 `crew card session batch/<n>` and `proposal/<n>` go through it: a start anew changes a waiting card and records `card.reading`, an answered card is left, a link given again changes and records nothing, and a refusal is recorded. The cases pass in `tests/py/test_cards.py` (design, Decisions 3 and 5; Task notes 2.2).

## 3. The batch's wait starts a missing reading

- [ ] 3.1 `crew card wait batch/<n>` with the card open and no session starts the reading and waits on both, and when it can't, says why once, naming `crew card session batch/<n>`, and waits on the card alone. The decision's cases pass in `tests/py/test_cards.py` (design, Decision 4; Task notes 3.1).

## 4. The rail's read tries again

- [ ] 4.1 Whether a card stands without its reading, and was last tried ten minutes ago or more, is a function of the run record's entries. Its cases pass in `tests/py/test_rail.py` (design, Decision 6; Task notes 4.1).
- [ ] 4.2 The rail's sweep tries each such batch or long proposal card that waits on the user, changes it to carry the link, and lists what came of it. The cases pass in `tests/py/test_rail.py` (design, Decision 6; Task notes 4.2).

## 5. The run record

- [ ] 5.1 `card.reading` is named among the card acts in `record.py`, and any case pinning the acts is updated. `tests/suite logic` passes (design, Decision 5; Task notes 5.1).

## 6. Briefs and docs

- [ ] 6.1 `planner.md` says a card raised without its reading names `crew card session`, that the batch's wait starts it, and that the rail's read tries again. `tests/suite t-briefs` passes (design, Decision 7; Task notes 6.1).
- [ ] 6.2 The crew skill's rows, the usage in `plugin/bin/crew` and `plan.py`, and README's card-session paragraph and list of acts say the same together. `tests/suite t-docs` passes (Task notes 6.2).

## 7. End to end

- [ ] 7.1 `tests/t-journey-review.sh` proves a batch card's second try carrying its link, a card raised without its reading naming `crew card session` with `Unread` in the run record, and the planner's wait starting the reading and changing the card. `tests/suite t-journey-review` passes, and `tests/moon.yml` is regenerated if the test's reads changed (Task notes 7.1).

## 8. Checks

- [ ] 8.1 `tests/suite logic`, `tests/suite t-journey-review t-briefs t-docs t-cards`, then `tests/suite --affected` once, all report 0 failed (Task notes 8.1).
