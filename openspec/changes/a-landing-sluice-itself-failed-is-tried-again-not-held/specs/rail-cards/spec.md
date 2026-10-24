## MODIFIED Requirements

### Requirement: A refused landing is held on its row
A bolt whose landing sluice refused for its own content, its submission in conflict or blamed for a check that ran and failed, SHALL be held on its row at that head, with no box, the row saying sluice's words and that it waits for its team's fix, while the bolts after it go on. It SHALL have a box again once its head moves and it reads proven. A landing that did not land for any other cause SHALL NOT hold its row.

#### Scenario: The second of three is refused
- **WHEN** the user sends `land/crew` with `y`, `z` and `w` ticked, and sluice refuses `z` for a conflict on `plugin/lib/plan.py`
- **THEN** `y` and `w` land, `z` stays on crew's landing row held, saying sluice's words and that it waits for its team's fix, and the next landings card raised carries `z` held with no box

#### Scenario: A check fails
- **WHEN** sluice blames `z`'s landing for `tests:logic`, which ran and failed
- **THEN** `z` is held on its row with no box, saying sluice's words and that it waits for its team's fix

#### Scenario: The fix merges
- **WHEN** `z`'s team's take-main fix merges into `z` and `z` reads proven at its new head
- **THEN** `z` has a box on `land/crew` again

## ADDED Requirements

### Requirement: A landing sluice or its host stopped keeps its box
A bolt whose landing did not land for a cause that is not its own content (sluice itself failing, a refusal or answer with no conflict or failed check in sluice's record, checks the host could not run, a withdrawal, or an outcome crew can't tell) SHALL keep its box and the user's word it has. Its row SHALL say what stopped the landing at that head, that it was nothing of the bolt's, and that main-level ops submits it again once that is cleared.

#### Scenario: Checks that never ran
- **WHEN** the user sent `land/crew` with `z` ticked, and sluice's record has `z`'s submission failed with every required check left without a result, the host unable to run them
- **THEN** `z` is not held: `land/crew` is left as the user answered it, `crew card read land/crew` names `z` as still landing on their send, saying what stopped it, with the command that lands it, and no new card asks for `z`

#### Scenario: sluice itself fails
- **WHEN** `crew bolt submit z` ends with sluice exiting 3 and main not holding `z`, and sluice's record of the submission has it neither in conflict nor blamed for a check that ran
- **THEN** `z` keeps its box at that head, and its row says sluice itself failed, in sluice's words, and that ops submits it again once that is cleared

#### Scenario: A new card while it is stopped
- **WHEN** `z`'s landing was stopped and a card of crew's landings follows the one the user answered
- **THEN** the closed card's outcome names `z` as still landing on their send with what stopped it, and the card that follows does not ask for `z` again

#### Scenario: The head moves
- **WHEN** `z`'s landing was stopped at `abc1234` and `z`'s head moves to a new head that reads proven
- **THEN** `z`'s row says nothing of the stop
