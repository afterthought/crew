# Spec Delta

## MODIFIED Requirements

### Requirement: A proposal is a case and the commands it would run
`crew plan propose <file>` SHALL write one Proposal record to `proposals.rec` on the flywheel's branch: its number, the planner's case, the plan commands it would run in order, who wrote it and when, and its state, `open`. The commands SHALL be among `bolt new`, `bolt order`, `bolt drop`, `unit add`, `unit amend`, `unit move`, `unit split`, `unit order`, `unit after`, `unit drop`, `chore add`, `chore move`, `chore order`, `chore after` and `chore drop`. A number SHALL be given once and never reused, and a proposal SHALL never be removed or its commands changed.

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

#### Scenario: A chore's words changed
- **WHEN** the planner proposes `chore drop bump-biome "…"` then `chore add bump-biome "<new words>" --bolt tooling`
- **THEN** the proposal is written; a chore has no amendment, so its words change by a drop and an add

### Requirement: Other agents write the plan only within their own job
A conductor SHALL write directly only `crew unit split`, `crew unit order`, `crew unit after`, `crew chore order` and `crew chore after`, and only on units and chores of the bolt its team holds. The design agent SHALL write directly only `crew unit add` and `crew chore add` into a kit's queue. A dispatcher's `crew bolt give` and the main-level ops' `crew bolt land` SHALL stay direct. Any other plan write by an agent crew started SHALL be refused, naming the planner. The user at a shell SHALL write the plan directly.

#### Scenario: A conductor narrows a unit of its bolt
- **WHEN** swb-2's conductor runs `crew unit split` on a unit of the bolt swb-2 holds
- **THEN** the split is written, with no proposal

#### Scenario: A conductor adds a unit to its bolt
- **WHEN** swb-2's conductor runs `crew unit add <unit> "<intent>" --bolt <its bolt>`
- **THEN** it is refused, and the message says to tell the planner

#### Scenario: A conductor adds a chore to its bolt
- **WHEN** swb-2's conductor runs `crew chore add <chore> "<words>" --bolt <its bolt>`
- **THEN** it is refused, and the message says to tell the planner

#### Scenario: The design agent queues a unit
- **WHEN** the design agent runs `crew unit add <unit> "<intent>" --repo <kit>`
- **THEN** the unit is queued, with no proposal

#### Scenario: The user at a shell
- **WHEN** the user runs `crew bolt new` in a terminal
- **THEN** the bolt is written, with no proposal
