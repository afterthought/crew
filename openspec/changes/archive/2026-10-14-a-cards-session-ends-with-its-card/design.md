## Context

See proposal.md, *Why*. ADR 0005 as amended 2026-10-10 (the point *No card's session outlives its card, whoever closed it*) makes the decision; `briefs.9` says the session ends when the card closes; `read.4` says crew never takes over what it did not make. This change touches the area of `briefs.md` only through the rule it builds; it edits no brief.

Today (`plugin/lib/plan.py`):

- `crew card session` records each session it starts in `~/.local/state/crew/cards/<label>/<key>/session.json` on the host it runs on (a batch card's under `<key>/<unit>/`), with the pid, the document, the link and when it started. A proposal's session runs on the planner's host, the partition's main machine; a verify report's on its team's host; a batch card's, one per unit, on each unit's team's host. A landing's key has none.
- `end_session` ends one: it removes the key's folder, then sends SIGTERM to the recorded pid only while `plannotator sessions --json` lists that pid serving the recorded document (`read.4`). When the list can't be read it ends nothing and still removes the folder, so the process is forgotten and nothing ever ends it.
- The card hook (`plugin/hooks/cards`) calls `end_session` when a crew agent closes or withdraws a keyed card, on its own host only; `crew card end <key>` does the same by hand.
- `rail_read` reads the rows, the open cards (`card.post` with no later `card.close`) and, in `rail_record`, the keys a `card.close` named (`held[label]["closed"]`), and which hosts' record did not answer (`unread`). `stray_cards` already judges which open cards have no row and skips those it can't judge. `crew rail` (`rail_view`) and the rail tab's refresh (`crew _views`, in `board.py`) both print `rail_text` from a `rail_read`; `crew board` reads it too.

## Goals / Non-Goals

**Goals:** every rail read ends the card sessions crew started whose card is closed or whose row is gone, on every host of the partitions read, and says which.

**Non-Goals:** ending a plannotator session crew did not record; making plannotator's page smaller or the tailnet faster (ADR 0005 records both as upstream's and main-ops's readings); `crew board` ending anything; closing Pending You cards, which only their owner can do (the rail already tells the owner).

## Decisions

### The reading host judges; each host ends its own

The rail's read already holds what the judgment needs, the rows, the open cards, the closed keys and what did not answer, so the host running the rail decides which keys are dead, and each host that may hold sessions ends its own. After the rows are made, for each partition whose plan was read, the rail sends one call to each of its hosts, the main machine and each team's machine: `crew card sweep --label <label>`, run there through `crew.on_machine` with `crew.crew_argv` (`code.3`), with the rail's judgment as JSON on standard input:

- `live`: the keys whose session must stay: every row key, less each key the record holds as closed with no card open under it. When the partition's record did not answer whole (`unread[label]` not empty), no key is taken out for being closed.
- `blind`: key prefixes the rail can't judge, whose sessions stay: `verify/<unit>/` for each unit of a bolt whose team's kit could not be read (its host not answering, or the kit not read), and `batch/` while the record did not answer whole.

On its host, `crew card sweep` reads each `session.json` under `~/.local/state/crew/cards/<label>/`, maps the folder back to its key (and unit, for `batch/<n>-<k>/<unit>`), and ends a session only when its key is in no `live` entry and starts with no `blind` prefix, it is at least two minutes old by its own `started` against this host's clock, and its folder's lock is free (`card_session` holds it while it starts one). It ends each through `end_session`, and prints, as JSON, each session it acted on with the words `end_session` gave. A folder with no `session.json`, or whose path is no card key, is left alone.

Considered: each host recomputing the rail itself, which would multiply the rail's reads by its hosts; listing sessions in `gather.py`'s survey, which reaches only hosts holding a bolt and is cached per kit, while the planner's host may hold none; two calls per host, list then end, which doubles the calls on every read to save sending a list of keys.

### Why the rail, and not the board

The ADR says every rail read. `crew rail` and the rail tab's refresh both print the rail; they sweep. `crew board` and `crew board --json` read the same rail but print no rail and promise to write nothing, so they do not sweep: `rail_read` takes a `sweep` flag, set by `rail_view` and by `_views` in `board.py`. With the operator up, the rail tab's refresh sweeps every 30 seconds.

### What is known, and what is not (`read.1`, `read.3`)

A row gone is known for a proposal from the proposals, which are on the state branch; for a verify key from the survey of its team's host; for a batch key from the whole run record. A card closed is known only from the whole record. Whatever the rail can't tell stays, and a later read judges it. A host that does not answer the sweep, or whose crew has no `card sweep` yet, is named, and every other host is still swept. A host the survey already found not answering is not asked again, and is named the same way.

The two-minute grace covers a session started between the rail's read of a kit and its sweep: its row exists, but the read could not have seen it. It is measured on the session's own host, by the time that host wrote, so no clock is compared across hosts.

### plannotator's list unread: keep the record (`read.1`)

`end_session` today forgets a session when it can't read plannotator's list, which leaves exactly the orphan this change ends. It now keeps the folder and says it ended nothing; the hook and `crew card end` print that, and a later sweep ends it. Its other outcomes stay: a pid plannotator lists on another document is not killed and the key is forgotten (`read.4`).

### What the rail prints

After the open cards with no row, and before the hosts that did not answer:

```
card sessions ended:
  proposal/4 (swancloud) on mac-studio: its row is gone; ended proposal/4's session, plannotator pid 4242
  verify/x/20261009-1412 (swancloud) on chuck-herdr-alpha: its card is closed; ended ..., plannotator pid 977
card sessions not checked:
  chuck-herdr-alpha (wldn): did not answer (<why>)
```

Why is read on the rail's side: a key with no row is "its row is gone", else "its card is closed". When the sweep ended nothing and checked every host, nothing is printed.

### Rules

`state.4`: the rail commits and appends nothing; it ends processes crew started and removes their folders under `~/.local/state/crew/cards/`, which are no part of a flywheel's state, as the card hook already does. `read.4`: only recorded sessions, only a pid plannotator lists serving the recorded document. `code.1`: standard library only. `code.2`: refusals through `fail()`. `docs.2`: README, the skill and the usage change together. `docs.7`: this change edits nothing under `docs/`; the design agent clears `_open.md`'s line after the landing.

## Risks / Trade-offs

- [A rail read costs one more call per host] → one ssh per host of each partition; the rail tab already reads every host each refresh. The sweep runs only after the rows are made, so a slow host delays the rail's printing by its ssh timeout at most, as the survey does.
- [A host's crew is older than the rail's] → the call fails and the host is named as not checked; hosts are pulled together after a landing.
- [A session decided but not yet read by its owner is ended] → only once its row is gone or its card closed, when its owner no longer waits on it; `crew card wait` already says a session crew ended.

## Proof in dev

Once the bolt has landed and every host has pulled: on mac-studio, `plannotator sessions --json` before and after one `crew rail --label swancloud` shows each session of a closed card or a gone row ended, and the rail lists each with its host; a session the user starts by hand on any document is still listed after the read; sessions of rows still open keep their links. No check here needs the user.

## Task notes

### 1.1

`crew card sweep --label <label>` in `plan.py`, beside `card_end`, added to the `card` parser's subcommands (it takes no key; a key or unit given is refused). It reads the judgment JSON from standard input, refusing input that is not `{"live": [str], "blind": [str]}`. It walks `CARDS / label` for `session.json` files, maps each folder's path relative to `CARDS / label` to a key that matches `CARD_KEYS` (and the unit, for a batch key), and ends a session only as *The reading host judges* says. The age check reads `started` from the record. Take the folder's `.lock` with `fcntl.flock(LOCK_EX | LOCK_NB)` and skip the session when it is held. Print a JSON list, one object per session acted on: `key`, `unit` (or null), `said` (the words `end_session` returned), `ended` (true only when it sent SIGTERM).

### 1.2

`end_session`: when `plannotator_sessions()` returns no list, return before removing the folder, in words naming why and that the key is kept: `crew can't read plannotator's sessions (<why>): it ended nothing, and keeps <key> to end later`. Read the list before the `rmtree`, as it does now.

### 1.3

In `rail_read`, a `sweep=False` parameter. With it, after the rows: for each label whose plan was read, compute `live` and `blind` as *The reading host judges* says, from `rows`, `cards`, `held[label]["closed"]` (return it from `rail_record`'s `held`, which already holds it), `unread[label]` and the survey; then call each host of `{partition's machine} ∪ crew.partition_hosts(fleet, label)` once, skipping and naming those the survey found down. Put the results in the read: `ended`, each `{label, host, key, unit, why, said}`, and `unchecked`, each `{label, host, why}`, where an `end_session` reply that ended nothing for a reason (plannotator's list unread) is listed under `ended` with its words, since it is what the sweep did. `rail_view` passes `sweep=True`, and `rail_text` prints them as *What the rail prints* shows, reading `ended`/`unchecked` with `.get` so a read without the sweep prints nothing.

### 1.4

In `board.py`, `_views` (the rail tab's refresh) calls `plan.rail_read(..., board=True, sweep=True)`; `crew board` does not. Update both modules' docstrings that say the rail or the refresh writes nothing, to say it ends the dead card sessions and writes no state.

### 1.5

`tests/t-card-sweep.sh`, new: in the world of `t-card-session.sh` (its helpers `rec`, `stub`, `listed`, `settle`, `decide` show how), with sessions on two hosts, one scenario per scenario of the delta's three new requirements: a landed or dropped unit's verify session ended from the other host; a proposal approved with its card still open ended; a closed card with its row still there ended; a session with no card yet kept; a plannotator the test starts outside crew on a closed proposal's page kept; a batch card closed on the main host ends its unit's session on the team host; the rail's lines for two ended, and nothing printed when nothing ended; a host not answering named with nothing there ended and other hosts still swept; a record host not answering keeps closed-card and batch sessions; a session younger than two minutes kept (set its recorded `started` to now). Age a session by rewriting its `started` in `session.json`. Run `tests/moon-tasks` and commit `tests/moon.yml`.

### 1.6

`tests/t-card-session.sh`: the case where plannotator's list can't be read, for `crew card end`: nothing killed, the key's folder kept, the words said; the header comment's "forgets the key either way" says the new behaviour.

### 2.1

README: in the card-session paragraph, that every rail read ends each session crew started whose card is closed or whose row is gone, on every host, leaves alone what it did not start and what it can't judge, and says which it ended; and that a session whose plannotator list can't be read is kept. In the rail paragraph, the new lines after the open cards with no row. The crew skill's table row for `crew rail` and the usage header's `crew rail` and `crew card` lines, `card sweep` named as the rail's, run on each host, not for hand use. `tests/suite t-docs` checks the usage against README.
