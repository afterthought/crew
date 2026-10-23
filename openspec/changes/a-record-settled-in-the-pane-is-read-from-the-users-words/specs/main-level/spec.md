## MODIFIED Requirements

### Requirement: A record's card is raised unless it was settled in the pane
`crew record <kit> <number> --proposed` SHALL put the record at its commit on its card in the design agent's name, raising the card the first time and changing it in place at each new commit, unless `--settled-in-pane --excerpt "<words>"` says the user settled it in the pane; with `--alternatives <file>`, which hands the Markdown of the alternatives a rule of the user's decided between, the rules and each loosened, the card SHALL be a choice.

#### Scenario: A record a rule decided
- **WHEN** the design agent runs `crew record switchboard-kit 32 --proposed --alternatives docs/adr/0032-alternatives.md`
- **THEN** the card is a choice of loosening the rules as drafted, accepting as ruled, or sending back, with the file on its face, and the design agent is woken by the answer

#### Scenario: A record settled in the pane
- **WHEN** the user says "Yes, accept 31 as written" in the design agent's pane, and the design agent commits record 31 as proposed and runs `crew record crew 31 --proposed --settled-in-pane --excerpt "Yes, accept 31 as written"`
- **THEN** the status is recorded with the user's yes as given in the pane, naming the transcript record the words came from and not the words, and no card is raised

## ADDED Requirements

### Requirement: A record settled in the pane takes the user's words, read as theirs
`crew record … --proposed --settled-in-pane` SHALL record the record settled in the pane only from the user's words, given with `--excerpt`, which crew reads in the caller's own session transcript on this host as the user's (`signals.5`), and only when the caller is the partition's design agent. Otherwise it SHALL refuse with the reason, record nothing and raise no card. Either flag without the other SHALL be refused.

#### Scenario: The design agent's own words
- **WHEN** the design agent runs `crew record crew 31 --proposed --settled-in-pane --excerpt "<words>"`, and the words are only in what the design agent wrote itself
- **THEN** crew refuses, saying only the user's own words in the pane settle a record and to run `crew record crew 31 --proposed` so the user answers on its card, and records nothing

#### Scenario: Another agent's tell of the user's yes
- **WHEN** the words are in the design agent's transcript only in a `[crew tell from swancloud-planner]` message
- **THEN** crew refuses, naming swancloud-planner as the one who said them, and records nothing

#### Scenario: Words crew cannot read as anyone's
- **WHEN** the words are only in crew's own message, in a tool's output, or in a record crew can't classify
- **THEN** crew refuses, saying which, and records nothing

#### Scenario: A transcript crew cannot read
- **WHEN** the caller's session has no transcript on this host, its transcript can't be read, or it has not been written for more than 15 minutes
- **THEN** crew refuses with that reason and records nothing

#### Scenario: Another caller
- **WHEN** an agent other than the partition's design agent, or the user at a terminal, runs `crew record … --proposed --settled-in-pane --excerpt "<words>"`
- **THEN** crew refuses, saying only the design agent records a record settled in its pane, and records nothing

#### Scenario: A flag without the other
- **WHEN** `--settled-in-pane` is given without `--excerpt`, or `--excerpt` without `--settled-in-pane`
- **THEN** crew refuses, naming the flag that is missing, and records nothing
