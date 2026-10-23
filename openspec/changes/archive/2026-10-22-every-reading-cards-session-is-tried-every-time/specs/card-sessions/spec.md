## MODIFIED Requirements

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

## ADDED Requirements

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
