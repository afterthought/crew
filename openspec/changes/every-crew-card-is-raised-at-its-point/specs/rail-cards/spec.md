## ADDED Requirements

### Requirement: crew raises a row's card at its event
crew SHALL build and post each rail row's card itself, from the facts of the event that makes the row, by the command that makes or reads the event, through the fleet's `pendingyou mcp --app claude-code` under the host's sign-in, in the name of the role whose row it is, with the row's key as the card's idempotency key, so the same event read twice makes one card. No crew agent SHALL write, post or close a row's card. The command SHALL print the card's id and the line that adopts it, `pendingyou hold <id>`, and, when the event runs outside the owner's session, SHALL tell the owner that line with `crew tell`.

#### Scenario: A proposal accepted into the plan
- **WHEN** the planner runs `crew plan propose <file>` and the proposal is accepted as number 4
- **THEN** one card keyed `proposal/4` is open, asked in the planner's name, built by crew from the plan and the proposal, and the command prints its id and `pendingyou hold <id>`

#### Scenario: A bolt reads proven at the merge's end
- **WHEN** the merge of bolt `y`'s last unit is recorded, every unit's latest change has been in a batch and sluice's verdict at `y`'s head is green
- **THEN** one card keyed `land/y` is open in `y`'s conductor's name, and a rail read moments later posts nothing more

#### Scenario: A deploy offered by the deployer
- **WHEN** the deployer runs `crew ops offer srv --to abc1234`
- **THEN** one card keyed `deploy/srv` is open in main-level ops's name, and main-level ops is told `pendingyou hold <id>` by `crew tell`

#### Scenario: Pending You refuses the card
- **WHEN** `crew plan propose` accepts proposal 5 and Pending You refuses its card
- **THEN** the proposal is in the plan, the run record has a `card.post` entry on it marked refused in Pending You's words, the command says so, and the rail shows the row with no card and the refusal

#### Scenario: The host is not signed in
- **WHEN** the host has no Pending You sign-in and `crew review` finds a batch due
- **THEN** the batch is cut and recorded, no card posts, and the command and the rail say the host is not signed in

### Requirement: A row's card is changed in place when its thing changes
When what a row's card asks changes while it is open, a proposal rewritten with `--replaces`, a conductor's agreement, a bolt's or a deploy's head moved, a record revised, crew SHALL change the one card in place with a change note the user sees, and SHALL post no second card under a new key. A proposal chain's card SHALL be the first proposal's, and the rail's row for the replacing proposal SHALL carry it.

#### Scenario: A proposal rewritten after a note
- **WHEN** the planner runs `crew plan propose <file> --replaces 4` and proposal 5 is accepted
- **THEN** the card keyed `proposal/4` is changed to proposal 5's title, summary, case, change and questions, with the change note "Rewritten as proposal 5 after your note", and the rail's row for proposal 5 names it as its card

#### Scenario: A fix moves a bolt with an open landing card
- **WHEN** the landing card `land/y` is open and a fix merges into `y`, moving its head to `def5678` with sluice green
- **THEN** the same card is changed, its summary naming `def5678` and the fix, with the change note "Head is now def5678 after the fix …"

#### Scenario: A newer head offered
- **WHEN** `deploy/srv`'s card is open for `abc1234` and the deployer offers `def5678`
- **THEN** the same card is changed to `def5678`, with the change note "Now offering def5678, which includes abc1234"

### Requirement: A card is closed by crew at the event that ends it
crew SHALL close each of its cards at the event that ends what it asks, with a one-line outcome: a proposal applied (what was added, dropped and left out) or dropped (the user's reason); a batch tapped or its reading session sent; a bolt landed (the merge and the hosts brought level), held for a fix on a note naming a defect, or declined; a deploy ended (each step's outcome) or failed (the step and its log) or declined; a step done, skipped, or done by its agent; a record accepted or rejected (the commit). A declined approval SHALL be closed with the user's words when its owner reads it with `crew card read`. A row's card whose row is gone SHALL be withdrawn by crew on the next rail read, with the reason.

#### Scenario: A proposal approved from the phone
- **WHEN** the user approves `proposal/4` on the phone, leaving one unit out, and the planner runs `crew plan answer` and `crew plan approve 4 --clear <unit>`
- **THEN** the card is closed with "Applied: 2 units added, 1 left out", and the rail's proposal row is gone

#### Scenario: A deploy fails
- **WHEN** the deployer records `crew ops record srv --act end` with a failed `guests` step
- **THEN** `deploy/srv`'s card is closed with "Failed at guests: <its log>; the next run offers it again"

#### Scenario: A landing declined
- **WHEN** the user declines `land/y` with "not before the demo" and the conductor runs `crew card read land/y`
- **THEN** the command prints the decline and its words, and the card is closed with them

#### Scenario: A row gone under an open card
- **WHEN** `proposal/4`'s card is open and the proposal is dropped from the planner's pane without its card closing
- **THEN** the next rail read withdraws the card, "its proposal was dropped", and says so

### Requirement: A card lost to the host's sign-in is posted again by crew
When the host signs in to Pending You anew and an open row's card reads not found, the next rail read SHALL post the row's card again under its key, its summary saying an older copy of the card is dead and this one is the one to answer, and the rail SHALL take the newer card as the row's.

#### Scenario: Signed in again with a proposal open
- **WHEN** the host runs `pendingyou-signin` while `proposal/4`'s card is open, and the rail is read
- **THEN** a new card is posted under `proposal/4` whose summary names the older copy dead, the rail shows the new card's id as the row's, and the old card is listed as lost

### Requirement: A question is asked by four roles in their own name
A conductor, the planner, main-level ops and the design agent MAY post a card for a question of their own through Pending You's own tools in their session, under an idempotency key of their own that is no row's, shaped as they see fit. A stage agent, a team's ops, a dispatcher and the operator agent SHALL post none: a stage agent asks its conductor with `crew needs`, the dispatcher asks through the planner. crew SHALL refuse a post, change or close from any other role, naming the chain of command, and SHALL refuse a crew agent's own post, change or close under a row's key or of a row's card, naming the card as crew's; it SHALL refuse nothing else of a question's form.

#### Scenario: A conductor asks
- **WHEN** swb-1-conductor calls `post_request` with the key `ask/swb-1-conductor/hold-the-macs` and three options
- **THEN** the call goes through, and the run record has a `card.post` entry on the conductor with that key and the card's id

#### Scenario: A coder asks
- **WHEN** a coder in a crew session calls `post_request`
- **THEN** the call is refused before it reaches Pending You, saying a stage agent asks its conductor with `crew needs`

#### Scenario: A conductor posts its landing card by hand
- **WHEN** swb-1-conductor calls `post_request` with the key `land/y`
- **THEN** the call is refused, saying the landing card is crew's and is raised when the bolt reads proven

### Requirement: A question whose asker is gone is withdrawn
On each rail read crew SHALL withdraw, under the host's connection, every open question card whose asker herdr no longer lists as an agent, with the reason naming the asker, and SHALL say so.

#### Scenario: A conductor's question outlives it
- **WHEN** crw-3-conductor's question card is open and crw-3's team is closed
- **THEN** the next rail read withdraws it with "crw-3-conductor ended; ask again if it still matters"

### Requirement: A batch's card is one notice
A batch's card SHALL be one card for the whole batch, never split, that says first what it is, the partition's changes written or rewritten since the last batch, already being built, read for notes and approving nothing; names every unit with its team and its reviewer's opening paragraph as prose; says that notes go in the reading session or in the card's note and reach each unit's team as the user's words; links the batch's one reading session in its words first and among its links; and asks nothing, closing on one tap or on the session's send, whichever is first.

#### Scenario: A batch of four
- **WHEN** crew cuts batch 7 of four changes from three teams
- **THEN** one card keyed `batch/7` names the four units with their teams and a paragraph each, says what it is, where notes go, carries one link to one session, and has no question, option or approval

### Requirement: A deploy's card is a high approval
A deploy's card SHALL be an `approve` of risk high, not reversible, because irreversible, naming the environment and the commit; its words SHALL give the landings since the environment's last deploy by subject, the environments before and after it, and the after-deploy steps gathered with their doers.

#### Scenario: Three landings since srv's last deploy
- **WHEN** the deployer offers srv `c882cff` and srv runs `6aed25c`
- **THEN** the card's approve block has risk high and reversible false, and its words name landings #16, #17 and #18, that the box follows on its own and mac-studio is offered after srv, and the two steps with their doers

### Requirement: A step's card is the user's do
A step whose doer is the user SHALL be a `do` card with the step's words, where it is done, each command whole as an action step, what is seen when it worked, and the options Done, Skip and Later. A step an agent runs on its own SHALL have no card.

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

### Requirement: A record's card is a low approval holding the record
A record's card SHALL be an `approve` of risk low, reversible, titled "Accept record <number> in <kit>: <title>?", its summary the record's opening sentences, its background the record's decision and, when the record quotes the user's words from the design talk, "Your own words, recorded as your decision:" and the quote, and one artifact, the record whole as Markdown. It SHALL link no reading session.

#### Scenario: A record proposed from the signals
- **WHEN** the design agent runs `crew record crew 32 --proposed` for a record not settled in the pane
- **THEN** one card keyed `record/crew/32` is open with that title, the record's opening sentences, its decision and the Markdown, and no link

## MODIFIED Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, the thing's and not its version's: `proposal/<n>` for a proposal chain, `n` its first proposal; `batch/<n>` for review batch n; `land/<bolt>` for a bolt proven; `deploy/<env>` for a `manual` environment's open offer; `op/<env>/<n>` for a step that waits on the user; `record/<kit>/<number>` for a record proposed. crew SHALL post the row's card with that key as its idempotency key. A question's card has no row and a key of its asker's own. There SHALL be no review row and no verify row.

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was proven at `abc1234`, a note named a defect, a fix landed on `y` at `def5678` and its verification is green
- **THEN** its landing row's key is still `land/y`, and its card is the one posted at `abc1234`, changed in place

#### Scenario: A proposal replaced
- **WHEN** proposal 4 is replaced by proposal 5
- **THEN** the rail's row for proposal 5 has the key `proposal/4`, and its card is the chain's

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2` from before this change, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, until its card closes

#### Scenario: A unit built again
- **WHEN** unit `u` was constructed at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** no review row or key exists for either head; the unit's revised change is due for the partition's next batch, whose card's key is the batch's

#### Scenario: A verify report saved
- **WHEN** unit `u`'s verify saves its report `verify-u-20261013-1200.md`
- **THEN** the rail has no row for it, and a card keyed `verify/u/20261013-1200` belongs to no row

### Requirement: A card says whose it is and where it belongs
crew SHALL ask each card in the name of the role whose row it is, with the host as the session's machine and the kit's checkout as its folder; a question's card SHALL be asked in its asker's crew name by the asker's session. A card SHALL be filed in the area of its kit, found by the kit's git remote, in the group named for its partition; crew SHALL create a kit's area that does not exist with the key `create-area:<owner>/<kit>`, and an agent SHALL create one under no other key and never a group. A card's title SHALL be the question, read cold, naming the thing.

#### Scenario: A landing card
- **WHEN** crew raises bolt `y`'s landing card for swb-1's team in switchboard-kit
- **THEN** the card is asked as `swb-1-conductor` on the team's host, sits in switchboard-kit's area in the `wldn` group, and its title asks whether to land bolt `y` on the kit's main

#### Scenario: A review card
- **WHEN** a unit's change is due for a batch
- **THEN** no review card is asked for it; the batch's card, asked in the planner's name, names the unit and its team

#### Scenario: The first card in a kit
- **WHEN** crew raises the first card in switchboard-kit and Pending You matches no area to its remote
- **THEN** crew makes the area under `create-area:WilldanGroup/switchboard-kit`, named `switchboard-kit`, in the partition's group, and files the card there

### Requirement: A card carries what the user would read and the row's answers
A proposal's card SHALL hold the proposal whole, its picture, its text and its case, and SHALL carry a reading session's link only when it holds more than fifteen new units. A batch's card SHALL carry its one session's link. A landing's, a deploy's, a step's and a record's card SHALL carry no link to a session: each holds what the user decides from.

#### Scenario: A proposal's card holds the proposal whole
- **WHEN** crew raises the card for proposal 4, which adds two units
- **THEN** the card carries the picture, the text and the case, and no session link

#### Scenario: A landing card has nothing to read
- **WHEN** crew raises bolt `y`'s landing card
- **THEN** it names the units and chores that land, sluice's verdict and when, and how far main has moved, and carries no link

#### Scenario: A review card's options
- **WHEN** a unit's change is due for a batch
- **THEN** no review card offers its approval; the batch's card asks nothing and its notes go to the unit's team

#### Scenario: A review card's link
- **WHEN** a unit's change is read in batch 3
- **THEN** the batch's card carries the one link to batch 3's session, and no card carries a link to the unit alone

#### Scenario: Answered in the session rather than on the card
- **WHEN** the user annotates a unit's change in the batch's session and sends the annotations
- **THEN** the planner's `crew card wait batch/3` returns them, they go to the unit's conductor as the user's words, and the batch's card is closed

### Requirement: An answer wakes the owner, which acts on the user's word
An answer on a crew card SHALL be acted on by the role whose row it is, woken in its session by the card it adopted, and by no other: the planner applies or rewrites the proposal; the conductor tells main-level ops to land, or starts a fix on a defect note; main-level ops runs the deploy's approval or the step's state; the design agent sets the record's status. crew SHALL then close the card at that act's event.

#### Scenario: Landing approved
- **WHEN** the user approves `land/y` and the conductor's session wakes
- **THEN** the conductor tells main-level ops to land `y` on the user's word, main-level ops lands it, and `crew bolt land` closes the card

#### Scenario: A proposal approved from the phone
- **WHEN** the user approves the card for proposal 4 on the phone
- **THEN** the planner is woken, runs `crew plan answer` and `crew plan approve 4`, which closes the card with what was applied, and the rail's proposal row is gone

#### Scenario: Changes asked for on a review card
- **WHEN** the user writes a note on a batch's card asking for changes to unit `x`
- **THEN** the planner's wait returns the note, the conductor runs construct again with its words, and no approval is asked

### Requirement: An agent never runs Pending You from npm or waits on a hold
An agent crew started SHALL adopt a card crew posted by running the fleet's `pendingyou hold <id>` once, as crew prints it, which the fleet's wake mod answers at once, and SHALL run no `npx pendingyou` command and wait on no hold. After a fresh start it SHALL read `crew rail` for its open cards and adopt each.

#### Scenario: Restarted with an answered card
- **WHEN** a conductor restarts while the user has answered its landing card
- **THEN** at its start `crew rail` names the card and its id, the conductor adopts it and acts on the answer

### Requirement: A crew agent's card acts are in the run record
Each card crew posts, changes, withdraws or closes, and each a crew agent posts, changes or closes through Pending You's tools, SHALL be an entry in the partition's run record naming the row's object or the asker, the card's id in `Card` and the key in `Key`, crew's read from Pending You's own reply, an agent's from the tool's result; a result crew cannot read SHALL be recorded as unread and listed by the rail. An entry SHALL NOT hold a card's title, summary or other text.

#### Scenario: A card crew posted
- **WHEN** `crew plan propose` accepts proposal 4 and Pending You answers with `req_p4`
- **THEN** the run record has a `card.post` entry on proposal 4 with the key `proposal/4` and the card `req_p4`

#### Scenario: A question posted
- **WHEN** swb-1-conductor's `post_request` under `ask/swb-1-conductor/hold-the-macs` returns `req_q1`
- **THEN** the run record has a `card.post` entry on swb-1-conductor with that key and `req_q1`

#### Scenario: A card posted and closed
- **WHEN** crew raises `land/y`'s card `req_l1` and later closes it at the landing
- **THEN** the run record has a `card.post` entry on `bolt/y` with that key and `req_l1`, and a `card.close` entry with the same id

#### Scenario: A card posted through crew
- **WHEN** `crew ops offer srv --to abc1234` runs and Pending You answers with the card `req_d1`
- **THEN** the run record has a `card.post` entry on `env/srv` with the key `deploy/srv` and the card `req_d1`, and nothing written on the card

#### Scenario: The user's own sessions
- **WHEN** a Claude session crew did not start posts a Pending You card
- **THEN** nothing is written to crew's run record

### Requirement: The rail shows each row's card
`crew rail` SHALL print, under each row, the row's card key, whether a card with that key is open, its id and whose it is, and after the groups the open question cards, each with its asker, its title and its age. A card is open from its `card.post` entry until a `card.close` entry for the same card.

#### Scenario: A row with its card and a question open
- **WHEN** `proposal/4`'s card `req_p4` is open and swb-1-conductor's question `req_q1` is open
- **THEN** the proposal row's card line names `proposal/4`, open, `req_p4`, the planner's; and the questions group lists `req_q1` with swb-1-conductor, its title and its age

#### Scenario: A row with its card
- **WHEN** bolt `y` reads proven and crew's card `req_l1` under `land/y` is open
- **THEN** the row's card line names `land/y` as open, `req_l1`, the conductor's

#### Scenario: A row without a card
- **WHEN** a proposal is open and its card's post was refused
- **THEN** the row's card line names `proposal/<n>` with no card open and the refusal's words

### Requirement: The rail names an open card whose row is gone
After its groups, `crew rail` SHALL list each card its sweep withdrew on this read, with its key, its owner and why (its row is gone, its asker ended), and each card it posted again as lost.

#### Scenario: A withdrawn card
- **WHEN** bolt `y` was dropped while `land/y`'s card was open
- **THEN** the rail withdraws the card and lists it, "withdrawn: its bolt was dropped"

#### Scenario: A forgotten card
- **WHEN** proposal 4 was approved from the planner's pane and its card `proposal/4` is still open
- **THEN** the next rail read closes it with the approval's outcome and lists it, "closed: its proposal was applied"

### Requirement: A card's words are the document's own
A crew card's words SHALL be prose the phone wraps, in short paragraphs, cut at whole sentences to Pending You's budget, with nothing depending on Markdown rendering and no code block; where a card speaks for a document, a proposal's case, a unit's opening paragraph, a record's opening sentences, it SHALL use the document's own words, never reworded. The only artifacts a crew card carries SHALL be a proposal's picture, uploaded; a record's Markdown; and a step's commands as action steps. A path SHALL appear only inside a step's command or a deploy's log name.

#### Scenario: A batch card's summary
- **WHEN** crew raises batch 7's card for four units
- **THEN** each unit's paragraph is the reviewer's opening paragraph as prose, no code block or attachment carries it, and the card wraps on the phone

#### Scenario: A record's artifact
- **WHEN** crew raises record 32's card
- **THEN** its one artifact is the record as Markdown, and no file is attached

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

### Requirement: The landing card is posted once the bolt's verification is green
crew SHALL raise a bolt's landing card once every unit and chore of the bolt has merged, every unit's latest change has been in a batch and sluice's verdict at its head is green, keyed `land/<bolt>`, as an `approve` of risk high, not reversible, because irreversible, naming what lands in units and chores, the verdict and when, how far main has moved, and what follows; it SHALL ask only for the landing. A note naming a defect SHALL have the conductor start a fix on the bolt, which withdraws the card, and the card SHALL be raised again once the bolt reads proven again.

#### Scenario: A green bolt
- **WHEN** every unit and chore of bolt `y` has merged, each unit's latest change has been in a batch and sluice is green at `abc1234`
- **THEN** one card keyed `land/y` is open, an approve of risk high, naming the units and chores and the verdict

#### Scenario: A defect noted on the card
- **WHEN** the user answers `land/y` with a note naming a defect and the conductor runs `crew fix` on `y`
- **THEN** the card is withdrawn, "held for a fix: <the note>", and a new card is raised when `y` reads proven again

### Requirement: The check refuses what it cannot read, and only for crew's sessions
crew's hook SHALL run only in a session with `CREW_AGENT` set, and SHALL refuse a Pending You call when it cannot read the agent's role or the call's key, naming what it could not read, never letting a call through on a guess; the user's own sessions SHALL be untouched.

#### Scenario: The agent's role cannot be read
- **WHEN** a crew session's `CREW_AGENT` names no role the teams file knows and the agent calls `post_request`
- **THEN** the call is refused, naming the agent, and nothing is posted

#### Scenario: The plan cannot be read
- **WHEN** the hook cannot read the partition's rows to tell whether a key is a row's
- **THEN** the call is refused, naming what could not be read, and nothing is posted

#### Scenario: The user's own session
- **WHEN** a session with no `CREW_AGENT` calls `post_request`
- **THEN** the hook does nothing, and the call goes through as Pending You ships it

### Requirement: crew's card commands refuse what they cannot do, in the words that say why
A card act Pending You refuses SHALL be refused in Pending You's own words and recorded as the act refused, and SHALL refuse nothing of the event it was raised for. When the host is not signed in to Pending You, or Pending You cannot be reached or does not answer within 60 seconds, the act SHALL be recorded as not posted, the command SHALL say so, and the event SHALL stand. A reply that lacks the card's or the area's id SHALL be recorded as unread, never taken as empty.

#### Scenario: The host is not signed in
- **WHEN** the host has no Pending You sign-in and `crew ops offer` runs
- **THEN** the offer is recorded, no card posts, and the command says this computer is not signed in to Pending You

#### Scenario: Pending You refuses the card
- **WHEN** Pending You refuses a card crew posts with "Approve requests give their risk in approve.risk."
- **THEN** the command says so in those words, the run record has a `card.post` entry with that refusal and no card, and the event it was raised for stands

## REMOVED Requirements

### Requirement: The owner of a row posts its card
**Reason**: crew raises a row's card itself at its event; no agent posts one (record 0031).

### Requirement: A review's card is an approval with a note
**Reason**: there is no review row (record 0014); the requirement outlived it.

### Requirement: A proposal's card is an approval
**Reason**: restated in "A card carries what the user would read and the row's answers" and `plan-proposals`; the proposal's form is record 0018's, built by crew.

### Requirement: A landing's card is a high-stakes approval
**Reason**: restated in "The landing card is posted once the bolt's verification is green", with its `approve` of risk high.

### Requirement: No row's card takes another kind
**Reason**: crew builds every row's card; there is no other kind to refuse.

### Requirement: crew refuses a row's card in another form
**Reason**: no agent builds a row's card; crew refuses an agent's call under a row's key instead.

### Requirement: crew refuses a change that takes a row's card out of its form
**Reason**: the same.

### Requirement: crew checks only a row's card in a crew session
**Reason**: the hook's scope is now "The check refuses what it cannot read, and only for crew's sessions" and "A question is asked by four roles in their own name".

### Requirement: crew refuses a crew agent's card under any key but a row's of its own
**Reason**: a question under the asker's own key is allowed; a row's key is refused to agents (record 0031, the user: "My goal isn't to prevent agents from also using pendingyou").

### Requirement: crew refuses a crew agent's area under any key but the kit's
**Reason**: kept inside "A card says whose it is and where it belongs".

### Requirement: A crew agent's card is posted through crew
**Reason**: `crew card post` goes; crew posts its own cards at their events.

### Requirement: A crew agent's card is changed, closed and read through crew
**Reason**: `crew card change|close` go; `crew card read` is restated under "A card is closed by crew at the event that ends it" and "An agent never runs Pending You from npm or waits on a hold".

### Requirement: crew names the card a change ends
**Reason**: crew closes the card itself at the event; there is nothing to name to an owner.

### Requirement: A row's card is closed when the row's key changes
**Reason**: a key is the thing's, not its version's; the card is changed in place.

### Requirement: A card's link and bolt come first
**Reason**: folded into "A card carries what the user would read and the row's answers" and "A card's words are the document's own": a batch's link comes first in its words; other cards carry none.

### Requirement: No card carries a path
**Reason**: narrowed inside "A card's words are the document's own": a step's command and a deploy's log name carry one (the user, 2026-10-14: "I don't think we need to be using absolutes everywhere like this").
