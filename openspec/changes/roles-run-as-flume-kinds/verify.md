# Verify: roles-run-as-flume-kinds

Read 2026-10-31 on deneb, at `0e0d6443` on `change/roles-run-as-flume-kinds`, cut from `bolt/crew-runs-its-work-through-flume` at `91bd81f7`, which has not moved since.

**Outcome: the work holds.** Every requirement and scenario of the change's eight spec deltas is met and proved by a check in crew's tiers, every one of its 25 tasks is ticked, and every check the tasks name passes. The change is archived.

## Checks

| Check | Result |
|---|---|
| `tests/suite --affected` (task 13.2) | 35 passed (35 replayed), 0 failed: every task of the suite, the command core having changed; each replayed from a run that passed on this host with identical inputs |
| `tests/suite --force logic contract mod t-roles t-journey-roles t-journey-signals t-journey-review t-journey-land t-cards t-journey-main t-hold t-session-hook t-briefs t-docs` (every task the tasks name) | 14 passed (0 replayed), 0 failed |
| `tests/moon-tasks --check` | in step |
| `openspec validate roles-run-as-flume-kinds --strict` | valid |
| `tests/py/test_asks.py` `TestMainUp` (task 10.4) against `plan.py` as it stood at `b779ceba`, before `kinds_up` read `roles.rec` with no role running as its kind | 2 failed (the last kind role moved back; a fetch refused, said), 1 passed (ops still running as its kind): the cases reproduce what they prove, and pass at `0e0d6443` |

## Tasks

All 25 tasks, 1.1 to 13.2, are ticked, and the check each names passes. The tasks marked *needs teams-cross* (4.2, 5.4, 6.1, 11.1) rest on `teams-cross-to-flume-as-their-bolts-land`, which is on the bolt at `91bd81f7`: `runner.py`, `requests.rec`, `runner_facts` and the runner's branches are there.

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
- Role records follow the teams file: *The planner moves* is `t-journey-main` (`roles.rec` holding the planner's and the reviewer's records after `crew main up wldn`) and `test_roles_rec_follows_the_teams_file_and_a_branch_with_nothing_due_gets_none`; *An ask before main up* is `test_the_first_ask_starts_asks_rec_and_writes_its_roles_record_beside_it`; *The planner stands again* is `test_asks.py` `TestMainUp` `test_a_role_that_stands_again_leaves_roles_rec_though_it_was_the_last_to_run_as_its_kind`, `plan.kinds_up` removing the planner's record in one commit both where it was the partition's last role running as its kind and where ops still runs as its kind, and `test_with_none_running_as_its_kind_no_record_no_branch_or_a_branch_unread_writes_nothing` for a branch with no record, no branch, and a fetch refused, which is said and removes nothing (`read.1`).
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

`crew main up` for a partition running no role as its kind now fetches its flywheel's branch to read `roles.rec`, writing nothing where no record is held, and saying a refused fetch and going on: today's path otherwise unchanged (`roles.8`), and no new reach, since the same up already writes its `main.up` entry to that branch (`read.5`).

The design names each rule it departs from, with the user's settlement of 2026-10-31 as its reason, for the design agent to amend at the landing (`docs.5`, `docs.7`): `roles.7`, `roles.9`, `teams.6`, `teams.7`, `teams.11` and `code.5`. The change touches no page under `docs/architecture/` or `docs/adr/`.
