## ADDED Requirements

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
