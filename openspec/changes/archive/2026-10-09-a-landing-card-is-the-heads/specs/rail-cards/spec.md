# Spec Delta

## MODIFIED Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, derived from the row's state: `proposal/<n>` for an open proposal, `review/<unit>/<head>` for a unit in review (the first seven characters of its branch's head), `verify/<unit>/<YYYYMMDD-HHMM>` for a verify report (the stamp in the report's file name), and `land/<bolt>/<head>` for a bolt ready to land (the first seven characters of the bolt's branch head). A row's owner SHALL post its card with that key as the card's idempotency key.

#### Scenario: A unit built again
- **WHEN** unit `u` was in review at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** its review row's key is `review/u/def5678`, and a card keyed `review/u/abc1234` belongs to no row

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was ready to land at head `abc1234`, its landing failed, and a fix moved its head to `def5678` and ops proved it again
- **THEN** its landing row's key is `land/y/def5678`, its conductor posts a new landing card under that key, and a card keyed `land/y/abc1234` belongs to no row

## ADDED Requirements

### Requirement: A row's card is closed when the row's key changes
When a row's key changes because what it asks changed, a unit built again or a bolt's head moved by a fix, the row's owner SHALL close the card it holds under the old key with a one-line outcome, and post the row's card under the new key once the row asks again.

#### Scenario: A fix moves a bolt with an open landing card
- **WHEN** the conductor's landing card `land/y/abc1234` is open and a fix merges into bolt `y`, moving its head to `def5678`
- **THEN** the conductor closes `land/y/abc1234` saying the fix changed the bolt, and posts `land/y/def5678` once ops has proved the bolt again

#### Scenario: A landing card forgotten under an old head
- **WHEN** the card `land/y/abc1234` is still open while bolt `y` waits to land at `def5678`
- **THEN** `crew rail` shows `land/y/def5678` with no card open under the landing row, and lists `land/y/abc1234` after the groups with `crew tell <its owner> "Close your Pending You card land/y/abc1234: its row is gone."`
