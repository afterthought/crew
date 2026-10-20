## MODIFIED Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, the thing's and not its version's: `proposal/<n>` for a proposal chain, `n` its first proposal; `batch/<n>` for review batch n; `land/<bolt>` for a bolt proven; `deploy/<env>` for a `manual` environment's open offer; `op/<env>/<n>` for a step that waits on the user; `record/<kit>/<number>` for a record proposed. crew SHALL post the row's card with that key as its idempotency key, filled out at its end with `_` to Pending You's eight characters when it is shorter, the same on every post of it, and SHALL record the post under the row's key. A question's card has no row and a key of its asker's own. There SHALL be no review row and no verify row. A batch's row SHALL last until its card closes or the batch waits on nothing (`review-batches`). A batch whose cards were posted under `batch/<n>-<k>` before one card per batch was built SHALL keep a row for each of those keys until its card closes or the units it holds wait on nothing, and SHALL have no `batch/<n>` row.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A key shorter than Pending You takes
- **WHEN** crew raises review batch 7's card, `batch/7` being seven characters, and raises it again after its first post had no answer within a minute
- **THEN** both posts are under `batch/7_`, so Pending You gives the second the card the first made, and the run record holds it under `batch/7`

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2` from before one card per batch, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, until its card closes

#### Scenario: An old batch card whose units have landed
- **WHEN** batch 2's cards were posted under `batch/2-1` and `batch/2-2`, neither has closed, and every unit `batch/2-2` holds has landed while one unit of `batch/2-1` has not
- **THEN** the rail has one row for batch 2, keyed `batch/2-1`, and the sweep withdraws `batch/2-2`'s card, saying its units have landed

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was ready to land at head `abc1234`, a note on its landing card named a defect, and a fix landed on the bolt at `def5678` with its verification green
- **THEN** its landing row's key is still `land/y`, and crew raises a new landing card under it, following the one the fix held

#### Scenario: A unit built again
- **WHEN** unit `u` was constructed at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** no review row or key exists for either head; the unit's revised change is due for the partition's next batch, whose card's key is the batch's

#### Scenario: A verify report saved
- **WHEN** unit `u`'s verify saves its report `verify-u-20261013-1200.md`
- **THEN** the rail has no row for it, and a card keyed `verify/u/20261013-1200` belongs to no row

#### Scenario: A proposal replaced
- **WHEN** proposal 4 is replaced by proposal 5
- **THEN** the rail's row for proposal 5 has the key `proposal/4`, and its card is the chain's
