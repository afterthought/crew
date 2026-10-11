# Spec Delta

## MODIFIED Requirements

### Requirement: A unit in flight goes back through construct and review
`crew unit run <unit> construct "<words>"` SHALL be accepted at any stage before the unit has merged into its bolt. Run on a unit that is approved, in code or in verify, it SHALL mark the unit amended in the plan before the stage starts, and only the conductor of the team holding the unit's bolt or the user SHALL be accepted to run it. Run on a unit whose intent was amended and whose construct has not run since, it SHALL be accepted from any caller. While a unit is marked amended, `crew unit run <unit> code`, `verify` and `merge` SHALL be refused, saying the unit waits for the user's review.

#### Scenario: The user wants a change to a unit in code
- **WHEN** the conductor runs `crew unit run <unit> construct "<the user's words>"` on a unit in code
- **THEN** the unit is marked amended, a fresh construct agent rewrites the change in the unit's slot and place, and when it commits the unit's stage is `review`

#### Scenario: Code on an amended unit
- **WHEN** `crew unit run <unit> code` runs on a unit that is marked amended
- **THEN** it is refused until the user has approved the unit again

#### Scenario: An amended intent arrives from an approved proposal
- **WHEN** an approved proposal amends the intent of a unit in flight
- **THEN** the approval starts construct again on the unit, and the fresh construct agent is given the new intent, told the change is to be revised to it, and given the case of the proposal the user approved; the conductor is told that construct runs again and to wait for it

#### Scenario: The planner approves on the user's word
- **WHEN** the planner runs `crew plan approve <n>` for a proposal that amends a unit in review
- **THEN** construct starts on the unit, recorded as started by the planner, and is not refused for who asked

#### Scenario: A merged unit
- **WHEN** `crew unit run <unit> construct` runs on a unit that has merged into its bolt
- **THEN** it is refused; a defect is a fix, and a new need is a new unit

## ADDED Requirements

### Requirement: Construct on an amended unit names the card the amendment ended
When construct starts on a unit whose intent was amended, crew SHALL name to the unit's conductor the card of the row the unit held before the amendment, `review/<unit>` or `verify/<unit>`: in the command's output when the conductor started it, and by a notice when anyone else did. When the amendment's construct does not start, the amendment's notice to the conductor SHALL name that card.

#### Scenario: An amendment approved while the unit is in review
- **WHEN** the planner approves a proposal amending a unit whose review card is open, and construct starts
- **THEN** the conductor is told to close its card for `review/<unit>`

#### Scenario: The conductor starts it itself
- **WHEN** a conductor brought back runs `crew unit run <unit> construct` on an amended unit that was in verify before its amendment
- **THEN** the command's output names the card for `verify/<unit>` to close

### Requirement: A conductor brought back is told which units wait amended
When crew starts or brings back a team's conductor with `crew up`, `crew rebuild`, `crew restart` or `crew revive`, its one greeting SHALL name each unit of its bolt whose stage is `amended`, and tell it to run construct on each. `crew resume`, which greets nobody, SHALL send the same words as a notice, and only when such a unit exists. When the plan or the bolt's kit cannot be read, the greeting or notice SHALL say so rather than name no unit.

#### Scenario: Restarted with an amended unit
- **WHEN** swb-1's conductor is restarted while a unit of its bolt reads `amended`
- **THEN** its greeting names that unit and tells it to run construct on it, and it does

#### Scenario: Nothing amended
- **WHEN** swb-1's conductor is resumed and no unit of its bolt reads `amended`
- **THEN** it is sent nothing

#### Scenario: A construct already running
- **WHEN** a unit's amended construct has started and not yet committed, and its conductor is restarted
- **THEN** the greeting does not name the unit, whose stage reads `construct`
