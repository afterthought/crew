## REMOVED Requirements

### Requirement: A card carries what the user would read and the row's answers
**Reason**: It held that a landing's card carries no link to a session; record 0031, amended 2026-10-19, has a landing's card link one reading of the bolt.
**Migration**: The requirement "A card carries what the user reads and the row's answers" below holds the same rules for the other cards, and the landing's link.

## ADDED Requirements

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
- **THEN** the planner's `crew card wait batch/3` returns them, they go to the unit's conductor as the user's words, and the batch's card is closed

#### Scenario: A proposal's card holds the proposal whole
- **WHEN** crew raises the card for proposal 4, which adds two units
- **THEN** the card carries the picture, the text and the case, and no session link

#### Scenario: A landing card links its reading
- **WHEN** crew raises bolt `y`'s landing card
- **THEN** it names the units and chores that land, sluice's verdict and when, and how far main has moved, as before; its details open with the link to `land/y`'s session and say the reading lands nothing; the link is among its links, after which sluice's pull request when it has one; and it is an approval of risk high, the approval being the word to land

#### Scenario: A landing approved without opening its reading
- **WHEN** the user approves `land/y`'s card without opening its session
- **THEN** the conductor tells main-level ops to land `y` as before, and nothing waits on the session
