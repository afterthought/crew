# rail-cards Specification

## Purpose
Each decision on the rail reaches the user as one Pending You card from the agent that owns it, answered on the Mac or the phone, kept true by crew's own events, and shown on the rail so a stale card is seen at once.

## Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, derived from the row's state: `proposal/<n>` for an open proposal, `review/<unit>/<head>` for a unit in review (the first seven characters of its branch's head), `verify/<unit>/<YYYYMMDD-HHMM>` for a verify report (the stamp in the report's file name), and `land/<bolt>/<head>` for a bolt ready to land (the first seven characters of the bolt's branch head). A row's owner SHALL post its card with that key as the card's idempotency key.

#### Scenario: A unit built again
- **WHEN** unit `u` was in review at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** its review row's key is `review/u/def5678`, and a card keyed `review/u/abc1234` belongs to no row

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was ready to land at head `abc1234`, its landing failed, and a fix moved its head to `def5678` and ops proved it again
- **THEN** its landing row's key is `land/y/def5678`, its conductor posts a new landing card under that key, and a card keyed `land/y/abc1234` belongs to no row

### Requirement: The owner of a row posts its card
When an agent crew started has Pending You's tools, it SHALL post one card for each row it owns: the planner for each proposal it opens, a conductor for each of its team's units in review, for each verify report its team's units wait on the user for, and for its bolt once the bolt is proven, or proven but for steps only the user can take. It SHALL post no second card for a row that has one open. A team's cards SHALL be its conductor's: its ops and every stage agent SHALL post no card, and no crew agent SHALL post a card that is not a row's.

#### Scenario: A proposal opened
- **WHEN** the planner opens proposal 4 in a session with Pending You's tools
- **THEN** one card keyed `proposal/4` is open, asked by the planner

#### Scenario: No Pending You
- **WHEN** a conductor's session has no Pending You tools and a unit reaches review
- **THEN** no card is posted, the unit's rail row is as before, and the conductor tells the operator agents it waits on the user

#### Scenario: A proof leaves the user a check
- **WHEN** brd-2's ops finishes its proof with every item green but one check only the user can make on their Mac
- **THEN** ops writes that check in its proof file and posts no card, and the user gets one card for it, the conductor's landing card for the bolt

### Requirement: A card says whose it is and where it belongs
A card SHALL be asked in the agent's crew name, with its host as the session's machine and its worktree as the session's folder. It SHALL be filed in the area of its kit, found by the kit's git remote, in the group named for its partition. An agent that finds no area for its kit SHALL create it with the key `create-area:<owner>/<kit>`, the kit's repository, and with no other key. Its title SHALL name what it asks and its bolt. An agent SHALL never create a group.

#### Scenario: A review card
- **WHEN** swb-1-conductor posts the card for unit `x` of bolt `y` in switchboard-kit
- **THEN** the card is asked by `swb-1-conductor` on its host, sits in switchboard-kit's area in the `wldn` group, and its title names unit `x` and bolt `y`

#### Scenario: The first card in a kit
- **WHEN** no area matches the kit `WilldanGroup/switchboard-kit`
- **THEN** the agent creates it once, with the key `create-area:WilldanGroup/switchboard-kit`, so two agents posting at the same time make one area

### Requirement: A card carries what the user would read and the row's answers
A proposal's card, a review card and a verify card SHALL each carry the link to the plannotator session its owner started for the card's key: on the proposal's page as `crew plan proposed <n>` prints it, on the unit's change folder, or on the verify report. The card SHALL carry the link in place of the page, the folder's path or the report, and SHALL NOT be posted without it when the owner's session has plannotator. A landing card carries no link. Each card's options SHALL be the row's answers: approve or ask for changes for a proposal or a review, what to fix or merge for a verify report, and approve for a landing. A decision the user makes in the card's session SHALL be acted on by the owner as the card's answer, and the owner SHALL then close the card.

#### Scenario: A review card's options
- **WHEN** the user opens a review card
- **THEN** it offers approval, and a note in the user's own words asks for changes

#### Scenario: A review card's link
- **WHEN** swb-1-conductor posts the card for unit `x` in review at `abc1234`
- **THEN** the card carries the link `crew card session review/x/abc1234` printed, and no folder path

#### Scenario: Answered in the session rather than on the card
- **WHEN** the user annotates the change in the review card's session and sends the annotations
- **THEN** the conductor runs construct again with them, as for a note on the card, and withdraws the card saying it was answered in its session

### Requirement: Landing is approved only by holding the button
The card for a bolt ready to land SHALL be marked high stakes, so it is approved by holding the button in the Pending You app and never with a key in Herdr's popup.

#### Scenario: Landing from the popup
- **WHEN** the user presses the approve key on a landing card in Herdr's popup
- **THEN** Pending You refuses it as high stakes, and the bolt does not land

### Requirement: An answer wakes the owner, which acts on the user's word
An answer on a card SHALL be acted on by the agent that posted it, when it is woken in its session, and by no other: the planner approves, replaces or drops the proposal; the conductor approves the unit or runs construct again with the user's words, fixes or merges after a verify report, or asks main-level ops to land the bolt. The agent SHALL then close the card with a one-line outcome.

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
Each card a crew agent posts, updates, withdraws or closes in Pending You SHALL be an entry in its partition's run record, naming the row's object, the card's id in `Card`, and the key in `Key` when it is one of the four row keys. An entry SHALL NOT hold a card's title, summary or any other text written on it.

#### Scenario: A card posted and closed
- **WHEN** swb-1-conductor posts the card `review/x/abc1234` and later closes it
- **THEN** the run record has a `card.post` entry on `unit/x` with that key and the card's id, and a `card.close` entry with the same id

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
A conductor with Pending You's tools SHALL NOT tell the operator agents when it waits on the user for a review, a verify report or a landing, since that row's card reaches the user. It SHALL tell them when it waits on a question asked only in its pane, and for every wait when it has no Pending You tools.

#### Scenario: A unit reaches review
- **WHEN** a conductor with Pending You's tools has posted the card for a unit in review
- **THEN** it sends no tell to the operator agents for it

#### Scenario: A question in the pane
- **WHEN** a stage stops on a question for the user that only the conductor's pane holds
- **THEN** the conductor tells the operator agents in one line what it waits for and where

### Requirement: A card's words are the document's own
A card a crew agent posts for a rail row SHALL say what the user decides from in the words of the document it asks the user to read, cut by whole sentences and never reworded: a review card the change's Why and the lead sentence of each What Changes item; a proposal card the proposal's case and each change in a line, as `crew plan proposed <n>` words them; a verify card each finding in a line, with what the conductor would do about it.

#### Scenario: A review card
- **WHEN** swb-1-conductor posts the review card for unit `x` of bolt `y`
- **THEN** the card's background holds `x`'s Why and one line per What Changes item, in the proposal's words

#### Scenario: A verify card
- **WHEN** a conductor posts the card for a verify report that raised two warnings
- **THEN** the card's background holds one line for each warning, saying what it found and what the conductor would do about it

#### Scenario: A change too long for the summary
- **WHEN** a unit's Why runs past what the summary holds after the link and the bolt
- **THEN** the summary ends at the last whole sentence that fits, and the background holds the whole Why

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

### Requirement: ops writes a proof's steps for the user in its proof file
When a bolt's proof leaves steps only the user can take or check, ops SHALL write each in its proof file as a step the user can do from a card: where, what to do or paste, and what they will see when it worked. ops SHALL post no card for them.

#### Scenario: One check left for the user
- **WHEN** ops's proof of bolt `y` is clean but for a gateway check on the user's Mac
- **THEN** the proof file holds that check as a step for the user, marked as waiting on the user, and ops posts no card

### Requirement: The landing card asks the proof's steps before approval
The conductor SHALL post the bolt's landing card once the proof is clean, or clean but for the user's steps, with those steps on it ahead of the approval. Approving it SHALL mean the user took them, they worked, and the bolt may land. A step the user says failed SHALL be a defect fixed on the bolt before the landing is asked again.

#### Scenario: Landing with one check left
- **WHEN** ops's proof of bolt `y` is clean but for a gateway check on the user's Mac
- **THEN** the conductor posts one high-stakes card keyed `land/y/<head>` whose first words and steps are that check, and an approval on it tells main-level ops to land `y`

#### Scenario: The check fails
- **WHEN** the user answers the landing card for `y` with a note that the gateway check is red
- **THEN** the conductor does not ask main-level ops to land `y`, closes the card with that outcome, and runs a fix on the bolt

#### Scenario: A clean proof
- **WHEN** ops's proof of bolt `y` leaves nothing for the user
- **THEN** the landing card for `y` asks only for approval, as before

### Requirement: crew refuses a crew agent's card under any key but a row's of its own
Before a Pending You card is posted from a session crew started, crew SHALL refuse it unless its idempotency key is the card key of a rail row the agent owns: for the planner, `proposal/<n>` for an open proposal of its partition; for a conductor, `review/<unit>/<head>` or `verify/<unit>/<stamp>` for a unit of the bolt its team holds, or `land/<bolt>/<head>` for that bolt. Every other crew agent SHALL own no key. A refused card SHALL NOT reach Pending You, and its refusal SHALL name the keys to use.

#### Scenario: ops posts a card
- **WHEN** brd-2-ops calls Pending You's `post_request` under any key
- **THEN** the call is refused before it reaches Pending You, and the refusal says ops owns no key: a team's cards are its conductor's, and what is left for the user goes in the proof file

#### Scenario: A conductor posts under a key of its own making
- **WHEN** brd-2-conductor, whose team holds bolt `y`, posts a card keyed `gateway-check-y`
- **THEN** the call is refused, and the refusal names `land/y/<head>` and the review and verify keys of `y`'s units, read from `crew rail`

#### Scenario: A conductor posts another team's row
- **WHEN** brd-2-conductor posts a card keyed `review/z/abc1234` for a unit `z` of a bolt another team holds
- **THEN** the call is refused, naming the keys that are brd-2-conductor's

#### Scenario: The planner posts a proposal's card
- **WHEN** wldn-planner posts a card keyed `proposal/4` while proposal 4 of `wldn` is open
- **THEN** the call goes through, and the card is recorded as before

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
