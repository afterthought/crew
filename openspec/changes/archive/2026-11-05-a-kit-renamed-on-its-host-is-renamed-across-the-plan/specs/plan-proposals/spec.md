## ADDED Requirements

### Requirement: A proposal's card draws a kit's rename
A proposal holding `kit rename <old> <new>` SHALL draw it on its card as a block of its own. The block SHALL name the old name and the new, the bolts and units the rename renames, and the started bolts among them. The card's picture SHALL show each renamed bolt under its new kit. A proposal whose changes add no unit SHALL stay a plain approval, the rename asking no question of its own.

#### Scenario: madswan's renames proposed
- **WHEN** madswan-planner proposes `kit rename flywheel-cloud boomdrive-cloud` and `kit rename tailrace timber`
- **THEN** its card draws two rename blocks, the first naming `you-sign-in-to-staging` as started and its unit, and the card is a plain approval
