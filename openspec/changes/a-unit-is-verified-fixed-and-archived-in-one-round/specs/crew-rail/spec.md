## RENAMED Requirements

- FROM: `### Requirement: The rail lists what waits on the user in five groups`
- TO: `### Requirement: The rail lists what waits on the user in four groups`

## MODIFIED Requirements

### Requirement: The rail lists what waits on the user in four groups
`crew rail [--label L]` SHALL print, from any host, what waits on the user in a partition, or in every partition when no label is given or known. It SHALL group the rows in this order: proposals, batches, land, operations. A verify report SHALL be no row: its findings are fixed in one round with no wait on the user (`teams.17`). Every group heading SHALL be printed, with `none` under a group that has no rows.

#### Scenario: Something waits in two groups
- **WHEN** a proposal is open and a deploy is offered, and nothing else waits
- **THEN** `crew rail --label swancloud` prints the four headings in order, one row under proposals, one under operations, and `none` under batches and land

#### Scenario: Run from another host
- **WHEN** `crew rail --label wldn` runs on a host that holds none of wldn's teams
- **THEN** it prints the same rows as it does on the teams' host

#### Scenario: A unit in verify with its report
- **WHEN** unit `x` is in verify and its report was written after the last commit on `unit/x`
- **THEN** `crew rail` has no row for `x`

## REMOVED Requirements

### Requirement: A verify report the user has not answered is a row
**Reason**: A verify report waits on no one: its findings are fixed in one round with no card (record 0027, `teams.17`).
**Migration**: None: the row was read from the reports folder and the branch, and nothing was written for it.
