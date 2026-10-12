# Spec Delta

## MODIFIED Requirements

### Requirement: A session is started for a card's row by its key
`crew card session <key> [<unit>]` SHALL start a plannotator review of the document the rail row with that card key asks the user to read: the proposal's page for `proposal/<n>`, the verify report for `verify/<unit>/<stamp>`, and, for `batch/<n>` with one of the batch's units named, that unit's whole change folder (its proposal, design, specs and tasks). A batch card posted before one card per batch was built, keyed `batch/<n>-<k>`, SHALL be read the same way for the units that card holds. A batch card's session SHALL run on the host the teams file names for the unit's team, where the unit's kit is; every other session on the host the command runs on. The session SHALL offer an Approve button and SHALL NOT open a browser on the host, and the command SHALL print the session's link.

#### Scenario: A batch card's sessions
- **WHEN** the planner runs `crew card session batch/3 x` and `crew card session batch/3 z`, for two units of the batch in teams on its host
- **THEN** two plannotator sessions are running, one on `x`'s change folder and one on `z`'s, no browser has opened, and each command prints a link of the form `http://<host's tailnet name>:<port>`

#### Scenario: A unit the batch does not hold
- **WHEN** the planner runs `crew card session batch/3 w`, and `w` is not among the units of batch 3
- **THEN** it is refused, naming the units the batch holds, and no session is started

#### Scenario: A batch card posted under an old key
- **WHEN** the planner runs `crew card session batch/2-2 x` for an open card of batch 2 posted under that key, and `x` is among its units
- **THEN** a session on `x`'s change folder is running and its link is printed, as before

#### Scenario: A proposal card's session
- **WHEN** the planner runs `crew card session proposal/4`
- **THEN** a session is running on proposal 4's page as `crew plan proposed 4` prints it, and its link is printed

#### Scenario: A review card's session
- **WHEN** swb-1-conductor runs `crew card session review/x/abc1234`
- **THEN** it is refused as not a card key, since there is no review row, and no session is started

### Requirement: A session is started only where its link can be answered
`crew card session` SHALL refuse, naming why and leaving no session running: a key that matches no rail row of the caller's partition, a batch key without a unit, a `land/<bolt>/<head>` key, a document that is not on the host the session would run on, and a session whose link names the host only for itself (`localhost` or a loopback address).

#### Scenario: A key whose row is gone
- **WHEN** the planner runs `crew card session batch/3 x` after batch 3's card was closed
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
- **WHEN** the planner restarts and runs `crew card session batch/3 x` while the session it started before is still running
- **THEN** the command prints the same link, and one session runs for `x` on that card
