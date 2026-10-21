# The bolt is forecast against main on the conductor's waits

## Why

A bolt meets main only when main-level ops submits it (`plan.8`), so a conflict with what main has landed since the bolt took it is found then, however long it was there. switchboard-kit's main records on chuck-herdr-alpha, 2026-10-19 to 10-21, hold nine such conflicts, each knowable from 7 minutes to 18 hours before the bolt was submitted, #215 and #216 after twenty more commits each; each went back to the team by ops's word and was settled by a take-main fix in minutes. crew already forecasts every unit against its bolt on the conductor's waits (`teams.12`), and the bolts' queues held no conflict in those days. sluice now forecasts a branch no worktree holds against another and everything queued on it (its ADR 0039, `sluice submit --check --head`), so the bolt can be forecast against main the same way. Record 0036.

## What Changes

- **The wait forecasts the bolt against main.** After the units' forecasts, each conductor's wait runs `sluice submit main --check --head bolt/<bolt> --json` in the kit's main checkout for each bolt the team holds.
- **Said once.** A forecast is said on the wait once for the same bolt head, revision of main and submissions queued on main it meets, and recorded as a `forecast` on the bolt with `Reached: wait`. A conflict with what main has landed gives the take-main fix to start now; one with a submission queued on main is one to wait out; one sluice can't give is named once for the bolt's head.
- **The conductor's brief** starts the take-main fix on such a forecast, as on main-ops's word that a landing conflicts, and waits out one against a queued submission.
- **Rules:** `teams.20` added; `plan.8` amended so a bolt may meet main before its landing on such a forecast.
- **The stub sluice** answers the forecast from a file, and refuses `--head` as sluice 0.32.0 does without one.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: the bolt forecast against main on the conductor's waits.

## Impact

- `plugin/lib/plan.py` (`reach`, `sluice_check`, `bolt_forecast_read`, `bolt_forecast`, `unread_said`), `plugin/lib/record.py`'s descriptor comment, `plugin/roles/conductor.md`; `docs/architecture/teams.md`, `plan.md`; record 0036.
- `tests/py/test_forecast.py`, `tests/t-journey-main-forecast.sh`, `tests/t-briefs.sh`, `tests/stubs/sluice`, `tests/moon.yml`.
- Needs a sluice with `submit --check --head` on each team's host to forecast; until then the wait names the gap once per bolt head. Nothing is added to devenv and nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/plan.py
plugin/lib/record.py
plugin/roles/conductor.md
docs/architecture/teams.md
docs/architecture/plan.md
docs/adr/0036-*.md
tests/py/test_forecast.py
tests/t-journey-main-forecast.sh
tests/t-briefs.sh
tests/stubs/sluice
tests/moon.yml
```
