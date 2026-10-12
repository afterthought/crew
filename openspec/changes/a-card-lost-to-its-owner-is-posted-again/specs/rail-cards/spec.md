## ADDED Requirements

### Requirement: A row's card lost to its owner is posted again
A card Pending You answers "not found" to the agent that posted it is lost to that agent. While its row still waits, the owner SHALL post the row's card again under the row's key, in the row's form, its summary saying after the link and the bolt that an older copy is dead, to dismiss it in the app, and that this card is the one to answer. A lost card whose row is gone SHALL be posted again by nobody.

#### Scenario: The host signed in again
- **WHEN** the planner, started afresh, finds that the card the rail shows open under `proposal/17` reads "not found" in Pending You, and proposal 17 is still open
- **THEN** the planner posts a new approval card under `proposal/17`, whose summary, after its link, says an older copy of this card is dead, to dismiss it in the app, and to answer this one

#### Scenario: A close that finds nothing
- **WHEN** a conductor closes its verify card for unit `x` after acting on the user's word in the pane, and Pending You answers "not found"
- **THEN** the conductor posts no card for it, since the row no longer waits, and goes on

#### Scenario: A lost landing card
- **WHEN** bolt `y` waits to land at `def5678` and the conductor's card `land/y/def5678` reads "not found" when it updates the card
- **THEN** the conductor posts the landing card again under `land/y/def5678`, an approval of risk high naming the bolt, its summary saying the older copy is dead and this one is the one to answer

#### Scenario: A lost operations card
- **WHEN** main-level ops finds its card under `deploy/dev/abc1234` "not found" while the deploy's offer still waits
- **THEN** ops posts the deploy's card again under `deploy/dev/abc1234`, its summary saying the older copy is dead and this one is the one to answer

### Requirement: An owner checks its rows' cards when its sign-in may have changed
A row's owner SHALL ask Pending You for each card the rail shows open under its rows, by the card's id, at its start and whenever Pending You has it call `whoami` again, and SHALL take any card of its own that a Pending You tool answers "not found" as lost.

#### Scenario: Started afresh after the host signed in again
- **WHEN** a conductor starts and the rail shows its card `req_1` open under `verify/x/20261011-1400`
- **THEN** the conductor asks Pending You for `req_1`, and when it reads "not found" posts the row's card again

## MODIFIED Requirements

### Requirement: The owner of a row posts its card
When an agent crew started has Pending You's tools, it SHALL post one card for each row it owns: the planner for each proposal it opens, a conductor for each of its team's units in review, for each verify report its team's units wait on the user for, and for its bolt once the bolt is proven, or proven but for steps only the user can take. It SHALL post no second card for a row that has one open to it; a card lost to it is not, and is posted again as *A row's card lost to its owner is posted again* says. A team's cards SHALL be its conductor's: its ops and every stage agent SHALL post no card, and no crew agent SHALL post a card that is not a row's.

#### Scenario: A proposal opened
- **WHEN** the planner opens proposal 4 in a session with Pending You's tools
- **THEN** one card keyed `proposal/4` is open, asked by the planner

#### Scenario: No Pending You
- **WHEN** a conductor's session has no Pending You tools and a unit reaches review
- **THEN** no card is posted, the unit's rail row is as before, and the conductor tells the operator agents it waits on the user

#### Scenario: A proof leaves the user a check
- **WHEN** brd-2's ops finishes its proof with every item green but one check only the user can make on their Mac
- **THEN** ops writes that check in its proof file and posts no card, and the user gets one card for it, the conductor's landing card for the bolt

### Requirement: The rail shows each row's card
`crew rail` SHALL print, under each row, the row's card key and whether a card with that key is open, whose it is, and the open card's id. A card is open from its `card.post` entry until a `card.close` entry for the same card, or until a later `card.post` entry by the same owner under the same key names another card, which is then the row's card while the older is taken as lost.

#### Scenario: A row with its card
- **WHEN** unit `x` is in review at `abc1234` and swb-1-conductor's card `review/x/abc1234`, id `req_1`, is open
- **THEN** the row's card line names `review/x/abc1234` as open, asked by `swb-1-conductor`, with the id `req_1`

#### Scenario: A row without a card
- **WHEN** a proposal is open and no card has been posted for it
- **THEN** the row's card line names `proposal/<n>` with no card open

#### Scenario: A card posted again under its row's key
- **WHEN** the planner's card `req_1` under `proposal/17` was never closed, and the planner posts `req_2` under `proposal/17`
- **THEN** the row's card line names `req_2` as its open card, and `req_1` is neither on the row's card line nor among the open cards with no row
