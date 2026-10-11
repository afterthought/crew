# Tasks

## 1. The data

- [x] 1.1 `record.py` exports the lineage walk as one function that `crew trace` calls, takes `agenda/` names whole, and every existing trace test passes unchanged (design: *Data: entries decide, state labels*, *What must not break*; Task notes 1.1).
- [x] 1.2 `page.py` builds nodes, edges and per-node histories from the gathered entries for the five kinds, with `--since`, and the fixture gives five linked nodes, four edges and an unmoved signal with none (design: *Data: entries decide, state labels*; Task notes 1.2; `state.4`).
- [x] 1.3 For every node of the fixture, the page's history holds the entries `crew trace` prints for it, in the same order (design: *Checked against the trace*; Task notes 1.3).
- [x] 1.4 Every node carries its label and present status from the state at the commit its entries were read at, a node the state no longer holds is labelled from its entries, and a unit's stage is blank when its host does not answer (design: *Data: entries decide, state labels*; Task notes 1.4; `record.3`, `read.3`).

## 2. The page

- [x] 2.1 The template draws the five columns with their counts and lines, the selection with its history, the timeline, the filter and name box, in light and dark, from data inside the file and nothing outside it (design: *The file*; Task notes 2.1; `code.1`).
- [x] 2.2 `crew page <label> [--out <file>] [--since <time>]` writes the page whole, prints its path and header line, writes a page for an empty record, names a host that did not answer, and refuses with nothing written when the branch cannot be read (design: *Where it is written, and how it is opened*; Task notes 2.2; `read.1`, `record.1`, `code.2`).
- [x] 2.3 README, SKILL.md and the usage header say what `crew page` does, and `tests/t-docs.sh` passes (Task notes 2.3; `docs.2`).

## 3. The operator agent, and the suite

- [ ] 3.1 The operator brief has the agent make the page on request, open it beside its pane, and say as of when it is and any host it could not read, pinned in `tests/t-briefs.sh` (design: *Where it is written, and how it is opened*; Task notes 3.1; `briefs.1`, `tests.6`).
- [ ] 3.2 `tests/moon.yml` is regenerated for `tests/t-page.sh`, and the tests this change affects end with "0 failed" (Task notes 3.2; `tests.2`).
