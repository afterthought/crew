# Tasks

## 1. The partition links follow the page's own file

- [x] 1.1 The header links each other partition in the layout of the page's file, `../<other>/page.html` in crew's, `<other>.html` beside a page written as `<label>.html`, both swapped when both are, and names it unlinked when neither names the partition (design, *The links follow the layout of the page's own file*; Task notes 1.1); passes `tests/py/test_page.py`, `tests/suite logic` ends with "0 failed".
- [x] 1.2 `crew page` draws the links from the path it writes, and prints that the other partitions are not linked when its file and folder are not named for the partition (design, *A page whose layout names no partition links none and says so*; Task notes 1.2); Verify `tests/suite logic t-journey-board` ends with "0 failed".
- [x] 1.3 README, crew's usage and the crew skill say where the partition links point, the usage's `crew page` line unchanged (design, *Context*; Task notes 1.3); Verify `tests/suite t-docs` ends with "0 failed".

## 2. Integration

- [ ] 2.1 The tests the change affects pass; Verify `tests/suite --affected` ends with "0 failed".
