## ADDED Requirements

### Requirement: A question whose asker is gone is withdrawn
On each rail read crew SHALL withdraw, under the host's connection, every open question card whose asker herdr no longer lists as an agent, with the reason naming the asker, and SHALL say so.

#### Scenario: A conductor's question outlives it
- **WHEN** crw-3-conductor's question card is open and crw-3's team is closed
- **THEN** the next rail read withdraws it with "crw-3-conductor ended; ask again if it still matters"

## MODIFIED Requirements

### Requirement: The rail shows each row's card
`crew rail` SHALL print, under each row, the row's card key, whether a card with that key is open, its id and whose it is, and after the groups the open question cards, each with its asker, its title and its age, and the open record cards apart. A card is open from its `card.post` entry until a `card.close` entry for the same card, or until a later `card.post` under the same key names another card, which is then the row's card while the older is taken as lost.

#### Scenario: A row with its card
- **WHEN** bolt `y` reads proven and crew's card `req_l1` under `land/y` is open
- **THEN** the row's card line names `land/y` as open, `req_l1`, the conductor's

#### Scenario: A row without a card
- **WHEN** a proposal is open and its card's post was refused
- **THEN** the row's card line names `proposal/<n>` with no card open and the refusal's words

#### Scenario: A card posted again under its row's key
- **WHEN** crew's card `req_1` under `proposal/17` read not found after the host signed in again, and the rail read posted `req_2` under `proposal/17`
- **THEN** the row's card line names `req_2` as its open card, and `req_1` is listed as lost

#### Scenario: A row with its card and a question open
- **WHEN** `proposal/4`'s card `req_p4` is open and swb-1-conductor's question `req_q1` is open
- **THEN** the proposal row's card line names `proposal/4`, open, `req_p4`, the planner's; and after the groups `req_q1` is listed with swb-1-conductor, its title and its age

### Requirement: The rail names an open card whose row is gone
After its groups, `crew rail` SHALL list each card its sweep withdrew or closed on this read, with its key, its owner and why (its row is gone, its asker ended), and each card it posted again as lost.

#### Scenario: A forgotten card
- **WHEN** proposal 4 was approved from the planner's pane and its card `proposal/4` is still open
- **THEN** the next rail read closes it with the approval's outcome and lists it, "closed: its proposal was applied"

#### Scenario: A withdrawn card
- **WHEN** bolt `y` was dropped while `land/y`'s card was open
- **THEN** the rail withdraws the card and lists it, "withdrawn: its bolt was dropped"

### Requirement: A row's card lost to its owner is posted again
A card Pending You answers "not found" to the host's connection is lost: the host signed in anew. On the next rail read, while the row still waits, crew SHALL post the row's card again under the row's key, in the row's form, its summary saying that an older copy is dead, to dismiss it in the app, and that this card is the one to answer, and SHALL take the newer card as the row's. A lost card whose row is gone SHALL be posted again by nobody.

#### Scenario: The host signed in again
- **WHEN** the host runs `pendingyou-signin` while `proposal/17`'s card is open, and the rail is read
- **THEN** crew posts a new card under `proposal/17`, whose summary says an older copy of this card is dead, to dismiss it in the app, and to answer this one, and the rail shows the new card's id as the row's

#### Scenario: A close that finds nothing
- **WHEN** `crew plan approve 9` closes proposal 9's card and Pending You answers "not found"
- **THEN** crew posts no card for it, since the row no longer waits, records the close as lost, and goes on

#### Scenario: A lost landing card
- **WHEN** bolt `y` waits to land and `land/y`'s card reads "not found" when a fix moves the head and crew changes the card
- **THEN** crew posts the landing card again under `land/y`, an approval of risk high naming the bolt, its summary saying the older copy is dead and this one is the one to answer

#### Scenario: A lost operations card
- **WHEN** `deploy/dev`'s card reads "not found" while the deploy's offer still waits
- **THEN** the next rail read posts the deploy's card again under `deploy/dev`, its summary saying the older copy is dead and this one is the one to answer

## REMOVED Requirements

### Requirement: An owner checks its rows' cards when its sign-in may have changed
**Reason**: crew checks its cards on the rail read and posts a lost one again itself ("A row's card lost to its owner is posted again").
