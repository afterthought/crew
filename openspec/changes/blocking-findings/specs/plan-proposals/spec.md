# Spec Delta

## MODIFIED Requirements

### Requirement: A proposal is a case and the commands it would run
`crew plan propose <file>` SHALL write one Proposal record to `proposals.rec` on the flywheel's branch: its number, the planner's case, the plan commands it would run in order, who wrote it and when, and its state, `open`. The commands SHALL be among `bolt new`, `bolt order`, `bolt drop`, `unit add`, `unit amend`, `unit move`, `unit split`, `unit order`, `unit after`, `unit release` and `unit drop`. A number SHALL be given once and never reused, and a proposal SHALL never be removed or its commands changed.

#### Scenario: A new bolt with two units
- **WHEN** the planner proposes `bolt new cfn-checks …`, `unit add cfn-nag-security-check … --bolt cfn-checks` and `unit move retire-suite-cfn-lint cfn-checks`, with its case
- **THEN** proposal N holds the case and those three commands in that order, in state `open`, and the plan is unchanged

#### Scenario: A command a proposal cannot hold
- **WHEN** a proposal file holds `bolt give swb-1`
- **THEN** the proposal is refused, naming the command, and nothing is written

#### Scenario: Someone other than the planner
- **WHEN** a conductor runs `crew plan propose`
- **THEN** it is refused; only the partition's planner and the user write proposals

#### Scenario: An amendment to a unit in flight
- **WHEN** the planner proposes `unit amend <unit> "<new intent>"` for a unit in code in a bolt a team holds
- **THEN** the proposal is written, the unit's intent is unchanged, and that bolt's conductor is told

#### Scenario: A unit that came of a blocking finding
- **WHEN** the planner proposes `unit add <unit> "<intent>" --item <n> --bolt <bolt>` for an item that holds a unit of that bolt
- **THEN** the proposal is written, and its page says the held unit will come after the new one
