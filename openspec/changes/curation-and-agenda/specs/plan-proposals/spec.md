# Spec Delta

## ADDED Requirements

### Requirement: A proposal shows the item a unit rests on
For a `unit add` that names an agenda item, `crew plan proposed <n>` SHALL show, beside the unit's intent, the item's subject and each of its signals: who asserted it, its assertion, and its excerpt with the excerpt's grade.

#### Scenario: A unit from a plan item
- **WHEN** proposal N adds a unit from plan item 8, which rests on a conductor's capture of the user's words
- **THEN** its page shows the planner's intent with the user's words beneath it, marked `verified`

### Requirement: An approved unit closes the plan item it came from
When an approval applies a `unit add … --item <n>` for a plan-lane item, the same commit SHALL close the item as `planned`, with the unit as its result. Several units MAY come from one item, each a result. A proposal that is dropped SHALL leave its items open.

#### Scenario: A plan item is planned
- **WHEN** the user approves a proposal that adds a unit from plan item 8
- **THEN** one commit holds the unit, the closed proposal and item 8 as `planned` with `unit/<unit>` as its result

#### Scenario: A dropped proposal
- **WHEN** the user drops that proposal
- **THEN** item 8 is still open in the plan lane
