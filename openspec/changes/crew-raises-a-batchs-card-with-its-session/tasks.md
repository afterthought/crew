# Tasks

## 1. The batch's card

- [ ] 1.1 `crew review --wait` starts the batch's session and posts its card when the reviewer's summary is delivered; `crew card wait batch/<n>` prints the notes and closes the card on the tap or the session's send. Logic: `tests/py/test_batches.py`. Journey: `tests/t-cards.sh` (`briefs.12`).

## 2. Sessions

- [ ] 2.1 A session is started by crew for a batch and a long proposal alone, when the card is raised; `crew card session` prints a running link again and refuses other keys; the session ends on crew's close and on the sweep. Logic: `tests/py/test_cards.py` `TestSessions`. Journey: `tests/t-cards.sh` (`briefs.9`).

## 3. The suite

- [ ] 3.1 `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).
