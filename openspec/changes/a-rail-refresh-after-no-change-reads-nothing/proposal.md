# Proposal

## Why

On 2026-10-28 on deneb, with every team down, one refresh of crew's rail follower started 609 processes, 404 of them git, and took 17 seconds; it ran every 30 seconds and again at every run-record entry, for each of two partitions, beside three `crew events --follow` fetching every five seconds (signal 2026-10-28-swancloud-planner-0febe4ae/01; swancloud-ops's 2026-10-28-swancloud-ops-cc4c8120/01, which measured crew's followers with sluice's watchers holding deneb at 35–68% CPU). The user asked for the root cause to be fixed in crew. An idle host should cost nearly nothing: nothing has moved, so nothing needs reading.

The design agent ruled what a follower may do (`plan.12`'s reading of 2026-10-28): a view's refresh is a command in `plan.12`'s sense, so what it read at refs and a tip that have not moved stands between refreshes. With no move since the follower last read of anything the refresh acts on, a refresh starts no gather and forks nothing beyond the check that nothing moved; a refresh after a change costs one read of what moved; the state and blueprints caches are fetched on the clock alone, never per event, the clock no faster than a minute; and one follower's reading on a host serves every partition's tab there. What the follower keeps is a derived cache keyed by the commits and refs it read, never state (`state.4`), never read as a fact once they have moved (`read.1`), and the run record is still read from the branch alone (`read.5`).

What moved has to cover every source the refresh acts on, not only refs. Once `crew card wait` is gone (the sibling unit `crew-keeps-no-card-wait-and-a-row-carries-its-submission-number`), the refresh is what tells a card's owner that the user sent a reading back, and it reads each kit's queue in sluice for the rows' submission numbers; a check that left either out would let a sent reading, or a merge that moved in sluice, sit unseen until something else moved.

## What Changes

- **The follower checks before it reads.** Each refresh of the host's follower, `crew _follow` or a rail tab's loop, first checks whether anything it acts on has moved: each partition's state branch and blueprints main as this host's caches hold them; each kit's refs, worktrees, places' changes, slots files and sluice's records in the kit's git folder, on every host it reads; each host's card readings folder, where plannotator writes the reading the user sent back; the cards as Pending You last answered for them on the clock; the teams file; and crew's own checkout. When nothing has moved it starts no read and no process beyond that check: it prints each partition's rail and writes its board and agents' views again from the read it kept, with the time it checked.
- **A refresh after a change reads only what moved.** A moved state tip reads that partition's plan, proposals and run record again at the new tip, and no kit; a moved kit, its sluice records among it, is gathered again alone; a moved blueprints tip reads its signals again; a host whose readings folder moved has its card sessions swept, which is where a sent reading's owner is told; cards whose answers moved are swept. What did not move is taken from the follower's kept read.
- **One read serves every partition on the host.** The follower makes one read for every partition with an operator session on the host, each kit read once however many partitions it serves, and writes each partition's rail, board and agents' views from it.
- **Fetches run on a one-minute clock.** The follower fetches the state and blueprints caches once a minute, and never because an entry arrived; on the same tick, and only then, it asks Pending You about the cards its sweep acts on, in one bridge, and keeps the answers until the next tick. An entry written on this host moves this host's cache at once, so the rail and board redraw within seconds, as today; an entry from another host shows within the minute.
- **The run record's follow joins the clock.** `crew events --follow`, which the console's flow tab runs, reads the branch as this host's cache holds it, rereads it only when its tip moves, and fetches once a minute, itself only for a partition no follower on the host fetches. It no longer fetches every five seconds. The follower wakes on its own check of the cache, not on a `crew events --follow` child per partition.
- **A frame is stale after three minutes**, three of the follower's periods, where it was 90 seconds: the tabs and the agents' bands still say when the follower has stopped.
- Unchanged: the rail's words, the board, the agents' views and their shape, the card sessions a refresh after a change ends, `crew rail`, `crew board`, `crew events` without `--follow`, the follower lock and who follows.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `crew-board`: the host's follower reads once for every partition on the host, reads nothing when nothing moved and only what moved otherwise, and fetches on a one-minute clock.
- `run-record`: `crew events --follow` reads the branch as this host's cache holds it and fetches once a minute, not every five seconds.
- `operator-agent`: the console's flow tab shows an entry from another host within a minute, and one written on this host at once.
- `bolt-plan`: the host's follower and `crew events --follow` read again only what moved since they last looked, where they read everything afresh each time.
- `card-sessions`: a refresh sweeps a host's card sessions when that host's readings folder moved or the last sweep could not check it, and no other host's after nothing moved.

## Impact

- `plugin/lib/board.py`: the follower's clock, its check, its kept read, one read for every partition, the frames' time, `STALE`.
- `plugin/lib/plan.py`: the reads the follower serves from what it kept (the state tip, the kits, the state branch's files, the cards' answers) and `rail_read` taking them; the card sweep's ask of Pending You on the clock.
- `plugin/lib/gather.py`: a kit's stamp, sluice's records with it, and a host's readings folder's stamp, read with no process, for the check.
- `plugin/lib/record.py`: `crew events --follow` on the clock, reading only the run-record files whose blobs changed.
- `plugin/lib/crew.py`: crew's checkout read from its files, for the check.
- `plugin/bin/crew`, `plugin/skills/crew/SKILL.md`, `README.md`, `plugin/hooks/status.js`: the follower's and the follow's cadence in their words.
- Tests: logic cases in `tests/py/`, contract cases for the stamp, and `tests/t-journey-board.sh` and `tests/t-journey-state.sh` on the stubs; `tests/moon.yml` regenerated.
- sluice's watchers, the other half of deneb's load, are sluice's (swancloud-ops's signal), not this change's.

## Touches

```
plugin/lib/board.py
plugin/lib/plan.py
plugin/lib/gather.py
plugin/lib/record.py
plugin/lib/crew.py
plugin/bin/crew
plugin/hooks/status.js
plugin/tests/**
plugin/skills/crew/SKILL.md
README.md
tests/py/**
tests/contract/**
tests/t-journey-board.sh
tests/t-journey-state.sh
tests/t-journey-main.sh
tests/moon.yml
```
