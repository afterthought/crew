# Spec Delta

## MODIFIED Requirements

### Requirement: Every role starts on its model at its effort level
Every definition SHALL set this model, each with its 1M-token context, and this effort:

| role | model | effort |
|---|---|---|
| design agent | Fable 5.1 | xhigh |
| planner | Fable 5.1 | xhigh |
| curator | Fable 5.1 | high |
| conductor | Opus 5.5 | high |
| ops (team and main level) | Opus 5.5 | high |
| unit: construct | Opus 5.5 | high |
| unit: code and merge | Opus 5.5 | xhigh |
| unit: verify | Opus 5.5 | high |
| fix | Opus 5.5 | xhigh |
| dispatcher | Opus 5.5 | medium |
| operator agent | Opus 5.5 | medium |

#### Scenario: A unit moves from construct to code
- **WHEN** a unit's construct stage at high effort is followed by its code stage
- **THEN** the code stage's fresh agent starts at xhigh

#### Scenario: A curator starts
- **WHEN** `crew curate wldn` starts the curator
- **THEN** it runs on Fable 5.1 at high effort, unless wldn's partition entry overrides `roles.curator`
