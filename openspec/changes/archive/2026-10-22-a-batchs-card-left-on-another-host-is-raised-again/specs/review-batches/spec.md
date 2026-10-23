## ADDED Requirements

### Requirement: A batch whose reading session is sent is read, with or without its card
When the user sends a batch's reading session, approved or annotated, `crew card wait batch/<n>` SHALL record the batch read whether or not the planner holds a card of it on the main level's host: when it closes no card there, because none is held, the card is lost, or Pending You refused its close, crew SHALL record its own close of the batch in the planner's name, saying what was read ("Read; no notes", "Read; 2 notes sent to their teams"), and the wait SHALL print the notes as it does when it closes the card. A batch recorded read so SHALL be closed for every read of batches: no row on the rail, no batch named on a landing row, no card raised for it, until a newer card is posted under its key.

#### Scenario: Sent with no card on the main level's host
- **WHEN** batch 13's card was posted from mac-studio, the planner's wait runs on deneb with batch 13's session, and the user approves the session with no annotations
- **THEN** the wait prints "batch/13: approved", records crew's close of `batch/13` in the planner's name "Read; no notes", ends the session, and the rail no longer shows batch 13

#### Scenario: Sent while the card is lost
- **WHEN** the planner's wait finds batch 13's card lost, records it so, and the user then sends the session with two annotations
- **THEN** the wait prints both annotations as written and records crew's close of `batch/13` "Read; 2 notes sent to their teams"

#### Scenario: Sent while the card's close is refused
- **WHEN** the user sends batch 13's session and Pending You refuses the close of its card
- **THEN** crew records its close of `batch/13` with what was read, and the card, its row gone, is withdrawn by a later rail read

## MODIFIED Requirements

### Requirement: A bolt lands only once every unit's latest change has been in a batch the user has answered
A bolt SHALL be offered for landing only once every unit's latest change, the commit its last construct left, has been in a batch the user has answered: its card sent back with a tap or closed in Pending You, as crew records the card's close, or its reading session sent, as crew records the card's close or, with no card closed, the batch's. When a bolt is otherwise ready to land and some unit's latest change has not been in a batch, a batch SHALL be due at once for those units, and the bolt's landing row SHALL name them. While a batch holding a unit's latest change waits on the user's answer, the landing row SHALL name that batch. No landing card SHALL be raised, and the row SHALL carry no word to land, until every unit's latest change has been in a batch the user has answered, and `crew bolt land` SHALL be refused while any unit's latest change remains outside a batch. A card Pending You lost to its owner SHALL be no answer. A chore SHALL be in no batch and SHALL hold no landing.

#### Scenario: A late amendment
- **WHEN** every unit of a bolt has merged and its verification is green, and one unit's change was constructed again after the last batch
- **THEN** a batch holding that unit is due at once, the landing row names the unit, and no landing card is raised until the batch's card has been answered

#### Scenario: A batch card unanswered
- **WHEN** every unit of bolt `y` has merged and its verification is green, and batch 7, whose card the user has not answered, holds one unit's latest change
- **THEN** `y`'s landing row says it lands once you have answered batch 7, carries no command, and no landing card is raised for `y`

#### Scenario: The batch card answered
- **WHEN** the user sends batch 7's card back with no notes
- **THEN** the next rail read on `y`'s team's host raises `y`'s landing card, and its row carries the word to land

#### Scenario: The batch's session sent with no card held
- **WHEN** batch 7's card is held on a host the main level has left, and the user sends batch 7's reading session on the main level's host
- **THEN** crew records batch 7 read, and the next rail read on `y`'s team's host raises `y`'s landing card

#### Scenario: Notes send a unit back
- **WHEN** the user's notes on batch 7 send one of `y`'s units back to construct, and its new change is in no batch yet
- **THEN** `y`'s landing row names that unit as due a batch, and no landing card is raised until the batch that holds its new change has been answered
