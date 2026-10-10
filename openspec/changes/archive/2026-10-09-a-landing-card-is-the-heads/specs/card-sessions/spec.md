# Spec Delta

## MODIFIED Requirements

### Requirement: A session is started only where its link can be answered
`crew card session` SHALL refuse, naming why and leaving no session running: a key that matches no rail row of the caller's partition, a `land/<bolt>/<head>` key, a document that is not on this host, and a session whose link names the host only for itself (`localhost` or a loopback address).

#### Scenario: A key whose row is gone
- **WHEN** the conductor runs `crew card session review/x/abc1234` after construct ran again and `x` is in review at `def5678`
- **THEN** it is refused as a key with no row, and no session is started

#### Scenario: A landing card
- **WHEN** the conductor runs `crew card session land/y/abc1234`
- **THEN** it is refused: a landing card has no document to read

#### Scenario: A link only the host can open
- **WHEN** plannotator gives the session a link on `localhost`
- **THEN** crew ends that session, refuses, and says the link would open only on this host
