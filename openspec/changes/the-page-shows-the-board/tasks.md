# Tasks

## 1. Whose each object is

- [x] 1.1 `crew board --json` lists each partition's teams and gives every object the teams it belongs to, by the table in the design, with the board's text and every existing check in `tests/t-board.sh` unchanged (design: *Whose each object is, decided in the board's read*; Task notes 1.1; `state.4`).

## 2. The board on the page

- [x] 2.1 `crew page <label>` embeds the partition's board read, the teams file's partitions and its label, with the lineage's labels read at the board's plan tip or both tips named, and a silent host is in the board's attention while the page is still written (design: *The page makes the board's read and embeds it*; Task notes 2.1; `read.1`, `read.3`, `record.1`).
- [x] 2.2 The page opens on a board view that draws the four lanes in the mockup's forms and markers, side by side on a desktop and stacked under 760 px, light and dark, with nothing fetched from outside the file and none of the mockup's sample data (design: *The board view, in the mockup's forms*; Task notes 2.2; `code.1`).
- [x] 2.3 A team chosen in the header narrows every lane but the attention strip and survives a reload, through the page's address and the browser, and the header links each other partition's page at `../<label>/page.html` (design: *The team control, and how the choice is kept*, *The partitions in the header*; Task notes 2.3).
- [ ] 2.4 README, SKILL.md and the usage header say the page opens on the board, narrows to a team and links the other partitions' pages, and `tests/t-docs.sh` passes (Task notes 2.4; `docs.2`).
- [ ] 2.5 `tests/moon.yml` is in step with the tests, and `tests/suite t-page t-board t-rail t-docs t-events t-reads-once` ends with "0 failed" (Task notes 2.5; `tests.5`).
