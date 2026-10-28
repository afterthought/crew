## MODIFIED Requirements

### Requirement: The session's decision reaches the owner as the card's answer
`crew card read <key>`, run by the card's owner, SHALL give what the user decided in the key's session beside the card's answer, and print which: for a batch, the card's note and every annotation word for word, closing the card with the outcome and ending the session; for a long proposal, approved, annotated with every annotation, or closed by the user with no decision, the planner acting on it as on the card, and a decided session forgotten; for a landing, `land/<bolt>`, run by the bolt's conductor on the team's host, the session's decision alone, annotations word for word as notes on the bolt's row and an approval said to land nothing, the card left as it is and the decided session forgotten so the next `crew card session land/<bolt>` starts it anew. A decision reached while nobody read SHALL be given by the next read of that key. crew SHALL keep no process waiting on a session or a card: `crew card wait` SHALL be refused at once, naming `crew card read <key>`, with nothing started.

#### Scenario: Approved in the session
- **WHEN** the user opens the link on the card of a proposal of more than fifteen new units on the phone and presses Approve, and the planner runs `crew card read proposal/4`
- **THEN** the read prints `approved` for its reading beside the card's answer, and the planner acts on it as an approval on the card

#### Scenario: Annotated in the session
- **WHEN** the user annotates two passages of a proposal's page and sends them as feedback, and the planner runs `crew card read proposal/4`
- **THEN** the read prints `annotated` with both annotations and the user's words

#### Scenario: Annotated in a batch's session
- **WHEN** the user sends batch 3's session with two annotations and the planner runs `crew card read batch/3`
- **THEN** the command prints both annotations word for word, the card is closed "Read; 2 notes sent to their teams", and the session is ended

#### Scenario: Decided while the owner was down
- **WHEN** the user taps batch 3's card while the planner is restarting, and the restarted planner runs `crew card read batch/3`
- **THEN** the read prints the card's note, if any, at once and closes the card

#### Scenario: Closed with no decision
- **WHEN** the user closes a long proposal's session without approving or sending feedback, and the planner runs `crew card read proposal/4`
- **THEN** the read says the session was closed with no decision, and the card is still the user's to answer

#### Scenario: Annotated in a landing's session
- **WHEN** the user annotates a line of bolt `y`'s diff in its landing's session, "this drops the retry", and sends it, and swb-1-conductor runs `crew card read land/y`
- **THEN** the read prints the annotation word for word as a note on `y`'s landing row, the landing card is still open and unanswered, and `crew card session land/y` then starts a new session

#### Scenario: Approved in a landing's session
- **WHEN** the user presses Approve in bolt `y`'s landing's session and swb-1-conductor runs `crew card read land/y`
- **THEN** the read says the reading was approved and that this lands nothing, the card's approval being the word to land, and nobody is told to land `y`

#### Scenario: Nothing decided yet
- **WHEN** swb-1-conductor runs `crew card read land/y` while its reading runs and the user has sent nothing from it
- **THEN** the read says the reading waits on the user, and nothing is forgotten or ended

#### Scenario: The old wait run
- **WHEN** an agent runs `crew card wait batch/3`
- **THEN** it is refused at once, naming `crew card read batch/3`, and no process is left running

### Requirement: The session ends when its card closes
When crew closes or withdraws a card, the session started for its key SHALL be ended, and the rail's sweep SHALL end the session of any closed card or gone row. `crew card end <key>` SHALL end it as well. crew SHALL end only a plannotator process it started for that key, and only while plannotator lists that process as serving that document; a key with no session ends nothing and is not an error. When plannotator's list of sessions cannot be read, crew SHALL end nothing, SHALL keep the key's session as recorded, and SHALL say so, so a later rail read ends it.

#### Scenario: A review card closed after approval
- **WHEN** batch 3's card is closed by the planner's `crew card read batch/3` after the user's annotations
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
- **WHEN** the user taps batch 3's card, the planner is woken, and it runs `crew card read batch/3`
- **THEN** the session for `batch/3` is no longer running, and its link no longer opens

#### Scenario: A bolt landed
- **WHEN** `crew bolt land y` closes `y`'s landing card on swb-1's host
- **THEN** the session for `land/y` is no longer running there, and its link no longer opens

#### Scenario: A landing held for a fix
- **WHEN** swb-1-conductor starts a fix on bolt `y` and crew withdraws its landing card, held for the fix
- **THEN** the session for `land/y` is ended with it, and the card raised once `y` reads proven again carries a new session's link

### Requirement: A later try of a reading is recorded
Each try of a batch's, a long proposal's or a bolt's reading that is not part of its card's post or change, by `crew card session` starting it anew or by the rail's sweep, SHALL append one `card.reading` entry to the run record on the reading's key, in the name of its owner, the planner's for a batch's and a proposal's and the bolt's conductor's for a bolt's, `land/<bolt>`, done, or refused with crew's own message saying why. The sweep's try of a kit's landings card is its raise, recorded as the card's change.

#### Scenario: A try that refuses
- **WHEN** the rail's sweep tries batch 3's reading and plannotator does not list it within its start time
- **THEN** a `card.reading` entry for `batch/3` holds that reason in crew's words, and the card is not changed

#### Scenario: A link given again
- **WHEN** the planner runs `crew card session batch/3` while its session runs
- **THEN** no entry is appended

#### Scenario: A landing's reading started by hand
- **WHEN** swb-1-conductor runs `crew card session land/y`, no session of `land/y` runs, and the reading opens
- **THEN** a done `card.reading` entry for `land/y` is appended in swb-1-conductor's name

#### Scenario: A landing's try off its team's host
- **WHEN** the planner on mac-studio runs `crew card session land/y --label wldn`, and `y` is held by swb-1 on the box
- **THEN** it is refused as before, and no entry is appended, since no reading was tried

## ADDED Requirements

### Requirement: The rail's refresh tells a reading's owner once that the user sent it
On each rail read and follower refresh, crew's sweep on each host SHALL tell the owner of each reading there that the user sent, approved or annotated, and the owner has not read, once, through `crew tell`, naming `crew card read <key>` and no word of the user's; it SHALL mark the reading told once the tell goes through, and try again at the next refresh when it does not. A reading closed undecided, read or told SHALL be told nothing.

#### Scenario: A landing's reading sent
- **WHEN** the user sends bolt `y`'s reading with one annotation, and the follower on swb-1's host refreshes
- **THEN** swb-1-conductor is told once that `land/y`'s reading was sent and to run `crew card read land/y`, the tell holds none of the annotation's words, and the next refresh tells nothing

#### Scenario: The owner is down
- **WHEN** the user sends batch 3's reading with notes while the planner is not up, and the refresh's tell to it fails
- **THEN** the reading stays untold, and the first refresh after the planner is up tells it

#### Scenario: Read before the refresh
- **WHEN** the planner runs `crew card read batch/3` after the user sent its reading and before any refresh
- **THEN** no refresh tells the planner of it

#### Scenario: Closed with no decision
- **WHEN** the user closes proposal 4's reading without approving or sending feedback
- **THEN** no refresh tells the planner anything

## REMOVED Requirements

### Requirement: A wait on a landing card starts its reading when none runs
**Reason**: crew keeps no waiting process for a card (record 0046 parts 1 and 4, `teams.24`); a landing's reading starts at its row's raise, by `crew card session land/<bolt>` and by the rail's retry of a reading its card stands without.
**Migration**: the bolt's conductor runs `crew card session land/<bolt>` to start a reading that is not running, and `crew card read land/<bolt>` when told the user sent it.

### Requirement: A batch's wait starts its reading when none runs
**Reason**: crew keeps no waiting process for a card (record 0046 parts 1 and 4, `teams.24`); a batch's reading starts at its card's raise, by `crew card session batch/<n>` and by the rail's retry.
**Migration**: the planner runs `crew card session batch/<n>` to start a reading that is not running, and `crew card read batch/<n>` when woken by the card or told the reading was sent.
