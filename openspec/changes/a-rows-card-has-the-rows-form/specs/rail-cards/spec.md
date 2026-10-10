# Spec Delta

## ADDED Requirements

### Requirement: A row's card has the row's form
A row's card SHALL take its row's form, in Pending You's kinds of card:

- a proposal's card, `proposal/<n>`, is an approval (`approve`), with no options and no steps;
- a unit's review card, `review/<unit>/<head>`, is a review (`review`): it looks good, or it needs changes, with the user's note; it has no options and no steps;
- a verify report's card, `verify/<unit>/<stamp>`, is a choice (`choice`, or `multi` when the user may pick several findings) whose options are what the conductor would do;
- a bolt's landing card, `land/<bolt>/<head>`, is an approval (`approve`) marked high stakes, with no options, whose yes has the conductor tell main-level ops to land the bolt.

No row's card SHALL be a step for the user to take (`action`), a notice (`fyi`), a text question (`text`) or a grouped card. Only a landing card MAY carry steps, and only steps the bolt's proof leaves the user; a step never names the landing itself.

#### Scenario: A landing card
- **WHEN** the conductor posts the landing card for bolt `y` at head `abc1234`
- **THEN** the card is an approval marked high stakes, offers no Done button and no command to land, and is approved only by holding the button in the Pending You app

#### Scenario: A landing approved
- **WHEN** the user approves the landing card for bolt `y`
- **THEN** the conductor tells main-level ops to land `y` on the user's word, and the user runs nothing

#### Scenario: A review card
- **WHEN** the conductor posts the review card for unit `u`
- **THEN** the card is a review, answered with "looks good" or "needs changes" and the user's note

#### Scenario: A verify card
- **WHEN** the conductor posts the card for unit `u`'s verify report, which raised two findings
- **THEN** the card is a choice whose options are what the conductor would do about them

### Requirement: crew refuses a row's card in another form
Before Pending You's `post_request` runs in a session crew started, crew SHALL refuse a card whose key is a row's and whose form is not that row's, naming the form the row's card takes. A refused call never reaches Pending You. When crew cannot check a card it would check, it SHALL refuse it and name what failed.

#### Scenario: A landing card posted as a step
- **WHEN** a conductor posts a card keyed `land/y/abc1234` as an `action` with the landing command as its step
- **THEN** crew refuses it before Pending You is called, saying a landing's card is an approval marked high stakes whose yes has the conductor tell main-level ops to land, and no card is posted

#### Scenario: A landing card not marked high stakes
- **WHEN** a conductor posts a card keyed `land/y/abc1234` as an approval without `highStakes`
- **THEN** crew refuses it, saying the landing card is marked high stakes

#### Scenario: A review card as a bare approval
- **WHEN** a conductor posts a card keyed `review/u/abc1234` as an `approve` card
- **THEN** crew refuses it, saying a review's card is a review, looks good or needs changes, with a note

#### Scenario: A card in the row's form
- **WHEN** the planner posts a card keyed `proposal/4` as an `approve` card with no options
- **THEN** crew lets it through, and records it after it is posted, as before

### Requirement: crew refuses a change that takes a row's card out of its form
Before `update_request` runs on a card a crew agent on this host posted under a row's key, crew SHALL refuse a change that clears a landing card's high stakes, gives options to an approval or a review, or gives steps to any card but a landing's.

#### Scenario: A landing card loses its high stakes
- **WHEN** a conductor updates its open landing card with `highStakes` false
- **THEN** crew refuses the update, and the card stays high stakes

### Requirement: crew checks only a row's card in a crew session
crew SHALL let pass, unchecked, a card whose key is no row's, any card in a session crew did not start, and a tool of another server.

#### Scenario: The user's own session
- **WHEN** the user, in a session crew did not start, posts any card under any key
- **THEN** crew checks nothing and lets it through
