## ADDED Requirements

### Requirement: A deploy's card carries the kit's release notes and steps as the deployer hands them
A deploy's card's face SHALL carry the kit's release notes for exactly the range since the environment's last deploy, as the deployer hands them to `crew ops offer --notes <file>`, as inline Markdown, and the range's after-deploy steps with their doer, the user's, an agent's or held, as a text list, as the deployer hands them with `--steps <file>`; crew SHALL write no notes of its own, and an offer handed none SHALL give the landings' subjects alone.

#### Scenario: A kit that hands no notes
- **WHEN** the deployer offers mac-studio `c882cff` with no `--notes` and no `--steps`
- **THEN** the card's face gives the landings since mac-studio's last deploy by subject, and says the kit handed no release notes

### Requirement: A step's card is the user's do
A step whose doer is the user SHALL be a `do` card with the step's words, where it is done, each command whole as an action step, what is seen when it worked, and the options Done, Skip and Later. A step an agent runs on its own SHALL have no card. When a deploy ends with more than one step for a card, crew SHALL raise one card at a time: the first following the deploy's card, each next one following the one before, raised when crew closes it.

#### Scenario: Two steps after one deploy
- **WHEN** srv's deploy ends with a step that is the user's and a step held for the user's word
- **THEN** one card is open, following the deploy's card, and the second is raised following the first when the first is closed

#### Scenario: A password only the user can rotate
- **WHEN** the deployer records a step with doer user and two commands
- **THEN** the card keyed `op/srv/1` is a `do` with both commands whole, where to run them, when it is done, and Done, Skip and Later

#### Scenario: A step an agent runs on its own
- **WHEN** the deployer records a step with doer main-ops, when quiet, not held
- **THEN** no card is raised, and the step runs at the quiet moment

### Requirement: A held step's card is a choice of when
A step an agent can do that the change marked held for the user's word SHALL be a choice between now, when the host is quiet (recommended) and skip, each with its consequence; the agent SHALL do it at once or at the quiet moment as the user picks, or record it declined on skip.

#### Scenario: A restart held for the user's word
- **WHEN** the deployer records a step with doer main-ops marked held
- **THEN** the card is a choice of now, when quiet and skip, when quiet recommended with "no stage is cut", now with the stages it cuts, and the step runs when the user picks
