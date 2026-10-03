# Spec Delta

## MODIFIED Requirements

### Requirement: Work is queued from a signal
`crew unit add … --signal <id>` SHALL be for what the user tells the planner directly. It SHALL be accepted from the planner only inside a proposal, and only for a signal the planner itself captured that has no standing move. When the unit is applied, the same commit SHALL add it with the signal as its source, `signals/<id>`, and record the signal's `route` move targeting the unit, as the user's hand. Any other signal named by an agent SHALL be refused: one with no move as not yet curated, one on the agenda by naming its item. The user at a shell MAY queue from any unmoved signal.

#### Scenario: The user's word to the planner
- **WHEN** the user approves a proposal holding `unit add … --signal <id>` for a signal the planner captured from the user's words
- **THEN** one commit on the flywheel's branch adds the unit with `Source: signals/<id>` and a `route` move for that signal

#### Scenario: A conductor's signal
- **WHEN** the planner proposes `unit add … --signal <id>` for a signal a conductor captured
- **THEN** the proposal is refused, saying the signal has not been curated

#### Scenario: A signal on the agenda
- **WHEN** the signal named was routed to plan item 8
- **THEN** the proposal is refused, saying to use `--item 8`
