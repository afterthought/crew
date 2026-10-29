# Proposal

## Why

A proven bolt waiting to land runs no stage, so its conductor's wait never forecasts it against main, and its row on the kit's landings card is forecast only when the card is raised, not again when main moves. Even a row forecast to conflict with main keeps its box. So the user is asked to land, and approves, a bolt that already conflicts with what main holds, and sluice finds the conflict only at the submission: aws-bootstrap's `a-member-account-is-seeded-by-the-account-factory` was carded as landable at 23:17Z and approved, though main's 19:33Z archive had already edited a spec the bolt's own archive edited too (wldn signal 2026-10-24-wldn-ops-43c5823d/01; the user: "Whenever there's a merge conflict it's supposed to be fucking dealt with not fucking ignored"). `teams.21`, as read for that signal on 2026-10-24, says what must be true instead.

## What Changes

- Whenever a kit's main moves while its landings card is open, crew forecasts the card's rows again against main where it lives, after a fetch, and each bolt where it lives (`plan.18`, `plan.19`). crew notices the move on the rail's read on the main level's host, which the console's rail tab makes every 30 seconds, and at every landing crew closes, as today.
- A row forecast to conflict with what main holds **takes main first**: it is held with no box, its row saying it takes main first, on which files and why, and never that it can land. The rail's landing row says the same and leaves the bolt out of the tell that lands, so main-level ops never takes it for one that can land.
- The same forecast starts the team's take-main fix at once: the bolt's conductor is told the fix to start, in the words a conductor's wait gives (`teams.21`), once for the same bolt head and revision of main, whichever of the two forecasts said it first, and the forecast is recorded on the bolt.
- A conflict with main that a conductor's wait forecasts through sluice holds the bolt's row in the same way, and changes the kit's card at once.
- A take-main fix in flight on the bolt holds its row as taking main first too, in the fix's words.
- The card is changed in place to show the hold, as for any row held. On a card the user has already answered, a bolt they ticked that is held only to take main in keeps their send standing: the card is left, not closed with that bolt counted as held. The bolt is then landed on that same send once the fix has merged; that part is the sibling unit `a-landings-approval-stands-through-taking-main-in`'s.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: the landings card's forecast is made again whenever main moves; a row forecast to conflict with main, or carrying a take-main fix, takes main first with no box; a send stands for a ticked bolt taking main in.
- `bolt-teams`: a conflict with main forecast for a bolt waiting to land tells its conductor the take-main fix once, whichever forecast found it, and a wait's own such forecast changes the kit's landings card.
- `crew-rail`: a bolt taking main first is said so on the land row and left out of the row's tell.

## Impact

- `plugin/lib/plan.py`: the landings card's raise (`raise_landings`, `forecast_rows`, `landing_rows`, `landings_step`), the rail's read (`rail_read`, `rail_rows`), the conductor's wait (`reach`), and new decisions for when main moved and what a recorded forecast holds.
- `plugin/lib/gather.py`: each kit's read names the revision of main it read at.
- The conductor's and main-level ops's briefs, README and the crew skill: a forecast told for a waiting bolt, and a row taking main first (`docs.2`).
- Tests in the logic tier (`tests/py/test_landings.py`, `tests/py/test_rail.py`, `tests/py/test_forecast.py`), the contract tier (`tests/contract/test_gather.py`) and end to end (`tests/t-journey-land.sh`).

## Touches

```
plugin/lib/plan.py
plugin/lib/gather.py
plugin/roles/conductor.md
plugin/roles/main-ops.md
plugin/skills/crew/SKILL.md
README.md
tests/py/test_landings.py
tests/py/test_rail.py
tests/py/test_forecast.py
tests/contract/test_gather.py
tests/t-journey-land.sh
tests/moon.yml
```
