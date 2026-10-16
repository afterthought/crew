## MODIFIED Requirements

### Requirement: A proposal's card is drawn from the plan and the proposal
When crew raises or changes a proposal's card it SHALL read only the flywheel's branch and build every part of the card: its title "Plan change to <bolt or queue>: <counts>", no question and no proposal number; its summary, a sentence of what the planner proposes and why from the case; a paragraph per new unit and per dropped unit as inline Markdown on its face, the intent and a "Direction" line from the proposal's `Do` line and case, a dropped unit's with its why; its background; its boxes and its artifacts; and SHALL draw the card's picture, a PNG 1560 pixels wide at twice a phone's pixel density so it is sharp on a Retina screen, itself, with no browser, no other program and no agent.

#### Scenario: A proposal that drops, amends and adds
- **WHEN** crew raises the card for a proposal that drops one unit of bolt `y`, amends one and adds two
- **THEN** its title is "Plan change to y: 1 dropped, 1 amended, 2 new", its summary says what the planner proposes in a sentence, its face holds a paragraph for each new unit and the dropped one, and its picture is a PNG 1560 pixels wide

#### Scenario: Run on a host with no browser
- **WHEN** crew raises a proposal's card on a host where no browser and no image tool is installed
- **THEN** it draws the picture all the same

#### Scenario: A closed proposal
- **WHEN** a proposal is approved or dropped
- **THEN** its card is closed or withdrawn, and crew draws no card for it again

### Requirement: The change reads as text on a phone
The card's text artifact SHALL be the change in monospace lines of at most forty characters: the bolt and its unit count before and after, then one block per change headed by its kind (`DROP`, `AMEND`, `ADD`, `MOVE`, `ORDER`, `SPLIT`, `AFTER`, `NEW BOLT`, `ORDER BOLT`, `DROP BOLT`) with the unit or bolt and what it says, then the order once approved with each unit marked new (`+`), amended (`~`) or moved (`↕`). A name longer than a line SHALL wrap at its hyphens.

#### Scenario: The text of a proposal
- **WHEN** crew raises the card for a proposal that drops `a` with a reason and adds `c`
- **THEN** its text artifact holds a `DROP` block naming `a` with the reason, an `ADD` block naming `c` with its intent, and `ONCE APPROVED` listing `c` with `+`, and no line is longer than forty characters
