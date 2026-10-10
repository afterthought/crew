# Spec Delta

## ADDED Requirements

### Requirement: A proposal's card is an approval
A proposal's card, keyed `proposal/<n>`, SHALL be an approval (`approve`), with a note for changes or for dropping it, and no options or steps.

#### Scenario: A proposal card
- **WHEN** the planner posts the card for proposal 4
- **THEN** the card is an approval, and the user's yes has the planner approve proposal 4

### Requirement: A review's card is an approval with a note
A unit's review card, keyed `review/<unit>/<head>`, SHALL be an approval (`approve`) with no options, no steps and no attachment. Its yes approves the unit; its no carries the user's note for changes, and the conductor runs construct again with the note's words.

#### Scenario: A review card
- **WHEN** the conductor posts the review card for unit `u`
- **THEN** Pending You takes it as an approval, with the link to the change in its words and nothing attached

#### Scenario: A review declined with a note
- **WHEN** the user declines unit `u`'s review card with the note "keep the old flag"
- **THEN** the conductor runs construct again on `u` with "keep the old flag", and the unit comes back to review

### Requirement: A verify report's card is the conductor's options
A verify report's card, keyed `verify/<unit>/<stamp>`, SHALL be a choice (`choice`, or `multi` when the user may pick several findings) whose options are what the conductor would do, with no steps.

#### Scenario: A verify card
- **WHEN** the conductor posts the card for unit `u`'s verify report, which raised two findings
- **THEN** the card is a choice whose options are what the conductor would do about them

### Requirement: A landing's card is a high-stakes approval
A bolt's landing card, keyed `land/<bolt>/<head>`, SHALL be an approval (`approve`) marked high stakes, with no options, whose yes has the conductor tell main-level ops to land the bolt. It MAY carry steps the bolt's proof leaves the user, and no step SHALL name the landing itself.

#### Scenario: A landing card
- **WHEN** the conductor posts the landing card for bolt `y` at head `abc1234`
- **THEN** the card is an approval marked high stakes, offers no Done button and no command to land, and is approved only by holding the button in the Pending You app

#### Scenario: A landing approved
- **WHEN** the user approves the landing card for bolt `y`
- **THEN** the conductor tells main-level ops to land `y` on the user's word, and the user runs nothing

### Requirement: No row's card takes another kind
No row's card SHALL be a step for the user to take (`action`), a notice (`fyi`), a text question (`text`), a review (`review`) or a grouped card of questions.

#### Scenario: A review card as a review
- **WHEN** a conductor posts a card keyed `review/u/abc1234` as a `review` card
- **THEN** crew refuses it, saying a review's card is an approval with a note for changes

### Requirement: crew refuses a row's card in another form
Before Pending You's `post_request` runs in a session crew started, crew SHALL refuse a card whose key is a row's and whose form is not that row's, naming the form the row's card takes. A refused call never reaches Pending You. When crew cannot check a card it would check, its own input unreadable among the reasons, it SHALL refuse it and name what failed.

#### Scenario: A landing card posted as a step
- **WHEN** a conductor posts a card keyed `land/y/abc1234` as an `action` with the landing command as its step
- **THEN** crew refuses it before Pending You is called, saying a landing's card is an approval marked high stakes whose yes has the conductor tell main-level ops to land, and no card is posted

#### Scenario: A landing card not marked high stakes
- **WHEN** a conductor posts a card keyed `land/y/abc1234` as an approval without `highStakes`
- **THEN** crew refuses it, saying the landing card is marked high stakes

#### Scenario: Input crew cannot read
- **WHEN** the hook is given input before `post_request` that is not a JSON object
- **THEN** crew refuses the call, saying it could not check the card's form and why, and no card is posted

#### Scenario: A card in the row's form
- **WHEN** the planner posts a card keyed `proposal/4` as an `approve` card with no options
- **THEN** crew lets it through, and records it after it is posted, as before

### Requirement: crew refuses a change that takes a row's card out of its form
Before `update_request` runs on a card a crew agent on this host posted under a row's key, crew SHALL refuse a change that clears a landing card's high stakes, gives options to an approval, or gives steps to any card but a landing's.

#### Scenario: A landing card loses its high stakes
- **WHEN** a conductor updates its open landing card with `highStakes` false
- **THEN** crew refuses the update, and the card stays high stakes

### Requirement: crew checks only a row's card in a crew session
crew SHALL let pass, unchecked, a card whose key is no row's, any card in a session crew did not start, and a tool of another server.

#### Scenario: The user's own session
- **WHEN** the user, in a session crew did not start, posts any card under any key
- **THEN** crew checks nothing and lets it through
