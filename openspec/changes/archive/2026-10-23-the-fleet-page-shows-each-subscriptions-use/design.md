# Design

## Context

This unit is built on `the-fleet-page-shows-every-partition-at-once`, which gives crew the fleet page: `crew page --fleet` (`plugin/lib/page.py` `fleet_page`) makes one board read of every partition, turns it into the fleet's data with `fleet_data(fleet, bd, logs, now)`, a decision on plain facts, and writes it into `plugin/lib/fleet.html`, one file that loads nothing. Each partition's block already names, under each host, the herdr sessions its agents run in and the Claude account the hosts file gives each (`where`), and each team its slots at work and what its conductor waits on (`fleet_team`).

Record 0038 §5 rules the rest: every few minutes each Mac reads, for each Claude account signed in on it, what Claude Code's `/usage` reads, the five-hour and seven-day utilization with their resets, by model where given, and publishes the numbers alone where crew's page reads them, the credential never leaving the host; the fleet page shows them per subscription with the sessions and partitions on it and how old the reading is, marks a reading a host could not make, and computes nothing beyond setting a subscription's use beside the work of the sessions on it. The reader is swancloud's unit `a-mac-publishes-its-sign-ins-usage`; §6 makes the board on deneb. The record names where the numbers are published only as "where crew's page reads them", so this change fixes crew's side of it: the folder and the shape crew reads (Decision 1), which swancloud's reader writes.

What Claude Code reads, from its 2.1.308 bundle on mac-studio, 2026-10-23 (record 0038 read 2.1.307 for the same names): the usage endpoint `api/oauth/usage` answers windows `five_hour`, `seven_day`, `seven_day_oauth_apps`, `seven_day_opus` and `seven_day_sonnet`, each `{utilization, resets_at}` or null, `utilization` a percentage 0 to 100 or null and `resets_at` an ISO 8601 time or null; and `model_scoped`, a list of `{display_name, utilization, resets_at}`, a per-model weekly window the server labels ("e.g. 'Fable'"), absent when nothing is known of them. These are the names of Claude Code's structured `/usage` data, `rate_limits`, which it marks experimental.

Rules this design rests on: `state.4` (the page reads files and writes only itself; no service), `read.1` and `read.2` (what crew cannot read is named, an absent field never becomes text, a missing figure is said not given), `read.3` (a host whose use is missing or unreadable hides nothing else), `read.5` (crew reads no host over ssh for this: the readings reach the page's host by swancloud's hand), `code.1` (standard library; plain script in the one file), `code.4` (an account named in a reading matches crew's names), `code.5` (accounts and sessions from the hosts file as crew loads it, read, never written, no field defaulted), `code.7` (what the page says of a subscription is a function of plain facts, proved in the logic tier), `code.8` (subscriptions are not among what the agents' views draw: `board.agent_views` and `plugin/hooks/status.js` are unchanged), `tests.4`, `tests.10` and `tests.11` (logic cases for every decision, the read's wiring in the board journey), `docs.2` (README, the skill and the usage together). The change touches the areas of `tests.md` (`tests/`), `docs.md` (`README.md`) and `teams.md` (`plugin/bin/crew`'s usage text alone).

## Goals / Non-Goals

**Goals:**

- Every subscription on the fleet page with its use as the host holding its sign-in published it, who read it and how long ago, a failed or missing reading said so.
- The sessions, agents, teams' work and partitions on each subscription beside its use.
- A published shape simple enough for swancloud's reader to pass Claude Code's numbers through unchanged.

**Non-Goals:**

- Reading the use: swancloud's reader, its cadence, the credential, and how the files reach the board's host.
- Any judgment of efficiency: a ratio, a grade, a colour by level, a sum across subscriptions or a forecast (record 0038 §5).
- A dock on a subscription (record 0038 §2 lists one): the fleet page has no dock yet.
- `seven_day_oauth_apps` and the extra-usage spend: neither is the five-hour or seven-day use nor a model's.
- Any change to `crew board`, its JSON or the agents' views.

## Decisions

### 1. Where and in what shape crew reads the use

The fleet page reads every `*.json` file of `~/.local/state/crew/usage/` (`record.ROOT / "usage"`) on the host it is made on, each one host's readings, the file named for the host:

```json
{"host": "deneb",
 "readings": [
  {"account": "madswan", "at": "2026-10-23T11:58:04Z",
   "five_hour": {"utilization": 34.0, "resets_at": "2026-10-23T14:00:00Z"},
   "seven_day": {"utilization": 61.0, "resets_at": "2026-10-27T09:00:00Z"},
   "seven_day_opus": null,
   "seven_day_sonnet": {"utilization": 20.0, "resets_at": "2026-10-27T09:00:00Z"},
   "model_scoped": [{"display_name": "Fable", "utilization": 40.0, "resets_at": "2026-10-27T09:00:00Z"}]},
  {"account": "credits", "at": "2026-10-23T11:58:06Z", "unread": "the usage endpoint answered 401"}]}
```

`account` is the name the hosts file gives the sessions on that sign-in; `at` when the host read it, or tried; a reading holds either the windows, under Claude Code's own names, or `unread`, the host's words for why it could not read. Any window may be absent or null.

crew checks each file before it uses any of it (`read.2`): an object whose `host` is the file's name and whose `readings` is a list, each reading an `account` matching `code.4`, an `at` that is an ISO time, and either an `unread` string or windows each null, absent, or `{utilization: number or null, resets_at: string or null}`, `model_scoped` a list of such with a `display_name` string. A file that is not JSON, or not of the shape, is unreadable as a whole, named with what is wrong, and none of its readings used; the other files are read (`read.3`). A missing folder is a folder with no files.

Why a folder of one file per host: the reader on each host writes its own file whole, so no two hosts write one file; a host whose file stops being refreshed shows its age. Why on the page's host and not read by crew from each host: `read.5` keeps ssh to a host's kits' stages, and record 0038 §5 has the hosts publish; carrying the files to the board's host is swancloud's, as serving the page is. Why Claude Code's field names: the reader passes the endpoint's numbers through with nothing renamed, as §5's "the numbers alone" asks. Why no flag for another folder: swancloud's maker runs `crew page` with the board host's own home, and the default is where crew keeps the rest of its state; a flag can come when a second place is wanted. Considered: readings in the run record or the plan, written by a crew command on each host every few minutes, which `state.1` would carry but which fills the flywheel's branch with numbers no decision reads.

### 2. Which subscriptions, and which reading each shows

`subscriptions(fleet, usage, teams, now)` in `page.py`, a function of the fleet crew loaded, the files read (`{host: data or the words for why it is unreadable}`), the fleet page's teams as `fleet_team` gives them, and the time. The subscriptions are every account any session of the hosts file names and every account a readable file holds a reading of, sorted by name; a subscription is an account name, as the hosts file and Claude Code's account folders name them.

For each, its readings from every readable file, newest first by `at`. Its figures are those of the newest reading made (no `unread`), its host and age said: "read by deneb 2 min ago", the age in whole minutes before the page's `made.at`, "under a minute" below one, hours and minutes past sixty. Every other reading is listed under it: "mac-studio read 9 min ago", or "mac-studio could not read 4 min ago: <its words>". With no reading made: `state: "unread"`, "its use could not be read", each failed reading listed. With none at all: `state: "none"`, "no host has published its use".

### 3. What a reading's figures say

Each window said as published, the percentage rounded to a whole number and the reset in the page's own form, `HH:MMZ` when it falls on the page's day and `YYYY-MM-DD HH:MMZ` otherwise: "five-hour 34%, resets 14:00Z", "seven-day 61%, resets 2026-10-27 09:00Z". `five_hour` and `seven_day` are always shown, "five-hour not given" when absent, null or without a utilization; a reset that is null is left off its line. By model: `seven_day_opus` as Opus and `seven_day_sonnet` as Sonnet, then each of `model_scoped` by its `display_name`, in the reading's order, each only when present and not null, "Fable not given" when its utilization is null. Each window keeps its number for the bar the page draws (`pct`, 0 to 100, or null), clamped to that range for the bar's width alone.

Nothing else is made of the numbers (record 0038 §5): no colour by level, no total, no rate. The bar is one colour, its width the percentage.

### 4. The sessions and partitions on a subscription

`where`'s reckoning of which agents crew starts in which session moves into a helper, `agents_in(fleet, label)`, `{(host, session): [agent]}`: each team by its `machine` and `session`, each main-level role of `MAIN_STANDING` in `p["sessions"]` on `p["machine"]`, the dispatcher in `crew.dispatch_place` on each host the partition's teams run on. `where` reads it for its own host; the subscriptions read it for every partition.

A subscription's sessions are every session of the hosts file whose `account` is it, by host in name order and each host's sessions in the file's order, each `{host, session, agents, teams}`: its agents across every partition, teams first, then main levels' roles, then dispatchers, partitions in the teams file's order; and for each team among them its `at_work_said` and its `waits.said`, taken from the fleet page's own `fleet_team` result for it, so the two parts of the page cannot disagree. A session no crew agent runs in says "runs no crew agent". Its partitions are those with an agent in any of its sessions, in the teams file's order, each with the link its block has. A session the hosts file names no account for is on no subscription; the partition's block already says so.

### 5. The subscriptions section

`fleet_data` gains the files read as an argument and the key `subscriptions`, `{"said": ..., "items": [...]}`, beside `partitions`, and `unread_usage`, `[{host, file, why}]`. In `fleet.html` the section stands above the partitions' grid, headed "subscriptions" in the page's `.sec-h` form, its subscriptions a grid of cards side by side on a desktop and stacked under 760 px as the partitions are: each card its account name, its source line ("read by deneb 2 min ago" or the marked state, in `--warn` for a reading not made and `--ink3` for none), a row per window with its words and a plain bar, the other hosts' lines, then its sessions and partitions in the forms of a partition's sessions list. An unreadable file is a `.mark.attention` above the cards. Every text is set with `textContent`; the bar's width is set from `pct` through `style.width`, a number, never markup.

### 6. What the command prints

After what `crew page --fleet` prints today: a line for each unreadable file, "the use published in <file> could not be read: <why>", and, when the folder holds no file, "no subscription's use is published in <folder>". It still exits 0 with the page written: a reading is the board's to show, not a reason to write nothing.

## Risks / Trade-offs

- [Claude Code marks its `/usage` data experimental, and its windows may change] → crew reads only the names above, every one optional; a window the reader stops sending is said not given, and a new one is not shown until crew names it. `model_scoped` carries the server's own labels, so a new model's window arrives without a change to crew.
- [Two sign-ins of one subscription under two account names show as two subscriptions] → crew can tell a subscription only by the account name the hosts file and the reader share; both show the same figures, each with its own sessions.
- [A host off the network leaves its last file in place] → its readings' age says how old they are, and a newer reading of the same account from another host is the one shown.
- [The age is reckoned when the page is made] → the page is made every thirty seconds and its header says when.

## Migration Plan

None in crew: the section reads a folder that is empty until swancloud's reader fills it, and says so. Once `a-mac-publishes-its-sign-ins-usage` writes `~/.local/state/crew/usage/<host>.json` on the board's host in the shape of Decision 1, the figures appear on the next page made.

## After deploy

None: every scenario is proved in crew's tiers from files in the shape of Decision 1, and reading and carrying the use is swancloud's, outside this change.

## Task notes

**1.1** `plugin/lib/page.py`: `usage_files(folder)`, the thin read, `{host: data}` for each `*.json` file parsed, or the words for why it could not be (not JSON, could not be opened); `usage_checked(files)`, the decision, the checks of Decision 1, returning `(readings, unread)`, readings `[{host, account, at, unread, windows}]` and unread `[{host, file, why}]`. Cases in `tests/py/test_fleet.py`: a file of two readings, one made and one not; a file whose `host` is not its name; a reading with an account holding a capital; a window whose utilization is a string; `model_scoped` not a list; a file not JSON; each bad file named with its why and the good file's readings kept; a missing folder (through `usage_files` on a `tmp_path` that does not exist) giving nothing.

**1.2** `subscriptions(fleet, readings, teams, now)` and its sayings, as Decisions 2 and 3: cases for the order of accounts from sessions and readings (the spec's first scenario); the newest made reading shown and the other host listed with its age; a reading made and a newer one not, the made one's figures shown and the failure listed; only a failed reading, `state` unread with the host's words; no reading, `state` none; the madswan scenario's windows, a reset on the page's day said `14:00Z` and one on another day with its date, Sonnet and Fable shown and Opus not; five-hour with null utilization said not given; a `pct` of 104 kept as said and clamped for the bar; ages "under a minute", "2 min ago" and "1 h 5 min ago". Extend the module's `FLEET` with deneb's session agentplot-2 on madswan, no agent of any partition in it.

**1.3** `agents_in(fleet, label)` taken out of `where`, `where` unchanged in what it returns (its existing cases pass as they are), and the sessions and partitions on a subscription as Decision 4: madswan's sessions madswan (mad-1, with its slots at work and its conductor's wait as `fleet_team` says them) and swancloud (swancloud's main-level roles), agentplot-2 running no crew agent, the partitions madswan and swancloud with their links; madswan-2's session swancloud-2 with crw-6; a session with no account on no subscription.

**2.1** `fleet_data(fleet, bd, logs, usage, now)` with `subscriptions` and `unread_usage`, and `fleet.html`'s section as Decision 5: a case renders the fleet page and holds the section's script setting text by `textContent` only, still no `innerHTML`, `fetch`, `XMLHttpRequest`, `WebSocket`, `src=` or `<link`; an `unread` reason holding `</script><b>here</b>` kept as text in the data block; the 760 px rule covering the subscriptions' grid.

**2.2** `fleet_page` reads `usage_files(record.ROOT / "usage")` and prints as Decision 6. In `tests/t-journey-board.sh`, in the fleet page's case: before the first `crew page --fleet`, the folder absent, the command prints "no subscription's use is published in $(home_of mac-studio)/.local/state/crew/usage" and each subscription's `state` is `none`; then write `mac-studio.json` in the shape of Decision 1, a reading of `ia`, the account the stub hosts file gives its sessions (`tests/lib.sh` `sess`), with its windows, and one of `credits` with `unread`, and `$box.json` holding `not json`, under mac-studio's `~/.local/state/crew/usage/`: the data holds ia's five-hour figure and `read by mac-studio`, credits' `state` unread, and the command prints that `$box.json`'s use could not be read. Run `tests/moon-tasks` and commit `tests/moon.yml` if the test's reads change.

**3.1** `plugin/bin/crew`'s usage text for `crew page --fleet` and `page.py`'s docstring, README's fleet page paragraph, and `plugin/skills/crew/SKILL.md`'s fleet page row: the subscriptions section, what each shows, that it is read from `~/.local/state/crew/usage/<host>.json`, which swancloud's reader writes on the board's host, and what the command prints of it. `tests/t-docs.sh` passes.
