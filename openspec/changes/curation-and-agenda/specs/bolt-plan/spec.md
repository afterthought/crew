# Spec Delta

## MODIFIED Requirements

### Requirement: Work is queued from a signal
`crew unit add … --signal <id>` SHALL be for what the user tells the planner directly. It SHALL be accepted from the planner only inside a proposal, and only for a signal the planner itself captured that has no standing move. When the unit is applied, the same commit SHALL add it with the signal as its source, `signals/<id>`, and record the signal's `route` move targeting the unit, as the user's hand. Any other signal named by an agent SHALL be refused: one with no move as not yet curated, one on the agenda by naming its item. A signal with any other standing move SHALL be refused for every caller, naming the move. The user at a shell MAY queue from any unmoved signal, in the flywheel's state or in the partition's first blueprints repo.

#### Scenario: A signal routed to work
- **WHEN** the user at a shell runs `crew unit add … --signal <id>` for a signal with no standing move
- **THEN** one commit on the flywheel's branch adds the unit with `Source: signals/<id>` and a `route` move for that signal, targeting the unit

#### Scenario: A signal in another blueprints repo
- **WHEN** the user at a shell queues a flywheel-next unit, whose design is in agentplot/blueprints, from an unmoved signal that is not on `madswan/main` and is in afterthought/blueprints, the partition's first blueprints repo
- **THEN** the signal is found in afterthought/blueprints, the unit's `Source` is `signals/<id>`, and the route move is in `moves.rec` on `madswan/main`, in the same commit as the unit

#### Scenario: A signal already moved
- **WHEN** the signal named has a standing move that put it on no agenda item, such as `drop` or `answered`
- **THEN** the command is refused, naming the move it has, and the plan is unchanged

#### Scenario: A meeting's signal
- **WHEN** the signal named was written by the daily pass in the blueprints repo and has no standing move
- **THEN** it is found there; the planner's proposal naming it is refused as not yet curated, and the user at a shell may queue from it, the unit and the move written on the flywheel's branch

#### Scenario: The user's word to the planner
- **WHEN** the user approves a proposal holding `unit add … --signal <id>` for a signal the planner captured from the user's words
- **THEN** one commit on the flywheel's branch adds the unit with `Source: signals/<id>` and a `route` move for that signal

#### Scenario: A conductor's signal
- **WHEN** the planner proposes `unit add … --signal <id>` for a signal a conductor captured
- **THEN** the proposal is refused, saying the signal has not been curated

#### Scenario: A signal on the agenda
- **WHEN** the signal named was routed to plan item 8
- **THEN** the proposal is refused, saying to use `--item 8`
