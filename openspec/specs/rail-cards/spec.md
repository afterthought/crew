# rail-cards Specification

## Purpose
Each decision on the rail reaches the user as one Pending You card from the agent that owns it, answered on the Mac or the phone, kept true by crew's own events, and shown on the rail so a stale card is seen at once.

## Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, derived from the row's state: `proposal/<n>` for an open proposal, `batch/<n>` for review batch n, and `land/<bolt>` for a bolt whose every unit has merged, one key for the bolt whatever its head (record 0031). A row's owner SHALL post its card with that key as the card's idempotency key. There SHALL be no review row and no verify row, and no `review/<unit>/<head>` or `verify/<unit>/<stamp>` key. A batch whose cards were posted under `batch/<n>-<k>` before one card per batch was built SHALL keep a row for each of those keys until its card closes, and SHALL have no `batch/<n>` row.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2`, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, and the planner may not post `batch/2`

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was ready to land at head `abc1234`, a note on its landing card named a defect, and a fix landed on the bolt at `def5678` with its verification green
- **THEN** its landing row's key is still `land/y`, and crew raises a new landing card under it, following the one the fix held

#### Scenario: A unit built again
- **WHEN** unit `u` was constructed at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** no review row or key exists for either head; the unit's revised change is due for the partition's next batch, whose card's key is the batch's

#### Scenario: A verify report saved
- **WHEN** unit `u`'s verify saves its report `verify-u-20261013-1200.md`
- **THEN** the rail has no row for it, and a card keyed `verify/u/20261013-1200` belongs to no row

### Requirement: The owner of a row posts its card
When an agent crew started has Pending You's tools, it SHALL post one card for each row it owns: the planner for each proposal it opens and for each review batch, and a conductor for its bolt once every unit and chore has merged and its verification is green. It SHALL post no second card for a row that has one open to it; a card lost to it is not, and is posted again as *A row's card lost to its owner is posted again* says. A team's cards SHALL be its conductor's: its ops and every stage agent SHALL post no card, and no crew agent SHALL post a card that is not a row's. No card SHALL be posted for a verify report, which is no row.

#### Scenario: A proposal opened
- **WHEN** the planner opens proposal 4 in a session with Pending You's tools
- **THEN** one card keyed `proposal/4` is open, asked by the planner

#### Scenario: A batch due
- **WHEN** the reviewer delivers batch 3 of seven units
- **THEN** one card keyed `batch/3` is open, asked by the planner, and no conductor posts one

#### Scenario: No Pending You
- **WHEN** a conductor's session has no Pending You tools and its bolt's verification is green with every unit merged
- **THEN** no card is posted, the rail row is as before, and the conductor tells the operator agents it waits on the user

#### Scenario: A verify report saved
- **WHEN** a unit's verify saves its report, which marks two findings fix
- **THEN** its conductor posts no card and asks the user nothing, and runs code once more with the report's path

#### Scenario: A proof leaves the user a check
- **WHEN** a bolt's changes leave a check only the user can make on their Mac
- **THEN** no proof asks it and ops posts no card: it is an after-deploy step on a deploy's card, and the bolt's landing card asks only for the landing

### Requirement: A card says whose it is and where it belongs
crew SHALL ask each card in the name of the role whose row it is, with the host as the session's machine and the kit's checkout as its folder; a question's card SHALL be asked in its asker's crew name by the asker's session. A card SHALL be filed in the area of its kit, found by the kit's git remote, in the group named for its partition; crew SHALL create a kit's area that does not exist with the key `create-area:<owner>/<kit>`, and an agent SHALL create one under no other key and never a group. A card's title SHALL be the question, read cold, naming the thing.

#### Scenario: A review card
- **WHEN** a unit's change is due for a batch
- **THEN** no review card is asked for it; the batch's card, asked in the planner's name, names the unit and its team

#### Scenario: The first card in a kit
- **WHEN** crew raises the first card in switchboard-kit and Pending You matches no area to its remote
- **THEN** crew makes the area under `create-area:WilldanGroup/switchboard-kit`, named `switchboard-kit`, in the partition's group, and files the card there

#### Scenario: A landing card
- **WHEN** crew raises bolt `y`'s landing card for swb-1's team in switchboard-kit
- **THEN** the card is asked as `swb-1-conductor` on the team's host, sits in switchboard-kit's area in the `wldn` group, and its title asks whether to land bolt `y` on the kit's main

### Requirement: A card carries what the user would read and the row's answers
A proposal's card SHALL hold the proposal whole, its picture, its text and its case, and SHALL carry a reading session's link only when it holds more than fifteen new units. A batch's card SHALL carry its one session's link. A landing's, a deploy's, a step's and a record's card SHALL carry no link to a session: each holds what the user decides from.

#### Scenario: A review card's options
- **WHEN** a unit's change is due for a batch
- **THEN** no review card offers its approval; the batch's card asks nothing and its notes go to the unit's team

#### Scenario: A review card's link
- **WHEN** a unit's change is read in batch 3
- **THEN** the batch's card carries the one link to batch 3's session, and no card carries a link to the unit alone

#### Scenario: Answered in the session rather than on the card
- **WHEN** the user annotates a unit's change in the batch's session and sends the annotations
- **THEN** the planner's `crew card wait batch/3` returns them, they go to the unit's conductor as the user's words, and the batch's card is closed

#### Scenario: A proposal's card holds the proposal whole
- **WHEN** crew raises the card for proposal 4, which adds two units
- **THEN** the card carries the picture, the text and the case, and no session link

#### Scenario: A landing card has nothing to read
- **WHEN** crew raises bolt `y`'s landing card
- **THEN** it names the units and chores that land, sluice's verdict and when, and how far main has moved, and carries no link to a reading session

### Requirement: Landing is approved only by holding the button
A landing's card SHALL be an `approve` of risk high, not reversible, so it is approved by holding the button in the Pending You app and never with a key in Herdr's popup; it SHALL NOT carry the `highStakes` flag, which Pending You refuses on an approval.

#### Scenario: Landing from the popup
- **WHEN** the user presses the approve key on a landing card in Herdr's popup
- **THEN** Pending You refuses it as high risk, and the bolt does not land

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

### Requirement: An agent never runs Pending You from npm or waits on a hold
An agent crew started SHALL adopt a card crew posted by calling Pending You's `get_request` with the card's id under its own name, as the line crew prints or tells it says, from which the fleet's wake mod adopts the card and wakes the agent's session once the card is answered and the session is idle; it SHALL run no `pendingyou` command, `hold` and `watch` among them, none through `npx`, and wait on no hold. After a fresh start it SHALL read `crew rail` for its open cards and adopt each the same way.

#### Scenario: Restarted with an answered card
- **WHEN** a conductor restarts while the user has answered its landing card
- **THEN** at its start `crew rail` names the card and its id, the conductor adopts it and acts on the answer

### Requirement: crew names the card a change ends
When crew records a change that ends a row, it SHALL name that row's card to its owner: in the command's output when the owner made the change, and by a notice when anyone else did. That covers a proposal approved, dropped or replaced; a unit approved, built again, merged, moved off its team or dropped; and an amended intent. A bolt landed or dropped tells its conductor so, and names no card: crew closes the bolt's landing card itself.

#### Scenario: The user approves a unit from the rail's shell
- **WHEN** the user runs `crew unit approve x --label wldn`
- **THEN** swb-1-conductor is told that unit `x` was approved and to close its card for `review/x`

#### Scenario: The conductor builds a unit again
- **WHEN** swb-1-conductor runs `crew unit run x construct "<words>"` on a unit in review
- **THEN** the command's output names the card for `review/x` to close

#### Scenario: A bolt lands
- **WHEN** main-level ops runs `crew bolt land y`
- **THEN** the conductor of the team that held `y` is told it landed, and crew closes its landing card on the team's host

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

### Requirement: The rail shows each row's card
`crew rail` SHALL print, under each row, the row's card key, whether a card with that key is open, its id and whose it is, and after the groups the open question cards, each with its key, which names it, its asker and its age, and the open record cards apart. A card is open from its `card.post` entry until a `card.close` entry for the same card, or until a later `card.post` under the same key names another card, which is then the row's card while the older is taken as lost.

#### Scenario: A row with its card
- **WHEN** bolt `y` reads proven and crew's card `req_l1` under `land/y` is open
- **THEN** the row's card line names `land/y` as open, `req_l1`, the conductor's

#### Scenario: A row without a card
- **WHEN** a proposal is open and its card's post was refused
- **THEN** the row's card line names `proposal/<n>` with no card open and the refusal's words

#### Scenario: A card posted again under its row's key
- **WHEN** crew's card `req_1` under `proposal/17` read not found after the host signed in again, and the rail read posted `req_2` under `proposal/17`
- **THEN** the row's card line names `req_2` as its open card, and `req_1` is listed as lost

#### Scenario: A row with its card and a question open
- **WHEN** `proposal/4`'s card `req_p4` is open and swb-1-conductor's question `req_q1` is open
- **THEN** the proposal row's card line names `proposal/4`, open, `req_p4`, the planner's; and after the groups `req_q1` is listed with its key, swb-1-conductor and its age

### Requirement: The rail names an open card whose row is gone
After its groups, `crew rail` SHALL list each card its sweep withdrew or closed on this read, with its key, its owner and why (its row is gone, its asker ended), and each card it posted again as lost.

#### Scenario: A forgotten card
- **WHEN** proposal 4 was approved from the planner's pane and its card `proposal/4` is still open
- **THEN** the next rail read closes it with the approval's outcome and lists it, "closed: its proposal was applied"

#### Scenario: A withdrawn card
- **WHEN** bolt `y` was dropped while `land/y`'s card was open
- **THEN** the rail withdraws the card and lists it, "withdrawn: its bolt was dropped"

### Requirement: The conductor's tell to the operator agents is for what has no card
A conductor with Pending You's tools SHALL NOT tell the operator agents when it waits on the user for a review or a landing, since that row's card reaches the user. It SHALL tell them when it waits on a question asked only in its pane, and for every wait when it has no Pending You tools. A verify report is no wait on the user, and is told to no one.

#### Scenario: A unit reaches review
- **WHEN** a conductor with Pending You's tools has posted the card for a unit in review
- **THEN** it sends no tell to the operator agents for it

#### Scenario: A question in the pane
- **WHEN** a stage stops on a question for the user that only the conductor's pane holds
- **THEN** the conductor tells the operator agents in one line what it waits for and where

### Requirement: A card's words are the document's own
A crew card's words SHALL be prose the phone wraps, in short paragraphs, cut at whole sentences to Pending You's budget, with nothing the user has to read as raw Markdown; where a card speaks for a document, a proposal's case, a unit's opening paragraph, a record's opening sentences, it SHALL use the document's own words, never reworded. A list the user scans, the units that land, a deploy's steps, a proposal's change, SHALL be an artifact on the card's face, one thing a line and no line over forty characters, never a comma run in the summary or the background; the background SHALL hold only what is read when the face is not enough. A path SHALL appear only inside a step's command or a deploy's log name.

#### Scenario: Six units on a landing card
- **WHEN** crew raises the landing card of a bolt of six units
- **THEN** the six names are a text artifact on the face, one a line, and the background names none of them

#### Scenario: A card follows the card its thing follows
- **WHEN** crew raises srv's deploy card for a head that landing #24's card put on main
- **THEN** the card follows landing #24's card, and the phone shows it in that card's thread

#### Scenario: A review card
- **WHEN** unit `x`'s change is read in batch 3
- **THEN** the batch's card carries `x`'s reviewer paragraph in the reviewer's words, and no card carries `x`'s Why alone

#### Scenario: A verify card
- **WHEN** a unit's verify saves a report that raised two warnings
- **THEN** no card carries it: a verify report waits on no one, and its findings are fixed in one round

#### Scenario: A change too long for the summary
- **WHEN** a batch's paragraphs run past what the summary holds
- **THEN** the summary ends at the last whole sentence that fits, and the background holds every paragraph

#### Scenario: A proposal card
- **WHEN** crew raises the card for proposal 4
- **THEN** its title, summary, background, questions and artifacts are built from the plan and the proposal, the case and each change in the proposal's words

#### Scenario: A batch card's summary
- **WHEN** crew raises batch 7's card for four units
- **THEN** each unit's paragraph is the reviewer's opening paragraph as prose in its summary and details, with no code block in its words, the reviewer's summary rides its face as inline Markdown, and the card wraps on the phone

### Requirement: A row's card is closed when the row's key changes
When a row's key changes because what it asks changed, a unit built again, the row's owner SHALL close the card it holds under the old key with a one-line outcome, and post the row's card under the new key once the row asks again. A landing's key is its bolt's and does not change: when a merge moves the bolt's head while its landing card is open, crew SHALL change the card in place, and a card under an older head's key, `land/<bolt>/<head>` from before, SHALL belong to no row.

#### Scenario: A fix moves a bolt with an open landing card
- **WHEN** the landing card `land/y` is open, a fix is started on bolt `y`, and the fix merges, moving its head to `def5678`
- **THEN** the card was withdrawn when the fix started, held for it, and crew raises a new card under `land/y`, following it, once `y` reads proven at `def5678`

#### Scenario: A landing card forgotten under an old head
- **WHEN** a card keyed `land/y/abc1234`, posted before the key was the bolt's, is still open while bolt `y` waits to land
- **THEN** `crew rail` shows `land/y` under the landing row, and the card under `land/y/abc1234` belongs to no row, for the rail's read to close

#### Scenario: A merge moves a bolt with an open landing card
- **WHEN** the landing card `land/y` is open and a merge into bolt `y` moves its head to `def5678`
- **THEN** crew changes the card in place, "Its head is now def5678", and posts no second card

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
- **WHEN** a conductor posts a card keyed `land/y` as an `action` with the landing command as its step
- **THEN** crew refuses it before Pending You is called, saying a landing's card is an approval marked high stakes whose yes has the conductor tell main-level ops to land, and no card is posted

#### Scenario: A landing card not marked high stakes
- **WHEN** a conductor posts a card keyed `land/y` as an approval without `highStakes`
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

### Requirement: crew refuses a change that takes a row's card out of its form
Before `update_request` runs on a card a crew agent on this host posted under a row's key, crew SHALL refuse a change that clears a landing card's high stakes, gives options to an approval, or gives steps to any card but a landing's.

#### Scenario: A landing card loses its high stakes
- **WHEN** a conductor updates its open landing card with `highStakes` false
- **THEN** crew refuses the update, and the card stays high stakes

### Requirement: crew checks only a row's card in a crew session
crew SHALL check only sessions it started: any card in a session crew did not start, and a tool of another server, SHALL pass unchecked. In a session crew started, every card is checked: a row's card for its form, and every key against the rows the agent owns, as the requirement on keys below says.

#### Scenario: The user's own session
- **WHEN** the user, in a session crew did not start, posts any card under any key
- **THEN** crew checks nothing and lets it through

### Requirement: crew refuses a crew agent's card under any key but a row's of its own
Before a Pending You card is posted from a session crew started, crew SHALL refuse it unless its idempotency key is the card key of a rail row the agent owns: for the planner, `proposal/<n>` for an open proposal of its partition; for a conductor, `review/<unit>/<head>` for a unit of the bolt its team holds, or `land/<bolt>` for that bolt; `verify/<unit>/<stamp>` is no agent's. Every other crew agent SHALL own no key. A refused card SHALL NOT reach Pending You, and its refusal SHALL name the keys to use.

#### Scenario: ops posts a card
- **WHEN** brd-2-ops calls Pending You's `post_request` under any key
- **THEN** the call is refused before it reaches Pending You, and the refusal says ops owns no key: a team's cards are its conductor's, and what is left for the user goes in the proof file

#### Scenario: A conductor posts under a key of its own making
- **WHEN** brd-2-conductor, whose team holds bolt `y`, posts a card keyed `gateway-check-y`
- **THEN** the call is refused, and the refusal names `land/y` and the review keys of `y`'s units, read from `crew rail`

#### Scenario: A conductor posts another team's row
- **WHEN** brd-2-conductor posts a card keyed `review/z/abc1234` for a unit `z` of a bolt another team holds
- **THEN** the call is refused, naming the keys that are brd-2-conductor's

#### Scenario: The planner posts a proposal's card
- **WHEN** wldn-planner posts a card keyed `proposal/4` while proposal 4 of `wldn` is open
- **THEN** the call goes through, and the card is recorded as before

#### Scenario: A conductor posts a verify report's card
- **WHEN** brd-2-conductor, whose team holds bolt `y`, posts a card keyed `verify/u/20261013-1200` for a unit `u` of `y`
- **THEN** the call is refused before it reaches Pending You, naming `land/y`

### Requirement: The check refuses what it cannot read, and only for crew's sessions
When crew cannot read the teams file, the plan or the proposals a card's or an area's check depends on, it SHALL refuse the call and name what it could not read. A session crew did not start SHALL NOT be checked.

#### Scenario: The plan cannot be read
- **WHEN** a conductor posts a card keyed `land/y/<head>` and the partition's state branch cannot be fetched
- **THEN** the call is refused, naming the branch that could not be read, and the conductor posts it again later

#### Scenario: The user's own session
- **WHEN** a Claude session crew did not start posts a Pending You card or creates an area under any key
- **THEN** crew neither checks nor refuses it

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

### Requirement: crew's card commands refuse what they cannot do, in the words that say why
A card act Pending You refuses SHALL be refused in Pending You's own words and recorded as the act refused, and SHALL refuse nothing of the event it was raised for. When the host is not signed in to Pending You, or Pending You cannot be reached or does not answer within 60 seconds, the act SHALL be recorded as not posted, the command SHALL say so, and the event SHALL stand. A reply that lacks the card's or the area's id SHALL be recorded as unread, never taken as empty.

#### Scenario: Pending You refuses the card
- **WHEN** Pending You refuses a card crew posts with "Approve requests give their risk in approve.risk."
- **THEN** the command says so in those words, the run record has a `card.post` entry with that refusal and no card, and the event it was raised for stands

#### Scenario: The host is not signed in
- **WHEN** the host has no Pending You sign-in and `crew ops offer` runs
- **THEN** the offer is recorded, no card posts, and the command says this computer is not signed in to Pending You

### Requirement: The landing card is posted once the bolt's verification is green
crew SHALL raise a bolt's landing card once every unit and chore of the bolt has merged, every unit's latest change has been in a batch, sluice's verdict at its head is green and no fix is in flight on it, keyed `land/<bolt>`, as an `approve` of risk high, not reversible, because irreversible, its summary giving the counts, the batches, the verdict and when, and how far main has moved, its face a text artifact "What lands: N units, M chores" naming each one a line, its rationale what follows, and, when sluice's submission at the head has a pull request on GitHub, that pull request as a `url` artifact and among its links; it SHALL ask only for the landing. A note naming a defect SHALL have the conductor start a fix on the bolt, which withdraws the card, and the card SHALL be raised again once the bolt reads proven again.

#### Scenario: Sluice's pull request
- **WHEN** sluice's submission at `y`'s head has pull request #23 on the kit's GitHub
- **THEN** the card links it, titled as sluice's pull request for the landing, on its face and in its details

#### Scenario: No pull request
- **WHEN** the kit's sluice opens no pull request for a submission
- **THEN** the card carries no link, and says nothing of one

#### Scenario: A green bolt
- **WHEN** every unit and chore of bolt `y` has merged, each unit's latest change has been in a batch and sluice is green at `abc1234`
- **THEN** one card keyed `land/y` is open, an approve of risk high, naming the units and chores and the verdict

#### Scenario: A defect noted on the card
- **WHEN** the user answers `land/y` with a note naming a defect and the conductor runs `crew fix` on `y`
- **THEN** the card is withdrawn, "held for a fix: <the note>", and a new card is raised when `y` reads proven again

### Requirement: A batch's card is a notice naming every unit
A batch's card, keyed `batch/<n>`, SHALL be a Pending You notice (`fyi`) crew raises when the reviewer delivers the batch's summary, that asks nothing: no options, no question, no approval and no steps. Its title SHALL say what the batch is about, drawn from its units' subjects, with the batch's number after; its summary SHALL say first "N changes to read, nothing to approve", since the batch before it when there is one; its words SHALL say where notes go, the reading session or the card's own note, that each reaches its unit's team as the user's words, and that the units go on building whatever the user does with the card. The reviewer's summary SHALL ride the face as inline Markdown, a paragraph per unit under its name and team.

#### Scenario: A card of six units
- **WHEN** crew raises the card for batch 2 holding six units
- **THEN** the card is one `fyi` titled with batch 2, whose summary opens "6 changes to read, nothing to approve", whose words say the units go on building, whose face and background name all six units with their teams and paragraphs, and whose one link opens the batch's session

### Requirement: A batch's card names every unit and links its session
A batch's card's words SHALL name every unit of the batch with its team and hold each unit's opening paragraph from the reviewer's summary as prose, with no code block, and it SHALL have one link, to the batch's reading session, in its words first and among its links.

#### Scenario: Six units named
- **WHEN** crew raises the card for batch 2 holding six units of two teams
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
None of the six cards crew builds SHALL ask a question in words: no `text` field and no question of kind `text`, since Pending You makes every question required and the card's note is where the user's words go. A question card an agent asks is its asker's and may.

#### Scenario: A proposal card with a text question
- **WHEN** crew builds the card for proposal 4
- **THEN** it has no question of kind `text`: the approval, the unit questions and the note

### Requirement: A card's picture is uploaded
A picture a crew card needs, the proposal's drawing of each bolt once approved, SHALL be an artifact of kind `image` posted with `upload: true`, the file then put to the upload URL Pending You returns for it with the file's content type, so the user sees the picture; never an artifact of kind `path`. A question card's image SHALL be uploaded the same way by its asker.

#### Scenario: A screenshot on a card
- **WHEN** a conductor's question card needs a screenshot of a page
- **THEN** the card holds one artifact of kind `image` posted with `upload: true`, the conductor puts the image to the upload URL the post returned with its content type, and the user sees the picture on the card, with no path of the image anywhere on it

### Requirement: A card's document is inline Markdown
A document's substance shown on a crew card beyond its words SHALL be inline Markdown, an artifact of kind `code` with lang `markdown` and the text as its lines, never an uploaded file or HTML: a record's card carries the record whole so, a proposal's its new units' paragraphs, a batch's the reviewer's summary, a deploy's the kit's release notes. The only artifacts a crew card carries SHALL be such a picture, such Markdown, a list as text (a landing's units, a deploy's steps, a proposal's change), a link as a `url` artifact (sluice's pull request, a batch's reading), and a step's commands as action steps.

#### Scenario: A document's substance on a card
- **WHEN** crew raises record 32's card
- **THEN** its one artifact is the record as Markdown, its lines the record's text, and no file is attached

#### Scenario: A card with nothing to show
- **WHEN** crew raises a landing card
- **THEN** its artifacts are the units that land as text and, when sluice opened one, the pull request's link, and it carries no reading session

### Requirement: A proposal's card carries its change as text
A proposal's card SHALL carry its change as an artifact of kind `code` with lang `text`, its lines those `crew plan card <n>` prints, each at most forty characters, so it reads in monospace on a phone without wrapping.

#### Scenario: A proposal's change as text
- **WHEN** the planner posts the card for proposal 4, which drops a unit and adds two
- **THEN** the card carries two artifacts, the uploaded picture and a `code` artifact of lang `text` holding the change as `crew plan card 4` prints it, and no Markdown artifact and no link

### Requirement: A row's card lost to its owner is posted again
A card Pending You answers "not found" to the host's connection is lost: the host signed in anew. On the next rail read, while the row still waits, crew SHALL post the row's card again under the row's key, in the row's form, its summary saying that an older copy is dead, to dismiss it in the app, and that this card is the one to answer, and SHALL take the newer card as the row's. A lost card whose row is gone SHALL be posted again by nobody.

#### Scenario: The host signed in again
- **WHEN** the host runs `pendingyou-signin` while `proposal/17`'s card is open, and the rail is read
- **THEN** crew posts a new card under `proposal/17`, whose summary says an older copy of this card is dead, to dismiss it in the app, and to answer this one, and the rail shows the new card's id as the row's

#### Scenario: A close that finds nothing
- **WHEN** `crew plan approve 9` closes proposal 9's card and Pending You answers "not found"
- **THEN** crew posts no card for it, since the row no longer waits, records the close as lost, and goes on

#### Scenario: A lost landing card
- **WHEN** bolt `y` waits to land and `land/y`'s card reads "not found" when a fix moves the head and crew changes the card
- **THEN** crew posts the landing card again under `land/y`, an approval of risk high naming the bolt, its summary saying the older copy is dead and this one is the one to answer

#### Scenario: A lost operations card
- **WHEN** `deploy/dev`'s card reads "not found" while the deploy's offer still waits
- **THEN** the next rail read posts the deploy's card again under `deploy/dev`, its summary saying the older copy is dead and this one is the one to answer

### Requirement: The design agent posts a record's card under its record key
Besides the row keys, crew SHALL let the partition's design agent post a card under `record/<kit>/<number>/<commit>`, where `<kit>` is the name of a kit one of its partition's teams builds, `<number>` the record's four digits and `<commit>` the seven hex digits of the commit that proposed the record or the amendment. No other crew agent SHALL post under a record key. A record key with a kit that is not its partition's, or in any other shape, SHALL be refused naming the record key's form.

#### Scenario: The design agent posts a record's card
- **WHEN** wldn-design posts a card keyed `record/atlas-kit/0021/abc1234`, and atlas-kit is built by one of wldn's teams
- **THEN** the call goes through, and the run record has a `card.post` entry on `record/atlas-kit/0021` with that key

#### Scenario: A kit outside the partition
- **WHEN** wldn-design posts a card keyed `record/flywheel-next/0003/abc1234`, and no team of wldn builds flywheel-next
- **THEN** the call is refused before it reaches Pending You, naming `record/<kit>/<number>/<commit>` and wldn's kits

#### Scenario: Another agent posts under a record key
- **WHEN** wldn-planner or a conductor posts a card keyed `record/atlas-kit/0021/abc1234`
- **THEN** the call is refused as before, naming the keys that are its own

#### Scenario: The design agent posts under any other key
- **WHEN** wldn-design posts a card keyed `proposal/1`
- **THEN** the call is refused, naming `record/<kit>/<number>/<commit>` as the one key the design agent posts under

### Requirement: A record key is checked against the teams file alone
`crew record`'s check of the kit SHALL read nothing beyond the teams file.

#### Scenario: Checked with the plan unread
- **WHEN** wldn-design runs `crew record atlas-kit 21 --proposed` while wldn's plan can't be read
- **THEN** the card is raised on the teams file alone

### Requirement: A record card's acts are recorded on the record
A record card's acts SHALL be recorded in the run record on `record/<kit>/<number>` with the card's key in `Key`, and closing one SHALL end no plannotator session.

#### Scenario: A record's card closed
- **WHEN** wldn-design runs `crew record atlas-kit 21 --accepted` once the user said yes
- **THEN** the run record has a `card.close` entry on `record/atlas-kit/0021` with that key, and no plannotator session is ended

### Requirement: A record's card is an approval
A record's card SHALL be an `approve` of risk low, reversible, with no options and no steps, titled "Accept record <number> in <kit>: <title>", its summary the record's opening sentences, its background the record's decision and, when the record quotes the user's words from the design talk, "Your own words, recorded as your decision:" and the quote, and one artifact, the record whole as Markdown; it SHALL link no reading session. When the design agent runs `crew record … --proposed --alternatives <file>`, because a rule of the user's decided the record between alternatives, the card SHALL instead be a choice asked once: loosen the rules as drafted and take the other path, accept the record as ruled, or send it back with a note; its face SHALL carry that file as inline Markdown, the alternatives, the rules that decided and each rule as it would read loosened, before the record whole, and the recommended option SHALL be the one the user's own quoted words point to, else accepting as ruled. crew builds both, so no other form arises.

#### Scenario: A record card marked high risk
- **WHEN** crew raises record 21's card with no alternatives file
- **THEN** it is an approval of risk low, reversible true, with the record's opening sentences and the Markdown, and no options

#### Scenario: A record card as a choice
- **WHEN** the design agent runs `crew record switchboard-kit 32 --proposed --alternatives alternatives.md`, the file naming two ways, `ops.3` and `ops.7` as the rules that chose, and each loosened
- **THEN** the card is a choice of loosen, as ruled, or send back, with the file's Markdown on its face before the record, and the user's answer reaches the design agent as the record's status

#### Scenario: An alternatives file crew cannot read
- **WHEN** `--alternatives` names a file that is not there
- **THEN** the command refuses, naming the file, and raises nothing

### Requirement: The rail lists open record cards apart
After its groups, `crew rail` SHALL list each open record card under a heading of its own, with its key, the design agent and when it was raised, and SHALL NOT list it among the cards whose row is gone.

#### Scenario: A record waiting on the user
- **WHEN** `record/atlas-kit/0021`'s card is open
- **THEN** `crew rail` lists it under the record heading, in wldn-design's name, and not among the cards whose row is gone

#### Scenario: A record answered
- **WHEN** that card has been closed
- **THEN** `crew rail` no longer lists it

### Requirement: A deploy's card is a high approval
A deploy's card SHALL be an `approve` of risk high, not reversible, because irreversible, naming the environment and the commit; its summary SHALL count the landings since the environment's last deploy and name the environments before and after it, and its details SHALL hold the landings' subjects. It SHALL follow the landing card that put the offered commit on main, when there is one.

#### Scenario: Three landings since srv's last deploy
- **WHEN** the deployer offers srv `c882cff` with git-cliff's notes for `6aed25c..c882cff` and two steps, and srv runs `6aed25c`
- **THEN** the card's approve block has risk high and reversible false, its summary counts three landings and says the box follows on its own and mac-studio is offered after srv, its face holds the notes as handed and the two steps with their doers, and its details name landings #16, #17 and #18

### Requirement: A raised card is adopted by its owner
The command that raises a card SHALL print the card's id and the line that adopts it, `call get_request (requestId <id>, name <role>)`, and when the card is raised outside its owner's turn, a landing found on a rail read or the deployer's offer, SHALL tell the owner that line with `crew tell`.

#### Scenario: A deploy offered by the deployer
- **WHEN** the deployer runs `crew ops offer srv --to abc1234`
- **THEN** one card keyed `deploy/srv` is open in main-level ops's name, and main-level ops is told `call get_request (requestId <id>, name <role>)` by `crew tell`

#### Scenario: A proposal's card in the planner's own shell
- **WHEN** the planner's `crew plan propose` raises proposal 4's card
- **THEN** the command prints the card's id and `call get_request (requestId <id>, name <role>)`, and no tell is sent

### Requirement: A card the user answered is followed by its new version
When crew changes one of its own cards because its thing changed, it SHALL change the card in place while the card waits on the user. Once the user has answered the card, which Pending You no longer changes, crew SHALL ack it with the change note as its outcome and post the new version as a new card that follows it, in the same owner's name. The run record SHALL hold the answered card's close and the new card's post, both under the row's key.

#### Scenario: A card waiting on the user
- **WHEN** crew changes its card `req_1` under `land/b1`, which waits on the user
- **THEN** `req_1` is changed in place with the change note

#### Scenario: A card the user answered
- **WHEN** crew changes its card `req_1` under `land/b1` after the user has answered it
- **THEN** `req_1` is acked with the change note, and a new card following `req_1` is posted. The run record has `req_1`'s close and the new card's post under `land/b1`, and `crew card read land/b1` finds the new card

### Requirement: A card posted after a closed one takes its key's revision
Every card crew posts under a row's key after a card of the owner's under that key has closed SHALL take the key with its revision, `<key>:<n>`, as its idempotency key, so Pending You never gives the closed card back. A card still open under the key SHALL keep its own key, so posting it again gives it back.

#### Scenario: A card raised again after its last card closed
- **WHEN** crew raises b1's landing card after the user declined the last one under `land/b1`, or follows an answered one with its new version
- **THEN** it is posted under `land/b1:2` as a new card

#### Scenario: A card posted again while it is open
- **WHEN** crew posts its card under `land/b1` again while `req_1` is open there
- **THEN** it is posted under `land/b1`, and Pending You gives `req_1` back

### Requirement: A question whose asker is gone is withdrawn
On each rail read crew SHALL withdraw, under the host's connection, every open question card whose asker herdr no longer lists as an agent, with the reason naming the asker, and SHALL say so.

#### Scenario: A conductor's question outlives it
- **WHEN** crw-3-conductor's question card is open and crw-3's team is closed
- **THEN** the next rail read withdraws it with "crw-3-conductor ended; ask again if it still matters"

### Requirement: A deploy's card carries the kit's release notes and steps as the deployer hands them
A deploy's card's face SHALL carry the kit's release notes for exactly the range since the environment's last deploy, as the deployer hands them to `crew ops offer --notes <file>`, as inline Markdown, and the range's after-deploy steps with their doer, the user's, an agent's or held, as a text list, as the deployer hands them with `--steps <file>`; crew SHALL write no notes of its own, and an offer handed none SHALL give the landings' subjects alone.

#### Scenario: A kit that hands no notes
- **WHEN** the deployer offers mac-studio `c882cff` with no `--notes` and no `--steps`
- **THEN** the card's face gives the landings since mac-studio's last deploy by subject, and says the kit handed no release notes

### Requirement: A step's card is the user's do
A step whose doer is the user SHALL be a `do` card with the step's words, where it is done, each command whole as an action step, what is seen when it worked, and the options Done, Skip and Later. A step an agent runs on its own SHALL have no card. When a deploy ends with more than one step for a card, crew SHALL raise one card at a time: the first following the deploy's card, each next one following the one before, raised when crew closes it.

#### Scenario: Two steps after one deploy
- **WHEN** srv's deploy ends with a step that is the user's and a step held for the user's word
- **THEN** one card is open, following the deploy's card, and the second is raised following the first when the first is closed

#### Scenario: A password only the user can rotate
- **WHEN** the deployer records a step with doer user and two commands
- **THEN** the card keyed `op/srv/1` is a `do` with both commands whole, where to run them, when it is done, and Done, Skip and Later

#### Scenario: A step an agent runs on its own
- **WHEN** the deployer records a step with doer main-ops, when quiet, not held
- **THEN** no card is raised, and the step runs at the quiet moment

### Requirement: A held step's card is a choice of when
A step an agent can do that the change marked held for the user's word SHALL be a choice between now, when the host is quiet (recommended) and skip, each with its consequence; the agent SHALL do it at once or at the quiet moment as the user picks, or record it declined on skip.

#### Scenario: A restart held for the user's word
- **WHEN** the deployer records a step with doer main-ops marked held
- **THEN** the card is a choice of now, when quiet and skip, when quiet recommended with "no stage is cut", now with the stages it cuts, and the step runs when the user picks
