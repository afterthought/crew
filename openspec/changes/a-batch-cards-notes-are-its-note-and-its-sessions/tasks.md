## 1. A batch is one row and one card

- [x] 1.1 The rail, the planner's key check and the card commands read one row per batch, keyed `batch/<n>` and holding every unit, and still read a batch's old `batch/<n>-<k>` cards until each closes (design, *Task notes* 1.1).
- [x] 1.2 `tests/t-batches.sh` proves one row and one card key per batch, and an old batch's keys read until each closes (design, *Task notes* 1.2).

## 2. crew refuses a batch card in another form

- [x] 2.1 The card hook refuses a `batch/<n>` card that is not an `fyi` with nothing to answer and its summary as prose, and any row's card that asks a question in words, on post and on update (design, *Task notes* 2.1).
- [x] 2.2 The card hook refuses a batch card that leaves out one of the batch's units (design, *Task notes* 2.2).
- [x] 2.3 `tests/t-cards.sh` proves each refused form and the allowed form of a batch card, and the words question refused on every row (design, *Task notes* 2.3).
- [ ] 2.4 The card hook refuses a batch card with more than one link, and its form's words say the card says what it is and links the batch's one session (design, *Task notes* 2.4).

## 3. One reading session per batch

- [ ] 3.1 `crew card session batch/<n>` writes the batch's folder on the main level's host, the summary and every unit's Markdown files at its commit, and starts one plannotator session on those files as one review; a unit with that key is refused; an old key's per-unit sessions are as before (design, *Task notes* 3.1).
- [ ] 3.2 `crew card wait` and `end`, the hook's close and the sweep act on a `batch/<n>` card's one session (design, *Task notes* 3.2).
- [ ] 3.3 `tests/t-batch-cards.sh` and `tests/t-card-sweep.sh` prove the batch's folder, its order, its one session and its refusals, and an old batch's per-unit sessions (design, *Task notes* 3.3).

## 4. The briefs and the docs say so

- [ ] 4.1 The planner's brief posts one card per batch that says what it is, asks nothing, says where notes go in plain words and links the batch's one session, and sends the session's annotations at once and the card's note to each unit they speak of (design, *Task notes* 4.1).
- [ ] 4.2 The reviewer's brief opens each unit's section with the paragraph the card carries, and has the summary written as prose with no code block and Touches named in words (design, *Task notes* 4.2).
- [ ] 4.3 The card discipline says a batch card has one session on the batch, whose decision never answers the card (design, *Task notes* 4.3).
- [ ] 4.4 README, the crew skill and `crew`'s usage say a batch is one card asking nothing, with one session on the batch (design, *Task notes* 4.4).
- [ ] 4.5 `tests/t-briefs.sh` pins the briefs' new words and refuses the old ones; `tests/suite --affected` is green (design, *Task notes* 4.5).
