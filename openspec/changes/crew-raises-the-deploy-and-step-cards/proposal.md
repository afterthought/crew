# crew raises the deploy and step cards

## Why

Record 0031 makes a deploy's card and a step's card crew's own, raised in main-level ops's name by the commands that record them: a deploy's when the kit's deployer offers a `manual` environment a deploy, a step's when an after-deploy step is the user's or is held for the user's word. Today main-level ops posts both by hand, and the card hook refuses them for want of their keys, so ops's three deploy cards of 2026-10-15 went up by another path and the rail read none of them open. In the card trials the user asked for the deploy's release notes on the card ("when I'm offered a deploy, I want to be able to easily see a summary of what's in it from the release notes … or include a better summary of what will happen after the deploy"), and for a step card at a time, each following the one before ("only saw the one follows").

## What Changes

- `crew ops offer <env> --to <sha> --from <sha|none> [--notes <file>] [--steps <file>]` takes the kit's release notes for the range and the range's after-deploy steps from the deployer, raises the deploy's card in main-level ops's name, keyed `deploy/<env>`, with them on its face, following the landing card that put the commit on main, changes it when a newer head is offered, and tells main-level ops the line that adopts it, `call get_request (requestId <id>, name <role>)`.
- `crew ops record --act end` closes the deploy's card with each step's outcome, or with the failed step and its log.
- `crew ops step` raises a step's card, keyed `op/<env>/<n>`, when its doer is the user or it is held for the user's word, one card at a time, each following the one before; and closes it when the step is done or declined.
- A held step's card is a choice of now, when quiet or skip; a step an agent runs on its own has no card.
- Main-level ops's brief says crew raises the deploy's and the step's cards, how ops adopts one from the line it is told, and what it runs on the answer; it posts and closes none.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: the deploy's card carries the notes and steps as handed; the step's `do` card; the held step's choice of when.
- `main-level`: the deploy's and the step's cards crew's, the held step, the offer's notes and steps.

## Impact

- Follows `crew-builds-every-card-from-its-facts`, whose builders, `follows_of` and act it calls. Built beside `crew-raises-a-proposals-card`, `crew-raises-a-batchs-card-with-its-session`, `crew-record-raises-a-records-card` and `the-rail-shows-and-sweeps-every-card`; of crew's code it changes `ops.py`, `cards.py`'s `deploy_card` and `board.py`'s words for a held step, and of the files the others change only the docs' lines of its own command and one test of `deploy_card`.
- The interface swancloud's `a-deploy-offer-hands-its-release-notes-and-after-steps` builds to.

## Touches

```
plugin/lib/ops.py
plugin/lib/cards.py
plugin/lib/board.py
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
plugin/roles/main-ops.md
docs/architecture/plan.md
docs/architecture/_open.md
tests/py/test_ops.py
tests/py/test_cards.py
tests/py/test_board.py
tests/t-journey-ops.sh
tests/t-journey-board.sh
tests/t-briefs.sh
tests/t-docs.sh
```

`ops.py` changes `rows`, `environments` and `open_keys` (the deploy's row keyed `deploy/<env>`, the held step's row), `offer`, `record_cmd`, `step`, `parser` and `args_refusal`, and gains `deploy_facts`, `raise_deploy` and `raise_step` with the decisions and reads they stand on (`handed_steps`, `release_of`, `deploy_move`, `deploy_outcome`, `step_words`, `step_facts`, `step_due`, `stages_working`). `cards.py` changes `deploy_card` alone: its face says when the kit handed no release notes, and it says, rather than counts, landings crew can't read. `board.py` changes `waiting_fields` and `ops_view`, which name a held step held (`code.8`). `plugin/bin/crew` changes only its usage header's `crew ops offer` and `step` lines, README and the crew skill only theirs; `plugin/roles/main-ops.md` changes its offer's and its user's step's paragraphs of *Deploying main*, and `tests/t-briefs.sh` their words; `tests/t-docs.sh` pins the offer's flags; `plan.14`'s details and `_open.md` say it is built.
