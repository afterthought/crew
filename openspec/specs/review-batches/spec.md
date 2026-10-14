# review-batches Specification

## Purpose
TBD - created by archiving change units-build-at-once-and-are-reviewed-in-batches. Update Purpose after archive.

## Requirements

### Requirement: Each construct makes a unit's change due for review
A unit's change SHALL be due for the user's review each time a construct stage of the unit commits, the first construct and every construct run again. A change SHALL stop being due once a batch has included it at the commit its construct left.

#### Scenario: An amended change
- **WHEN** a unit already in a batch is constructed again with the user's notes
- **THEN** its change is due again, and counts toward the next batch

### Requirement: A batch spans the partition
A batch SHALL hold the changes due across every team of a partition. A partition SHALL have a batch setting, a count N and a number of hours T, read from its entry in the teams file. A batch SHALL be due, on any wait of a conductor of the partition, when N changes are due across its teams, or when T hours have passed since the partition's last batch and at least one change is due, whichever comes first.

#### Scenario: Changes from several teams
- **WHEN** a partition's setting is 5 and 4 hours, and two of swb-1's units and three of swb-3's have been constructed since its last batch
- **THEN** a batch is due, holding those five changes

#### Scenario: The time is reached
- **WHEN** two changes have been constructed across the partition's teams since its last batch, four hours ago
- **THEN** a batch is due, holding those two

#### Scenario: Nothing due
- **WHEN** four hours have passed since the last batch and no change has been constructed since
- **THEN** no batch is due

### Requirement: The planner starts the partition's reviewer
When a batch is due, crew SHALL tell the partition's planner once, and the planner SHALL start the reviewer: a main-level role, run fresh for each batch in its own tab of the main level's workspace, beside the planner, on the main level's host.

#### Scenario: A batch is due
- **WHEN** a conductor's wait finds a batch due in the wldn partition
- **THEN** wldn-planner is told once, and starts `wldn-reviewer` in the `wldn` workspace

### Requirement: The reviewer summarizes a batch
The reviewer SHALL read each due change whole and write one summary file holding, for each unit, its team, what the change does, the decisions it took, its risks, its Touches, and anything the user would likely care about. The batch SHALL end at that file, its deliverable, and the reviewer SHALL write nothing else. The run record SHALL name the batch, each unit it holds and the commit each unit's change was read at.

#### Scenario: A batch of three
- **WHEN** a batch holds three units' changes from two teams
- **THEN** the reviewer's file holds one section for each of the three, naming its team, and the run record names the three units and their commits

### Requirement: The planner posts a batch as cards of at most five units
The planner SHALL post a batch as partition cards, each keyed to a rail row of the batch, of at most five units each; a batch of more than five changes SHALL be split across cards. A batch's answers SHALL be the user's; no agent SHALL answer a batch card.

#### Scenario: Seven changes due
- **WHEN** a batch holds seven changes
- **THEN** the planner posts two cards, one of five units and one of two

### Requirement: A batch card is read and answered in Pending You
Each batch card SHALL carry, in its body, each unit's summary and the link to a plannotator session on each unit's whole OpenSpec change, one session for each unit, and SHALL ask two questions: one choice of several, "which need notes?", listing its units, and one question in words for the notes. The annotations the user sends from a unit's session SHALL be read as that unit's notes. The sessions SHALL end when the card closes.

#### Scenario: The user drills in
- **WHEN** the user opens a batch card holding three units
- **THEN** the card shows each unit's summary, and three links, each opening a plannotator session on one unit's whole change

#### Scenario: Notes written in a session
- **WHEN** the user annotates one unit's change in its session and sends the annotations
- **THEN** the planner sends them to that unit's conductor as that unit's notes, as if picked on the card

#### Scenario: Two fine, one with notes
- **WHEN** the user picks one unit of three under "which need notes?" and writes notes
- **THEN** only that unit is constructed again, with the notes, and the other two are fine

### Requirement: Notes reach the unit's conductor
The planner SHALL send the user's notes, verbatim, to the conductor of the team of each unit picked as needing notes. A unit not picked SHALL be fine.

#### Scenario: Fine
- **WHEN** the user does not pick a unit under "which need notes?"
- **THEN** nothing about the unit changes, and its change is no longer due

### Requirement: Notes amend a unit in flight with no re-approval
For a unit that has not merged, its conductor SHALL run construct again with the notes, as an amendment, waiting while that unit's construct is running until it settles. Once that construct has committed, the unit SHALL go on from its tasks with no approval asked, and its revised change SHALL be due for the next batch. A merged unit SHALL NOT be amended: a defect SHALL become a fix on the bolt, and new work the planner's.

#### Scenario: Notes on a unit in code
- **WHEN** the user's notes on a unit of swb-2 in code arrive on a batch card
- **THEN** swb-2's conductor runs construct again with the notes, and once it commits the unit's code goes on with nobody asked to approve it

#### Scenario: Notes on a merged unit
- **WHEN** the user's notes name a defect in a unit that has merged into its bolt
- **THEN** the unit is not amended, and its conductor starts a fix with the user's words

### Requirement: A bolt lands only once every unit's latest change has been in a batch
A bolt SHALL be offered for landing only once every unit's latest change, the commit its last construct left, has appeared in a batch. When a bolt is otherwise ready to land and some unit's latest change has not, a batch SHALL be due at once for those units, and the landing card SHALL name them. A landing SHALL be refused while any of them remains outside a batch.

#### Scenario: A late amendment
- **WHEN** every unit of a bolt has merged and its proof is clean, and one unit's change was constructed again after the last batch
- **THEN** a batch holding that unit is due at once, the landing card names the unit, and the landing is refused until the batch has been posted
