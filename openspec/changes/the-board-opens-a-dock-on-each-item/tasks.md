# Tasks

## 1. The dock pages

- [x] 1.1 Every item of the page's board and deploys, and every team, carries the key of a dock page `page.py` makes from the page's data and lineage alone, one key per item whichever lane or view draws it (design, Decisions 1 and 2; Task notes 1.1); passes `tests/py/test_page.py`, verify `tests/suite logic` ends with "0 failed".
- [x] 1.2 Each kind's dock page holds what the data and lineage hold of it, links only to items the page draws, and says an account or stage it cannot read as not known, never blank (design, Decisions 3 and 4; Task notes 1.2); passes `tests/py/test_page.py`, verify `tests/suite logic` ends with "0 failed".

## 2. The dock on the page

- [x] 2.1 The page draws the dock over the board in the mockup's forms, opened by a click or Enter on any item and on the strip's team pills, closed by Esc, × or a click outside, full screen under 760 px with its trail's back control, with no foot and nothing loaded (design, Decisions 5, 6 and 7; Task notes 2.1); passes `tests/py/test_page.py`, verify `tests/suite logic` ends with "0 failed".
- [x] 2.2 The open dock is kept in the page's address and reopened on a reload, a key the page no longer holds dropped (design, Decision 6; Task notes 2.2); passes `tests/py/test_page.py`, verify `tests/suite logic` ends with "0 failed".

## 3. Wiring and docs

- [x] 3.1 `crew page` writes the docks into the page, a held bolt's and a unit's with their history as `crew trace` prints it (design, Decision 1; Task notes 3.1); verify `tests/suite t-journey-board` ends with "0 failed".
- [x] 3.2 README and the crew skill say that a click on a board item opens its dock and that the strip names the teams (design, Context; Task notes 3.2); verify `tests/suite t-docs` ends with "0 failed".
- [x] 3.3 The tests the change affects pass: verify `tests/suite --affected` ends with "0 failed".
