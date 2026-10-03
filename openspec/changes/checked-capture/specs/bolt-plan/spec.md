# Spec Delta

## MODIFIED Requirements

### Requirement: Work is queued from a signal
`crew unit add … --signal <id>` SHALL queue the unit with the signal as its source, `signals/<id>`, and SHALL record the signal's one move, `route`, targeting the unit, in `moves.rec` on the flywheel's branch, in the same commit as the unit. The signal SHALL be looked up on the flywheel's branch and then in the partition's first blueprints repo. A signal that is in neither, already moved, or whose move would fail `recfix --check` SHALL be refused, and nothing written.

#### Scenario: A signal routed to work
- **WHEN** the planner queues a unit from a signal
- **THEN** one commit on the flywheel's branch adds the unit with `Source: signals/<id>` and a `route` move for that signal

#### Scenario: A signal already moved
- **WHEN** the signal named already has its move
- **THEN** the command is refused, naming the move it has, and the plan is unchanged

#### Scenario: A meeting's signal
- **WHEN** the signal named was written by the daily pass in the blueprints repo
- **THEN** it is found there, and the unit and the move are written on the flywheel's branch
