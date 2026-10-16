## ADDED Requirements

### Requirement: A card whose session could not start is raised all the same
When crew raises a batch's card or a long proposal's and its session could not start, crew SHALL raise the card all the same, saying after its summary's first paragraph that its reading could not be opened on the tailnet, and why first in its details, and SHALL say why in the command's output.

#### Scenario: A unit's change crew cannot read
- **WHEN** crew raises batch 3's card and the host of `z`'s team does not answer
- **THEN** no session is started on the rest of the batch, and the card says `z`'s change could not be read and the reading could not be opened

#### Scenario: A link only the host can open
- **WHEN** plannotator gives batch 3's session a link on `localhost`
- **THEN** crew ends that session, raises the batch's card saying its reading could not be opened on the tailnet, and says so

## MODIFIED Requirements

### Requirement: A session is started for a card's row by its key
crew SHALL start a plannotator reading session when it raises a batch's card, on the batch's folder, the reviewer's summary whole and every unit's whole change as read at its commit, given as one review, on the partition's main level's host, and when it raises the card of a proposal with more than fifteen new units, on the proposal's page; it SHALL put the session's link in the card's words first and among its links. The session SHALL offer an Approve button and SHALL NOT open a browser on the host. `crew card session <key>` SHALL print the running session's link for such a key again, and SHALL refuse any other key, saying that card has nothing to read. A batch card posted before one card per batch was built, keyed `batch/<n>-<k>`, SHALL keep its sessions as they were until its card closes.

#### Scenario: A batch card's session
- **WHEN** crew raises batch 3's card on the main level's host, for a batch of `x` and `z` from two teams' hosts
- **THEN** one plannotator session is running there on the batch's summary and both units' changes, no browser has opened, and the card carries a link of the form `http://<host's tailnet name>:<port>`

#### Scenario: A unit named with a batch's key
- **WHEN** the planner runs `crew card session batch/3 x`
- **THEN** it is refused, saying a batch has one reading session, on the whole batch, and no session is started

#### Scenario: A batch card posted under an old key
- **WHEN** the planner runs `crew card session batch/2-2 x` for an open card of batch 2 posted under that key before this change, and `x` is among its units
- **THEN** the session on `x`'s change runs as before on `x`'s team's host, and its link is printed

#### Scenario: A proposal card's session
- **WHEN** crew raises the card of proposal 4, which adds sixteen units
- **THEN** a session is running on proposal 4's page as `crew plan proposed 4` prints it, and the card carries its link

#### Scenario: A review card's session
- **WHEN** swb-1-conductor runs `crew card session review/x/abc1234`
- **THEN** it is refused as not a card key, since there is no review row, and no session is started

#### Scenario: A verify report's key
- **WHEN** swb-1-conductor runs `crew card session verify/x/20261013-1200`
- **THEN** it is refused, saying no row of the rail has that key, and no session is started

#### Scenario: A landing card
- **WHEN** the conductor runs `crew card session land/y`
- **THEN** it is refused: a landing card has nothing to read, and no session is started

### Requirement: A session is started only where its link can be answered
crew SHALL start no session, and SHALL say why, when the key is no row's or the row has nothing to read, when the batch's session would run on any host but the main level's, when the document is not on the host the session would run on or crew cannot read it whole, and when plannotator gives a link that names the host only for itself (`localhost` or a loopback address), ending that session.

#### Scenario: A key whose row is gone
- **WHEN** the planner runs `crew card session batch/3` after batch 3's card was closed
- **THEN** it is refused as a key with no row, and no session is started

#### Scenario: A batch's session on another host
- **WHEN** a conductor on the box runs `crew card session batch/3 --label wldn`, and the partition's main level is on mac-studio
- **THEN** it is refused, naming mac-studio, and no session is started

#### Scenario: A landing card
- **WHEN** the conductor runs `crew card session land/y`
- **THEN** it is refused: a landing card has no document to read

### Requirement: The session's decision reaches the owner as the card's answer
`crew card wait <key>` SHALL return when the card is answered or its session has the user's decision, whichever is first, and print which: for a batch, the card's note and every annotation word for word, closing the card with the outcome and ending the session; for a long proposal, approved, annotated with every annotation, closed by the user with no decision, or ended with no decision, the planner acting on it as on the card. A decision reached while nobody waited SHALL be returned by the next wait for that key. A wait for a key with no session and no card SHALL be refused.

#### Scenario: Approved in the session
- **WHEN** the user opens the link on the card of a proposal of more than fifteen new units on the phone and presses Approve
- **THEN** the planner's `crew card wait proposal/4` returns `approved`, and the planner acts on it as an approval on the card

#### Scenario: Annotated in the session
- **WHEN** the user annotates two passages of a proposal's page and sends them as feedback
- **THEN** the wait returns `annotated` with both annotations and the user's words

#### Scenario: Annotated in a batch's session
- **WHEN** the user sends batch 3's session with two annotations and the planner runs `crew card wait batch/3`
- **THEN** the command prints both annotations word for word, the card is closed "Read; 2 notes sent to their teams", and the session is ended

#### Scenario: Decided while the owner was down
- **WHEN** the user taps batch 3's card while the planner is restarting, and the restarted planner runs `crew card wait batch/3`
- **THEN** the wait returns at once with the card's note, if any, and closes the card

#### Scenario: Closed with no decision
- **WHEN** the user closes a long proposal's session without approving or sending feedback
- **THEN** the wait returns that the session was closed with no decision, and the card is still the user's to answer

### Requirement: The session ends when its card closes
When crew closes or withdraws a card, the session started for its key SHALL be ended, and the rail's sweep SHALL end the session of any closed card or gone row. `crew card end <key>` SHALL end it as well. crew SHALL end only a plannotator process it started for that key, and only while plannotator lists that process as serving that document; a key with no session ends nothing and is not an error. When plannotator's list of sessions cannot be read, crew SHALL end nothing, SHALL keep the key's session as recorded, and SHALL say so, so a later rail read ends it.

#### Scenario: A review card closed after approval
- **WHEN** batch 3's card is closed by the planner's wait after the user's annotations
- **THEN** the plannotator session for `batch/3` is no longer running, and its link no longer opens

#### Scenario: A card withdrawn when its row ends
- **WHEN** crew withdraws the card of a long proposal because the planner dropped it
- **THEN** the session for its key is ended

#### Scenario: A process that is not crew's
- **WHEN** the process recorded for a key is no longer a plannotator session on that key's document
- **THEN** crew kills nothing and forgets the key's session

#### Scenario: plannotator's list can't be read
- **WHEN** crew withdraws a long proposal's card and `plannotator sessions --json` fails on its host
- **THEN** crew ends nothing, says it could not read plannotator's sessions, and keeps the key's session, which the next rail read ends

#### Scenario: A batch card tapped on the phone
- **WHEN** the user taps batch 3's card and the planner's wait returns
- **THEN** the session for `batch/3` is no longer running, and its link no longer opens
