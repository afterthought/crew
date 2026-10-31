## ADDED Requirements

### Requirement: Anything sent to another partition reaches its operator
`crew send <partition> "<text>"` SHALL deliver the text to the operator of the partition it names by its label, `<label>-operator`, wherever that agent runs. The text SHALL arrive marked as every tell is, `[crew tell from <sender>]`, the sender being the agent that ran the command or `<user>@<host>`, followed by `(sent to <partition>)`, then the text. A name that is no partition's label SHALL be refused, naming the partitions there are. A send by the operator to its own partition SHALL be refused, saying it carries with `crew tell`. An operator that is not up, or waits on a question in its pane, SHALL get nothing typed, and the send SHALL fail saying so, as a tell does.

#### Scenario: An agent sends to another partition
- **WHEN** `swancloud-planner` runs `crew send wldn "The zone check fails on tenants with no region"`
- **THEN** `wldn-operator` is prompted with `[crew tell from swancloud-planner] (sent to wldn) The zone check fails on tenants with no region`

#### Scenario: A partition by its label
- **WHEN** the user, at a shell on mac-studio, runs `crew send wldn "<text>"`
- **THEN** `wldn-operator` is prompted with `[crew tell from <user>@mac-studio] (sent to wldn) <text>`

#### Scenario: A name crew does not know
- **WHEN** an agent runs `crew send swb-1 "<text>"`, a team's name from before teams left
- **THEN** nothing is sent, and crew says it sends to a partition by its label, naming each

#### Scenario: The door sends to itself
- **WHEN** `wldn-operator` runs `crew send wldn "<text>"`
- **THEN** nothing is sent, and crew says it is wldn's door and carries with `crew tell`

#### Scenario: The operator waits on a question
- **WHEN** an agent sends to wldn while `wldn-operator` waits on a question in its pane
- **THEN** nothing is typed, and the send fails saying the operator waits on a question and to send again once it is answered

### Requirement: The operator carries what is sent to it to the role whose job it is
The operator SHALL carry what reaches it by `crew send` on to the agent whose job it is, in the sender's words and naming the sender: a finding becomes a signal it records, quoting the words as sent; a design question goes to the design agent; work to build, or a message about a bolt's work, to the planner; a landing, a deploy or an operation to main-level ops. It SHALL NOT answer it in the sender's place or reason it out itself. A request to change the teams file, from an operator whose main level runs on a box, SHALL be sent with `crew send` to a partition whose main level runs on a Mac that keeps swancloud's checkout.

#### Scenario: A message about a bolt's work
- **WHEN** `wldn-operator` receives `[crew tell from swancloud-planner] (sent to wldn) <text about a wldn bolt>`
- **THEN** it tells `wldn-planner` the text, saying it is from `swancloud-planner`

#### Scenario: A finding
- **WHEN** what is sent reports a defect, with no request
- **THEN** the operator records it as a signal, its excerpt the words as sent

### Requirement: Every brief names one way to send to another partition
Every brief SHALL say in one line, beside its roster, that anything for another partition is sent with `crew send <partition> "<text>"`, which reaches that partition's operator, and that it is sent nowhere else. A main level's brief SHALL count every partition but its own. No brief SHALL tell an agent to tell another partition's operator by name.

#### Scenario: The planner's brief
- **WHEN** `crew brief wldn planner` prints
- **THEN** it says beside the roster that anything for another partition goes with `crew send`, and names no team

#### Scenario: The operator's brief on a box
- **WHEN** the operator's brief prints for a partition whose main level runs on a box
- **THEN** its request to change the teams file goes with `crew send` to a partition named by its label, not with `crew tell` to another operator

## MODIFIED Requirements

### Requirement: The operator agent works for the user
The operator agent SHALL answer where the partition's work stands from `crew bolts` and `crew sites`, and what waits on the user from `crew rail`. It SHALL carry a request to the agent whose job it is, in the user's words:

- what to build and in what order: the planner;
- a design question: the design agent;
- a bolt's landing, a deploy or an operation: main-level ops.

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

## REMOVED Requirements

### Requirement: Anything sent to another team or partition reaches its operator
**Reason**: Record 0047 move 5: no team to send to; a send names a partition by its label (`briefs.10`).
**Migration**: "Anything sent to another partition reaches its operator", added by this change.

### Requirement: The operator carries what is sent to it
**Reason**: Record 0047 move 5: no team's conductor to carry a message to.
**Migration**: "The operator carries what is sent to it to the role whose job it is", added by this change.

### Requirement: Every brief names one way to send to another team or partition
**Reason**: Record 0047 move 5: no team to send to and no team's brief left.
**Migration**: "Every brief names one way to send to another partition", added by this change.
