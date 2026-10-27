## MODIFIED Requirements

### Requirement: A card the user answered is followed by its new version
When crew changes one of its own cards because its thing changed, it SHALL change the card in place while the card waits on the user. Once the user has answered the card, which Pending You no longer changes, crew SHALL ack it with the change note as its outcome and post the new version as a new card that follows it, in the same owner's name, saying first that the user answered the earlier card, when and with what, and what changed since, as every card that follows one the user answered says it. The run record SHALL hold the answered card's close, with the answer, and the new card's post, both under the row's key.

#### Scenario: A card waiting on the user
- **WHEN** crew changes its card `req_1` under `land/b1`, which waits on the user
- **THEN** `req_1` is changed in place with the change note

#### Scenario: A card the user answered
- **WHEN** crew changes its card `req_1` under `land/b1` after the user has answered it
- **THEN** `req_1` is acked with the change note, and a new card following `req_1` is posted, its summary opening with what the user answered on `req_1` and what changed. The run record has `req_1`'s close, with the answer, and the new card's post under `land/b1`, and `crew card read land/b1` finds the new card

## ADDED Requirements

### Requirement: A card that follows one the user answered says so first
Every card crew posts that follows a card the user answered SHALL open its summary, and its details, with one paragraph saying that the user answered the earlier card, when the earlier card was posted and by when crew recorded their answer, what they answered, and what has changed since, before anything else the card says, so a card asked again is never read as a repeat. A card the user answered is one the run record shows closed after their answer, declined among them, and one whose follow-on crew withheld (below). What they answered SHALL be the answer crew recorded at the earlier card's close; where the run record holds none, the paragraph SHALL say crew holds no record of what they answered. What changed SHALL be the sentences the event that raised the card gives: a record's new commit; a proposal's rewrite read against the proposal it replaces; a deploy's newer head; a step's place after the card it follows; what the user's send on a kit's landings card landed, held and left, and the bolts proven or moved since.

#### Scenario: A record revised after the user's note
- **WHEN** the user answered record 0019's card `req_1`, posted 2026-10-23 13:10 UTC, with a note, crew recorded it by 14:02 UTC, and the design agent revises the record at `4be21c0`
- **THEN** the card that follows `req_1` opens "You answered the card before this one, posted 2026-10-23 13:10 UTC, by 14:02 UTC: declined, with a note. Since then: revised at 4be21c0", with the commit's subject, before the record's own opening

#### Scenario: A proposal rewritten after the user's note
- **WHEN** the user answered proposal 239's card with a note and the planner rewrites it as proposal 241, which adds unit `x` and no longer adds unit `y`
- **THEN** the card that follows says first what the user answered and that proposal 241 adds `x` and no longer adds `y`

#### Scenario: A deploy offered again after the user declined it
- **WHEN** the user declined deneb's deploy of `ddcf2cb` and the deployer offers deneb `e104bcf`
- **THEN** the new deploy card follows the declined one and opens saying the user declined `ddcf2cb`, when, and that the offer is now `e104bcf`

#### Scenario: The landings card after a send that left a bolt
- **WHEN** the user sent `land/crew` with `y` ticked and `z` cleared, and `y` lands
- **THEN** the card that follows opens saying the user sent the earlier card, when, ticking `y` and leaving `z`, and that `y` landed and `z`, which they left, waits on this card

#### Scenario: An answer crew holds no record of
- **WHEN** a card that follows one the user answered is posted, and the run record's close of the earlier card holds no answer, as a close made before crew recorded answers
- **THEN** its opening says the user answered the earlier card, when, that crew holds no record of what they answered, and what changed since

### Requirement: A follow-on with nothing changed is not posted, the earlier answer standing
A card that follows one the user answered, for which the event that raised it gives nothing changed since the answer, SHALL NOT be posted: crew SHALL record it as a `card.post` under the row's key in its owner's name, refused in crew's own words naming the earlier card and saying its answer stands, with that card's id and the state `stands`, and SHALL refuse nothing of the event. The rail's card line SHALL show those words, and the rail's sweep SHALL NOT raise that row's card again; the next post under the row's key SHALL follow the card whose answer stands and SHALL be posted only when its event gives what changed since.

#### Scenario: A proposal rewritten with nothing changed
- **WHEN** the user answered proposal 239's card and the planner rewrites it as proposal 240 with the same commands and the same case
- **THEN** no card is posted for proposal 240; the run record has a `card.post` under the proposal's key, refused in crew's words naming 239's card and saying its answer stands, state `stands`; and `crew rail` shows the row with those words

#### Scenario: A deploy offered again at the head the user declined
- **WHEN** the user declined deneb's deploy of `ddcf2cb` and the deployer offers deneb `ddcf2cb` again with the same notes and steps
- **THEN** no card is posted, and the decline stands

#### Scenario: The sweep meets a withheld card
- **WHEN** proposal 240's card was withheld and the rail is read on the planner's host
- **THEN** the sweep raises no card for proposal 240's row, and records nothing more

#### Scenario: Something changes after a withheld card
- **WHEN** proposal 240's card was withheld and the planner rewrites it as proposal 242, which adds unit `w`
- **THEN** proposal 242's card is posted following 239's card, opening with what the user answered on it and that proposal 242 adds `w`

### Requirement: The close of an answered card records the answer
When crew closes one of its own cards that the user answered, it SHALL record on the close's entry what they answered as `Answer`, in crew's own words made from names alone: approved or declined; the options they picked, by the bolt, unit or choice each names; done, a failed step, or that they will handle it themselves; and "with a note" when they wrote one, never the note's words (`record.3`). A card answered in a conversation, closed as answered there, SHALL record that it was answered in a pane.

#### Scenario: A landings card sent with ticks
- **WHEN** the user sends `land/crew` with `land:y` ticked, `land:z` cleared and a note, and crew closes it
- **THEN** the close's entry holds `Answer: ticked y, left z, with a note`, and none of the note's words

#### Scenario: A deploy declined
- **WHEN** the user declines deneb's deploy card with the words "not tonight" and crew closes it
- **THEN** the close's entry holds `Answer: declined, with a note`
