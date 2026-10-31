# Tasks

Build the groups in order: each stands on the ones before it, and each ends green on the moon task it names. The logic tier is `tests/suite logic` (moon task `tests:logic`), the contract tier `tests/suite contract` (`tests:contract`), the mod's cases `tests/suite mod` (`tests:mod`), and an end-to-end test `tests/suite <name>` (`tests:<name>`).

## 1. The setting

- [x] 1.1 `crew.load` reads `teams.json` version 2 as today, every team on today's path, and version 3 with every team's `flume` required, `false` or a stream's name, refusing anything else by team and file (design Decision 1; Task notes 1.1); passes `tests/py/test_teams.py`, verify `tests/suite logic` (`tests:logic`) ends with "0 failed".

## 2. A team's path and the crossing

- [x] 2.1 `runner.team_path` decides today's, due or crossed from the setting and the `Path` of each bolt the team holds (design Decision 2; Task notes 2.1); passes `tests/py/test_cross.py` in `tests:logic`.
- [x] 2.2 The plan's Bolt set allows `Path: flume` and the run record knows the act `team.cross` (design Decisions 2 and 3; Task notes 2.2); passes `tests/contract/test_recfix.py` in `tests:contract` and `tests/py/test_record.py` in `tests:logic`.
- [x] 2.3 `crew bolt give` refuses a due team naming each bolt it finishes first, and crew's tell that a team is free leaves a due team out (design Decision 2; Task notes 2.3); passes `tests/py/test_cross.py` and `tests/py/test_bolt_commands.py` in `tests:logic`.
- [x] 2.4 A crossed team's conductor and ops are due an end, given at their stop or by the hand that gives an idle agent its due restart, its workspaces closed and `team.cross` recorded once both are down, never on a held host (design Decision 3; Task notes 2.4); passes `tests/py/test_hold.py` and `tests/py/test_cross.py` in `tests:logic`, and verify `tests/suite t-journey-cross` (`tests:t-journey-cross`) ends with "0 failed".
- [x] 2.5 `crew up` and every other standing-agent or slot command of a crossed team refuses at once, naming where its work runs (design Decision 15; Task notes 2.5); passes `tests/py/test_cross.py` in `tests:logic`, and verify `tests/suite t-journey-cross` ends with "0 failed".

## 3. The exchange with the runner

- [x] 3.1 `requests.rec` on the flywheel's branch takes numbered, append-only requests, each checked by recfix and crew's own rules and written in the commit of the plan write that occasions it (design Decision 4; Task notes 3.1); passes `tests/contract/test_recfix.py` in `tests:contract` and `tests/py/test_runner.py` in `tests:logic`.
- [x] 3.2 crew fetches `<label>/runner/*` with `<label>/main` in one fetch and reads each host's runner, answers and places at its tip, naming a host whose branch is missing or unreadable (design Decision 4; Task notes 3.2); passes `tests/contract/test_git.py` in `tests:contract` and `tests/py/test_runner.py` in `tests:logic`.
- [ ] 3.3 `runner.stage_of` gives a crossed piece's stage from its launch, its answer and Flume's status as the runner carried it, every field guarded, pinned by flume 0.3.6 fixtures (design Decision 8; Task notes 3.3); passes `tests/py/test_runner.py` in `tests:logic`.

## 4. A crossed team's bolt launched whole

- [ ] 4.1 A give to a crossed team makes the bolt's branch through sluice, is refused only on a held host, a missing runner branch or the kit's policy, marks the bolt `Path: flume`, starts no agent and appends one launch per unit and chore with its `After` launches (design Decision 5; Task notes 4.1); passes `tests/py/test_cross.py` in `tests:logic`, and verify `tests/suite t-journey-cross` ends with "0 failed".
- [ ] 4.2 Every write that launches or reorders bolts sends the priorities the plan's order changed (design Decision 6; Task notes 4.2); passes `tests/py/test_runner.py` in `tests:logic`.
- [ ] 4.3 An added, amended or dropped unit or chore, and a dropped bolt, reach a crossed team's places as launches, retries and drops, and a move, split or `After` change of launched work is refused naming drop and add (design Decision 7; Task notes 4.3); passes `tests/py/test_cross.py` and `tests/py/test_amend.py` in `tests:logic`.
- [ ] 4.4 A bolt planned for a kit a crossed team builds, held by no team, is told to the partition's dispatchers that are up (design Decisions 3 and 5; Task notes 4.4); passes `tests/py/test_cross.py` in `tests:logic`.

## 5. Answers and fixes on a crossed team's bolt

- [ ] 5.1 `crew answer <work> "<words>"` appends the retry of the stage the place stopped short on or waits on, refused otherwise naming its stage (design Decision 9; Task notes 5.1); passes `tests/py/test_cross.py` in `tests:logic`, and verify `tests/suite t-journey-cross` ends with "0 failed".
- [ ] 5.2 `crew fix` on a crossed team launches a fix place on its bolt, `--drop` drops it, `--merge` and `--wait` refuse, and a fix in flight holds the bolt's landing (design Decision 10; Task notes 5.2); passes `tests/py/test_fix.py` in `tests:logic`.
- [ ] 5.3 A crossed team's landing that sluice refuses for a conflict with main launches its take-main fix with sluice's words by the act that reads the refusal, once (design Decision 10; Task notes 5.3); passes `tests/py/test_landings.py` and `tests/py/test_landing.py` in `tests:logic`.
- [ ] 5.4 The role table lets only the callers Decision 16 names run `crew answer`, `crew fix` on a crossed team and `crew main fix` (design Decision 16; Task notes 5.4); passes `tests/py/test_plan_roles.py` in `tests:logic`.

## 6. A fix of a red main

- [ ] 6.1 `crew main fix <kit> <name> "<words>"` launches a fix place on main with its submission held and ops as its recipient on the host of the crossed team building the kit, refused with `state.3`'s way where none does (design Decision 11; Task notes 6.1); passes `tests/py/test_main_fix.py` in `tests:logic`, and verify `tests/suite t-journey-main-fix` (`tests:t-journey-main-fix`) ends with "0 failed".
- [ ] 6.2 The kit's landings row carries a fix of main whose code delivered and whose submission waits held, and `crew main fix <kit> <name> --send` on the user's words appends the retry of its submission (design Decision 11; Task notes 6.2); passes `tests/py/test_rail.py` in `tests:logic`, and verify `tests/suite t-journey-main-fix` ends with "0 failed".

## 7. A crossed team's work in every view

- [ ] 7.1 `Stages.of` and `crew bolts`, text and JSON, read a crossed piece's stage from the runner's records and say each team's path (design Decisions 8 and 14; Task notes 7.1); passes `tests/py/test_bolt_commands.py` and `tests/py/test_stages.py` in `tests:logic`.
- [ ] 7.2 A crossed bolt reads proven and closes at its landing from its pieces' runner stages, a chore asked for no trailer (design Decision 12; Task notes 7.2); passes `tests/py/test_landing.py` in `tests:logic`.
- [ ] 7.3 A crossed team's unit enters a review batch once its change has landed on GitHub's bolt, read at that commit (design Decision 13; Task notes 7.3); passes `tests/py/test_batches.py` in `tests:logic`.
- [ ] 7.4 The rail's rows, the board's ledger and `board.agent_views` show crossed and due teams, the planner's band the places waiting on an answer and ops's the fixes in flight, and the mod draws them (design Decision 14, `code.8`; Task notes 7.4); passes `tests/py/test_board.py` and `tests/py/test_rail.py` in `tests:logic`, and verify `tests/suite mod` (`tests:mod`) ends with "0 failed".

## 8. Briefs and documentation

- [ ] 8.1 The dispatcher's, conductor's, planner's and main-level ops's briefs say what a due and a crossed team are and which commands answer, fix and land their work, each rule pinned by a phrase (design Decisions 2 to 11; Task notes 8.1); verify `tests/suite t-briefs t-roles` (`tests:t-briefs`, `tests:t-roles`) ends with "0 failed".
- [ ] 8.2 README, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage header say the same together (`docs.2`; Task notes 8.2); verify `tests/suite t-docs` (`tests:t-docs`) ends with "0 failed".

## 9. The tests' tasks

- [ ] 9.1 `tests/moon.yml` matches the tests after `tests/moon-tasks`, and the tests the change affects pass (Task notes 9.1); verify `tests/suite --affected` ends with "0 failed".
