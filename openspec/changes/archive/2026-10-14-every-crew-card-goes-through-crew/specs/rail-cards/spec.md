## ADDED Requirements

### Requirement: crew builds a row's card in its row's form
crew SHALL build a row's card in its row's form from the row and the words its owner gives `crew card post`, and SHALL refuse words or fields the row's card does not take, naming the form, before anything reaches Pending You. When crew cannot read what the row's card is built from, it SHALL refuse it and name what failed.

#### Scenario: A landing card
- **WHEN** a conductor runs `crew card post land/y/abc1234` with the bolt's title and the proof's step for the user
- **THEN** crew posts an approval of risk high, not reversible, because irreversible, whose action is main-level ops landing `y`, with that step first

#### Scenario: Options given to a landing card
- **WHEN** a conductor gives options to `crew card post land/y/abc1234`
- **THEN** crew refuses, saying a landing's card is an approval with no options, and nothing is posted

#### Scenario: A proposal's card
- **WHEN** the planner runs `crew card post proposal/4`
- **THEN** crew posts the card `crew plan card 4` prints, whole

### Requirement: crew refuses a crew agent's own Pending You call that changes a card or an area
In a session crew started, crew SHALL refuse Pending You's `post_request`, `update_request`, `cancel_request`, `ack_answer` and `create_area` before they reach Pending You, naming the `crew card` command that does it. Pending You's reads SHALL pass. A session crew did not start SHALL NOT be checked.

#### Scenario: A conductor calls post_request
- **WHEN** swb-1-conductor calls Pending You's `post_request` in its session
- **THEN** the call is refused before it reaches Pending You, saying to post the card with `crew card post <key>`

#### Scenario: The wake reads a card
- **WHEN** the wake mod in swb-1-conductor's session calls `get_request`
- **THEN** crew lets it through

#### Scenario: The user's own session
- **WHEN** a Claude session crew did not start calls `post_request`
- **THEN** crew neither checks nor refuses it


## MODIFIED Requirements

### Requirement: The owner of a row posts its card
An agent crew started SHALL post one card for each row it owns, with `crew card post <key>` and the row's words: the planner for each proposal it opens, a conductor for each verify report its team's units wait on the user for and for its bolt once the bolt is proven, or proven but for steps only the user can take. It SHALL post no second card for a row that has one open. A team's cards SHALL be its conductor's: its ops and every stage agent SHALL post no card.

#### Scenario: A proposal opened
- **WHEN** the planner opens proposal 4
- **THEN** it runs `crew card post proposal/4`, and one card keyed `proposal/4` is open, asked by the planner

#### Scenario: No Pending You
- **WHEN** a conductor's session has no Pending You tools and its bolt is proven
- **THEN** it posts the landing card with `crew card post land/<bolt>/<head>`, and the card reaches the user

#### Scenario: A proof leaves the user a check
- **WHEN** brd-2's ops finishes its proof with every item green but one check only the user can make on their Mac
- **THEN** ops writes that check in its proof file and posts no card, and the user gets one card for it, the conductor's landing card for the bolt

### Requirement: An agent never runs Pending You from npm or waits on a hold
An agent crew started SHALL hear an answer by being woken in its session or by reading its card with `crew card read <key>`, as its brief says, and SHALL NOT run any `npx pendingyou` command. After a fresh start it SHALL read each of its open cards with `crew card read` and act on any the user has answered.

#### Scenario: Restarted with an answered card
- **WHEN** a conductor restarts while the user has answered its landing card
- **THEN** at its start it reads the card with `crew card read`, finds the answer, and acts on it

## REMOVED Requirements

### Requirement: crew refuses a row's card in another form
**Reason**: crew builds a row's card in its row's form, as the added requirement says, so there is no card an agent wrote to check.
**Migration**: the owner gives `crew card post` the row's words.

### Requirement: crew checks only a row's card in a crew session
**Reason**: a crew agent posts no card through Pending You's tools, so the hook checks no card's form; it refuses the call, as the added requirement says.
**Migration**: a row's card is posted with `crew card post`, which builds it in its row's form.
