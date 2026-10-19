# Design

## Context

See proposal.md for why. What exists, or will once the unit ahead of this one is built:

- **`crew board [--label L] [--json]`** (`plugin/lib/board.py`, built by `a-board-shows-the-flow-in-the-terminal`). `flow_read(fleet, labels)` makes one read: `plan.rail_read(..., board=True)` (plan, proposals, survey of every team's kit, cards, run record, landings) plus each label's unmoved signals. `board_data(fleet, labels, read, now)` turns it into `{"read_at", "from", "partitions": [...], "unread"}`. Each partition holds `label`, `plan` (the tip read), `hosts`, `inception.signals` / `inception.explorations`, `bolt_plan.proposals` / `planned` / `queue`, `construction` (ledgers with `units` and `fixes`), `operation` and `attention`. Markers carry `group` (`proposals`, `land`, `verify`), `key`, `glyph` (✓, ✎), `at` and `card`.
- **`crew page <label>`** (`plugin/lib/page.py` and its template `plugin/lib/page.html`, built by `page-of-the-flow`, which this unit comes after). It writes one self-contained HTML file to `~/.local/state/crew/<label>/page.html`, or to `--out`. The file holds a `<script type="application/json">` data block, inline CSS, inline JavaScript, a header naming the time and the commit it was made from and any host it could not read, and the lineage view.
- **The mockup**, agentplot/blueprints `design/flywheel-next/mockups/rail-and-board.html`. Its phases view and its forms are described in `surfaces.md` S12 to S18, and requirement 307 says the phone is the same page under 760 px. The CSS this change borrows is: the colour tokens on `:root` with the dark set under `prefers-color-scheme` and `data-theme` (lines 232 to 248); `.lanes` and `.lane` (371, 431 to 439), with Bolt plan's hatch; `.sheet` and `.slip` (512 to 535); `.ledger` and its parts (574 to 599); `.record` (614 to 626); `.quote` (627 to 633); `.marks` and `.mark` (666 to 669); the hosts strip and `.host` (281 to 292); `.sec-h` and `.empty`; and the phone block, `@media (max-width:759px)` from line 1016, for its `.lanes` and `.lane` rules (1035, 1044). The mockup loads Manrope and JetBrains Mono from Google Fonts, which a self-contained page cannot do.
- **The teams file** lists partitions in order (`madswan`, `swancloud`, `wldn` today), each with its teams, and each team with its kit and machine (`crew.load()`: `fleet["partitions"][label]["teams"]`, `fleet["teams"][t]["kit"]["name"]`, `["machine"]`). `plan.role(fleet, name)` says which team an agent's name belongs to.
- **Serving** is swancloud's (record 0019): each partition's page regenerated on mac-studio every 30 seconds and on each run-record entry, the pages served side by side at one fleet name on the tailnet, and the board opened from the SwiftBar menu.

Record 0010 is the decision this builds: "The page is the board the user looks at" (2026-10-09). Rules this rests on: `state.4` (a view is computed from files, nothing written); `record.1` (a pure read appends no entry); `read.1` and `read.3` (what could not be read is named, and the rest still shown); `code.1` (standard library only, no dependency fetched); `code.2` (refusals); `docs.2` (README, SKILL.md and usage together); `tests.2` (test headers); `tests.5` (`tests/moon.yml`).

## Goals / Non-Goals

**Goals:**
- Opening a partition's page shows its board, laid out and styled like the mockup's phases view, readable at a glance on a desktop and a phone, light or dark.
- A viewer can narrow the board to one team and keep that choice across reloads.
- Each partition's page is one step from the others when they are served side by side.
- The page stays one file that needs nothing outside it, and nothing in crew reads it.

**Non-Goals:**
- Serving the pages, regenerating them, the SwiftBar link. Those are swancloud's.
- The page reloading itself. Nothing in record 0010 asks for it, and the user reloads. Named for the design agent in the final message.
- The mockup's map view, rail, dock, palette, machinery strip, keyboard walk, intents, threads and beads, chores and session chips. crew has no data for them, or they answer things, and the board answers nothing (S18).
- Narrowing the lineage view to a team.
- Any change to `crew board`'s text or `crew rail`.

## Decisions

### The page makes the board's read and embeds it

`page.py` calls `board.flow_read(fleet, [label])` and `board.board_data(...)` for the one partition, then embeds `data["partitions"][0]` with `read_at` and `unread`, under a `board` key in the page's data block. It also embeds `partitions`, the labels of every partition in the teams file in order, and `label`. The lineage data `page-of-the-flow` builds stays where it is.

One read, one commit. The header names one commit as the one the page was made from. The board's read already reads the run record (for landings) and the plan's tip. `page.py` passes that tip to the lineage read, so the labels of both views come from one tip. When `page-of-the-flow`'s code cannot take a tip without changing how `record.gather` reads, the header names each tip it read instead of claiming one (`read.1`). Task notes 2.1 say where to look.

A board that is partly unreadable is still drawn, as `crew board` draws it: hosts that did not answer and plans or signal homes not read are in the partition's `attention` and the page shows them (`read.3`). When the flywheel's branch cannot be read at all, `crew page` refuses as `page-of-the-flow` has it, and writes nothing.

*Alternative:* the page runs `crew board --json` as a subprocess. Rejected: that is a second process and a second read for what one function call gives, and `board.py` is already imported by crew's own code.

### Whose each object is, decided in the board's read

Narrowing needs, for each object, the teams it belongs to. That is decided once, in `board_data`, and put in `crew board --json` as `teams` on each object, so the page only compares strings and the rule is tested in Python with the rest of the board:

| Object | Its teams |
|---|---|
| held bolt (Construction ledger), its units and fixes | the ledger's `team` |
| landed bolt (Operation) | `team`, the team it was given to, when known; else none |
| signal | the team `plan.role` gives its `captured_by`, when that is a conductor, ops or unit of a team of this partition; else none |
| exploration | every team of the partition whose kit is the exploration's kit |
| proposal | each team holding a bolt its changes name, and each team of the partition whose kit is the repository of a bolt or unit its changes name |
| planned bolt and its units | every team of the partition whose kit is the bolt's repository |
| queued unit | every team of the partition whose kit is the unit's repository |

Each partition also gains `teams`: `[{"team", "kit", "host"}]` in the teams file's order, which is what the page's control offers.

Why work no team holds belongs to every team building its repository: narrowed to crw-3, the user wants to see what crw-3 could be given next, and planned crew bolts and queued crew units are exactly that. A signal the user wrote, or one a machine captured, belongs to no team and is seen with all teams.

The attention strip is never narrowed. A host that did not answer or a plan that could not be read is about the whole partition's reading, and hiding it behind a team choice would hide a failure (`read.3`).

### The board view, in the mockup's forms

The template gains a board view beside the lineage view, and the board view is what the page opens on. The header holds, left to right: the partitions, the view switch (board, flow) as the mockup's segmented control, the team control, and the time and commit. Under the header sits a strip, borrowed from the mockup's hosts strip. It shows each host of the partition as a pill, a host that did not answer with the mockup's warning border, then each attention item marked !. Under the strip, the four lanes.

Each object is drawn in its kind's form, using the board's JSON fields:

- **Inception** (`.lane.inception`). The signals are grouped by `captured_by`, each group under a counter line, for example "wldn-planner · 2 not moved · oldest 3d". Each signal is a `.quote`: its `first` in the quotation, and under it in mono its `kind`, its age from `at`, and its `signal` id dimmed. Under a section head "explorations", each exploration is a row: kit greyed, name, first line.
- **Bolt plan** (`.lane.plan`, the hatched gate, header chip "gate"). Each proposal is a `.sheet`: kicker "proposal N", title the first line of its case, meta "by X · opened Y", and a foot "waiting on X-conductor" when `waiting` is not empty. The mockup's 190 px minimum height is dropped, since crew's sheets carry only a few lines. Each planned bolt is a `.ledger` with no team in its head and every unit a queued link. Each queued unit is a `.slip`: repository greyed before its name, kicker "queued", its sources under it.
- **Construction** (`.lane.construction`). Each held bolt is a `.ledger`. Its head holds the repository greyed, the bolt, "team on host", and the state when it is not active. Its chain holds the units in plan order: `merged` and `landed` as `.lg-unit.merged`; `construct`, `code`, `verify` and `settle` as `.lg-unit.building`, with its stage and tasks (`code 1/2`), its slot and its server's URL as text; every other stage (`planned`, `ready`, `waiting`, `amended`, `unknown`) as `.lg-unit.queued`, its stage written beside its name. The fixes go on the machinery row (`.lg-mach`) with "fix" or "fix merged" and the slot. The bolt's server goes in the foot. A URL is shown as text and is not a link, since the page answers nothing and a dev server on another host may not be reachable from where the page is read.
- **Operation** (`.lane.operation`, header chip "observed"). Each landing is a `.record`: the bolt, when it landed (in the viewer's time, at the right), a stamp "landed by X", the team and the units under it.

**Markers** go in a `.marks` row on their object: the sheet, the ledger's head, or the unit's link. Each is a `.mark` classed by its glyph, ✓ `approve` and ✎ `answer`, showing the glyph and "card open, asked by X" or "no card". A ledger whose bolt is `landed` also carries a `.mark.attention` "!". A lane with nothing in it shows `.empty`, "nothing here", or "nothing here for crw-3" when narrowed. No object carries its lane's name (S18).

**Fonts** are the mockup's fallback stacks only: `system-ui, -apple-system, "Segoe UI", sans-serif` and `ui-monospace, Menlo, Consolas, monospace`. Nothing is loaded from anywhere.

**Layout.** `.lanes` is the mockup's grid of four columns, `minmax(225px,.95fr) minmax(185px,.6fr) minmax(330px,1.45fr) minmax(215px,.9fr)`. Under `@media (max-width:759px)`, the mockup's breakpoint for under 760 px, it becomes one column with each lane at its natural height, the header wrapping onto two rows, and long names breaking rather than running past the edge (`overflow-wrap:anywhere` on names and URLs). The page scrolls as a whole on a phone, and each lane scrolls on its own on a desktop, as in the mockup.

**Light and dark.** These are the mockup's tokens, light on `:root` and dark under `@media (prefers-color-scheme:dark)`. The mockup's `data-theme` override is kept, so a later control can force one, but no control is added.

### The team control, and how the choice is kept

The control is a `<select>` in the header: "all teams", then each of `board.teams` by name, with its host as the hint. Choosing one sets `document.body.dataset.team`. The script then hides every object whose `teams` does not include that team, re-counts each lane, and shows the empty line where a lane has nothing left. Units inside a ledger follow their ledger.

The choice is kept in two places:

1. **The address.** The fragment `#team=<name>` is set with `history.replaceState`, so a reload, which keeps the fragment, opens on the same team, and a bookmark or a SwiftBar link can carry it.
2. **The browser,** for when the address names none. `localStorage` under `crew-page:<label>:team`, written on each choice and read when the page opens with no `team` in its fragment. Every read and write is wrapped in try/catch, since a page opened from disk or in a private window can refuse storage, and the address alone then still works.

A fragment naming a team the partition no longer has, or a stored one, is shown as all teams. The fragment is left as it is, so the user sees what was asked. The view switch is kept the same way (`#view=flow`), so a reload stays on the view the user was on, defaulting to the board.

Why both: the 30-second regeneration replaces the file, and the user reloads. The fragment survives that by itself. The browser's copy covers the SwiftBar link, which opens the plain page, and a step from another partition's page, which carries only that partition's link.

### The partitions in the header

The header lists `partitions` in the teams file's order. The page's own label is marked current (`aria-current="page"`, not a link). Each other label is an `<a href>` to `../<label>/page.html`, relative, carrying the team fragment only when the team exists in that partition too (crew's teams belong to one partition, so in practice none is carried).

`../<label>/page.html` is crew's own layout under `~/.local/state/crew/`. It holds whenever the pages are written by default, or under any folder as `<folder>/<label>/page.html`, which is what "served side by side" needs from swancloud. A page written by `--out` somewhere else has links that lead nowhere unless the same layout is kept; README says so. A partition whose page has not been written gives the server's not-found, and the page cannot know that in advance.

*Alternative:* one page holding every partition's board. Rejected by record 0010 ("one page per partition, as one board per flywheel", requirement 235), and the user asked for one partition at a time.

### What must not break

`crew board`'s text and `crew rail` are unchanged: `teams` fields are added to the JSON only, and `tests/t-board.sh`'s and `tests/t-rail.sh`'s existing checks pass untouched. The lineage view still draws as `page-of-the-flow` built it, one switch away, and its tests pass.

## Risks / Trade-offs

- [`crew page` now asks every host of the partition for its kits, so it takes seconds and depends on ssh] → the same read `crew board` and `crew rail` make, 2.4 to 4.7 s per partition from mac-studio, inside the 30-second cadence. A host that does not answer is named and the page is still written (`read.3`).
- [The mockup's CSS is long and full of forms crew does not use] → only the classes named under *Context* are copied, and the page carries no unused form.
- [The page and the mockup drift apart] → the template names the mockup and the lines its styles came from in one comment at the head of its style block, so a restyle starts from there.
- [The rendering cannot be checked by the suite: the devenv has no browser or JavaScript engine (`code.1`)] → the suite checks the data and the file's static shape. How it looks, narrows and stacks is checked on real work, after landing.
- [Narrowing by repository shows the same planned work under every team of a kit] → that is what each of those teams could be given next, so it is the honest answer. The held bolt and the team's own signals are what tell teams apart.
- [`localStorage` on `file://` is shared by every file page in some browsers] → the key carries the label, and the value is only a team name.

## Migration Plan

None. Pull crew on every host, and the next `crew page` writes a page that opens on the board. Rollback is reverting the commit. An earlier page is overwritten at its next regeneration.

## Proof in dev

None. crew has no dev environment, and the bolt's proof is its verification.

## Proof on real work

Once the bolt has landed and every host has pulled, with swancloud serving the pages side by side (or, until it does, with `crew page madswan`, `crew page swancloud` and `crew page wldn` run on mac-studio and the folder `~/.local/state/crew/` opened in a browser):

1. Open swancloud's page on the desktop. It opens on the board. The four lanes sit side by side, Bolt plan hatched and narrow. Held bolts are ledgers with their units as a chain, open proposals are sheets with ✓, and landings are muted records. The header shows madswan, swancloud and wldn, and the time and commit. The browser's network panel shows no request beyond the file.
2. Switch the system to dark: the page follows. Narrow the window under 760 px, or open it on the phone: the lanes stack in order, and nothing scrolls sideways.
3. Choose crw-3. Every lane narrows to crw-3's work, and the attention strip stays. Reload: still crw-3. Run `crew page swancloud` again and reload: still crw-3. Open the plain page from the SwiftBar link: still crw-3.
4. Click wldn in the header: wldn's page opens. Click swancloud: back, still on crw-3.
5. Switch to the flow view, reload: still the flow view. Switch back to the board.

## Task notes

### 1.1

In `board.py`'s `board_data`, per partition:

- `teams`: `[{"team": t, "kit": fleet["teams"][t]["kit"]["name"], "host": fleet["teams"][t]["machine"]} for t in p["teams"]]`, in the partition's order.
- A helper `building(repo)`, giving the partition's teams whose kit name is `repo`, in that order.

Add `teams` to every object, following the table under *Whose each object is*:

- Ledger: `[b.get("Team")]`.
- Landing: `[team]` when `read["gives"]` has it, else `[]`.
- Signal: `plan.role(fleet, captured_by)` when its kind is `conductor` or `team` and the team is in `p["teams"]`.
- Exploration: `building(kit)`.
- Planned bolt: `building(repo)`.
- Queued unit: `building(repo)`.
- Proposal: from the open proposal's `changes[].bolts`. A bolt in the plan gives its `Team` when held, and `building(Repo)` otherwise. `"queue"` and a new bolt give `building` of the repository the change's unit or bolt names. Read what `open_proposals` already returns before reaching for more, and when a change names no repository, it adds none.

Units and fixes inside a ledger need no field of their own: the page reads the ledger's. Keep each list's order the partition's, with no repeats.

`board_text` is not touched. In `tests/t-board.sh`, add jq checks on the fixture it already builds: the ledger's teams; the queued `zone-two`'s and the planned `apex-zones`' teams (every team of `switchboard-kit` in the fixture's teams file); the user's note `plans-are-checked`'s `[]`; wldn-planner's signals' `[]` (a planner is no team); the proposal's teams; and the partition's `teams` list. Every existing check passes untouched.

### 2.1

Before this task, take `page-of-the-flow`'s work into this place as it stands: `git merge unit/page-of-the-flow`. crew already took its head when this place was made, but its code may have moved on since. When `plugin/lib/page.py` and `plugin/lib/page.html` are not there yet because its code has not committed them, stop and say so with `crew needs`: this task builds on them.

In `page.py`, make the board's read for the one label and embed it, as *The page makes the board's read and embeds it* says: `board`, `partitions` and `label` in the data block. Give the lineage read the plan tip the board read (`data["partitions"][0]["plan"]`) where its code reads the labels at a tip. If it reads entries through `record.gather` with its own fetch, look for a way to hand it the tip without changing what `crew events` prints. If there is none, the header names both tips. `crew page` prints its header line as `page-of-the-flow` has it.

In `tests/t-page.sh`, add checks on the page written for its fixture, whose data block can be read with `python3` from the file:

- `board.label` is the label.
- The four lanes are present.
- `partitions` equals the teams file's labels in order.
- A host made unreachable through `$T/down` appears in `board.attention`, and the page is still written.

### 2.2

The board view in `page.html`, as *The board view, in the mockup's forms* says.

- Copy the named classes from the mockup with their tokens, light and dark. Swap the font stacks for the system ones. Drop the sheet's minimum height.
- Add one comment at the head of the style block naming the mockup's path and the line ranges.
- The view switch, with the board as the default.
- The strip with hosts and attention.
- The four lanes, built by the script from `board` with `textContent` only, never `innerHTML` for state text. Each element carries its object's `teams` in a `data-teams` attribute, space-separated.
- Each lane's empty line.

`tests/t-page.sh` checks the static shape:

- The file holds `@media (max-width:759px)` and `prefers-color-scheme:dark`.
- It holds the four lane names.
- It holds no `<link`, no `<script src`, no `@import`, no `url(http`, and no `http://` or `https://` outside the data block.
- It holds none of the mockup's sample names (`atlas`, `plan-decisions`, `books`).

How it draws is the first proof on real work.

### 2.3

The team control and its keeping, as *The team control, and how the choice is kept* says:

- The `<select>` filled from `board.teams`.
- Narrowing by `data-teams`, with counts and empty lines kept right.
- `#team=` and `#view=` in the fragment through `history.replaceState`.
- `localStorage` under `crew-page:<label>:team` and `crew-page:<label>:view`, each access in try/catch.
- An unknown team shown as all.

The partitions in the header: the current one marked, the others linked as `../<label>/page.html`.

`tests/t-page.sh` checks:

- For the fixture's teams file, the page holds `href="../<other>/page.html"` for each other partition and none for its own.
- The data's `board.teams` lists the partition's teams.

The rest is the third and fourth proofs on real work.

### 2.4

- README, in "Seeing what happened" where `page-of-the-flow` documents `crew page`: one paragraph saying the page opens on the board. Say the lanes are drawn as the flywheel mockup draws them and that a viewer can narrow it to one team, kept across reloads. Say the header links each partition's page beside it, `../<label>/page.html`, which holds when the pages keep crew's layout (not under an arbitrary `--out`), and that the lineage is the flow view one switch away.
- The same in a sentence in `plugin/skills/crew/SKILL.md` and in `crew page`'s line of the usage header in `plugin/bin/crew`.
- `tests/t-docs.sh` passes.

### 2.5

If `tests/t-page.sh` or `tests/t-board.sh` now reads a file it did not, name it on the test's `# Reads:` line, run `tests/moon-tasks` and commit `tests/moon.yml`. Then `tests/suite t-page t-board t-rail t-docs t-events t-reads-once` ends with "0 failed".
