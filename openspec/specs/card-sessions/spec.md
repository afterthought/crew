# card-sessions Specification

## Purpose
A card that asks the user to read something links a plannotator session on that document, started by the card's owner on its own host without opening a browser there, reachable wherever the card is answered; what the user decides in the session reaches the owner as the card's answer, and the session ends when the card closes.

## Requirements

### Requirement: A session is started for a card's row by its key
`crew card session <key>` SHALL start a plannotator review, on the host it runs on, of the document the rail row with that card key asks the user to read: the proposal's page for `proposal/<n>`, the unit's change folder for `review/<unit>/<head>`, and the verify report for `verify/<unit>/<stamp>`. The session SHALL offer an Approve button and SHALL NOT open a browser on the host, and the command SHALL print the session's link.

#### Scenario: A review card's session
- **WHEN** swb-1-conductor runs `crew card session review/x/abc1234` while unit `x` is in review at `abc1234` on its host
- **THEN** a plannotator session on `x`'s change folder (its proposal, design, specs and tasks) is running on that host, no browser has opened there, and the command prints a link of the form `http://<host's tailnet name>:<port>`

#### Scenario: A proposal card's session
- **WHEN** the planner runs `crew card session proposal/4`
- **THEN** a session is running on proposal 4's page as `crew plan proposed 4` prints it, and its link is printed

### Requirement: A session is started only where its link can be answered
`crew card session` SHALL refuse, naming why and leaving no session running: a key that matches no rail row of the caller's partition, a `land/<bolt>` key, a document that is not on this host, and a session whose link names the host only for itself (`localhost` or a loopback address).

#### Scenario: A key whose row is gone
- **WHEN** the conductor runs `crew card session review/x/abc1234` after construct ran again and `x` is in review at `def5678`
- **THEN** it is refused as a key with no row, and no session is started

#### Scenario: A landing card
- **WHEN** the conductor runs `crew card session land/y`
- **THEN** it is refused: a landing card has no document to read

#### Scenario: A link only the host can open
- **WHEN** plannotator gives the session a link on `localhost`
- **THEN** crew ends that session, refuses, and says the link would open only on this host

### Requirement: One session per card key
While a session started for a key is running, `crew card session <key>` SHALL start nothing and print that session's link again.

#### Scenario: Run again after a restart
- **WHEN** the conductor restarts and runs `crew card session review/x/abc1234` while the session it started before is still running
- **THEN** the command prints the same link, and one session runs for that key

### Requirement: The session's decision reaches the owner as the card's answer
`crew card wait <key>` SHALL return when the session for that key has a decision from the user, or has ended without one, and print which: approved, with any notes the user gave; annotated, with the feedback and every annotation the user wrote, word for word; closed by the user with no decision; or ended with no decision. A decision reached while nobody waited SHALL be returned by the next wait for that key. A wait for a key with no session started SHALL be refused.

#### Scenario: Approved in the session
- **WHEN** the user opens the review card's link on the phone and presses Approve
- **THEN** the conductor's `crew card wait review/x/abc1234` returns `approved`, and the conductor acts on it as an approval on the card

#### Scenario: Annotated in the session
- **WHEN** the user annotates two passages of the design and sends them as feedback
- **THEN** the wait returns `annotated` with both annotations and the user's words, and the conductor runs construct again with them

#### Scenario: Decided while the owner was down
- **WHEN** the user approves in the session while the conductor is restarting, and the restarted conductor runs `crew card wait` for that key
- **THEN** the wait returns `approved` at once

#### Scenario: Closed with no decision
- **WHEN** the user closes the session without approving or sending feedback
- **THEN** the wait returns that the session was closed with no decision, and the card is still the user's to answer

### Requirement: The session ends when its card closes
When a crew agent closes or withdraws a card keyed with a row key, the session started for that key on that host SHALL be ended. `crew card end <key>` SHALL end it as well. crew SHALL end only a plannotator process it started for that key, and only while plannotator lists that process as serving that document; a key with no session ends nothing and is not an error.

#### Scenario: A review card closed after approval
- **WHEN** the conductor approves unit `x` on the card's answer and closes card `review/x/abc1234` with `ack_answer`
- **THEN** the plannotator session for `review/x/abc1234` is no longer running, and its link no longer opens

#### Scenario: A card withdrawn when its row ends
- **WHEN** the planner withdraws card `proposal/4` because proposal 5 replaced it
- **THEN** the session for `proposal/4` is ended

#### Scenario: A process that is not crew's
- **WHEN** the process recorded for a key is no longer a plannotator session on that key's document
- **THEN** crew kills nothing and forgets the key's session
