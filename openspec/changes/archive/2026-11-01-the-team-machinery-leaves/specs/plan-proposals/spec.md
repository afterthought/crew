## ADDED Requirements

### Requirement: Other agents write the plan only within their own job, and no conductor or dispatcher is among them
The design agent SHALL write directly only `crew unit add` and `crew chore add` into a kit's queue. The main-level ops' `crew bolt land` SHALL stay direct. Any other plan write by an agent crew started SHALL be refused, naming the planner. The user at a shell SHALL write the plan directly.

#### Scenario: An agent narrows a unit of a bolt
- **WHEN** an agent crew started, other than the planner, runs `crew unit split` on a unit of a bolt in flight
- **THEN** it is refused, naming the planner, and the plan is unchanged

#### Scenario: An agent adds a unit to a bolt
- **WHEN** main-level ops runs `crew unit add <unit> "<intent>" --bolt <a bolt>`
- **THEN** it is refused, and the message says to tell the planner

#### Scenario: An agent adds a chore to a bolt
- **WHEN** main-level ops runs `crew chore add <chore> "<words>" --bolt <a bolt>`
- **THEN** it is refused, and the message says to tell the planner

#### Scenario: The design agent queues a unit
- **WHEN** the design agent runs `crew unit add <unit> "<intent>" --repo <kit>`
- **THEN** the unit is queued, with no proposal

#### Scenario: The user at a shell
- **WHEN** the user runs `crew bolt new` in a terminal
- **THEN** the bolt is written, with no proposal

### Requirement: Work a bolt in flight needs goes into that bolt
Landing SHALL be part of every bolt's goal. A unit that a bolt in flight needs before it can be proven or land SHALL be proposed into that bolt, ordered ahead of the units that wait on it, and marked with the bolt it unblocks (`--unblocks <bolt>` on the `crew unit add` or `crew unit move` the proposal runs). crew SHALL refuse a proposal that marks a unit as unblocking a bolt in flight but places it in the queue or in another bolt. `crew plan proposed <n>` SHALL show the mark beside the unit. The planner's brief SHALL say this, and SHALL say to fold into a bolt in flight the units a planned bolt holds that only serve it.

#### Scenario: A bolt can't land without new work
- **WHEN** a stage stops short telling the planner its bolt can't land until two pins agree
- **THEN** the planner's proposal adds the unit to that bolt, ahead of the units waiting on it, marked as unblocking that bolt, and the user reads the mark on the proposal

#### Scenario: Unblocking work placed elsewhere
- **WHEN** a proposal marks a unit `--unblocks biome-follows-the-shell` but adds it to the queue or to a new bolt
- **THEN** writing the proposal is refused, naming the bolt in flight

#### Scenario: The planner's brief on unblocking work
- **WHEN** the planner's brief is printed
- **THEN** it says to propose work a bolt in flight needs into that bolt, marked `--unblocks`, and to fold into it the units of a planned bolt that only serve it

### Requirement: A proposal is read as the user would read it, waiting on the user alone
`crew plan proposed` SHALL list the open proposals from any host, each with its number, who wrote it, when, the first line of its case and what it waits on. `crew plan proposed <n>` SHALL print the case and then each change in plain words: a new unit's intent beside the sources it rests on and the goal of the bolt it would join, a move's bolts with their goals, a new bolt's goal, a drop's reason. Under each change's plain words it SHALL print the command approval will run for that change, so the sequence of adds, moves and drops reads as the plan commands it is. For an open proposal it SHALL then name, in words, that it waits on the user, without the commands that answer it. `--json` SHALL give the same.

#### Scenario: A unit for an existing bolt
- **WHEN** proposal N adds a unit to a bolt in flight
- **THEN** `crew plan proposed N` shows the unit's intent and the bolt's goal beside it, and names no agreement it waits on

#### Scenario: Each change shows its command
- **WHEN** proposal N creates a bolt, adds a unit to it and moves a queued unit into it
- **THEN** `crew plan proposed N` prints under each of the three changes, in order, the `crew` command approval will run for it

#### Scenario: Waiting on, in words
- **WHEN** proposal N is open
- **THEN** `crew plan proposed N` names the user and what they would do, and prints no `crew plan approve` or `crew plan drop` command

#### Scenario: Nothing open
- **WHEN** no proposal is open
- **THEN** `crew plan proposed` says so

## MODIFIED Requirements

### Requirement: Approval applies a proposal exactly as it was read
`crew plan approve <n>` SHALL apply the proposal's commands in order to the plan at the branch's tip and close the proposal as `approved`, in one commit. When any command would now be refused, the approval SHALL be refused, naming the command and the reason, and the plan and the proposal SHALL be unchanged. What follows a direct command SHALL follow the approval. `crew plan approve <n> --clear <unit>...` SHALL apply the commands the user kept: each cleared unit SHALL be one the proposal adds or moves into a bolt, every command that names only cleared units SHALL be left out, and when a command left in names a cleared unit the approval SHALL be refused, naming that command and the unit, with nothing changed. The approved proposal SHALL record each cleared unit.

#### Scenario: A proposal is approved
- **WHEN** the user approves proposal N, which creates a bolt and adds a unit to it
- **THEN** one commit adds the bolt and the unit and marks the proposal approved, and no reader sees the bolt without the unit

#### Scenario: The plan moved since
- **WHEN** a unit the proposal moves was dropped after the proposal was written
- **THEN** the approval is refused, naming that command, and the proposal stays open

#### Scenario: A unit with a worktree is moved
- **WHEN** an approved proposal moves unit `a`, launched as a Flume place on started `x`, to bolt `y`
- **THEN** the approval is refused, naming `a`'s place and that it is dropped and added again as the way on, crew rebases nothing, and the plan and the proposal are unchanged

#### Scenario: A unit from a signal
- **WHEN** an approved proposal holds `unit add … --signal <id>`
- **THEN** the same commit adds the unit and the signal's `route` move

#### Scenario: A new unit left out
- **WHEN** proposal N drops `a`, adds `b` and `c` to bolt `y`, and orders `c` first, and the user approves it with `c` cleared
- **THEN** one commit drops `a`, adds `b`, makes no unit `c`, runs no order of `c`, marks the proposal approved and records `c` as cleared

#### Scenario: A unit moved in from the queue left out
- **WHEN** proposal N moves queued unit `q` into bolt `y` and the user clears `q`
- **THEN** the approval applies the rest, and `q` stays in the queue as it was

#### Scenario: A kept command names a cleared unit
- **WHEN** proposal N adds `b` and `c` to bolt `y`, `c` with `--after b`, and the user clears `b` and keeps `c`
- **THEN** the approval is refused, naming the `unit add c` command and `b`, the plan and the proposal are unchanged, and the planner writes the proposal again without `b`

#### Scenario: A unit that is not new is cleared
- **WHEN** `crew plan approve N --clear a` names a unit proposal N only amends
- **THEN** the approval is refused, naming `a` and the units the proposal adds or moves in, and nothing changes

## REMOVED Requirements

### Requirement: A bolt in flight is changed only with its conductor's agreement
**Reason**: Record 0047 move 5: no conductor stands to agree; the user's approval is the one word on a proposal (`roles.2`), and `plan.4`'s agreement clause retires.
**Migration**: None: `crew plan agree` is gone, and an open proposal waits on the user alone.

### Requirement: Other agents write the plan only within their own job
**Reason**: Record 0047 move 5: the conductor's direct writes within its bolt and the dispatcher's give leave (`roles.1`).
**Migration**: "Other agents write the plan only within their own job, and no conductor or dispatcher is among them", added by this change.

### Requirement: Work a bolt in flight needs to land goes into that bolt
**Reason**: Record 0047 move 5: no team holds a bolt and no dispatcher gives one; a bolt in flight is one whose work has started.
**Migration**: "Work a bolt in flight needs goes into that bolt", added by this change.

### Requirement: A proposal is read as the user would read it
**Reason**: Record 0047 move 5: no conductor's agreement is waited on, so no proposal names one.
**Migration**: "A proposal is read as the user would read it, waiting on the user alone", added by this change.
