# crew raises the deploy and step cards

## Why

Record 0031 makes a deploy's card and a step's card crew's own, raised in main-level ops's name by the commands that record them: a deploy's when the kit's deployer offers a `manual` environment a deploy, a step's when an after-deploy step is the user's or is held for the user's word. Today main-level ops posts both by hand, and the card hook refuses them for want of their keys, so ops's three deploy cards of 2026-10-15 went up by another path and the rail read none of them open. In the card trials the user asked for the deploy's release notes on the card ("when I'm offered a deploy, I want to be able to easily see a summary of what's in it from the release notes … or include a better summary of what will happen after the deploy"), and for a step card at a time, each following the one before ("only saw the one follows").

## What Changes

- `crew ops offer <env> <sha> [--notes <file>] [--steps <file>]` takes the kit's release notes for the range and the range's after-deploy steps from the deployer, raises the deploy's card in main-level ops's name, keyed `deploy/<env>`, with them on its face, following the landing card that put the commit on main, changes it when a newer head is offered, and tells main-level ops the card's id.
- `crew ops record --act end` closes the deploy's card with each step's outcome, or with the failed step and its log.
- `crew ops step` raises a step's card, keyed `op/<env>/<n>`, when its doer is the user or it is held for the user's word, one card at a time, each following the one before; and closes it when the step is done or declined.
- A held step's card is a choice of now, when quiet or skip; a step an agent runs on its own has no card.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: the deploy's card carries the notes and steps as handed; the step's `do` card; the held step's choice of when.
- `main-level`: the deploy's and the step's cards crew's, the held step, the offer's notes and steps.

## Impact

- Follows `crew-builds-every-card-from-its-facts`, whose builders, `follows_of` and act it calls. Built beside `crew-raises-a-proposals-card`, `crew-raises-a-batchs-card-with-its-session`, `crew-record-raises-a-records-card` and `the-rail-shows-and-sweeps-every-card`; it changes `ops.py` alone of crew's code, and of the files the others change only the docs' lines of its own command.
- The interface swancloud's `a-deploy-offer-hands-its-release-notes-and-after-steps` builds to. Main-level ops's brief keeps its words until `only-crew-raises-a-rows-card`.

## Touches

```
plugin/lib/ops.py
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
tests/py/test_ops.py
tests/t-journey-ops.sh
tests/moon.yml
```

`ops.py` changes `rows`, `environments` and `open_keys` (the deploy's row keyed `deploy/<env>`, the held step's row), `offer`, `record_cmd`, `step`, `parser` and `args_refusal`, and gains `deploy_facts`, `raise_deploy` and `raise_step`. `plugin/bin/crew` changes only its usage header's `crew ops offer` lines, README and the crew skill only theirs; `tests/moon.yml` is regenerated.
