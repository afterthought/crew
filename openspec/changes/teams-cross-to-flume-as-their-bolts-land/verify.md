# Verify: teams-cross-to-flume-as-their-bolts-land

Read 2026-10-31 on mac-studio, at `b9adb66e` on `change/teams-cross-to-flume-as-their-bolts-land`, cut from `bolt/crew-runs-its-work-through-flume` at `227870c3`.

**Outcome: not archived.** The work holds everywhere but one scenario, which no check proves and which the code does not meet in the host hold's own flow. It goes back to code for that (Finding 1).

## Checks

| Check the tasks name | Result |
|---|---|
| `tests/suite logic contract mod t-journey-cross t-journey-main-fix t-briefs t-roles t-docs` | 8 passed (8 replayed), 0 failed |
| `tests/suite --force logic contract mod t-journey-cross t-journey-main-fix` | 5 passed (0 replayed), 0 failed |
| `tests/suite --affected` (task 9.1) | 34 passed (34 replayed), 0 failed: every task of the suite, the command core having changed |
| `openspec validate teams-cross-to-flume-as-their-bolts-land --strict` | valid |

`tests/moon.yml` holds 34 `check-full` tasks, the 31 suite tests and the logic, contract and mod tiers, so `--affected` ran the whole suite.

## Tasks

All 26 tasks, 1.1 to 9.1, are ticked, and the check each names passes. Task 2.4's "never on a held host" is not proved by any of the checks it names (Finding 1).

## Requirements and scenarios

The two MODIFIED requirements of `bolt-teams` keep every scenario the main spec holds. Each scenario below is matched to the check that proves it.

**bolt-teams**
- Teams are fixed in the teams file: *The first version of the file* is `test_teams.py` `test_another_version_is_refused_naming_2_and_3` (1, 4, "3", true and null); *Version 3 names each team's setting*, *A team in version 3 without its setting* and *Version 2 still loads* are `test_teams.py`'s version-3 cases; the other two are unchanged and pass.
- A team builds one bolt and may hold one more: *A crossed team takes a third bolt* is `test_cross.py` `test_a_crossed_team_takes_a_third_bolt_and_its_launches_follow_the_requests_already_written`; the other four are unchanged and pass.
- A team's path is today's, due or crossed: `test_cross.py` `TestPath`, its three scenarios each a case; `t-journey-cross` shows the due team's conductor and ops running on.
- A team due to cross is given no new bolt: `test_cross.py` `TestDue`, and `t-journey-cross`, the plan unchanged and no `bolt/next` made.
- A team crosses once its last bolt of today's path has gone: *A due team's bolt lands* is `t-journey-cross` with `test_hold.py` `TestCrossing`. *A held host* has no check (Finding 1).
- A crossed team runs no standing agent: `test_cross.py` `TestNoStandingAgent`, and `t-journey-cross` for `crew up`, with no ssh to the host and no pane.
- A crossed team's give launches its bolt whole: `test_cross.py` `test_a_bolt_of_three` and `test_a_give_with_no_runner_on_the_host_is_refused_naming_it`, and `t-journey-cross`'s two gives.
- A crossed team's launch carries its stream, priority, intent and recipient: `test_runner.py` `test_two_bolts_given_in_order` and `test_a_reorder_sends_only_what_changed`.
- A crossed team's dependent launches once its After work has landed: `test_cross.py` `test_a_bolt_of_three` (b's `After` names a's launch) and `test_stages.py` `test_a_dependent_waits_on_the_work_it_comes_after`.
- Plan writes reach a crossed team's places: `test_amend.py` `test_a_unit_in_code_is_a_retry_of_its_construct_with_the_amendments_words`; `test_cross.py` `test_a_unit_dropped_drops_its_launch_and_a_dependent_held_for_it_is_launched_again_without_it`.
- Launched work keeps its bolt and order: `test_cross.py` `test_launched_work_moved_out_is_refused_naming_its_place_and_drop_then_add`.
- A crossed team's place is answered by a retry: `test_cross.py` `TestAnswer`, and `t-journey-cross`'s `crew answer a`.
- A crossed team's fix is a fix place on its bolt: `test_fix.py` `test_a_review_note_marked_fix_is_a_launch_of_a_fix_on_the_bolts_branch`, and `test_rail.py` `test_a_fix_in_flight_on_it_holds_its_landing`.
- A crossed team's landing that conflicts with main takes main in: `test_landing.py` `test_a_landing_refused_for_a_conflict_launches_one_take_main_fix_with_sluices_words`, `test_read_twice_it_launches_nothing_more` and `test_its_row_says_it_takes_main_first`.

**flywheel-state**: `test_runner.py` `test_never_renumbered`, `test_a_launch_with_no_stream_is_refused`, `test_a_retry_of_nothing_is_refused_naming_the_request` and `test_two_hosts_one_silent`; `tests/contract/test_git.py` `test_the_runners_branches_come_with_the_flywheels_branch_in_one_fetch_and_each_hosts_is_read_at_its_tip`.

**bolt-plan**: `test_stages.py`, a case for each of the six scenarios, read against flume 0.3.6's `status --json` fixtures in `tests/py/flume-0.3.6/`.

**main-level**: `test_main_fix.py`, a case for each of the three scenarios, and `t-journey-main-fix`.

**crew-rail**: `test_rail.py` `test_a_crossed_bolt_proven` and `test_a_fix_of_main_waits_beside_a_bolt_ahead_of_it_naming_ops_command_for_its_send`.

**crew-board**: `test_board.py` `test_a_crossed_teams_ledger`, `test_a_due_team`, `test_a_question_in_the_planners_band` and `test_a_fix_of_main_in_ops_band`; the mod's two new cases in `plugin/tests/status.test.ts`.

**review-batches**: `test_batches.py` `test_merged_then_batched` and `test_constructed_but_not_landed_is_not_yet_due`.

**run-record**: `test_record.py` `test_a_teams_crossing_names_its_stream_and_its_trace_reads_it_after_the_landing_that_crossed_it`, and `t-journey-cross`'s `team.cross` entry.

## Findings

### 1. A crossing on a held host is not proved, and the hold's own flow leaves it unfinished

The bolt-teams requirement *A team crosses once its last bolt of today's path has gone*, scenario *A held host*: "WHEN crw-4 has crossed and its host is held THEN its conductor and ops are not ended until the host goes".

- **No check proves it.** None of the checks task 2.4 names holds a held host: `test_hold.py` `TestCrossing` tests `crew.end_due` and `crew.due_of`; `test_cross.py` tests `runner.cross_due`; `t-journey-cross` crosses an unheld host. No test reaches `hold.renew` or `hold.cross_end` on a held host. `openspec/config.yaml` has it that every scenario is one a check proves, and a scenario no existing check proves is a check the change adds (`docs.6`).
- **The code does not meet it in the hold's flow.** A host is held for a restart as `crew hold`, then `crew hold wait`, whose `take_down` ends every crew agent there, keeping its pane, and then `crew go`. A crossed team whose conductor and ops were up when the host was held loses both to `take_down`, not to its crossing. After `crew go`:
  - `revive_cmd` refuses the team (`not_crossed`, `plugin/lib/plan.py` 12742), so neither role comes back. That part is right.
  - `update_here` finds each due an end (`crew.end_due`) and hands it to `crew _renew`. `hold.renew` reads it not up and returns: "is not up, so its team's crossing to Flume has nothing of it to end" (`plugin/lib/hold.py` 412–414). It never reaches `cross_end`.
  - `cross_end` is the only writer of `team.cross` (`plugin/lib/hold.py` 513). So the team's workspaces stay open, the team is not marked down, its slots are not freed (`plan.reap`), `team.cross` is never recorded, and the dispatchers are never told the team takes bolts of its kits. Every later `crew go` or `crew revive` on the host prints the team's refusal again.

  The requirement's "Once neither is up, crew SHALL record `team.cross` … and tell the partition's dispatchers" is not met on this path. The same holds for a crossed team whose conductor and ops are down for any other reason when its crossing comes due.

**For the code stage:** finish a crossing whose roles are already down, whether a hold's `take_down` ended them or anything else did. Once the team reads crossed and neither role is up, close its workspaces, mark it down, free its slots, record `team.cross` once and tell the dispatchers, never on a held host. Then add a check for the scenario. A decision over facts is the logic tier's: whether the crossing is due its close, given the path, the roles up and whether `team.cross` is already recorded. `t-journey-cross` can hold one case of its wiring, a hold and `crew hold wait` before the landing and `crew go` after it.

### 2. Not blocking: the give's skip of a crossed team's bound is shown only through a test helper

*A crossed team takes a third bolt* is proved by `test_cross.py`'s `give()` helper, which sets `Team` and `Path` and calls `plan.reach_places` as the give's change function does. Skipping `give_refusal` and the change function's two-bolt check for a crossed team happens in `plan.bolt_give` (`plugin/lib/plan.py` 1903–1912, 1946–1951), and no test reaches it with a team already holding a bolt. The code reads right. A case where the team holds a bolt when it is given another would pin it, and it can ride with Finding 1's fix.
