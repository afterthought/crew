# Design

## Context

The page is one file `crew page <label>` writes (`plugin/lib/page.py`): the template `plugin/lib/page.html` with the page's data as one JSON block, read from one fetch of the flywheel's branch and one board read (`board.flow_read`, `board.board_data`). The data holds `board` (the partition's lanes, hosts, teams and attention, as `crew board --json` gives them), the lineage (`nodes`, `edges`, `histories`, `entries`, from the run record by `record.lineage`, the walk `crew trace` makes), `deploys` (each environment's deploys with their release notes) and `made`. The script draws the board, the flow and the deploys views from it with `textContent` only, and nothing on the board opens: the template's opening comment says so ("the pointer over the forms [is dropped], since nothing on the board is clicked").

The mockup is flywheel-next's `design/mockups/rail-and-board.html` (read on its main, 2924aa2f): its dock is `aside.dock` with `.dk-h`, `.dk-b`, `.dk-f` (lines 771 to 800), opened by a key per object (`openDock`, `renderDock`, 3076 to 3108) over a transparent `.scrim`, slid in with `transform` so the board under it does not move, full screen under 760 px (1052). Its rules are `design/surfaces.md` S27 (one panel over the right of the board; Esc, × or a click outside closes it; under 760 px full screen with a back control; a page opened from a page keeps a trail; its header takes the object's form; no foot, and an object with nothing to answer says nothing about it) and S28 (a page per kind). Record 0038 §2 and §7 rule that the page gets that dock, in its one file, forms borrowed and not the file; record 0010 that the board answers nothing.

Rules this design rests on: `state.4` (the page is a view that writes nothing and runs no service), `code.1` (standard library; the page's script is plain), `code.5` (the teams and hosts files read, never written, no field defaulted), `code.7` (each dock page is a decision on plain facts, made in Python), `read.1` and `read.2` (a fact the data does not hold is said not known, never guessed or blank), `code.8` (nothing the agents' views draw moves, so `board.agent_views` and `plugin/hooks/status.js` stay as they are), `tests.11` and `tests.12` (the dock pages in the logic tier, the written page's wiring in one end-to-end case), `docs.2` (README and the skill's line for `crew page`). The change touches the areas of `tests.md` (`tests/`) and `docs.md` (`README.md`); its code is in `plugin/lib/page.py` and `page.html`, which no area page covers.

## Goals / Non-Goals

**Goals:**

- Every item the record names, as the page draws it, opens a dock with what the page's data and lineage hold about it.
- The board does not move when the dock opens or closes.
- What each dock says is decided in Python and proved in the logic tier.

**Non-Goals:**

- The word from the dock to the item's agent, its routing and its marking: `a-word-from-the-board-reaches-the-items-agent`. This change leaves no field, button or address for it.
- A subscription's use and limits, and the fleet page: `the-fleet-page-shows-every-partition-at-once`, `the-fleet-page-shows-each-subscriptions-use`. A subscription's dock here holds only the sessions the hosts file puts on its account.
- The flow view: its objects keep their own selection and history table.
- Any read beyond the one the page is made from, and any change to `crew board`'s JSON.

## Decisions

### 1. Python makes each dock page; the script only draws it

`page.py` gains `docks(d, fleet, label)`, a function of the page's data and the fleet, which returns `{key: page}`, one page per item, and gives each item of `d["board"]` and `d["deploys"]` its `dock` key. A page is plain data: `kind`, `form` (the head's form), `title`, `tail`, `facts` (pairs of label and text), `markers` (as the board's), `parts` (titled lists of rows, each a text and, where the item is drawn, the key it opens) and `history` (entry ids, oldest first, from `d["histories"]`). The script draws any page the same way, from those fields, with `textContent`.

Why: what a dock says is a decision on plain facts (`code.7`), and nothing in crew's tiers runs the page's script; made in Python, every dock's content is a logic case, where the script's own share is drawing a list. Considered: building each dock in the script from the board's objects, as the mockup's `renderDock` does; it puts every kind's rules where no test can reach them and leaves the coder to prove them by string presence.

### 2. Keys name the item, not its place

A key is `<kind>:<name>`: `signal:<id>`, `proposal:<n>`, `bolt:<name>`, `unit:<name>` (a chore too, its kind said in the page), `fix:<bolt>/<fix>`, `landing:<bolt>`, `deploy:<env>/<to>/<offered or started>`, `operation:<env>/<key>`, `team:<name>`, `subscription:<account>`. A lineage node's id maps to the key of its kind (`signals/x` to `signal:x`, `chore/x` to `unit:x`); an agenda item has no dock and is named as text. The key is what the address keeps (Decision 6), so the same item on a page written again opens again, and the same deploy opens one dock from the Operation lane and from the deploys view.

Why a deploy's key holds when it was offered or started: one commit can be offered to an environment more than once; `ops.environments` gives every deploy one or the other and never changes either once set. Its `at` moves with each step, so it is not used.

### 3. What each kind's dock holds

From the page's data alone, as S28 lists per kind and record 0038 §2 bounds it; the whole list per kind is in Task notes 1.2. In short: a signal its whole assertion (the lineage node's label), kind, capturer, age and history; a proposal its case's first line, who opened it and when, whose agreement it waits on, its markers, the units and bolts the lineage joins to it and its history; a bolt its ledger's facts, units, fixes, landing, the deploys that carried it and its history; a unit its bolt, stage, tasks, slot, worktree, server, intent and history; a fix its bolt, whether it merged, slot, worktree and server; a landing when and by whom, its team and units, and the deploys carrying it; a deploy and an operation what the deploys view says of them; a team and a subscription as below. A fact the data does not hold is left out, and a dock never says a field blank (`read.2`); a stage the board gives as unknown is said unknown (`read.1`).

A fix has no history: the lineage's columns are signals, agenda items, proposals, units and bolts, and a fix is none of them. Its bolt's dock carries the bolt's.

### 4. Teams in the strip, and the subscription through its team

The strip after the hosts gains a pill per team, in the teams file's order (`d["board"]["teams"]`), each naming its host; a ledger's head and a landing's record name the team too, and the team's name there opens the same dock. A team's dock adds what `page.py` reads from the fleet crew already loaded: the team's herdr session and the account the hosts file gives that session (`fleet["hosts"][machine]["sessions"][session]["account"]`, `code.5`). The account is a link to its subscription's dock, which lists every session of the partition on it: the teams, and the main-level agents by `p["sessions"]` on the partition's machine, each with host and session. A session whose entry names no account is said "no account named in herdr-hosts" (`read.2`).

Why the strip: the board names a team only on a bolt it holds or a landing it made, and a team with neither would have no item to open; the mockup's strip is where its hosts and repositories open their docks (its `.host`, `.repo`). Why through the team: the page draws no subscription of its own until the fleet page's units, and record 0038's context says the page's fleet already holds each session's account. The account is added in `page.py`, not in `board_data`, so `crew board --json` and the agents' views are unchanged (`code.8`).

### 5. The dock's form, from the mockup

`page.html` takes the mockup's `.scrim`, `.dock`, `.dk-h` with its forms (`dk-sheet`, `dk-slip`, `dk-ledger`, `dk-record`), `.dk-b`, `.sec` and `.kv`, and its phone rule, with the page's own colour tokens, which are already the mockup's; no `.dk-f`, since the dock has no foot (S27). The dock is `position:absolute` over `#view-board`'s right, `width:min(600px, calc(100% - 200px))`, and slides with `transform`, so the lanes' grid and scroll are never touched; the scrim is transparent and catches the click outside. Under 760 px the dock is `position:fixed` over the whole window with a back control, and the board's own scroll is left where it was. The dock is `role="dialog"` with `aria-modal="false"`, labelled by its title; it takes the focus on opening and gives it back to its item on closing. Items take `tabindex="0"` and `role="button"`, as the flow view's nodes do, and the pointer over them returns.

### 6. A trail, and the dock in the address

A link in a dock opens its item's dock in place and pushes the one it left onto a trail; the back control, shown once the trail holds one, pops it (S27's ruling of 2026-09-16). Under 760 px the back control is always shown, and with the trail empty it closes the dock onto the board as it was. Esc, × and a click outside close the dock and clear the trail. The open key is kept in the page's address beside `team` and `view` (`#dock=<key>`, the existing `keep`), so a reload or a rewrite reopens it; a key the new page's `D.docks` does not hold is dropped from the address and the board is shown. The trail is not kept.

### 7. The board still answers nothing

No dock holds a control that answers, moves or sends: a marker in a dock is drawn by the board's own `marks`, its words unchanged, and the dock has no foot. The next unit adds the word's field; nothing here anticipates it.

## Risks / Trade-offs

- [The page grows by a page per item] → The docks hold facts already in the data plus keys; a partition's page holds tens of items, so the file grows by kilobytes. The page is written whole and read from disk or the tailnet.
- [A dock and the board say different things about one item] → Both are drawn from the one data block of one read; the dock adds no read (Decision 1).
- [The template's behaviour is proved by its marks, not by running it] → As the page's forms are today (`test_page.py`); what each dock says, which is most of the change, is a logic case.
- [A key whose item moves lanes, a unit from the queue into a ledger] → The key names the item, not its lane (Decision 2), so the dock follows it.

## Migration Plan

None: the page is written whole every thirty seconds by swancloud's maker, and the next write carries the dock. Rolling back is the next write from an older crew.

## After deploy

None: every scenario is proved in crew's tiers, and serving the page is swancloud's, unchanged by this change.

## Task notes

**1.1** `plugin/lib/page.py`: `key_of(node_id)`, a lineage node's id to its dock's key or None (agenda items, and kinds with no dock); `docks(d, fleet, label)`, returning `{key: page}` and setting `dock` on each item of `d["board"]` (each signal, proposal, planned bolt and its units, held bolt, its units and fixes, queued unit, landing, environment deploy and waiting operation, and each team) and on each deploy of `d["deploys"]`; called in `page()` after `d["deploys"]` is set, its result put in `d["docks"]`. A page: `{"kind", "form", "title", "tail", "facts": [[label, text]], "markers": [...], "parts": [{"title", "rows": [{"text", "key"}]}], "history": [entry ids]}`, `key` only where `docks` holds it, `form` one of `sheet`, `slip`, `ledger`, `record` or None. Cases in `tests/py/test_page.py`, a class `TestDocks` on a board and lineage built as `TestData`'s and `test_board.py`'s are: every item of each kind carries a key the docks hold, and every team; a unit's dock in a ledger says its bolt as a link, its stage, `1 of 2 tasks` and its slot; the same deploy from `board.environments` and from `deploys` has one key; a key names its item, not its lane; a link's key is set only where a dock exists, an agenda item a row with no key.

**1.2** What each page holds, each fact only when the data has it:
- signal: title its first words, tail `kind · captured by <who> · <age>`; facts the id, kind, who captured it and when; a part `assertion` with the lineage node's label when the node is in the window; `linked` from the lineage edges both ways; history `d["histories"]["signals/<id>"]`.
- proposal (`form` sheet): title its case's first line, tail `proposal <n> · by <who> · opened <when>`; facts waiting on (each team's conductor); markers; teams; parts `units and bolts` from the edges out of `proposal/<n>`; history.
- bolt (`form` ledger): title the bolt, tail `<repo> · <team> on <host> · <state>` or `planned, no team`; facts goal, server; parts `units` in plan order, each `<unit> · <stage>[ <done>/<total>]` and its key; `fixes`; `landed` when Operation holds its landing; `carried by` the deploys whose `bolts` name it; markers and the landed attention as the board draws them; history.
- unit (`form` slip when queued): title the unit, tail `unit` or `chore` and where it is (`in <bolt>`, `queued`, `planned in <bolt>`); facts bolt (a link), repo, stage (unknown when the board gives none), tasks, slot, worktree, server, sources; part `intent` from the lineage label; history from `unit/` or `chore/`.
- fix: title the fix, tail `fix of <bolt>`; facts merged or not, slot, worktree, server; part `bolt` with its key.
- landing (`form` record): title the bolt, tail `landed <when> by <who>`; facts team; parts `units`, `carried by`; the bolt's `bolt.land` entry as its history.
- deploy (`form` record): title `deploy <to[:7]>` on its environment; facts from, to, the word (the deploys view's sentence for its answer), started, ended, outcome; parts `steps`, `checks`, `carried` with each bolt's release notes from `d["deploys"]`, `after deploy`; markers.
- operation (`form` record): title its key; facts state said as the board says it (`waitSaid`'s words, in Python), environment, commit, held, gate, at; part `text` and `note`; markers.
- team: title the team, tail `<kit> on <host>`; facts kits, host, session, account (a link to `subscription:<account>`, or `no account named in herdr-hosts`); parts `bolts held` (or `holds no bolt`), `landings`, `signals captured` by its agents (from `captured_by` and `plan.role`, as `board_data` does), `environment` on its host.
- subscription: title the account, tail `Claude account`; part `sessions on it` in this partition: each team and each main-level agent (`<label>-<role>`, by `p["sessions"]` on `p["machine"]`), `<agent> · <host> session <session>`, a team's row its key.
Cases: one per kind, each asserting its title, tail and facts on a fixture holding that kind; the subscription case with two teams on one account and a main-level role on it; the account missing from a session's entry said, not blank; a signal's assertion holding `</script><b>here</b>` kept as it is in the page and in `render`'s block.

**2.1** `plugin/lib/page.html`: the dock markup after `.lanes` inside `#view-board` (`.scrim`, `aside.dock` with `.dk-h` and `.dk-b`), its styles from the mockup's lines 771 to 800 and 1052 as Decision 5 says, the template's opening comment and style comment saying the dock is borrowed and that the board's items open it; every drawn item `tabindex="0"`, `role="button"`, `data-dock` its key, opened on click and on Enter or space; `openDock(key)`, `closeDock()`, `back()`, the trail, Esc, × and a click on the scrim; the dock drawn from `D.docks[key]` by one function using `el` and `textContent` only, history rows from `D.entries` (`At` in the viewer's zone, `Act`, `Why`, `By`, `Host`, `Refused`), markers by the existing `marks`; the strip's team pills after the hosts; the deploys view's deploys carrying `data-dock`. Cases in `tests/py/test_page.py`, on `page.render` with the data block removed, as the page's form cases are: the dock's markup and forms are there (`class="dock"`, `role="dialog"`, `.dk-h.dk-sheet`, `.dk-h.dk-ledger`, `.dk-h.dk-record`, `.dk-h.dk-slip`, `transform`, the phone rule's `position:fixed`); no `.dk-f`; the keys `Escape`, `Enter`; `D.docks`; `"dock"` kept by `keep`; no `innerHTML`, `fetch`, `XMLHttpRequest` or `WebSocket`; the existing "nothing loads from outside" case still passes.

**2.2** The open dock in the address: `open()` reads `dock` from the fragment and opens it when `D.docks` holds it, else drops it with `keep("dock", "")`; opening keeps it, closing clears it. A case on the rendered template for the fragment's `dock` and its drop.

**3.1** `tests/t-journey-board.sh`, in its `crew page` case: the written page's data holds `docks`, the held bolt `tenant-environments` carries its key and `.docks["bolt:tenant-environments"].title` is its name, and unit a's dock's history is the ids `crew trace unit/a` prints, as the node's history is checked today. No new `# Reads:` path.

**3.2** README's `crew page` paragraph and `plugin/skills/crew/SKILL.md`'s row: a click on any item opens its dock over the board with its details and history, the board answering nothing; the strip names the teams. `tests/t-docs.sh` passes.
