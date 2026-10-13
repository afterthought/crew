## ADDED Requirements

### Requirement: Every suite on a host shares the host's test slots
Every crew test on a host, whichever worktree, team or suite runs it, SHALL take one of the host's test slots before it runs and hold it until it ends, killed or not, and a test that finds none free SHALL wait its turn. A host SHALL have `CREW_TEST_SLOTS` slots, else its cores less two and at least two; a count that is not a number SHALL be refused. A test started inside another's slot SHALL run in that slot.

#### Scenario: Two tests and one slot
- **WHEN** a host has one slot and a second test starts while the first holds it
- **THEN** the second waits, and runs once the first lets its slot go

#### Scenario: A killed test
- **WHEN** a test holding a slot is killed
- **THEN** its slot is free again for the next test

#### Scenario: No count given
- **WHEN** `CREW_TEST_SLOTS` is not set on a host with ten cores
- **THEN** the host has eight slots
