# crew raises a proposal's card

## Why

Record 0031 makes a proposal's card crew's own: raised when `crew plan propose` accepts the proposal, in the planner's name, changed in place when the planner rewrites it or a conductor agrees, and closed with what was applied or withdrawn with the user's reason. Today the planner builds the card from `crew plan card`, posts it itself, and posts a second card for each rewrite under a new key; and Send on the card can leave a new unit out but cannot keep a dropped unit or an amendment's old words, which the card trials found the user wants ("What if I objected to something being dropped?").

## What Changes

- `crew plan propose` raises the proposal's card itself in the planner's name, keyed `proposal/<n>` of the chain's first proposal, built by `crew-builds-every-card-from-its-facts`'s proposal builder from the plan and the proposal, and prints the card's key and id.
- `crew plan propose --replaces <m>` changes the chain's one card in place, "Rewritten as proposal <n> after your note"; the rail's row for the successor carries the chain's key.
- `crew plan agree` changes the card to say it no longer waits on that conductor.
- `crew plan approve` closes the card with what was applied; `crew plan drop` withdraws it with the reason.
- Send applies the boxes as they stand: a new unit unticked is left out, a dropped unit ticked "Keep" stays, an amendment ticked "Keep … old intent" is not applied, and the planner is told which.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plan-proposals`: the proposal's card raised by `crew plan propose`, changed in place by `--replaces`, closed by approve and withdrawn by drop; its one checkbox list applied as it stands.
- `rail-cards`: the proposal's card is no longer an approval.

## Impact

- Follows `crew-builds-every-card-from-its-facts`, whose builder and act it calls. Built beside `crew-raises-a-batchs-card-with-its-session`, `crew-raises-the-deploy-and-step-cards`, `crew-record-raises-a-records-card` and `the-rail-shows-and-sweeps-every-card`, none of which changes a function this one changes.
- The planner's brief keeps its words until `only-crew-raises-a-rows-card`, which also removes `crew plan card` and the card hook's proposal form.

## Touches

```
plugin/lib/plan.py
tests/py/test_proposal_life.py
tests/py/test_proposals.py
tests/t-cards.sh
tests/moon.yml
```

`plan.py` changes `plan_propose`, `plan_agree`, `plan_approve`, `plan_drop`, `plan_answer`, `card_answer`, `with_answer`, `answered`, `CardReads.open_proposals` and the proposal's row in `rail_rows`, and gains `proposal_chain`, `proposal_facts` (what `card_model` reads, handed to the builder) and `raise_proposal`. `tests/t-cards.sh` gains the proposal's journey; `tests/moon.yml` is regenerated.
