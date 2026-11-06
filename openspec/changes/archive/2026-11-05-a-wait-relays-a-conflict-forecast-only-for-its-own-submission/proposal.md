# A wait relays a conflict forecast only for its own submission

## Why

On 2026-11-02 on chuck-herdr-alpha, wldn's swb-3 conductor started a take-main fix that crew's wait named for its bolt `the-class-declares-its-environments-identity-settings`. The fix drafted the bolt's pull request, which withdrew its landing, switchboard-kit's sluice #1277, while #1277 was under test. The bolt merged cleanly with main. The conductor dropped the fix, and ops submitted the same head again as #1279, which landed (signals wldn 2026-11-02-wldn-planner-039772f5/01, swancloud 2026-11-02-swancloud-planner-5e5b0d4f/01 and 2026-11-05-swancloud-operator-8f7c4c61/01).

The box's records show how it happened:

- 23:31:48Z: #1275, the bolt at `75016a0`, conflicted with main on `packages/commissioning/src/frontegg.test.ts`. It was sluice's only conflict of the evening.
- 23:34:43Z: the conductor started `crew unit wait` on another unit's construct, in the background.
- 23:35:27Z: as it began, that wait forecast the bolt at `75016a0` against main `e93346c` and found the same conflict. That was true of `75016a0`, and the bolt's own take-main fix, sluice's #1274 into the bolt, was under test at the time. The wait wrote the take-main words on standard error.
- 23:36:59Z: #1274 landed and the bolt moved to `2722779`.
- 23:38:43Z: ops submitted `2722779` to main as #1277.
- 23:45:02Z: the construct ended, the wait answered, and the conductor read the forecast's words with the answer: "bolt/… is forecast to conflict with main on packages/commissioning/src/frontegg.test.ts … crew fix swb-3 take-main-e93346c …". Nothing in those words named `75016a0`, so the conductor read them as being about the bolt as it then stood, `2722779`, whose submission was #1277.

So the wait relayed a forecast of an earlier head, the one #1275 had submitted, as if it were a forecast of the later one. sluice's forecast says the head and revision it formed on (sluice clause 64). crew recorded that head in the forecast's `Heads` but did not say it, and did not check it again before the conductor read the words.

## What Changes

- **A forecast names its head.** The wait's words for a bolt's forecast against main name the bolt's head the forecast is of: `bolt/<bolt> at <head> is forecast to conflict with main on …`. This covers a conflict with what main has landed, a conflict with a submission queued on main, and a bolt the user left. The landings card uses the same words when it tells a conductor the take-main fix.
- **A wait's answer says when its forecast is stale.** As the wait answers, crew reads where each bolt it forecast at its start now stands, after a fetch. Before the answer it says, for each bolt that moved from the head forecast while the wait waited, that the forecast is of that head and not of the bolt now, that nothing is to be taken in for it, and that the next wait forecasts the bolt where it stands. For a bolt whose head it can't read, it says it can't tell, and why (`read.1`). A bolt still at the head forecast gets nothing more said.
- **The record and the card are unchanged.** The forecast is still recorded at the head it was made of. The landings card still changes at once on a conflict with main, and its next raise forecasts the bolt at its present head.
- The conductor's brief, README, the crew skill and `crew`'s usage header say this (`docs.2`, `tests.6`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a bolt's forecast against main names its head, and a wait's answer says a forecast is not the bolt's now when the bolt moved from that head while the wait waited.

## Impact

- `plugin/lib/plan.py`: `bolt_forecast`'s words; `bolt_said` and `reach` give the forecasts said with their heads; `before_waiting` hands them on; the new decision `forecasts_moved`, its read `forecast_heads_now` and `forecasts_after`; and `stage_wait` uses them as it answers.
- `plugin/roles/conductor.md`, `plugin/skills/crew/SKILL.md`, `plugin/bin/crew`'s usage header, README.
- Tests: `tests/py/test_forecast.py`, `tests/py/test_landings.py`, `tests/t-journey-main-forecast.sh`, `tests/t-journey-land.sh`, `tests/t-briefs.sh`.
- Nothing the board or the mod draws changes (`code.8` not reached), the run record's fields don't change, and nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/plan.py
plugin/roles/conductor.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
README.md
tests/py/test_forecast.py
tests/py/test_landings.py
tests/t-journey-main-forecast.sh
tests/t-journey-land.sh
tests/t-briefs.sh
```
