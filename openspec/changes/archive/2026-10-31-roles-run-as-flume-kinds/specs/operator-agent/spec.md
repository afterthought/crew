## MODIFIED Requirements

### Requirement: The operator is a main-level role
The partition's operator, `<label>-operator`, SHALL be a role of its main level: while it stands, `crew main up <label>` SHALL start it in an `operator` tab of the `<label>` workspace, beside the design agent, the planner and ops, and greet it once it is up as it greets them; `crew main down <label>` SHALL end it; `crew revive` SHALL bring it back as it brings them back. While its partition runs it as its kind, it SHALL run as a role's run does, on an ask, and none of these SHALL start it. Every brief SHALL name it as the partition's operator, and crew SHALL start no other operator agent for the partition.

#### Scenario: The main level comes up with its operator
- **WHEN** `crew main up wldn` runs
- **THEN** `wldn-operator` starts in the `wldn` workspace's `operator` tab and is greeted once, beside `wldn-design`, `wldn-planner` and `wldn-ops`

#### Scenario: A conductor waits on the user with no card
- **WHEN** a conductor of wldn stops on a question asked only in its pane
- **THEN** its brief has it tell `wldn-operator`, the partition's one operator

#### Scenario: The operator runs as its kind
- **WHEN** madswan's `flume` names a stream for its operator and `crew main up madswan` runs
- **THEN** no `operator` tab is opened and no operator is started, and a tell to `madswan-operator` is an ask of its role

### Requirement: Anything sent to another team or partition reaches its operator
`crew send <team or partition> "<text>"` SHALL deliver the text to the operator of the partition it names, `<label>-operator`, wherever that agent runs: a partition is named by its label, and a team resolves to the partition it belongs to. The text SHALL arrive marked as every tell is, `[crew tell from <sender>]`, the sender being the agent that ran the command or `<user>@<host>`, followed by `(sent to <team or partition>)` as it was named, then the text. A name that is no team and no partition SHALL be refused, naming the teams and partitions there are. A send by the operator to its own partition, or to one of its own partition's teams, SHALL be refused, saying it carries with `crew tell`. An operator that is not up, or waits on a question in its pane, SHALL get nothing typed, and the send SHALL fail saying so, as a tell does. To a partition that runs its operator as its kind, with no standing operator up, the send SHALL be written as an ask of the operator from the sender, carrying whom it was sent to and the text, and SHALL not fail for the operator not being up.

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

#### Scenario: An operator that runs as its kind
- **WHEN** madswan runs its operator as its kind, no standing operator of it is up, and swancloud-planner runs `crew send madswan "<text>"`
- **THEN** an ask of madswan's operator from swancloud-planner holds `(sent to madswan)` and the text, and nothing is typed
