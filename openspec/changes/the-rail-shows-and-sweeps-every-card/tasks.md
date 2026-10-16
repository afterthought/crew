# Tasks

## 1. The rail and the board

- [x] 1.1 `crew rail` prints each row's card id and state, the open questions after its groups, and what the sweep did; `board.agent_views` gives each agent its open cards and `status.js` draws them. Logic: `tests/py/test_rail.py` `TestText`, `tests/py/test_board.py`. Mod: `plugin/tests/` through `tests/mod`. Journey: `tests/t-journey-board.sh` (`code.8`).
- [x] 1.2 The board's design band shows the records proposed and not yet accepted or rejected, from the run record's `record.<status>` entries, and the mod draws them. Logic: `tests/py/test_board.py`. Mod: `plugin/tests/` through `tests/mod` (`code.8`, `briefs.15`).

## 2. The sweep

- [x] 2.1 The rail read withdraws a row's card whose row is gone and a question whose asker herdr no longer lists, and posts again an open row's card that reads not found after the host signed in anew; `crew board` writes nothing. Logic: `tests/py/test_rail.py` `TestSweepJudged`, `TestSweep`. Journey: `tests/t-cards.sh` (`read.4`, `state.4`).
- [x] 2.2 The rail read posts a row's card that has none, a post refused or never made, through its kind's raise, and leaves a row whose kind has no raise as it is. Logic: `tests/py/test_rail.py` `TestSweep`. Journey: `tests/t-cards.sh` (`read.1`).

## 3. The suite

- [x] 3.1 `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).
