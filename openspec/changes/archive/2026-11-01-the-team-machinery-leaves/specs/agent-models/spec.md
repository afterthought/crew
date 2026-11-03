## ADDED Requirements

### Requirement: Each standing role starts on its model at its effort level
Every definition SHALL set this model, each with its 1M-token context where it runs on Opus, and this effort: the design agent and the planner Fable 5.1 at xhigh; main-level ops and the reviewer Opus 5.5 at high; the operator agent Opus 5.5 at medium. No definition SHALL exist for a conductor, a team's ops, a dispatcher or a unit's stage.

#### Scenario: The planner comes up
- **WHEN** `crew main up wldn` starts `wldn-planner`
- **THEN** it runs on Fable 5.1 at xhigh, as `roles/planner.md` sets

#### Scenario: A role crew no longer has
- **WHEN** anything asks crew for the brief of `conductor`, `ops`, `dispatcher`, `construct`, `coder` or `verify`
- **THEN** crew refuses, naming the definition it has no file for

### Requirement: The design agent is the partition's one design role
No role SHALL be called fable. The design agent at the main level SHALL take over what fable did, and SHALL be the partition's one design role.

#### Scenario: The main level's one design role
- **WHEN** `crew main up wldn` runs
- **THEN** `wldn-design` is the one design agent it starts, and nothing named fable starts

## MODIFIED Requirements

### Requirement: The teams file overrides a role's model or effort
A partition's main level in `teams.json` MAY set `roles.<role>.model` or `roles.<role>.effort` for its design agent, planner, main-level ops, operator or reviewer. crew SHALL start that role there with the override instead of its definition's value. An override naming a role or an effort level that does not exist SHALL be refused with a message naming it.

#### Scenario: One partition's planner
- **WHEN** wldn's partition entry sets `roles.planner.effort` to `max`
- **THEN** wldn's planner starts at max, and madswan's at its definition's xhigh

#### Scenario: A dispatcher's override
- **WHEN** a partition's entry sets `roles.dispatcher.effort`
- **THEN** crew refuses to load the teams file, naming the role it has no definition for

## REMOVED Requirements

### Requirement: Every role starts on its model at its effort level
**Reason**: Record 0047 move 5: the conductor's, team ops's, the unit stages', the fix's and the dispatcher's rows leave with those roles.
**Migration**: "Each standing role starts on its model at its effort level", added by this change.

### Requirement: The design agent replaces fable
**Reason**: Record 0047 move 5: no team, so no team's design question to route.
**Migration**: "The design agent is the partition's one design role", added by this change.
