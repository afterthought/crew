# Proposal

## Why

crew still keeps a waiting process of its own for a card: `crew card wait` asks Pending You every thirty seconds and plannotator every five, and belongs to nobody once the session that started it ends. On 2026-10-28 nine of madswan's batch waits ran orphaned on deneb for 33 hours at a tenth of a core each. And nothing a session waits on in sluice is on the records crew reads: after a restart, a conductor or main-level ops comes back cold, not knowing which merge or landing it had in sluice. Record 0046, accepted by the user on 2026-10-28, settles both (its parts 2, 4 and 5; `teams.22`, `teams.24`): crew keeps no waiting process, a card's answer reaches its owner by the wake's push and is read at the owner's act and at the rail's refresh, and every submission's number is on its bolt's row from the submit.

## What Changes

- **BREAKING** `crew card wait` is gone. Run, it refuses at once, naming `crew card read <key>` as what reads an answer now. Nothing of crew's polls Pending You or plannotator on an agent's behalf.
- A card's answer on Pending You reaches its owner by the fleet's wake mod, as every other card's does, and the owner reads it with `crew card read <key>`. For a batch, that read prints the card's note and every annotation from the reading word for word, closes the card, records the batch read and ends the reading; for a bolt's reading, `land/<bolt>`, run by its conductor, it prints the reading's annotations as notes on the bolt's row and an approval there as landing nothing; for a long proposal it adds the reading's decision to the card's answer.
- The rail's refresh, on the host where a reading runs, finds a reading the user sent and tells its owner once, through `crew tell`, to run `crew card read <key>`; it marks the reading told, and a tell that does not go through is tried at the next refresh. A batch's reading approved with no annotations is recorded read at that refresh, its card closed "Read; no notes", since there are no words to send.
- A batch's, a landing's or a long proposal's reading starts only at its card's raise, by `crew card session`, and by the rail's retry of a reading its card stands without; never by a wait.
- Every submission's number is on its bolt's row from the moment of the submit: each unit's, chore's or fix's merge standing in sluice on the bolt's branch on that work's line, and the bolt's landing standing on main on the bolt's head line, each with its state in sluice's queue, in `crew bolts`, on the board's ledgers and in the agents' bands. crew reads it from sluice's own record of the queue on the team's host; a queue it cannot read is said, never guessed.
- `crew bolt submit <bolt>`, run again while the bolt's landing stands in sluice at the bolt's head, waits on that submission again instead of submitting anew, and says so. That is how main-level ops picks a landing up from the row after a restart; a merge's agent picks its own up with `sluice wait`, as its brief already says.
- The planner's and the conductor's briefs, the crew skill, the command's usage, README and the specs card-sessions, review-batches, rail-cards, bolt-teams, crew-board and signal-capture say so in place of the wait.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `card-sessions`: a reading's decision reaches its owner through `crew card read` and the rail's refresh, not a wait; the two requirements on a wait starting a reading are removed.
- `review-batches`: a batch's notes are given, its card closed and the batch recorded read by the planner's `crew card read batch/<n>`, and a wordless send by the rail's refresh.
- `rail-cards`: a batch card's answer wakes the planner, who reads it with `crew card read`.
- `bolt-teams`: every submission's number is on its bolt's row from the submit; a landing standing in sluice is waited on again, not submitted again; a conductor restarted for a give is told of its waiting bolt's reading without a wait.
- `crew-board`: the Construction lane's ledger and the bands carry each standing submission's number and state.
- `signal-capture`: its example of a crew command's own printed line names a command that still exists.

## Impact

- `plugin/lib/plan.py`: `card_wait`, `batch_wait` and the readings they start removed; `card_read` gains the batch's, the landing reading's and the proposal reading's decisions; the card sweep tells a sent reading's owner; `bolt_submit` waits again on a standing landing; `crew bolts` shows the numbers.
- `plugin/lib/gather.py`, `plugin/lib/board.py`, `plugin/hooks/status.js`: sluice's queue read on each kit's host and carried to the rows, the board and the bands (`code.8`).
- `plugin/roles/planner.md`, `plugin/roles/conductor.md`, `plugin/lib/crew.py` (the conductor's greeting of two bolts), `plugin/lib/hold.py`, `plugin/skills/crew/SKILL.md`, `plugin/bin/crew`, `README.md`.
- Tests in all three tiers and the mod's cases; `tests/moon.yml` when a test's reads change.
- The sibling chore `a-wait-ends-with-the-session-that-started-it` ends the waits that stay; the sibling unit `a-rail-refresh-after-no-change-reads-nothing` decides when a refresh reads anything. Both touch some of the same files.

## Touches

```
plugin/lib/plan.py
plugin/lib/gather.py
plugin/lib/board.py
plugin/lib/crew.py
plugin/lib/hold.py
plugin/hooks/status.js
plugin/roles/planner.md
plugin/roles/conductor.md
plugin/roles/main-ops.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
README.md
tests/py/**
tests/t-*.sh
tests/moon.yml
tests/stubs/**
plugin/tests/**
```
