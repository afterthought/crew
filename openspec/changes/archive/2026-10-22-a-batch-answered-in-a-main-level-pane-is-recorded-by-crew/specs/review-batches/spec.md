## ADDED Requirements

### Requirement: A batch is answered by the user's own words in a main-level pane
A batch SHALL also be answered by the user's own words in the planner's pane or the operator's pane of its partition. The agent in that pane SHALL run `crew card answer batch/<n> --excerpt "<the user's words>"`. crew SHALL record the batch answered only when it finds the words in that agent's own live session transcript, on the host where the command runs, in a record the session received and that crew reads as the user's under `signals.5`. That is typing in the pane, or a `crew tell` from `<user>@<host>`. A later echo of the same words, in a tool's output or a tell, SHALL NOT hide the user's record. crew SHALL refuse the command, recording no answer, in each of these cases:
- the words are not in the transcript, or are only in what the agent wrote itself;
- the record holding them is a tool's output, crew's own message, or another agent's tell;
- crew cannot read the transcript, or cannot tell that it is the live session's;
- the caller is not that partition's planner or operator;
- the run record holds no batch `n`;
- the batch was already answered, by a tap, its reading session's send, or a pane;
- the batch waits on nothing.

The answer SHALL be one run-record entry, `batch.answer`, on `batch/<n>`. It names the batch, the caller, its session, the transcript record the words were read from, and the words' length, and holds none of the words (`record.3`). The answer SHALL close every card key of batch `n` for good: a card posted under one of those keys afterwards does not open the batch again. Answering several batches in one sentence SHALL take one command per batch.

#### Scenario: Typed in the planner's pane
- **WHEN** the user types "Batch 13 is fine, approve it" in swancloud-planner's pane, and the planner runs `crew card answer batch/13 --excerpt "Batch 13 is fine, approve it"`
- **THEN** batch 13 is recorded answered, with no words in the run record, and the rail and the board have no row for it

#### Scenario: Through the rail's answer command
- **WHEN** the user runs `crew tell swancloud-planner "On batch 14: fine"` at a shell, and the planner runs `crew card answer batch/14 --excerpt "On batch 14: fine"`
- **THEN** batch 14 is recorded answered, since a tell from `<user>@<host>` is the user's

#### Scenario: The agent's own words
- **WHEN** the planner writes "the user approved batch 15" in its own reply and runs `crew card answer batch/15 --excerpt "the user approved batch 15"`
- **THEN** the command is refused, saying the words are not in a record the session received, and batch 15 is not answered

#### Scenario: Words another agent passed on
- **WHEN** swancloud-operator tells the planner "The user says batch 15 is fine", and the planner runs the command with those words
- **THEN** the command is refused, naming swancloud-operator as the one who said them, and batch 15 is not answered

#### Scenario: Already answered on its card
- **WHEN** the user tapped batch 13's card, and then the planner runs `crew card answer batch/13` with the user's words in its pane
- **THEN** the command is refused, saying batch 13 was answered already, and nothing is recorded

#### Scenario: Three batches in one sentence
- **WHEN** the user writes, in the planner's pane, one sentence approving batches 13, 14 and 15
- **THEN** the planner runs the command once for each batch with that sentence, and each batch is recorded answered on its own

### Requirement: A pane answer closes the batch's card and offers its bolts for landing
Once a batch is answered in a pane, crew SHALL treat it exactly as a batch whose card the user tapped. The command SHALL close the batch's card as answered, naming the user's words, when the planner holds the card open on the host where the command runs. When no card is held there, because it was posted from a host the main level has left, the batch SHALL be answered all the same. Its card SHALL be closed as answered, saying in whose pane and when, by the rail's sweep on the host that holds it, when it is found or raised again. The planner's wait on the batch, `crew card wait batch/<n>`, SHALL end on the answer, saying in whose pane it was given, closing the card it holds and ending the batch's reading session. A bolt waiting on the batch SHALL be offered for landing as after a tap: the next rail read on its team's host raises its landing card once every unit's latest change has been in an answered batch.

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
- **WHEN** the planner's `crew card wait batch/16` is running, and the operator answers batch 16 in its pane
- **THEN** the wait ends, saying batch 16 was answered in swancloud-operator's pane, and the card it holds is closed

## MODIFIED Requirements

### Requirement: A batch card is read and answered in Pending You
A batch card SHALL be a notice that asks nothing, which the user sends back with one tap. Its title SHALL say what the batch is about, from its units' subjects, with the batch's number after. Its summary SHALL open "N changes to read, nothing to approve", and its words SHALL say that notes go in the reading session or in the card's own note naming the change. It SHALL carry each unit's name, team and opening paragraph as inline Markdown on its face, and one link to one plannotator session holding the summary whole and every change. The batch's notes SHALL be the session's annotations, the card's own note, and the user's own words when they answer the batch in a main-level pane. The card SHALL close on the tap, on the session's send or on the user's answer in a main-level pane, whichever is first, and the session SHALL end with it.

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

#### Scenario: Answered in a pane
- **WHEN** the user writes in the planner's pane "Batch 9: x1's design should name the host" and the planner runs `crew card answer batch/9` with those words
- **THEN** batch 9's card is closed as answered, and those words are batch 9's note

### Requirement: Notes reach the unit's conductor
The planner SHALL send the user's notes, word for word, to the conductor of the team of each unit they speak of: the session's annotations, by the file each is on or what it says; the card's own note, by the unit it names or what it says of a unit's summary; and the user's words that answered the batch in a main-level pane, by the unit they name or what they say of one. Each message SHALL name every unit it went to. When the operator answered the batch in its pane, crew SHALL tell the planner the user's words, saying the batch was answered in the operator's pane, and the operator SHALL send none itself. Words that speak of no unit the planner can tell SHALL go to every unit's conductor, saying so. The planner SHALL NOT split, reword or summarize the user's words. A unit of which no annotation and no note speaks SHALL be fine. The card's closing line SHALL name the units notes went to.

#### Scenario: Fine
- **WHEN** the user sends no annotation on a unit's files and the card's note does not speak of it
- **THEN** nothing about the unit changes, and its change is no longer due

#### Scenario: One note for two units
- **WHEN** the user's note on the card speaks of `x1` and `z1`, of teams swb-1 and atl-1
- **THEN** swb-1's conductor gets the note word for word as `x1`'s notes, atl-1's conductor gets it as `z1`'s, each message names both units, and the card's closing line names `x1` and `z1`

#### Scenario: Words that name no unit
- **WHEN** the user's note on a card of three units speaks of none of them that the planner can tell
- **THEN** each of the three units' conductors gets the note word for word, saying it named no unit

#### Scenario: Answered in the operator's pane
- **WHEN** the user writes in swancloud-operator's pane "Batch 9: z1's tasks miss the rail test" and the operator runs `crew card answer batch/9` with those words
- **THEN** crew tells swancloud-planner those words, saying batch 9 was answered in swancloud-operator's pane, and the planner sends them word for word to `z1`'s conductor

### Requirement: A bolt lands only once every unit's latest change has been in a batch the user has answered
A bolt SHALL be offered for landing only once every unit's latest change, the commit its last construct left, has been in a batch the user has answered. A batch is answered when its card was sent back with a tap, sent from its reading session or closed in Pending You, as crew records the card's close, or when the user answered it in their own words in a main-level pane, as crew records from that session's transcript. When a bolt is otherwise ready to land and some unit's latest change has not been in a batch, a batch SHALL be due at once for those units, and the bolt's landing row SHALL name them. While a batch holding a unit's latest change waits on the user's answer, the landing row SHALL name that batch. No landing card SHALL be raised, and the row SHALL carry no word to land, until every unit's latest change has been in a batch the user has answered. `crew bolt land` SHALL be refused while any unit's latest change remains outside a batch. A card Pending You lost to its owner SHALL be no answer, and neither SHALL an agent's own words or another agent's tell of what the user said. A chore SHALL be in no batch and SHALL hold no landing.

#### Scenario: A late amendment
- **WHEN** every unit of a bolt has merged and its verification is green, and one unit's change was constructed again after the last batch
- **THEN** a batch holding that unit is due at once, the landing row names the unit, and no landing card is raised until the batch's card has been answered

#### Scenario: A batch card unanswered
- **WHEN** every unit of bolt `y` has merged and its verification is green, and batch 7, whose card the user has not answered, holds one unit's latest change
- **THEN** `y`'s landing row says it lands once you have answered batch 7, carries no command, and no landing card is raised for `y`

#### Scenario: The batch card answered
- **WHEN** the user sends batch 7's card back with no notes
- **THEN** the next rail read on `y`'s team's host raises `y`'s landing card, and its row carries the word to land

#### Scenario: The batch answered in a pane
- **WHEN** the user answers batch 7 in their own words in the planner's pane, and the planner records it with `crew card answer batch/7`
- **THEN** the next rail read on `y`'s team's host raises `y`'s landing card, and its row carries the word to land

#### Scenario: Notes send a unit back
- **WHEN** the user's notes on batch 7 send one of `y`'s units back to construct, and its new change is in no batch yet
- **THEN** `y`'s landing row names that unit as due a batch, and no landing card is raised until the batch that holds its new change has been answered
