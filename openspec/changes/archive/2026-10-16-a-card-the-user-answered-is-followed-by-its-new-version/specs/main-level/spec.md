## MODIFIED Requirements

### Requirement: A record the user does not accept is revised or rejected
On a note asking for changes, the design agent SHALL revise the record, still proposed, commit it and run `crew record … --proposed` again, which closes the card the user answered with the new commit named and puts the revised record on a new card that follows it; a record revised while its card still waits on the user changes the card in place with the new commit named. On a no, it SHALL mark the record rejected, in the user's words, take out the rules drawn from it, and run `crew record … --rejected`, which closes the card.

#### Scenario: The user asks for changes
- **WHEN** the user answers the card with a note asking for a change
- **THEN** the design agent revises the record, commits it still proposed, and the card the user answered is closed, "Revised at …", naming the new commit, with a new card for the revised record following it

#### Scenario: The user says no
- **WHEN** the user rejects the card
- **THEN** the record's status becomes rejected with the user's words, every rule drawn from it is taken out, and the card is closed with the commit
