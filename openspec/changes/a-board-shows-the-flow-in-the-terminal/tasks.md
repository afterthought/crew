# Tasks

## 1. The read the board needs

- [x] 1.1 Asked for the board, gather.py answers each team's slots and each kit's explorations on main beside what it answers now, and `tests/t-sites.sh` and `tests/t-reads-once.sh` still pass (design: *One read, two renderings*; Task notes 1.1; `read.2`, `code.1`).
- [x] 1.2 `survey` can make the board's read, `rail_record` also gives the landings and gives it reads, and the rail's text is made from a read it is handed, with `tests/t-rail.sh` passing untouched (design: *One read, two renderings*; Task notes 1.2; `plan.12`).

## 2. crew board

- [x] 2.1 One flow read of a partition gives the board's data: its four lanes, every rail row as a marker on its object with its card, and the attention line, in the fields of *The JSON* (design: *What each lane reads*, *Markers*, *The JSON*; Task notes 2.1; `read.1`, `read.3`).
- [x] 2.2 The board's text prints the header, the four lanes in order and the attention line, one object to a line with its marker in the gutter, cut to the terminal's width and plain under `NO_COLOR` or a pipe (design: *The text*; Task notes 2.2).
- [x] 2.3 `crew board [--label L] [--json]` prints the board or its JSON, makes no reading folder, and is in the usage header, README and SKILL.md, with `tests/t-docs.sh` passing (design: *The command*; Task notes 2.3; `code.2`, `docs.2`).
- [x] 2.4 `tests/t-board.sh` passes, proving each requirement of the `crew-board` delta but the last, that the board prints no answering command and writes nothing, and `tests/moon.yml` is regenerated (Task notes 2.4; `state.4`, `tests.2`).

## 3. The board tab

- [x] 3.1 The rail tab's loop makes one read each refresh, prints the rail from it as `crew rail` prints it, and writes the board's frame whole for the board tab (design: *The rail tab's loop hands the board to the board tab*; Task notes 3.1; `state.4`).
- [x] 3.2 `crew operator up` opens one `board` tab after `rail` that draws the latest frame at its own width, says how old a stale frame is, and says how to open both tabs afresh when there is none (design: *The rail tab's loop hands the board to the board tab*; Task notes 3.2; `roles.4`).
- [x] 3.3 `tests/t-board.sh` proves one read serves both tabs and the board tab's three states, `tests/t-record-team.sh` proves the tab is opened once, and README and `_open.md` say the board is drawn (Task notes 3.3; `tests.2`, `docs.2`).
- [x] 3.4 `tests/suite t-board t-rail t-record-team t-reads-once t-sites t-bolts t-docs` ends with "0 failed" (Task notes 3.4).
