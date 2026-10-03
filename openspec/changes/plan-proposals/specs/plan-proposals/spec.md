# Spec Delta

## Purpose

Makes every change the planner would make to a flywheel's plan a proposal the user reads and approves before it takes effect, with the agreement of any conductor whose bolt it touches, so that where work goes is the user's decision and what was approved is exactly what is applied.

## ADDED Requirements

### Requirement: The planner changes the plan only by a proposal
A command that would write the plan, run by a partition's planner, SHALL be refused with a message naming `crew plan propose`. The planner SHALL change the plan only by writing a proposal, which changes nothing until it is approved.

#### Scenario: The planner adds a unit directly
- **WHEN** `wldn-planner` runs `crew unit add <unit> "<intent>" --repo switchboard-kit`
- **THEN** it is refused, the plan is unchanged, and the message names `crew plan propose`

#### Scenario: The planner creates a bolt directly
- **WHEN** `wldn-planner` runs `crew bolt new <bolt> "<goal>" --repo switchboard-kit`
- **THEN** it is refused in the same way

### Requirement: Other agents write the plan only within their own job
A conductor SHALL write directly only `crew unit split`, `crew unit order` and `crew unit after`, and only on units of the bolt its team holds. The design agent SHALL write directly only `crew unit add` into a kit's queue. A dispatcher's `crew bolt give` and the main-level ops' `crew bolt land` SHALL stay direct. Any other plan write by an agent crew started SHALL be refused, naming the planner. The user at a shell SHALL write the plan directly.

#### Scenario: A conductor narrows a unit of its bolt
- **WHEN** swb-2's conductor runs `crew unit split` on a unit of the bolt swb-2 holds
- **THEN** the split is written, with no proposal

#### Scenario: A conductor adds a unit to its bolt
- **WHEN** swb-2's conductor runs `crew unit add <unit> "<intent>" --bolt <its bolt>`
- **THEN** it is refused, and the message says to tell the planner

#### Scenario: The design agent queues a unit
- **WHEN** the design agent runs `crew unit add <unit> "<intent>" --repo <kit>`
- **THEN** the unit is queued, with no proposal

#### Scenario: The user at a shell
- **WHEN** the user runs `crew bolt new` in a terminal
- **THEN** the bolt is written, with no proposal

### Requirement: A proposal is a case and the commands it would run
`crew plan propose <file>` SHALL write one Proposal record to `proposals.rec` on the flywheel's branch: its number, the planner's case, the plan commands it would run in order, who wrote it and when, and its state, `open`. The commands SHALL be among `bolt new`, `bolt order`, `bolt drop`, `unit add`, `unit move`, `unit split`, `unit order`, `unit after` and `unit drop`. A number SHALL be given once and never reused, and a proposal SHALL never be removed or its commands changed.

#### Scenario: A new bolt with two units
- **WHEN** the planner proposes `bolt new cfn-checks …`, `unit add cfn-nag-security-check … --bolt cfn-checks` and `unit move retire-suite-cfn-lint cfn-checks`, with its case
- **THEN** proposal N holds the case and those three commands in that order, in state `open`, and the plan is unchanged

#### Scenario: A command a proposal cannot hold
- **WHEN** a proposal file holds `bolt give swb-1`
- **THEN** the proposal is refused, naming the command, and nothing is written

#### Scenario: Someone other than the planner
- **WHEN** a conductor runs `crew plan propose`
- **THEN** it is refused; only the partition's planner and the user write proposals

### Requirement: A proposal is checked when it is written
Before a proposal is written, each of its commands SHALL be applied in order to a copy of the plan at the branch's tip, and SHALL pass every refusal and rule that command has when run directly. A proposal with a command that would be refused SHALL be refused, naming the command and the reason, and nothing SHALL be written.

#### Scenario: A later command depends on an earlier one
- **WHEN** a proposal creates a bolt and then adds a unit to that bolt
- **THEN** it passes, because the unit is checked against the plan as the first command leaves it

#### Scenario: A unit name the kit already has
- **WHEN** a proposal adds a unit whose name the kit's main already has as a change
- **THEN** the proposal is refused, naming that command and the name

#### Scenario: Moving merged work
- **WHEN** a proposal moves a unit that has merged into its bolt
- **THEN** the proposal is refused, as the move would be

### Requirement: A proposal is read as the user would read it
`crew plan proposed` SHALL list the open proposals from any host, each with its number, who wrote it, when, the first line of its case and what it waits on. `crew plan proposed <n>` SHALL print the case and then each change in plain words: a new unit's intent beside the sources it rests on and the goal of the bolt it would join, a move's bolts with their goals, a new bolt's goal, a drop's reason, and which conductors have agreed. `--json` SHALL give the same.

#### Scenario: A unit for an existing bolt
- **WHEN** proposal N adds a unit to a bolt a team holds
- **THEN** `crew plan proposed N` shows the unit's intent, the bolt's goal beside it, and that the bolt's conductor has not yet agreed

#### Scenario: Nothing open
- **WHEN** no proposal is open
- **THEN** `crew plan proposed` says so

### Requirement: A bolt in flight is changed only with its conductor's agreement
When a proposal is written, crew SHALL tell the conductor of each bolt a team holds that the proposal touches, with the commands that touch it. `crew plan agree <n>`, run by that conductor, SHALL record the team's agreement on the proposal. Approval SHALL be refused while any touched bolt held by a team has no recorded agreement, naming the conductor.

#### Scenario: The conductor agrees
- **WHEN** swb-2's conductor runs `crew plan agree 4` for a proposal that adds a unit to its bolt
- **THEN** the proposal records swb-2's agreement, and the planner is told

#### Scenario: Approval before agreement
- **WHEN** `crew plan approve 4` runs while swb-2 has not agreed
- **THEN** it is refused, naming `swb-2-conductor`, and nothing changes

#### Scenario: A conductor whose bolt is not touched
- **WHEN** swb-1's conductor runs `crew plan agree 4` and the proposal touches no bolt swb-1 holds
- **THEN** it is refused

#### Scenario: A bolt given after the proposal was written
- **WHEN** a planned bolt the proposal touches is given to a team before approval
- **THEN** approval is refused until that team's conductor has agreed

### Requirement: Approval applies a proposal exactly as it was read
`crew plan approve <n>` SHALL apply the proposal's commands in order to the plan at the branch's tip and close the proposal as `approved`, in one commit. When any command would now be refused, the approval SHALL be refused, naming the command and the reason, and the plan and the proposal SHALL be unchanged. What follows a direct command (a rebased unit, a freed slot, a conductor told) SHALL follow the approval.

#### Scenario: A proposal is approved
- **WHEN** the user approves proposal N, which creates a bolt and adds a unit to it
- **THEN** one commit adds the bolt and the unit and marks the proposal approved, and no reader sees the bolt without the unit

#### Scenario: The plan moved since
- **WHEN** a unit the proposal moves was dropped after the proposal was written
- **THEN** the approval is refused, naming that command, and the proposal stays open

#### Scenario: A unit with a worktree is moved
- **WHEN** an approved proposal moves a unit in construct to another bolt in the same checkout and the rebase conflicts
- **THEN** the rebase is undone, the approval is refused, and the plan and the proposal are unchanged

#### Scenario: A unit from a signal
- **WHEN** an approved proposal holds `unit add … --signal <id>`
- **THEN** the same commit adds the unit and the signal's `route` move

### Requirement: Only the user approves
`crew plan approve` SHALL be run by the user, or by an agent on the user's word in that agent's pane. An agent SHALL NOT approve a proposal on its own judgment. The run record SHALL show who ran the approval and in which session.

#### Scenario: The user says yes to the planner
- **WHEN** the user reads proposal N in the planner's pane and says to go ahead
- **THEN** the planner runs `crew plan approve N`, and the entry names the planner and its session, where the user's words are

#### Scenario: Nobody has said yes
- **WHEN** a proposal is open and the user has said nothing about it
- **THEN** no agent approves it, and it is listed as waiting on the user

### Requirement: A proposal is dropped with a reason, or replaced
`crew plan drop <n> "<reason>"` SHALL close an open proposal as `dropped` with the reason, applying nothing, and SHALL tell the planner when someone else dropped it. `crew plan propose <file> --replaces <n>` SHALL drop proposal n and write its successor in one commit, the successor naming the one it replaces.

#### Scenario: The user rejects a proposal
- **WHEN** the user drops proposal N with a reason
- **THEN** the proposal is `dropped`, the plan is unchanged, and the planner is told the reason

#### Scenario: The planner revises
- **WHEN** the planner proposes again with `--replaces N` after the user asked for a different placement
- **THEN** proposal N is `dropped`, proposal N+1 is `open` and names N, and agreements given to N do not carry over

### Requirement: Each step of a proposal is in the run record
Writing, agreeing, approving and dropping a proposal SHALL each leave a run-record entry naming `proposal/<n>` and the bolts and units its commands name. Each change an approval applies SHALL leave its own entry, with the proposal as what it came from and the approval's commit.

#### Scenario: Tracing a unit
- **WHEN** `crew trace unit/<unit>` runs for a unit an approved proposal added
- **THEN** it shows the proposal written, any agreement, the approval, and the unit's add, in order
