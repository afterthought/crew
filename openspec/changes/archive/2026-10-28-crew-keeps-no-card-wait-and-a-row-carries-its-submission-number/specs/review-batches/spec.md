## MODIFIED Requirements

### Requirement: A batch card is read and answered in Pending You
A batch card SHALL be a notice that asks nothing, which the user sends back with one tap. Its title SHALL say what the batch is about, from its units' subjects, with the batch's number after. Its summary SHALL open "N changes to read, nothing to approve", and its words SHALL say that notes go in the reading session or in the card's own note naming the change. It SHALL carry each unit's name, team and opening paragraph as inline Markdown on its face, and one link to one plannotator session holding the summary whole and every change. The batch's notes SHALL be the session's annotations, the card's own note, and the user's own words when they answer the batch in a main-level pane. The card SHALL close on the planner's read of the tap or the session's send, on the rail's refresh of a send with no words, or on the user's answer in a main-level pane, whichever is first, and the session SHALL end with it.

#### Scenario: The user drills in
- **WHEN** the user opens a batch card holding three units
- **THEN** the card says what it is, that there is nothing to answer and where notes go, shows each unit's paragraph as prose, and has one link, which opens the summary and the three changes as one review

#### Scenario: Every unit fine
- **WHEN** the user sends a batch card of six units back with one tap and no note, having sent nothing from the session, and the planner, woken, runs `crew card read batch/<n>`
- **THEN** the card is closed, no unit is constructed again, and the user picked and typed nothing

#### Scenario: Notes written in a session
- **WHEN** the user annotates `x1`'s design and `z1`'s tasks in the batch's session and sends the annotations, and the planner, told by the rail's refresh, runs `crew card read batch/<n>`
- **THEN** the read prints them, the planner sends each unit's annotations to its conductor at once, and the card is closed

#### Scenario: Two fine, one with notes
- **WHEN** the user writes notes for one unit of three in the card's note, naming it, and sends the card back
- **THEN** only that unit is constructed again, with the notes, and the other two are fine

#### Scenario: The session approved
- **WHEN** the user approves the batch's session without annotations
- **THEN** nothing is sent for any unit, and the card is closed "Read; no notes", by the planner's read or the next refresh, whichever is first

#### Scenario: Answered in a pane
- **WHEN** the user writes in the planner's pane "Batch 9: x1's design should name the host" and the planner runs `crew card answer batch/9` with those words
- **THEN** batch 9's card is closed as answered, and those words are batch 9's note

### Requirement: crew raises a batch's one card
When the reviewer delivers a batch's summary and the planner's `crew review --wait` returns, crew SHALL start the batch's one reading session and raise its one card in the planner's name, keyed `batch/<n>`, as `rail-cards` says a batch's card is; the planner SHALL write nothing of it and post nothing. The planner's `crew card read batch/<n>` SHALL give it the notes and close the card.

#### Scenario: A summary delivered
- **WHEN** the reviewer delivers batch 7's summary of four changes and the planner's wait returns
- **THEN** batch 7's session is started, and one card keyed `batch/7` is open in the planner's name

### Requirement: A pane answer closes the batch's card and offers its bolts for landing
Once a batch is answered in a pane, crew SHALL treat it exactly as a batch whose card the user tapped. The command SHALL close the batch's card as answered, naming the user's words, when the planner holds the card open on the host where the command runs. When no card is held there, because it was posted from a host the main level has left, the batch SHALL be answered all the same. Its card SHALL be closed as answered, saying in whose pane and when, by the rail's sweep on the host that holds it, when it is found or raised again. The planner's `crew card read batch/<n>` after the answer SHALL say in whose pane it was given, closing the card it holds and ending the batch's reading session. A bolt waiting on the batch SHALL be offered for landing as after a tap: the next rail read on its team's host raises its landing card once every unit's latest change has been in an answered batch.

#### Scenario: The card held on this host
- **WHEN** the planner, on deneb, holds batch 16's card open, and answers batch 16 in its pane
- **THEN** the card is closed as answered with the user's words, and the batch's reading session ends

#### Scenario: The card on a host the main level has left
- **WHEN** batch 13's card was posted from mac-studio, the planner on deneb holds none, and the planner answers batch 13 in its pane
- **THEN** batch 13 is answered, the command says its card is held on mac-studio and is closed there by the rail's sweep, and the next rail read on mac-studio closes it "Answered in swancloud-planner's pane"

#### Scenario: The bolt it held is offered
- **WHEN** bolt `y`'s only unanswered batch is 13, every unit has merged, and its verification is green, and batch 13 is answered in the planner's pane
- **THEN** the next rail read on `y`'s team's host raises `y`'s landing card, and its row carries the word to land

#### Scenario: The planner's wait was running
- **WHEN** the operator answers batch 16 in its pane, and the planner then runs `crew card read batch/16`
- **THEN** the read says batch 16 was answered in swancloud-operator's pane, without the words, and the card it holds is closed

### Requirement: A batch whose reading session is sent is read, with or without its card
When the user sends a batch's reading session, approved or annotated, crew SHALL record the batch read whether or not the planner holds a card of it on the main level's host: at the planner's `crew card read batch/<n>`, which prints the notes as it does when it closes the card, and, for a send with no annotations, at the rail's refresh on that host. When it closes no card there, because none is held, the card is lost, or Pending You refused its close, crew SHALL record its own close of the batch in the planner's name, saying what was read ("Read; no notes", "Read; 2 notes sent to their teams"). A batch recorded read so SHALL be closed for every read of batches: no row on the rail, no batch named on a landing row, no card raised for it, until a newer card is posted under its key. A send with annotations SHALL be recorded read only by the planner's read, so no bolt lands before its notes are given.

#### Scenario: Sent with no card on the main level's host
- **WHEN** batch 13's card was posted from mac-studio, the planner's session runs on deneb with batch 13's reading, and the user approves the session with no annotations
- **THEN** the next refresh on deneb, or the planner's `crew card read batch/13` if it comes first, records crew's close of `batch/13` in the planner's name "Read; no notes", ends the session, and the rail no longer shows batch 13

#### Scenario: Sent while the card is lost
- **WHEN** batch 13's card is recorded lost, and the user then sends the session with two annotations, and the planner runs `crew card read batch/13`
- **THEN** the read prints both annotations as written and records crew's close of `batch/13` "Read; 2 notes sent to their teams"

#### Scenario: Sent while the card's close is refused
- **WHEN** the user sends batch 13's session, the planner runs `crew card read batch/13`, and Pending You refuses the close of its card
- **THEN** crew records its close of `batch/13` with what was read, and the card, its row gone, is withdrawn by a later rail read

#### Scenario: Notes sent while the planner is down
- **WHEN** the user sends batch 13's session with two annotations while the planner is not up, and the refresh runs
- **THEN** batch 13 is not recorded read, its row stays, no bolt it holds is offered for landing, and once up the planner is told to run `crew card read batch/13`
