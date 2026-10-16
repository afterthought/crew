# The rail shows and sweeps every card

## Why

Record 0031 makes the rail the truth of what is open and whose, and has crew close what nobody will: a row's card whose row is gone, a question whose asker has ended, and a card lost when the host signed in anew. Today the rail names an open card whose row is gone and leaves a pasteable `crew tell` for its owner to close it, a card lost to its owner waits for the owner to notice, and the agents' bands above their prompts show no card at all.

## What Changes

- `crew rail` prints under each row its card key, whether a card is open, its id and whose it is; after its groups the open question cards, each with its key, its asker and its age, the open record cards apart, and what its sweep did.
- On each rail read, under the host's connection, crew closes a row's card whose row is gone, with the outcome or the reason; withdraws a question card whose asker herdr no longer lists, naming the asker; posts again, under its key, an open row's card that reads not found; and posts a row's card that has none, through the raise its kind's change gives it.
- `board.agent_views` gives each agent its open cards, questions among them, and the design band the records proposed; the mod draws them. `crew board` stays a view that writes nothing.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: the rail's card lines, questions and records; the sweep's withdrawals and posts again; a question whose asker is gone; a lost card posted again by crew.

## Impact

- Follows `crew-builds-every-card-from-its-facts`, whose act it calls. Built beside `crew-raises-a-proposals-card`, `crew-raises-a-batchs-card-with-its-session`, `crew-raises-the-deploy-and-step-cards` and `crew-record-raises-a-records-card`, none of which changes a function this one changes: the sweep posts a kind's card through that kind's raise once its change has landed, and leaves the kind's rows as they are before then.
- `crew-raises-a-bolts-landing-card` follows this one, whose read posts the landing card through its raise.

## Touches

```
plugin/lib/plan.py
plugin/lib/board.py
plugin/hooks/status.js
plugin/tests/status.test.ts
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/py/test_rail.py
tests/py/test_board.py
tests/t-journey-board.sh
tests/t-cards.sh
tests/moon.yml
```

`plan.py` changes `rail_record` (it hands on every entry it read), `rail_read`, `rail_text`, `record_cards`, `stray_cards` and `card_row`'s reading of `rail_record`, and gains `card_kind`, `question_cards`, `row_gone`, `row_owner`, `sweep_judged`, which judges from the rows, the run record and the cards which to close, ask after, post again or post, `swept_cards`, and `sweep_cards` with `SweepActs` and `question_close`, which ask Pending You and herdr and act through the act. `board.py` changes `board_data`, `agent_views` and the design agent's view, and gains `records_proposed`, `record_row` and `card_line`; `status.js` draws each agent's open cards above its view. `plugin/bin/crew`'s usage header, the crew skill and README change only `crew rail`'s lines and the agents' bands' (`docs.2`). `tests/t-cards.sh` gains the sweep's journey; `tests/moon.yml` is regenerated.
