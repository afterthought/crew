# Spec Delta

## MODIFIED Requirements

### Requirement: An entry names what it acted on and what that came from
An entry's `On` fields SHALL name each object the act touched, and its `From` fields each object the act came from, as typed names: `unit/<unit>`, `chore/<chore>`, `bolt/<bolt>`, `queue/<kit>`, `signals/<id>`, `team/<team>`, `agent/<name>`, `stage/<unit or chore>/<stage>`, `fix/<bolt>/<name>`.

#### Scenario: A unit queued from a signal
- **WHEN** a unit is added with `--signal <id>`
- **THEN** the `unit.add` entry has `On: unit/<unit>` and `From: signals/<id>`, and the route move's entry has `On: signals/<id>` and `On: unit/<unit>`

#### Scenario: A stage
- **WHEN** a unit's code stage starts in slot 2 of swb-1
- **THEN** the entry has `On: stage/<unit>/code`, `On: unit/<unit>` and `On: agent/swb-1-unit-2`

#### Scenario: A chore's stage
- **WHEN** a chore's verify starts in slot 1 of swb-1
- **THEN** the entry has `On: stage/<chore>/verify`, `On: chore/<chore>` and `On: agent/swb-1-unit-1`
