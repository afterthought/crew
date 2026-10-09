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
- **The page carries the deploys** (2026-10-09, the user: "I'd like to have a way to review recent deployments and release notes about what changed. Ideally, this would be an HTML page served on my network. It should have an intuitive timeline-based view ... browse back a couple of days. I also want to see the sequence of what I approved and didn't approve", signal 2026-10-09-swc-2-conductor-3572ecd8/01). Once `deploys-go-through-crew` records them, the page has a deploys view: a timeline by environment over the record's window, each deploy with the state it moved from and to, the bolts it carried and their changes' proposals as its release notes (record 0012 point 4), its checks and outcome, and the user's word on it as the card's answer recorded it, approved, declined or still waiting, so the sequence of what was approved and what was not reads off the timeline. The page is still one self-contained file read from the record; a `--since` names the window. Serving it on the network is the kit's, not crew's: swancloud regenerates it on the rail's cadence and serves it at a fleet name on the tailnet (swancloud record 0019).
- **The page is the board the user looks at** (2026-10-09, the user, through swancloud-operator-mac-studio: "How much work would it be to generate an HTML page every 30 seconds and have it served over my network so I can always open it from my Swift bar? That way, the board layout would look as close as possible to my flywheel mockups, so it looks pretty and it's easy to understand what bolt plans are waiting and what bolts are being built. I think I'd want to be able to switch between partitions, so I'd only see one partition at a time on a board, but I could switch between them. Within a partition I could toggle between teams as well"). The page's board view draws the four lanes of `crew board --json` in the mockup's phases-view forms and glyphs (`mockups/rail-and-board.html`, S12 to S18): lanes side by side on a desktop and stacked under 760 px as the phone is (requirement 307), light and dark, borrowing the mockup's lane styles and none of its seeded data, the page still one self-contained file. One page per partition, as one board per flywheel (235): its header names every partition in the teams file, and when the pages are served side by side each is one step from the others. A viewer narrows every lane to one team of the partition, and the choice survives a reload. The text board stays as the read the page draws from and as the operator workspace's tab; the page is where the user looks. Serving stays the kit's: swancloud regenerates each partition's page on the rail's cadence, every 30 seconds and on each run-record entry, which covers every deploy, serves the pages side by side at one fleet name on the tailnet, and opens the board from the SwiftBar menu (swancloud record 0019). Reading: `crew rail` takes 2.4 to 4.7 s per partition from mac-studio, the remote one slowest, so three partitions fit the cadence.
- **Not now:** rich, textual or curses, which the devenv lacks and the answering, a paste into the rail's shell or a card, does not need.

Ordering is the planner's: after the kits-once read, after the rail's units, before the page.
