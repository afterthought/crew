## MODIFIED Requirements

### Requirement: The rail lists what waits on the user in four groups
`crew rail [--label L]` SHALL print, from any host, what waits on the user in a partition, or in every partition when no label is given or known. It SHALL group the rows in this order: proposals, batches, land, operations, questions, the last the open question cards agents asked in their own name, each with its asker, its title and its age. A verify report SHALL be no row (`teams.17`). Every group heading SHALL be printed, with `none` under a group that has no rows.

#### Scenario: Something waits in three groups
- **WHEN** a proposal is open, a deploy is offered and a conductor's question is open, and nothing else waits
- **THEN** `crew rail --label swancloud` prints the five headings in order, one row under proposals, one under operations, one under questions, and `none` under batches and land

#### Scenario: Run from another host
- **WHEN** `crew rail --label wldn` runs on a host that holds none of wldn's teams
- **THEN** it prints the same rows as it does on the teams' host
