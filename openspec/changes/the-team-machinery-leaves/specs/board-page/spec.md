## MODIFIED Requirements

### Requirement: A word goes to the agent its item's kind names
The agent a dock's word goes to SHALL be decided from the item's kind: a bolt, a unit or chore, a fix, a proposal or a batch to the partition's planner; a signal or a record to its design agent; a landing, a deploy or an operation to its main-level ops; and a subscription or a partition to the partition's operator.

#### Scenario: Each kind's agent
- **WHEN** the page is written for wldn with a bolt in flight with a unit and a fix, a planned bolt, a proposal, a signal, a landing, a deploy, an operation and a subscription
- **THEN** the bolt, unit, fix, planned bolt and proposal go to wldn-planner, the signal to wldn-design, the landing, deploy and operation to wldn-ops, and the subscription to wldn-operator

## REMOVED Requirements

### Requirement: A viewer narrows every lane to one team
**Reason**: Record 0047 move 5, record 0050 part 3: no teams to narrow to or name.
**Migration**: None.

### Requirement: The team chosen survives a reload
**Reason**: Record 0047 move 5, record 0050 part 3: no teams to narrow to or name.
**Migration**: None.

### Requirement: The strip names the partition's teams
**Reason**: Record 0047 move 5, record 0050 part 3: no teams to narrow to or name.
**Migration**: None.
