# Tasks

## 1. The batch's card

- [x] 1.1 `crew review --wait` starts the batch's session and posts its card when the reviewer's summary is delivered; `crew card wait batch/<n>` prints the notes and closes the card on the tap or the session's send. Logic: `tests/py/test_batches.py` `TestBatchFacts`, `tests/py/test_cards.py` `TestSessions`. Journey: `tests/t-cards.sh`, `tests/t-journey-review.sh` (`briefs.12`).
- [x] 1.2 `planner.md`'s *Batches* says crew starts the batch's session and raises its card when the summary is delivered, the planner adopting the card by the line its wait prints and reading the notes with `crew card wait batch/<n>`; it no longer starts the session or posts or closes the card. Journey: `tests/t-briefs.sh` pins the words (`tests.6`, `briefs.12`).

## 2. Sessions

- [x] 2.1 A session is started by crew for a batch and a long proposal alone, when the card is raised; `crew card session` prints a running link again and refuses other keys; the session ends on crew's close and on the sweep. Logic: `tests/py/test_cards.py` `TestSessions`. Journey: `tests/t-cards.sh` (`briefs.9`).

## 3. The suite

- [ ] 3.1 `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).
