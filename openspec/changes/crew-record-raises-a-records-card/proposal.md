# crew record raises a record's card

## Why

Record 0031 makes a decision record's card crew's own: raised in the design agent's name when a record it committed as proposed was not settled with the user in the pane, changed in place when the record is revised, and closed when it is accepted or rejected. Today the design agent posts the card by hand under a key that carries the commit, so each revision is a new card. In the card trials the user asked to be shown when a rule of theirs decided between alternatives ("I want the designer to let me know when there are alternatives, especially if it's choosing one alternative over the other based on my rules … That should all be one decision: go with my plan or loosen the rules, and here's what the loosened rules would look like").

## What Changes

- New: `crew record <kit> <number> --proposed|--accepted|--rejected [--settled-in-pane] [--alternatives <file>]`, run by the design agent at each turn of a record's status, records the status with its commit in the run record and refuses a status the record's file does not hold at that commit.
- `--proposed` raises the record's card in the design agent's name, keyed `record/<kit>/<number>`, unless `--settled-in-pane` says the user settled it in the pane, and changes it in place at each new commit; with `--alternatives <file>` the card is a choice of loosening the rules as drafted, accepting as ruled, or sending back.
- `--accepted` and `--rejected` close the card with the commit.
- The design agent's brief says `crew record` at each turn of a record's status and how it adopts the card, and that a record a rule of the user's decided between alternatives names them, never settled silently; it posts and closes no record card.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `main-level`: `crew record`; the record's card raised unless settled in the pane, closed with its status; the user's own words on it; a record accepted, revised or rejected through `crew record`.
- `rail-cards`: the record's card raised by `crew record`, its key the record's number without a commit, its form a choice when a rule decided.

## Impact

- Follows `crew-builds-every-card-from-its-facts`, whose record builder and act it calls. Built beside `crew-raises-a-proposals-card`, `crew-raises-a-batchs-card-with-its-session`, `crew-raises-the-deploy-and-step-cards` and `the-rail-shows-and-sweeps-every-card`, none of which changes a function this one changes; of the files they share, it changes only its own command's lines of the docs.

## Touches

```
plugin/lib/plan.py
plugin/hooks/cards
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
tests/py/test_cards.py
tests/t-cards.sh
plugin/roles/design.md
tests/t-briefs.sh
tests/moon.yml
```

`plan.py` changes `RECORD_KEY` (`record/<kit>/<number>`), the design agent's branch of `card_refusal`, `parser` and `main`, and gains `record_status` (the command), `record_facts` and `raise_record`. The card hook changes only its `KEYS` line for a record's key. `plugin/bin/crew` gains `record`'s dispatch and its usage lines, README and the crew skill theirs; `plugin/roles/design.md` changes *Decision records*, and `tests/t-briefs.sh` its words; `tests/moon.yml` is regenerated.
