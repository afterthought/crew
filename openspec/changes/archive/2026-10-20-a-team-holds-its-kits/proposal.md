# Proposal

## Why

Record 0035, part 3: a team held one kit, its `repos` its kit then its partition's blueprints repo, so a kit two teams should both build, agentplot/weir for slc-1 and flm-1, needed a team of its own, which the user did not want ("i dont think we want a dedicated team for this. is it possible to assign this repo to both the sluice and flume team?", 2026-10-20). The user then asked that proposal 200's crew bolt be built outside the plan.

## What Changes

- A team's `repos` are its kits, one or more, then its partition's blueprints repo, each named once.
- A bolt is of one kit; `crew bolt give` gives a team the first free bolt, in the plan's order, of any kit it holds, or the one named when it is of one of them.
- While a team holds a bolt, crew reads, readies, merges and lands in that bolt's kit's checkout on the team's host: the stages, places, policy, branch, landing, review readings and the conductor's and ops' brief and folder all take the bolt's kit.
- A team holding no bolt works in its first kit; the board and the briefs name every kit a team holds.

## Capabilities

### Modified Capabilities

- `bolt-teams`: a team holds its kits, and takes a bolt of any of them.

## Impact

`plugin/lib/crew.py` (`load`, `kits_of`, `with_kit`, `builds`, `held_team`, `launch`, `brief`, `team_tokens`, `main_tokens`, `kits_on`), `plugin/lib/plan.py` (`bolt_team`, `held_repo`, `at_work`, `unit_kit_team`, `survey`, `Stages.kit`, `to_give`, `bolt_give`, the team commands), `plugin/lib/board.py`, `plugin/lib/sites.py`, `plugin/lib/page.py`; swancloud's `lib/crew-teams.nix` and `herdr.3` give slc-1 and flm-1 weir.
