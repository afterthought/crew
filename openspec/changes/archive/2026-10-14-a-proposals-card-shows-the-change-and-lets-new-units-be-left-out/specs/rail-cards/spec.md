## MODIFIED Requirements

### Requirement: A card's link and bolt come first
A card that carries a link SHALL begin its summary with the link to its row's plannotator session, then name the bolt, within Pending You's 400 characters, and its background SHALL begin with the same link. The link SHALL be the card's entry in its links and SHALL NOT be carried as an attached artifact. A landing card, which has nothing to read, SHALL name its bolt and carry no link; a proposal's card that carries no link SHALL name its bolt in its title.

#### Scenario: A review card's opening
- **WHEN** swb-1-conductor posts the review card for unit `x` of bolt `y`, whose session's link is `http://mac-studio.ts.swancloud.net:19432`
- **THEN** the card's summary begins with that link and names bolt `y`, its background begins with the link, its links hold it labelled "Read and annotate it in plannotator", and it has no artifact

#### Scenario: A proposal's card opening
- **WHEN** the planner posts the card for proposal 4, which changes bolt `y`
- **THEN** its title names `y` and the counts, and its summary begins with what the proposal is

### Requirement: A proposal's card is an approval
A proposal's card, keyed `proposal/<n>`, SHALL be posted as `crew plan card <n>` prints it: an approval (`approve`) with no options or steps when the proposal adds or moves into a bolt no unit, or more than fifteen; otherwise a grouped card, its `about` naming the proposal, of a question `plan` of kind `approve` and one `units-<k>` question per group of at most five new units, of kind `multi`, or `choice` for a lone unit, with no text question. Its picture is an uploaded image and its text a code artifact of lang `text`. A note beside a decline carries what to change, an objection to a drop or an amendment, or the reason to drop the proposal; a note beside an approval changes nothing of what is applied.

#### Scenario: A proposal card
- **WHEN** the planner posts the card for proposal 4, which only amends a unit
- **THEN** the card is an approval, and the user's yes has the planner approve proposal 4

#### Scenario: A proposal card with new units
- **WHEN** the planner posts the card for proposal 5, which adds three units
- **THEN** the card asks `plan` and `units-1`, the three units all ticked, and the user's yes with one cleared has the planner record both answers with `crew plan answer 5`

### Requirement: No row's card takes another kind
No row's card SHALL be a step for the user to take (`action`), a notice (`fyi`), a text question (`text`) or a review (`review`), and no row's card but a proposal's SHALL be a grouped card of questions. No card SHALL hold a text question.

#### Scenario: A review card as a review
- **WHEN** a conductor posts a card keyed `review/u/abc1234` as a `review` card
- **THEN** crew refuses it, saying a review's card is an approval with a note for changes

#### Scenario: A proposal card asking for words
- **WHEN** the planner posts the card for proposal 5 with a third question of kind `text` for feedback
- **THEN** crew refuses it, saying the note is the place for words

### Requirement: crew refuses a row's card in another form
Before Pending You's `post_request` runs in a session crew started, crew SHALL refuse a card whose key is a row's and whose form is not that row's, naming the form the row's card takes. A proposal's card SHALL be refused when its unit questions do not hold, each exactly once, the units the proposal adds or moves into a bolt. A refused call never reaches Pending You. When crew cannot check a card it would check, its own input or the proposal unreadable among the reasons, it SHALL refuse it and name what failed.

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
- **WHEN** the planner posts a card keyed `proposal/4`, a proposal that adds no unit, as an `approve` card with no options
- **THEN** crew lets it through, and records it after it is posted, as before

#### Scenario: A proposal card missing a new unit
- **WHEN** the planner posts a card keyed `proposal/5`, which adds `b` and `c`, whose unit question lists only `b`
- **THEN** crew refuses it, naming `c` as a new unit the card does not ask about

#### Scenario: A proposal card with new units posted as a plain approval
- **WHEN** the planner posts a card keyed `proposal/5`, which adds `b` and `c`, as an `approve` card with no questions
- **THEN** crew refuses it, saying the card asks `plan` and a question of its new units, as `crew plan card 5` prints it
