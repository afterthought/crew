## RENAMED Requirements

- FROM: `### Requirement: The rail lists what waits on the user in four groups`
- TO: `### Requirement: The rail lists what waits on the user in five groups`

## MODIFIED Requirements

### Requirement: The rail lists what waits on the user in five groups
`crew rail [--label L]` SHALL print, from any host, what waits on the user in a partition, or in every partition when no label is given or known. It SHALL group the rows in this order: proposals, batches, verify, land, deploys. Every group heading SHALL be printed, with `none` under a group that has no rows.

#### Scenario: Something waits in two groups
- **WHEN** a proposal is open and a deploy is offered, and nothing else waits
- **THEN** `crew rail --label swancloud` prints the five headings in order, one row under proposals, one under deploys, and `none` under batches, verify and land

#### Scenario: Run from another host
- **WHEN** `crew rail --label wldn` runs on a host that holds none of wldn's teams
- **THEN** it prints the same rows as it does on the teams' host
