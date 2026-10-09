# Spec Delta

## MODIFIED Requirements

### Requirement: The owner of a row posts its card
When an agent crew started has Pending You's tools, it SHALL post one card for each row it owns: the planner for each proposal it opens, a conductor for each of its team's units in review, for each verify report its team's units wait on the user for, and for its bolt once the bolt is proven, or proven but for steps only the user can take. It SHALL post no second card for a row that has one open. A team's cards SHALL be its conductor's: its ops and every stage agent SHALL post no card, and no crew agent SHALL post a card that is not a row's.

#### Scenario: A proposal opened
- **WHEN** the planner opens proposal 4 in a session with Pending You's tools
- **THEN** one card keyed `proposal/4` is open, asked by the planner

#### Scenario: No Pending You
- **WHEN** a conductor's session has no Pending You tools and a unit reaches review
- **THEN** no card is posted, the unit's rail row is as before, and the conductor tells the operator agents it waits on the user

#### Scenario: A proof leaves the user a check
- **WHEN** brd-2's ops finishes its proof with every item green but one check only the user can make on their Mac
- **THEN** ops writes that check in its proof file and posts no card, and the user gets one card for it, the conductor's landing card for the bolt

### Requirement: A card says whose it is and where it belongs
A card SHALL be asked in the agent's crew name, with its host as the session's machine and its worktree as the session's folder. It SHALL be filed in the area of its kit, found by the kit's git remote, in the group named for its partition. An agent that finds no area for its kit SHALL create it with the key `create-area:<owner>/<kit>`, the kit's repository, and with no other key. Its title SHALL name what it asks and its bolt. An agent SHALL never create a group.

#### Scenario: A review card
- **WHEN** swb-1-conductor posts the card for unit `x` of bolt `y` in switchboard-kit
- **THEN** the card is asked by `swb-1-conductor` on its host, sits in switchboard-kit's area in the `wldn` group, and its title names unit `x` and bolt `y`

#### Scenario: The first card in a kit
- **WHEN** no area matches the kit `WilldanGroup/switchboard-kit`
- **THEN** the agent creates it once, with the key `create-area:WilldanGroup/switchboard-kit`, so two agents posting at the same time make one area

## ADDED Requirements

### Requirement: ops writes a proof's steps for the user in its proof file
When a bolt's proof leaves steps only the user can take or check, ops SHALL write each in its proof file as a step the user can do from a card: where, what to do or paste, and what they will see when it worked. ops SHALL post no card for them.

#### Scenario: One check left for the user
- **WHEN** ops's proof of bolt `y` is clean but for a gateway check on the user's Mac
- **THEN** the proof file holds that check as a step for the user, marked as waiting on the user, and ops posts no card

### Requirement: The landing card asks the proof's steps before approval
The conductor SHALL post the bolt's landing card once the proof is clean, or clean but for the user's steps, with those steps on it ahead of the approval. Approving it SHALL mean the user took them, they worked, and the bolt may land. A step the user says failed SHALL be a defect fixed on the bolt before the landing is asked again.

#### Scenario: Landing with one check left
- **WHEN** ops's proof of bolt `y` is clean but for a gateway check on the user's Mac
- **THEN** the conductor posts one high-stakes card keyed `land/y/<head>` whose first words and steps are that check, and an approval on it tells main-level ops to land `y`

#### Scenario: The check fails
- **WHEN** the user answers the landing card for `y` with a note that the gateway check is red
- **THEN** the conductor does not ask main-level ops to land `y`, closes the card with that outcome, and runs a fix on the bolt

#### Scenario: A clean proof
- **WHEN** ops's proof of bolt `y` leaves nothing for the user
- **THEN** the landing card for `y` asks only for approval, as before

### Requirement: crew refuses a crew agent's card under any key but a row's of its own
Before a Pending You card is posted from a session crew started, crew SHALL refuse it unless its idempotency key is the card key of a rail row the agent owns: for the planner, `proposal/<n>` for an open proposal of its partition; for a conductor, `review/<unit>/<head>` or `verify/<unit>/<stamp>` for a unit of the bolt its team holds, or `land/<bolt>/<head>` for that bolt. Every other crew agent SHALL own no key. A refused card SHALL NOT reach Pending You, and its refusal SHALL name the keys to use.

#### Scenario: ops posts a card
- **WHEN** brd-2-ops calls Pending You's `post_request` under any key
- **THEN** the call is refused before it reaches Pending You, and the refusal says ops owns no key: a team's cards are its conductor's, and what is left for the user goes in the proof file

#### Scenario: A conductor posts under a key of its own making
- **WHEN** brd-2-conductor, whose team holds bolt `y`, posts a card keyed `gateway-check-y`
- **THEN** the call is refused, and the refusal names `land/y/<head>` and the review and verify keys of `y`'s units, read from `crew rail`

#### Scenario: A conductor posts another team's row
- **WHEN** brd-2-conductor posts a card keyed `review/z/abc1234` for a unit `z` of a bolt another team holds
- **THEN** the call is refused, naming the keys that are brd-2-conductor's

#### Scenario: The planner posts a proposal's card
- **WHEN** wldn-planner posts a card keyed `proposal/4` while proposal 4 of `wldn` is open
- **THEN** the call goes through, and the card is recorded as before

### Requirement: crew refuses a crew agent's area under any key but the kit's
Before an area is created from a session crew started, crew SHALL refuse it unless its key is `create-area:<owner>/<kit>` for a kit the agent's team builds, or, for an agent of the main level, a kit of its partition's teams. The refusal SHALL name that key.

#### Scenario: An area under the agent's own key
- **WHEN** brd-2-conductor creates switchboard-kit's area with the key `area:brd-2-conductor`
- **THEN** the call is refused before it reaches Pending You, naming `create-area:WilldanGroup/switchboard-kit`

### Requirement: The check refuses what it cannot read, and only for crew's sessions
When crew cannot read the teams file, the plan or the proposals a card's or an area's check depends on, it SHALL refuse the call and name what it could not read. A session crew did not start SHALL NOT be checked.

#### Scenario: The plan cannot be read
- **WHEN** a conductor posts a card keyed `land/y/<head>` and the partition's state branch cannot be fetched
- **THEN** the call is refused, naming the branch that could not be read, and the conductor posts it again later

#### Scenario: The user's own session
- **WHEN** a Claude session crew did not start posts a Pending You card or creates an area under any key
- **THEN** crew neither checks nor refuses it
