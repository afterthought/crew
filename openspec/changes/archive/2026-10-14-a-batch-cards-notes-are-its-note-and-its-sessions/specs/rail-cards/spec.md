# Spec Delta

## ADDED Requirements

### Requirement: A batch's card is a notice naming every unit
A batch's card, keyed `batch/<n>`, SHALL be a Pending You notice (`fyi`) that asks nothing: no options, no question, no approval, no steps and no attachment. Its summary SHALL say first what the card is: the partition's batch of the changes constructed or amended since the last batch, already being built, read for notes and approving nothing.

#### Scenario: A card of six units
- **WHEN** the planner posts the card for batch 2 holding six units
- **THEN** the card is one `fyi` whose summary opens by saying it is batch 2 of the partition, already being built and approving nothing, whose background names all six units with their teams and paragraphs, and whose one link opens the batch's session

### Requirement: A batch's card names every unit and links its session
A batch's card's words SHALL name every unit of the batch with its team and hold each unit's opening paragraph from the reviewer's summary as prose, with no code block, and it SHALL have one link, to the batch's reading session.

#### Scenario: Six units named
- **WHEN** the planner posts the card for batch 2 holding six units of two teams
- **THEN** its background names all six with their teams and paragraphs as prose, and its one link opens the batch's session

### Requirement: crew refuses a batch card in another form
Before `post_request` or `update_request` runs in a session crew started, crew SHALL refuse a card keyed `batch/<n>` that is not in the batch card's form, or a change that takes it out of that form, naming the form: anything to answer, steps, an attachment, a code block in its words, more than one link, or a background that leaves out a unit of the batch. When crew cannot read the batch's units, it SHALL refuse and name what failed.

#### Scenario: A batch card with a choice of units
- **WHEN** the planner posts a card keyed `batch/2` as a `multi` of its units
- **THEN** crew refuses it before Pending You is called, saying a batch's card is one notice for the whole batch with nothing to answer, and no card is posted

#### Scenario: A batch card with its summary as code
- **WHEN** the planner posts a card keyed `batch/2` as an `fyi` whose background holds a fenced code block, or with the summary attached as a `code` artifact
- **THEN** crew refuses it, saying the summary goes in the card's words as prose, since a code block scrolls sideways on the phone

#### Scenario: A batch card with a link per unit
- **WHEN** the planner posts a card keyed `batch/2` as an `fyi` with three links, one for each unit
- **THEN** crew refuses it, saying a batch has one reading session

#### Scenario: A batch card that leaves out a unit
- **WHEN** the planner posts a card keyed `batch/2`, whose batch holds `x1`, `x2` and `z1`, with a background naming only `x1` and `x2`
- **THEN** crew refuses it, saying it leaves out `z1`

#### Scenario: A batch card in its form
- **WHEN** the planner posts a card keyed `batch/2` as an `fyi` whose background names `x1`, `x2` and `z1`, each with its paragraph as prose, with one link
- **THEN** crew lets it through, and records it after it is posted, as before

### Requirement: No card of crew's asks a question in words
Before `post_request` or `update_request` runs in a session crew started, crew SHALL refuse a card under a row's key that is a text question, carries a `text` field, or holds a question of kind `text`, saying Pending You makes every question required and the card's note is where the user's words go.

#### Scenario: A proposal card with a text question
- **WHEN** the planner posts a card keyed `proposal/4` with a question of kind `text` for feedback
- **THEN** crew refuses it, saying the card asks a question in words, which Pending You makes required, and no card is posted
