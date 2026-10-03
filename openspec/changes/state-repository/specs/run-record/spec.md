# Spec Delta

## ADDED Requirements

### Requirement: The run record is carried to the state repository
Every write crew makes to a flywheel's branch SHALL, in the same commit, bring `runs/<host>/` on the branch up to the entries that host has recorded for the flywheel. `crew events --push` SHALL do the same on request with no other change. Only a host SHALL write its own files there, entries SHALL be added and never removed, and carrying the same entries twice SHALL change nothing.

#### Scenario: A tell, then a plan write
- **WHEN** an agent on the box tells another agent and later writes the plan
- **THEN** the plan write's commit also adds the tell's entry to `runs/chuck-herdr-alpha/` on the branch

#### Scenario: The newest entry
- **WHEN** a plan write has just landed
- **THEN** its own entry, which names that commit, is on the host and reaches the branch with the host's next write or `crew events --push`

#### Scenario: A host is rebuilt
- **WHEN** a host loses its local run record after carrying it
- **THEN** the entries it had carried are still on the branch, and its next carry adds its new entries beside them

## MODIFIED Requirements

### Requirement: Entries are gathered from every host
`crew events [--label <label>] [--about <object>] [--since <time>] [--json]` SHALL read the run record on the flywheel's branch of its state repository, then ask every host where the partition's teams, main level and operator sessions run, one call per host, for the entries it has not yet carried, and print them all in time order. A host that does not answer SHALL be named, and its entries shown as far as it had carried them.

#### Scenario: Two hosts
- **WHEN** `crew events --label wldn` runs on mac-studio while wldn's teams run on the box
- **THEN** the box's entries and mac-studio's are printed together in time order

#### Scenario: A host is asleep
- **WHEN** a Mac holding entries does not answer
- **THEN** the entries it had carried are printed with the other hosts', and the Mac is named as not answering

#### Scenario: One object
- **WHEN** `crew events --about unit/<unit>` runs
- **THEN** only entries naming that unit in `On` or `From` are printed
