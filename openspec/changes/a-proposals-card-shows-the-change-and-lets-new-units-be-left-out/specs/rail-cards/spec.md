## MODIFIED Requirements

### Requirement: A card carries what the user would read and the row's answers
A review card and a verify card SHALL each carry the link to the plannotator session its owner started for the card's key: on the unit's change folder, or on the verify report. The card SHALL carry the link in place of the folder's path or the report, and SHALL NOT be posted without it when the owner's session has plannotator. A proposal's card SHALL hold the proposal whole, its picture, its text and its case, and SHALL carry no link, but for a proposal of more than fifteen new units, whose card carries the link to the session on the proposal's page as `crew plan proposed <n>` prints it. A landing card carries no link. Each card's options SHALL be the row's answers: approve, and keep or leave out each new unit, for a proposal; approve or ask for changes for a review; what to fix or merge for a verify report; and approve for a landing. A decision the user makes in the card's session SHALL be acted on by the owner as the card's answer, and the owner SHALL then close the card.

#### Scenario: A review card's options
- **WHEN** the user opens a review card
- **THEN** it offers approval, and a note in the user's own words asks for changes

#### Scenario: A review card's link
- **WHEN** swb-1-conductor posts the card for unit `x` in review at `abc1234`
- **THEN** the card carries the link `crew card session review/x/abc1234` printed, and no folder path

#### Scenario: Answered in the session rather than on the card
- **WHEN** the user annotates the change in the review card's session and sends the annotations
- **THEN** the conductor runs construct again with them, as for a note on the card, and withdraws the card saying it was answered in its session

#### Scenario: A proposal's card holds the proposal whole
- **WHEN** the planner posts the card for proposal 4, which adds two units
- **THEN** the card carries the picture, the text and the case, and no plannotator link

### Requirement: A card's words are the document's own
A card a crew agent posts for a rail row SHALL say what the user decides from in the words of the document it asks the user to read, cut by whole sentences and never reworded: a review card the change's Why and the lead sentence of each What Changes item; a proposal card the words `crew plan card <n>` prints, which are the proposal's case and each change as `crew plan proposed <n>` words it; a verify card each finding in a line, with what the conductor would do about it.

#### Scenario: A review card
- **WHEN** swb-1-conductor posts the review card for unit `x` of bolt `y`
- **THEN** the card's background holds `x`'s Why and one line per What Changes item, in the proposal's words

#### Scenario: A verify card
- **WHEN** a conductor posts the card for a verify report that raised two warnings
- **THEN** the card's background holds one line for each warning, saying what it found and what the conductor would do about it

#### Scenario: A change too long for the summary
- **WHEN** a unit's Why runs past what the summary holds after the link and the bolt
- **THEN** the summary ends at the last whole sentence that fits, and the background holds the whole Why

#### Scenario: A proposal card
- **WHEN** the planner posts the card for proposal 4
- **THEN** its title, summary, background, questions and artifacts are those `crew plan card 4` prints

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

### Requirement: A card's document is inline Markdown
A document's substance shown on a card beyond its words SHALL be inline Markdown, an artifact of kind `code` with lang `markdown` and the text as its lines, never an uploaded file or HTML. The whole document SHALL be reached only through the card's plannotator link, but for a proposal's card, which holds its proposal whole. A card SHALL carry no artifact but such a picture or such Markdown, and a proposal's card its change as text: an artifact of kind `code` with lang `text`, its lines those `crew plan card <n>` prints, each at most forty characters, so it reads in monospace on a phone without wrapping.

#### Scenario: A document's substance on a card
- **WHEN** an agent shows part of a document on a card beside its words
- **THEN** that part is an artifact of kind `code` with lang `markdown`, its lines the document's Markdown, and the whole document is reached through the card's plannotator link, never attached as a file

#### Scenario: A card with nothing to show
- **WHEN** a card needs no picture and shows no part of a document beyond its words
- **THEN** its artifacts are empty, and its plannotator link is in its words and its links, never an artifact

#### Scenario: A proposal's change as text
- **WHEN** the planner posts the card for proposal 4, which drops a unit and adds two
- **THEN** the card carries two artifacts, the uploaded picture and a `code` artifact of lang `text` holding the change as `crew plan card 4` prints it, and no Markdown artifact and no link

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
