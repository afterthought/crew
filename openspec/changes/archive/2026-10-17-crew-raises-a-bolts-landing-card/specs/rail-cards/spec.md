## MODIFIED Requirements

### Requirement: The landing card is posted once the bolt's verification is green
crew SHALL raise a bolt's landing card once every unit and chore of the bolt has merged, every unit's latest change has been in a batch, sluice's verdict at its head is green and no fix is in flight on it, keyed `land/<bolt>`, as an `approve` of risk high, not reversible, because irreversible, its summary giving the counts, the batches, the verdict and when, and how far main has moved, its face a text artifact "What lands: N units, M chores" naming each one a line, its rationale what follows, and, when sluice's submission at the head has a pull request on GitHub, that pull request as a `url` artifact and among its links; it SHALL ask only for the landing. A note naming a defect SHALL have the conductor start a fix on the bolt, which withdraws the card, and the card SHALL be raised again once the bolt reads proven again.

#### Scenario: Sluice's pull request
- **WHEN** sluice's submission at `y`'s head has pull request #23 on the kit's GitHub
- **THEN** the card links it, titled as sluice's pull request for the landing, on its face and in its details

#### Scenario: No pull request
- **WHEN** the kit's sluice opens no pull request for a submission
- **THEN** the card carries no link, and says nothing of one

#### Scenario: A green bolt
- **WHEN** every unit and chore of bolt `y` has merged, each unit's latest change has been in a batch and sluice is green at `abc1234`
- **THEN** one card keyed `land/y` is open, an approve of risk high, naming the units and chores and the verdict

#### Scenario: A defect noted on the card
- **WHEN** the user answers `land/y` with a note naming a defect and the conductor runs `crew fix` on `y`
- **THEN** the card is withdrawn, "held for a fix: <the note>", and a new card is raised when `y` reads proven again

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, derived from the row's state: `proposal/<n>` for an open proposal, `batch/<n>` for review batch n, and `land/<bolt>` for a bolt whose every unit has merged, one key for the bolt whatever its head (record 0031). A row's owner SHALL post its card with that key as the card's idempotency key. There SHALL be no review row and no verify row, and no `review/<unit>/<head>` or `verify/<unit>/<stamp>` key. A batch whose cards were posted under `batch/<n>-<k>` before one card per batch was built SHALL keep a row for each of those keys until its card closes, and SHALL have no `batch/<n>` row.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2`, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, and the planner may not post `batch/2`

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was ready to land at head `abc1234`, a note on its landing card named a defect, and a fix landed on the bolt at `def5678` with its verification green
- **THEN** its landing row's key is still `land/y`, and crew raises a new landing card under it, following the one the fix held

#### Scenario: A unit built again
- **WHEN** unit `u` was constructed at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** no review row or key exists for either head; the unit's revised change is due for the partition's next batch, whose card's key is the batch's

#### Scenario: A verify report saved
- **WHEN** unit `u`'s verify saves its report `verify-u-20261013-1200.md`
- **THEN** the rail has no row for it, and a card keyed `verify/u/20261013-1200` belongs to no row

### Requirement: crew names the card a change ends
When crew records a change that ends a row, it SHALL name that row's card to its owner: in the command's output when the owner made the change, and by a notice when anyone else did. That covers a proposal approved, dropped or replaced; a unit approved, built again, merged, moved off its team or dropped; and an amended intent. A bolt landed or dropped tells its conductor so, and names no card: crew closes the bolt's landing card itself.

#### Scenario: The user approves a unit from the rail's shell
- **WHEN** the user runs `crew unit approve x --label wldn`
- **THEN** swb-1-conductor is told that unit `x` was approved and to close its card for `review/x`

#### Scenario: The conductor builds a unit again
- **WHEN** swb-1-conductor runs `crew unit run x construct "<words>"` on a unit in review
- **THEN** the command's output names the card for `review/x` to close

#### Scenario: A bolt lands
- **WHEN** main-level ops runs `crew bolt land y`
- **THEN** the conductor of the team that held `y` is told it landed, and crew closes its landing card on the team's host

### Requirement: A row's card is closed when the row's key changes
When a row's key changes because what it asks changed, a unit built again, the row's owner SHALL close the card it holds under the old key with a one-line outcome, and post the row's card under the new key once the row asks again. A landing's key is its bolt's and does not change: when a merge moves the bolt's head while its landing card is open, crew SHALL change the card in place, and a card under an older head's key, `land/<bolt>/<head>` from before, SHALL belong to no row.

#### Scenario: A fix moves a bolt with an open landing card
- **WHEN** the landing card `land/y` is open, a fix is started on bolt `y`, and the fix merges, moving its head to `def5678`
- **THEN** the card was withdrawn when the fix started, held for it, and crew raises a new card under `land/y`, following it, once `y` reads proven at `def5678`

#### Scenario: A landing card forgotten under an old head
- **WHEN** a card keyed `land/y/abc1234`, posted before the key was the bolt's, is still open while bolt `y` waits to land
- **THEN** `crew rail` shows `land/y` under the landing row, and the card under `land/y/abc1234` belongs to no row, for the rail's read to close

#### Scenario: A merge moves a bolt with an open landing card
- **WHEN** the landing card `land/y` is open and a merge into bolt `y` moves its head to `def5678`
- **THEN** crew changes the card in place, "Its head is now def5678", and posts no second card

### Requirement: crew refuses a row's card in another form
Before Pending You's `post_request` runs in a session crew started, crew SHALL refuse a card whose key is a row's and whose form is not that row's, naming the form the row's card takes. A proposal's card SHALL be refused when its unit questions do not hold, each exactly once, the units the proposal adds or moves into a bolt. A refused call never reaches Pending You. When crew cannot check a card it would check, its own input or the proposal unreadable among the reasons, it SHALL refuse it and name what failed.

#### Scenario: A landing card posted as a step
- **WHEN** a conductor posts a card keyed `land/y` as an `action` with the landing command as its step
- **THEN** crew refuses it before Pending You is called, saying a landing's card is an approval marked high stakes whose yes has the conductor tell main-level ops to land, and no card is posted

#### Scenario: A landing card not marked high stakes
- **WHEN** a conductor posts a card keyed `land/y` as an approval without `highStakes`
- **THEN** crew refuses it, saying the landing card is marked high stakes

#### Scenario: Input crew cannot read
- **WHEN** the hook is given input before `post_request` that is not a JSON object
- **THEN** crew refuses the call, saying it could not check the card's form and why, and no card is posted

#### Scenario: A card in the row's form
- **WHEN** the planner posts a card keyed `proposal/4`, a proposal that adds no unit, as an `approve` card with no options
- **THEN** crew lets it through, and records it after it is posted, as before

#### Scenario: A proposal card missing a new unit
- **WHEN** the planner posts a card keyed `proposal/5`, which adds `b` and `c`, whose unit question lists only `b`
- **THEN** crew refuses it, naming `c` as a new unit the card does not ask about

#### Scenario: A proposal card with new units posted as a plain approval
- **WHEN** the planner posts a card keyed `proposal/5`, which adds `b` and `c`, as an `approve` card with no questions
- **THEN** crew refuses it, saying the card asks `plan` and a question of its new units, as `crew plan card 5` prints it

### Requirement: crew refuses a crew agent's card under any key but a row's of its own
Before a Pending You card is posted from a session crew started, crew SHALL refuse it unless its idempotency key is the card key of a rail row the agent owns: for the planner, `proposal/<n>` for an open proposal of its partition; for a conductor, `review/<unit>/<head>` for a unit of the bolt its team holds, or `land/<bolt>` for that bolt; `verify/<unit>/<stamp>` is no agent's. Every other crew agent SHALL own no key. A refused card SHALL NOT reach Pending You, and its refusal SHALL name the keys to use.

#### Scenario: ops posts a card
- **WHEN** brd-2-ops calls Pending You's `post_request` under any key
- **THEN** the call is refused before it reaches Pending You, and the refusal says ops owns no key: a team's cards are its conductor's, and what is left for the user goes in the proof file

#### Scenario: A conductor posts under a key of its own making
- **WHEN** brd-2-conductor, whose team holds bolt `y`, posts a card keyed `gateway-check-y`
- **THEN** the call is refused, and the refusal names `land/y` and the review keys of `y`'s units, read from `crew rail`

#### Scenario: A conductor posts another team's row
- **WHEN** brd-2-conductor posts a card keyed `review/z/abc1234` for a unit `z` of a bolt another team holds
- **THEN** the call is refused, naming the keys that are brd-2-conductor's

#### Scenario: The planner posts a proposal's card
- **WHEN** wldn-planner posts a card keyed `proposal/4` while proposal 4 of `wldn` is open
- **THEN** the call goes through, and the card is recorded as before

#### Scenario: A conductor posts a verify report's card
- **WHEN** brd-2-conductor, whose team holds bolt `y`, posts a card keyed `verify/u/20261013-1200` for a unit `u` of `y`
- **THEN** the call is refused before it reaches Pending You, naming `land/y`
