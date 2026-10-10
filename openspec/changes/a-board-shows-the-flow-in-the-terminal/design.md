# Design

## Context

What the board is and why is record 0010 (`docs/adr/0010-a-board-shows-the-flow-read-from-state.md`); what it was drawn from is the reading (`openspec/explorations/board-from-crew-state/reading.md`); the lanes, the markers and the rule that nothing is answered on the board come from Flywheel Next's `design/flywheel-next/surfaces.md` S10 to S18 (agentplot/blueprints). The spec delta says what the board shows; this says how it is read and drawn.

What crew has today:

- **The rail's read** (`plan.py` `rail_view`): `plans()` fetches each flywheel's branch; `survey()` pipes `gather.py` once to each host holding a bolt; `open_proposals()` reads `proposals.rec` at the tip already fetched; `rail_record()` reads the run record once from 14 days back, or earlier for an old proposal, for proposal times and open cards; `rail_rows()` makes the four groups' rows, each with its group, label, card key and time; `stray_cards()` the open cards with no row. It prints, writing nothing.
- **The rest of what the lanes need is already read somewhere**: stages by `Stages` (`plan.py` 835), the ledger's shape by `bolts_view` (3363), the dev servers by `sites.py` (`survey(..., sites=True)` and `url_of`), signals and moves by `signal_at`, `capture_of`, `frontmatter` and `moves.rec`, landings as `bolt.land` entries naming `bolt/<bolt>` and each `unit/<unit>` (`bolt_land`, 1118), and the slots in `~/.local/state/<team>-team/slots` on the team's host, one line each: `<slot> <kind> <name> <place>` (`slot_stages`, 2809).
- **The rail tab** (`plugin/bin/crew` `_rail`, `ensure_rail`): a bash loop in the operator workspace's `rail` tab that clears the pane and prints `crew rail` every 30 seconds and on each run-record entry (`crew events --follow`), with a shell below it. A herdr pane shows only what its own process prints (`herdr pane --help`, 0.9.3: `send-text` and `run` type into a pane; nothing writes its output), so a second tab needs a process of its own.
- **The command's reading** (`a-command-reads-the-kits-once`, `plan.12`): within one Python process, `fetch()` and `survey()` keep what they read; a sites survey is neither served from nor kept in it.

Rules this design rests on: `state.4` (a view is computed from the files and the run record, nothing written), `plan.12` (one kit read and one fetch per command on each host), `read.1` (what can't be read is named, a stage unknown stays unknown), `read.2` (an absent field never becomes text), `read.3` (a host that does not answer is named and everything else still shown), `code.1` (the standard library only), `code.2` (refusals through `fail()`), `code.4` (names checked), `roles.4` (nothing typed into a pane but the tab's own command, as the rail tab does), `docs.2` (README, SKILL.md and the usage header together), `tests.1`, `tests.2`. Pages whose area this touches: `plan.md` (`plan.py`, `gather.py`), `teams.md` (`plugin/bin/crew`), `tests.md` (`tests/`), `docs.md` (`README.md`, `docs/`, `openspec/`).

## Goals / Non-Goals

**Goals:**

- `crew board` and `crew board --json` from one read of the plan, the proposals, the moves, the signals, the kits and the run record.
- The rail and the board from one read each time the rail tab refreshes, `crew rail`'s output unchanged.
- A `--json` whose fields the page can draw from without reading anything else.

**Non-Goals:**

- The page and its board view (`page-of-the-flow`, `the-page-shows-the-board`).
- Deploys in Operation (`deploys-go-through-crew`), agenda items and intents in Inception (`curation-and-agenda`), chores' shared lines (`chores-beside-units-and-fixes`).
- Whether a slot's agent is working or idle, which needs herdr on the team's host; the board says which slot holds the work, and `crew status` says how its agent is.
- The rail's own land group missing an all-landed bolt (the reading's "gap"): the board names it; the rail is not changed here.
- A full-screen terminal application (record 0010, "not now").

## Decisions

### A module of its own, beside sites.py

`plugin/lib/board.py` holds the board: its read, its data, its text, and the tab's follower, importing `plan`, `sites` and `record` as `sites.py` imports `plan`. `plan.py` is 4,000 lines and the board adds nothing to the plan; what the board needs from the rail, `plan.py` exposes by splitting `rail_view` into its read and its text.

Alternative: the board in `plan.py` beside `rail_view`. Rejected for size only; nothing else differs.

### One read, two renderings

A **flow read** is everything one refresh reads, for a list of partitions: the plans (`plans()`), a survey of every team of those partitions on every host they run on (each team's held bolt, or none), with the dev servers, the slots and the explorations; the open proposals at the tips already fetched; the run record, read once by `rail_record()`, which also returns the landings and gives it sees; the cards; and the rail's rows. The rail's text and the board's data are each made from it.

- `crew rail` keeps its own, narrower read (held teams only, no sites), so its cost and output do not change.
- The survey is a sites survey and so is neither served from nor kept in the command's reading (`plan.12`'s exception for `sites`); within the one process that makes the flow read it is made once. The rail's text from a flow read names only hosts that hold a bolt as not answering, which is what `crew rail` names, so the rail tab prints exactly what `crew rail` would.
- gather.py, piped from the asking host, answers the new fields itself; the board still reads them with `.get(..., [])`, so a missing field is none, never text (`read.2`).

Alternative: the board tab runs its own loop and its own read. Rejected by record 0010 ("one kit read, two renderings"): it doubles every refresh's cost, and the two tabs could disagree for a few seconds.

### The rail tab's loop hands the board to the board tab

Each refresh, the rail tab's loop runs `crew _views <label>`: one Python run that makes the flow read, prints the rail's text for the loop to show, and writes the board's data, as `crew board --json` prints it, to `~/.cache/crew/board/<label>.json` through a temporary file and `os.replace`, so it is only ever whole. The `board` tab runs `crew _board <label>`, a Python loop that looks at that file once a second and clears and draws the board whenever the file or its own pane's size changes.

The file is not state (`state.4`): it is one frame handed between two panes of the same loop, in crew's cache, read by nothing but the board tab, and losing it loses one redraw. It is held to `state.4` as the command's reading is (`a-command-reads-the-kits-once`, "not a service and not state"). The data, not the text, is handed over so that the board tab draws at its own width, and so that the frame is what `--json` prints.

- With no file, the board tab says that the rail tab's loop writes it and has not yet, and that a rail tab opened before `crew board` existed draws no board: close the operator workspace's `rail` tab and run `crew operator up <label>`.
- When the frame's `read_at` is more than 90 seconds old (three of the loop's periods), the board's header says how long ago it was read (`age()`), so a stopped loop is never taken for a live board (`read.1`).
- `crew _board <label> --once` draws one frame and exits, for the tests.

Alternatives: a named pipe from the loop to the tab (rejected: a write blocks or is lost without a reader, and a restarted board tab has nothing to show until the next refresh); the loop printing the board's text into a file (rejected: the rail pane's width is not the board pane's); one tab with the board above the rail (rejected by record 0010, a tab beside the rail).

### What each lane reads

- **Inception.** Signals: every `signals/<capture>/<NN>-<slug>.md` at the flywheel's tip, and on main of the partition's first blueprints repo (`signals.1`, the two homes), whose id has no `Move` in `moves.rec`; each grouped by its capture's `captured_by` (its `source` when it has none), each group with its count and its oldest capture's `at`, each signal with its frontmatter `kind` and its first body line, oldest first. The files are read with one `git cat-file --batch` per repository, since each refresh pays it. A blueprints repo that can't be fetched is an attention item, never "no signals" (`read.1`). Explorations: each folder under `openspec/explorations/` on `main` of each kit the partition's teams build, read by gather.py on the first host that answered for that kit, with the first non-blank line of the first `.md` file in name order, its leading `> ` dropped.
- **Bolt plan.** The open proposals (`open_proposals`); each bolt with no `Team`, with its units and their stages (ready, waiting or unknown, from `Stages`); the queue by repository (`plan.queue()`), as `bolts_view` gives it.
- **Construction.** Each bolt with a `Team`, in plan order: its units in plan order with `Stages.of` (stage, tasks), the slot whose line in its team's slots file names the unit (kind `unit`) or the fix's branch (kind `fix`), and the URL of the server running in its worktree by `sites.url_of`, shown only when there is one; its fixes from the kit's `fixes`; the bolt worktree's server at the foot. A host that did not answer leaves its ledgers with their units from the plan and their stages `unknown`.
- **Operation.** The `bolt.land` entries with no `Refused` from the last seven days of the run record already read (the record's own default window, `record.when`), newest first: the bolt from its `bolt/` object, its units from its `unit/` objects, `At` and `By`, and its team from the newest `bolt.give` entry naming the bolt in the same read, else none.

### Markers, and what the board does not print

Each row `rail_rows` makes is put on its object by its group and key: `proposals` on the proposal's line, `review` and `verify` on the unit's line in its ledger, `land` on the ledger's head line. The glyph is Flywheel Next's for the decision the row asks (S17): ✓ for an approval (a proposal, a review, a landing, which the user approves by holding the card's button), ✎ for an answer in the user's words (a verify report, answered by a tell). Each marker carries its card, open or not and who asked it, from the rail's cards. `!` marks attention: the head of a bolt whose every unit has landed and which is still in the plan (`Stages.bolt_state` is `landed`), and each item of the attention line. No row is printed as a line of its own and no command is printed (S17, S18): the rail and its shell are where things are answered.

The board shows no count of decisions (S10, S18). It does show Inception's curation counter, each captured-by group's count and its oldest (S13), which counts signals, not decisions.

### The text

One board per partition: a header line (`<label> board, as of HH:MM:SS, read from <hosts that answered>`), then the four lanes, each a bold heading and its objects indented under it, then `attention` with its items or `none`. A marker sits in a two-column gutter at the left of its object's line; its card is said at the line's end (`card open, asked by <agent>` or `no card open`). A repository is printed dim before a bolt's or a queued unit's name (S14). Each line is cut to the terminal's width (`shutil.get_terminal_size()`) when standard output is a terminal, and not otherwise. Bold and dim are left out when `NO_COLOR` is set or the output is not a terminal; the glyphs stay, being text.

### The JSON

`crew board --json` prints, and `_views` writes:

```
{"read_at": <ISO time>, "from": <host>, "partitions": [{
   "label": ..., "plan": <tip or null>, "hosts": {<host>: true | <why it did not answer>},
   "inception": {"signals": [{"signal", "home": "branch" | "blueprints", "captured_by", "at", "kind", "first"}],
                 "explorations": [{"kit", "name", "first"}]},
   "bolt_plan": {"proposals": [{"proposal", "by", "opened", "case", "waiting", "markers"}],
                 "planned": [{"bolt", "repo", "goal", "units": [{"unit", "stage"}]}],
                 "queue": [{"unit", "repo", "sources"}]},
   "construction": [{"bolt", "repo", "goal", "team", "host", "state", "url", "markers",
                     "units": [{"unit", "stage", "tasks", "slot", "worktree", "url", "markers"}],
                     "fixes": [{"fix", "merged", "slot", "worktree", "url"}]}],
   "operation": [{"bolt", "at", "by", "units", "team"}],
   "attention": [{"what": "host" | "plan" | "signals" | "landed", "name", "why"}]}],
 "unread": {<what>: <why>}}
```

A marker is `{"group", "key", "glyph", "at", "card": {"by", "host", "at"} | null}`, `at` being when its row began to wait. Every object of a ledger carries the ledger's `team` through its ledger; the page narrows lanes by it. A field crew cannot know is `null`, never omitted and never a guess.

### The command

`crew board [--label L] [--json]`: the partition named, else `CREW_LABEL`, else every partition (`default_label`), as `crew rail`. It is one Python run, exec'd by `plugin/bin/crew` with `crew rail`, `crew sites` and the rest that make no reading folder; `_views` and `_board` likewise. Like `crew rail`, it prints everything it could read and then exits non-zero naming each plan it could not.

## Risks / Trade-offs

- [Each rail-tab refresh now reads the dev servers, the signals' second home and the explorations, beyond what `crew rail` reads] → a refresh takes longer than `crew rail`'s 2.4 to 4.7 s by about a fetch and a few git calls per kit; it is measured in the proof below, and the loop's 30-second period is unchanged.
- [The frame file goes stale when the loop dies] → the board tab heads a frame older than 90 seconds with its age.
- [A rail tab opened before this lands runs the old loop and writes no frame] → the board tab says so and how to open both afresh.
- [An exploration has no "open" or "settled" mark today] → the board lists every exploration on each kit's main with its first line, which says what it is (`docs.1`); a rule for which explorations are open is the design agent's to make, and the board then filters by it.
- [The JSON's fields become the page's contract] → the page's units read these fields; a change to them is a change to this capability's spec.

## Migration Plan

Land, then pull on every host in one step. Nothing is stored between refreshes but the frame, which the next refresh replaces. A running rail tab keeps its old loop: close it and run `crew operator up <label>`, which opens the rail tab and the board tab afresh. Rollback: revert; a leftover `~/.cache/crew/board/` holds only frames and can be removed.

## Proof in dev

None: crew has no dev environment, and the bolt's proof is its verification.

## Proof on real work

Once the bolt has landed and every host has pulled:

1. `crew board --label swancloud` on mac-studio: every row `crew rail --label swancloud` lists is a marker on its object, Inception's unmoved signals match the signals with no move on `refs/crew/swancloud/main`, and the box is named if it does not answer.
2. In swancloud's operator workspace, close the `rail` tab and run `crew operator up swancloud`: a `board` tab opens after `rail`, and approving a unit from the rail's shell redraws both tabs within a few seconds.
3. The rail tab's refresh time with the board, beside `crew rail --label swancloud` alone, both timed on mac-studio.

## Task notes

### 1.1

`gather.py`: a request may set `"board": true`, and each kit may carry `"slots": {<team>: <path, ~ allowed>}`. With `board`, `kit()` adds `"slots": {<team>: [{"slot", "kind", "name", "place"}]}`, each file's non-blank lines split on whitespace into four fields (a missing file is `[]`, a line of another shape is skipped), and `"explorations": [{"name", "first"}]` from `git ls-tree --name-only main openspec/explorations/` and, for each folder, the first `.md` in `git ls-tree --name-only main openspec/explorations/<name>/` order read with `git show main:<path>`, its first non-blank line with a leading `> ` dropped. Update the module docstring, which `_open.md` also says is stale about `sites`.

### 1.2

`plan.py`: `survey(fleet, held, sites=False, board=False)`, `board` implying `sites` and asking gather.py for `board` with each kit's `slots` for every team that builds it on that host, built as `reports` is. `rail_record` also returns `landings` (each `bolt.land` entry not refused, as `{label, bolt, units, at, by, host}`) and `gives` (`{(label, bolt): team}` from the newest `bolt.give` entry naming each bolt); its callers take the extra values. Split `rail_view` into a read and `rail_text(fleet, labels, read, now)`, the text exactly as printed today; `rail_text` names a host as not answering only when it holds a bolt of the plans read. `crew rail`'s output must not change: `tests/t-rail.sh` passes untouched.

### 2.1

`board.py` `flow_read(fleet, labels)`: `plans` with errors, `survey(..., board=True)` over `[(t, bolt held by t or None) for every team of the labels]`, `open_proposals` with `found`, `rail_record`, `rail_rows`, and the signals of each label (Decisions, *What each lane reads*; `fetch(srepo, "main")` for the blueprints home, its failure kept for the attention line). `board_data(fleet, labels, read, now)` builds the JSON of *The JSON* from it. Markers: index `rows` by `(label, group, object)`, the object being `proposal/<n>`, the unit, or the bolt (from the row's key), and the cards by `(label, key)` as `rail_view` matches them.

### 2.2

`board.py` `board_text(data, width, color)`: Decisions, *The text*. Lanes and attention in order; `none` under an empty lane; a unit's stage with `done/total` in code and verify, as `bolts_view` prints it; the slot as `unit-1`; the URL last. `width` None means no cutting.

### 2.3

`board.py` `main`: `board [--label L] [--json]`, `_views <label>`, `_board <label> [--once]`, refusals through `fail()` turned into `sys.exit` at the entry point (`code.2`), the label checked with `crew.partition_of` (`code.4`). `plugin/bin/crew`: `board | _views | _board` exec `board.py` and are added to the case that makes no reading folder; the usage header gains `crew board` under `crew rail`. README: `crew board [--label L] [--json]` in the main level's command block under `crew rail`, and a paragraph after the rail's: the four lanes and what each holds, the markers, the attention line and `--json`. `plugin/skills/crew/SKILL.md`: a row "see the whole flow of a partition, by phase" → `crew board [--label <label>]` (`docs.2`; `tests/t-docs.sh`).

### 2.4

`tests/t-board.sh`, its first command the `TESTS` guard (`tests.2`), built like `tests/t-rail.sh` (its `world`, `card`, `commit_at` and `$T/down` patterns): one scenario per requirement of the `crew-board` delta but the last, asserting lanes in order with `none`; two unmoved signals by two capturers and one routed, which is absent; an exploration on the kit's main; a planned bolt and a queued unit; a held bolt with a unit in code in a slot, a unit in review with a card open (✓ on its line, no other line naming its review), a verify report (✎), a fix; a bolt with every unit merged (✓ on the head) and one with every unit landed (! on the head and in attention); a `crew bolt land` within the window and one entry made eight days old, absent; the box down; no `crew plan approve`, `crew unit approve` or `crew tell` in the output, the branch's tip and the record's entry count unchanged; `--json` holding the fields of *The JSON*. Then `tests/moon-tasks`, and commit `tests/moon.yml`.

### 3.1

`_views <label>`: `flow_read` for that label, print `rail_text`, write `board_data` to `~/.cache/crew/board/<label>.json` (make the folder; temporary file in the same folder, then `os.replace`). `plugin/bin/crew` `_rail`: `out=$(bash "$0" _views "$label" 2>&1 || true)` in place of `crew rail`; the rest of the loop unchanged.

### 3.2

`_board <label>`: loop once a second on `(mtime of the frame, shutil.get_terminal_size())`; on a change, read the frame, clear (`\033[H\033[2J`) and print `board_text` at the pane's width, with the stale header past 90 seconds of `read_at` and the no-frame message of Decisions when the file is missing or not whole JSON. `--once` draws once and exits 0. `plugin/bin/crew`: `ensure_board`, after `ensure_rail` in `operator up`: `tab operator board "$CWD" board` and `h pane run` of `bash crew _board $LABEL`, nothing when the pane is live.

### 3.3

`tests/t-board.sh`: `crew _views wldn` prints what `crew rail --label wldn` prints, past its as-of line, and writes a frame equal to `crew board --label wldn --json` past `read_at`; with the shims of `tests/t-reads-once.sh`, one `_views` fetches the state branch once and gathers once on each host; `crew _board wldn --once` with no frame, a fresh frame, and a frame whose `read_at` is 5 minutes old. `tests/t-record-team.sh`: `operator up` opens one `board` tab after `rail` running `crew _board wldn`, and a second `operator up` opens none. README's paragraph gains the `board` tab, drawn from the rail tab's read; `docs/architecture/_open.md`, in record 0010's line, "nothing draws lanes today" becomes "`crew board` draws them as text". Run `tests/moon-tasks` again if the test's reads changed.

### 3.4

`tests/suite t-board t-rail t-record-team t-reads-once t-sites t-bolts t-docs` ends with "0 failed".
