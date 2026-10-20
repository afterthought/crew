## MODIFIED Requirements

### Requirement: Every decision is a marker on its object
Every marker the board's read gives SHALL be drawn on its object's form, never as a form of its own: ✓ for an approval (an open proposal, a bolt to land), ✎ for an answer (a verify report not yet answered), ! for attention (a held bolt every unit of which has landed). Each marker SHALL say whether its card is open and who asked it, and, when none is open and its last post was refused, that its post was refused, with Pending You's words where the marker is pointed at. The board view SHALL hold no button, link or command that answers or moves anything.

#### Scenario: A proposal waiting
- **WHEN** proposal 4 is open and wldn-planner has its card open
- **THEN** proposal 4's sheet carries ✓ and says its card is open, asked by wldn-planner, and nothing on the page approves it

#### Scenario: A deploy whose card was refused
- **WHEN** a deploy of deneb waits on the user's word and Pending You refused its card's last post
- **THEN** the deploy's marker says it has no card, its post refused, and pointing at it shows Pending You's words
