## MODIFIED Requirements

### Requirement: A landing's session follows the bolt's head
A bolt's reading, keyed `land/<bolt>`, SHALL run on the host of the team holding it while the bolt is a row of its kit's landings card, and its link SHALL be carried on that row. When a merge moves the bolt's head, crew SHALL end the session on the old head and start one on the new head before the row changes, and the card, changed in place, SHALL carry the new link. When `crew card session land/<bolt>` starts the session anew because none runs, crew SHALL change the kit's open card in place to carry the new link while it waits on the user, and SHALL leave a card the user has answered as it is, printing the link alone.

#### Scenario: A merge moves the head
- **WHEN** bolt `y` is a row of `land/crew` with a session on head `abc1234`, and a fix merges into `y` at `def5678`
- **THEN** the session on `abc1234` is no longer running, one on `def5678` is, and `land/crew`, changed in place saying `y`'s head is now `def5678`, carries the new session's link on `y`'s row

#### Scenario: Started again after a restart
- **WHEN** the team's host restarted, `land/y`'s session no longer runs, and swb-1-conductor runs `crew card session land/y` while `land/crew` waits on the user
- **THEN** a new session starts on `y` at its head, its link is printed, and `land/crew`, changed in place, carries that link on `y`'s row

#### Scenario: A card raised before landings had a reading
- **WHEN** bolt `y`'s row on `land/crew` carries no link, and swb-1-conductor runs `crew card session land/y`
- **THEN** a session starts on `y` at its head, and the open card is changed in place to carry its link on `y`'s row

#### Scenario: A card already approved
- **WHEN** the user has sent `land/crew`, `y`'s session no longer runs, and swb-1-conductor runs `crew card session land/y`
- **THEN** a new session starts and its link is printed, and the card is not changed and no new card follows it

#### Scenario: A bolt that is no row
- **WHEN** swb-1-conductor runs `crew card session land/y` while `y` does not read proven
- **THEN** it is refused, saying `y` is no row of crew's landings card and what it waits on, and nothing is started

### Requirement: A landing's raise tries its reading again before raising without it
When a bolt's reading refuses to open as crew puts its row on the kit's landings card or changes it, crew SHALL try once more as `crew card session land/<bolt>` would, on the team's host: the kit's main fetched there, the bolt's landing read afresh, and its reading opened again. The row SHALL carry the second try's link, and be on the card without a reading only when both tries refuse, with the second's reason. A failed fetch SHALL be said and SHALL NOT stop the second try.

#### Scenario: The first start fails and the second opens
- **WHEN** the merge's end makes bolt `y` a row of `land/crew` and plannotator's first start of its reading ends before it is ready, and its second start comes up
- **THEN** one session runs for `land/y` on the team's host, and `y`'s row on the posted card carries its link

#### Scenario: Both starts fail
- **WHEN** both starts of bolt `y`'s reading end before they are ready
- **THEN** `y`'s row is on the card without a reading, saying so with the second start's reason and naming `crew card session land/y` as its conductor's act, and no session of `land/y` is recorded

#### Scenario: The bolt no longer reads proven at the second try
- **WHEN** the first start of bolt `y`'s reading fails and, read afresh, `y` no longer reads proven
- **THEN** crew does not try again, and `y` is no row of the card

#### Scenario: Every raise and change tries again
- **WHEN** `y`'s row is put on the card again after a fix, by the rail's sweep, or at a preview's end, and its first start fails
- **THEN** crew tries the reading a second time before the card is posted or changed, as at a merge's end

### Requirement: A wait on a landing card starts its reading when none runs
`crew card wait land/<bolt>`, run by the bolt's conductor on the team's host while the bolt is a row of its kit's landings card, SHALL wait on the bolt's reading and return what the user sends from it, each annotation a note on that row, an approval in it landing nothing. When it finds no session of the key, it SHALL start the reading as `crew card session land/<bolt>` does, printing its link and changing the kit's card to carry it while the card waits on the user, and SHALL then wait on it. When the reading will not open, it SHALL be refused, saying why and naming `crew card session land/<bolt>`. While the bolt is no row of an open landings card, it SHALL be refused, saying so.

#### Scenario: A card raised without its reading
- **WHEN** bolt `y`'s row says its reading could not be opened, and swb-1-conductor runs `crew card wait land/y` once the cause has passed
- **THEN** a session starts on `y` at its head, its link is printed, `land/crew` is changed in place to carry it, and the wait waits on that session

#### Scenario: Waiting again after a decision
- **WHEN** the wait on `land/y` printed the user's annotations and forgot the decided session, and swb-1-conductor runs `crew card wait land/y` again while `y` is a row
- **THEN** a new session starts on `y` at its head, the card carries its new link, and the wait waits on it, saying nothing about no session having been started

#### Scenario: The reading still will not open
- **WHEN** swb-1-conductor runs `crew card wait land/y`, no session of `land/y` runs, and plannotator is not on the team's host's path
- **THEN** the wait is refused, saying the reading could not be opened and why, and naming `crew card session land/y`, and the card is not changed

#### Scenario: No landing card held
- **WHEN** swb-1-conductor runs `crew card wait land/y` and `y` is no row of an open landings card, and no session of it runs
- **THEN** the wait is refused, saying `y` is no row of its kit's landings card, and nothing is started
