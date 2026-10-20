## MODIFIED Requirements

### Requirement: A card whose session could not start is raised all the same
When crew raises a batch's card, a long proposal's or a landing's and its session could not start, crew SHALL raise the card all the same, saying after its summary's first paragraph that its reading could not be opened on the tailnet, and why first in its details, and SHALL say why in the command's output. A landing's card SHALL also name `crew card session land/<bolt>` as how the bolt's conductor starts the reading, the card then changing to carry its link, and the command's output SHALL name it too. The run record's entry for the card's post or change SHALL hold why, as crew's own message.

#### Scenario: A unit's change crew cannot read
- **WHEN** crew raises batch 3's card and the host of `z`'s team does not answer
- **THEN** no session is started on the rest of the batch, and the card says `z`'s change could not be read and the reading could not be opened

#### Scenario: A link only the host can open
- **WHEN** plannotator gives batch 3's session a link on `localhost`
- **THEN** crew ends that session, raises the batch's card saying its reading could not be opened on the tailnet, and says so

#### Scenario: A landing whose reading could not open
- **WHEN** crew raises bolt `y`'s landing card and plannotator is not on the team's host's path
- **THEN** the landing card is raised all the same, an approval as before, saying its reading could not be opened on the tailnet and why, and that the bolt's conductor starts it with `crew card session land/y`, after which the card carries its link; and the merge's wait says so, naming `crew card session land/y`

#### Scenario: Why is kept in the run record
- **WHEN** bolt `y`'s landing card is posted, or changed when a merge moves its head, and its reading could not open because plannotator did not list the session within its start time
- **THEN** the run record's `card.post` or `card.update` entry for `land/y` holds that reason in crew's words, beside the card's id and key

#### Scenario: A card whose reading opened records no reason
- **WHEN** bolt `y`'s landing card is posted and its reading opens
- **THEN** its `card.post` entry holds no reason, and the card carries the reading's link

## ADDED Requirements

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
