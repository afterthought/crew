# Spec Delta

## MODIFIED Requirements

### Requirement: A session is started only where its link can be answered
`crew card session` SHALL refuse, naming why and leaving no session running: a key that matches no rail row of the caller's partition, a `batch/<n>-<k>` key without a unit, a `land/<bolt>/<head>` key, a document that is not on the host the session would run on, and a session whose link names the host only for itself (`localhost` or a loopback address).

#### Scenario: A key whose row is gone
- **WHEN** the planner runs `crew card session batch/3-1 x` after every card of batch 3 was closed
- **THEN** it is refused as a key with no row, and no session is started

#### Scenario: A landing card
- **WHEN** the conductor runs `crew card session land/y/abc1234`
- **THEN** it is refused: a landing card has no document to read

#### Scenario: A link only the host can open
- **WHEN** plannotator gives the session a link on `localhost`
- **THEN** crew ends that session, refuses, and says the link would open only on this host

### Requirement: One session per card key
While a session started for a key, and for a batch key a unit, is running, `crew card session` with that key and unit SHALL start nothing and print that session's link again.

#### Scenario: Run again after a restart
- **WHEN** the planner restarts and runs `crew card session batch/3-1 x` while the session it started before is still running
- **THEN** the command prints the same link, and one session runs for `x` on that card
