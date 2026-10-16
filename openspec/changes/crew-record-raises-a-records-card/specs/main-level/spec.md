## ADDED Requirements

### Requirement: A record's status is recorded through crew
`crew record <kit> <number> --proposed|--accepted|--rejected` SHALL record the record's status with its commit in the run record, and SHALL refuse a status the record's file does not hold at that commit.

#### Scenario: A status the file does not hold
- **WHEN** the design agent runs `crew record crew 32 --accepted` while the file at HEAD still says proposed
- **THEN** the command refuses, naming the file's status, and records nothing

### Requirement: A record's card is raised unless it was settled in the pane
`crew record <kit> <number> --proposed` SHALL put the record at its commit on its card in the design agent's name, raising the card the first time and changing it in place at each new commit, unless `--settled-in-pane` says the user settled it in the pane; with `--alternatives <file>`, which hands the Markdown of the alternatives a rule of the user's decided between, the rules and each loosened, the card SHALL be a choice.

#### Scenario: A record a rule decided
- **WHEN** the design agent runs `crew record switchboard-kit 32 --proposed --alternatives docs/adr/0032-alternatives.md`
- **THEN** the card is a choice of loosening the rules as drafted, accepting as ruled, or sending back, with the file on its face, and the design agent is woken by the answer

#### Scenario: A record settled in the pane
- **WHEN** the design agent commits record 31 as proposed after the user settled it beside them and runs `crew record crew 31 --proposed --settled-in-pane`
- **THEN** the status is recorded with the user's yes as given in the pane, and no card is raised

### Requirement: A record's card is closed with its accepted or rejected status
`crew record <kit> <number> --accepted` or `--rejected` SHALL close the record's card with the commit that holds the status.

#### Scenario: A record from the signals, accepted on its card
- **WHEN** the design agent runs `crew record crew 32 --proposed`, the user accepts the card, and the design agent commits it accepted and runs `crew record crew 32 --accepted`
- **THEN** the card was raised, and is closed with the accepting commit

## MODIFIED Requirements

### Requirement: A decision record is accepted only on the user's yes
Every decision record the design agent writes, and every amendment it makes to one, SHALL be committed as proposed. A record or an amendment SHALL become accepted only on the user's yes, recorded in the record with the date and the user's words: given in the pane where the record was settled with them, or on the one card crew raises for it through `crew record` when it was not. Until the yes, a rule drawn from the record SHALL be written marked as proposed, and no unit SHALL be queued from it.

#### Scenario: A new record
- **WHEN** the design agent writes record 0021 in crew's `docs/adr/` from the signals, with the user not in its pane
- **THEN** it commits the record with the status proposed and runs `crew record crew 21 --proposed`, which raises one card asking the user to accept it, in the record's words, and queues no unit from it yet

#### Scenario: The user says yes
- **WHEN** the user approves the card for record 0021
- **THEN** the design agent commits the record as accepted by the user on that date, takes the proposed mark off each rule drawn from it, runs `crew record crew 21 --accepted`, which closes the card, and only then queues the units it calls for

#### Scenario: An amendment to an accepted record
- **WHEN** the design agent amends record 0005, which is accepted, with the user not in its pane
- **THEN** the amendment is marked proposed in the record, the card crew raises carries the amendment's words, and the amendment is accepted only on the user's yes

### Requirement: A record the user does not accept is revised or rejected
On a note asking for changes, the design agent SHALL revise the record, still proposed, commit it and run `crew record … --proposed` again, which changes the card in place with the new commit named. On a no, it SHALL mark the record rejected, in the user's words, take out the rules drawn from it, and run `crew record … --rejected`, which closes the card.

#### Scenario: The user asks for changes
- **WHEN** the user answers the card with a note asking for a change
- **THEN** the design agent revises the record, commits it still proposed, and the card is changed in place, "Revised: …", naming the new commit

#### Scenario: The user says no
- **WHEN** the user rejects the card
- **THEN** the record's status becomes rejected with the user's words, every rule drawn from it is taken out, and the card is closed with the commit

### Requirement: The user's own words are their decision
What the user settled in their own words in the design talk SHALL be quoted in the record as their decision; when a card is raised for the record, it SHALL say which part that is, and when the user settled the whole record in the pane, their yes there SHALL be recorded and no card raised.

#### Scenario: The user's own words
- **WHEN** the user said in the design talk "the landing still needs my yes", and the record rests on it
- **THEN** the record quotes those words as the user's decision, and the card, when one is raised, says that part is the user's own
