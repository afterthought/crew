# Tasks

## 1. The decisions

- [x] 1.1 Whether a kit's policy at a head declares `[preview]` is read by a function of its text, refusing what is not TOML; proved by new cases in `tests/py/test_kit.py` (design, *Decisions* 1 and *Task notes* 1.1).
- [x] 1.2 What crew does with a bolt's preview at each raise, what change note a preview's end puts on the card, and which entry of sluice's list is the head's are functions of facts; proved by new cases in `tests/py/test_landing.py` (design, *Decisions* 3, 5 and *Task notes* 1.2).

## 2. The card

- [x] 2.1 A landing card built with a preview lists its addresses beside the reading, says it lands nothing, says a preview that failed or was not named, keeps its face within eight artifacts, and one built without is as before; proved by cases in `tests/py/test_cards.py` (design, *Decisions* 4 and *Task notes* 2.1).
- [ ] 2.2 A landing card is raised with its preview asked for first when the kit declares one, and its close releases the preview crew recorded; proved by cases with the acts' stand-in in `tests/py/test_cards.py` (design, *Decisions* 2, 3, 6 and *Task notes* 2.2).

## 3. The handed ask and the sweep

- [ ] 3.1 `crew _preview` waits on sluice's preview in a process of its own, records its outcome, and changes the open card in place when the outcome changes what the card says while it waits on the user; proved by `tests/t-journey-land.sh` with the stub's failure switch (design, *Decisions* 5 and *Task notes* 3.1, 5.1).
- [ ] 3.2 The rail's card sweep releases each preview crew recorded whose landing card is judged dead; proved by a case beside the sweep's judgment cases in `tests/py/` (design, *Decisions* 6 and *Task notes* 3.2).

## 4. The words

- [ ] 4.1 The conductor's brief and README say the landing card lists a preview's addresses, which crew asks for, replaces and releases, and which lands nothing; proved by `tests/t-briefs.sh` and `tests/t-docs.sh` (design, *Task notes* 4.1).

## 5. The journey

- [ ] 5.1 On the stubs, a landing card in a kit declaring a preview lists its address, a fix releases it and the card raised again lists the new head's, and the landing releases the last; proved by `tests/t-journey-land.sh` with `tests/stubs/sluice` answering previews (design, *Task notes* 5.1).

## 6. Checks

- [ ] 6.1 The logic tier and the end-to-end tests this change affects are green (design, *Task notes* 6.1).
