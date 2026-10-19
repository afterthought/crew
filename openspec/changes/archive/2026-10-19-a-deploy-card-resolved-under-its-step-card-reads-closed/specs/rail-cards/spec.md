## ADDED Requirements

### Requirement: A card Pending You has ended reads closed to crew
crew SHALL read a card of its own as ended once Pending You reports it `resolved`, `cancelled` or `expired`, recording a resolved card closed and a cancelled or expired one withdrawn, and SHALL send it no change and no close from then on. A change SHALL post the card's next version as a new card under its key's next revision, following the old card if it was resolved and nothing if it was cancelled or expired.

#### Scenario: A card the user dismissed while crew held it open
- **WHEN** crew goes to change or close its card under `land/b1`, and Pending You reports it `cancelled`
- **THEN** crew records the card withdrawn as ended in Pending You already, sends no `update_request`, `ack_answer` or `cancel_request`, and a change posts its new version under `land/b1:2`, following nothing

#### Scenario: A question already ended when its asker is gone
- **WHEN** the rail's read withdraws crw-3-conductor's question after crw-3's team closed, and Pending You reports the question `resolved`
- **THEN** crew records it closed as ended in Pending You already, and sends no `cancel_request`

### Requirement: A post that follows an open card reads it
When crew posts a card that follows a card of the same owner the run record still holds open, it SHALL read that card once the post is made, and SHALL record it closed if Pending You has ended it, as Pending You does for an answered card a new card follows. A read that fails SHALL leave the post standing and the followed card as the record holds it.

#### Scenario: A deploy card picked up by its step's card
- **WHEN** the user has approved `deploy/mac-studio`'s card, its deploy records a step that is the user's, and crew posts `op/mac-studio/1`'s card following the deploy's card, which Pending You then reports `resolved`
- **THEN** the run record holds the deploy's card closed, and the rail shows mac-studio with no open deploy card

#### Scenario: The deploy's end after its card was picked up
- **WHEN** the deployer records the end of that deploy
- **THEN** crew finds no open card under `deploy/mac-studio`, sends Pending You nothing, and records no refused close

#### Scenario: The next offer to that environment
- **WHEN** the deployer then offers mac-studio d35fbf2
- **THEN** crew posts a new card under `deploy/mac-studio`'s next revision, following the card a deploy's card follows when its last one closed, and the user can approve it, as they could deneb's offer of d35fbf2

#### Scenario: A card followed while it still waits
- **WHEN** crew posts a card following one of its own that Pending You still reports `pending` or `answered` after the post
- **THEN** the followed card stays open in the run record, for the event that ends it to close
