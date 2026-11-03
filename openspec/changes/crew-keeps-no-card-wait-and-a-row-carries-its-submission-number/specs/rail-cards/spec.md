## MODIFIED Requirements

### Requirement: An answer wakes the owner, which acts on the user's word
An answer on a crew card SHALL be acted on by the role whose row it is, woken in its session by the card it adopted, and by no other: the planner applies or rewrites the proposal, and reads a batch's answer with `crew card read batch/<n>`; main-level ops lands the bolts the user ticked on a kit's landings card, in the card's order, and passes a note naming a defect in a bolt to that bolt's conductor, who starts a fix on it; main-level ops runs the deploy's approval or the step's state; the design agent sets the record's status. crew SHALL then close the card at that act's event. No process of crew's SHALL wait on a card's answer.

#### Scenario: A proposal approved from the phone
- **WHEN** the user approves the card for proposal 4 on the phone
- **THEN** the planner is woken, runs `crew plan answer` and `crew plan approve 4`, which closes the card with what was applied, and the rail's proposal row is gone

#### Scenario: Changes asked for on a review card
- **WHEN** the user writes a note on a batch's card asking for changes to unit `x`
- **THEN** the planner is woken, `crew card read batch/<n>` prints the note and closes the card, the conductor runs construct again with its words, and no approval is asked

#### Scenario: Landing approved
- **WHEN** the user leaves `a` and `c` ticked on `land/crew`, clears `b`, and sends
- **THEN** swancloud-ops is woken, `crew card read land/crew` prints `a` then `c` and the command that lands them in that order, and no conductor is asked to pass anything on

#### Scenario: A defect noted on a row
- **WHEN** the user's note on `land/crew` names a defect in bolt `b`
- **THEN** swancloud-ops tells `b`'s conductor the note's words, the conductor starts a fix on `b`, and `b`'s row is held for the fix

### Requirement: A card carries what the user reads and the row's answers
A proposal's card SHALL hold the proposal whole, picture, text and case, linking a reading session only when it holds more than fifteen new units. A batch's card SHALL link its one session. A landing's card SHALL link its one session, on what the bolt brings to main, first in its details and among its links, saying the reading lands nothing. A deploy's, a step's and a record's card SHALL link no session: each holds what the user decides from.

#### Scenario: A review card's options
- **WHEN** a unit's change is due for a batch
- **THEN** no review card offers its approval; the batch's card asks nothing and its notes go to the unit's team

#### Scenario: A review card's link
- **WHEN** a unit's change is read in batch 3
- **THEN** the batch's card carries the one link to batch 3's session, and no card carries a link to the unit alone

#### Scenario: Answered in the session rather than on the card
- **WHEN** the user annotates a unit's change in the batch's session and sends the annotations
- **THEN** the rail's refresh tells the planner to read batch 3, its `crew card read batch/3` prints them, they go to the unit's conductor as the user's words, and the batch's card is closed

#### Scenario: A proposal's card holds the proposal whole
- **WHEN** crew raises the card for proposal 4, which adds two units
- **THEN** the card carries the picture, the text and the case, and no session link

#### Scenario: A landing card links its reading
- **WHEN** crew raises bolt `y`'s landing card
- **THEN** it names the units and chores that land, sluice's verdict and when, and how far main has moved, as before; its details open with the link to `land/y`'s session and say the reading lands nothing; the link is among its links, after which sluice's pull request when it has one; and it is an approval of risk high, the approval being the word to land

#### Scenario: A landing approved without opening its reading
- **WHEN** the user approves `land/y`'s card without opening its session
- **THEN** the conductor tells main-level ops to land `y` as before, and nothing waits on the session
