# Spec Delta

## ADDED Requirements

### Requirement: A unit in flight goes back through construct and review
`crew unit run <unit> construct "<words>"` SHALL be accepted at any stage before the unit has merged into its bolt. Run on a unit that is approved, in code or in verify, it SHALL mark the unit amended in the plan before the stage starts. While a unit is marked amended, `crew unit run <unit> code`, `verify` and `merge` SHALL be refused, saying the unit waits for the user's review.

#### Scenario: The user wants a change to a unit in code
- **WHEN** the conductor runs `crew unit run <unit> construct "<the user's words>"` on a unit in code
- **THEN** the unit is marked amended, a fresh construct agent rewrites the change in the unit's slot and place, and when it commits the unit's stage is `review`

#### Scenario: Code on an amended unit
- **WHEN** `crew unit run <unit> code` runs on a unit that is marked amended
- **THEN** it is refused until the user has approved the unit again

#### Scenario: An amended intent arrives from an approved proposal
- **WHEN** an approved proposal amends the intent of a unit in flight
- **THEN** the conductor is told, runs construct again, and the fresh construct agent is given the new intent and told the change is to be revised to it

#### Scenario: A merged unit
- **WHEN** `crew unit run <unit> construct` runs on a unit that has merged into its bolt
- **THEN** it is refused; a defect is a fix, and a new need is a new unit
