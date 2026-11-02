## MODIFIED Requirements

### Requirement: An answer wakes the owner, which acts on the user's word
An answer on a crew card SHALL be acted on by the role whose row it is, woken in its session by the card it adopted, and by no other: the planner applies or rewrites the proposal, and reads a batch's answer with `crew card read batch/<n>`; main-level ops lands the bolts the user ticked on a kit's landings card, in the card's order, and passes a note naming a defect in a bolt to that bolt's conductor, who starts a fix on it; main-level ops runs the deploy's approval or the step's state; the design agent sets the record's status. crew SHALL then close the card at that act's event. No process of crew's SHALL wait on a card's answer. Where the role runs as its kind, the host's follower SHALL write an ask of the role for each change Pending You's notice names on a card in the role's name, once per version of the card, reading nothing of the card, and the role's next run SHALL read the card in the role's own name and act on it as the woken session would.

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

#### Scenario: A proposal approved while the planner runs as its kind
- **WHEN** madswan's planner runs as its kind, no run of it is live, and the user approves proposal 12's card on the phone
- **THEN** the host's follower, told by Pending You's notice, writes one ask of the planner naming the card's request, and the planner's next run reads the card in madswan-planner's name and runs `crew plan answer` and `crew plan approve 12`
