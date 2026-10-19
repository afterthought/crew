## ADDED Requirements

### Requirement: A deploy held at a gate whose reviewer is the user waits as the user's step
A deploy a hosted deployer holds at a gate whose reviewer is the user SHALL be recorded by whoever dispatched it as a step that is the user's, waiting, the gate's link its text and the deploy's commit its `--to` when known, with no offer posted for it. Its rail row, the board's Operation lane and main-level ops's view SHALL say the deploy waits at its gate for the user.

#### Scenario: A stand dispatched to dev's gate
- **WHEN** a crew agent dispatches a run that waits at dev's gate, whose one reviewer is the user, and records `crew ops step dev --to 4f2a9c1 --key gate-38612817613 --doer user --state waiting --text <file holding the run's link>`
- **THEN** the rail shows the row `op/dev/<n>` under operations, saying the deploy of 4f2a9c1 to dev waits at its gate for the user with the gate's link, its card is raised, and no deploy offer is made for that commit

#### Scenario: The gate in the views
- **WHEN** the gate's step waits on dev
- **THEN** the board's Operation lane says it waits at its gate for the user, and main-level ops's view names it the gate of 4f2a9c1, not a step after 4f2a9c1

### Requirement: A gate's step ends when the gate is passed or rejected
A gate's step SHALL be recorded done when the deployer's run shows the gate passed, by whoever dispatched it, or by main-level ops on the user's Done; and declined when the gate is rejected or on the user's Skip. Its card SHALL close with that state, as every step's card does.

#### Scenario: The gate passed
- **WHEN** the deployer's run shows it has passed the gate, and its dispatcher records the step done
- **THEN** the step's card is closed as done, and its row leaves the rail

#### Scenario: The user taps Done
- **WHEN** the user approves at the gate and taps Done on the card
- **THEN** main-level ops runs the row's done command, and the card closes

#### Scenario: The gate rejected
- **WHEN** the user rejects the deployment at the gate and taps Skip on the card
- **THEN** main-level ops runs the row's decline command, and the card closes as declined
