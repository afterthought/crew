## ADDED Requirements

### Requirement: crew raises a batch's one card
When the reviewer delivers a batch's summary and the planner's `crew review --wait` returns, crew SHALL start the batch's one reading session and raise its one card in the planner's name, keyed `batch/<n>`, as `rail-cards` says a batch's card is; the planner SHALL write nothing of it and post nothing. `crew card wait batch/<n>` SHALL give the planner the notes and close the card.

#### Scenario: A summary delivered
- **WHEN** the reviewer delivers batch 7's summary of four changes and the planner's wait returns
- **THEN** batch 7's session is started, and one card keyed `batch/7` is open in the planner's name

## MODIFIED Requirements

### Requirement: A batch card is read and answered in Pending You
A batch card SHALL be a notice that asks nothing, which the user sends back with one tap. It SHALL say first what it is, then that there is nothing to answer and that notes go in the reading session or in the card's own note naming the change, and SHALL carry each unit's name, team and opening paragraph as prose that wraps on a phone, and one link to one plannotator session holding the summary whole and every change. The batch's notes SHALL be the session's annotations and the card's own note. The card SHALL close on the tap or on the session's send, whichever is first, and the session SHALL end with it.

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

## REMOVED Requirements

### Requirement: The planner posts a batch as one card
**Reason**: crew raises it when the reviewer delivers the summary; the planner reads the notes (record 0031).
