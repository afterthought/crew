# card-sessions Specification

## Purpose
A card that asks the user to read something links a plannotator session on that document, started by the card's owner on its own host without opening a browser there, reachable wherever the card is answered; what the user decides in the session reaches the owner as the card's answer, and the session ends when the card closes.

## Requirements

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
When crew raises a batch's card, a long proposal's or a landing's and its session could not start, crew SHALL raise the card all the same, saying after its summary's first paragraph that its reading could not be opened on the tailnet, and why first in its details, and SHALL say why in the command's output. A landing's card SHALL also name `crew card session land/<bolt>` as how the bolt's conductor starts the reading, the card then changing to carry its link, and the command's output SHALL name it too. A batch's card and a long proposal's SHALL say that crew tries the reading again when the rail is read and name `crew card session <key>` as how the planner starts it, the card then changing to carry its link, and the command's output SHALL name it too. The run record's entry for the card's post or change SHALL hold why, as crew's own message.

#### Scenario: A unit's change crew cannot read
- **WHEN** crew raises batch 3's card and the host of `z`'s team does not answer
- **THEN** no session is started on the rest of the batch, and the card says `z`'s change could not be read and the reading could not be opened

#### Scenario: A link only the host can open
- **WHEN** plannotator gives batch 3's session a link on `localhost`
- **THEN** crew ends that session, raises the batch's card saying its reading could not be opened on the tailnet, and says so

#### Scenario: A landing whose reading could not open
- **WHEN** crew raises bolt `y`'s landing card and plannotator is not on the team's host's path
- **THEN** the landing card is raised all the same, an approval as before, saying its reading could not be opened on the tailnet and why, and that the bolt's conductor starts it with `crew card session land/y`, after which the card carries its link; and the merge's wait says so, naming `crew card session land/y`

#### Scenario: A batch whose reading could not open
- **WHEN** crew raises batch 3's card and plannotator is not on the main level's host's path
- **THEN** the batch's card is raised all the same, saying its reading could not be opened on the tailnet and why, that crew tries it again when the rail is read, and that the planner starts it with `crew card session batch/3`, after which the card carries its link; and `crew review --wait` says so, naming `crew card session batch/3`

#### Scenario: Why is kept in the run record
- **WHEN** bolt `y`'s landing card is posted, or changed when a merge moves its head, and its reading could not open because plannotator did not list the session within its start time
- **THEN** the run record's `card.post` or `card.update` entry for `land/y` holds that reason in crew's words, beside the card's id and key

#### Scenario: A card whose reading opened records no reason
- **WHEN** bolt `y`'s landing card is posted and its reading opens
- **THEN** its `card.post` entry holds no reason, and the card carries the reading's link

### Requirement: One session per card key
While a session started for a key, and for an old batch key a unit, is running, `crew card session` with that key and unit SHALL start nothing and print that session's link again.

#### Scenario: Run again after a restart
- **WHEN** the planner restarts and runs `crew card session batch/3` while the session it started before is still running
- **THEN** the command prints the same link, one session runs for batch 3, and the batch's folder is not written again

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

### Requirement: A landing's raise tries its reading again before raising without it
When a landing card's reading refuses to open as crew raises or changes the card, crew SHALL try once more as `crew card session land/<bolt>` would, on the team's host: the kit's main fetched there, the bolt's landing read afresh, and its reading opened again. The card SHALL carry the second try's link, and be raised without a reading only when both tries refuse, with the second's reason. A failed fetch SHALL be said and SHALL NOT stop the second try.

#### Scenario: The first start fails and the second opens
- **WHEN** the merge's end raises bolt `y`'s landing card and plannotator's first start of its reading ends before it is ready, and its second start comes up
- **THEN** one session runs for `land/y` on the team's host, the posted card carries its link, and its `card.post` entry holds no reason

#### Scenario: Both starts fail
- **WHEN** both starts of bolt `y`'s reading end before they are ready as crew raises its landing card
- **THEN** the card is raised without a reading, saying so with the second start's reason and naming `crew card session land/y`, no session of `land/y` is recorded, and the card's `card.post` entry holds that reason

#### Scenario: The bolt no longer reads proven at the second try
- **WHEN** the first start of bolt `y`'s reading fails and, read afresh, `y` no longer reads proven
- **THEN** crew does not try again, and posts or changes no card on this raise, as for a bolt that does not read proven

#### Scenario: Every raise and change tries again
- **WHEN** bolt `y`'s landing card is raised again after a fix, posted again by the rail's sweep, or changed at a preview's end, and its first start fails
- **THEN** crew tries the reading a second time before it posts or changes the card, as at a merge's end

### Requirement: A wait on a landing card starts its reading when none runs
When `crew card wait land/<bolt>` finds no session of the key on the team's host and the bolt's conductor holds its landing card open there, the wait SHALL start the reading as `crew card session land/<bolt>` does, printing its link and changing the card to carry it while the card waits on the user, and SHALL then wait on it. When the reading will not open, the wait SHALL be refused, saying why and naming `crew card session land/<bolt>`. With no landing card held, it SHALL be refused as before.

#### Scenario: A card raised without its reading
- **WHEN** bolt `y`'s landing card was raised saying its reading could not be opened, and swb-1-conductor runs `crew card wait land/y` once the cause has passed
- **THEN** a session starts on `y` at its head, its link is printed, the card is changed in place to carry it, and the wait waits on that session

#### Scenario: Waiting again after a decision
- **WHEN** the wait on `land/y` printed the user's annotations and forgot the decided session, and swb-1-conductor runs `crew card wait land/y` again while the card is open
- **THEN** a new session starts on `y` at its head, the card carries its new link, and the wait waits on it, saying nothing about no session having been started

#### Scenario: The reading still will not open
- **WHEN** swb-1-conductor runs `crew card wait land/y`, no session of `land/y` runs, and plannotator is not on the team's host's path
- **THEN** the wait is refused, saying the reading could not be opened and why, and naming `crew card session land/y`, and the card is not changed

#### Scenario: No landing card held
- **WHEN** swb-1-conductor runs `crew card wait land/y` and holds no landing card under `land/y` on this host, and no session of it runs
- **THEN** the wait is refused, saying no session was started and no landing card of `y` is held there, and nothing is started

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

### Requirement: A batch's or a long proposal's raise tries its reading twice
When a batch card's or a long proposal card's reading refuses to open as crew raises or changes the card, crew SHALL try it once more before building the card, at every point that raises or changes it. The card SHALL carry the second try's link, and be raised without its reading only when both tries refuse, with the second's reason. The first refusal SHALL be said in the command's output.

#### Scenario: The first start fails and the second opens
- **WHEN** `crew review --wait` raises batch 3's card, plannotator's first start of its reading ends before it is ready, and its second start comes up
- **THEN** one session runs for `batch/3` on the main level's host, the posted card carries its link, and its `card.post` entry holds no reason

#### Scenario: Both starts fail
- **WHEN** both starts of proposal 4's reading end before they are ready as `crew plan propose` raises the card of proposal 4, which adds sixteen units
- **THEN** the card is raised without its reading, saying so with the second start's reason and naming `crew card session proposal/4`, no session of `proposal/4` is recorded, and the card's `card.post` entry holds that reason

#### Scenario: Every raise and change tries again
- **WHEN** proposal 4's card is changed by a rewrite or a conductor's agreement, or batch 3's card is posted again by the rail's sweep, and the first start of its reading fails
- **THEN** crew tries the reading a second time before it posts or changes the card

### Requirement: Starting a batch's or a proposal's reading changes its card
When `crew card session batch/<n>` or `crew card session proposal/<n>` starts the reading anew because none runs, crew SHALL change the card the planner holds open under the key in place to carry the new link while it waits on the user, with a change note saying its reading is open again, and SHALL leave a card the user has answered as it is, printing the link alone.

#### Scenario: A batch card raised without its reading
- **WHEN** batch 3's card was raised saying its reading could not be opened, and the planner runs `crew card session batch/3` once the cause has passed
- **THEN** a session starts on batch 3's folder, its link is printed, and the card, changed in place, carries that link

#### Scenario: A proposal card already answered
- **WHEN** the user has answered proposal 4's card, its session no longer runs, and the planner runs `crew card session proposal/4`
- **THEN** a new session starts and its link is printed, and the card is not changed and no new card follows it

#### Scenario: A session that still runs
- **WHEN** the planner runs `crew card session batch/3` while its session runs
- **THEN** the same link is printed and the card is not changed

### Requirement: A batch's wait starts its reading when none runs
When `crew card wait batch/<n>` finds the planner's card of the batch open on the main level's host and no session of the key, the wait SHALL start the reading as `crew card session batch/<n>` does, changing the card to carry its link, and SHALL then wait on the card and the session together. When the reading will not open, the wait SHALL say why once, naming `crew card session batch/<n>`, and SHALL go on waiting on the card alone.

#### Scenario: A card raised without its reading
- **WHEN** batch 3's card was raised saying its reading could not be opened, and the planner runs `crew card wait batch/3` once the cause has passed
- **THEN** a session starts on batch 3's folder, the card is changed in place to carry its link, and the wait returns on the user's word in either

#### Scenario: The reading still will not open
- **WHEN** the planner runs `crew card wait batch/3`, no session of `batch/3` runs, and plannotator is not on the main level's host's path
- **THEN** the wait says once that the reading could not be opened and why, naming `crew card session batch/3`, leaves the card as it is, and returns when the user sends the card back

### Requirement: The rail's read tries a reading its card stands without
On each rail read, crew's sweep SHALL try the reading of each batch card and long proposal card posted on this host that waits on the user and that the run record shows standing without its reading, its last post, change or try of the reading having refused to open it, as `crew card session <key>` does, changing the card to carry the link. A card whose last try refused under ten minutes before SHALL be left for a later read. The rail SHALL list each such try with what came of it.

#### Scenario: A batch card raised without its reading
- **WHEN** batch 3's card was posted with its reading refused twenty minutes ago, the card waits on the user, and the planner's host now starts plannotator
- **THEN** the next rail read on that host starts batch 3's reading, changes the card in place to carry its link, and lists `batch/3` as its reading opened

#### Scenario: A try that fails is left for later
- **WHEN** a rail read tries proposal 4's reading and it refuses, and another rail read comes five minutes later
- **THEN** the first read lists `proposal/4` as left with why, and the second does not try it

#### Scenario: A card whose reading opened since
- **WHEN** batch 3's card was posted without its reading, and the planner's `crew card session batch/3` has since changed it to carry its link
- **THEN** no rail read tries batch 3's reading

#### Scenario: A card the user has answered
- **WHEN** batch 3's card was posted without its reading and the user has sent it back
- **THEN** no rail read tries its reading

### Requirement: A later try of a reading is recorded
Each try of a batch's or a long proposal's reading that is not part of its card's post or change, by `crew card session` starting it anew, by the batch's wait or by the rail's sweep, SHALL append one `card.reading` entry to the run record on the card's key, done, or refused with crew's own message saying why.

#### Scenario: A try that refuses
- **WHEN** the rail's sweep tries batch 3's reading and plannotator does not list it within its start time
- **THEN** a `card.reading` entry for `batch/3` holds that reason in crew's words, and the card is not changed

#### Scenario: A link given again
- **WHEN** the planner runs `crew card session batch/3` while its session runs
- **THEN** no entry is appended
