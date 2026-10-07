# Spec Delta

## Purpose

Each decision on the rail reaches the user as one Pending You card from the agent that owns it, answered on the Mac or the phone, kept true by crew's own events, and shown on the rail so a stale card is seen at once.

## ADDED Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, derived from the row's state: `proposal/<n>` for an open proposal, `review/<unit>/<head>` for a unit in review (the first seven characters of its branch's head), `verify/<unit>/<YYYYMMDD-HHMM>` for a verify report (the stamp in the report's file name), and `land/<bolt>` for a bolt ready to land. A row's owner SHALL post its card with that key as the card's idempotency key.

#### Scenario: A unit built again
- **WHEN** unit `u` was in review at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** its review row's key is `review/u/def5678`, and a card keyed `review/u/abc1234` belongs to no row

### Requirement: The owner of a row posts its card
When an agent crew started has Pending You's tools, it SHALL post one card for each row it owns: the planner for each proposal it opens, a conductor for each of its team's units in review, for each verify report its team's units wait on the user for, and for its bolt once the bolt is proven. It SHALL post no second card for a row that has one open.

#### Scenario: A proposal opened
- **WHEN** the planner opens proposal 4 in a session with Pending You's tools
- **THEN** one card keyed `proposal/4` is open, asked by the planner

#### Scenario: No Pending You
- **WHEN** a conductor's session has no Pending You tools and a unit reaches review
- **THEN** no card is posted, the unit's rail row is as before, and the conductor tells the operator agents it waits on the user

### Requirement: A card says whose it is and where it belongs
A card SHALL be asked in the agent's crew name, with its host as the session's machine and its worktree as the session's folder. It SHALL be filed in the area of its kit, found by the kit's git remote, in the group named for its partition. Its title SHALL name what it asks and its bolt. An agent SHALL never create a group.

#### Scenario: A review card
- **WHEN** swb-1-conductor posts the card for unit `x` of bolt `y` in switchboard-kit
- **THEN** the card is asked by `swb-1-conductor` on its host, sits in switchboard-kit's area in the `wldn` group, and its title names unit `x` and bolt `y`

#### Scenario: The first card in a kit
- **WHEN** no area matches the kit `WilldanGroup/switchboard-kit`
- **THEN** the agent creates it once, with the key `create-area:WilldanGroup/switchboard-kit`, so two agents posting at the same time make one area

### Requirement: A card carries what the user would read and the row's answers
A proposal's card SHALL carry the proposal's page as `crew plan proposed <n>` prints it; a review card the path of the unit's change folder on its host; a verify card the report. Each card's options SHALL be the row's answers: approve or ask for changes for a proposal or a review, what to fix or merge for a verify report, and approve for a landing.

#### Scenario: A review card's options
- **WHEN** the user opens a review card
- **THEN** it offers approval, and a note in the user's own words asks for changes

### Requirement: Landing is approved only by holding the button
The card for a bolt ready to land SHALL be marked high stakes, so it is approved by holding the button in the Pending You app and never with a key in Herdr's popup.

#### Scenario: Landing from the popup
- **WHEN** the user presses the approve key on a landing card in Herdr's popup
- **THEN** Pending You refuses it as high stakes, and the bolt does not land

### Requirement: An answer wakes the owner, which acts on the user's word
An answer on a card SHALL be acted on by the agent that posted it, when it is woken in its session, and by no other: the planner approves, replaces or drops the proposal; the conductor approves the unit or runs construct again with the user's words, fixes or merges after a verify report, or asks main-level ops to land the bolt. The agent SHALL then close the card with a one-line outcome.

#### Scenario: A proposal approved from the phone
- **WHEN** the user approves the card for proposal 4 on the phone
- **THEN** the planner is woken, runs `crew plan approve 4`, closes the card with what was applied, and the rail's proposal row is gone

#### Scenario: Changes asked for on a review card
- **WHEN** the user answers a review card with a note asking for changes
- **THEN** the conductor runs construct again with the note's words and closes the card

#### Scenario: Landing approved
- **WHEN** the user approves the landing card for bolt `y`
- **THEN** the conductor tells the partition's main-level ops to land `y` on the user's word, and main-level ops lands it

### Requirement: An agent never runs Pending You from npm or waits on a hold
An agent crew started SHALL hear answers only by being woken in its session, and SHALL NOT run any `npx pendingyou` command or `pendingyou hold`. After a fresh start it SHALL list its own open cards and act on any the user has answered.

#### Scenario: Restarted with an answered card
- **WHEN** a conductor restarts while the user has answered its review card
- **THEN** at its start it finds the answered card among its own, and acts on it

### Requirement: crew names the card a change ends
When crew records a change that ends a row, it SHALL name that row's card to its owner: in the command's output when the owner made the change, and by a notice when anyone else did. That covers a proposal approved, dropped or replaced; a unit approved, built again, merged, moved off its team or dropped; an amended intent; and a bolt landed or dropped.

#### Scenario: The user approves a unit from the rail's shell
- **WHEN** the user runs `crew unit approve x --label wldn`
- **THEN** swb-1-conductor is told that unit `x` was approved and to close its card for `review/x`

#### Scenario: The conductor builds a unit again
- **WHEN** swb-1-conductor runs `crew unit run x construct "<words>"` on a unit in review
- **THEN** the command's output names the card for `review/x` to close

#### Scenario: A bolt lands
- **WHEN** main-level ops runs `crew bolt land y`
- **THEN** the conductor of the team that held `y` is told it landed and to close its card for `land/y`

### Requirement: A crew agent's card acts are in the run record
Each card a crew agent posts, updates, withdraws or closes in Pending You SHALL be an entry in its partition's run record, naming the row's object, the card's id in `Card`, and the key in `Key` when it is one of the four row keys. An entry SHALL NOT hold a card's title, summary or any other text written on it.

#### Scenario: A card posted and closed
- **WHEN** swb-1-conductor posts the card `review/x/abc1234` and later closes it
- **THEN** the run record has a `card.post` entry on `unit/x` with that key and the card's id, and a `card.close` entry with the same id

#### Scenario: The user's own sessions
- **WHEN** a Claude session crew did not start posts a Pending You card
- **THEN** nothing is written to crew's run record

### Requirement: The rail shows each row's card
`crew rail` SHALL print, under each row, the row's card key and whether a card with that key is open, and whose it is. A card is open from its `card.post` entry until a `card.close` entry for the same card.

#### Scenario: A row with its card
- **WHEN** unit `x` is in review at `abc1234` and swb-1-conductor's card `review/x/abc1234` is open
- **THEN** the row's card line names `review/x/abc1234` as open, asked by `swb-1-conductor`

#### Scenario: A row without a card
- **WHEN** a proposal is open and no card has been posted for it
- **THEN** the row's card line names `proposal/<n>` with no card open

### Requirement: The rail names an open card whose row is gone
After its groups, `crew rail` SHALL list each open card that matches no row, with its key, its owner, when it was posted, and a pasteable `crew tell` asking the owner to close it. crew SHALL NOT close another agent's card itself.

#### Scenario: A forgotten card
- **WHEN** unit `x` was approved and swb-1-conductor's card `review/x/abc1234` was never closed
- **THEN** the rail lists `review/x/abc1234`, owned by swb-1-conductor, with `crew tell swb-1-conductor "Close your Pending You card review/x/abc1234: its row is gone."`

### Requirement: The conductor's tell to the operator agents is for what has no card
A conductor with Pending You's tools SHALL NOT tell the operator agents when it waits on the user for a review, a verify report or a landing, since that row's card reaches the user. It SHALL tell them when it waits on a question asked only in its pane, and for every wait when it has no Pending You tools.

#### Scenario: A unit reaches review
- **WHEN** a conductor with Pending You's tools has posted the card for a unit in review
- **THEN** it sends no tell to the operator agents for it

#### Scenario: A question in the pane
- **WHEN** a stage stops on a question for the user that only the conductor's pane holds
- **THEN** the conductor tells the operator agents in one line what it waits for and where
