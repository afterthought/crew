# Verify: teams-cross-to-flume-as-their-bolts-land

Read 2026-10-31 on mac-studio, at `c15a432d` on `change/teams-cross-to-flume-as-their-bolts-land`, cut from `bolt/crew-runs-its-work-through-flume` at `227870c3`.

**Outcome: archived.** Every requirement and scenario of the change's eight spec deltas is met and proved by a check in crew's tiers, every task is ticked, and every check the tasks name passes. Two findings below are not blocking.

## Checks

| Check the tasks name | Result |
|---|---|
| `tests/suite --force logic contract mod t-journey-cross t-journey-main-fix t-briefs t-roles t-docs t-hold` | 9 passed (0 replayed), 0 failed |
| `tests/suite --affected` (task 9.1) | 34 passed (34 replayed), 0 failed: every task of the suite, the command core having changed |
| `openspec validate teams-cross-to-flume-as-their-bolts-land --strict` | valid |

`tests/moon.yml` is in step with the tests: `tests/suite` refuses to run when it is not.

## Tasks

All 28 tasks, 1.1 to 9.1, are ticked, and the check each names passes.

## Requirements and scenarios

Each scenario is matched to the check that proves it. The two MODIFIED requirements of `bolt-teams` keep every scenario the main spec holds.

**bolt-teams**
- Teams are fixed in the teams file: *The first version of the file* is `test_teams.py` `test_another_version_is_refused_naming_2_and_3`; *Version 3 names each team's setting*, *A team in version 3 without its setting* and *Version 2 still loads* are `test_teams.py`'s version-3 cases; the other two are unchanged and pass.
- A team builds one bolt and may hold one more: *A crossed team takes a third bolt* is `test_cross.py` `test_a_crossed_team_takes_a_third_bolt_and_its_launches_follow_the_requests_already_written`, and through the command `t-journey-cross`, crossed swb-1, holding `next` with none of its work merged, given `more` and then `last` (task 4.5); the other four are unchanged and pass.
- A team's path is today's, due or crossed: `test_cross.py` `TestPath`, one case per scenario; `t-journey-cross` shows the due team's conductor and ops running on.
- A team due to cross is given no new bolt: `test_cross.py` `TestDue`, and `t-journey-cross`, the plan unchanged and no `bolt/next` made.
- A team crosses once its last bolt of today's path has gone: *A due team's bolt lands* is `t-journey-cross` with `test_hold.py` `TestCrossing`. *A held host* is `test_hold.py` `test_a_held_host_ends_neither_role_until_it_goes`, and `t-journey-cross`'s swb-2, whose landing on the held host hands both roles back to `crew go`.
- A crossed team is closed once neither of its roles is up: *Its roles ended by the host's hold* is `t-journey-cross`'s swb-2: `crew hold` and `crew hold wait` end its roles with its workspaces kept, its bolt lands with nothing closed or recorded, and `crew go` closes its workspaces, brings neither role back and records `team.cross` naming `wldn`, once; `test_hold.py` `TestCrossingClosed` proves the close's parts, the team marked down, its slots freed and the dispatchers told, and that a held host closes nothing until it goes. *A crossing already recorded* is `TestCrossingClosed` `test_neither_role_up_closes_the_team_records_its_crossing_and_tells_the_dispatchers_once` and `test_the_record_is_read_from_this_hosts_day_files_newest_first`, with `test_cross.py` `TestCrossing`'s cases of `cross_close` and `cross_recorded`; `t-journey-cross`'s second `_renew` at `crew go` says the crossing is recorded already.
- A crossed team runs no standing agent: `test_cross.py` `TestNoStandingAgent`, and `t-journey-cross` for `crew up`, with no ssh to the host and no pane.
- A crossed team's give launches its bolt whole: `test_cross.py` `test_a_bolt_of_three` and `test_a_give_with_no_runner_on_the_host_is_refused_naming_it`, and `t-journey-cross`'s gives.
- A crossed team's launch carries its stream, priority, intent and recipient: `test_runner.py` `test_two_bolts_given_in_order` and `test_a_reorder_sends_only_what_changed`.
- A crossed team's dependent launches once its After work has landed: `test_cross.py` `test_a_bolt_of_three` (b's `After` names a's launch) and `test_stages.py` `test_a_dependent_waits_on_the_work_it_comes_after`.
- Plan writes reach a crossed team's places: `test_amend.py` `test_a_unit_in_code_is_a_retry_of_its_construct_with_the_amendments_words`; `test_cross.py` `test_a_unit_dropped_drops_its_launch_and_a_dependent_held_for_it_is_launched_again_without_it`.
- Launched work keeps its bolt and order: `test_cross.py` `test_launched_work_moved_out_is_refused_naming_its_place_and_drop_then_add`.
- A crossed team's place is answered by a retry: `test_cross.py` `TestAnswer`, and `t-journey-cross`'s `crew answer a`.
- A crossed team's fix is a fix place on its bolt: `test_fix.py` `test_a_review_note_marked_fix_is_a_launch_of_a_fix_on_the_bolts_branch`, and `test_rail.py` `test_a_fix_in_flight_on_it_holds_its_landing`.
- A crossed team's landing that conflicts with main takes main in: `test_landing.py` `test_a_landing_refused_for_a_conflict_launches_one_take_main_fix_with_sluices_words`, `test_read_twice_it_launches_nothing_more` and `test_its_row_says_it_takes_main_first`.

**flywheel-state**: `test_runner.py` `test_never_renumbered`, `test_a_launch_with_no_stream_is_refused`, `test_a_retry_of_nothing_is_refused_naming_the_request` and `test_two_hosts_one_silent`; `tests/contract/test_git.py` `test_the_runners_branches_come_with_the_flywheels_branch_in_one_fetch_and_each_hosts_is_read_at_its_tip`.

**bolt-plan**: `test_stages.py`, one case per scenario, read against flume 0.3.6's `status --json` fixtures in `tests/py/flume-0.3.6/`.

**main-level**: `test_main_fix.py`, one case per scenario, and `t-journey-main-fix`.

**crew-rail**: `test_rail.py` `test_a_crossed_bolt_proven` and `test_a_fix_of_main_waits_beside_a_bolt_ahead_of_it_naming_ops_command_for_its_send`.

**crew-board**: `test_board.py` `test_a_crossed_teams_ledger`, `test_a_due_team`, `test_a_question_in_the_planners_band` and `test_a_fix_of_main_in_ops_band`; the mod's cases in `plugin/tests/status.test.ts`, "the planner's band draws a crossed place's question and its team's Flume stream" and "main-level ops's band draws a fix of main in flight with its stage" (`code.8`).

**review-batches**: `test_batches.py` `test_merged_then_batched` and `test_constructed_but_not_landed_is_not_yet_due`.

**run-record**: `test_record.py` `test_a_teams_crossing_names_its_stream_and_its_trace_reads_it_after_the_landing_that_crossed_it`, and `t-journey-cross`'s `team.cross` entries.

## Rules

The design names each rule it departs from, with its reason, for the design agent to amend at the landing (`docs.5`, `docs.7`): `code.5`, `state.2`, `plan.13` and `plan.11`, `teams.16`, `teams.21`, `teams.23`, `roles.9`, `record.md`'s acts, and `read.5`, whose departure is that whether a team's crossing is recorded is read from the team's host's own run record. That read holds: `record.emit` appends to the host's day file before it pushes, and nothing removes a day file, so a crossing recorded there stays readable.

## Findings

### 1. Not blocking: a crossing already closed is still said to be due an end at every update

Once a team's crossing is closed, its conductor's and ops's start files stay in `~/.local/state/crew/sessions`. So `crew.due_of` keeps reading each due an end (`end_due`, `plugin/lib/crew.py` 1967–1982). Every later `crew update` and `crew go` on the host prints "<agent> is due (its team has crossed to Flume, whose places run its work): it is ended once it is idle, never restarted" for each (`hold.update_here`, `plugin/lib/hold.py` 356–361) and hands each to `crew _renew`. That run finds the role down and says the crossing is recorded already. Nothing is closed or recorded again, so *A crossing already recorded* holds, but the update's words promise an end that never comes. A chore could leave out of `end_due` a crossed team whose crossing `crossing_recorded` already holds.

### 2. Not blocking: the journey's held-host case was not run against the code before its fix

`c15a432d` says `t-journey-cross`'s swb-2 case fails at `crew go` on the code before it. I did not run it there. Reading the code bears it out: before that commit, `hold.renew` returned at "is not up" without closing anything. The case waits for "swb-2 has crossed to Flume: its workspaces are closed…", which only `close_crossing` prints.
