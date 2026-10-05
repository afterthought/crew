# operator-agent Specification

## Purpose
A standing agent in each operator session that works for the user. It says where the partition's work stands, opens what is running, and carries requests to the agent whose job they are.

## Requirements

### Requirement: The operator agent starts with its operator session
`crew operator up <label>` SHALL start the operator agent, `<label>-operator-<host>`, in a herdr workspace named `operator` in the session named `<label>` on the host it runs on. When the agent is already up, it SHALL do nothing and succeed. When the session or the partition is unknown, it SHALL exit non-zero, naming what is missing.

#### Scenario: Started by the host
- **WHEN** the `madswan` operator session starts on mac-studio and its supervisor runs `crew operator up madswan`
- **THEN** `madswan-operator-mac-studio` is running in the `operator` workspace of that session

#### Scenario: Run twice
- **WHEN** `crew operator up wldn` runs while the agent is up
- **THEN** nothing is started and the command succeeds

### Requirement: The operator agent works for the user
The operator agent SHALL answer where the partition's work stands from `crew bolts`, `crew status` and `crew sites`. It SHALL carry a request to the agent whose job it is, in the user's words:

- what to build and in what order: the planner;
- a design question: the design agent;
- which host runs what: that host's dispatcher;
- a bolt's progress: its conductor.

It SHALL NOT write the plan, a kit or a design itself.

#### Scenario: Where things stand
- **WHEN** the user asks the operator agent what is in flight
- **THEN** it answers in a few plain sentences from `crew bolts` and names anything waiting on the user, such as units in review

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
