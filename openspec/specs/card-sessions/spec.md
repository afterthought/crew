# card-sessions Specification

## Purpose
A card that asks the user to read something links a plannotator session on that document, started by the card's owner on its own host without opening a browser there, reachable wherever the card is answered; what the user decides in the session reaches the owner as the card's answer, and the session ends when the card closes.

## Requirements

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
crew SHALL start no session, and SHALL say why, when the key is no row's or the row has nothing to read, when the batch's session would run on any host but the main level's, when the document is not on the host the session would run on or crew cannot read it whole, and when plannotator gives a link that names the host only for itself (`localhost` or a loopback address), ending that session; a card whose session could not start SHALL still be raised, saying its reading could not be opened on the tailnet.

#### Scenario: A key whose row is gone
- **WHEN** the planner runs `crew card session batch/3` after batch 3's card was closed
- **THEN** it is refused as a key with no row, and no session is started

#### Scenario: A batch's session on another host
- **WHEN** a conductor on the box runs `crew card session batch/3 --label wldn`, and the partition's main level is on mac-studio
- **THEN** it is refused, naming mac-studio, and no session is started

#### Scenario: A unit's change crew cannot read
- **WHEN** crew raises batch 3's card and the host of `z`'s team does not answer
- **THEN** no session is started on the rest of the batch, and the card says `z`'s change could not be read and the reading could not be opened

#### Scenario: A landing card
- **WHEN** the conductor runs `crew card session land/y`
- **THEN** it is refused: a landing card has no document to read

#### Scenario: A link only the host can open
- **WHEN** plannotator gives batch 3's session a link on `localhost`
- **THEN** crew ends that session, raises the batch's card saying its reading could not be opened on the tailnet, and says so

### Requirement: One session per card key
While a session started for a key, and for an old batch key a unit, is running, `crew card session` with that key and unit SHALL start nothing and print that session's link again.

#### Scenario: Run again after a restart
- **WHEN** the planner restarts and runs `crew card session batch/3` while the session it started before is still running
- **THEN** the command prints the same link, one session runs for batch 3, and the batch's folder is not written again

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

### Requirement: A batch's session opens its summary and every change whole, as one review
A `batch/<n>` card's session SHALL be one plannotator review of several files, in this order: the reviewer's summary, then for each unit in the batch's order its proposal, design, specs and tasks and any other Markdown file of its change, as read at the commit the batch read it at. Each file SHALL be opened whole, as its own path, never through a folder whose files the user must open one by one, and each file's name SHALL carry its unit.

#### Scenario: Two units from two teams
- **WHEN** batch 3 holds `x` of swb-1, on the box, and `z` of atl-1, on mac-studio, and the planner starts its session on mac-studio
- **THEN** the batch's folder holds `00-summary.md`, then `01-x-proposal.md` and the rest of `x`'s change, then `02-z-proposal.md` and the rest of `z`'s, each as it stood at the commit batch 3 read it at, and plannotator was given those files in that order

#### Scenario: A change's metadata
- **WHEN** a unit's change folder holds `.openspec.yaml` beside its Markdown files
- **THEN** the batch's folder and its session hold the Markdown files only

### Requirement: A batch's session is written on the main level's host
crew SHALL write a batch's session's files into the batch's own folder on the main level's host before it starts the session, and SHALL patch nothing of plannotator's.

#### Scenario: Written before the session starts
- **WHEN** the planner starts batch 3's session on mac-studio
- **THEN** every file plannotator is given is in batch 3's folder on mac-studio before plannotator starts

### Requirement: A session whose card is closed or whose row is gone is ended on every rail read
Each time `crew rail` runs, and each time the rail tab refreshes, crew SHALL end, on every host of each partition read, each session it started for a card key whose row is gone, or whose card the run record holds as closed with no card open under the key. It SHALL end only sessions it recorded, and only a process plannotator lists as serving the recorded document.

#### Scenario: A verify card's session from before
- **WHEN** the session crew started for `verify/x/20261009-1412`, before a verify report had no row, still runs on chuck-herdr-alpha
- **THEN** the next `crew rail`, run on mac-studio, ends that session, since no row has its key, and its link no longer opens

#### Scenario: A proposal approved in the app
- **WHEN** the user approves proposal 4 on its card, the planner runs `crew plan approve 4` but its session lost Pending You's tools before it closed the card
- **THEN** the next rail read ends the session for `proposal/4`, since its row is gone

#### Scenario: A card closed while its row stays
- **WHEN** the planner closed card `proposal/4` with `ack_answer`, its hook could not end the session, and proposal 4 is still open
- **THEN** the next rail read ends that session

#### Scenario: A row with no card yet
- **WHEN** the planner started the session for `proposal/4` and has not yet posted its card
- **THEN** a rail read leaves the session running

#### Scenario: A session crew did not start
- **WHEN** the user runs plannotator by hand on a closed proposal's page on mac-studio
- **THEN** no rail read ends it

#### Scenario: A batch card's sessions on another host
- **WHEN** the planner closed card `batch/3-1` on mac-studio, and the session for its unit `y` still runs on chuck-herdr-alpha
- **THEN** the next rail read ends `y`'s session there

### Requirement: The rail says which sessions it ended
After its groups and its open cards with no row, `crew rail` SHALL list each session it ended on that read, with its card key, the unit for a batch card's, its partition, its host and whether its card was closed or its row gone, and SHALL name each host whose sessions it could not check, with why. When it ended nothing and checked every host, it SHALL print nothing about sessions.

#### Scenario: Two sessions ended
- **WHEN** a rail read ends the sessions of `proposal/4` and `batch/3`
- **THEN** the rail lists both, each with its host and why it was ended

#### Scenario: Nothing to end
- **WHEN** every recorded session's row and card are open
- **THEN** the rail says nothing about sessions

### Requirement: A session crew can't judge is kept
A rail read SHALL end no session whose row or card it cannot tell: none on a host that does not answer, which it names; no session for a card closed, and no batch card's, while a host of the partition's run record did not answer; and no session started less than two minutes before its host is checked, which a later read judges.

#### Scenario: The team's host is asleep
- **WHEN** chuck-herdr-alpha does not answer
- **THEN** the rail ends no session there, names chuck-herdr-alpha as not checked, and ends what it can judge elsewhere

#### Scenario: The record is read in part
- **WHEN** a host of the partition's run record does not answer
- **THEN** the rail ends no session for a card closed and no batch card's session, and still ends a session whose proposal's row is gone

#### Scenario: A session just started
- **WHEN** the planner starts a session for a proposal opened after the rail's read began
- **THEN** that read leaves it running
