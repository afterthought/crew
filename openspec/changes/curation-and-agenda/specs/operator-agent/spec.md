# Spec Delta

## MODIFIED Requirements

### Requirement: The operator agent works for the user
The operator agent SHALL answer where the partition's work stands from `crew bolts`, `crew status` and `crew sites`, and what waits on the user from `crew agenda` and `crew plan proposed`. It SHALL carry a request to the agent whose job it is, in the user's words:

- what to build and in what order: the planner;
- a design question, or an agenda item the user wants to take up: the design agent;
- which host runs what: that host's dispatcher;
- a bolt's progress: its conductor.

It SHALL start curation with `crew curate` when the user asks for it, and SHALL move a signal by hand or approve a proposal only on the user's word. It SHALL NOT write the plan, a kit or a design itself.

#### Scenario: Where things stand
- **WHEN** the user asks the operator agent what is in flight
- **THEN** it answers in a few plain sentences from `crew bolts` and names anything waiting on the user: units in review, proposals to approve, and design items on the agenda

#### Scenario: A request for new work
- **WHEN** the user asks for a feature
- **THEN** the operator agent passes it to the planner in the user's words, and tells the user which pane to carry on in

#### Scenario: Curate now
- **WHEN** the user says to curate the signals
- **THEN** the operator agent runs `crew curate <label>` and says how many signals the batch holds
