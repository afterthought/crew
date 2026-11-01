## ADDED Requirements

### Requirement: A later try of a card's reading is recorded
Each try of a batch's, a long proposal's or a bolt's reading that is not part of its card's post or change, by `crew card session` starting it anew or by the rail's sweep, SHALL append one `card.reading` entry to the run record on the reading's key, in the name of its owner, the planner's for a batch's and a proposal's and main-level ops's for a bolt's, `land/<bolt>`, done, or refused with crew's own message saying why. The sweep's try of a kit's landings card is its raise, recorded as the card's change.

#### Scenario: A try that refuses
- **WHEN** the rail's sweep tries batch 3's reading and plannotator does not list it within its start time
- **THEN** a `card.reading` entry for `batch/3` holds that reason in crew's words, and the card is not changed

#### Scenario: A link given again
- **WHEN** the planner runs `crew card session batch/3` while its session runs
- **THEN** no entry is appended

#### Scenario: A landing's reading started by hand
- **WHEN** wldn-ops runs `crew card session land/y`, no session of `land/y` runs, and the reading opens
- **THEN** a done `card.reading` entry for `land/y` is appended in wldn-ops's name

#### Scenario: A landing's try off the host its work runs on
- **WHEN** the planner on mac-studio runs `crew card session land/y --label wldn`, and the runner that took `y`'s work runs on the box
- **THEN** it is refused as before, and no entry is appended, since no reading was tried

## MODIFIED Requirements

### Requirement: A session is started only where its link can be answered
crew SHALL start no session, and SHALL say why, when the key is no row's or the row has nothing to read, when the batch's session would run on any host but the main level's, when a landing's session would run on any host but the one its bolt's work runs on, as the runner that took it reported, when a landing's bolt is not started or does not read proven, when the document is not on the host the session would run on or crew cannot read it whole, and when plannotator gives a link that names the host only for itself (`localhost` or a loopback address), ending that session.

#### Scenario: A key whose row is gone
- **WHEN** the planner runs `crew card session batch/3` after batch 3's card was closed
- **THEN** it is refused as a key with no row, and no session is started

#### Scenario: A batch's session on another host
- **WHEN** wldn-ops on the box runs `crew card session batch/3 --label wldn`, and the partition's main level is on mac-studio
- **THEN** it is refused, naming mac-studio, and no session is started

#### Scenario: A landing's session on another host
- **WHEN** the planner on mac-studio runs `crew card session land/y --label wldn`, and the runner that took `y`'s work runs on the box
- **THEN** it is refused, naming the box as where `land/y`'s reading runs, and no session is started

#### Scenario: A landing card
- **WHEN** wldn-ops runs `crew card session land/y` while unit `b` of `y` has not merged
- **THEN** it is refused, saying `y` does not read proven and why, so its landing card is not raised and has no session

### Requirement: A landing's session follows the bolt's head
A bolt's reading, keyed `land/<bolt>`, SHALL run on the host its work runs on, as the runner that took it reported, in the kit's folder there, while the bolt is a row of its kit's landings card, and its link SHALL be carried on that row. When a merge moves the bolt's head, crew SHALL end the session on the old head and start one on the new head before the row changes, and the card, changed in place, SHALL carry the new link. When `crew card session land/<bolt>` starts the session anew because none runs, or gives a running session's link again while the run record shows the kit's card standing without a row's reading, crew SHALL change the kit's open card in place to carry the link while it waits on the user, and SHALL leave a card the user has answered as it is, printing the link alone.

#### Scenario: A merge moves the head
- **WHEN** bolt `y` is a row of `land/crew` with a session on head `abc1234`, and a fix merges into `y` at `def5678`
- **THEN** the session on `abc1234` is no longer running, one on `def5678` is, and `land/crew`, changed in place saying `y`'s head is now `def5678`, carries the new session's link on `y`'s row

#### Scenario: Started again after a restart
- **WHEN** the bolt's host restarted, `land/y`'s session no longer runs, and wldn-ops runs `crew card session land/y` while `land/crew` waits on the user
- **THEN** a new session starts on `y` at its head, its link is printed, and `land/crew`, changed in place, carries that link on `y`'s row

#### Scenario: A card raised before landings had a reading
- **WHEN** bolt `y`'s row on `land/crew` carries no link, and wldn-ops runs `crew card session land/y`
- **THEN** a session starts on `y` at its head, and the open card is changed in place to carry its link on `y`'s row

#### Scenario: A card already approved
- **WHEN** the user has sent `land/crew`, `y`'s session no longer runs, and wldn-ops runs `crew card session land/y`
- **THEN** a new session starts and its link is printed, and the card is not changed and no new card follows it

#### Scenario: A running session whose row never got its link
- **WHEN** `land/crew` was posted with `y`'s row standing without its reading, a later try started `y`'s session but the card's change was refused, and wldn-ops runs `crew card session land/y` while that session runs and the card waits on the user
- **THEN** the same link is printed, no new session starts, and `land/crew`, changed in place, carries that link on `y`'s row

#### Scenario: A running session on a card that carries it
- **WHEN** wldn-ops runs `crew card session land/y` while its session runs and `land/crew` already carries every row's link
- **THEN** the same link is printed and the card is not changed

#### Scenario: A bolt that is no row
- **WHEN** wldn-ops runs `crew card session land/y` while `y` does not read proven
- **THEN** it is refused, saying `y` is no row of crew's landings card and what it waits on, and nothing is started

### Requirement: A landing's raise tries its reading again before raising without it
When a bolt's reading refuses to open as crew puts its row on the kit's landings card or changes it, crew SHALL try once more as `crew card session land/<bolt>` would, on the host the bolt's work runs on: the kit's main fetched in its folder there, the bolt's landing read afresh, and its reading opened again. The row SHALL carry the second try's link, and be on the card without a reading only when both tries refuse, with the second's reason. A failed fetch SHALL be said and SHALL NOT stop the second try.

#### Scenario: The first start fails and the second opens
- **WHEN** the merge's end makes bolt `y` a row of `land/crew` and plannotator's first start of its reading ends before it is ready, and its second start comes up
- **THEN** one session runs for `land/y` on the bolt's host, and `y`'s row on the posted card carries its link

#### Scenario: Both starts fail
- **WHEN** both starts of bolt `y`'s reading end before they are ready
- **THEN** `y`'s row is on the card without a reading, saying so with the second start's reason and naming `crew card session land/y` as main-level ops's act, and no session of `land/y` is recorded

#### Scenario: The bolt no longer reads proven at the second try
- **WHEN** the first start of bolt `y`'s reading fails and, read afresh, `y` no longer reads proven
- **THEN** crew does not try again, and `y` is no row of the card

#### Scenario: Every raise and change tries again
- **WHEN** `y`'s row is put on the card again after a fix, by the rail's sweep, or at a preview's end, and its first start fails
- **THEN** crew tries the reading a second time before the card is posted or changed, as at a merge's end

## REMOVED Requirements

### Requirement: A later try of a reading is recorded
**Reason**: Record 0047 move 5: a landing's reading runs where the bolt's work runs, as the runner that took it reported, not on a team's host, so its scenario's name changes with it.
**Migration**: "A later try of a card's reading is recorded", added by this change.
