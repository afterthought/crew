# A deploy waiting at its gate has its card

## Why

When a hosted deployer, such as a GitHub Actions run, holds a deploy at an environment gate whose one reviewer is the user, nothing tells the user: no agent can pass the gate, and no card asks them to. On 2026-10-14 swb-4's break-glass stand (switchboard-kit run 38612817613) waited at the `dev` gate with no card, and wldn's planner could only say so in its pane (signal 2026-10-14-swancloud-planner-b2e8502f/01). The rule already says what the gate is: a step that is the user's, `op/<env>/<n>`, recorded by whoever dispatched the deploy with the gate's link as its text, its card main-level ops's with that link as its one step (`plan.14`). crew records such a step today, but its card and its rail row read it as a step *after* a deploy, so the user is told "After dev's deploy: https://…" for a deploy that has not happened, and no brief tells anyone to record the gate.

## What Changes

- A step that is the user's, whose words are the gate's link alone, is read as the deploy waiting at its gate.
- Its card, raised by crew in main-level ops's name as every step's is, asks the user to approve the deploy at its gate: it names the environment and, when the step names one, the commit; its one step and its *where* are the gate's link; and it says the click at the gate is the word to deploy, so nothing else asks for it.
- Its rail row, the board's Operation lane and main-level ops's band say the deploy waits at its gate for the user, not that the step comes after the deploy.
- Main-level ops's brief (*Deploying main*) says how a gate is recorded, that no offer is posted for it, and that the step is marked done when the deployer's run shows the gate passed, or on the user's Done.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a gate's card, the user's `do` with the gate's link as its one step.
- `main-level`: a deploy held at a gate whose reviewer is the user waits as the user's step, recorded by whoever dispatched it, with no offer, and is marked done when the gate is passed.

## Impact

- Code: `plugin/lib/ops.py` (reading a step as a gate, its facts, its rail row, its entry in `environments`), `plugin/lib/cards.py` (`step_card`'s gate form), `plugin/lib/board.py` (the gate's words in the Operation lane and main-level ops's view, `code.8`).
- Brief: `plugin/roles/main-ops.md` *Deploying main*, and `tests/t-briefs.sh` for its words.
- The card hook is not changed: crew already raises the operations' cards itself, under their rows' keys `deploy/<env>` and `op/<env>/<n>`, records them as every other row's card, and refuses an agent's own post under them (`briefs.11`, record 0031, built by `crew-raises-the-deploy-and-step-cards`).
- The rule pages are not changed: `plan.14`'s *Not built* clause, `briefs.11`'s note on the hook's keys and `_open.md`'s item are the design agent's to settle after the landing (`docs.7`, proposed).
- No new command, flag or key: the gate is recorded with `crew ops step` as `plan.14` names it.

## Touches

```
plugin/lib/ops.py
plugin/lib/cards.py
plugin/lib/board.py
plugin/roles/main-ops.md
tests/py/test_ops.py
tests/py/test_cards.py
tests/py/test_board.py
tests/t-briefs.sh
```
