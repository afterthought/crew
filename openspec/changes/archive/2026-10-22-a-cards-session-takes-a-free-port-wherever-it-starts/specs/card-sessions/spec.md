## ADDED Requirements

### Requirement: A session takes a free port of plannotator's range wherever it is started
crew SHALL start every card's reading session on a port range, so plannotator takes the first port in it no other session holds, whether crew runs in an agent's pane, in a shell outside any agent, or in a raise within another command. The range SHALL be the one the environment's `PLANNOTATOR_PORT` names when it names a range, and otherwise crew's own, 19432–19451.

#### Scenario: Started from a shell outside any agent
- **WHEN** the user runs `crew card session batch/13` on the main level's host from a shell whose environment names no `PLANNOTATOR_PORT`, while a landing card's session holds port 19432
- **THEN** batch 13's session starts on the next free port of 19432–19451, and the command prints its link on that port

#### Scenario: Started from an agent's pane
- **WHEN** a conductor's merge raises bolt `y`'s landing card in an agent whose environment names `PLANNOTATOR_PORT=19432-19451`, while two other sessions hold 19432 and 19433
- **THEN** `y`'s reading starts on 19434, and its card carries that link

#### Scenario: An environment naming one port
- **WHEN** crew starts a batch's session where `PLANNOTATOR_PORT` names the single port 19432
- **THEN** the session is started on crew's range, 19432–19451, not on that port alone

