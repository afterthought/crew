## MODIFIED Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, derived from the row's state: `proposal/<n>` for an open proposal, `batch/<n>` for review batch n, and `land/<bolt>/<head>` for a bolt ready to land (the first seven characters of the bolt's branch head). A row's owner SHALL post its card with that key as the card's idempotency key. There SHALL be no review row and no `review/<unit>/<head>` key, and no verify row: a verify report waits on no one, and `verify/<unit>/<stamp>` is no row's key (`teams.17`). A batch whose cards were posted under `batch/<n>-<k>` before one card per batch was built SHALL keep a row for each of those keys until its card closes, and SHALL have no `batch/<n>` row.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2`, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, and the planner may not post `batch/2`

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was ready to land at head `abc1234`, its landing failed, and a fix moved its head to `def5678` and ops proved it again
- **THEN** its landing row's key is `land/y/def5678`, its conductor posts a new landing card under that key, and a card keyed `land/y/abc1234` belongs to no row

#### Scenario: A unit built again
- **WHEN** unit `u` was constructed at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** no review row or key exists for either head; the unit's revised change is due for the partition's next batch, whose card's key is the batch's

#### Scenario: A verify report saved
- **WHEN** unit `u`'s verify saves its report `verify-u-20261013-1200.md`
- **THEN** the rail has no row for it, and a card keyed `verify/u/20261013-1200` belongs to no row

### Requirement: The owner of a row posts its card
When an agent crew started has Pending You's tools, it SHALL post one card for each row it owns: the planner for each proposal it opens and for each review batch, and a conductor for its bolt once the bolt is proven, or proven but for steps only the user can take. It SHALL post no second card for a row that has one open to it; a card lost to it is not, and is posted again as *A row's card lost to its owner is posted again* says. A team's cards SHALL be its conductor's: its ops and every stage agent SHALL post no card, and no crew agent SHALL post a card that is not a row's. No card SHALL be posted for a verify report, which is no row.

#### Scenario: A proposal opened
- **WHEN** the planner opens proposal 4 in a session with Pending You's tools
- **THEN** one card keyed `proposal/4` is open, asked by the planner

#### Scenario: A batch due
- **WHEN** the reviewer delivers batch 3 of seven units
- **THEN** one card keyed `batch/3` is open, asked by the planner, and no conductor posts one

#### Scenario: No Pending You
- **WHEN** a conductor's session has no Pending You tools and its bolt is proven
- **THEN** no card is posted, the rail row is as before, and the conductor tells the operator agents it waits on the user

#### Scenario: A verify report saved
- **WHEN** a unit's verify saves its report, which marks two findings fix
- **THEN** its conductor posts no card and asks the user nothing, and runs code once more with the report's path

#### Scenario: A proof leaves the user a check
- **WHEN** brd-2's ops finishes its proof with every item green but one check only the user can make on their Mac
- **THEN** ops writes that check in its proof file and posts no card, and the user gets one card for it, the conductor's landing card for the bolt

### Requirement: A card carries what the user would read and the row's answers
A review card SHALL carry the link to the plannotator session its owner started for the card's key, on the unit's change folder. The card SHALL carry the link in place of the folder's path, and SHALL NOT be posted without it when the owner's session has plannotator. A proposal's card SHALL hold the proposal whole, its picture, its text and its case, and SHALL carry no link, but for a proposal of more than fifteen new units, whose card carries the link to the session on the proposal's page as `crew plan proposed <n>` prints it. A landing card carries no link. Each card's options SHALL be the row's answers: approve, and keep or leave out each new unit, for a proposal; approve or ask for changes for a review; and approve for a landing. A decision the user makes in the card's session SHALL be acted on by the owner as the card's answer, and the owner SHALL then close the card.

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

### Requirement: An answer wakes the owner, which acts on the user's word
An answer on a card SHALL be acted on by the agent that posted it, when it is woken in its session, and by no other: the planner approves, replaces or drops the proposal; the conductor approves the unit or runs construct again with the user's words, or asks main-level ops to land the bolt. The agent SHALL then close the card with a one-line outcome.

#### Scenario: A proposal approved from the phone
- **WHEN** the user approves the card for proposal 4 on the phone
- **THEN** the planner is woken, runs `crew plan approve 4`, closes the card with what was applied, and the rail's proposal row is gone

#### Scenario: Changes asked for on a review card
- **WHEN** the user answers a review card with a note asking for changes
- **THEN** the conductor runs construct again with the note's words and closes the card

#### Scenario: Landing approved
- **WHEN** the user approves the landing card for bolt `y`
- **THEN** the conductor tells the partition's main-level ops to land `y` on the user's word, and main-level ops lands it

### Requirement: The conductor's tell to the operator agents is for what has no card
A conductor with Pending You's tools SHALL NOT tell the operator agents when it waits on the user for a review or a landing, since that row's card reaches the user. It SHALL tell them when it waits on a question asked only in its pane, and for every wait when it has no Pending You tools. A verify report is no wait on the user, and is told to no one.

#### Scenario: A unit reaches review
- **WHEN** a conductor with Pending You's tools has posted the card for a unit in review
- **THEN** it sends no tell to the operator agents for it

#### Scenario: A question in the pane
- **WHEN** a stage stops on a question for the user that only the conductor's pane holds
- **THEN** the conductor tells the operator agents in one line what it waits for and where

### Requirement: A card's words are the document's own
A card a crew agent posts for a rail row SHALL say what the user decides from in the words of the document it asks the user to read, cut by whole sentences and never reworded: a review card the change's Why and the lead sentence of each What Changes item; a proposal card the words `crew plan card <n>` prints, which are the proposal's case and each change as `crew plan proposed <n>` words it.

#### Scenario: A review card
- **WHEN** swb-1-conductor posts the review card for unit `x` of bolt `y`
- **THEN** the card's background holds `x`'s Why and one line per What Changes item, in the proposal's words

#### Scenario: A verify card
- **WHEN** a unit's verify saves a report that raised two warnings
- **THEN** no card carries it: a verify report waits on no one, and its findings are fixed in one round

#### Scenario: A change too long for the summary
- **WHEN** a unit's Why runs past what the summary holds after the link and the bolt
- **THEN** the summary ends at the last whole sentence that fits, and the background holds the whole Why

#### Scenario: A proposal card
- **WHEN** the planner posts the card for proposal 4
- **THEN** its title, summary, background, questions and artifacts are those `crew plan card 4` prints

### Requirement: crew refuses a crew agent's card under any key but a row's of its own
Before a Pending You card is posted from a session crew started, crew SHALL refuse it unless its idempotency key is the card key of a rail row the agent owns: for the planner, `proposal/<n>` for an open proposal of its partition; for a conductor, `review/<unit>/<head>` for a unit of the bolt its team holds, or `land/<bolt>/<head>` for that bolt; `verify/<unit>/<stamp>` is no agent's. Every other crew agent SHALL own no key. A refused card SHALL NOT reach Pending You, and its refusal SHALL name the keys to use.

#### Scenario: ops posts a card
- **WHEN** brd-2-ops calls Pending You's `post_request` under any key
- **THEN** the call is refused before it reaches Pending You, and the refusal says ops owns no key: a team's cards are its conductor's, and what is left for the user goes in the proof file

#### Scenario: A conductor posts under a key of its own making
- **WHEN** brd-2-conductor, whose team holds bolt `y`, posts a card keyed `gateway-check-y`
- **THEN** the call is refused, and the refusal names `land/y/<head>` and the review keys of `y`'s units, read from `crew rail`

#### Scenario: A conductor posts another team's row
- **WHEN** brd-2-conductor posts a card keyed `review/z/abc1234` for a unit `z` of a bolt another team holds
- **THEN** the call is refused, naming the keys that are brd-2-conductor's

#### Scenario: The planner posts a proposal's card
- **WHEN** wldn-planner posts a card keyed `proposal/4` while proposal 4 of `wldn` is open
- **THEN** the call goes through, and the card is recorded as before

#### Scenario: A conductor posts a verify report's card
- **WHEN** brd-2-conductor, whose team holds bolt `y`, posts a card keyed `verify/u/20261013-1200` for a unit `u` of `y`
- **THEN** the call is refused before it reaches Pending You, naming `land/y/<head>`

### Requirement: A crew agent's card acts are in the run record
Each card a crew agent posts, updates, withdraws or closes in Pending You, through Pending You's tools in its session or through `crew card`, SHALL be an entry in its partition's run record, naming the row's object, the card's id in `Card`, and the key in `Key` when it is a row's key. Through `crew card` the card's id SHALL be read from Pending You's own reply. An entry SHALL NOT hold a card's title, summary or any other text written on it.

#### Scenario: A card posted and closed
- **WHEN** swb-1-conductor posts the card `review/x/abc1234` and later closes it
- **THEN** the run record has a `card.post` entry on `unit/x` with that key and the card's id, and a `card.close` entry with the same id

#### Scenario: A card posted through crew
- **WHEN** swb-1-conductor runs `crew card post land/b1/<head>` and Pending You answers with the card `req_b1`
- **THEN** the run record has a `card.post` entry on `bolt/b1` with the key `land/b1/<head>` and the card `req_b1`, and nothing written on the card

#### Scenario: The user's own sessions
- **WHEN** a Claude session crew did not start posts a Pending You card
- **THEN** nothing is written to crew's run record

### Requirement: A crew agent's card is posted through crew
`crew card post <key>` SHALL post the card given as one JSON object on its standard input as the asking assistant, through the fleet's `pendingyou mcp --app claude-code` under the host's sign-in, and SHALL print the card's id and its link. crew SHALL set the card's `idempotencyKey` to the key, its session to the agent's crew name, this host and the folder the command runs in, and its area to the one Pending You matches to the folder's git remote, or, when none matches, the kit's area made under `create-area:<owner>/<kit>`. It SHALL refuse a card that gives any of those itself. Before anything reaches Pending You it SHALL refuse a key and a form that crew's card hook refuses, in the hook's words.

#### Scenario: A landing card posted
- **WHEN** swb-1-conductor, whose team holds bolt `b1`, runs `crew card post land/b1/<head>` in its worktree with a landing card on standard input
- **THEN** Pending You is asked, as swb-1-conductor, to post that card under the key `land/b1/<head>`, with swb-1-conductor's name, the host and the worktree as its session and the kit's area, and the command prints the card's id and link

#### Scenario: A verify card posted
- **WHEN** swb-1-conductor runs `crew card post verify/v1/<stamp>`
- **THEN** the command refuses in the hook's words, naming `land/b1/<head>`: a verify report is no row, and Pending You is not called

#### Scenario: Posted again
- **WHEN** swb-1-conductor runs the same post a second time
- **THEN** Pending You gives the same card back under the same key, and no second card is made

#### Scenario: A key that is not the agent's
- **WHEN** swb-1-conductor runs `crew card post proposal/9`
- **THEN** the command refuses in the hook's words, naming the keys that are swb-1-conductor's, and Pending You is not called

#### Scenario: A card in another form than its row's
- **WHEN** swb-1-conductor posts its landing card as a choice
- **THEN** the command refuses, naming the form a landing's card takes, and Pending You is not called

#### Scenario: A card that sets crew's fields
- **WHEN** a card on standard input gives its own `areaId`
- **THEN** the command refuses, saying crew sets `idempotencyKey`, `areaId` and `session` itself

#### Scenario: No kit's area yet
- **WHEN** Pending You matches no area to the worktree's remote `github.com/WilldanGroup/switchboard-kit`
- **THEN** crew makes the area under `create-area:WilldanGroup/switchboard-kit`, named `switchboard-kit`, in the partition's group, and files the card there

### Requirement: A crew agent's card is changed, closed and read through crew
`crew card change <key>` SHALL change the card the agent holds under the key with the fields given on its standard input, at the version Pending You reports, and SHALL refuse a change that takes a row's card out of its form, as the hook does. `crew card close <key>` SHALL close it with `--outcome` once the agent has acted on its answer, or withdraw it with `--reason`, and SHALL then end its plannotator session as a close through Pending You's tools does. `crew card read <key>` SHALL print the card's status, whose turn it is and, when it is the agent's, the user's answer and words, and SHALL record nothing. The card a key names SHALL be the agent's newest card posted under it on this host that no close has closed; with none, each command SHALL refuse, naming the key.

#### Scenario: A change
- **WHEN** swb-1-conductor runs `crew card change land/b1/<head>` with a new summary and a change note
- **THEN** Pending You is asked to change that card at the version it last reported, and a `card.update` entry names it

#### Scenario: An answer read
- **WHEN** the user has approved swb-1-conductor's landing card with a note
- **THEN** `crew card read land/b1/<head>` prints that it is the agent's turn, the approval and the note

#### Scenario: Closed on its answer
- **WHEN** swb-1-conductor runs `crew card close land/b1/<head> --outcome "Told wldn-ops to land b1."`
- **THEN** Pending You is told the answer was acted on at the card's version, a `card.close` entry names the card, and the card's plannotator session ends

#### Scenario: Withdrawn
- **WHEN** swb-1-conductor runs `crew card close land/b1/<head> --reason "A fix moved the bolt's head"`
- **THEN** Pending You withdraws the card with that reason, and a `card.close` entry names it

#### Scenario: A card lost to its owner
- **WHEN** the host has signed in to Pending You again, and swb-1-conductor runs `crew card read land/b1/<head>` for a card it posted before
- **THEN** the command refuses, saying the card is lost to its owner and to post the row's card again with `crew card post land/b1/<head>`, its summary saying an older copy is dead; and once posted again, the new card is the one the key names

#### Scenario: No card under the key
- **WHEN** swb-1-conductor runs `crew card read land/b1/<head>` and has posted no card under it
- **THEN** the command refuses, saying swb-1-conductor holds no open card under that key

## REMOVED Requirements

### Requirement: A verify report's card is the conductor's options
**Reason**: A verify report waits on no one: its findings are fixed in one round with no card (record 0027, `teams.17`).
**Migration**: A card posted under `verify/<unit>/<stamp>` before is a card whose row is gone: the rail names it for its owner to close.
