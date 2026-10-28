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
`crew console up <label> flow` SHALL open a `flow` tab in the `console` workspace of the host's `<label>` session that runs `crew events --follow` for the partition, and SHALL start no agent. When the tab is already there it SHALL do nothing. `crew console down <label>` SHALL close the console's tabs.

#### Scenario: The tab is opened with no agent
- **WHEN** `crew console up wldn flow` runs on mac-studio
- **THEN** the `console` workspace of mac-studio's `wldn` session has a `flow` tab printing wldn's entries as they are written, and no agent is started or greeted

#### Scenario: Run twice
- **WHEN** `crew console up wldn flow` runs again
- **THEN** no second `flow` tab is opened

#### Scenario: Not asked for
- **WHEN** `crew console up wldn` runs on a host with no `flow` tab open
- **THEN** no `flow` tab is opened

### Requirement: The console has a rail tab
`crew console up <label> rail` SHALL open a `rail` tab in the `console` workspace, split in two, as `crew console up <label>` SHALL while no host job runs the follower. The upper pane SHALL show the rail frame the host's follower writes, `crew rail --label <label>` as of its last read, drawn again whenever the frame changes, and SHALL follow itself while no one does. The lower pane SHALL be a shell with crew on its path. When the tab is already there, it SHALL open nothing.

#### Scenario: The tab is opened
- **WHEN** `crew console up wldn rail` runs
- **THEN** the `console` workspace has a `rail` tab with wldn's rail above and a shell below in which `crew` runs

#### Scenario: A new entry refreshes the list
- **WHEN** the user approves a unit from the shell below
- **THEN** the list above is printed again within a few seconds, without that unit's review row

#### Scenario: Run twice
- **WHEN** `crew console up wldn rail` runs again
- **THEN** no second `rail` tab is opened

#### Scenario: The host's job stops
- **WHEN** the rail tab draws the frames of swancloud's follower job, and that job ends
- **THEN** within one period the rail tab follows itself, and the rail, the board's frame and the agents' views are written again

### Requirement: The console has a board tab
`crew console up <label> board` SHALL open a `board` tab in the `console` workspace, after the `rail` tab when it is there, showing the partition's board, drawn again each time the host's follower writes the board's frame. When the tab is already there, it SHALL open nothing.

#### Scenario: The tab is opened
- **WHEN** `crew console up wldn board` runs
- **THEN** the `console` workspace has a `board` tab showing wldn's board

#### Scenario: Run twice
- **WHEN** `crew console up wldn board` runs again
- **THEN** no second `board` tab is opened

#### Scenario: A new entry redraws it
- **WHEN** the user approves a unit from the rail tab's shell
- **THEN** the board tab is drawn again within a few seconds, with that unit's marker gone

### Requirement: The console's old name opens it and retires the host's operator agent
`crew operator up <label>` SHALL open the console as `crew console up <label>` does, saying it is `crew console up` now. The console's up SHALL end the operator agent the host's operator session held before the operator was a main-level role, `<label>-operator-<host>`, and close the panes crew recorded in its `operator` workspace, once that agent is not working; one working SHALL be left and said.

#### Scenario: The host's timer still runs the old name
- **WHEN** swancloud's timer runs `crew operator up wldn` on mac-studio
- **THEN** the console opens, the command says `crew operator up` is `crew console up` now, and no agent is started

### Requirement: Anything sent to another team or partition reaches its operator
`crew send <team or partition> "<text>"` SHALL deliver the text to the operator of the partition it names, `<label>-operator`, wherever that agent runs: a partition is named by its label, and a team resolves to the partition it belongs to. The text SHALL arrive marked as every tell is, `[crew tell from <sender>]`, the sender being the agent that ran the command or `<user>@<host>`, followed by `(sent to <team or partition>)` as it was named, then the text. A name that is no team and no partition SHALL be refused, naming the teams and partitions there are. A send by the operator to its own partition, or to one of its own partition's teams, SHALL be refused, saying it carries with `crew tell`. An operator that is not up, or waits on a question in its pane, SHALL get nothing typed, and the send SHALL fail saying so, as a tell does.

#### Scenario: A team's agent sends to another partition's team
- **WHEN** `crw-5-unit-1` runs `crew send swb-1 "The zone check fails on tenants with no region"`
- **THEN** `wldn-operator` is prompted with `[crew tell from crw-5-unit-1] (sent to swb-1) The zone check fails on tenants with no region`

#### Scenario: A partition by its label
- **WHEN** the user, at a shell on mac-studio, runs `crew send wldn "<text>"`
- **THEN** `wldn-operator` is prompted with `[crew tell from <user>@mac-studio] (sent to wldn) <text>`

#### Scenario: A name crew does not know
- **WHEN** an agent runs `crew send swb-1-conductor "<text>"`
- **THEN** nothing is sent, and crew says it sends to a team or a partition, naming each

#### Scenario: The door sends to itself
- **WHEN** `wldn-operator` runs `crew send swb-1 "<text>"` for a team of wldn
- **THEN** nothing is sent, and crew says it is wldn's door and carries with `crew tell`

#### Scenario: The operator waits on a question
- **WHEN** an agent sends to wldn while `wldn-operator` waits on a question in its pane
- **THEN** nothing is typed, and the send fails saying the operator waits on a question and to send again once it is answered

### Requirement: The operator carries what is sent to it
The operator SHALL carry what reaches it by `crew send` on to the agent whose job it is, in the sender's words and naming the sender: a finding becomes a signal it records, quoting the words as sent; a design question goes to the design agent; work to build to the planner; a message for a team to that team's conductor. It SHALL NOT answer it in the sender's place or reason it out itself. A request to change the teams, from an operator whose main level runs on a box, SHALL be sent with `crew send` to a partition whose main level runs on a Mac that keeps swancloud's checkout.

#### Scenario: A message for a team
- **WHEN** `wldn-operator` receives `[crew tell from crw-5-unit-1] (sent to swb-1) <text>`
- **THEN** it tells `swb-1-conductor` the text, saying it is from `crw-5-unit-1`

#### Scenario: A finding
- **WHEN** what is sent reports a defect, with no request
- **THEN** the operator records it as a signal, its excerpt the words as sent

### Requirement: Every brief names one way to send to another team or partition
Every brief SHALL say in one line, beside its roster, that anything for another team or another partition is sent with `crew send <team or partition> "<text>"`, which reaches that partition's operator, and that it is sent nowhere else. A team's brief SHALL count every team but its own as another team; a main level's brief SHALL count every partition but its own, and the teams of those. No brief SHALL tell an agent to send a team's or a partition's business to its conductors, or to tell another partition's operator by name.

#### Scenario: A coder's brief
- **WHEN** `crew brief swb-1 coder` prints
- **THEN** it says beside the roster that anything for another team or partition goes with `crew send`, and names no conductor of another team to send to

#### Scenario: The operator's brief on a box
- **WHEN** the operator's brief prints for a partition whose main level runs on a box
- **THEN** its request to change the teams goes with `crew send` to a partition named by its label, not with `crew tell` to another operator

### Requirement: The console opens with its shell alone
`crew console up <label> [flow] [rail] [board]` SHALL open the `console` workspace of the host's `<label>` session with a `shell` tab, a shell with crew on its path, and SHALL start no agent. It SHALL open the `flow`, `rail` or `board` tab only when named, or the rail tab while no host job runs the host's follower. A name that is no tab SHALL be refused, naming the three.

#### Scenario: Opened while the host's job follows
- **WHEN** swancloud's job runs `crew _follow` on mac-studio and `crew console up wldn` runs there
- **THEN** wldn's `console` workspace holds the `shell` tab alone, no agent is started or greeted, and the board's frame and wldn's agents' views are still written on every refresh

#### Scenario: Opened while no job follows
- **WHEN** no host job runs the follower on mac-studio and `crew console up wldn` runs there
- **THEN** wldn's `console` workspace holds the `shell` tab and the `rail` tab, whose loop is the host's follower, and no `flow` or `board` tab

#### Scenario: A tab asked for by name
- **WHEN** `crew console up wldn rail` runs while the host's job follows
- **THEN** the `console` workspace has the `rail` tab beside its `shell` tab, as the rail tab requirement says, and no `flow` or `board` tab

#### Scenario: A name that is no tab
- **WHEN** `crew console up wldn page` runs
- **THEN** it is refused, saying the tabs are flow, rail and board, and nothing is opened

### Requirement: The console keeps the tabs it has open
Every later `crew console up <label>`, a tab named or not, SHALL keep each console tab already open, running its command again where a restart left its pane its shell alone, and SHALL not open again a tab the user closed unless it is named, or is the rail tab while no host job runs the follower.

#### Scenario: Run again
- **WHEN** `crew console up wldn` runs again after `crew console up wldn rail`
- **THEN** nothing is opened, run or greeted, and the `rail` tab stays open

#### Scenario: A tab the user closed
- **WHEN** the user closed the `board` tab, and swancloud's timer runs `crew console up wldn`
- **THEN** no `board` tab is opened

#### Scenario: After a restart
- **WHEN** herdr brings the console's `flow` and `rail` tabs back as their shells alone, and `crew console up wldn` runs
- **THEN** each runs its command there again, and no tab is opened
