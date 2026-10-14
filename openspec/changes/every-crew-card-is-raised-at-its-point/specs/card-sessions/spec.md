## MODIFIED Requirements

### Requirement: A session is started for a card's row by its key
crew SHALL start a plannotator reading session when it raises a batch's card, on the batch's folder, the reviewer's summary whole and every unit's whole change as read at its commit, given as one review, and when it raises the card of a proposal with more than fifteen new units, on the proposal's page; it SHALL put the session's link in the card's words first and among its links. `crew card session <key>` SHALL print the running session's link for `batch/<n>` or such a `proposal/<n>` again, and SHALL refuse any other key, saying that card has nothing to read.

#### Scenario: A batch card's session
- **WHEN** `crew review` cuts batch 3 of `x` and `z` on the main level's host
- **THEN** one plannotator session is running there on the batch's summary and both changes, no browser has opened, and the card carries its link of the form `http://<host's tailnet name>:<port>`

#### Scenario: A landing card
- **WHEN** the conductor runs `crew card session land/y`
- **THEN** it is refused: a landing card has nothing to read, and no session is started

### Requirement: A session is started only where its link can be answered
crew SHALL start no session, and SHALL raise the card without a link saying why, when the document is not on this host or when plannotator gives a link that names the host only for itself (`localhost` or a loopback address), ending that session.

#### Scenario: A link only the host can open
- **WHEN** plannotator gives batch 3's session a link on `localhost`
- **THEN** crew ends that session, raises the batch's card saying its reading could not be opened on the tailnet, and says so

### Requirement: The session's decision reaches the owner as the card's answer
`crew card wait batch/<n>` SHALL return when the batch's card is tapped or its session has the user's decision, whichever is first, print the card's note and every annotation word for word, close the card with the outcome, and end the session. A decision reached while nobody waited SHALL be returned by the next wait.

#### Scenario: Annotated in the session
- **WHEN** the user sends batch 3's session with two annotations and the planner runs `crew card wait batch/3`
- **THEN** the command prints both annotations, the card is closed "Read; 2 notes sent to their teams", and the session is ended

### Requirement: The session ends when its card closes
When crew closes or withdraws a card, the session started for its key SHALL be ended; the rail's sweep SHALL end the session of any closed card or gone row. crew SHALL end only a plannotator process it started for that key, and only while plannotator lists that process as serving that document.

#### Scenario: A batch card tapped on the phone
- **WHEN** the user taps batch 3's card and the planner's wait returns
- **THEN** the session for `batch/3` is no longer running, and its link no longer opens
