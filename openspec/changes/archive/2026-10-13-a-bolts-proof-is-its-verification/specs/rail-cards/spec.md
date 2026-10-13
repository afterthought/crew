## ADDED Requirements

### Requirement: The landing card is posted once the bolt's verification is green
The conductor SHALL post a bolt's landing card once every unit and chore of the bolt has merged and its verification is green, and the card SHALL ask only for the landing. A step only the user can take or check SHALL be an after-deploy step on a deploy's card, never a question on the landing card. A note on the landing card that names a defect SHALL be a fix on the bolt, and the landing SHALL be asked again only once the verification is green again.

#### Scenario: A green bolt
- **WHEN** every unit of bolt `y` has merged and its verification is green at head `abc1234`
- **THEN** the conductor posts one high-stakes card keyed `land/y/abc1234` that asks only for the landing

#### Scenario: A defect noted on the card
- **WHEN** the user answers the landing card for `y` with a note naming a defect
- **THEN** the conductor does not ask main-level ops to land `y`, closes the card with that outcome, and runs a fix on the bolt

## MODIFIED Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, derived from the row's state: `proposal/<n>` for an open proposal, `batch/<n>` for review batch n, and `land/<bolt>/<head>` for a bolt ready to land (the first seven characters of the bolt's branch head). A row's owner SHALL post its card with that key as the card's idempotency key. There SHALL be no review row and no verify row, and no `review/<unit>/<head>` or `verify/<unit>/<stamp>` key. A batch whose cards were posted under `batch/<n>-<k>` before one card per batch was built SHALL keep a row for each of those keys until its card closes, and SHALL have no `batch/<n>` row.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2`, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, and the planner may not post `batch/2`

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was ready to land at head `abc1234`, a note on its landing card named a defect, and a fix landed on the bolt at `def5678` with its verification green
- **THEN** its landing row's key is `land/y/def5678`, its conductor posts a new landing card under that key, and a card keyed `land/y/abc1234` belongs to no row

#### Scenario: A unit built again
- **WHEN** unit `u` was constructed at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** no review row or key exists for either head; the unit's revised change is due for the partition's next batch, whose card's key is the batch's

#### Scenario: A verify report saved
- **WHEN** unit `u`'s verify saves its report `verify-u-20261013-1200.md`
- **THEN** the rail has no row for it, and a card keyed `verify/u/20261013-1200` belongs to no row

### Requirement: The owner of a row posts its card
When an agent crew started has Pending You's tools, it SHALL post one card for each row it owns: the planner for each proposal it opens and for each review batch, and a conductor for its bolt once every unit and chore has merged and its verification is green. It SHALL post no second card for a row that has one open to it; a card lost to it is not, and is posted again as *A row's card lost to its owner is posted again* says. A team's cards SHALL be its conductor's: its ops and every stage agent SHALL post no card, and no crew agent SHALL post a card that is not a row's. No card SHALL be posted for a verify report, which is no row.

#### Scenario: A proposal opened
- **WHEN** the planner opens proposal 4 in a session with Pending You's tools
- **THEN** one card keyed `proposal/4` is open, asked by the planner

#### Scenario: A batch due
- **WHEN** the reviewer delivers batch 3 of seven units
- **THEN** one card keyed `batch/3` is open, asked by the planner, and no conductor posts one

#### Scenario: No Pending You
- **WHEN** a conductor's session has no Pending You tools and its bolt's verification is green with every unit merged
- **THEN** no card is posted, the rail row is as before, and the conductor tells the operator agents it waits on the user

#### Scenario: A verify report saved
- **WHEN** a unit's verify saves its report, which marks two findings fix
- **THEN** its conductor posts no card and asks the user nothing, and runs code once more with the report's path

#### Scenario: A proof leaves the user a check
- **WHEN** a bolt's changes leave a check only the user can make on their Mac
- **THEN** no proof asks it and ops posts no card: it is an after-deploy step on a deploy's card, and the bolt's landing card asks only for the landing

### Requirement: A landing's card is a high-stakes approval
A bolt's landing card, keyed `land/<bolt>/<head>`, SHALL be an approval (`approve`) marked high stakes, with no options and no steps, whose yes has the conductor tell main-level ops to land the bolt.

#### Scenario: A landing card
- **WHEN** the conductor posts the landing card for bolt `y` at head `abc1234`
- **THEN** the card is an approval marked high stakes, offers no Done button, no step and no command to land, and is approved only by holding the button in the Pending You app

#### Scenario: A landing card with a step
- **WHEN** the conductor posts the landing card for `y` with a step for the user
- **THEN** crew refuses it, saying the card has steps for the user to take

#### Scenario: A landing approved
- **WHEN** the user approves the landing card for bolt `y`
- **THEN** the conductor tells main-level ops to land `y` on the user's word, and the user runs nothing

## REMOVED Requirements

### Requirement: ops writes a proof's steps for the user in its proof file
**Reason**: Record 0025: ops's proof report and its *Left for the user* go.
**Migration**: A step only the user can do is an after-deploy step on a deploy's card (`plan.14`).

### Requirement: The landing card asks the proof's steps before approval
**Reason**: Record 0025: the landing card asks only for the landing, once the bolt's verification is green.
**Migration**: "The landing card is posted once the bolt's verification is green".
