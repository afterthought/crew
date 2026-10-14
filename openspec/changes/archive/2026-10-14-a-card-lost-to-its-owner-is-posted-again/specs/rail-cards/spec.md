## ADDED Requirements

### Requirement: A row's card lost to its owner is posted again
A card Pending You answers "not found" to the agent that posted it is lost to that agent. While its row still waits, the owner SHALL post the row's card again under the row's key, in the row's form, its summary saying after the link and the bolt that an older copy is dead, to dismiss it in the app, and that this card is the one to answer. A lost card whose row is gone SHALL be posted again by nobody.

#### Scenario: The host signed in again
- **WHEN** the planner, started afresh, finds that the card the rail shows open under `proposal/17` reads "not found" in Pending You, and proposal 17 is still open
- **THEN** the planner posts a new approval card under `proposal/17`, whose summary, after its link, says an older copy of this card is dead, to dismiss it in the app, and to answer this one

#### Scenario: A close that finds nothing
- **WHEN** the planner closes its card for proposal 9 after applying the user's approval given in its pane, and Pending You answers "not found"
- **THEN** the planner posts no card for it, since the row no longer waits, and goes on

#### Scenario: A lost landing card
- **WHEN** bolt `y` waits to land at `def5678` and the conductor's card `land/y/def5678` reads "not found" when it updates the card
- **THEN** the conductor posts the landing card again under `land/y/def5678`, an approval of risk high naming the bolt, its summary saying the older copy is dead and this one is the one to answer

#### Scenario: A lost operations card
- **WHEN** main-level ops finds its card under `deploy/dev/abc1234` "not found" while the deploy's offer still waits
- **THEN** ops posts the deploy's card again under `deploy/dev/abc1234`, its summary saying the older copy is dead and this one is the one to answer

### Requirement: An owner checks its rows' cards when its sign-in may have changed
A row's owner SHALL ask Pending You for each card the rail shows open under its rows, by the card's id, at its start and whenever Pending You has it call `whoami` again, and SHALL take any card of its own that a Pending You tool answers "not found" as lost.

#### Scenario: Started afresh after the host signed in again
- **WHEN** a conductor starts and the rail shows its card `req_1` open under `land/y/def5678`
- **THEN** the conductor asks Pending You for `req_1`, and when it reads "not found" posts the row's card again

## MODIFIED Requirements

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
