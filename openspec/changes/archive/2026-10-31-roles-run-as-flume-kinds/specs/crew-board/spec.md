## ADDED Requirements

### Requirement: A role that runs as its kind has its view
Each role its partition runs as its kind SHALL have a view among the agents' views under its run's name, `<label>-<role>`, drawn above its run's prompt by crew's mod where crew's plugin loads: what its turn took, and how many asks wait for the role and since when.

#### Scenario: A run with an ask waiting
- **WHEN** madswan's planner run took two asks and a third has waited four minutes
- **THEN** madswan-planner's view shows the two it took and one waiting for four minutes

#### Scenario: Nothing waiting
- **WHEN** madswan's planner run took one ask and nothing else waits
- **THEN** madswan-planner's view shows the one it took and says nothing waits

### Requirement: The attention line names a role's run that waits
The board's attention line SHALL name each run of a role that the runner's records show stopped short, with its words, or lost, with its place and host, and SHALL print no command for it.

#### Scenario: A lost run
- **WHEN** the runner's records show madswan's design run `crew-design--madswan` on deneb lost
- **THEN** the attention line names madswan's design run as lost, with its place and deneb, and prints no command
