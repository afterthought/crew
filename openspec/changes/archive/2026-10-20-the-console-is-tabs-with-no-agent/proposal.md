# Proposal

## Why

Record 0035, part 2: with the operator a main-level role, the flow, rail and board a person reads on each host need no agent. The user approved it on their card on 2026-10-20, with the console change first.

## What Changes

- `crew console up <label>` opens the flow, rail and board tabs in a `console` workspace of this host's `<label>` session and starts no agent; `crew console down <label>` closes them.
- A tab that came back after a restart as its shell alone runs its command again; one running anything else is left and said, as the operator's tabs were.
- `crew operator up <label>`, which swancloud's timer runs every five minutes until its chore lands, opens the console, saying it is `crew console up` now.
- The operator agent a host's console held before, `<label>-operator-<host>`, is ended and its `operator` workspace closed once it is not working; one working is left and said.

## Capabilities

### Modified Capabilities

- `operator-agent`: its workspace's tabs become the console's.

## Impact

`plugin/lib/plan.py` (`console_cmd`, `retire_operator`), `plugin/lib/crew.py` (`standing`, the `console` kind, `here`), `plugin/bin/crew`, `plugin/lib/board.py` and `plugin/hooks/status.js` (the words naming the console); README, the skill, the usage.
