# rail-cards Specification

## Purpose
Each decision on the rail reaches the user as one Pending You card from the agent that owns it, answered on the Mac or the phone, kept true by crew's own events, and shown on the rail so a stale card is seen at once.

## Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, derived from the row's state: `proposal/<n>` for an open proposal, `batch/<n>` for review batch n, and `land/<bolt>/<head>` for a bolt ready to land (the first seven characters of the bolt's branch head). A row's owner SHALL post its card with that key as the card's idempotency key. There SHALL be no review row and no verify row, and no `review/<unit>/<head>` or `verify/<unit>/<stamp>` key. A batch whose cards were posted under `batch/<n>-<k>` before one card per batch was built SHALL keep a row for each of those keys until its card closes, and SHALL have no `batch/<n>` row.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2`, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, and the planner may not post `batch/2`

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was ready to land at head `abc1234`, a note on its landing card named a defect, and a fix landed on the bolt at `def5678` with its verification green
- **THEN** its landing row's key is `land/y/def5678`, its conductor posts a new landing card under that key, and a card keyed `land/y/abc1234` belongs to no row

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
A card SHALL be asked in the agent's crew name, with its host as the session's machine and its worktree as the session's folder. It SHALL be filed in the area of its kit, found by the kit's git remote, in the group named for its partition. An agent that finds no area for its kit SHALL create it with the key `create-area:<owner>/<kit>`, the kit's repository, and with no other key. Its title SHALL name what it asks and its bolt. An agent SHALL never create a group.

#### Scenario: A review card
- **WHEN** swb-1-conductor posts the card for unit `x` of bolt `y` in switchboard-kit
- **THEN** the card is asked by `swb-1-conductor` on its host, sits in switchboard-kit's area in the `wldn` group, and its title names unit `x` and bolt `y`

#### Scenario: The first card in a kit
- **WHEN** no area matches the kit `WilldanGroup/switchboard-kit`
- **THEN** the agent creates it once, with the key `create-area:WilldanGroup/switchboard-kit`, so two agents posting at the same time make one area

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

### Requirement: Landing is approved only by holding the button
The card for a bolt ready to land SHALL be marked high stakes, so it is approved by holding the button in the Pending You app and never with a key in Herdr's popup.

#### Scenario: Landing from the popup
- **WHEN** the user presses the approve key on a landing card in Herdr's popup
- **THEN** Pending You refuses it as high stakes, and the bolt does not land

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
An agent crew started SHALL hear answers only by being woken in its session, and SHALL NOT run any `npx pendingyou` command or `pendingyou hold`. After a fresh start it SHALL list its own open cards and act on any the user has answered.

#### Scenario: Restarted with an answered card
- **WHEN** a conductor restarts while the user has answered its review card
- **THEN** at its start it finds the answered card among its own, and acts on it

### Requirement: crew names the card a change ends
When crew records a change that ends a row, it SHALL name that row's card to its owner: in the command's output when the owner made the change, and by a notice when anyone else did. That covers a proposal approved, dropped or replaced; a unit approved, built again, merged, moved off its team or dropped; an amended intent; and a bolt landed or dropped.

#### Scenario: The user approves a unit from the rail's shell
- **WHEN** the user runs `crew unit approve x --label wldn`
- **THEN** swb-1-conductor is told that unit `x` was approved and to close its card for `review/x`

#### Scenario: The conductor builds a unit again
- **WHEN** swb-1-conductor runs `crew unit run x construct "<words>"` on a unit in review
- **THEN** the command's output names the card for `review/x` to close

#### Scenario: A bolt lands
- **WHEN** main-level ops runs `crew bolt land y`
- **THEN** the conductor of the team that held `y` is told it landed and to close its card for `land/y`

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
`crew rail` SHALL print, under each row, the row's card key and whether a card with that key is open, and whose it is. A card is open from its `card.post` entry until a `card.close` entry for the same card.

#### Scenario: A row with its card
- **WHEN** unit `x` is in review at `abc1234` and swb-1-conductor's card `review/x/abc1234` is open
- **THEN** the row's card line names `review/x/abc1234` as open, asked by `swb-1-conductor`

#### Scenario: A row without a card
- **WHEN** a proposal is open and no card has been posted for it
- **THEN** the row's card line names `proposal/<n>` with no card open

### Requirement: The rail names an open card whose row is gone
After its groups, `crew rail` SHALL list each open card that matches no row, with its key, its owner, when it was posted, and a pasteable `crew tell` asking the owner to close it. crew SHALL NOT close another agent's card itself.

#### Scenario: A forgotten card
- **WHEN** unit `x` was approved and swb-1-conductor's card `review/x/abc1234` was never closed
- **THEN** the rail lists `review/x/abc1234`, owned by swb-1-conductor, with `crew tell swb-1-conductor "Close your Pending You card review/x/abc1234: its row is gone."`

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

### Requirement: A card's link and bolt come first
A card's summary SHALL begin with the link to its row's plannotator session, then name the bolt, within Pending You's 400 characters, and its background SHALL begin with the same link. The link SHALL be the card's entry in its links and SHALL NOT be carried as an attached artifact. A landing card, which has nothing to read, SHALL name its bolt and carry no link.

#### Scenario: A review card's opening
- **WHEN** swb-1-conductor posts the review card for unit `x` of bolt `y`, whose session's link is `http://mac-studio.ts.swancloud.net:19432`
- **THEN** the card's summary begins with that link and names bolt `y`, its background begins with the link, its links hold it labelled "Read and annotate it in plannotator", and it has no artifact

### Requirement: No card carries a path
A card a crew agent posts SHALL carry no path of a file, a folder or a report: none in its title, summary, background, trace, files touched, links or artifacts.

#### Scenario: A review card's change folder
- **WHEN** a conductor posts the review card for a unit whose change is at `~/Code/kit/places/x/openspec/changes/x/`
- **THEN** that path is nowhere on the card, its files touched is empty, and the change is reached through the session's link

### Requirement: A row's card is closed when the row's key changes
When a row's key changes because what it asks changed, a unit built again or a bolt's head moved by a fix, the row's owner SHALL close the card it holds under the old key with a one-line outcome, and post the row's card under the new key once the row asks again.

#### Scenario: A fix moves a bolt with an open landing card
- **WHEN** the conductor's landing card `land/y/abc1234` is open and a fix merges into bolt `y`, moving its head to `def5678`
- **THEN** the conductor closes `land/y/abc1234` saying the fix changed the bolt, and posts `land/y/def5678` once ops has proved the bolt again

#### Scenario: A landing card forgotten under an old head
- **WHEN** the card `land/y/abc1234` is still open while bolt `y` waits to land at `def5678`
- **THEN** `crew rail` shows `land/y/def5678` with no card open under the landing row, and lists `land/y/abc1234` after the groups with `crew tell <its owner> "Close your Pending You card land/y/abc1234: its row is gone."`

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

### Requirement: A landing's card is a high-stakes approval
A bolt's landing card, keyed `land/<bolt>/<head>`, SHALL be an approval (`approve`) marked high stakes, with no options and no steps, whose yes has the conductor tell main-level ops to land the bolt.

#### Scenario: A landing card
- **WHEN** the conductor posts the landing card for bolt `y` at head `abc1234`
- **THEN** the card is an approval marked high stakes, offers no Done button, no step and no command to land, and is approved only by holding the button in the Pending You app

#### Scenario: A landing card with a step
- **WHEN** the conductor posts the landing card for `y` with a step for the user
- **THEN** crew refuses it, saying the card has steps for the user to take

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
crew SHALL check only sessions it started: any card in a session crew did not start, and a tool of another server, SHALL pass unchecked. In a session crew started, every card is checked: a row's card for its form, and every key against the rows the agent owns, as the requirement on keys below says.

#### Scenario: The user's own session
- **WHEN** the user, in a session crew did not start, posts any card under any key
- **THEN** crew checks nothing and lets it through

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

### Requirement: crew refuses a crew agent's area under any key but the kit's
Before an area is created from a session crew started, crew SHALL refuse it unless its key is `create-area:<owner>/<kit>` for a kit the agent's team builds, or, for an agent of the main level, a kit of its partition's teams. The refusal SHALL name that key.

#### Scenario: An area under the agent's own key
- **WHEN** brd-2-conductor creates switchboard-kit's area with the key `area:brd-2-conductor`
- **THEN** the call is refused before it reaches Pending You, naming `create-area:WilldanGroup/switchboard-kit`

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
A call Pending You refuses SHALL be refused in Pending You's own words and recorded as the act refused. When the host is not signed in to Pending You, or Pending You cannot be reached or does not answer within 60 seconds, the command SHALL refuse saying so and to try again later, and SHALL post nothing. A reply that lacks the card's or the area's id SHALL be refused as unread, never taken as empty.

#### Scenario: Pending You refuses the card
- **WHEN** Pending You refuses a posted card with "Approve requests give their risk in approve.risk."
- **THEN** the command refuses with those words, and the run record has a `card.post` entry with that refusal and no card

#### Scenario: The host is not signed in
- **WHEN** the host has no Pending You sign-in and an agent runs `crew card post`
- **THEN** the command refuses, saying this computer is not signed in to Pending You, and nothing is posted

### Requirement: The landing card is posted once the bolt's verification is green
The conductor SHALL post a bolt's landing card once every unit and chore of the bolt has merged and its verification is green, and the card SHALL ask only for the landing. A step only the user can take or check SHALL be an after-deploy step on a deploy's card, never a question on the landing card. A note on the landing card that names a defect SHALL be a fix on the bolt, and the landing SHALL be asked again only once the verification is green again.

#### Scenario: A green bolt
- **WHEN** every unit of bolt `y` has merged and its verification is green at head `abc1234`
- **THEN** the conductor posts one high-stakes card keyed `land/y/abc1234` that asks only for the landing

#### Scenario: A defect noted on the card
- **WHEN** the user answers the landing card for `y` with a note naming a defect
- **THEN** the conductor does not ask main-level ops to land `y`, closes the card with that outcome, and runs a fix on the bolt

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
