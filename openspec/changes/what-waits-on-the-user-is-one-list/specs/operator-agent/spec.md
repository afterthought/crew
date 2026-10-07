# Spec Delta

## MODIFIED Requirements

### Requirement: The operator agent works for the user
The operator agent SHALL answer where the partition's work stands from `crew bolts`, `crew status` and `crew sites`, and what waits on the user from `crew rail`. It SHALL carry a request to the agent whose job it is, in the user's words:

- what to build and in what order: the planner;
- a design question: the design agent;
- which host runs what: that host's dispatcher;
- a bolt's progress: its conductor.

It SHALL NOT write the plan, a kit or a design itself.

#### Scenario: Where things stand
- **WHEN** the user asks the operator agent what is in flight
- **THEN** it answers in a few plain sentences from `crew bolts` and names anything waiting on the user, such as units in review

#### Scenario: What waits on the user
- **WHEN** the user asks the operator agent what waits on them
- **THEN** it answers from what `crew rail --label <label>` prints, oldest first in each group, and points the user to the `rail` tab for the commands

#### Scenario: A request for new work
- **WHEN** the user asks for a feature
- **THEN** the operator agent passes it to the planner in the user's words, and tells the user which pane to carry on in

## ADDED Requirements

### Requirement: The operator workspace has a rail tab
`crew operator up <label>` SHALL also open a `rail` tab in the `operator` workspace, split in two. The upper pane SHALL show `crew rail --label <label>`, printed again every 30 seconds and whenever the partition's run record gains an entry. The lower pane SHALL be a shell with crew on its path. When the tab is already there, it SHALL open nothing.

#### Scenario: The tab is opened with the agent
- **WHEN** `crew operator up wldn` starts the operator agent
- **THEN** the `operator` workspace has a `rail` tab with wldn's rail above and a shell below in which `crew` runs

#### Scenario: A new entry refreshes the list
- **WHEN** the user approves a unit from the shell below
- **THEN** the list above is printed again within a few seconds, without that unit's review row

#### Scenario: Run twice
- **WHEN** `crew operator up wldn` runs again
- **THEN** no second `rail` tab is opened
