# Tasks

## 1. A give waits only for the held bolt's proof

- [x] 1.1 `plan.give_refusal` refuses a give only while the team holds two bolts or a held bolt is unread, empty, has a unit or chore not merged, or a verification not green, and `holding` is gone (design, Decision 1; Task notes 1.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_bolt_commands.py`.
- [x] 1.2 `crew bolt give` gives a team holding a proven bolt its next one and refuses a third (design, Decision 2; Task notes 1.2). Verify `tests/suite t-journey-land t-journey-teams` ends with "0 failed".

## 2. The bolt a team builds is the one given last

- [x] 2.1 `plan.building` picks the bolt given last, and the branch hint, a team's kit, a unit's fallback bolt, ops's greeting and `where_of` use it or name both (design, Decision 3; Task notes 2.1). Verify `tests/suite logic` ends with "0 failed".

## 3. A fix names its bolt

- [x] 3.1 `crew fix` takes `--bolt`, refuses a new fix that names none while two bolts are held, finds a fix in flight by name, and the forecast's take-main command names the bolt when two are held (design, Decision 4; Task notes 3.1). Verify `tests/suite logic t-journey-fix` ends with "0 failed".

## 4. A give beside a waiting bolt restarts at the next stop

- [x] 4.1 A give to a team holding a proven bolt hands its conductor and ops to their restart at the next stop, and the conductor's greeting names both bolts, the open landing card with its adopting line and each fix in flight (design, Decision 5; Task notes 4.1). Verify `tests/suite logic t-journey-land` ends with "0 failed".

## 5. A merge's end frees the team

- [x] 5.1 A merge's end raises the landing card of the bolt it merged into, changes the other's card when a yes now frees the team, and tells the dispatchers when the team is free and a bolt is planned for it (design, Decision 6; Task notes 5.1). Verify `tests/suite logic t-journey-land` ends with "0 failed".

## 6. The rail and the card say what a yes frees

- [x] 6.1 The landing row says the bolt waits to land and what its team builds meanwhile or what a yes frees, and the landing card's summary says what a yes frees (design, Decision 7; Task notes 6.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_rail.py`, `tests/py/test_cards.py` and `tests/py/test_landing.py`.

## 7. The board and the bands draw a waiting bolt

- [ ] 7.1 A proven bolt's ledger says it waits to land, beside the bolt its team builds, in the board and the conductor's band (design, Decision 8; Task notes 7.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_board.py`, and `tests/suite mod` ends with "0 failed".

## 8. A landing leaves the team its other bolt

- [x] 8.1 `crew bolt land` says which bolt the team still builds, or that it holds none (design, Decision 9; Task notes 8.1). Verify `tests/suite t-journey-land` ends with "0 failed".

## 9. The briefs and the docs

- [ ] 9.1 The conductor's, ops's and dispatcher's briefs say a team builds one bolt and may hold one more that waits to land, when to give, and `--bolt` for a fix (design, Decision 10; Task notes 9.1). Verify `tests/suite t-briefs` ends with "0 failed".
- [ ] 9.2 README, the crew skill, `crew`'s usage and the `bolt-teams` spec's purpose say the same (design, Decision 10; Task notes 9.2). Verify `tests/suite t-docs` ends with "0 failed".

## 10. Integration

- [ ] 10.1 Everything this change affects passes. Verify `tests/suite --affected` ends with "0 failed".
