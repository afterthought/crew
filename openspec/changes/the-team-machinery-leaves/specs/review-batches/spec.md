## ADDED Requirements

### Requirement: A batch spans the partition's bolts
A batch SHALL hold the changes due across every bolt of a partition. A partition SHALL have a batch setting, a count N and a number of hours T, read from its entry in the teams file. A batch SHALL be due, at the rail's sweep on the partition's main-level host, when N changes are due across its bolts, or when T hours have passed since the partition's last batch and at least one change is due, whichever comes first.

#### Scenario: Changes from several bolts
- **WHEN** a partition's setting is 5 and 4 hours, and two units of bolt `x` and three of bolt `y` have been constructed since its last batch
- **THEN** a batch is due at the rail's next sweep on the main level's host, holding those five changes

#### Scenario: The time is reached
- **WHEN** two changes have been constructed across the partition's bolts since its last batch, four hours ago
- **THEN** a batch is due, holding those two

#### Scenario: Nothing due
- **WHEN** four hours have passed since the last batch and no change has been constructed since
- **THEN** no batch is due

#### Scenario: Swept on another host
- **WHEN** the rail's sweep runs on a host that is not wldn's main-level host
- **THEN** it reckons no batch for wldn

### Requirement: A batch is reckoned from the partition's branch, never a host
Whether a batch is due, what a review holds, and whether every unit's latest change of a bolt has been in a batch, SHALL be read from the run record on the partition's branch alone, asking no host for it. A host that does not answer SHALL hold none of them. When the branch cannot be read, each SHALL be refused naming the branch, as crew can't tell then which changes have been in a batch.

#### Scenario: The laptop asleep at the rail's sweep
- **WHEN** the rail's sweep on chuck-herdr-alpha, wldn's main-level host, runs while macbook-pro, which holds a wldn operator session, does not answer, and five changes are due
- **THEN** the sweep finds the batch due and the planner is told, and macbook-pro is not asked

#### Scenario: A review while the laptop is asleep
- **WHEN** the planner runs `crew review wldn` while macbook-pro does not answer and a batch is due
- **THEN** the reviewer is started on the batch's due changes, and no earlier batch's summary is returned in its place

#### Scenario: A landing while the laptop is off
- **WHEN** `crew bolt land` runs on mac-studio for a bolt whose every unit's latest change has been in a batch the user answered, while macbook-pro is off the tailnet
- **THEN** the bolt is closed as landed, and nothing names macbook-pro

#### Scenario: The branch cannot be read
- **WHEN** the rail's sweep runs while `wldn/main` cannot be fetched
- **THEN** whether a batch is due is not reckoned, and the sweep says crew can't tell which changes have been in a batch, naming `wldn/main` and why

## MODIFIED Requirements

### Requirement: The reviewer summarizes a batch
The reviewer SHALL read each due change whole and write one summary file holding, for each unit, its bolt, a short opening paragraph saying what the change does and what the user would most care about, then the decisions it took, its risks, what it touches named in words, and anything the user would likely care about, as paragraphs and plain lists with no code block, no table and no path. The batch SHALL end at that file, its deliverable, and the reviewer SHALL write nothing else. The run record SHALL name the batch, each unit it holds and the commit each unit's change was read at.

#### Scenario: A batch of three
- **WHEN** a batch holds three units' changes from two bolts
- **THEN** the reviewer's file holds one section for each of the three, naming its bolt and opening with its paragraph, and the run record names the three units and their commits

#### Scenario: What a change touches
- **WHEN** the reviewer summarizes a change whose Touches lists the card hook and its test
- **THEN** its section names them in words, with no code block and no path

## REMOVED Requirements

### Requirement: Notes reach the unit's conductor
**Reason**: Record 0047 move 5: no conductor stands; batches and amendments are the planner's, and a unit's notes reach its work as the crossed path hands them.
**Migration**: The crossed path's requirement for a crossed bolt's notes (`teams-cross-to-flume-as-their-bolts-land`); the planner still sends nothing but the user's words.

### Requirement: Notes amend a unit in flight with no re-approval
**Reason**: Record 0047 move 5: no conductor runs construct again; the crossed path launches a unit's construct again with its notes, and a merged unit's defect as a fix on the bolt.
**Migration**: The crossed path's requirement for a crossed bolt's notes (`teams-cross-to-flume-as-their-bolts-land`).

### Requirement: A batch spans the partition
**Reason**: Record 0047 move 5: a batch spans the partition's bolts, reckoned on its main-level host; no team or conductor's wait.
**Migration**: "A batch spans the partition's bolts", added by this change.

### Requirement: A batch is reckoned from the partition's branch alone
**Reason**: Record 0047 move 5: no conductor's wait reckons a batch; the rail's sweep on the main-level host does.
**Migration**: "A batch is reckoned from the partition's branch, never a host", added by this change.
