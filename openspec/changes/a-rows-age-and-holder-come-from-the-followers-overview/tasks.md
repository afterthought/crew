# Tasks

## 1. The gather reads sluice only through the overview

- [x] 1.1 A kit's gather runs no `sluice status`, and its answer's `decided` comes from the follower's hand or from the overview's recent events, read by a guarded `decided_in` over both of their forms (design, Decision 1; Task notes 1.1). Passes `tests/py/test_bolt_submissions.py` in the logic tier (`tests/suite logic`).
- [x] 1.2 A gather with the follower's queue handed in starts no sluice process, one without it runs one overview and no status, and the follower's read of a kit on the box starts no `sluice status` (design, Decision 1; Task notes 1.2). Passes `tests/contract/test_gather.py` (`tests/suite contract`), and `tests/suite t-journey-board` ends with "0 failed".

## 2. The follower keeps each submission from its submit to its decision

- [ ] 2.1 The follower keeps each held bolt's submissions per kit across lines and gathers, deciding one at its recent event's time or at the line's time, in place of `kept_gone` and the gather's history (design, Decision 2; Task notes 2.1). Passes `tests/py/test_board.py` in the logic tier (`tests/suite logic`).

## 3. A decided merge's stay is split only where crew holds its checks' start

- [ ] 3.1 `bolt_time` gives a submission's stay with no checks' start, and an ended merge stage with no submit crew holds, to team-or-kit, and never to the team under the merge stage; `time_said` names the share and its reason (design, Decision 3; Task notes 3.1). Passes `tests/py/test_bolt_time.py` in the logic tier (`tests/suite logic`).
- [ ] 3.2 `bolt_facts` and `held_time` read the kept or overview `decided` in place of history, give each stage its work, and take a landing by its queued number (design, Decision 4; Task notes 3.2). Passes `tests/py/test_bolt_time.py` and `tests/py/test_rail.py` in the logic tier (`tests/suite logic`).

## 4. The landing's split follows the same rule

- [ ] 4.1 A landing entry's `Split` names team-or-kit and sums to `Age`, from its one read of sluice's record on the team's host (design, Decision 5; Task notes 4.1). Passes `tests/py/test_landing.py` in the logic tier (`tests/suite logic`).

## 5. The views

- [ ] 5.1 The board's JSON `time` carries the team-or-kit share, and a band draws a head line holding one (design, Decision 6; Task notes 5.1). Passes `tests/py/test_board.py` (`tests/suite logic`), and `tests/suite mod` ends with "0 failed".

## 6. Docs and the run

- [ ] 6.1 README and the crew skill say the follower reads sluice only through the overview, and that a stay crew can't split shows as team or kit (Task notes 6.1). `tests/suite t-docs` ends with "0 failed".
- [ ] 6.2 `tests/moon.yml` is in step with the tests' reads, and the tests the change affects pass (Task notes 6.2). `tests/suite --affected` ends with "0 failed".
