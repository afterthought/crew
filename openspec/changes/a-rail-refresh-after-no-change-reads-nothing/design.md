# Design

## Context

This builds on the host's follower as `crew-opens-no-tab-the-user-does-not-use` left it on main (448c543, taken into this bolt at d2e95582). The follower is `board.py`'s `Follower`, run by `crew _follow` as the host's job or by a rail tab's loop where no job runs, one to a host under its lock. Today each of its rounds, for each partition with an operator session on the host (`labels_here`):

- runs `moved_at()`, which forks `git rev-parse HEAD` in crew's checkout, and `crew _update` when that or the teams file moved;
- runs `crew _views <label>` as a child process, a whole `flow_read`: `plan.rail_read` fetches the state branch (`plan.fetch`), reads the plan, proposals, moves and run record with a `git show` or `ls-tree` per file, surveys every team's kits with `board=True`, which no `Reading` serves (`survey`'s `have = {} if sites ...`), so every kit is gathered afresh, here in-process with dozens of git calls per kit and on another host over ssh, then fetches the blueprints repo for signals, and sweeps cards (Pending You), card sessions (an ssh and a `crew card sweep` per host) and batches.

It does that every `PERIOD` (30 s) and whenever a `crew events --follow` child it keeps per partition prints an entry; each of those follows fetches its branch every five seconds (`record.follow`). On deneb that came to 609 processes a refresh (proposal, Why).

The ruling is `plan.12`'s reading of 2026-10-28 (the proposal quotes it), with `state.4` (a follower's kept read is a derived cache, remade whenever what it was read at moves), `read.1` (never read as a fact once moved; what can't be read is not taken as unmoved) and `read.5` (the run record from the branch alone). Pages whose areas this touches: `plan.md` (`plan.py`, `gather.py`), `teams.md` (`plugin/bin/crew`, `crew.py`), `record.md` (`record.py`), `tests.md` (`tests/`) and `docs.md` (README, `openspec/`).

## Goals / Non-Goals

**Goals:**
- A refresh with nothing moved starts no process on this host, and asks another host only for its check.
- A refresh after a change reads each moved part once and nothing else.
- One read per refresh for every partition on the host.
- Fetches on a one-minute clock, shared by the follower and `crew events --follow`.

**Non-Goals:**
- Commands other than the follower and the follow: `crew rail`, `crew board`, `crew status` and waits read as they do (`plan.12` already holds them to one read each).
- sluice's watchers (swancloud-ops's signal; sluice's side).
- Keeping anything across the follower's life: what it keeps dies with its process (`state.4`).
- Facts outside crew's files that no check can see without a process: which dev servers portless lists, whether Pending You still finds a card, whether herdr lists an asker's agent, a batch made due by hours alone. They stand from the last read until something moves (Risks).

## Decisions

### 1. The check: a stamp of everything the read rests on, read with no process

The follower's check is a decision on plain facts (`code.7`): `moved(kept, now)` compares the stamps its last read was made at with the stamps now, and names the parts that moved. The stamps:

- **Each partition's state tip and blueprints tip**, as this host's bare caches hold them, `refs/crew/<label>/main` and `refs/crew/main`, read from the cache's files: the loose ref, else its line in `packed-refs`. Only when neither holds it is `git rev-parse` run, and its answer used (`read.1`: never a guess).
- **crew's checkout and the teams file**: crew's `HEAD` read from its files (the worktree's `.git` file to its gitdir to `HEAD`), the teams file's bytes, as `moved_at` reads them now less the fork.
- **Each kit's stamp** on each host the read surveys, from `gather.stamp(kit)`: the size and time of every file under the kit's git common dir that the gather reads through git (`HEAD`, `packed-refs`, every loose ref under `refs/`, `config`, each `worktrees/<w>/HEAD` and `gitdir`), every file of each place's change folder and of its places' `openspec/changes/archive` listing, and each slots file the request names, hashed to one value. It reads with `os.stat` and `os.scandir` alone. On this host `gathered` runs it in-process; on another, one ssh per host pipes `gather.py` a `{"stamp": true}` request, as a gather is piped now. A host that does not answer gives no stamp, and every kit on it counts as moved (`read.1`); the read then names it as today (`read.3`).

The stamp is wider than "refs": a task ticked and not yet committed moves `tasks.md`, which the gather reads (the bolt-plan spec's "A wait sees what changes while it waits"), so leaving it out would read the kept answer as a fact after what it rests on moved, which `read.1` forbids.

Considered: `git for-each-ref` and `git status` per kit, rejected as the forks this change removes; file system events (`fsevents`, `inotify`), rejected as a mechanism no tool of the host holds and as unavailable on a remote host without a process of its own there (`roles.5`, `roles.6`).

### 2. The follower keeps its read, keyed by the stamps, and reads only what moved

The follower makes its read in its own process, no longer as a `crew _views` child, and keeps it between refreshes: the parts and the stamp each was read at. Each refresh:

1. Computes the stamps (Decision 1).
2. **Nothing moved:** reuses its last read whole. It renders each partition's rail (`plan.rail_text`), board (`board_data`) and agents' views (`agent_views`, with `here_read` kept by crew's `HEAD`, the teams file, the starts and hold files' stamps) at the time now, and writes the frames with `read_at` set to this refresh's time: the frame says when the follower last confirmed it. No sweep runs, but the card session sweep on a host the last refresh could not check (Decision 5).
3. **Something moved:** runs `rail_read` for every partition with the kept parts handed in: `plan.READ` holds the kept state tips (no fetch, Decision 3), each unmoved state branch's files by blob (below), and each unmoved kit's answer, which `survey` serves for a board survey too when the kit's stamp and request are unchanged; a moved kit is asked of its host alone, in one gather per host of the moved kits. Then the sweeps run as today against the new read, and the frames are written.

The state branch's files are kept by blob: one `git ls-tree -r <tip>` at a moved tip names each file's blob, and only a file whose blob changed is read again, through one `git cat-file --batch` per refresh, so a moved tip with one new entry reads that day's run-record file, not a week of them. `plan.show` takes its text from the kept blob when the blob is unchanged.

Rows, rail text and board data are computed from the parts in-process as today. A part kept is never consulted once its stamp moves: the cache is keyed by stamp, so a moved stamp misses (`state.4`, `read.1`).

Considered: a cache file under `~/.cache/crew`, rejected as a second copy of state to keep honest and nothing a follower in one process needs; keeping `crew _views` children with a cache passed in, rejected as a process per partition per refresh.

### 3. One clock: fetch once a minute, look at the caches every second

`PERIOD` becomes 60 seconds. On each tick the follower fetches, for every partition it follows, the state branch and the blueprints main (`plan.fetch(..., fresh=True)`), then refreshes. Between ticks, once a second, it reads the state and blueprints caches' tips and crew's checkout and teams file from their files (no process); when one moved, after `BURST` for what follows, it refreshes at once, fetching nothing. A write on this host moves its cache's tip when it lands (`plan.land`'s `update-ref`), so the user's approve redraws the rail within seconds, as the operator-agent spec asks; another host's write shows at the next tick. Kits are stamped at each refresh, not each second: a kit's move with no entry shows within the minute.

The `crew events --follow` children go: the follower's one-second look at the cache replaces them as its wake.

`SIGUSR1` makes the follower's next tick at once, and a follow's likewise: the tiers move the clock rather than wait for it (`tests.md`'s rule that a test moves time), and it is harmless to send by hand.

### 4. One read for every partition on the host

A refresh reads all of `labels_here` at once: `rail_read(fleet, labels, board=True, sweep=True)` already takes several labels, and `survey` merges every team's kits by host, so a kit shared by two partitions is gathered once. Each partition's frames are made from the one read: `board_data(fleet, [l], read, now)`, `rail_text(fleet, [l], read, now)` (made to take one label of a read of several, rows and cards filtered by it), `agent_views`. What the refresh says on standard error goes into the rail frame of each partition it read, as each partition's own round put its words there before. The due restarts are still handed out per partition by `crew _update --label <l>` when crew's checkout or the teams file moved; then the follower re-executes itself (`os.execv`, keeping the lock's descriptor open across it), so the new crew runs the next refresh and the kept read goes with the old process.

### 5. Sweeps after a change, and only the unchecked hosts after none

The card sweep, the moved-landings sweep, the session sweep and the batch reckoning judge facts read from the plan, the record and the kits (card-sessions spec), so after nothing moved they would judge the same facts as last time: they do not run. One exception: `sweep_sessions` left `unchecked` hosts (one that did not answer); a no-change refresh runs the session sweep on those hosts alone, with the kept judgment, so a session a host's silence kept alive is ended when it answers. The rail of a no-change refresh lists the sessions this refresh ended, none but those, and the hosts still unchecked.

### 6. `crew events --follow` on the clock

`record.follow` reads each label's tip from the cache's files every second, and when it moved, `ls-tree` once and reads only the day files of the follow whose blob changed. It fetches each label on a 60-second clock of its own, only for a label the host's follower does not fetch: a label not in `labels_here`, or any label while `follower_here()` is `none`. The first read fetches once, as today, so the follow's start sees the branch as GitHub holds it.

## Risks / Trade-offs

- [A fact outside crew's files changes with nothing moving: a dev server started by hand, a card Pending You lost, an asker's pane emptied, a batch due by hours] → it shows at the next refresh after anything moves. On a working host something moves every few minutes; on an idle one nobody is waiting on these. Whether any of them needs a slower clock of its own is the design agent's to say; none is built here.
- [A remote host's check is still one ssh a minute per host] → it is the check `plan.12`'s reading allows; it replaces a whole gather there.
- [An entry from another host shows up to a minute late, where it was five to thirty seconds] → the reading's clock; a write on this host is still at once.
- [The kept read grows with a long-lived follower] → it holds one read and the blobs of one week's run record per partition, replaced as they move.
- [A frame's `read_at` now means "confirmed at"] → the frames' shape and the mod are unchanged (`code.8`); what the tab says when stale is still right, since a stopped follower stops confirming.

## Migration Plan

None beyond landing: the follower is restarted by the host's job when crew moves (`teams.19`), and a rail tab re-runs its command at the next `crew console up`.

## After deploy

None: every behaviour here is pinned by the logic, contract and end-to-end tiers on the stubs, and the host's job running `crew _follow` is swancloud's.

## Task notes

**1.1** `plugin/lib/board.py`: a decision `moved(kept, now)` over stamps `{"crew": (head, teams), "state": {label: tip}, "blueprints": {label: tip}, "kits": {(host, main): stamp or None}}`, returning which partitions' state and blueprints moved, which kits moved (a `None` stamp, unreadable, counts as moved), and whether crew moved. Cases in `tests/py/test_board.py`: nothing moved; one state tip; one kit; an unreadable kit; crew's head.

**1.2** `plugin/lib/gather.py`: `stamp(req)` for one kit, `os.stat`/`os.scandir` only, and `{"stamp": true}` in `__main__` answering `{main: stamp}`; `plugin/lib/plan.py` `stamped(fleet, host, kits)` in-process on this host, piped on another. Contract cases in `tests/contract/test_gather.py`, each against a scratch kit: the stamp moves on a commit in a place, a fetch that moves a remote ref, a task ticked in a place's `tasks.md`, a place made and removed, a line written to a slots file, a fix branch's config changed; it stays when nothing changed, and `stamp` starts no process (`subprocess` patched to raise).

**1.3** `plugin/lib/plan.py`: a `tip_here(repo, ref)` reading the cache's ref from its files (loose, then `packed-refs`), `git rev-parse` only when neither holds it; `plugin/lib/crew.py`: crew's `HEAD` from its files. Contract cases: a loose ref, a packed ref after `git pack-refs --all`, a detached worktree's `HEAD`.

**2.1** `plugin/lib/plan.py`: `READ` serves a board survey's unmoved kits when the follower hands them in, keyed by (host, main, stamp, request); `rail_read` and `plans`, `open_proposals`, `rail_record`, `signals` read state files through `show`, which serves an unchanged blob from what the follower kept (one `ls-tree -r` per moved tip, one `cat-file --batch` per refresh). Logic cases where they are decisions (which kits to ask of which host, from the stamps); the wiring in 3.x.

**2.2** `plugin/lib/board.py` `Follower`: the refresh of Decision 2 in its own process for all of `labels_here` (Decision 4), frames written per partition, standard error captured into each; `follow_round` and the `crew events --follow` children go; `_update` then `os.execv` on crew's move, with the lock's descriptor made inheritable. `rail_text` takes one label of a several-label read. Logic cases in `tests/py/test_board.py` for the refresh's plan (render only, read parts, which sweeps) from `moved`'s answer.

**2.3** `PERIOD = 60`, `STALE = 3 * PERIOD`; the one-second look at the caches' tips (Decision 3); `SIGUSR1` makes the next tick now. Logic case: the tick's due time and the look's wake from plain times and tips.

**2.4** Decision 5: a no-change refresh runs `sweep_sessions` on the kept read's unchecked hosts alone. Logic case in `tests/py/test_rail.py` or `test_board.py`: unchecked `{box}` and nothing moved → the box alone asked.

**3.1** `plugin/lib/record.py` `follow`: Decision 6, `SIGUSR1` making its fetch now; the fetch decision `follow_fetches(label, followed_here, follower, last, now)` a function of facts. Logic cases in `tests/py/test_record.py`.

**3.2** `tests/t-journey-state.sh`, the follow's case: the entry the box pushes appears after a `kill -USR1` of the follow, not by waiting; a shim on git counts the follow's fetches: one at its start and one per signal, none otherwise.

**4.1** `tests/t-journey-board.sh`: `crew _follow --once` writes wldn's and swancloud's frames from one read, the box's kits gathered once (`reads $box gather` 1 for both). Then a running `crew _follow` in the background (killed at the end), its first refresh waited on by the rail frame's `read_at`; with the shims counting every git, every `python3 -` and every ssh: `kill -USR1` with nothing moved writes the frames again with a later `read_at`, 0 git and 0 gather on mac-studio and one stamp request to the box; then a plan write on mac-studio (`crew plan propose`) moves the cache and the next refresh, within the one-second look, fetches 0, gathers 0, and reads the plan at the new tip, its rail showing the proposal.

**4.2** README (the follower's paragraph, the run record's `--follow`), `plugin/skills/crew/SKILL.md`, `plugin/bin/crew`'s usage of `_follow` and `events --follow`, `board.py`'s and `record.py`'s headers and `status.js`'s comment say once a minute, at once for this host's writes, three minutes to stale (`docs.2`). The mod's cases still pass with the views' shape unchanged.
