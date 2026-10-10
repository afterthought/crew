# Spec Delta

## ADDED Requirements

### Requirement: The operator agent posts no card
The operator agent SHALL post no Pending You card, whatever a Pending You reminder in its session says.

#### Scenario: Told of a landing
- **WHEN** a conductor tells the operator agent it waits on the user to land bolt `y`
- **THEN** the operator agent posts no card for it

### Requirement: The operator agent shows only a wait with no card
When told of a wait for a unit in review, a verify report or a landing, the operator agent SHALL read that row on the rail and send nothing when its card is open. A wait with no card, a question asked in a pane or a row whose card is not open, SHALL be shown as a herdr notification in the operator session, with one line to the user on what it needs and where.

#### Scenario: A landing whose card is open
- **WHEN** a conductor tells the operator agent it waits on the user to land bolt `y`, and the rail shows the landing row's card open
- **THEN** the operator agent posts no card and shows no notification for it

#### Scenario: A question in a pane
- **WHEN** a conductor tells the operator agent it waits on the user for a question asked only in its pane
- **THEN** the operator agent shows a herdr notification naming the conductor and what it waits for, tells the user in one line, and posts no card

#### Scenario: A row with no card open
- **WHEN** a conductor whose session has lost Pending You's tools tells the operator agent that unit `u` waits in review, and the rail shows no card open for its row
- **THEN** the operator agent shows a herdr notification for it, and posts no card
