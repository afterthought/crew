# Spec Delta

## ADDED Requirements

### Requirement: An amendment is read as before and after
For a `unit amend` command, `crew plan proposed <n>` SHALL show the unit's intent as it stands and as it would be, the unit's bolt, team and stage, and what approval sets in motion: for a unit with a worktree, that its conductor runs construct again and the unit returns to the user's review.

#### Scenario: An amendment to a unit in code
- **WHEN** proposal N amends the intent of a unit in code in the bolt swb-2 holds
- **THEN** its page shows both intents, that the unit is in code under swb-2, that swb-2's conductor has or has not agreed, and that on approval the unit goes back to construct and review

## MODIFIED Requirements

### Requirement: A proposal is a case and the commands it would run
`crew plan propose <file>` SHALL write one Proposal record to `proposals.rec` on the flywheel's branch: its number, the planner's case, the plan commands it would run in order, who wrote it and when, and its state, `open`. The commands SHALL be among `bolt new`, `bolt order`, `bolt drop`, `unit add`, `unit amend`, `unit move`, `unit split`, `unit order`, `unit after` and `unit drop`. A number SHALL be given once and never reused, and a proposal SHALL never be removed or its commands changed.

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
