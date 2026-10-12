## 1. A batch is one row and one card

- [x] 1.1 The rail, the planner's key check and the card commands read one row per batch, keyed `batch/<n>` and holding every unit, and still read a batch's old `batch/<n>-<k>` cards until each closes (design, *Task notes* 1.1).
- [x] 1.2 `tests/t-batch-cards.sh` and `tests/t-batches.sh` prove one row and one card key per batch, the sessions under `batch/<n>`, and an old batch's keys read until closed (design, *Task notes* 1.2).

## 2. crew refuses a batch card in another form

- [x] 2.1 The card hook refuses a `batch/<n>` card that is not an `fyi` with nothing to answer and its summary as prose, and any row's card that asks a question in words, on post and on update (design, *Task notes* 2.1).
- [x] 2.2 The card hook refuses a batch card that leaves out one of the batch's units (design, *Task notes* 2.2).
- [ ] 2.3 `tests/t-cards.sh` proves each refused form and the allowed form of a batch card, and the words question refused on every row (design, *Task notes* 2.3).

## 3. The briefs and README say so

- [ ] 3.1 The planner's brief posts one card per batch that asks nothing, says where notes go in plain words, and sends a unit's session annotations at once and the card's note to each unit it speaks of (design, *Task notes* 3.1).
- [ ] 3.2 The reviewer's brief has the summary written as prose with no code block and Touches named in words (design, *Task notes* 3.2).
- [ ] 3.3 The card discipline says a batch card's sessions are its units' and none answers the card (design, *Task notes* 3.3).
- [ ] 3.4 README says a batch is one card asking nothing (design, *Task notes* 3.4).
- [ ] 3.5 `tests/t-briefs.sh` pins the briefs' new words and refuses the old ones; `tests/suite --affected` is green (design, *Task notes* 3.5).
