# Tasks

## 1. Every entry is pushed as it is written

- [x] 1.1 `record.unpushed` gives the host's entries the branch lacks, oldest first, each with its day file as it stands once added, and `record.entry_message` gives each its own commit message naming it (design, Decisions 2 and 4; Task notes 1.1); passes `tests/py/test_record.py` in the logic tier, `tests/suite logic`.
- [x] 1.2 `plan.land` commits a chain of entries one on another, checks each file, pushes the last without force and replays the whole chain on a moved tip (design, Decision 3; Task notes 1.2); passes `tests/contract/test_record.py`, `tests/suite contract`.
- [x] 1.3 `record.emit` pushes through `record.reach` before it returns, and a push that fails is said once on standard error and changes nothing the command does, the logic tier standing in for `reach` (design, Decisions 1, 4 and 8; Task notes 1.3); passes `tests/py/test_record.py` and `tests/suite t-journey-state`.

## 2. A write carries nothing

- [x] 2.1 A plan write commits only its own files and its entry follows as its own commit; a missed entry goes with the host's next, and `crew events --push` pushes what is left or says nothing is (design, Decisions 4 and 5; Task notes 2.1); passes `tests/suite t-journey-state`.

## 3. The record is read from the branch alone

- [ ] 3.1 `record.gather` reads the branch alone and names only the branch when it cannot read it, `hosts_of` and the per-host read gone (design, Decision 6; Task notes 3.1); passes `tests/py/test_record.py`, `tests/suite logic`.
- [ ] 3.2 The batch clock, a review, the landing's guard and the rail refuse or hold back only when the branch cannot be read, and a silent host hides no card's close (design, Decision 6; Task notes 3.2); passes `tests/py/test_batches.py`, `tests/py/test_rail.py` and `tests/py/test_landing.py` in `tests/suite logic`, and `tests/suite t-journey-review`.
- [ ] 3.3 The board names a host for its kits alone, never for its run record (design, Decision 6; Task notes 3.3); passes `tests/py/test_board.py` in `tests/suite logic` and `tests/suite t-journey-board`.
- [ ] 3.4 The page names the branch it read and no host for its record (design, Decision 6; Task notes 3.4); passes `tests/py/test_page.py`, `tests/suite logic`.
- [x] 3.5 `crew events --follow` follows the branch every five seconds and starts nothing on any host (design, Decision 7; Task notes 3.5); passes `tests/py/test_record.py` in `tests/suite logic` and `tests/suite t-journey-state`.

## 4. What the docs say

- [ ] 4.1 README, the crew skill, `crew`'s usage header, `record.py`'s usage and the operator's brief say the record is read from the partition's branch, each entry pushed as it is written (design, Task notes 4.1); passes `tests/suite t-docs t-briefs`.

## 5. The affected tests

- [ ] 5.1 After `tests/moon-tasks` is run and `tests/moon.yml` committed for any test whose reads changed, `tests/suite --affected` ends with "0 failed".
