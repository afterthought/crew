## MODIFIED Requirements

### Requirement: Every agent crew starts carries its name for sluice
Every agent crew starts SHALL have `SLUICE_AGENT` in its environment, the same as its `CREW_AGENT`, from its start and again when herdr resumes it where crew gives it its identity back; a main level's agent herdr resumes off its main level's host SHALL have neither (`main-level`).

#### Scenario: A stage's agent starts
- **WHEN** crew starts `swb-1-unit-2` for a code stage
- **THEN** its environment holds `CREW_AGENT=swb-1-unit-2` and `SLUICE_AGENT=swb-1-unit-2`

#### Scenario: herdr resumes an agent
- **WHEN** herdr resumes the conductor's session without crew's environment
- **THEN** its commands see `SLUICE_AGENT` back, the same as its `CREW_AGENT`

#### Scenario: herdr resumes a main level's agent on another host
- **WHEN** herdr resumes `swancloud-planner`'s session on a host the teams file does not name for swancloud's main level
- **THEN** its commands see neither `CREW_AGENT` nor `SLUICE_AGENT`
