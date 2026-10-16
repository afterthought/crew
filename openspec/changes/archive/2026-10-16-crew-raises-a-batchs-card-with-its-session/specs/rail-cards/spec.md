## MODIFIED Requirements

### Requirement: A card carries what the user would read and the row's answers
A proposal's card SHALL hold the proposal whole, its picture, its text and its case, and SHALL carry a reading session's link only when it holds more than fifteen new units. A batch's card SHALL carry its one session's link. A landing's, a deploy's, a step's and a record's card SHALL carry no link to a session: each holds what the user decides from.

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

#### Scenario: A landing card has nothing to read
- **WHEN** crew raises bolt `y`'s landing card
- **THEN** it names the units and chores that land, sluice's verdict and when, and how far main has moved, and carries no link to a reading session

### Requirement: A batch's card is a notice naming every unit
A batch's card, keyed `batch/<n>`, SHALL be a Pending You notice (`fyi`) crew raises when the reviewer delivers the batch's summary, that asks nothing: no options, no question, no approval and no steps. Its title SHALL say what the batch is about, drawn from its units' subjects, with the batch's number after; its summary SHALL say first "N changes to read, nothing to approve", since the batch before it when there is one; its words SHALL say where notes go, the reading session or the card's own note, that each reaches its unit's team as the user's words, and that the units go on building whatever the user does with the card. The reviewer's summary SHALL ride the face as inline Markdown, a paragraph per unit under its name and team.

#### Scenario: A card of six units
- **WHEN** crew raises the card for batch 2 holding six units
- **THEN** the card is one `fyi` titled with batch 2, whose summary opens "6 changes to read, nothing to approve", whose words say the units go on building, whose face and background name all six units with their teams and paragraphs, and whose one link opens the batch's session

## REMOVED Requirements

### Requirement: A card's link and bolt come first
**Reason**: folded into "A card carries what the user would read and the row's answers" and "A batch's card names every unit and links its session".
