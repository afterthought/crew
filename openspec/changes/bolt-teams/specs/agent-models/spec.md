# Spec Delta

## Purpose

Says which model every agent crew starts runs on, and how hard each role thinks. Changing either is one edit in crew.

## ADDED Requirements

### Requirement: Every agent runs on Opus 5.5
Every agent crew starts SHALL run on Opus 5.5 with its 1M-token context, named in one place in crew. No role SHALL run on another model.

#### Scenario: The design agent
- **WHEN** `crew main up wldn` starts the design agent
- **THEN** it runs on Opus 5.5, as every other role does

### Requirement: Each role has its effort level
crew SHALL start each role at its effort level:

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

### Requirement: Fable is gone
No role SHALL be called fable or run on the Fable model. The design agent at the main level SHALL take over what fable did, and a team SHALL have no design role of its own.

#### Scenario: A team's design question
- **WHEN** a conductor needs a design answer
- **THEN** it asks its partition's design agent
