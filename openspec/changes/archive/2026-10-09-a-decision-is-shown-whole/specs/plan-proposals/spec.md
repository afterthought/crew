## MODIFIED Requirements

### Requirement: A proposal is read as the user would read it
`crew plan proposed` SHALL list the open proposals from any host, each with its number, who wrote it, when, the first line of its case and what it waits on. `crew plan proposed <n>` SHALL print the case and then each change in plain words: a new unit's intent beside the sources it rests on and the goal of the bolt it would join, a move's bolts with their goals, a new bolt's goal, a drop's reason. Under each change's plain words it SHALL print the command approval will run for that change, so the sequence of adds, moves and drops reads as the plan commands it is. For an open proposal it SHALL then name, in words, each conductor whose agreement it still waits on, the conductors that have agreed, and the user, without the commands that answer it. `--json` SHALL give the same.

#### Scenario: A unit for an existing bolt
- **WHEN** proposal N adds a unit to a bolt a team holds
- **THEN** `crew plan proposed N` shows the unit's intent, the bolt's goal beside it, and that the bolt's conductor has not yet agreed

#### Scenario: Each change shows its command
- **WHEN** proposal N creates a bolt, adds a unit to it and moves a queued unit into it
- **THEN** `crew plan proposed N` prints under each of the three changes, in order, the `crew` command approval will run for it

#### Scenario: Waiting on, in words
- **WHEN** proposal N is open and waits on a conductor and the user
- **THEN** `crew plan proposed N` names both and what each would do, and prints no `crew plan agree`, `crew plan approve` or `crew plan drop` command

#### Scenario: Nothing open
- **WHEN** no proposal is open
- **THEN** `crew plan proposed` says so

## ADDED Requirements

### Requirement: A proposal is put before the user whole
Any agent that puts one of the planner's proposals before the user, the planner, a conductor or the operator agent, SHALL show what `crew plan proposed <n>` prints, in its own pane or opened beside it, and SHALL NOT name the proposal by its number alone; the number SHALL follow the words, as a reference. The agent SHALL ask for the user's answer in words, SHALL NOT recite a command for the user to answer with, and SHALL run the answering command only on the user's word.

#### Scenario: The planner proposes
- **WHEN** the planner has written proposal N
- **THEN** it shows the user what `crew plan proposed N` prints and asks them to approve it or say what to change

#### Scenario: The user asks what waits on them
- **WHEN** the operator agent answers where things stand and proposal N is open
- **THEN** its answer shows what `crew plan proposed N` prints, not only that proposal N is open

#### Scenario: The user says yes
- **WHEN** the user tells the agent showing proposal N to approve it
- **THEN** that agent runs `crew plan approve N`
