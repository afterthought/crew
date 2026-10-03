# Design

## Context

See proposal.md for why. What exists:

- The run record: recutils entries with `Id`, `At`, `Host`, `By`, `Session`, `Act`, `On`, `From`, `Commit`, `Why`, `Refused` and a few act-specific fields, on each host and carried to `runs/<host>/<date>.rec` on the flywheel's branch. `On` and `From` hold typed names: `signals/<id>`, `agenda/<n>`, `proposal/<n>`, `unit/<unit>`, `bolt/<bolt>`, `queue/<kit>`, `team/<team>`, `agent/<name>`, `stage/<unit>/<stage>`, `fix/<bolt>/<name>`, `batch/<id>`.
- `plugin/lib/record.py` gathers entries (the branch first, then each reachable host's uncarried tail) for `crew events`, and walks `On` and `From` for `crew trace`: start from an object, add entries naming an object in the set, add the objects those entries came from and the objects that came from them, and never follow `agent/`, `team/`, `queue/` or `plan/` names.
- The flywheel's state on its branch: `plan.rec` (bolts with goals, units with intents), `agenda.rec` (items with subjects, lanes and states), `proposals.rec` (cases, states), and signals in the state and in the blueprints, read through crew's git caches.
- The operator agent opens pages in terminal-browser beside its pane (the operator brief, for dev servers).

The findings-to-design proposal compared views (its section 4): text first; this page second; a zoetrope provider not planned, because zoetrope's nodes are agents; entries written as Claude-format transcripts rejected.

## Goals / Non-Goals

**Goals:**
- A person sees the lineage of work at a glance and can drill into any object's history.
- The page is a projection: nothing in crew reads it, and deleting it loses nothing.
- It cannot disagree with `crew trace`.

**Non-Goals:**
- A live page. It is made on request and says when; `crew events --follow` is the live view.
- A server, a build step, or any dependency fetched at view time.
- Showing agents as nodes, or team lifecycle (`agent.*`, `team.*`, `tell`). Those are in an object's history where they name it, and in `crew events`.
- Editing anything from the page.

## Decisions

### Data: entries decide, state labels

`page.py` asks `record.py` for the flywheel's entries (all, or from `--since`) and builds:

- **nodes**: every object named in an `On` or `From` whose kind is `signals`, `agenda`, `proposal`, `unit` or `bolt`;
- **edges**: for each entry, from each `From` object to each `On` object of those kinds, and between the `On` objects of one entry where one contains the other in the flow's order (a `signal.move` joins its signal to its item; a `unit.add` joins its unit to its bolt). An edge is kept once, with the entries that made it;
- **history** per node: the entries `crew trace <node>` would print, computed with the same walk, exported from `record.py` as one function both use.

Then it reads the state once for labels and present status: a signal's assertion and kind; an item's subject, lane and state; a proposal's first line of case and state; a unit's intent and stage (from `crew bolts --json`, when hosts answer); a bolt's goal, team and state. A node the state no longer holds (a landed bolt's units are removed from the plan) keeps its name and is labelled from its entries' `Why`.

*Alternative:* build the graph from the state files. Rejected: the state holds only what is, and the page is about what happened; and invariant 19 of the findings-to-design brief wants views to be over the events.

### The file

One HTML file: a `<script type="application/json">` block with nodes, edges, histories and the header facts; inline CSS; inline vanilla JavaScript; an inline SVG the script lays out. No font, script or style is loaded from anywhere. It follows the viewer's light or dark preference.

Layout:

```
 as of 2026-10-09 14:02Z · wldn/main 4119bf2 · mac-studio did not answer
 ┌ Signals ──┐ ┌ Agenda ───┐ ┌ Proposals ┐ ┌ Units ────┐ ┌ Bolts ────┐
 │ ▪ …       │─│ 8 plan    │─│ 3 approved│─│ cfn-nag…  │─│ cfn-checks│
 │ ▪ …       │─│ 7 design  │ │           │ │ devenv-…  │ │ smoke-2   │
 └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘
 timeline ▁▂▁▁▅▂▁▁▁▃▁
 ┌ selected: unit cfn-nag-security-check ─────────────────────────────┐
 │ 10-06 14:02  plan.propose  wldn-planner  chuck-herdr-alpha  4119bf2 │
 │ 10-06 14:10  plan.approve  wldn-planner  …   zoe 7be1…              │
 └─────────────────────────────────────────────────────────────────────┘
```

- Nodes are ordered within a column by the time of their first entry, newest first, and coloured by state (open, in flight, done, dropped). Signals with no move sit in their column unlinked; a count heads each column.
- Selecting a node marks its ancestors and descendants (the closure over edges), dims the rest, lists its history beneath, and marks its entries on the timeline. The timeline is entries per day, as bars.
- A filter hides closed and landed work, on by default once there are more than a few dozen nodes, and a text box narrows by name.
- Each history line shows `zoe <session id>` and the host as copyable text; the page cannot open a terminal.

The template lives beside `page.py` as one file with a placeholder for the data, so the page can be restyled without touching the code that builds the data.

### Where it is written, and how it is opened

Default `~/.local/state/crew/<label>/page.html`; `--out <file>` elsewhere. `crew page` runs on whatever host it is typed on, since everything it reads comes from the state repository and from hosts over ssh, as `crew events` does. It prints the path and the header line.

The operator agent's brief gains: when the user wants to see the flow, run `crew page <label>` and open the file in terminal-browser beside the pane, as it opens a dev server; say as of when it is.

### Checked against the trace

A test builds the page's data for a fixture run record and asserts, for every node, that its history equals `crew trace`'s output for that object. This is what "the page and the trace cannot disagree" means in practice, and why both use one function.

### What must not break

`crew events` and `crew trace` are unchanged; `record.py` gains an exported function and loses none.

## Risks / Trade-offs

- [A long-lived flywheel has thousands of nodes] → `--since`, the hide-closed filter and the name box; the data is embedded once, and histories are lists of entry ids into one table.
- [The page goes stale the moment it is written] → it says when it was made; making it again is one command.
- [Labels read from the state show typed text (intents, assertions)] → the file is local and uncommitted; the same text is already in the state repository.
- [Layout code in hand-written JavaScript is fiddly] → columns and straight or single-bend lines only; no force layout, no library.

## Migration Plan

None. Pull crew; the command exists. Rollback is reverting the commit.
