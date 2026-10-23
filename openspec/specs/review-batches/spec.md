# review-batches Specification

## Purpose
The user reads a partition's constructed and amended changes in batches, after building has started: each construct makes its change due, the planner starts the partition's reviewer when a batch is due and posts the batch as one card, and the notes the user sends from it reach each unit's conductor, which runs construct again with no approval asked (`briefs.12`, record 0014).

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
A batch card SHALL be a notice that asks nothing, which the user sends back with one tap. Its title SHALL say what the batch is about, from its units' subjects, with the batch's number after; its summary SHALL open "N changes to read, nothing to approve", and its words SHALL say that notes go in the reading session or in the card's own note naming the change; it SHALL carry each unit's name, team and opening paragraph as inline Markdown on its face, and one link to one plannotator session holding the summary whole and every change. The batch's notes SHALL be the session's annotations and the card's own note. The card SHALL close on the tap or on the session's send, whichever is first, and the session SHALL end with it.

#### Scenario: The user drills in
- **WHEN** the user opens a batch card holding three units
- **THEN** the card says what it is, that there is nothing to answer and where notes go, shows each unit's paragraph as prose, and has one link, which opens the summary and the three changes as one review

#### Scenario: Every unit fine
- **WHEN** the user sends a batch card of six units back with one tap and no note, having sent nothing from the session
- **THEN** the card is closed, no unit is constructed again, and the user picked and typed nothing

#### Scenario: Notes written in a session
- **WHEN** the user annotates `x1`'s design and `z1`'s tasks in the batch's session and sends the annotations
- **THEN** the planner's wait returns them, sends each unit's annotations to its conductor at once, and the card is closed

#### Scenario: Two fine, one with notes
- **WHEN** the user writes notes for one unit of three in the card's note, naming it, and sends the card back
- **THEN** only that unit is constructed again, with the notes, and the other two are fine

#### Scenario: The session approved
- **WHEN** the user approves the batch's session without annotations
- **THEN** nothing is sent for any unit, and the card is closed "Read; no notes"

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

### Requirement: A bolt lands only once every unit's latest change has been in a batch the user has answered
A bolt SHALL be offered for landing only once every unit's latest change, the commit its last construct left, has been in a batch whose card the user has answered: sent back with a tap, sent from its reading session, or closed in Pending You, as crew records the card's close. When a bolt is otherwise ready to land and some unit's latest change has not been in a batch, a batch SHALL be due at once for those units, and the bolt's landing row SHALL name them. While a batch holding a unit's latest change waits on the user's answer, the landing row SHALL name that batch. No landing card SHALL be raised, and the row SHALL carry no word to land, until every unit's latest change has been in a batch the user has answered, and `crew bolt land` SHALL be refused while any unit's latest change remains outside a batch. A card Pending You lost to its owner SHALL be no answer. A chore SHALL be in no batch and SHALL hold no landing.

#### Scenario: A late amendment
- **WHEN** every unit of a bolt has merged and its verification is green, and one unit's change was constructed again after the last batch
- **THEN** a batch holding that unit is due at once, the landing row names the unit, and no landing card is raised until the batch's card has been answered

#### Scenario: A batch card unanswered
- **WHEN** every unit of bolt `y` has merged and its verification is green, and batch 7, whose card the user has not answered, holds one unit's latest change
- **THEN** `y`'s landing row says it lands once you have answered batch 7, carries no command, and no landing card is raised for `y`

#### Scenario: The batch card answered
- **WHEN** the user sends batch 7's card back with no notes
- **THEN** the next rail read on `y`'s team's host raises `y`'s landing card, and its row carries the word to land

#### Scenario: Notes send a unit back
- **WHEN** the user's notes on batch 7 send one of `y`'s units back to construct, and its new change is in no batch yet
- **THEN** `y`'s landing row names that unit as due a batch, and no landing card is raised until the batch that holds its new change has been answered

### Requirement: crew raises a batch's one card
When the reviewer delivers a batch's summary and the planner's `crew review --wait` returns, crew SHALL start the batch's one reading session and raise its one card in the planner's name, keyed `batch/<n>`, as `rail-cards` says a batch's card is; the planner SHALL write nothing of it and post nothing. `crew card wait batch/<n>` SHALL give the planner the notes and close the card.

#### Scenario: A summary delivered
- **WHEN** the reviewer delivers batch 7's summary of four changes and the planner's wait returns
- **THEN** batch 7's session is started, and one card keyed `batch/7` is open in the planner's name

### Requirement: A batch that waits on nothing is closed by crew
A batch SHALL wait on nothing once each of its units has landed, has been dropped from the plan since the batch was made, or is held by a later batch. crew SHALL read such a batch closed from the run record at every read of the rail and the board, so it is no row and crew raises no card for it; the rail's sweep SHALL record crew's close once, in the planner's name, saying why, and SHALL withdraw a card open under its key with the same words. A batch with any other unit SHALL stay a row until its card closes.

#### Scenario: Every unit has landed
- **WHEN** batch 3 holds `x1` and `x2`, no card of it was ever closed, and the bolt holding both has landed
- **THEN** the rail and the board have no row for batch 3, no card is posted for it, and the next rail read on the partition's main-level host records crew's close of `batch/3` in the planner's name, "its batch waits on nothing: x1 and x2 have landed"

#### Scenario: A later batch holds the unit
- **WHEN** batch 5 holds `x1`, the user's notes on it were given in the planner's pane, `x1` was constructed again, and batch 7 holds its new change
- **THEN** batch 5 is no row, crew's close of `batch/5` says "its batch waits on nothing: batch 7 holds a newer change of x1", and batch 7 is a row until its own card closes

#### Scenario: One unit landed and another held again
- **WHEN** batch 6 holds `x1`, which has landed, and `y1`, which batch 8 holds again
- **THEN** batch 6 is no row, and crew's close says "its batch waits on nothing: x1 has landed; batch 8 holds a newer change of y1"

#### Scenario: A unit dropped
- **WHEN** batch 4 holds `x1` and `x2`, `x1` has landed, and `x2` is dropped from the plan after batch 4 was made, by `crew unit drop`, by a proposal the user approved, or with its bolt
- **THEN** batch 4 is no row, and crew's close says "its batch waits on nothing: x1 has landed; x2 was dropped"

#### Scenario: A unit dropped and added again before the batch
- **WHEN** unit `x1` was dropped, a unit of the same name was added again and constructed, and batch 10 then holds its change
- **THEN** the earlier drop does not close batch 10, which stays a row until its card closes, or until `x1` lands, is dropped again or a later batch holds it

#### Scenario: A bolt dropped with its units queued
- **WHEN** batch 11 holds `x1`, and `x1`'s bolt is dropped with `--requeue`, so `x1` goes back to the queue
- **THEN** `x1` was not dropped, and batch 11 stays a row until its card closes or a later batch holds `x1`

#### Scenario: One unit still waits on the user
- **WHEN** batch 9 holds `x1`, which has landed, and `y1`, which has not landed, has not been dropped and no later batch holds
- **THEN** batch 9 is a row as it is today, and its card is raised and closed as before

#### Scenario: Its card is already open
- **WHEN** crew posted `batch/12`'s card in the planner's name on the main-level host, and every unit of batch 12 has landed
- **THEN** the next rail read there withdraws the card "its batch waits on nothing: …" with the words of crew's close, records both, and says so in its sweep's lines

#### Scenario: The unit moves on again
- **WHEN** batch 7 held `x1` again after batch 5, and `x1` is then constructed a third time, its newest change in no batch yet
- **THEN** batch 5 stays closed and is no row, and `x1`'s newest change is due for the next batch

#### Scenario: Read again after the close
- **WHEN** crew's close of `batch/3` is recorded and the rail is read again
- **THEN** no second close is recorded, and nothing is posted under `batch/3`

#### Scenario: crew's close is not the user's answer
- **WHEN** batch 5 is closed by crew because batch 7 holds `x1`'s newer change, and batch 7's card is unanswered
- **THEN** `x1`'s bolt's landing row says it lands once you have answered batch 7, as before

#### Scenario: The record did not answer whole
- **WHEN** the partition's branch cannot be read, so its run record cannot be
- **THEN** the sweep records no close for any batch, says the partition was not swept, and names the branch

#### Scenario: A host does not answer
- **WHEN** macbook-pro, which holds a wldn operator session, does not answer a rail read
- **THEN** each batch is closed as far as the entries on `wldn/main` show it, as when every host answers

### Requirement: A batch is reckoned from the partition's branch alone
Whether a batch is due, what a review holds, and whether every unit's latest change of a bolt has been in a batch, SHALL be read from the run record on the partition's branch alone, asking no host for it. A host that does not answer SHALL hold none of them. When the branch cannot be read, each SHALL be refused naming the branch, as crew can't tell then which changes have been in a batch.

#### Scenario: The laptop asleep at a conductor's wait
- **WHEN** a wldn conductor's wait on chuck-herdr-alpha runs while macbook-pro, which holds a wldn operator session, does not answer, and five changes are due
- **THEN** the wait finds the batch due and the planner is told, and macbook-pro is not asked

#### Scenario: A review while the laptop is asleep
- **WHEN** the planner runs `crew review wldn` while macbook-pro does not answer and a batch is due
- **THEN** the reviewer is started on the batch's due changes, and no earlier batch's summary is returned in its place

#### Scenario: A landing while the laptop is off
- **WHEN** `crew bolt land` runs on mac-studio for a bolt whose every unit's latest change has been in a batch the user answered, while macbook-pro is off the tailnet
- **THEN** the bolt is closed as landed, and nothing names macbook-pro

#### Scenario: The branch cannot be read
- **WHEN** a conductor's wait runs while `wldn/main` cannot be fetched
- **THEN** whether a batch is due is not reckoned, and the wait says crew can't tell which changes have been in a batch, naming `wldn/main` and why
