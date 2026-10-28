## 1. The queued submission is recorded, and its waiter waits a call at a time

- [ ] 1.1 A run-record entry carries `Submission` (design, Decision 1; Task notes 1.1); passes `tests/py/test_record.py`.
- [ ] 1.2 `crew bolt submit` records a `bolt.submit` entry with `Outcome: queued`, `Submission`, `Head` and `Base` as soon as sluice has queued the landing, keeps the user's pane words on the submitting host then, and no reader of the record takes a queued entry for an outcome (design, Decision 1; Task notes 1.2); passes `tests/py/test_landing.py`.
- [ ] 1.3 The landing's background waiter on the team's host calls `sluice wait <n> --timeout 9m --json` again while it exits 5, then runs `crew _landing-read <label> <bolt>`, and `landing_now` still reads it alive meanwhile (design, Decision 3; Task notes 1.3); Verify `tests/suite t-journey-land` ends with "0 failed".

## 2. One read records a landing from sluice's record

- [ ] 2.1 What sluice's record of a submission means for a landing (standing, out with its exit, or unreadable) is a decision of facts (design, Decision 2; Task notes 2.1); passes `tests/py/test_landing.py`.
- [ ] 2.2 `crew _landing-read <label> <bolt>` runs only on the team's host, one at a time per bolt, records a submission's outcome once from sluice's record as `crew bolt submit` records it today, records nothing while the submission stands or the record can't be read, and says which (design, Decision 2; Task notes 2.2); passes `tests/py/test_landing.py`, and Verify `tests/suite t-journey-land` ends with "0 failed".
- [ ] 2.3 A read that finds the bolt landed closes it with `crew bolt land`'s code in main-level ops's name, and a refused close is said every time and recorded as a refused `bolt.land` only when its words are new since the landing (design, Decision 4; Task notes 2.3); passes `tests/py/test_landing.py`.

## 3. Every crew act that reads the bolt after its landing runs the read

- [ ] 3.1 `crew bolt submit`'s own end hands the outcome to the read on the team's host and prints what it said, and exits non-zero for a bolt that did not land (design, Decision 3; Task notes 3.1); passes `tests/py/test_landing.py`.
- [ ] 3.2 The team's read runs the landing's read for a bolt whose landing worktree stands with no waiter alive, or whose every unit and chore has landed while the plan holds it, and for no other (design, Decision 3; Task notes 3.2); passes `tests/py/test_landing.py`.
- [ ] 3.3 `crew bolt land` reads a queued landing first, so a hand close of an unrecorded landing records it before closing (design, Decision 3; Task notes 3.3); passes `tests/py/test_landing.py`.

## 4. The bolt's head line and the agents' views

- [ ] 4.1 A held bolt's head line says its landing is queued with its submission number, or that it landed on main and was not closed with its refused close's words, and main-level ops's band shows the latter (design, Decision 5; Task notes 4.1); passes `tests/py/test_board.py`, and Verify `tests/suite mod` ends with "0 failed".

## 5. ops's brief

- [ ] 5.1 Main-level ops's brief says crew's next read closes a bolt that landed and was not closed once what it named is mended, and that ops may run `crew bolt land` (design, Decision 6; Task notes 5.1); Verify `tests/suite t-briefs` ends with "0 failed".

## 6. Journeys

- [ ] 6.1 The landing journey proves a submitter killed after the queue with the waiter's read recording and closing the bolt, a stopped waiter with the conductor's next command recording it, and a refused close recorded once, shown on the bolt's head line and lifted by a later read (design, Decision 2 to 5; Task notes 6.1); Verify `tests/suite t-journey-land` ends with "0 failed".
- [ ] 6.2 The tests the change affects pass; Verify `tests/suite --affected` ends with "0 failed".
