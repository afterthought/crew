## MODIFIED Requirements

### Requirement: A bolt whose every unit has merged and that has not landed is a row
Each kit with a bolt held by a team whose units have all merged and not all landed SHALL be one row under land, keyed `land/<kit>`, naming the partition's main-level ops and, in the plan's order, each such bolt with its team and what it waits on. When its team holds another bolt, a bolt's line SHALL name it: as the bolt its team builds meanwhile while that bolt is not proven, and, once it is proven too, the team's next planned bolt as what a yes frees the team for, or that nothing is planned for the team. A bolt not yet proven SHALL say what it waits on: the verification as it reads, the units due a batch, the batches waiting on the user's answer, a fix in flight, or a landing sluice refused at its head for the bolt's own content. A bolt that can land whose last landing at its head sluice or its host stopped SHALL say, beside that it can land, what stopped it and that main-level ops submits it again once that is cleared. Once a bolt can land, the row SHALL carry `crew tell <label>-ops "Land <bolts that can land, in order>."`. The row SHALL have begun to wait at the time of the earliest last commit among its bolts' branches.

#### Scenario: The last unit merges
- **WHEN** the last unit of crew's bolt `b` merges into `bolt/b` through sluice, every unit's change has been in a batch the user has answered, and the landing's verdict is `passed`
- **THEN** crew's row under land names `b` with its team and `swancloud-ops`, saying `b` waits to land, with the tell that lands it

#### Scenario: Two bolts of one kit
- **WHEN** crew's bolts `b` and `c` can both land, `b` first in the plan
- **THEN** there is one row, `land/crew`, naming `b` then `c`, its tell naming both in that order

#### Scenario: The team builds another bolt meanwhile
- **WHEN** swc-1 holds `b`, which waits to land, and `c`, given after it, with a unit in code
- **THEN** `b`'s line says swc-1 builds `c` meanwhile, and names no bolt that a yes frees

#### Scenario: A yes frees the team
- **WHEN** swc-1 holds `b` and `c`, both proven, and the plan's next bolt of swc-1's kit that no team holds is `d`
- **THEN** `b`'s line says a yes frees swc-1 for `d`

#### Scenario: A verification that is not green
- **WHEN** every unit of bolt `b` has merged and been in a batch the user has answered, and `bolt/b`'s head is no landing of sluice's
- **THEN** `b`'s line says it lands once its verification is green and what the verification is now, and the row's tell leaves `b` out

#### Scenario: A batch that waits on the user
- **WHEN** every unit of bolt `b` has merged, its verification is green, and batches 8 and 9, whose cards the user has not answered, hold its units' latest changes
- **THEN** `b`'s line says it lands once you have answered batches 8 and 9, and the row carries no tell when no other bolt can land

#### Scenario: A refused landing
- **WHEN** sluice refused `b`'s landing at its head for a conflict
- **THEN** `b`'s line says it is held, in sluice's words, until its team's fix moves its head

#### Scenario: A stopped landing
- **WHEN** `b`'s last landing at its head did not land because sluice itself failed
- **THEN** `b`'s line says it can land, that sluice itself failed at that head, in sluice's words, and that `swancloud-ops` submits it again once that is cleared, and the row's tell names `b`

#### Scenario: It lands
- **WHEN** the bolt is landed and closed in the plan
- **THEN** the next `crew rail` names it on no row
