# Proposal

## Why

`crew ops` records every deploy and every other operation on a partition's environments in the run record (`plan.14`), and a landing now records the commit its kit's main holds afterwards. Nothing shows them: the board's Operation lane lists only the bolts landed in the last seven days, and the page has no view of what each environment runs, on whose word, and what each deploy carried. Record 0010 has the page draw the deploys as a view of its own, and `plan.14` has the Operation lane show each environment's deploys.

## What Changes

- **The board's Operation lane** shows, after the week's landings, each environment's deploys that moved in those seven days or are still open, newest first, and the operations waiting on it. A deploy is one line: the commit and the one it comes from, where it stands (waiting on the user's word, replaced unanswered, deploying, approved and not yet deployed, or its outcome and when it ended, at the step that failed), whose word it went on, and the bolts it carried or why the record can't tell. An operation waiting is one line: its key, who has it and its first line. A deploy waiting on the word and an operation waiting on the user carry their rail row's ✓ marker and card.
- **`crew board --json`** gives each partition `environments`: each environment with the teams on its host, its deploys and the operations waiting, each with its rail row and marker.
- **The operator's view** names each environment with a deploy or an operation waiting, under Operation, and counts their cards among what waits on the user (`code.8`).
- **Main-level ops's view**, new among the agents' views: the deploys waiting on the user's word with their cards, those approved and not yet deployed, those running, and the operation steps waiting, handed or failed, each with the deploy it comes after and its doer (the user, 2026-10-12, by `code.8`).
- **The page's deploys view**, a third switch beside board and flow: each environment a timeline over the record's window (`--since`), oldest at the top, each deploy with the commit it moved from and to, the user's word on it as its card's answer recorded it, its steps, the suite's checks and its outcome, the bolts it carried with their changes' proposals as its release notes, and the after-deploy steps of its commit with their doers and states; then the operations waiting.

All of it is read from the `ops.*` entries of the main level's host and the `bolt.land` entries, as a function of those facts (`ops.environments`, `state.4`, `code.7`).

## Capabilities

### Modified Capabilities

- `crew-board`: the Operation lane shows each environment's deploys and the operations waiting.
- `board-page`: the board view draws them, and the page gains the deploys view.

## Impact

- `plugin/lib/ops.py` (`landings`, `carried`, `environments`), `plugin/lib/board.py`, `plugin/lib/plan.py` (`rail_record` hands the board the entries), `plugin/lib/page.py`, `plugin/lib/page.html`.
- README, `plugin/skills/crew/SKILL.md`.
- `tests/py/test_ops.py`, `test_board.py`, `test_page.py`, `tests/t-journey-board.sh`.
- Nothing is written to any repository and no command's arguments change.

## Touches

```
plugin/lib/ops.py
plugin/lib/board.py
plugin/lib/plan.py
plugin/lib/page.py
plugin/lib/page.html
README.md
plugin/skills/crew/SKILL.md
tests/**
```
