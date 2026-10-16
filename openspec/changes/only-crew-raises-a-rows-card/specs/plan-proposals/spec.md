## ADDED Requirements

### Requirement: A proposal's card has no command of its own
There SHALL be no `crew plan card` command: a proposal's card is crew's, raised by `crew plan propose`.

#### Scenario: The command asked for
- **WHEN** an agent runs `crew plan card 4`
- **THEN** crew says it has no such command, and proposal 4's card is the one `crew plan propose` raised when the proposal was accepted
