# Tasks

## 1. A row taking main first stays on the card

- [x] 1.1 `card_rows` gives the rows a kit's landings card shows: those that can land and, beside them, those taking main first, but one an earlier send lands (design, Decision 1; Task notes 1.1). Passes `tests/py/test_landings.py` (`tests/suite logic`).
- [x] 1.2 `landings_step` reads a waiting card's rows, form and change note from `card_rows`, and an answered card's unticked row taking main first is no bolt the user left (design, Decisions 2 and 3; Task notes 1.2). Passes `tests/py/test_landings.py` (`tests/suite logic`).
- [x] 1.3 The raise records a row taking main first as `:main`, reads it back as the card's `taking`, and builds every card it posts or follows with from `card_rows`; a forecast that flips between raises holds the card to one request, changed in place (design, Decisions 1 to 3; Task notes 1.3). Passes `tests/py/test_landings.py` (`tests/suite logic`).
- [x] 1.4 `landings_card` shows a row taking main first as an unticked box saying why and what a tick does (design, Decision 1; Task notes 1.4). Passes `tests/py/test_cards.py` (`tests/suite logic`).

## 2. A tick on it stands

- [x] 2.1 `crew card read land/<kit>` leaves a ticked bolt with a conflict recorded at the head the card showed out of its submit only while the bolt stands there or has a conflict recorded at its head now (design, Decision 4; Task notes 1.5). Passes `tests/py/test_card_commands.py` (`tests/suite logic`).

## 3. The docs and the change's tests

- [x] 3.1 README and the crew skill say a row taking main first stays on the card unticked, and that its coming and going changes the card in place (`docs.2`). Verify `tests/suite t-docs` ends with "0 failed".
- [x] 3.2 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".
