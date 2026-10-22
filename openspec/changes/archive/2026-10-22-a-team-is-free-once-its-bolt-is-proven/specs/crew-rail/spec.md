## MODIFIED Requirements

### Requirement: A bolt whose every unit has merged and that has not landed is a row
A bolt held by a team, whose units have all merged and not all landed, SHALL be a row under land. It SHALL name its team and the partition's main-level ops, and say that it waits to land. When its team holds another bolt, the row SHALL name it: as the bolt its team builds meanwhile while that bolt is not proven, and, once it is proven too, the team's next planned bolt of its kits that no team holds as what a yes frees the team for, or that nothing is planned for the team when none is. Once every unit's latest change has been in a batch whose card the user has answered and the bolt's verification is green, sluice's verdict on its last landing, it SHALL carry `crew tell <label>-ops "Land bolt <bolt>."`; until then it SHALL say what it waits on, the verification as it reads, the units due a batch and the batches waiting on the user's answer, and carry no command. It SHALL have begun to wait at the time of the last commit on its bolt branch.

#### Scenario: The last unit merges
- **WHEN** the last unit of bolt `b` merges into `bolt/b` through sluice, every unit's change has been in a batch the user has answered, and the landing's verdict is `passed`
- **THEN** `b` is a row under land, naming its team and `wldn-ops`, saying it waits to land, with the tell that lands it

#### Scenario: The team builds another bolt meanwhile
- **WHEN** swc-1 holds `b`, which waits to land, and `c`, given after it, with a unit in code
- **THEN** `b`'s row says swc-1 builds `c` meanwhile, and names no bolt that a yes frees

#### Scenario: A yes frees the team
- **WHEN** swc-1 holds `b` and `c`, both proven, and the plan's next bolt of swc-1's kit that no team holds is `d`
- **THEN** `b`'s row says a yes frees swc-1 for `d`

#### Scenario: A verification that is not green
- **WHEN** every unit of bolt `b` has merged and been in a batch the user has answered, and `bolt/b`'s head is no landing of sluice's
- **THEN** `b`'s row says it lands once its verification is green and what the verification is now, and carries no command

#### Scenario: A batch that waits on the user
- **WHEN** every unit of bolt `b` has merged, its verification is green, and batches 8 and 9, whose cards the user has not answered, hold its units' latest changes
- **THEN** `b`'s row says it lands once you have answered batches 8 and 9, and carries no command

#### Scenario: It lands
- **WHEN** the bolt is landed and closed in the plan
- **THEN** the next `crew rail` has no row for it
