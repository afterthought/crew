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
The reviewer SHALL read each due change whole and write one summary file holding, for each unit, its team, a short opening paragraph saying what the change does and what the user would most care about, then the decisions it took, its risks, what it touches named in words, and anything the user would likely care about, as paragraphs and plain lists with no code block, no table and no path. The batch SHALL end at that file, its deliverable, and the reviewer SHALL write nothing else. The run record SHALL name the batch, each unit it holds and the commit each unit's change was read at.

#### Scenario: A batch of three
- **WHEN** a batch holds three units' changes from two teams
- **THEN** the reviewer's file holds one section for each of the three, naming its team and opening with its paragraph, and the run record names the three units and their commits

#### Scenario: What a change touches
- **WHEN** the reviewer summarizes a change whose Touches lists the card hook and its test
- **THEN** its section names them in words, with no code block and no path

### Requirement: A batch card is read and answered in Pending You
A batch card SHALL be a notice that asks nothing, which the user sends back with one tap. It SHALL say first, in plain words, what it is: the partition's batch of the changes constructed or amended since the last batch, already being built, read for notes and approving nothing; then that there is nothing to answer, and that notes go in the batch's reading session or in the card's own note naming the change. It SHALL carry each unit's name, team and opening paragraph as prose that wraps on a phone, never in a code block or an attachment, and one link, to one plannotator session holding the reviewer's summary whole and every unit's whole change. The batch's notes SHALL be the annotations the user sends from that session and the card's own note. A decision in the session SHALL NOT answer or withdraw the card. The session SHALL end when the card closes.

#### Scenario: The user drills in
- **WHEN** the user opens a batch card holding three units
- **THEN** the card says what it is, that there is nothing to answer and where notes go, shows each unit's paragraph as prose, and has one link, which opens the summary and the three changes as one review

#### Scenario: Every unit fine
- **WHEN** the user sends a batch card of six units back with one tap and no note, having sent nothing from the session
- **THEN** the card is answered, no unit is constructed again, and the user picked and typed nothing

#### Scenario: Notes written in a session
- **WHEN** the user annotates `x1`'s design and `z1`'s tasks in the batch's session and sends the annotations
- **THEN** the planner sends each unit's annotations to its conductor at once, and the card stays open for the user

#### Scenario: Two fine, one with notes
- **WHEN** the user writes notes for one unit of three in the card's note, naming it, and sends the card back
- **THEN** only that unit is constructed again, with the notes, and the other two are fine

#### Scenario: The session approved
- **WHEN** the user approves the batch's session without annotations
- **THEN** nothing is sent for any unit, and the card stays open for the user

### Requirement: Notes reach the unit's conductor
The planner SHALL send the user's notes, word for word, to the conductor of the team of each unit they speak of: the session's annotations, by the file each is on or what it says, and the card's own note, by the unit it names or what it says of a unit's summary, each message naming every unit it went to. Words that speak of no unit the planner can tell SHALL go to every unit's conductor, saying so. The planner SHALL NOT split, reword or summarize the user's words. A unit of which no annotation and no note speaks SHALL be fine. The card's closing line SHALL name the units notes went to.

#### Scenario: Fine
- **WHEN** the user sends no annotation on a unit's files and the card's note does not speak of it
- **THEN** nothing about the unit changes, and its change is no longer due

#### Scenario: One note for two units
- **WHEN** the user's note on the card speaks of `x1` and `z1`, of teams swb-1 and atl-1
- **THEN** swb-1's conductor gets the note word for word as `x1`'s notes, atl-1's conductor gets it as `z1`'s, each message names both units, and the card's closing line names `x1` and `z1`

#### Scenario: Words that name no unit
- **WHEN** the user's note on a card of three units speaks of none of them that the planner can tell
- **THEN** each of the three units' conductors gets the note word for word, saying it named no unit

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

### Requirement: The planner posts a batch as one card
The planner SHALL post each batch as one partition card, keyed `batch/<n>`, naming every unit the batch holds, however many; a batch SHALL NOT be split across cards. A batch's answer SHALL be the user's; no agent SHALL answer a batch card.

#### Scenario: Seven changes due
- **WHEN** a batch holds seven changes
- **THEN** the planner posts one card for it, naming all seven units
