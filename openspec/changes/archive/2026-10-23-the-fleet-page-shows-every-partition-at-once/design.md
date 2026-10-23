# Design

## Context

`crew page <label>` (`plugin/lib/page.py`) writes one partition's page from one board read of that partition (`board.flow_read`, `board.board_data`) and its lineage, into the template `plugin/lib/page.html`, which loads nothing. swancloud's maker (`packages/swancloud-board`) runs it for each partition every thirty seconds and srv's Caddy serves the pages side by side as `/<label>.html`, sending the bare name to the first partition's page (`modules/board-server.nix`). This unit is built on `the-board-opens-a-dock-on-each-item`, which gives each partition's page a dock per item kept in the address as `#dock=<key>`, a team's key `team:<name>`.

Record 0038 §1 rules a fleet page at the board's root, every partition at once; its consequences make it a second file of the same maker, one file loading nothing (§7), and leave each partition's page as it is, a link away. Record 0010 holds: the page is the board the user looks at and the board answers nothing. Everything the fleet page shows is already read by crew for the board of every partition at once (`crew board` with no label): `board_data` gives each partition's hosts and whether they answered, its teams with their kits and host, its held bolts with their units' stages and slots, its fixes, its planned bolts and queue, its landings and its attention; `read["logs"]` holds each partition's run-record entries in the record's window, `bolt.land` with its `Repo` and `Head` (`plan.14`) and `stage.start` and `stage.end` naming `stage/<unit>/<stage>` and `agent/<team>-<slot>`; and `crew.load()` gives each team's and main-level role's herdr session (`p["sessions"]`, `crew.dispatch_place`) and the hosts file each session's `account` (`code.5`).

Rules this design rests on: `state.4` (a view reads and writes nothing, no service), `code.1` (standard library; the page's script plain), `code.5` (the teams and hosts files read, never written, no field defaulted), `code.7` (what the fleet page says is a function of plain facts, made in Python and proved in the logic tier), `read.1` and `read.2` (what cannot be read is said so, never guessed or left blank), `read.3` (a host that does not answer is named and the rest shown), `read.5` (the run record is read from the branch; a host is read over ssh only for its kits' stages, which the board's read already does), `plan.12` (one read of each kit), `code.8` (nothing the agents' views draw moves, so `board.agent_views` and `plugin/hooks/status.js` are unchanged), `tests.10` and `tests.11` (the cases in the logic tier, the wiring in one end-to-end case, its task's inputs regenerated), `docs.2` (README, the skill and the usage header together). The change touches the areas of `tests.md` (`tests/`) and `docs.md` (`README.md`); `teams.md` covers `plugin/bin/crew`, whose usage header alone changes.

## Goals / Non-Goals

**Goals:**

- One file, made by one read, showing every partition's hosts and sessions with their accounts, kits and their mains, teams and how busy each is, and attention.
- Every fact on it decided in Python on plain facts and proved in the logic tier.
- The fleet page and the partitions' pages linked both ways in the layouts crew and swancloud write them in.

**Non-Goals:**

- A subscription's use and limits: `the-fleet-page-shows-each-subscriptions-use`. This unit shows the account each session runs on and nothing of its use.
- A dock on the fleet page, or a word sent from it: a partition's name opens its page and a team opens its dock there.
- Serving the fleet page at the board's root: swancloud's maker and server.
- Sluice's own queue on a main: crew does not read it for the board, and this unit adds no read.
- Any change to `crew board`, its JSON or the agents' views.

## Decisions

### 1. `crew page --fleet`, one read of every partition

`crew page` gains `--fleet`, taken in place of the label (one of the two, refused otherwise), with `--out`; `--since` stays the partition page's alone, since the fleet page's window is the record's, as the board's is. It runs `board.flow_read(fleet, labels)` and `board.board_data(fleet, labels, read, now)` once over every label in the teams file, the same read `crew board` makes of all of them, and draws nothing from any other read. Written whole, as the partition page is (`write`), to `--out` or to `record.ROOT / "page.html"`.

Why a flag of `crew page` and not a command of its own: record 0038 makes the fleet page a second file of the same maker, and swancloud's maker already finds `crew page` in crew's usage before it makes anything. Why not a partition named `fleet`: a label is any name `code.4` allows, and one may yet be called that. Considered: making the fleet page from the partitions' pages' data, one read per partition; it reads each kit as many times as partitions share hosts, against `plan.12`, and the pages could disagree with each other.

### 2. The fleet's data is a decision on plain facts

`page.py` gains `fleet_data(fleet, bd, logs, now)`, a function of the fleet crew loaded, `board_data`'s result, each partition's entries (`read["logs"]`) and the time, returning `{"made": {...}, "partitions": [...]}`; nothing in it calls a tool (`code.7`). Each partition is:

- `label`, `partition` (its name in the teams file), `plan` (the commit its plan was read at, or None), `unread` (what could not be read, `bd["unread"]` for it);
- `hosts`: each host of `p["hosts"]`, in its order, `{host, answered, why, sessions}`, each session `{session, account, agents}`, the agents those crew starts there for the partition: each team whose `session` and `machine` they are, each main-level role of `MAIN_STANDING` by `p["sessions"]` on `p["machine"]` (named `<label>-<role>`), and the dispatcher `crew.dispatch_place` gives that host when the partition's teams run there (`<label>-dispatch-<host>`). A session no agent of the partition runs in is left out, since the block says where the partition runs; `account` is the hosts file's or None, said "no account named in herdr-hosts" (`read.2`), the dock's words for it. The main level's host is listed even when no team runs there.
- `kits`: Decision 3. `teams`: Decision 4. `attention`: `board.attention_text` of each of the board's attention items, and `cards`, how many open cards the board lists.

### 3. A kit's main: its last landing and what is queued for it

Each kit the partition's teams build, once, in the order `board_data`'s explorations take them (teams by name, each team's kits in order), with the teams building it. Its last landing is the newest `bolt.land` entry of the partition's entries not refused whose `Repo` is the kit: `{bolt, head: Head, at, by}`; none in the window is said "no landing since <the window's start>". What is queued for its main, read from the board's lanes, each bolt and unit by its `repo`: the held bolts whose state is `waits`, each with its landing marker's card open or none, in the plan's order; the held bolts in construction (any other state), named; and the planned bolts and queued units, counted.

Why these and not sluice's queue on main: record 0038's context lists what the page's data already holds and adds no read of main beyond it; the board names what waits on a main as bolts proven and waiting to land, which is what reaches it next through crew. A landing older than the window is not looked for: the record's window is the board's (`record.when`), and a read of the whole record for one line is a cost the page is made every thirty seconds with.

### 4. A team: its bolt, its slots and its conductor's wait

Each team in the teams file's order: `team`, `host`, `session`, `account`, `kits`; its held bolts from `construction` (the bolt, its `board.pips`, `board.merged`, `board.state_said`); `slots`, one per slot `unit-1` to `unit-<units>` (`fleet["teams"][t]["units"]`), each:

- **at work** when the partition's entries hold a `stage.start` not refused naming `agent/<team>-unit-<n>` with no later `stage.end` naming the same `stage/...` object (for a fix, the same `fix/...` object and agent): `{state: "work", stage, kind, name, since}`;
- **holding** when a unit, chore or fix of its held bolt names that slot (`board_data`'s `slot`) and no stage runs: `{state: "held", kind, name, stage}`, the stage the board reads for it;
- **free** otherwise.

`at_work` counts the slots at work. The conductor's wait, `waits`, is the first that holds of: `stages`, the stages running, counted and named; `landing`, when a bolt it holds waits to land, with its card open or none; `nothing`, its bolt's units neither running nor waiting to land, or no bolt held. Said: "waits on 1 stage: code of x", "waits on the landing, its card open", "waits on nothing".

Why from the run record: a stage's start and end reach the branch as they are written (`read.5`), so whether a slot is at work is read where every view reads it, with no herdr reading of a pane on any host; a team's stages file, which `crew needs` reads, is on its host alone. A stage started before the record's window and still running is not seen, and its slot reads holding: the window is seven days and no stage runs so long without crew calling it stuck (`teams.4`).

### 5. The template, its links and the back link

`plugin/lib/fleet.html`, a second template beside `page.html`, with one placeholder for the data, `/*{{DATA}}*/`, filled by `page.render`'s escaping (a shared helper), so nothing in the data ends its block. Its colour tokens, light and dark, are `page.html`'s own, copied, and a logic case holds the two `:root` blocks equal so they cannot drift; its blocks are a grid of partitions side by side on a desktop and stacked under 760 px, as the lanes are. Its script draws every text with `textContent`, holds no `innerHTML`, `fetch`, `XMLHttpRequest` or `WebSocket`, and no control but links.

Links, decided in Python (`fleet_links(path, labels)`) and set in the data: written as `index.html`, each partition `<label>.html` beside it; as `page.html`, `<label>/page.html`; any other name, none, and `crew page --fleet` prints that the partitions are not linked. A team's link is its partition's link with `#dock=team:<name>`, the address the dock keeps. Back from a partition's page, `nav` puts a link to the fleet page before the partitions (`fleet_back(path, label)`): `index.html` beside a page whose file alone is named for its partition, `../page.html` from a `page.html` in a folder named for it, none for any other layout, as the partition links are none when crew cannot tell (`read.1`).

Why a second template and not a view of `page.html`: the partition page's script draws one partition's lanes, dock and deploys from data the fleet page does not carry; one file for both would carry each one's script in the other. Why `index.html` for the served layout: a server answers a folder's root with it, and on disk it opens as a file, where a link to `./` opens a listing.

### 6. What the command prints

As `crew page` does: the path written, then a header, `as of <time> · <label> <commit>` for each partition, then a line for each host or plan that did not answer, by partition, and the line saying the partitions are not linked when the file's name gives no layout. It exits 0 when a page was written, as `crew page` does with a host silent; it writes nothing and refuses only when the teams file cannot be loaded.

## Risks / Trade-offs

- [The read of every partition takes the sum of each one's] → About 2.4 to 4.7 s a partition from mac-studio (record 0010's reading); three partitions fit swancloud's thirty seconds and its maker's two-minute limit, and one read is shared across partitions on one host.
- [A team's slots read from the record differ from its stages file for a moment] → The record is written at the stage's start and end on the team's host and carried to the branch with that write (`read.5`); the page is made again within thirty seconds.
- [Two templates share their tokens by copy] → A logic case holds the two `:root` blocks equal.
- [A last landing older than seven days is not shown] → Said as none since the window's start, never blank; the partition's page and `crew trace` read further back.

## Migration Plan

None in crew: the flag is new and the partition page gains one link. The fleet page reaches the board when swancloud's maker writes it as `index.html` and its server answers the root with it; until then it is a file crew writes on request.

## After deploy

None: every scenario is proved in crew's tiers, and serving the page is swancloud's, outside this change.

## Task notes

**1.1** `plugin/lib/page.py`: `fleet_data(fleet, bd, logs, now)` and its helpers, as Decisions 2 to 4; `tests/py/test_fleet.py`, a new file, its fleet built as `tests/py/test_page.py`'s and `test_board.py`'s fixtures are (teams and hosts as plain dicts, `board_data`'s shape for the board): three partitions in order, each with `plan` and `unread`; a host that did not answer named with its why; deneb's sessions swancloud (design agent, planner, ops, operator, account madswan) and swancloud-2 (crw-6, account madswan-2); a session with no account said so; a session of the partition no agent runs in left out; a dispatcher named on a team's host away from the main level.

**1.2** Kits and teams: a kit's last landing from two `bolt.land` entries of it and one of another kit, the newer taken, a refused one passed over; a kit with none said none since the window's start; a bolt waiting to land with its card open, one in construction, one planned and one unit queued, each counted under its kit; a slot at work from a `stage.start` with no end, one holding a unit whose verify ended, a fix's slot at work, a free slot, `at_work` 2 of 4; the conductor waiting on stages, on the landing, and on nothing for a team with no bolt; attention in `board.attention_text`'s words and the count of open cards.

**2.1** `fleet_links(path, labels)` and `fleet_back(path, label)` in `page.py`, and `nav` taking the back link before the partitions: cases in `tests/py/test_fleet.py` for `index.html`, `page.html`, `fleet.html` (none), and in `tests/py/test_page.py` for the back link from `<f>/swancloud.html` (`index.html`), from `~/.local/state/crew/swancloud/page.html` (`../page.html`), from `<f>/wldn/wldn.html` and `<f>/board.html` (none); a team's link holding `#dock=team:crw-6`.

**2.2** `plugin/lib/fleet.html` and the fleet page's render: the data placeholder once, filled by the same escaping as the partition page's (move `render`'s escaping into a helper both use); `:root` tokens equal to `page.html`'s, read from both files; no `innerHTML`, `fetch`, `XMLHttpRequest`, `WebSocket`, `src=` or `<link`; the phone rule at 760 px; an attention item holding `</script><b>here</b>` kept as text in the rendered data block. Cases in `tests/py/test_fleet.py`.

**3.1** `crew page --fleet` in `page.py`'s `main` and `page()`: `--fleet` or a label, one and not both, refused in words naming both; `--since` refused with `--fleet`; the default path `record.ROOT / "page.html"`; printing as Decision 6. In `tests/t-journey-board.sh`, beside its `crew page` case: `crew page --fleet` writes `$HOME/.local/state/crew/page.html`, prints its path and each partition's header line, its data names every partition of the stub teams file in order and links wldn to `wldn/page.html`; `--out "$T/served/index.html"` links `wldn.html`; `--out "$T/served/fleet.html"` prints that the partitions are not linked; the earlier case's host that does not answer is named by the fleet page too; and `crew page wldn --out "$T/served/wldn.html"` holds a link to `index.html`. Its `# Reads:` line gains `plugin/lib/fleet.html`; run `tests/moon-tasks` and commit `tests/moon.yml`.

**3.2** `plugin/bin/crew`'s usage for `crew page` (`--fleet [--out <file>]`), README's `crew page` paragraph and its usage line, and `plugin/skills/crew/SKILL.md`'s row: the fleet page, what each partition's block shows, its links in both layouts and the partitions' link back. `tests/t-docs.sh` passes.
