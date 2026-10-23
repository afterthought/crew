## MODIFIED Requirements

### Requirement: A card whose session could not start is raised all the same
When crew raises a batch's card, a long proposal's or a landing's and its session could not start, crew SHALL raise the card all the same, saying after its summary's first paragraph that its reading could not be opened on the tailnet, and why first in its details, and SHALL say why in the command's output. A landing's card SHALL also say that crew tries the reading again when the rail is read and name `crew card session land/<bolt>` as how the bolt's conductor starts it, the card then changing to carry its link, and the command's output SHALL name it too. A batch's card and a long proposal's SHALL say that crew tries the reading again when the rail is read and name `crew card session <key>` as how the planner starts it, the card then changing to carry its link, and the command's output SHALL name it too. The run record's entry for the card's post or change SHALL hold why, as crew's own message.

#### Scenario: A unit's change crew cannot read
- **WHEN** crew raises batch 3's card and the host of `z`'s team does not answer
- **THEN** no session is started on the rest of the batch, and the card says `z`'s change could not be read and the reading could not be opened

#### Scenario: A link only the host can open
- **WHEN** plannotator gives batch 3's session a link on `localhost`
- **THEN** crew ends that session, raises the batch's card saying its reading could not be opened on the tailnet, and says so

#### Scenario: A landing whose reading could not open
- **WHEN** crew raises bolt `y`'s landing card and plannotator is not on the team's host's path
- **THEN** the landing card is raised all the same, an approval as before, saying its reading could not be opened on the tailnet and why, that crew tries it again when the rail is read, and that the bolt's conductor starts it with `crew card session land/y`, after which the card carries its link; and the merge's wait says so, naming `crew card session land/y`

#### Scenario: A batch whose reading could not open
- **WHEN** crew raises batch 3's card and plannotator is not on the main level's host's path
- **THEN** the batch's card is raised all the same, saying its reading could not be opened on the tailnet and why, that crew tries it again when the rail is read, and that the planner starts it with `crew card session batch/3`, after which the card carries its link; and `crew review --wait` says so, naming `crew card session batch/3`

#### Scenario: Why is kept in the run record
- **WHEN** bolt `y`'s landing card is posted, or changed when a merge moves its head, and its reading could not open because plannotator did not list the session within its start time
- **THEN** the run record's `card.post` or `card.update` entry for `land/y` holds that reason in crew's words, beside the card's id and key

#### Scenario: A card whose reading opened records no reason
- **WHEN** bolt `y`'s landing card is posted and its reading opens
- **THEN** its `card.post` entry holds no reason, and the card carries the reading's link

### Requirement: A landing's session follows the bolt's head
When a merge moves a bolt's head while its landing card is open, crew SHALL end the session on the old head and start one on the new head before it changes the card, and the card changed in place SHALL carry the new link. When `crew card session land/<bolt>` starts the session anew because none runs, or gives a running session's link again while the run record shows the card standing without its reading, crew SHALL change the open landing card in place to carry the link while the card waits on the user, and SHALL leave a card the user has answered as it is, printing the link alone.

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

#### Scenario: A running session whose card never got its link
- **WHEN** `land/y`'s card was posted without its reading, a later try started its session but the card's change was refused, and swb-1-conductor runs `crew card session land/y` while that session runs and the card waits on the user
- **THEN** the same link is printed, no new session starts, and the card, changed in place, carries that link

#### Scenario: A running session on a card that carries it
- **WHEN** swb-1-conductor runs `crew card session land/y` while its session runs and the card already carries its link
- **THEN** the same link is printed and the card is not changed

### Requirement: The rail's read tries a reading its card stands without
On each rail read, crew's sweep SHALL try the reading of each batch card, long proposal card and landing card posted on this host that waits on the user and that the run record shows standing without its reading, its last post, change or try of the reading having refused to open it: a batch's and a proposal's as `crew card session <key>` does, a landing's as `crew card session land/<bolt>` does, on the host of the team holding the bolt with the bolt read afresh; each changing the card to carry the link. A card whose last try refused under ten minutes before SHALL be left for a later read. The rail SHALL list each such try with what came of it.

#### Scenario: A batch card raised without its reading
- **WHEN** batch 3's card was posted with its reading refused twenty minutes ago, the card waits on the user, and the planner's host now starts plannotator
- **THEN** the next rail read on that host starts batch 3's reading, changes the card in place to carry its link, and lists `batch/3` as its reading opened

#### Scenario: A landing card raised without its reading
- **WHEN** bolt `y`'s landing card was posted on swb-1's host with its reading refused twenty minutes ago, the card waits on the user, and that host now starts plannotator
- **THEN** the next rail read on that host starts `y`'s reading at its head, changes the card in place to carry its link, and lists `land/y` as its reading opened

#### Scenario: A try that fails is left for later
- **WHEN** a rail read tries proposal 4's reading and it refuses, and another rail read comes five minutes later
- **THEN** the first read lists `proposal/4` as left with why, and the second does not try it

#### Scenario: A landing's try that fails is left for later
- **WHEN** a rail read tries `land/y`'s reading and it refuses, and another rail read comes five minutes later
- **THEN** the first read lists `land/y` as left with why, a `card.reading` entry for `land/y` holds why, and the second read does not try it

#### Scenario: A card whose reading opened since
- **WHEN** batch 3's card was posted without its reading, and the planner's `crew card session batch/3` has since changed it to carry its link
- **THEN** no rail read tries batch 3's reading

#### Scenario: A card the user has answered
- **WHEN** batch 3's card was posted without its reading and the user has sent it back
- **THEN** no rail read tries its reading

#### Scenario: A landing card on another host
- **WHEN** `land/y`'s card stands without its reading on the box, and the rail is read on mac-studio
- **THEN** that read does not try `land/y`'s reading

### Requirement: A later try of a reading is recorded
Each try of a batch's, a long proposal's or a landing's reading that is not part of its card's post or change, by `crew card session` starting it anew, by the batch's or the landing's wait or by the rail's sweep, SHALL append one `card.reading` entry to the run record on the card's key, in the name of the card's owner, the planner's for a batch's and a proposal's and the bolt's conductor's for a landing's, done, or refused with crew's own message saying why.

#### Scenario: A try that refuses
- **WHEN** the rail's sweep tries batch 3's reading and plannotator does not list it within its start time
- **THEN** a `card.reading` entry for `batch/3` holds that reason in crew's words, and the card is not changed

#### Scenario: A link given again
- **WHEN** the planner runs `crew card session batch/3` while its session runs
- **THEN** no entry is appended

#### Scenario: A landing's reading started by hand
- **WHEN** swb-1-conductor runs `crew card session land/y`, no session of `land/y` runs, and the reading opens
- **THEN** a done `card.reading` entry for `land/y` is appended in swb-1-conductor's name, beside the card it holds

#### Scenario: A landing's try off its team's host
- **WHEN** the planner on mac-studio runs `crew card session land/y --label wldn`, and `y` is held by swb-1 on the box
- **THEN** it is refused as before, and no entry is appended, since no reading was tried
