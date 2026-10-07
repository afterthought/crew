# Spec Delta

## Purpose

One list of everything that waits on the user, read from the state crew already keeps, so the user can work down it and an answered item leaves it on its own.

## ADDED Requirements

### Requirement: The rail lists what waits on the user in four groups
`crew rail [--label L]` SHALL print, from any host, what waits on the user in a partition, or in every partition when no label is given or known. It SHALL group the rows in this order: proposals, review, verify, land. Every group heading SHALL be printed, with `none` under a group that has no rows.

#### Scenario: Something waits in two groups
- **WHEN** a proposal is open and a unit is in review, and nothing else waits
- **THEN** `crew rail --label wldn` prints the four headings in order, one row under proposals, one under review, and `none` under verify and land

#### Scenario: Run from another host
- **WHEN** `crew rail --label wldn` runs on a host that holds none of wldn's teams
- **THEN** it prints the same rows as it does on the teams' host

### Requirement: Each row has its time, its age and the command that answers it
Each row SHALL name what waits, when it began to wait, how long ago that was, and the command that answers it, written to be pasted into a shell, with every path quoted. Within a group, rows SHALL be ordered oldest first. A row's time SHALL be read from the same state as the row itself, never from a record kept for the rail.

#### Scenario: Two units in review
- **WHEN** unit `a` has been in review since 09:00 and unit `b` since 11:00
- **THEN** `a`'s row comes before `b`'s, and each shows its time and its age

### Requirement: An open proposal is a row until it is approved or dropped
Each open proposal on the flywheel's branch SHALL be a row under proposals. The row SHALL name the conductors whose agreement it still needs, the command that prints it (`crew plan proposed <n> --label <label>`) and the command that approves it (`crew plan approve <n> --label <label>`). It SHALL have begun to wait at its `plan.propose` entry in the run record, or at its `Opened` date when no entry is found.

#### Scenario: A proposal waiting on a conductor
- **WHEN** proposal 3 is open and touches a bolt swb-1 holds, and swb-1-conductor has not agreed
- **THEN** its row says it still needs swb-1-conductor's agreement and carries `crew plan proposed 3 --label wldn` and `crew plan approve 3 --label wldn`

#### Scenario: Approved
- **WHEN** proposal 3 is approved
- **THEN** the next `crew rail` has no row for it

### Requirement: A unit in review is a row with the command that opens its whole change
Each unit whose stage is review SHALL be a row under review, naming its team and host. The row SHALL carry a command that opens the unit's whole change folder in plannotator, and the command that approves it (`crew unit approve <unit> --label <label>`). It SHALL have begun to wait at the time of the last commit on the unit's branch.

#### Scenario: Opened on the team's host
- **WHEN** `crew rail` runs on the host of the unit's team
- **THEN** the row carries `plannotator-tui herdr open <kit>/places/<unit>/openspec/changes/<unit>/`

#### Scenario: Opened from another host
- **WHEN** `crew rail` runs on a host other than the unit's team's host
- **THEN** the row carries `ssh -t <the team host's ssh name> plannotator-tui <the same folder>`

#### Scenario: Construct runs again
- **WHEN** the unit is sent back to construct
- **THEN** the next `crew rail` has no row for it until its change is in review again

### Requirement: A verify report the user has not answered is a row
A unit in verify whose newest verify report in its team's reports folder is newer than the last commit on its branch SHALL be a row under verify. The row SHALL show the report's path, a command that opens it, and `crew tell <team>-conductor "On <unit>'s verify report: "` for the user to complete in their own words. It SHALL have begun to wait at the report file's time.

#### Scenario: A report written after the last commit
- **WHEN** unit `x` is in verify and its report was written after the last commit on `unit/x`
- **THEN** `x` is a row under verify with the report's path

#### Scenario: Code commits again
- **WHEN** a code stage then commits on `unit/x`
- **THEN** the next `crew rail` has no verify row for `x`

### Requirement: A bolt whose every unit has merged and that has not landed is a row
A bolt held by a team, whose units have all merged and not all landed, SHALL be a row under land. It SHALL name its team and the partition's main-level ops, and carry `crew tell <label>-ops "Land bolt <bolt>."`. It SHALL have begun to wait at the time of the last commit on its bolt branch.

#### Scenario: The last unit merges
- **WHEN** the last unit of bolt `b` merges into `bolt/b`
- **THEN** `b` is a row under land, naming its team and `wldn-ops`

#### Scenario: It lands
- **WHEN** the bolt is landed and closed in the plan
- **THEN** the next `crew rail` has no row for it

### Requirement: Nothing is written to make or clear a row
`crew rail` SHALL read only the plan, the proposals, the kits and the run record, and SHALL write nothing to any of them. Every row SHALL leave the list when the state it was read from records its answer.

#### Scenario: A read leaves no trace
- **WHEN** `crew rail` runs
- **THEN** the flywheel's branch, the kits and the run record are unchanged

### Requirement: A host that does not answer is named
When a team's host does not answer, `crew rail` SHALL print the rows it could read and name that host, saying that its units and bolts may also wait on the user. It SHALL exit zero. When a partition's plan cannot be read, it SHALL name it and exit non-zero.

#### Scenario: The box is asleep
- **WHEN** chuck-herdr-alpha does not answer
- **THEN** `crew rail` still lists the open proposals and the rows of other hosts, and names chuck-herdr-alpha as not answering
