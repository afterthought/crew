# Tasks

## 1. The forecast

- [x] 1.1 `reach` forecasts each bolt the team holds against main through `sluice_check`, says each forecast once and records it on the bolt; `bolt_forecast_read`, `bolt_forecast` and `unread_said` decide. Logic: `tests/py/test_forecast.py` `TestBoltAgainstMain`. Journey: `tests/t-journey-main-forecast.sh`, on the stub sluice (`teams.19`, `plan.8`, `read.1`, `read.2`, `code.7`).
- [x] 1.2 The stub sluice answers `submit main --check --head bolt/<bolt> --json` from `$CREW_TEST_ROOT/sluice-check-<bolt>.json`, and refuses `--head` as sluice 0.32.0 does without one.

## 2. The brief, the rules and the record

- [x] 2.1 `conductor.md` *Forecasts and settling*: the take-main fix on a forecast against main, and a queued submission waited out. Journey: `tests/t-briefs.sh` (`briefs.11`).
- [x] 2.2 `teams.19` added, `plan.8` amended, record 0036 written, the run record's descriptor comment names a bolt's forecast.
