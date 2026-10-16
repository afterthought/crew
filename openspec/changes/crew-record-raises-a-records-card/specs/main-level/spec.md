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

### Requirement: The user's own words are their decision
What the user settled in their own words in the design talk SHALL be quoted in the record as their decision; when a card is raised for the record, it SHALL say which part that is, and when the user settled the whole record in the pane, their yes there SHALL be recorded and no card raised.

#### Scenario: The user's own words
- **WHEN** the user said in the design talk "the landing still needs my yes", and the record rests on it
- **THEN** the record quotes those words as the user's decision, and the card, when one is raised, says that part is the user's own
