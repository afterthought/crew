# Design

## Context

See proposal.md for why. This is the design of `openspec/changes/lineage-page`, approved by the user on 2026-10-03, read against crew as it stands on 2026-10-11. What exists:

- The run record: recutils entries with `Id`, `At`, `Host`, `By`, `Session`, `Act`, `On`, `From`, `Commit`, `Why`, `Refused` and a few act-specific fields, on each host and carried to `runs/<host>/<date>.rec` on the flywheel's branch (`record.4`). `On` and `From` hold typed names: `signals/<id>`, `proposal/<n>`, `unit/<unit>`, `bolt/<bolt>`, `queue/<kit>`, `team/<team>`, `agent/<name>`, `stage/<unit>/<stage>`, `fix/<bolt>/<name>`, `batch/<n>`, `report/<file>`, `proof/<file>`; `agenda/<n>` once `curation-and-agenda` is built.
- `plugin/lib/record.py` gathers entries (`gather`: the branch first, then each reachable host's uncarried tail, and what did not answer) for `crew events`, and walks `On` and `From` for `crew trace` (`trace`, inline today): start from an object, add entries naming an object in the set, add the objects those entries came from and the objects that came from them, never follow `agent/`, `team/`, `queue/` or `plan/` names, never take a `unit.move`'s `From` bolt as an origin, and follow a proposal forward only when the trace starts there.
- The flywheel's state on its branch: `plan.rec` (bolts with goals and teams, units with intents), `proposals.rec` (cases, states), signals under `signals/` there and in the blueprints (`plan.signal_text` reads a signal's assertion from either home), and `agenda.rec` once `curation-and-agenda` is built, read through crew's git caches.
- The operator agent opens pages in terminal-browser beside its pane on a Mac, for dev servers (the operator brief's `{{SHOWING}}`, `crew.py`).
- `crew board` (`board.py`) reads the same state for its lanes; record 0010 has later units draw it, and the deploys, as further views of this page.

The findings-to-design proposal compared views (its section 4): text first; this page second; a zoetrope provider not planned, because zoetrope's nodes are agents; entries written as Claude-format transcripts rejected.

Rules this rests on: `state.4` (a view computed from files, nothing written), `record.1` (a pure read appends no entry), `record.3` (labels come from the state, never from entries), `read.1` and `read.3` (what could not be read is named), `code.1` (standard library only), `code.2` (refusals), `docs.2` (README, SKILL.md and usage together), `tests.2` and `tests.6`, `briefs.1` (the operator agent writes nothing: crew writes the file, the agent opens it). Pages touched: `record.md`, `briefs.md`, `tests.md`, `docs.md`. `read.5`, proposed, would have the record read from the branch alone; the page takes what could not be read from `gather`, so it follows that change with nothing of its own to change.

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
- The board and deploys views of record 0010, which later units add.

## Decisions

### Data: entries decide, state labels

`page.py` asks `record.py` for the flywheel's entries (all, or from `--since`) and builds:

- **nodes**: every object named in an `On` or `From` whose kind is `signals`, `agenda`, `proposal`, `unit` or `bolt`;
- **edges**: for each entry, the objects of those kinds it names, in `On` and `From`, are joined in the flow's order: each object to the objects of the next column the entry names, so a `signal.move` joins its signal to its item, a `unit.add` from an approval joins its item to its proposal, its proposal to its unit and its unit to its bolt, and no line skips a column the entry also names. The walk's exceptions hold: a `unit.move`'s `From` bolt is where the unit was, and draws no line. An edge is kept once, with the entries that made it;
- **history** per node: the entries `crew trace <node>` would print, computed with the same walk, exported from `record.py` as one function both use.

Then it reads the state once, at the commit the entries were read from, for labels and present status: a signal's assertion; an item's subject, lane and state; a proposal's first line of case and state; a unit's intent and stage (the stage from the read `crew bolts --json` makes, when hosts answer); a bolt's goal, team and state. A node the state no longer holds (a landed bolt's units are removed from the plan) keeps its name and is labelled from its entries' `Why`.

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

Default `~/.local/state/crew/<label>/page.html`; `--out <file>` elsewhere. The file is written whole and moved into place, so a reader never sees half of it. `crew page` runs on whatever host it is typed on, since everything it reads comes from the state repository and from hosts over ssh, as `crew events` does. It prints the path and the header line. It appends no entry to the run record (`record.1`). When the flywheel's branch cannot be read it writes nothing and names the branch (`read.1`): the page names the commit it was made from, and every label comes from there.

The operator agent's brief gains: when the user wants to see the flow, run `crew page <label>` and open the file in terminal-browser beside the pane, as it opens a dev server; say as of when it is.

### Checked against the trace

A test builds the page's data for a fixture run record and asserts, for every node, that its history equals `crew trace`'s output for that object. This is what "the page and the trace cannot disagree" means in practice, and why both use one function.

### What must not break

`crew events` and `crew trace` print what they print today; `record.py` gains an exported function and loses none.

## Risks / Trade-offs

- [A long-lived flywheel has thousands of nodes] → `--since`, the hide-closed filter and the name box; the data is embedded once, and histories are lists of entry ids into one table.
- [The page goes stale the moment it is written] → it says when it was made; making it again is one command.
- [Labels read from the state show typed text (intents, assertions)] → the file is local and uncommitted; the same text is already in the state repository. It is escaped where it is drawn.
- [Layout code in hand-written JavaScript is fiddly] → columns and straight or single-bend lines only; no force layout, no library.
- [`curation-and-agenda` also touches `record.py`'s kinds] → this change adds `agenda/` to the kinds a trace takes whole; the later change finds it there.

## Migration Plan

None. Pull crew on every host; the command exists. Rollback is reverting the commit; a leftover `page.html` under `~/.local/state/crew/<label>/` can be removed.

## Proof in dev

None: crew has no dev environment, and the bolt's proof is its verification.

## Proof on real work

Once the bolt has landed and every host has pulled:

1. Ask the operator agent on mac-studio to show the flow of a partition whose signals have been routed into units (wldn once `curation-and-agenda`'s proof has run; swancloud's signals routed with `crew signal move` until then). The page opens beside its pane in terminal-browser, with nothing fetched from the network; each routed signal shows a line to its unit; selecting a unit marks its whole chain and lists the same entries `crew trace unit/<unit>` prints; and the header names the time and the commit, and the agent says them.
2. Make the page with the box unreachable from the Mac. It is written, complete as far as the box had carried, and names the box.

## Task notes

### 1.1

Move the walk out of `trace` into one function, `lineage(entries, start)`, returning the chosen entries sorted by time then `Id`, with every rule `trace` has today: `names`, `UNFOLLOWED`, the `unit.move` bolt exception, and following a proposal forward only from the start. `trace` resolves a bare name as now, then calls it and prints. Add `agenda/` to `KINDS`, so `crew trace agenda/<n>` is taken whole. `tests/t-events.sh` and every other test that runs `crew trace` pass unchanged; add one line to `t-events.sh` for `crew trace agenda/<n>`.

### 1.2

`page.py`: `data(entries, since)` → `{"nodes", "edges", "entries", "histories"}`, where `entries` is one table by `Id` and each history is a list of ids. The five kinds in column order are `signals/`, `agenda/`, `proposal/`, `unit/`, `bolt/`. Edges as *Data* says: per entry, the named objects of the five kinds in column order, each joined to the objects of the next column present in that entry, a `unit.move`'s `From` bolt left out. Without `--since`, read everything, as `trace` does (`"0000-00-00"`), not `when()`'s seven days; with it, take `when(--since)` and keep only entries at or after its stamp, histories included. The fixture in `tests/t-page.sh` emits, with `record.py emit`: a capture of `signals/a`, a `signal.move` of it to `agenda/8`, a `plan.propose` of `proposal/3` naming `unit/u` and `bolt/b`, the approval's `unit.add` of `unit/u` to `bolt/b` from `agenda/8` and `proposal/3`, a `bolt.land` of `bolt/b`, and a capture of `signals/z` that nothing moves: five linked nodes, four edges, and `signals/z` with none.

### 1.3

In `tests/t-page.sh`, for every node of the fixture's data, the ids of its history equal the ids, in order, of the entries `crew trace <node>` prints; compare by making `page.py` print its data as JSON (a hidden `--json`, or `python3 page.py data`), and `crew trace`'s lines by their time and act, or by exposing ids the same way. Pick whichever keeps `crew trace`'s output unchanged.

### 1.4

Read entries and labels at one commit: learn the tip `gather` read each branch at (a function beside `on_branch`, or `gather` returning it to callers that ask, with `crew events` printing what it prints today), and read `plan.rec`, `proposals.rec`, `agenda.rec` when present, and signals through `plan.signal_text`, at that tip. A unit's stage comes from the read `crew bolts --json` makes; a host that does not answer leaves its units' stages blank and is already in what `gather` names. A node the state no longer holds is labelled from the `Why` of its newest entry. Test against the stub state remote, with a bolt landed and its units gone from `plan.rec`.

### 2.1

`plugin/lib/page.html`: one placeholder the data replaces, as JSON inside `<script type="application/json">` with `</` escaped. Every label is set as text, never as HTML. No `src=`, `href=` or `url(` reaching outside the file. Five columns with counts; lines between linked nodes; selection marking the closure over edges both ways, dimming the rest, listing the history (time, act, who, host, commit, refusal, `zoe <session>` and host as selectable text) and marking the timeline's days; the hide-closed filter, on by default above about forty nodes; the name box; `prefers-color-scheme` for light and dark. `tests/t-page.sh` checks the file holds the data block, no `<script src`, no `<link`, and no `http://` or `https://` outside the data; how it renders is the first proof on real work.

### 2.2

`crew page <label> [--out <file>] [--since <time>]` in `plugin/bin/crew`, dispatched to `page.py` as `events | trace` are to `record.py`, and refusing an unknown label as they do. Write to a temporary file in the target's folder and rename it into place; make `~/.local/state/crew/<label>/` if missing. Print the path, then the header line: `as of <UTC time> · <label>/main <short sha>`, then each host that did not answer. An empty record writes a page saying nothing has been recorded. When the branch cannot be read, refuse with `fail()` naming `<label>/main` and leave any earlier page as it was. Test with the stubs: a host made unreachable through `$T/down`, as `t-events.sh` does, and the state remote made unfetchable.

### 2.3

README's "Seeing what happened": `crew page <label> [--out <file>] [--since <time>]` in its command block and a paragraph saying what the page shows, where it is written, that it is read from the record alone, and that nothing reads it. The same line in the usage header beside `events` and `trace`, and in `plugin/skills/crew/SKILL.md`. `tests/t-docs.sh` passes.

### 3.1

`plugin/roles/operator.md`, beside the `trace` paragraph: when the user wants to see how work flowed, run `{{TEAM_CMD}} page {{LABEL}}`, open the file it prints in terminal-browser beside the pane (on a Mac, as `{{SHOWING}}` has it for sites; on the box, give the path and say it opens from a Mac with the file copied there), and say as of when it is and any host it could not read. Pin the paragraph with a phrase in `tests/t-briefs.sh` (`tests.6`); `tests/t-operator.sh`'s check that the brief prints for `wldn` with no unfilled token passes.

### 3.2

After adding `tests/t-page.sh`, run `tests/moon-tasks` and commit `tests/moon.yml`. Then `tests/suite t-page t-events t-briefs t-operator t-docs t-record t-capture t-amend-intent t-stage-ends` ends with "0 failed".
