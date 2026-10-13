# Tasks

## 1. Ahead is the merge order

- [x] 1.1 `comes_after`, `ahead` and `bolt_order` decide ahead pair by pair, `After` at any depth first and the plan's order only between units neither comes after. Checked by `tests/py/test_touches.py` `TestAheadFollowsAfter::test_ahead_is_after_first_then_the_files_order` (`teams.12`, `plan.13`, `code.7`).
- [x] 1.2 `overlapping` tells a unit's code only of units ahead of it in that order. Checked by `tests/py/test_touches.py` `TestAheadFollowsAfter`, the wldn case with the dependent listed first (`teams.12`).
- [x] 1.3 `forecasts_due` forecasts a unit only against units ahead of it, the wait handing it the bolt's `After` names, and puts no `After` on a unit that already comes after the other at any depth. Checked by `tests/py/test_forecast.py` `TestDue::test_a_dependent_listed_first_is_forecast_against_the_unit_it_comes_after_never_the_other_way` and `test_one_that_comes_after_at_any_depth_is_not_put_after_it_again`; the wait's wiring by `tests/t-journey-merge.sh` (`teams.12`, `plan.13`).

## 2. The briefs say so

- [x] 2.1 The conductor's brief and README name the bolt's merge order. Checked by `tests/t-briefs.sh` and `tests/t-docs.sh` (`docs.2`).
