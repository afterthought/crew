# Proposal

## Why

The rail says what waits on the user, but nothing in crew shows the whole flow at once: which signals have not been taken up, what is proposed and planned, what each team is building and how far, and what landed this week. The user asked whether Flywheel Next's board could be drawn over crew's own state; the reading found three of its four lanes already in what `crew rail` and `crew bolts` read, and record 0010 decided a text board in the terminal first, drawn from the same read as the rail, with JSON for the page to draw later.

## What Changes

- **`crew board [--label L] [--json]` prints the flow as four lanes stacked one above the other**, one object to a line, for each partition: *Inception* (the signals no move has taken, grouped by who captured them, and the explorations on each kit's main), *Bolt plan* (the open proposals, the planned bolts no team holds yet, and the queue), *Construction* (each bolt a team holds, as a ledger of its units with their stages and tasks, its fixes, the slot holding each, and the dev server running in each worktree), and *Operation* (the bolts landed in the last seven days, from the run record). It reads the plan, the proposals, the moves, the signals, the kits and the run record, and writes nothing.
- **Every rail row is a marker on its object, never a line of its own.** A proposal waiting on the user carries ✓ on its line in Bolt plan; a unit in review carries ✓ and a verify report the user hasn't answered carries ✎ on the unit's line in its ledger; a bolt waiting to land carries ✓ on its ledger's head. The marker says whether that row's Pending You card is open and who asked it. The board prints no command and answers nothing; the rail and its shell stay where things are answered.
- **The board names what needs attention at its foot, with !**: each host that did not answer, each plan it could not read, and each bolt whose every unit has landed but which is still in the plan, which today shows nowhere.
- **`--json` prints the same lanes as data**, every object with its partition, its team where it has one, and its markers, for the page that draws the board later (`page-of-the-flow`, `the-page-shows-the-board`).
- **The rail and the board come from one read.** The operator workspace gets a `board` tab beside `rail`. The rail tab's loop reads the plans, the kits and the run record once each time it refreshes, prints the rail as `crew rail` does, and hands the board's data to the board tab, which draws it at its own width. A board tab whose loop has stopped says how old its board is.

## Capabilities

### New Capabilities

- `crew-board`: the board of a partition's flow, its four lanes, its markers and its attention line, as text and as JSON, and the board tab drawn from the rail's read.

### Modified Capabilities

- `operator-agent`: `crew operator up` also opens a `board` tab beside `rail`, refreshed with it.

## Impact

- New command `crew board`; `crew rail`'s output does not change.
- The rail tab's loop reads a little more each refresh (the dev servers, the signals' second home, the explorations), so a refresh takes somewhat longer than `crew rail` alone.
- A rail tab opened before this lands keeps its old loop and draws no board; closing the operator workspace's rail tab and running `crew operator up <label>` again opens both afresh.
- The page (`page-of-the-flow`, `the-page-shows-the-board`) reads `crew board --json`; this change fixes its fields. Deploys in the Operation lane wait for `deploys-go-through-crew`, and agenda items in Inception for `curation-and-agenda`.

## Touches

```
plugin/lib/board.py
plugin/lib/plan.py
plugin/lib/gather.py
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
docs/architecture/_open.md
tests/t-board.sh
tests/t-record-team.sh
tests/moon.yml
openspec/specs/crew-board/spec.md
openspec/specs/operator-agent/spec.md
```

`plugin/lib/board.py` and `tests/t-board.sh` are new. `plan.py` changes in the rail's read (`rail_view`, `rail_record`) and `survey`; `gather.py` gains the slots and explorations it answers; `plugin/bin/crew` changes its usage header, `ensure_rail`, the `_rail` loop, and adds `board` and `_board`. `tests/moon.yml` is shared and regenerated for the new test. The two specs change by delta.
