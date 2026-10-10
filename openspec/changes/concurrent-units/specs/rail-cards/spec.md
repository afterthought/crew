# rail-cards

## MODIFIED Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, derived from the row's state: `proposal/<n>` for an open proposal, `batch/<n>-<k>` for the k-th card of review batch n, `verify/<unit>/<YYYYMMDD-HHMM>` for a verify report (the stamp in the report's file name), and `land/<bolt>` for a bolt ready to land. A row's owner SHALL post its card with that key as the card's idempotency key. There SHALL be no review row and no `review/<unit>/<head>` key.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes
- **THEN** the rail has two batch rows, keyed `batch/3-1` and `batch/3-2`, and a card keyed `review/u/abc1234` belongs to no row

### Requirement: The owner of a row posts its card
When an agent crew started has Pending You's tools, it SHALL post one card for each row it owns: the planner for each proposal it opens and for each card of a review batch, a conductor for each verify report its team's units wait on the user for, and for its bolt once the bolt is proven. It SHALL post no second card for a row that has one open.

#### Scenario: A proposal opened
- **WHEN** the planner opens proposal 4 in a session with Pending You's tools
- **THEN** one card keyed `proposal/4` is open, asked by the planner

#### Scenario: A batch due
- **WHEN** the reviewer delivers batch 3 of five units
- **THEN** one card keyed `batch/3-1` is open, asked by the planner, and no conductor posts one
