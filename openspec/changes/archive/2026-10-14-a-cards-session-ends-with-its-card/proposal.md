# A card's session ends with its card

## Why

A card's plannotator session is ended today only when its owner closes the card through Pending You's tools in its own session, so a card closed any other way, by the user in the app, by an owner whose session lost the tools, or by a landing, leaves its server listening. On 2026-10-10 eleven idle servers ran on mac-studio, about 600 MB together, among them the sessions of a unit that had landed and of a proposal two days closed (the user: "I wonder if we have lots of orphaned Planitator sessions running", signal 2026-10-10-swancloud-operator-mac-studio-4a5e5091/01). ADR 0005 as amended that day rules that crew ends them on every rail read.

## What Changes

- Every time the rail is read, by `crew rail` and by the rail tab's refresh in the operator workspace, crew ends each card session it started, on every host of the partition, whose card is closed or whose row is gone, and leaves alone every session it did not start.
- The rail says which sessions it ended, each with its card key, its host and why (its card is closed, or its row is gone), and names each host whose sessions it could not check.
- Where crew can't tell whether a row or its card is still open (a host that did not answer, a run record it could not read whole), it ends nothing that depends on it; a session started moments before the read is left for the next one.
- When crew can't read plannotator's list of sessions on a host, it ends nothing there and keeps the session's record, so a later read ends it. This holds for the card hook and `crew card end` too, which today forget a session they could not end.
- `crew board` on its own does not end sessions: it stays a view that writes nothing.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `card-sessions`: a session whose card is closed or whose row is gone is ended on every rail read, which says so; a session that can't be judged is kept; a session's record is kept when plannotator's list can't be read.

## Impact

- `plugin/lib/plan.py`: the rail's read gains the sweep and its text the ended sessions; `crew card sweep`, run on each host; `end_session` keeps the record when plannotator's list can't be read.
- `plugin/lib/board.py`: the rail tab's refresh sweeps; `crew board` does not.
- `plugin/bin/crew`, README, the crew skill: the usage, the rail and card-session paragraphs.
- `tests/t-card-sweep.sh`, new, and `tests/moon.yml`; `tests/t-card-session.sh` for the kept record.
- One ssh call per host of each partition on every rail read; on the rail tab, every 30 seconds.

## Touches

```
plugin/lib/plan.py
plugin/lib/board.py
plugin/hooks/cards
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
tests/t-card-sweep.sh
tests/t-card-session.sh
tests/t-cards.sh
tests/moon.yml
```
