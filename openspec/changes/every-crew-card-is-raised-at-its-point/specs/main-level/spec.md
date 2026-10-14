## ADDED Requirements

### Requirement: A record's status is recorded through crew, and its card raised when it was not settled in the pane
`crew record <kit> <number> --proposed|--accepted|--rejected [--settled-in-pane]` SHALL record the record's status with its commit in the run record, SHALL raise the record's card in the design agent's name on `--proposed` unless `--settled-in-pane` says the user settled it in the pane, SHALL change the card when `--proposed` is run again at a new commit, SHALL close it on `--accepted` or `--rejected` with the commit, and SHALL refuse a status the record's file does not hold at that commit.

#### Scenario: A record settled in the pane
- **WHEN** the design agent commits record 31 as proposed after the user settled it beside them and runs `crew record crew 31 --proposed --settled-in-pane`
- **THEN** the status is recorded with the user's yes as given in the pane, and no card is raised

#### Scenario: A record from the signals, accepted on its card
- **WHEN** the design agent runs `crew record crew 32 --proposed`, the user accepts the card, and the design agent commits it accepted and runs `crew record crew 32 --accepted`
- **THEN** the card was raised, and is closed with the accepting commit

#### Scenario: A status the file does not hold
- **WHEN** the design agent runs `crew record crew 32 --accepted` while the file at HEAD still says proposed
- **THEN** the command refuses, naming the file's status, and records nothing

## MODIFIED Requirements

### Requirement: A deploy and every operation are approved and recorded through crew
A kit's deployer SHALL ask crew for each deploy of a `manual` environment with `crew ops offer`, which SHALL raise the deploy's card in main-level ops's name, keyed `deploy/<env>`, change it when a newer head is offered, and tell main-level ops the card's id; the user's word SHALL be holding that card, recorded with `crew ops approve`. `crew ops record --act end` SHALL close the card with the deploy's outcome. `crew ops step` SHALL raise a step's card, keyed `op/<env>/<n>`, when the step's doer is the user or the step is marked held for the user's word, and SHALL close it when the step is recorded done or declined, or done by its agent after the user's now or quiet. `crew ops word` SHALL give the commit the word is for until that deploy's end is recorded. Every `crew ops` command SHALL run where the partition's main level runs.

#### Scenario: A deploy offered and approved
- **WHEN** the deployer offers srv a deploy of main's head and the user holds its card
- **THEN** main-level ops runs `crew ops approve`, the deployer deploys at its next run, and `crew ops record srv --act end` closes the card with each step's outcome

#### Scenario: A held step
- **WHEN** the deployer records a step whose doer is main-ops and marked held, after mac-studio's deploy
- **THEN** the rail shows it under operations with a card asking now, when quiet or skip, and the step runs when the user answers

#### Scenario: An operation the user is to take
- **WHEN** the deployer records a step whose doer is the user as waiting
- **THEN** the rail shows it under operations with its `do` card until it is recorded done or declined, and `crew ops steps` gives its latest state
