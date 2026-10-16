# Tasks

## 1. The proposal's card at its acts

- [x] 1.1 `crew plan propose`, `--replaces`, `agree`, `approve` and `drop` post, change and close the proposal's card under `proposal/<n>` of the chain; a refused post is recorded and the rail shows it. Logic: `tests/py/test_proposal_life.py`, the chain's key and which act each step makes. Journey: `tests/t-cards.sh` on the stub pendingyou (`plan.4`, `briefs.11`).
- [x] 1.2 `crew plan answer` gathers every box of the card's list and `crew plan approve` applies the change with the boxes as they stand: a new unit unticked left out, a dropped unit ticked kept, an amendment ticked not applied, the card's outcome and the planner's tell saying which. Logic: `tests/py/test_proposal_life.py`, the scenarios of "The card's questions are the approval and the new units" that Send decides (`roles.2`, `briefs.13`).
- [x] 1.3 `planner.md` says crew raises the proposal's card at `crew plan propose` and changes it at a rewrite and an agreement, the planner adopting it by the line the command prints, gathering its answers with `crew plan answer` and applying them with `crew plan approve`, its `Do` lines carrying each new unit's direction; it no longer posts, changes or closes the card or runs `crew plan card`. Journey: `tests/t-briefs.sh` pins the words (`tests.6`, `briefs.11`, `briefs.13`).

## 2. The suite

- [x] 2.1 `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).
