## ADDED Requirements

### Requirement: A standing agent of a role that now runs as its kind is ended at its next stop
A standing agent whose partition now runs its role as its kind SHALL be ended at its next stop, once herdr reads it idle with no question open and no background work of its own but crew's waits, told that its role now runs as its kind, and started again by nothing: no restart, no `crew revive`, no `crew update`. Nothing SHALL be ended on a held host.

#### Scenario: The planner moves
- **WHEN** madswan's teams entry comes to name a stream for its planner while `madswan-planner` stands, and it ends its turn
- **THEN** `madswan-planner` is ended, its pane is left with no agent started in it, and its log says its role now runs as its kind

#### Scenario: An update after the move
- **WHEN** `crew update` runs on deneb after madswan's planner has moved
- **THEN** no planner of madswan is restarted or started
