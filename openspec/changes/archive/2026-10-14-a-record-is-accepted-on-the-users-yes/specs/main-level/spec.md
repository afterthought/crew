## ADDED Requirements

### Requirement: A decision record is accepted only on the user's yes
Every decision record the design agent writes, and every amendment it makes to one, SHALL be committed as proposed and put to the user on one Pending You card in the record's own words. A record or an amendment SHALL become accepted only on the user's yes, recorded in the record with the date and any words the user added. Until the yes, a rule drawn from the record SHALL be written marked as proposed, and no unit SHALL be queued from it.

#### Scenario: A new record
- **WHEN** the design agent writes record 0021 in crew's `docs/adr/` after a design talk
- **THEN** it commits the record with the status proposed and posts one card asking the user to accept it, in the record's words, and queues no unit from it yet

#### Scenario: The user says yes
- **WHEN** the user approves the card for record 0021
- **THEN** the design agent commits the record as accepted by the user on that date, takes the proposed mark off each rule drawn from it, and only then queues the units it calls for

#### Scenario: An amendment to an accepted record
- **WHEN** the design agent amends record 0005, which is accepted
- **THEN** the amendment is marked proposed in the record, the card carries the amendment's words, and the amendment is accepted only on the user's yes

### Requirement: A record the user does not accept is revised or rejected
On a note asking for changes, the design agent SHALL revise the record, still proposed, and put it on a new card. On a no, it SHALL mark the record rejected, in the user's words, and take out the rules drawn from it.

#### Scenario: The user asks for changes
- **WHEN** the user answers the card with a note asking for a change
- **THEN** the design agent revises the record, commits it still proposed, closes the old card with what changed, and posts a new card for the new version

#### Scenario: The user says no
- **WHEN** the user rejects the card
- **THEN** the record's status becomes rejected with the user's words, and every rule drawn from it is taken out

### Requirement: The user's own words are their decision
What the user settled in their own words in the design talk SHALL be quoted in the record as their decision, and the record's card SHALL say which part that is.

#### Scenario: The user's own words
- **WHEN** the user said in the design talk "the landing still needs my yes", and the record rests on it
- **THEN** the record quotes those words as the user's decision, and the card says that part is the user's own
