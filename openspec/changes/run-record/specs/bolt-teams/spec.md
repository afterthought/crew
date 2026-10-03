# Spec Delta

## ADDED Requirements

### Requirement: The conductor waits for a stage through crew
After starting a unit's stage, the conductor SHALL wait for it with `crew unit wait <unit>`, run as a background command, and SHALL NOT wait on the slot's agent with herdr directly. `crew unit wait` SHALL run on the team's host, return when the slot's agent is no longer working or its timeout passes, and say which.

#### Scenario: A stage settles
- **WHEN** a conductor has `crew unit wait <unit>` running and the unit's code agent goes idle
- **THEN** the command returns, saying the agent settled, and the stage's end is in the run record

#### Scenario: The timeout passes
- **WHEN** the agent is still working when the timeout passes
- **THEN** the command returns saying so, and no `stage.end` entry is written
