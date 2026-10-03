# Spec Delta

## ADDED Requirements

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
