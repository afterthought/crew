# Tasks

## 1. crew finds the user's own record of the words

- [x] 1.1 `transcript.check` with `want="user"` grades the words by the newest received record the user wrote, so a later echo in a tool's output or a tell does not hide it (design, Decision 2; Task notes 1.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_transcript.py`.

## 2. A pane answer closes its batch for good

- [x] 2.1 `batch_closed` reads a `batch.answer` as closing every key of its batch for good, `awaiting_answer` frees the batch's units, `row_gone` gives its card "Answered in <agent>'s pane at <time>", and the rail drops its row and offers the bolt it held for landing (design, Decision 3 and 4; Task notes 2.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_batches.py` and `tests/py/test_rail.py`.

## 3. `crew card answer` records it

- [x] 3.1 `pane_answer_refusal` refuses a caller who is not the planner or operator, an unknown batch, a batch answered already or waiting on nothing, and any words not read as the user's, naming who said them (design, Decision 1 to 3; Task notes 3.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_batch_answer.py`.
- [x] 3.2 `crew card answer batch/<n> --excerpt "<words>"` records one `batch.answer` with no words in it, closes the planner's card held on this host with the words, and tells the planner the words when the operator ran it (design, Decision 1, 4 and 5; Task notes 3.2). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_batch_answer.py`.
- [x] 3.3 `crew card wait batch/<n>` ends once the batch is answered in a pane, saying in whose pane, and closes the card it holds (design, Decision 4; Task notes 3.3). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_batch_answer.py`.

## 4. The briefs and the docs say it

- [x] 4.1 The planner's and the operator's briefs say when to run `crew card answer` and what becomes of the words, and the usage, README and SKILL.md name the command (design, Decision 6; Task notes 4.1). Verify `tests/suite t-briefs t-docs` ends with "0 failed".
- [ ] 4.2 The tests this change affects pass. Verify `tests/suite --affected` ends with "0 failed".
