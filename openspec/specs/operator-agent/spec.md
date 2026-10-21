# operator-agent Specification

## Purpose
A standing agent in each operator session that works for the user. It says where the partition's work stands, opens what is running, and carries requests to the agent whose job they are.

## Requirements

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

### Requirement: The operator agent answers what happened from the run record
When the user asks what happened to a bolt, a unit or a signal, the operator agent SHALL answer from `crew trace`, and SHALL NOT read transcripts or git logs to piece it together.

#### Scenario: What became of a finding
- **WHEN** the user asks what became of a signal a conductor recorded
- **THEN** the operator agent runs `crew trace signals/<id>` and answers in a few plain sentences from what it prints

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

### Requirement: The operator agent opens the lineage page
On request, the operator agent SHALL make the partition's lineage page with `crew page <label>` and open it in terminal-browser beside its pane. It SHALL say when the page was made and name any host the page could not read.

#### Scenario: Show me the flow
- **WHEN** the user asks the operator agent on mac-studio to show how the week's findings flowed
- **THEN** it runs `crew page wldn`, opens the file beside its pane, and says as of when it is

### Requirement: The operator is a main-level role
The partition's operator, `<label>-operator`, SHALL be a standing role of its main level: `crew main up <label>` SHALL start it in an `operator` tab of the `<label>` workspace, beside the design agent, the planner and ops, and greet it once it is up as it greets them; `crew main down <label>` SHALL end it; `crew revive` SHALL bring it back as it brings them back. Every brief SHALL name it as the partition's operator, and crew SHALL start no other operator agent for the partition.

#### Scenario: The main level comes up with its operator
- **WHEN** `crew main up wldn` runs
- **THEN** `wldn-operator` starts in the `wldn` workspace's `operator` tab and is greeted once, beside `wldn-design`, `wldn-planner` and `wldn-ops`

#### Scenario: A conductor waits on the user with no card
- **WHEN** a conductor of wldn stops on a question asked only in its pane
- **THEN** its brief has it tell `wldn-operator`, the partition's one operator

### Requirement: The console follows the run record
`crew console up <label>` SHALL open a `flow` tab in the `console` workspace of the host's `<label>` session that runs `crew events --follow` for the partition, and SHALL start no agent. When the tab is already there it SHALL do nothing. `crew console down <label>` SHALL close the console's tabs.

#### Scenario: The tab is opened with no agent
- **WHEN** `crew console up wldn` runs on mac-studio
- **THEN** the `console` workspace of mac-studio's `wldn` session has a `flow` tab printing wldn's entries as they are written, and no agent is started or greeted

#### Scenario: Run twice
- **WHEN** `crew console up wldn` runs again
- **THEN** no second `flow` tab is opened

### Requirement: The console has a rail tab
`crew console up <label>` SHALL also open a `rail` tab in the `console` workspace, split in two. The upper pane SHALL show `crew rail --label <label>`, printed again every 30 seconds and whenever the partition's run record gains an entry. The lower pane SHALL be a shell with crew on its path. When the tab is already there, it SHALL open nothing.

#### Scenario: The tab is opened
- **WHEN** `crew console up wldn` runs
- **THEN** the `console` workspace has a `rail` tab with wldn's rail above and a shell below in which `crew` runs

#### Scenario: A new entry refreshes the list
- **WHEN** the user approves a unit from the shell below
- **THEN** the list above is printed again within a few seconds, without that unit's review row

#### Scenario: Run twice
- **WHEN** `crew console up wldn` runs again
- **THEN** no second `rail` tab is opened

### Requirement: The console has a board tab
`crew console up <label>` SHALL also open a `board` tab in the `console` workspace, after the `rail` tab, showing the partition's board, drawn again each time the rail tab refreshes. When the tab is already there, it SHALL open nothing.

#### Scenario: The tab is opened
- **WHEN** `crew console up wldn` runs
- **THEN** the `console` workspace has a `board` tab after `rail`, showing wldn's board

#### Scenario: Run twice
- **WHEN** `crew console up wldn` runs again
- **THEN** no second `board` tab is opened

#### Scenario: A new entry redraws it
- **WHEN** the user approves a unit from the rail tab's shell
- **THEN** the board tab is drawn again within a few seconds, with that unit's marker gone

### Requirement: The console's old name opens it and retires the host's operator agent
`crew operator up <label>` SHALL open the console as `crew console up <label>` does, saying it is `crew console up` now. The console's up SHALL end the operator agent the host's operator session held before the operator was a main-level role, `<label>-operator-<host>`, and close the panes crew recorded in its `operator` workspace, once that agent is not working; one working SHALL be left and said.

#### Scenario: The host's timer still runs the old name
- **WHEN** swancloud's timer runs `crew operator up wldn` on mac-studio
- **THEN** the console opens, the command says `crew operator up` is `crew console up` now, and no agent is started
