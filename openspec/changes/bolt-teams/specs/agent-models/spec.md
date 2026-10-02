# Spec Delta

## Purpose

Says which model and effort each agent crew starts runs with, where they are set, and how one team or partition overrides them.

## ADDED Requirements

### Requirement: Each role is an agent definition
Each role crew starts SHALL be an agent definition, `plugin/roles/<role>.md` in Claude Code's agent format, whose frontmatter sets its `model` and `effort`. crew SHALL start the role with that model and effort, and with the definition's body, filled from `teams.json`, appended to Claude Code's own system prompt. No model or effort SHALL be named anywhere else in crew.

#### Scenario: The design agent
- **WHEN** `crew main up wldn` starts the design agent
- **THEN** it runs with the model and effort in `roles/design.md`

#### Scenario: A role changes for everyone
- **WHEN** a role's `effort` is edited in its definition and crew's checkout is pulled
- **THEN** that role's next start uses it, with no deploy

### Requirement: Every role starts on Opus 5.5 at its effort level
Every definition SHALL set Opus 5.5 with its 1M-token context, and this effort:

| role | effort |
|---|---|
| design agent | xhigh |
| planner | xhigh |
| conductor | high |
| ops (team and main level) | high |
| unit: construct | high |
| unit: code and merge | xhigh |
| unit: verify | high |
| fix | xhigh |
| dispatcher | medium |
| operator agent | medium |

#### Scenario: A unit moves from construct to code
- **WHEN** a unit's construct stage at high effort is followed by its code stage
- **THEN** the code stage's fresh agent starts at xhigh

### Requirement: The teams file overrides a role's model or effort
A team, or a partition's main level, in `teams.json` MAY set `roles.<role>.model` or `roles.<role>.effort`. crew SHALL start that role there with the override instead of its definition's value. An override naming a role or an effort level that does not exist SHALL be refused with a message naming it.

#### Scenario: One partition's planner
- **WHEN** wldn's partition entry sets `roles.planner.effort` to `max`
- **THEN** wldn's planner starts at max, and madswan's at its definition's xhigh

### Requirement: Fable is gone
No role SHALL be called fable or run on the Fable model. The design agent at the main level SHALL take over what fable did, and a team SHALL have no design role of its own.

#### Scenario: A team's design question
- **WHEN** a conductor needs a design answer
- **THEN** it asks its partition's design agent
