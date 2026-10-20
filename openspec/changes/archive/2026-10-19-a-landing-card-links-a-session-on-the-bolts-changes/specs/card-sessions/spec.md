## MODIFIED Requirements

### Requirement: A session is started for a card's row by its key
crew SHALL start a plannotator reading session when it raises a batch's card, on the batch's folder, the reviewer's summary whole and every unit's whole change as read at its commit, given as one review, on the partition's main level's host; when it raises the card of a proposal with more than fifteen new units, on the proposal's page; and when it raises a bolt's landing card, on what the bolt brings to main, on the team's host; it SHALL put the session's link in the card's words first and among its links. The session SHALL offer an Approve button and SHALL NOT open a browser on the host. `crew card session <key>` SHALL print the running session's link for such a key again, and SHALL refuse any other key, saying that card has nothing to read. A batch card posted before one card per batch was built, keyed `batch/<n>-<k>`, SHALL keep its sessions as they were until its card closes.

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
- **WHEN** crew raises bolt `y`'s landing card on swb-1's host, mac-studio, once `y` reads proven
- **THEN** one plannotator session is running there on what `y` brings to main, no browser has opened, and the card carries a link of the form `http://<host's tailnet name>:<port>`

#### Scenario: A landing card's session asked for again
- **WHEN** swb-1-conductor runs `crew card session land/y` while that session runs
- **THEN** the command prints the same link, one session runs for `land/y`, and its files are not written again

### Requirement: A session is started only where its link can be answered
crew SHALL start no session, and SHALL say why, when the key is no row's or the row has nothing to read, when the batch's session would run on any host but the main level's, when a landing's session would run on any host but its bolt's team's, when a landing's bolt does not read proven, when the document is not on the host the session would run on or crew cannot read it whole, and when plannotator gives a link that names the host only for itself (`localhost` or a loopback address), ending that session.

#### Scenario: A key whose row is gone
- **WHEN** the planner runs `crew card session batch/3` after batch 3's card was closed
- **THEN** it is refused as a key with no row, and no session is started

#### Scenario: A batch's session on another host
- **WHEN** a conductor on the box runs `crew card session batch/3 --label wldn`, and the partition's main level is on mac-studio
- **THEN** it is refused, naming mac-studio, and no session is started

#### Scenario: A landing's session on another host
- **WHEN** the planner on mac-studio runs `crew card session land/y --label wldn`, and `y` is held by swb-1, whose host is the box
- **THEN** it is refused, naming the box as where `land/y`'s reading runs, and no session is started

#### Scenario: A landing card
- **WHEN** swb-1-conductor runs `crew card session land/y` while unit `b` of `y` has not merged
- **THEN** it is refused, saying `y` does not read proven and why, so its landing card is not raised and has no session

### Requirement: A card whose session could not start is raised all the same
When crew raises a batch's card, a long proposal's or a landing's and its session could not start, crew SHALL raise the card all the same, saying after its summary's first paragraph that its reading could not be opened on the tailnet, and why first in its details, and SHALL say why in the command's output.

#### Scenario: A unit's change crew cannot read
- **WHEN** crew raises batch 3's card and the host of `z`'s team does not answer
- **THEN** no session is started on the rest of the batch, and the card says `z`'s change could not be read and the reading could not be opened

#### Scenario: A link only the host can open
- **WHEN** plannotator gives batch 3's session a link on `localhost`
- **THEN** crew ends that session, raises the batch's card saying its reading could not be opened on the tailnet, and says so

#### Scenario: A landing whose reading could not open
- **WHEN** crew raises bolt `y`'s landing card and plannotator is not on the team's host's path
- **THEN** the landing card is raised all the same, an approval as before, saying its reading could not be opened on the tailnet and why, and the merge's wait says so

### Requirement: The session's decision reaches the owner as the card's answer
`crew card wait <key>` SHALL return when the card is answered or its session has the user's decision, whichever is first, and print which: for a batch, the card's note and every annotation word for word, closing the card with the outcome and ending the session; for a long proposal, approved, annotated with every annotation, closed by the user with no decision, or ended with no decision, the planner acting on it as on the card; for a landing, the session's decision alone, annotations word for word as notes on the landing card and an approval said to land nothing, the card left as it is and the decided session forgotten so the next `crew card session` starts it anew. A decision reached while nobody waited SHALL be returned by the next wait for that key. A wait for a key with no session and no card SHALL be refused.

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

#### Scenario: Annotated in a landing's session
- **WHEN** the user annotates a line of bolt `y`'s diff in its landing's session, "this drops the retry", and sends it, and swb-1-conductor's `crew card wait land/y` is running
- **THEN** the wait prints the annotation word for word as a note on `y`'s landing card, the landing card is still open and unanswered, and `crew card session land/y` then starts a new session

#### Scenario: Approved in a landing's session
- **WHEN** the user presses Approve in bolt `y`'s landing's session
- **THEN** the conductor's wait says the reading was approved and that this lands nothing, the card's approval being the word to land, and nobody is told to land `y`

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

#### Scenario: A bolt landed
- **WHEN** `crew bolt land y` closes `y`'s landing card on swb-1's host
- **THEN** the session for `land/y` is no longer running there, and its link no longer opens

#### Scenario: A landing held for a fix
- **WHEN** swb-1-conductor starts a fix on bolt `y` and crew withdraws its landing card, held for the fix
- **THEN** the session for `land/y` is ended with it, and the card raised once `y` reads proven again carries a new session's link

## ADDED Requirements

### Requirement: A landing's session opens what the bolt brings to main, as one review
A `land/<bolt>` card's session SHALL be one plannotator review of several files, in this order: a page naming the bolt, its head, the units and chores that land, and that the reading lands nothing; each unit's change in the plan's order as the head holds it, its Markdown files named for the unit; then the bolt's diff against main, from where the bolt last met main to its head, less the change folders already shown. Each file SHALL open whole, as its own path.

#### Scenario: A bolt of two units and a chore
- **WHEN** bolt `y` holds units `a` and `b`, both archived on its branch, and chore `c`, and crew raises its landing card at head `def5678`
- **THEN** the session's files are `00-y.md`, then `01-a-proposal.md` and the rest of `a`'s change, then `02-b-proposal.md` and the rest of `b`'s, then the diff of `y` against main as text, which holds `c`'s code and every unit's code and no file under `openspec/changes/`, each as it stands at `def5678`

#### Scenario: A change's metadata
- **WHEN** `a`'s archived change folder holds `.openspec.yaml` beside its Markdown files
- **THEN** the landing's session holds the Markdown files only

#### Scenario: Main moved since the bolt was cut
- **WHEN** main has had two landings since bolt `y` last met it
- **THEN** the diff in `y`'s session holds only what `y` brings, from where `y` last met main to its head, and none of those landings' changes

### Requirement: A landing's session follows the bolt's head
When a merge moves a bolt's head while its landing card is open, crew SHALL end the session on the old head and start one on the new head before it changes the card, and the card changed in place SHALL carry the new link. When `crew card session land/<bolt>` starts the session anew because none runs, crew SHALL change the open landing card in place to carry the new link while the card waits on the user, and SHALL leave a card the user has answered as it is, printing the link alone.

#### Scenario: A merge moves the head
- **WHEN** bolt `y`'s landing card is open with a session on head `abc1234`, and a fix merges into `y` at `def5678`
- **THEN** the session on `abc1234` is no longer running, one on `def5678` is, and the card, changed in place saying its head is now `def5678`, carries the new session's link

#### Scenario: Started again after a restart
- **WHEN** the team's host restarted, `land/y`'s session no longer runs, and swb-1-conductor runs `crew card session land/y` while the card waits on the user
- **THEN** a new session starts on `y` at its head, its link is printed, and the card, changed in place, carries that link

#### Scenario: A card raised before landings had a reading
- **WHEN** bolt `y`'s landing card was raised with no link before this change, and swb-1-conductor runs `crew card session land/y`
- **THEN** a session starts on `y` at its head, and the open card is changed in place to carry its link

#### Scenario: A card already approved
- **WHEN** the user has approved `land/y`'s card, its session no longer runs, and swb-1-conductor runs `crew card session land/y`
- **THEN** a new session starts and its link is printed, and the card is not changed and no new card follows it
