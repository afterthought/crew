---
number: 10
title: A board shows the flow, read from state, in the terminal first
status: accepted
date: 2026-10-07
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# A board shows the flow, read from state, in the terminal first

## Context and Problem Statement

Flywheel Next's board is the status view drawn by phase: four lanes, Inception, Bolt plan, Construction, Operation, every decision a marker on its object, nothing answered on the board, the whole a projection of state never written by hand (agentplot/blueprints `design/flywheel-next/surfaces.md` S10 to S18; requirements 141, 142, 209). crew has the rail (record 0002) and its answering surface (record 0005), and the user asked whether the board can be approximated over crew's state, and what it would look like in the terminal (`openspec/explorations/board-from-crew-state/reading.md`). The reading found three of four lanes already derivable from the reads `crew rail` and `crew bolts` make, the fourth thin until curation lands; the user's word was "send this to crew".

## Considered Options

* `crew board`, a read-only text view beside `crew rail`, Python standard library, stacked lanes, in its own tab, fed by the one kit read; a page later from its `--json`
* The page first, drawn by `page-of-the-flow` and opened in terminal-browser
* A full-screen terminal application (rich, textual, curses)

## Decision Outcome

Chosen option: the text board first (`state.4`: a view reads and never writes; `code.1`: the standard library only).

- **`crew board [--label L] [--json]`** prints the four lanes stacked, one object per line, from the plan, the proposals, the moves, the kits and the run record: Inception (unmoved signals by who captured them, open explorations, agenda items once they exist), Bolt plan (open proposals, planned bolts with no team, the queue), Construction (each held bolt as a ledger: its units with stages, fixes, the slot sessions, the sites), Operation (landings from the run record over the last seven days, the record's own window). A rail row is a marker on its object, never a row of its own; an open card's state rides the marker once cards exist; the board answers nothing. A host that did not answer, and a bolt whose every unit has landed but which is still in the plan, are the board's attention line.
- **One read, two renderings.** The board and the rail come from one kit read, which `a-command-reads-the-kits-once` makes possible; the operator workspace gets a `board` tab beside `rail`, refreshed by the same loop.
- **The page follows.** `page-of-the-flow` draws the lanes as a second view of its page from `crew board --json`, opened in terminal-browser; it borrows the mockup's forms, not its file.
- **Not now:** rich, textual or curses, which the devenv lacks and the answering, a paste into the rail's shell or a card, does not need.

Ordering is the planner's: after the kits-once read, after the rail's units, before the page.
