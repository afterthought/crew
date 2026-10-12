# Spec Delta

## MODIFIED Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, derived from the row's state: `proposal/<n>` for an open proposal, `batch/<n>` for review batch n, `verify/<unit>/<YYYYMMDD-HHMM>` for a verify report (the stamp in the report's file name), and `land/<bolt>/<head>` for a bolt ready to land (the first seven characters of the bolt's branch head). A row's owner SHALL post its card with that key as the card's idempotency key. There SHALL be no review row and no `review/<unit>/<head>` key. A batch whose cards were posted under `batch/<n>-<k>` before one card per batch was built SHALL keep a row for each of those keys until its card closes, and SHALL have no `batch/<n>` row.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2`, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, and the planner may not post `batch/2`

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was ready to land at head `abc1234`, its landing failed, and a fix moved its head to `def5678` and ops proved it again
- **THEN** its landing row's key is `land/y/def5678`, its conductor posts a new landing card under that key, and a card keyed `land/y/abc1234` belongs to no row

#### Scenario: A unit built again
- **WHEN** unit `u` was constructed at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** no review row or key exists for either head; the unit's revised change is due for the partition's next batch, whose card's key is the batch's

### Requirement: The owner of a row posts its card
When an agent crew started has Pending You's tools, it SHALL post one card for each row it owns: the planner for each proposal it opens and for each review batch, a conductor for each verify report its team's units wait on the user for, and for its bolt once the bolt is proven. It SHALL post no second card for a row that has one open.

#### Scenario: A proposal opened
- **WHEN** the planner opens proposal 4 in a session with Pending You's tools
- **THEN** one card keyed `proposal/4` is open, asked by the planner

#### Scenario: A batch due
- **WHEN** the reviewer delivers batch 3 of seven units
- **THEN** one card keyed `batch/3` is open, asked by the planner, and no conductor posts one

#### Scenario: No Pending You
- **WHEN** a conductor's session has no Pending You tools and its bolt is proven, or a unit of its waits on a verify report
- **THEN** no card is posted, the rail row is as before, and the conductor tells the operator agents it waits on the user

#### Scenario: A proof leaves the user a check
- **WHEN** brd-2's ops finishes its proof with every item green but one check only the user can make on their Mac
- **THEN** ops writes that check in its proof file and posts no card, and the user gets one card for it, the conductor's landing card for the bolt

## ADDED Requirements

### Requirement: A batch's card is a notice naming every unit
A batch's card, keyed `batch/<n>`, SHALL be a Pending You notice (`fyi`) that asks nothing: no options, no question, no approval, no steps and no attachment. Its words SHALL name every unit of the batch and hold each unit's summary as prose, with no code block.

#### Scenario: A card of six units
- **WHEN** the planner posts the card for batch 2 holding six units
- **THEN** the card is one `fyi` whose words name all six units, each with its summary and its reading session's link

### Requirement: crew refuses a batch card in another form
Before `post_request` or `update_request` runs in a session crew started, crew SHALL refuse a card keyed `batch/<n>` that is not in the batch card's form, or a change that takes it out of that form, naming the form: anything to answer, steps, an attachment, a code block in its words, or a background that leaves out a unit of the batch. When crew cannot read the batch's units, it SHALL refuse and name what failed.

#### Scenario: A batch card with a choice of units
- **WHEN** the planner posts a card keyed `batch/2` as a `multi` of its units
- **THEN** crew refuses it before Pending You is called, saying a batch's card is one notice for the whole batch with nothing to answer, and no card is posted

#### Scenario: A batch card with its summary as code
- **WHEN** the planner posts a card keyed `batch/2` as an `fyi` whose background holds a fenced code block, or with the summary attached as a `code` artifact
- **THEN** crew refuses it, saying the summary goes in the card's words as prose, since a code block scrolls sideways on the phone

#### Scenario: A batch card that leaves out a unit
- **WHEN** the planner posts a card keyed `batch/2`, whose batch holds `x1`, `x2` and `z1`, with a background naming only `x1` and `x2`
- **THEN** crew refuses it, saying it leaves out `z1`

#### Scenario: A batch card in its form
- **WHEN** the planner posts a card keyed `batch/2` as an `fyi` whose background names `x1`, `x2` and `z1`, each with its summary as prose
- **THEN** crew lets it through, and records it after it is posted, as before

### Requirement: No card of crew's asks a question in words
Before `post_request` or `update_request` runs in a session crew started, crew SHALL refuse a card under a row's key that is a text question, carries a `text` field, or holds a question of kind `text`, saying Pending You makes every question required and the card's note is where the user's words go.

#### Scenario: A proposal card with a text question
- **WHEN** the planner posts a card keyed `proposal/4` with a question of kind `text` for feedback
- **THEN** crew refuses it, saying the card asks a question in words, which Pending You makes required, and no card is posted
