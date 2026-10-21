# Spec Delta

## REMOVED Requirements

### Requirement: The operator agent starts with its operator session
**Reason**: Record 0035: the operator is one main-level role per partition; no host's operator agent is started apart from it.
**Migration**: `crew main up <label>` starts `<label>-operator`; `crew console up <label>` opens the tabs the operator session held.

## ADDED Requirements

### Requirement: The operator is a main-level role
The partition's operator, `<label>-operator`, SHALL be a standing role of its main level: `crew main up <label>` SHALL start it in an `operator` tab of the `<label>` workspace, beside the design agent, the planner and ops, and greet it once it is up as it greets them; `crew main down <label>` SHALL end it; `crew revive` SHALL bring it back as it brings them back. Every brief SHALL name it as the partition's operator, and crew SHALL start no other operator agent for the partition.

#### Scenario: The main level comes up with its operator
- **WHEN** `crew main up wldn` runs
- **THEN** `wldn-operator` starts in the `wldn` workspace's `operator` tab and is greeted once, beside `wldn-design`, `wldn-planner` and `wldn-ops`

#### Scenario: A conductor waits on the user with no card
- **WHEN** a conductor of wldn stops on a question asked only in its pane
- **THEN** its brief has it tell `wldn-operator`, the partition's one operator
