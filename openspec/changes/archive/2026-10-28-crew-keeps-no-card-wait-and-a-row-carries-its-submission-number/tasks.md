# Tasks

## 1. No waiting process for a card

- [x] 1.1 `crew card wait` refuses at once naming `crew card read <key>`, and the waits and the readings they started are gone from `plan.py` (design Decision 1; Task notes 1.1); passes `tests/py/test_card_commands.py`, verify `tests/suite logic` ends with "0 failed".
- [x] 1.2 `crew card read` gives a batch's card and reading together (closing the card, recording the batch read, ending the session), a landing reading's notes to its conductor, and a long proposal reading's decision, each from a decision of plain facts (design Decisions 2 and 4; Task notes 1.2); passes `tests/py/test_cards.py` and `tests/py/test_landings.py`.
- [x] 1.3 `crew card sweep` tells a sent reading's owner once, marks it told only when the tell goes through, and records a wordless batch send read (design Decisions 3 and 4; Task notes 1.3); passes `tests/py/test_card_commands.py`, and verify `tests/suite t-journey-review t-cards` ends with "0 failed".
- [x] 1.4 A conductor restarted for a give is told of its waiting bolt's reading with no wait to start, and `hold.py` names no `crew card wait` (bolt-teams delta; Task notes 1.4); passes `tests/py/test_teams.py` and `tests/py/test_hold.py`.

## 2. Every submission's number on its bolt's row

- [x] 2.1 The gather reads `sluice overview --json` once per kit main on a host holding a bolt of it, every field guarded, a failure said (design Decision 6; Task notes 2.1); passes a case on sluice 0.51.3's overview fixture in `tests/py/`, verify `tests/suite logic` ends with "0 failed".
- [x] 2.2 `crew bolts`, as text and JSON, shows each standing merge's number and state on its unit's, chore's or fix's line and the landing's on the bolt's head line, and says once when the queue can't be read (design Decision 6; Task notes 2.2); passes `tests/py/test_bolt_submissions.py`.
- [x] 2.3 The board's ledger, `board.agent_views` and the mod draw the same numbers in the conductors' and main-level ops's bands (design Decision 6, `code.8`; Task notes 2.3); passes `tests/py/test_board.py` and verify `tests/suite mod` ends with "0 failed".
- [x] 2.4 `crew bolt submit` waits again on a landing standing at the bolt's head and submits as before past one standing at another head, saying which (design Decision 7; Task notes 2.4); passes `tests/py/test_landing.py`, and verify `tests/suite t-journey-land` ends with "0 failed".

## 3. Briefs and documentation

- [x] 3.1 The planner's, the conductor's and main-level ops's briefs say to read cards with `crew card read`, that crew tells them when a reading is sent, that the rows carry each submission's number, and name no `crew card wait` (design Decisions 2, 3 and 7; Task notes 3.1); verify `tests/suite t-briefs t-roles` ends with "0 failed".
- [x] 3.2 README, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage header say the same together (`docs.2`; Task notes 3.2); verify `tests/suite t-docs` ends with "0 failed".
- [x] 3.3 `tests/moon.yml` matches the tests after `tests/moon-tasks`, and the affected tests pass (Task notes 3.3); verify `tests/suite --affected` ends with "0 failed".
