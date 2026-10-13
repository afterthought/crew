# A unit's dependents are never ahead of it

## Why

crew's overlap note in a code stage's prompt, and the forecasts on a conductor's wait, take "ahead of it in the bolt" from the order `plan.rec` lists units in, not from `After`. In wldn on 2026-10-13 (swb-4, switchboard-kit), the-deploy-hands-a-stack-its-boundary was declared `After` the-s3-cdn-archetype-lists-what-a-site-with-its-own-api-declares but listed first, so the dependency's code was told its own dependent was "ahead of it in the bolt and not merged"; its coder merged the dependent's branch into its own "as the forecast asks" (21770f631), and the dependent's commits reached the bolt inside the dependency's merge (signal 2026-10-13-swancloud-planner-51c2c852/01). `teams.12`, as amended that day, says ahead is the bolt's merge order, `After` first and the file's order only among units neither comes after.

## What Changes

- **Ahead is the merge order.** A unit `a` is ahead of `b` in their bolt when `b` comes after `a` through `After` at any depth; else, unless `a` comes after `b`, when the plan lists `a` first. A unit's dependents are never ahead of it.
- **The overlap note follows it.** A unit's code is told of the overlapping Touches of each unmerged unit ahead of it in that order, never of one that comes after it.
- **So do the forecasts.** A conductor's wait forecasts each unit against the units ahead of it in that order, so a dependency is never forecast against its dependent and never asked to take its work; a forecast gives `After` only to a unit that does not already come after the other, at any depth.
- **The briefs say so.** The conductor's brief and README name the order.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: ahead in a bolt is its merge order, for the overlap note and the forecasts.

## Impact

- `plan.py`: `comes_after`, `ahead` and `bolt_order` are new; `overlapping` and `forecasts_due` take ahead from them, and the wait hands `forecasts_due` the bolt's `After` names.
- No plan write, record or view changes; only which unit a note or forecast names as ahead.

## Touches

```
plugin/lib/plan.py
plugin/roles/conductor.md
README.md
tests/py/test_touches.py
tests/py/test_forecast.py
tests/t-briefs.sh
```
