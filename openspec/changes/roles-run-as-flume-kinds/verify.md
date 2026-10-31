# Verify: roles-run-as-flume-kinds

Read 2026-10-31 on deneb, at `73552850` on `change/roles-run-as-flume-kinds`, cut from `bolt/crew-runs-its-work-through-flume` at `91bd81f7`.

**Outcome: not archived.** One scenario fails: role-runs "Role records follow the teams file", *The planner stands again*, when the role moved back is the last of its partition's roles that runs as its kind. `crew main up` then leaves its role record on the branch (finding 1). Every other requirement and scenario of the change's eight spec deltas is met and proved by a check in crew's tiers. Every task is ticked, and every check the tasks name passes. The change goes back to its code stage for finding 1.

## Findings

### 1. `crew main up` leaves the last role record of a role that stands again (fix)

role-runs, "Role records follow the teams file": crew "SHALL remove the record of a role the teams file no longer runs as its kind", and *The planner stands again* has `crew main up madswan` leave `roles.rec` with no record of the planner once madswan's teams entry names the planner `false` again.

`plan.py` `kinds_up` (13025) builds `kinds`, the roles the partition runs as its kind now, and at 13032 returns when there are none, before it reads `roles.rec` or calls `roles_lines`. So when the role moved back is the partition's only one running as its kind, nothing removes its record. That is the case the design's migration starts with: the reviewer moves first, alone, and moving it back leaves `crew-reviewer`'s record standing. Nothing else removes a record: an ask writes `roles.rec` only for the role it asks (`ask_rec`, `roles_lines(..., [role])`), and no ask is written for a role that stands.

Reproduced in the logic tier's harness (`tests/py/test_asks.py` `on_branch`, `madswan`, `written`), as a scratch case not committed:

- madswan's `roles.rec` holds the planner's record, as `roles_lines` wrote it while `flume` named `madswan-main` for the planner;
- the fleet then names every role `false`;
- `plan.kinds_up(stood, "madswan", [])` writes nothing, and `roles.rec` still holds `['planner']`.

The same case with ops still running as its kind (`madswan(ops="madswan-ops")`) removes the planner's record and keeps ops's, as `test_roles_rec_follows_the_teams_file_and_a_branch_with_nothing_due_gets_none` shows for `roles_lines`. That test calls `roles_lines` directly, always with a role left running as its kind, and `t-journey-main` never moves a role back, so no check covers the failing case.

What follows from the stale record: the runner keeps the role's record (R1, R2), so a run of it is launched whenever anything is pending for its address: an ask written before the move and never taken, or a place whose launch request names `<label>/<role>`. That run's `crew role start` refuses (`run_named`: the partition no longer runs the role as its kind), so the run stops short and holds its place until `flume retry`, beside the role's standing agent.

The fix: `kinds_up` brings `roles.rec` to match the teams file whenever `asks.roles_due` finds anything due or gone, even with no role running as its kind, and returns early only before the standing-agent loop. The fix carries a case proving it: a logic case of `kinds_up` with the partition's last kind role moved back, or `t-journey-main` naming the planner and reviewer `false` again and reading `roles.rec` empty of both after `crew main up wldn`.

## Checks

| Check | Result |
|---|---|
| `tests/suite --affected` (task 13.2) | 35 passed (35 replayed), 0 failed: every task of the suite, the command core having changed; each replayed from a run that passed on this host with identical inputs |
| `tests/suite --force logic contract mod t-roles t-journey-roles t-journey-signals t-journey-review t-journey-land t-cards t-journey-main t-hold t-session-hook t-briefs t-docs` (every task the tasks name) | 14 passed (0 replayed), 0 failed |
| `tests/moon-tasks --check` | in step |
| `openspec validate roles-run-as-flume-kinds --strict` | valid |
| Scratch case of finding 1 (logic tier harness, not committed) | 1 failed (the last kind role moved back), 1 passed (the control, ops still running as its kind) |

## Tasks

All 24 tasks, 1.1 to 13.2, are ticked, and the check each names passes. The tasks marked *needs teams-cross* (4.2, 5.4, 6.1, 11.1) rest on `teams-cross-to-flume-as-their-bolts-land`, which is on the bolt at `91bd81f7`: `runner.py`, `requests.rec`, `runner_facts` and the runner's branches are there. Task 10.1's check passes but does not cover finding 1.

## Requirements and scenarios

Each scenario is matched to the check that proves it.

**role-runs**
- crew's release carries a kind for each main-level role: `test_role_kinds.py` `test_it_declares_one_kind_for_each_role_a_partition_can_run_as_its_kind`, `TestFlumesFormat`, `test_each_kind_is_one_turn_that_lands_nothing_and_ends_at_its_report_in_the_places_own_folder`, `test_nothing_names_a_model_instructions_or_an_environment`.
- A turn's prompt starts and ends the turn: `test_role_kinds.py` `TestThePrompt`.
- An ask is a record naming a role (*A malformed ask*): `tests/contract/test_recfix.py` `test_an_ask_or_a_role_record_the_headers_do_not_allow_is_refused`, an ask with no `Role` among them, and `test_the_asks_turns_and_role_records_crew_writes_pass_recfix`.
- An ask with a key is written once (*One answer seen twice*): `test_asks.py` `TestKeyed`, `test_an_ask_whose_key_the_tip_holds_writes_nothing`, `test_an_ask_alone_whose_key_is_held_commits_nothing_and_says_so`; `t-cards` hands `crew _answered` the same notice twice and reads one ask.
- An ask is written with the act that makes it (*A capture*): `test_signals.py`, `test_asks.py` `test_an_ask_in_its_acts_commit_is_named_beside_the_acts_entry_and_a_held_key_is_kept_to_say`; `t-journey-signals`.
- A tell, a notice or a send to a role that runs as its kind is an ask: `test_tell_asks.py` `TestTell` (*A tell to the planner*, *crew's own notice*) and `TestSend`.
- A capture and a landing are asks (*A landing*): `test_landing.py`; `t-journey-land`.
- A card's answer, an opening and a batch are asks: `test_card_commands.py`, the `card_ask` cases for ops's and the planner's runs and for a standing role's name (*A deploy approved from the phone*, *A standing agent's card*); `test_asks.py` `TestOpen`; `test_review.py`.
- The follower hears Pending You's notice while a role here runs as its kind: `test_card_commands.py` `test_the_follower_hears_the_notice_only_where_a_role_whose_main_level_is_here_runs_as_its_kind`; `test_board.py` `test_the_follower_runs_pending_yous_notice_while_a_role_here_runs_as_its_kind`.
- A role that stands is asked nothing (*A role still standing*): `test_tell_asks.py` `test_a_role_that_stands_is_refused_when_not_up_and_never_asked`, `TestAsksInstead` `test_a_role_that_stands_is_never_asked`; the standing paths of `test_signals.py`, `test_landing.py` and `test_review.py`.
- A tell finds a standing agent of the role first (*The standing agent not yet stopped*): `test_tell_asks.py` `test_a_standing_agent_still_up_is_typed_into_and_asked_nothing`, `test_herdr_unread_refuses_naming_it_and_asks_nothing`.
- A place that waits on a role is pending for the role: `test_asks.py` `TestWaitsOn` (*A stage asks the planner*, *A stage that delivers*), `test_a_place_that_waits_on_the_role_is_taken_and_a_runner_that_cant_be_read_is_said`.
- A role's landed work is pending for the role (*A record lands*): `test_asks.py` `test_a_place_a_role_launched_is_pending_for_it_once_it_has_landed`.
- A role record names its run (*The planner's record*): `test_asks.py` `test_the_planners_record_names_its_run`.
- Role records follow the teams file: *The planner moves* is `t-journey-main` (`roles.rec` holding the planner's and the reviewer's records after `crew main up wldn`) and `test_roles_rec_follows_the_teams_file_and_a_branch_with_nothing_due_gets_none`; *An ask before main up* is `test_the_first_ask_starts_asks_rec_and_writes_its_roles_record_beside_it`; *The planner stands again* **fails** when the planner is the partition's last role running as its kind (finding 1), and holds while another still does.
- A role has at most one run, wanted while anything is pending: `test_asks.py` `TestPending` (*A burst*, *An ask during a run*, *Nothing pending*), `test_an_ask_written_after_the_start_waits_for_the_next_run`.
- A run's start takes everything pending: `test_asks.py` `TestStart` (*Two asks waiting*, *Nothing waiting*, *Not a run*); `t-journey-roles`.
- A run's start gives its brief and what it took (*What the planner's run reads*): `test_asks.py` `test_two_asks_waiting_are_one_turn_and_it_prints_the_brief_then_each_ask_then_the_cards`, `TestRunCards`.
- A start takes again what a lost run took: `test_asks.py` `test_a_lost_runs_open_turn_is_superseded_and_its_ask_taken_again`, `TestTurns`.
- A run's end answers what it took: `test_asks.py` `TestEnd` (*A turn ends*, *No turn open*); `t-journey-roles`.
- A run is named as its role: `test_plan_roles.py` (*The planner's run proposes*, *A place of another kind*); `plugin/bin/crew` resolves the run's name with `crew.py run-name` before forwarding (`code.3`).
- A run's brief says how a turn goes (*Every brief filled*): `t-briefs`, `t-roles`.
- A role's work that lands is a place it launches (*The design agent's records*): `test_asks.py` `TestLand`; `tests/contract/test_recfix.py`; `t-journey-roles`.
- The user opens a role to talk (*No run live*, *A run live*): `test_asks.py` `TestOpen`, `TestRoleRun`; `t-journey-roles`.
- A turn the user opened lasts their conversation: `plugin/flume/turn.md` step 2 and the five briefs' `{{TURN}}`, pinned by `test_role_kinds.py` and `t-briefs`. The conversation itself is the agent's, which no tier runs.
- Main-level ops's landing from a run does not wait (*A landing that conflicts*): `test_landing.py`; `t-journey-land`.
- A run's model is its definition's (*An override*): `test_asks.py` `test_a_runs_model_is_its_definitions_after_the_teams_files_override`.

**main-level**
- Partitions are declared in the teams file: `test_teams.py` `test_version_4_names_each_roles_stream_or_that_it_stands`, `test_below_version_4_every_role_stands_whatever_the_entry_holds`, `test_a_role_with_no_kind_is_refused` and the version 4 refusals; the scenarios unchanged pass.
- The main level is one herdr workspace: *Two roles run as their kinds* and *A standing planner from before* are `t-journey-main` (no tab, nothing started or greeted, the role records written, the idle standing planner ended, `crew revive` passing both over); `kinds_up` leaves a working agent and says so; the scenarios unchanged pass.
- Any agent crew starts is reached by name (*A role that runs as its kind*): `test_tell_asks.py`; the scenarios unchanged pass.
- A role that runs as its kind is not started by crew-role: *The planner started by hand* is `t-roles`; *Main status* is `test_teams.py` `test_main_status_says_a_role_runs_as_its_kind_whether_a_run_stands_and_how_many_asks_wait` and `t-journey-main`.

**operator-agent**
- The operator is a main-level role (*The operator runs as its kind*): `crew.main_sessions` filters each role that runs as its kind out of the tabs `crew main up` opens; `test_tell_asks.py` for the tell.
- Anything sent to another team or partition reaches its operator (*An operator that runs as its kind*): `test_tell_asks.py` `TestSend`.

**review-batches**: `test_review.py` (*A reviewer that runs as its kind*, *Waiting on a reviewer that runs as its kind*, *A batch delivered*, *A summary not written*); `t-journey-review`.

**rail-cards** (*A proposal approved while the planner runs as its kind*): `test_card_commands.py` `card_ask` cases and `t-cards`; the run's read of its cards in its own name is `test_asks.py` `TestRunCards`.

**crew-board**: `test_board.py` `test_a_run_with_an_ask_waiting`, `test_nothing_waiting` and `test_a_lost_run`, beside `test_a_run_that_stopped_short_is_named_with_its_words`, with the case pinning every key the mod reads (`code.8`); `plugin/tests/status.test.ts` for the band.

**run-record**: `test_record.py` `test_a_tell_that_is_an_ask_records_its_length_and_never_its_text` and `test_a_turn_traced_lists_its_asks_its_begin_taking_them_and_its_end`.

**host-holds-and-updates**: `test_hold.py` (*The planner moves*: ended idle, its pane left, recorded; *An update after the move*: `crew update` passes it over; a held host ends nothing); `t-hold`, `t-session-hook`.

## Rules

The design names each rule it departs from, with the user's settlement of 2026-10-31 as its reason, for the design agent to amend at the landing (`docs.5`, `docs.7`): `roles.7`, `roles.9`, `teams.6`, `teams.7`, `teams.11` and `code.5`. The change touches no page under `docs/architecture/` or `docs/adr/`.
