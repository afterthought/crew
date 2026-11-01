# review-batches Specification

## Purpose
The user reads a partition's constructed and amended changes in batches, after building has started: each construct makes its change due, the planner starts the partition's reviewer when a batch is due and posts the batch as one card, and the notes the user sends from it reach each unit's conductor, which runs construct again with no approval asked (`briefs.12`, record 0014).

## Requirements

### Requirement: Each construct makes a unit's change due for review
A unit's change SHALL be due for the user's review each time a construct stage of the unit commits, the first construct and every construct run again. A change SHALL stop being due once a batch has included it at the commit its construct left.

#### Scenario: An amended change
- **WHEN** a unit already in a batch is constructed again with the user's notes
- **THEN** its change is due again, and counts toward the next batch

### Requirement: The planner starts the partition's reviewer
When a batch is due, crew SHALL tell the partition's planner once, and the planner SHALL start the reviewer: a main-level role, run fresh for each batch in its own tab of the main level's workspace, beside the planner, on the main level's host. Where the partition runs its reviewer as its kind, `crew review <label>` SHALL instead write an ask of the reviewer carrying the batch, as the reviewer's first message carries it today, open no tab and start no agent, and `crew review <label> --wait` SHALL refuse, saying the batch's delivery reaches the planner as an ask.

#### Scenario: A batch is due
- **WHEN** a conductor's wait finds a batch due in the wldn partition
- **THEN** wldn-planner is told once, and starts `wldn-reviewer` in the `wldn` workspace

#### Scenario: A reviewer that runs as its kind
- **WHEN** madswan runs its reviewer as its kind and the planner's run runs `crew review madswan`
- **THEN** an ask of the reviewer holds the batch's changes, how to read each and the file to write, no tab is opened, and no reviewer is started by crew

#### Scenario: Waiting on a reviewer that runs as its kind
- **WHEN** madswan runs its reviewer as its kind and `crew review madswan --wait` runs
- **THEN** it refuses, saying the batch's delivery reaches the planner as an ask, and waits on nothing

### Requirement: The reviewer summarizes a batch
The reviewer SHALL read each due change whole and write one summary file holding, for each unit, its bolt, a short opening paragraph saying what the change does and what the user would most care about, then the decisions it took, its risks, what it touches named in words, and anything the user would likely care about, as paragraphs and plain lists with no code block, no table and no path. The batch SHALL end at that file, its deliverable, and the reviewer SHALL write nothing else. The run record SHALL name the batch, each unit it holds and the commit each unit's change was read at.

#### Scenario: A batch of three
- **WHEN** a batch holds three units' changes from two bolts
- **THEN** the reviewer's file holds one section for each of the three, naming its bolt and opening with its paragraph, and the run record names the three units and their commits

#### Scenario: What a change touches
- **WHEN** the reviewer summarizes a change whose Touches lists the card hook and its test
- **THEN** its section names them in words, with no code block and no path

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

### Requirement: A bolt lands only once every unit's latest change has been in a batch the user has answered
A bolt SHALL be offered for landing only once every unit's latest change, the commit its last construct left, has been in a batch the user has answered. A batch is answered when its card was sent back with a tap or closed in Pending You, as crew records the card's close, when its reading session was sent, as crew records the card's close or, with no card closed, the batch's, or when the user answered it in their own words in a main-level pane, as crew records from that session's transcript. When a bolt is otherwise ready to land and some unit's latest change has not been in a batch, a batch SHALL be due at once for those units, and the bolt's landing row SHALL name them. While a batch holding a unit's latest change waits on the user's answer, the landing row SHALL name that batch. No landing card SHALL be raised, and the row SHALL carry no word to land, until every unit's latest change has been in a batch the user has answered. `crew bolt land` SHALL be refused while any unit's latest change remains outside a batch. A card Pending You lost to its owner SHALL be no answer, and neither SHALL an agent's own words or another agent's tell of what the user said. A chore SHALL be in no batch and SHALL hold no landing.

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

#### Scenario: The batch's session sent with no card held
- **WHEN** batch 7's card is held on a host the main level has left, and the user sends batch 7's reading session on the main level's host
- **THEN** crew records batch 7 read, and the next rail read on `y`'s team's host raises `y`'s landing card

#### Scenario: Notes send a unit back
- **WHEN** the user's notes on batch 7 send one of `y`'s units back to construct, and its new change is in no batch yet
- **THEN** `y`'s landing row names that unit as due a batch, and no landing card is raised until the batch that holds its new change has been answered

### Requirement: crew raises a batch's one card
When the reviewer delivers a batch's summary and the planner's `crew review --wait` returns, crew SHALL start the batch's one reading session and raise its one card in the planner's name, keyed `batch/<n>`, as `rail-cards` says a batch's card is; the planner SHALL write nothing of it and post nothing. The planner's `crew card read batch/<n>` SHALL give it the notes and close the card.

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

### Requirement: A unit is batched once its change has landed on its bolt
A unit of a started bolt SHALL become due for review when the runner's records read it merged, its change read archived on GitHub's bolt after a fetch, and SHALL be named in its batch with its bolt at the commit of the bolt that holds it, `<unit>:<bolt>@<commit>`, its reading opening its archived folder. A note the user marks fix on such a unit SHALL reach its bolt as a fix place, by the planner's `crew fix`.

#### Scenario: Merged, then batched
- **WHEN** `a` of started `x` lands on `bolt/x` at `9f1c2ab`, its change archived there
- **THEN** `a` counts toward the partition's next batch, named `a:x@9f1c2ab`

#### Scenario: Constructed but not landed
- **WHEN** `b`'s construct has delivered and its place is in code
- **THEN** `b` is not yet due for review

### Requirement: A reviewer's run hands its batch back
`crew review delivered [--label L]`, run in the reviewer's run once each batch its turn took has its summary written, SHALL do for each what the planner's wait did once the summary was written: record the batch, start its one reading session, and raise its one card in the planner's name; and SHALL write an ask of the planner naming `batch/<n>` with the line that adopts its card. A batch whose summary file is not written SHALL be refused by name, and the others delivered.

#### Scenario: A batch delivered
- **WHEN** madswan's reviewer run has written batch 21's summary and runs `crew review delivered`
- **THEN** batch 21 is recorded, its reading session started and its card raised in madswan-planner's name, and an ask of the planner names `batch/21` and the `get_request` line that adopts it

#### Scenario: A summary not written
- **WHEN** the reviewer's turn took batches 21 and 22, only 21's summary is written, and it runs `crew review delivered`
- **THEN** batch 21 is delivered, and batch 22 is refused, naming its file

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
