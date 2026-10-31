## ADDED Requirements

### Requirement: A question is asked by three roles in their own name
The planner, main-level ops and the design agent MAY post a card for a question of their own through Pending You's own tools in their session, under an idempotency key of their own that is no row's, shaped as they see fit. The operator agent SHALL post none, the user being in its pane.

#### Scenario: The planner asks
- **WHEN** wldn-planner calls `post_request` with the key `ask/wldn-planner/hold-the-macs` and three options
- **THEN** the call goes through, and the run record has a `card.post` entry on the planner with that key and the card's id

#### Scenario: A question with a words answer
- **WHEN** the design agent's question card asks for the user's words in a `text` question
- **THEN** the call goes through: a question's form is its asker's

### Requirement: crew refuses a question card from any role but the three, or under a row's key
crew SHALL refuse a post, change or close from any role but the three, naming them, and a crew agent's own post, change or close under a row's key or of a row's card, naming the card as crew's; it SHALL refuse nothing else of a question's form. A post's key SHALL be judged by its form alone, with or without `:<n>` or the fill of a short key; a change's or a close's, which carries a request id, by the card this host's run record holds under that id, crew's raises and the agents' own posts alike.

#### Scenario: An agent posts a landing card by hand
- **WHEN** wldn-ops calls `post_request` with the key `land/y`
- **THEN** the call is refused, saying the landing card is crew's and is raised when the bolt reads proven

#### Scenario: An agent posts under a row's key as crew sends it
- **WHEN** wldn-ops calls `post_request` with the key `land/b1_`, or wldn-planner with `batch/7_` or `batch/7:2`
- **THEN** the call is refused, saying the card is crew's

## REMOVED Requirements

### Requirement: The conductor's tell to the operator agents is for what has no card
**Reason**: Record 0047 move 5, record 0050 part 3: no conductor, and no operator agents of a team to tell.
**Migration**: A question with no card goes to the partition's operator by `crew send` or `crew tell`, as any role's.

### Requirement: A take-main fix holds its row as taking main first
**Reason**: Record 0047 move 5, record 0050 part 3: no team's take-main fix; a landing's conflict with main is answered as the crossed path answers it.
**Migration**: The crossed path's fix of a bolt (`teams-cross-to-flume-as-their-bolts-land`).

### Requirement: Ticking a left bolt that conflicts with main starts its take-main fix
**Reason**: Record 0047 move 5, record 0050 part 3: no team's take-main fix is started by a tick.
**Migration**: The crossed path's fix of a bolt (`teams-cross-to-flume-as-their-bolts-land`).

### Requirement: A question is asked by four roles in their own name
**Reason**: Record 0047 move 5: the conductor is no longer among those who ask, and no stage agent, team ops or dispatcher of crew's is left to refuse (`briefs.11`).
**Migration**: "A question is asked by three roles in their own name", added by this change.

### Requirement: crew refuses a question card from any other role or under a row's key
**Reason**: Record 0047 move 5: no stage agent of crew's asks its conductor, and no conductor posts.
**Migration**: "crew refuses a question card from any role but the three, or under a row's key", added by this change.
