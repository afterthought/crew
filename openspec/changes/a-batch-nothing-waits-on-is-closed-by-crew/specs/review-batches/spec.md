## ADDED Requirements

### Requirement: A batch that waits on nothing is closed by crew
A batch SHALL wait on nothing once each of its units has landed or is held by a later batch. crew SHALL read such a batch closed from the run record at every read of the rail and the board, so it is no row and crew raises no card for it; the rail's sweep SHALL record crew's close once, in the planner's name, saying why, and SHALL withdraw a card open under its key with the same words. A batch with any other unit SHALL stay a row until its card closes.

#### Scenario: Every unit has landed
- **WHEN** batch 3 holds `x1` and `x2`, no card of it was ever closed, and the bolt holding both has landed
- **THEN** the rail and the board have no row for batch 3, no card is posted for it, and the next rail read on the partition's main-level host records crew's close of `batch/3` in the planner's name, "its batch waits on nothing: x1 and x2 have landed"

#### Scenario: A later batch holds the unit
- **WHEN** batch 5 holds `x1`, the user's notes on it were given in the planner's pane, `x1` was constructed again, and batch 7 holds its new change
- **THEN** batch 5 is no row, crew's close of `batch/5` says "its batch waits on nothing: batch 7 holds a newer change of x1", and batch 7 is a row until its own card closes

#### Scenario: One unit landed and another held again
- **WHEN** batch 6 holds `x1`, which has landed, and `y1`, which batch 8 holds again
- **THEN** batch 6 is no row, and crew's close says "its batch waits on nothing: x1 has landed; batch 8 holds a newer change of y1"

#### Scenario: One unit still waits on the user
- **WHEN** batch 9 holds `x1`, which has landed, and `y1`, which has not landed and no later batch holds
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
- **WHEN** the partition's run record did not answer on the main-level host
- **THEN** the sweep records no close for any batch, says the partition was not swept, and a batch is closed only as far as the entries read show it
