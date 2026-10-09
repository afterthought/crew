# Spec Delta

## ADDED Requirements

### Requirement: Each construct makes a unit's change due for review
A unit's change SHALL be due for the user's review each time a construct stage of the unit commits, the first construct and every construct run again. A change SHALL stop being due once a batch has included it at the commit its construct left.

#### Scenario: An amended change
- **WHEN** a unit already in a batch is constructed again with the user's feedback
- **THEN** its change is due again, and counts toward the next batch

### Requirement: Constructed changes are reviewed in batches
A team SHALL have a batch setting, a count N and a number of hours T, read from the teams file. A batch SHALL be due on the conductor's wait when N changes are due, or when T hours have passed since the team's last batch and at least one change is due, whichever comes first.

#### Scenario: The count is reached
- **WHEN** a team's setting is 5 and 4 hours, and the fifth change since its last batch is constructed an hour after that batch
- **THEN** a batch is due, holding those five changes

#### Scenario: The time is reached
- **WHEN** two changes have been constructed since a team's last batch, four hours ago
- **THEN** a batch is due, holding those two

#### Scenario: Nothing due
- **WHEN** four hours have passed since the last batch and no change has been constructed since
- **THEN** no batch is due

### Requirement: A batch is summarized by a fresh reviewer agent
When a batch is due, crew SHALL start a fresh reviewer agent, which reads each due change whole and writes one summary file: for each unit, what the change does, the decisions it took, its risks, its Touches, and anything the user would likely care about. The batch SHALL end at that file, its deliverable. The run record SHALL name the batch, each unit it holds and the commit each unit's change was read at.

#### Scenario: A batch of three
- **WHEN** a batch holds three units' changes
- **THEN** the reviewer's file holds one section for each of the three, and the run record names the three units and their commits

### Requirement: A batch is one card with a question for each unit
The conductor SHALL post each batch as one Pending You card, keyed to the batch's rail row, asking for each unit whether its change is fine or what the user wants changed. The card SHALL carry each unit's summary and attach or link each unit's whole OpenSpec change, its proposal, design, specs and tasks, so the user reads them and answers in Pending You. No plannotator session SHALL be started for a batch card. A batch's answers SHALL be the user's; no agent SHALL answer a batch card.

#### Scenario: The user drills in
- **WHEN** the user opens a batch card holding three units
- **THEN** the card shows each unit's summary, and each unit's whole change opens from the card in Pending You

#### Scenario: One answer for each unit
- **WHEN** the user answers a batch of three units, two fine and one with feedback
- **THEN** the conductor acts on each unit's answer, and only the third unit is constructed again

### Requirement: Feedback amends a unit in flight with no re-approval
Feedback on a unit that has not merged SHALL run construct again on it with the user's words, at whatever stage it is in, as an amendment. Once that construct has committed, the unit SHALL go on from its tasks with no approval asked, and its revised change SHALL be due for the next batch. Feedback on a unit whose construct is running SHALL wait until that construct settles. Feedback on a unit that has merged SHALL NOT amend it: a defect SHALL become a fix on the bolt, and new work the planner's.

#### Scenario: Feedback on a unit in code
- **WHEN** the user's feedback on a unit in code arrives on a batch card
- **THEN** construct runs again with the user's words, and once it commits the unit's code goes on with nobody asked to approve it

#### Scenario: Feedback on a merged unit
- **WHEN** the user's feedback names a defect in a unit that has merged into the bolt
- **THEN** the unit is not amended, and the conductor starts a fix with the user's words

#### Scenario: Fine
- **WHEN** the user answers that a unit's change is fine
- **THEN** nothing about the unit changes, and its change is no longer due

### Requirement: A bolt lands only once every unit's latest change has been in a batch
A bolt SHALL be offered for landing only once every unit's latest change, the commit its last construct left, has appeared in a batch. When a bolt is otherwise ready to land and some unit's latest change has not, a batch SHALL be due at once for those units, and the landing card SHALL name them. A landing SHALL be refused while any of them remains outside a batch.

#### Scenario: A late amendment
- **WHEN** every unit of a bolt has merged and its proof is clean, and one unit's change was constructed again after the last batch
- **THEN** a batch holding that unit is due at once, the landing card names the unit, and the landing is refused until the batch has been posted
