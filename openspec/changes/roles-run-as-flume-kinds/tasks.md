# Tasks

Built after `teams-cross-to-flume-as-their-bolts-land` (design *What this change rests on*, 1). A task marked *needs teams-cross* uses that change's exchange with the runner, `requests.rec` or `runner.read_runners`; where that piece is not on the bolt, stop short with `flume needs --found` and name it.

## 1. The teams file names the roles that run as kinds

- [x] 1.1 crew reads `teams.json` versions 2, 3 and 4, every partition at version 4 carrying its `flume` of five roles, read and refused as the main-level delta says, every role standing below 4, and the test world writes version 4 with every role `false` (design Decision 3; Task notes 1.1); passes `tests/py/test_teams.py`, and the moon tasks `tests:logic` and `tests:t-roles` (`tests/suite logic t-roles`) end with "0 failed".
- [x] 1.2 `crew.py` answers whether a partition runs a role as its kind and which role and partition an agent name is (design Decision 3; Task notes 1.2); passes `tests/py/test_teams.py` under the moon task `tests:logic`.

## 2. Asks, turns and role records

- [x] 2.1 `plugin/lib/asks.py` decides what is pending for a role, whether it is wanted, its open and superseded turns, an ask's key already held, the next numbers, and the role records due, each from plain facts (design Decisions 4, 6 and 7; Task notes 2.1); passes a new `tests/py/test_asks.py` under the moon task `tests:logic`.
- [x] 2.2 crew writes `asks.rec` and `roles.rec` on the flywheel's branch through `land()`, with headers `recfix --check` holds them to, an ask written alone or in its act's commit (design Decision 4; Task notes 2.2); passes `tests/contract/test_recfix.py`, and the moon task `tests:contract` (`tests/suite contract`) ends with "0 failed".
- [ ] 2.3 The run record gains `ask`, `turn.begin` and `turn.end` entries holding no words, and `crew trace agent/<label>-<role>` lists them (run-record delta; Task notes 2.3); passes `tests/py/test_record.py` under the moon task `tests:logic`.

## 3. The kinds in crew's release

- [ ] 3.1 `plugin/flume/kinds.toml` declares the five kinds and `plugin/flume/turn.md` is their prompt, as Flume's format reads them (design Decisions 1 and 2; Task notes 3.1); passes a new `tests/py/test_role_kinds.py` under the moon task `tests:logic`.

## 4. A run's name, start and end

- [ ] 4.1 A command run in a role's run takes the role's name and partition from its place, through `agent()`, `may_write` and the label reads, and carries them when forwarded (design Decision 8; Task notes 4.1); passes `tests/py/test_plan_roles.py` under the moon task `tests:logic`.
- [ ] 4.2 `crew role start` takes everything pending, records the turn, writes the brief's file and prints it and the asks, and `crew role end` answers the turn and always writes the report, each refusing outside a run (design Decisions 7 and 9; Task notes 4.2); *needs teams-cross* for the ends; passes `tests/py/test_asks.py`, and the moon task `tests:t-journey-roles` (`tests/suite t-journey-roles`) ends with "0 failed".

## 5. What writes an ask

- [ ] 5.1 A tell or a send to a role that runs as its kind, with no standing agent of it up, is an ask, crew's own notices among them, and one still up is typed as today (design Decision 5; Task notes 5.1); passes `tests/py/test_send.py` and a new `tests/py/test_tell_asks.py`, and the moon tasks `tests:logic` and `tests:t-journey-roles` end with "0 failed".
- [ ] 5.2 A signal captured through crew is an ask of a design agent that runs as its kind, in the capture's commit (design Decision 5; Task notes 5.2); passes `tests/py/test_signals.py`, and the moon task `tests:t-journey-signals` ends with "0 failed".
- [ ] 5.3 A bolt's landing is an ask of the planner and the design agent, and a landing that did not land one of ops with sluice's words, in the landing's write (design Decision 5; Task notes 5.3); passes `tests/py/test_landing.py` under the moon task `tests:logic`.
- [ ] 5.4 `crew role open` writes the user's ask, names a live run instead, or refuses when the runner's records can't be read (design Decision 13; Task notes 5.4); *needs teams-cross*; passes `tests/py/test_asks.py`, and the moon task `tests:t-journey-roles` ends with "0 failed".

## 6. A role's work that lands

- [ ] 6.1 `crew role land` writes a chore launch in the named repository on its default branch, the brief whole and the run's address its recipient, refusing outside a run and for a repository crew does not name (design Decision 10; Task notes 6.1); *needs teams-cross*; passes `tests/py/test_asks.py`, and the moon task `tests:t-journey-roles` ends with "0 failed".

## 7. The reviewer

- [ ] 7.1 `crew review` asks a reviewer that runs as its kind its batch and `--wait` refuses for it, and `crew review delivered` records each written batch, starts its session, raises its card in the planner's name and asks the planner (design Decision 11; Task notes 7.1); passes `tests/py/test_review.py`, and the moon task `tests:t-journey-review` ends with "0 failed".

## 8. Main-level ops's landing from a run

- [ ] 8.1 `crew bolt submit` from ops's run returns once each bolt is queued, and the landing's read asks the planner, the design agent or ops as it lands or not (design Decision 12; Task notes 8.1); passes `tests/py/test_landing.py`, and the moon task `tests:t-journey-land` ends with "0 failed".

## 9. A card's answer

- [ ] 9.1 The follower's card sweep writes one ask per answer on a card owned by a role that runs as its kind (design Decision 5; Task notes 9.1); passes `tests/py/test_card_commands.py`, and the moon task `tests:t-cards` ends with "0 failed".

## 10. Standing agents stop

- [ ] 10.1 `crew main up`, `down`, `status` and `crew revive` start, greet and bring back no role that runs as its kind, `main up` writes its role record and ends its standing agent once not working, and `main status` says how it runs (design Decision 14; Task notes 10.1); passes `tests/py/test_teams.py`, and the moon task `tests:t-journey-main` ends with "0 failed".
- [ ] 10.2 A standing agent whose role now runs as its kind is ended at its next stop and never restarted, and `crew update` passes it over (design Decision 14; Task notes 10.2); passes `tests/py/test_hold.py`, and the moon tasks `tests:t-hold` and `tests:t-session-hook` end with "0 failed".
- [ ] 10.3 `crew-role` refuses a role that runs as its kind, naming `crew role open`, and starts no Claude (design Decision 14; Task notes 10.3); the moon task `tests:t-roles` ends with "0 failed".

## 11. Views

- [ ] 11.1 `board.agent_views` gives each run its view and the board's attention line names a run stopped short or lost, with the case pinning every key the mod reads (design Decision 15, `code.8`; Task notes 11.1); *needs teams-cross*; passes `tests/py/test_board.py` under the moon task `tests:logic`.
- [ ] 11.2 crew's mod draws a run's view in its band (design Decision 15; Task notes 11.2); the moon task `tests:mod` (`tests/suite mod`) ends with "0 failed".

## 12. Briefs

- [ ] 12.1 The five briefs carry `{{TURN}}`, filled for a role that runs as its kind and for one that stands, each pinned by its phrases, and every brief prints with no token unfilled for a partition running all five as kinds (design Decision 9; Task notes 12.1); the moon tasks `tests:t-briefs` and `tests:t-roles` end with "0 failed".

## 13. Documentation and the suite

- [ ] 13.1 README, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage say the role commands, `crew review delivered`, a partition's `flume`, `asks.rec` and `roles.rec` together (`docs.2`; Task notes 13.1); the moon task `tests:t-docs` ends with "0 failed".
- [ ] 13.2 `tests/moon.yml` matches the tests after `tests/moon-tasks`, `t-journey-roles` among them, and the tests the change affects pass (`tests.10`; Task notes 13.2); verify `tests/suite --affected` ends with "0 failed".
