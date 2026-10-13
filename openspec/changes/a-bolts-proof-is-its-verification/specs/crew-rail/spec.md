## MODIFIED Requirements

### Requirement: A bolt whose every unit has merged and that has not landed is a row
A bolt held by a team, whose units have all merged and not all landed, SHALL be a row under land. It SHALL name its team and the partition's main-level ops. Once every unit's latest change has been in a batch and the bolt's verification is green, sluice's verdict on its last landing, it SHALL carry `crew tell <label>-ops "Land bolt <bolt>."`; until then it SHALL say what it waits on, the verification as it reads, and carry no command. It SHALL have begun to wait at the time of the last commit on its bolt branch.

#### Scenario: The last unit merges
- **WHEN** the last unit of bolt `b` merges into `bolt/b` through sluice, every unit's change has been in a batch, and the landing's verdict is `passed`
- **THEN** `b` is a row under land, naming its team and `wldn-ops`, with the tell that lands it

#### Scenario: A verification that is not green
- **WHEN** every unit of bolt `b` has merged and been in a batch, and `bolt/b`'s head is no landing of sluice's
- **THEN** `b`'s row says it lands once its verification is green and what the verification is now, and carries no command

#### Scenario: It lands
- **WHEN** the bolt is landed and closed in the plan
- **THEN** the next `crew rail` has no row for it
