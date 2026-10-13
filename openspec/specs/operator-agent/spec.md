# operator-agent Specification

## Purpose
A standing agent in each operator session that works for the user. It says where the partition's work stands, opens what is running, and carries requests to the agent whose job they are.

## Requirements

### Requirement: The operator agent starts with its operator session
`crew operator up <label>` SHALL start the operator agent, `<label>-operator-<host>`, in a herdr workspace named `operator` in the session named `<label>` on the host it runs on, and greet it once it is up, as the `main-level` spec greets every agent crew starts outside a team: told, in a message marked as crew's, to read where the partition stands and carry on with what is its role's. When the agent is already up, it SHALL do nothing, greet nobody, and succeed. When the session or the partition is unknown, it SHALL exit non-zero, naming what is missing.

#### Scenario: Started by the host
- **WHEN** the `madswan` operator session starts on mac-studio and its supervisor runs `crew operator up madswan`
- **THEN** `madswan-operator-mac-studio` is running in the `operator` workspace of that session, and is greeted once

#### Scenario: Run twice
- **WHEN** `crew operator up wldn` runs while the agent is up
- **THEN** nothing is started, nobody is greeted, and the command succeeds

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

### Requirement: The operator agent opens what is running
On request, the operator agent SHALL list the running dev servers with `crew sites` and open the one the user picks in terminal-browser beside its pane. When the server cannot be opened from the host the agent runs on, it SHALL say so and give the URL to open from a Mac.

#### Scenario: On a Mac
- **WHEN** the user asks the operator agent on mac-studio to show a unit running on the box
- **THEN** terminal-browser opens the unit's `dev.swancloud.net` name beside the agent's pane

#### Scenario: On the box
- **WHEN** the user asks the operator agent on the box to show the same unit
- **THEN** it says the box cannot open dev names and gives the URL to open from a Mac

### Requirement: The operator workspace follows the run record
`crew operator up <label>` SHALL also open a `flow` tab in the `operator` workspace that runs `crew events --follow` for the partition. When the tab is already there it SHALL do nothing.

#### Scenario: The tab is opened with the agent
- **WHEN** `crew operator up wldn` starts the operator agent
- **THEN** the `operator` workspace has a `flow` tab printing wldn's entries as they are written

#### Scenario: Run twice
- **WHEN** `crew operator up wldn` runs again
- **THEN** no second `flow` tab is opened

### Requirement: The operator agent answers what happened from the run record
When the user asks what happened to a bolt, a unit or a signal, the operator agent SHALL answer from `crew trace`, and SHALL NOT read transcripts or git logs to piece it together.

#### Scenario: What became of a finding
- **WHEN** the user asks what became of a signal a conductor recorded
- **THEN** the operator agent runs `crew trace signals/<id>` and answers in a few plain sentences from what it prints

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

### Requirement: The operator agent posts no card
The operator agent SHALL post no Pending You card, whatever a Pending You reminder in its session says.

#### Scenario: Told of a landing
- **WHEN** a conductor tells the operator agent it waits on the user to land bolt `y`
- **THEN** the operator agent posts no card for it

### Requirement: The operator agent shows only a wait with no card
When told of a wait for a unit in review or a landing, the operator agent SHALL read that row on the rail and send nothing when its card is open. A wait with no card, a question asked in a pane or a row whose card is not open, SHALL be shown as a herdr notification in the operator session, with one line to the user on what it needs and where.

#### Scenario: A landing whose card is open
- **WHEN** a conductor tells the operator agent it waits on the user to land bolt `y`, and the rail shows the landing row's card open
- **THEN** the operator agent posts no card and shows no notification for it

#### Scenario: A question in a pane
- **WHEN** a conductor tells the operator agent it waits on the user for a question asked only in its pane
- **THEN** the operator agent shows a herdr notification naming the conductor and what it waits for, tells the user in one line, and posts no card

#### Scenario: A row with no card open
- **WHEN** a conductor whose session has lost Pending You's tools tells the operator agent that unit `u` waits in review, and the rail shows no card open for its row
- **THEN** the operator agent shows a herdr notification for it, and posts no card
