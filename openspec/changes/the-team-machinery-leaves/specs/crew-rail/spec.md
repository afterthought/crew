## ADDED Requirements

### Requirement: A bolt whose every unit has merged and that has not landed is a row of its kit's
Each kit with a bolt in flight whose units have all merged and not all landed SHALL be one row under land, keyed `land/<kit>`, naming the partition's main-level ops and, in the plan's order, each such bolt with what it waits on. A bolt not yet proven SHALL say what it waits on: the verification as it reads, the units due a batch, the batches waiting on the user's answer, a fix in flight, a landing sluice refused at its head for the bolt's own content, or that it takes main first, forecast at its present head to conflict with what main holds. A bolt that can land whose last landing at its head sluice or its host stopped SHALL say, beside that it can land, what stopped it and that main-level ops submits it again once that is cleared. Once a bolt can land, the row SHALL carry `crew tell <label>-ops "Land <bolts that can land, in order>."`. The row SHALL have begun to wait at the time of the earliest last commit among its bolts' branches.

#### Scenario: The last unit merges
- **WHEN** the last unit of crew's bolt `b` merges into `bolt/b` through sluice, every unit's change has been in a batch the user has answered, and the landing's verdict is `passed`
- **THEN** crew's row under land names `b` and `swancloud-ops`, saying `b` waits to land, with the tell that lands it

#### Scenario: Two bolts of one kit
- **WHEN** crew's bolts `b` and `c` can both land, `b` first in the plan
- **THEN** there is one row, `land/crew`, naming `b` then `c`, its tell naming both in that order

#### Scenario: A verification that is not green
- **WHEN** every unit of bolt `b` has merged and been in a batch the user has answered, and `bolt/b`'s head is no landing of sluice's
- **THEN** `b`'s line says it lands once its verification is green and what the verification is now, and the row's tell leaves `b` out

#### Scenario: A batch that waits on the user
- **WHEN** every unit of bolt `b` has merged, its verification is green, and batches 8 and 9, whose cards the user has not answered, hold its units' latest changes
- **THEN** `b`'s line says it lands once you have answered batches 8 and 9, and the row carries no tell when no other bolt can land

#### Scenario: A refused landing
- **WHEN** sluice refused `b`'s landing at its head for a conflict
- **THEN** `b`'s line says it is held, in sluice's words, until a fix moves its head

#### Scenario: A bolt taking main first
- **WHEN** `b` reads proven and the run record holds a `forecast` on `bolt/b` at `b`'s present head naming a conflict with main on `README.md` and no submission queued on main
- **THEN** `b`'s line says it takes main first, forecast to conflict with main on `README.md`, until a fix taking main in moves its head, and the row's tell leaves `b` out

#### Scenario: A conflict forecast at an older head
- **WHEN** the run record's `forecast` on `bolt/b` naming a conflict with main is at a head `b` has since moved from
- **THEN** that forecast holds nothing on `b`'s line

#### Scenario: A stopped landing
- **WHEN** `b`'s last landing at its head did not land because sluice itself failed
- **THEN** `b`'s line says it can land, that sluice itself failed at that head, in sluice's words, and that `swancloud-ops` submits it again once that is cleared, and the row's tell names `b`

#### Scenario: It lands
- **WHEN** the bolt is landed and closed in the plan
- **THEN** the next `crew rail` names it on no row

### Requirement: An open proposal is a row until the user approves or drops it
Each open proposal on the flywheel's branch SHALL be a row under proposals. The row SHALL name the command that prints it (`crew plan proposed <n> --label <label>`), the command that opens it in plannotator for the user to read and annotate (`crew plan proposed <n> --label <label> --open`), and the command that approves it (`crew plan approve <n> --label <label>`). It SHALL have begun to wait at its `plan.propose` entry in the run record, or at its `Opened` date when no entry is found.

#### Scenario: An open proposal
- **WHEN** proposal 3 is open and touches a bolt in flight
- **THEN** its row names no agreement it needs and carries `crew plan proposed 3 --label wldn`, `crew plan proposed 3 --label wldn --open` and `crew plan approve 3 --label wldn`

#### Scenario: Approved
- **WHEN** proposal 3 is approved
- **THEN** the next `crew rail` has no row for it

## REMOVED Requirements

### Requirement: A bolt whose every unit has merged and that has not landed is a row
**Reason**: Record 0047 move 5, record 0050 part 3: no team holds a bolt, builds another meanwhile or is freed by a yes.
**Migration**: "A bolt whose every unit has merged and that has not landed is a row of its kit's", added by this change.

### Requirement: An open proposal is a row until it is approved or dropped
**Reason**: Record 0047 move 5: no conductor's agreement is needed (`plan.4`).
**Migration**: "An open proposal is a row until the user approves or drops it", added by this change.
