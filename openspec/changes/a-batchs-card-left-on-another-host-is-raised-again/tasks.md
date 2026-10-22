# Tasks

## 1. crew can tell which copy of a key's card the main level's host can't reach

- [x] 1.1 `cards.stranded` names the owner's newest card under a key when it was posted from another host and is still open, or was closed as lost, and nothing otherwise, and its logic-tier cases pass in `tests/suite logic` (design: *One decision says which copy*; Task notes 1.1; `code.7`).

## 2. The rail's next read on the main level's host raises such a batch's card again

- [x] 2.1 The rail's sweep on the main level's host posts again, through the batch's raise, each batch whose card it can't reach, reports the older card as lost and the new one posted, and leaves the batch's row out of the rows with no card (design: *The rail's sweep on the main level's host*; Task notes 2.1; `briefs.12`, `read.1`).
- [x] 2.2 A batch raised again because of an older copy says on its card's summary that the older copy was lost and to dismiss it in the app (design: *The raise posts with the dead-copy summary*; Task notes 2.2; `briefs.13`).
- [x] 2.3 `tests/py/test_rail.py` and `tests/py/test_cards.py` prove a card held on another host and one lost there raised again on the main level's host alone, a proposal's left alone, the dead-copy summary and the sweep's report, and `tests/suite logic` ends with "0 failed" (Task notes 2.3).

## 3. A batch whose session the user sends is read, with or without its card

- [x] 3.1 `crew card wait batch/<n>` records crew's close of the batch, in the planner's name with what was read, whenever the session's send closes no card on the main level's host (design: *A session sent records the batch read*; Task notes 3.1; `briefs.12`, `roles.2`).
- [x] 3.2 A batch closed so is closed for the rail, the landing rows and the batch's raise until a newer card is posted under its key, proved in `tests/py/test_batches.py`, `tests/py/test_cards.py` and `tests/py/test_rail.py` with `tests/suite logic` ending "0 failed" (design: *`batch_closed` reads crew's close of a batch*; Task notes 3.2).
- [x] 3.3 `tests/t-cards.sh` proves the planner's wait on a session sent with no card, and with a card whose close is refused, records the batch read, and `tests/suite t-cards` ends with "0 failed" (Task notes 3.3).

## 4. The docs say so

- [ ] 4.1 README, the crew skill and `crew`'s usage header say a batch's card the main level's host can't reach is posted again there, and a session sent records the batch read with no card closed, and `tests/suite --affected` ends with "0 failed" (Task notes 4.1; `docs.2`).
