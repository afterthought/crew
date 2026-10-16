## ADDED Requirements

### Requirement: crew raises a row's card at its event
crew SHALL build and post each rail row's card itself, from the facts of the event that makes the row, by the command that makes or reads the event, through the fleet's `pendingyou mcp --app claude-code` under the host's sign-in, in the name of the role whose row it is, with the row's key as the card's idempotency key. No crew agent SHALL write, post or close a row's card.

#### Scenario: A proposal accepted into the plan
- **WHEN** the planner runs `crew plan propose <file>` and the proposal is accepted as number 4
- **THEN** one card keyed `proposal/4` is open, asked in the planner's name, built by crew from the plan and the proposal, and the command prints its id and `call get_request (requestId <id>, name <role>)`

#### Scenario: A bolt reads proven at the merge's end
- **WHEN** the merge of bolt `y`'s last unit is recorded, every unit's latest change has been in a batch and sluice's verdict at `y`'s head is green
- **THEN** one card keyed `land/y` is open in `y`'s conductor's name, and a rail read moments later posts nothing more

#### Scenario: A batch's summary delivered
- **WHEN** the reviewer delivers batch 7's summary and the planner's `crew review --wait` returns
- **THEN** crew starts the batch's reading session and one card keyed `batch/7` is open in the planner's name

#### Scenario: Pending You refuses the card
- **WHEN** `crew plan propose` accepts proposal 5 and Pending You refuses its card
- **THEN** the proposal is in the plan, the run record has a `card.post` entry on it marked refused in Pending You's words, the command says so, and the rail shows the row with no card and the refusal

#### Scenario: The host is not signed in
- **WHEN** the host has no Pending You sign-in and a batch's summary is delivered
- **THEN** the batch is recorded, no card posts, and the command and the rail say the host is not signed in

### Requirement: A raised card is adopted by its owner
The command that raises a card SHALL print the card's id and the line that adopts it, `call get_request (requestId <id>, name <role>)`, and when the card is raised outside its owner's turn, a landing found on a rail read or the deployer's offer, SHALL tell the owner that line with `crew tell`.

#### Scenario: A deploy offered by the deployer
- **WHEN** the deployer runs `crew ops offer srv --to abc1234`
- **THEN** one card keyed `deploy/srv` is open in main-level ops's name, and main-level ops is told `call get_request (requestId <id>, name <role>)` by `crew tell`

#### Scenario: A proposal's card in the planner's own shell
- **WHEN** the planner's `crew plan propose` raises proposal 4's card
- **THEN** the command prints the card's id and `call get_request (requestId <id>, name <role>)`, and no tell is sent

### Requirement: A row's card is changed in place when its thing changes
When what a row's card asks changes while it is open, crew SHALL change the one card in place with a change note the user sees, and SHALL post no second card under a new key. A proposal chain's card SHALL be the first proposal's, and the rail's row for the replacing proposal SHALL carry it.

#### Scenario: A proposal rewritten after a note
- **WHEN** the planner runs `crew plan propose <file> --replaces 4` and proposal 5 is accepted
- **THEN** the card keyed `proposal/4` is changed to proposal 5's title, summary, case, change and questions, with the change note "Rewritten as proposal 5 after your note", and the rail's row for proposal 5 names it as its card

#### Scenario: A fix moves a bolt with an open landing card
- **WHEN** the landing card `land/y` is open and a fix merges into `y`, moving its head to `def5678` with sluice green
- **THEN** the same card is changed, its summary naming `def5678` and the fix, with the change note "Head is now def5678 after the fix …"

#### Scenario: A newer head offered
- **WHEN** `deploy/srv`'s card is open for `abc1234` and the deployer offers `def5678`
- **THEN** the same card is changed to `def5678`, with the change note "Now offering def5678, which includes abc1234"

#### Scenario: A conductor agrees
- **WHEN** `proposal/4`'s card says it waits on crw-2's conductor and that conductor runs `crew plan agree 4`
- **THEN** the card is changed to say it no longer waits on crw-2

### Requirement: A card is closed by crew at the event that ends it
crew SHALL close each of its cards at the event that ends what it asks, with a one-line outcome, and SHALL withdraw a row's card whose row is gone on the next rail read, with the reason. A declined approval SHALL be closed with the user's words when its owner reads it with `crew card read`.

#### Scenario: A proposal approved from the phone
- **WHEN** the user approves `proposal/4` on the phone, leaving one unit out, and the planner runs `crew plan answer` and `crew plan approve 4 --clear <unit>`
- **THEN** the card is closed with "Applied: 2 units added, 1 left out", and the rail's proposal row is gone

#### Scenario: A proposal dropped
- **WHEN** the planner runs `crew plan drop 4 "the user: not this quarter"`
- **THEN** the card is withdrawn with those words

#### Scenario: A bolt landed
- **WHEN** main-level ops runs `crew bolt land y` after the landing's submission
- **THEN** `land/y`'s card is closed with the landing's outcome, in the words `crew-raises-a-bolts-landing-card` gives it

#### Scenario: A deploy fails
- **WHEN** the deployer records `crew ops record srv --act end` with a failed `guests` step
- **THEN** `deploy/srv`'s card is closed with "Failed at guests: <its log>; the next run offers it again"

#### Scenario: A step done
- **WHEN** the user answers `op/srv/1` Done and main-level ops runs `crew ops step srv --key <key> --state done`
- **THEN** the card is closed "Done by you"

#### Scenario: A landing declined
- **WHEN** the user declines `land/y` with "not before the demo" and the conductor runs `crew card read land/y`
- **THEN** the command prints the decline and its words, and the card is closed with them

#### Scenario: A row gone under an open card
- **WHEN** `proposal/4`'s card is open and the proposal is dropped without its card closing
- **THEN** the next rail read withdraws the card, "its proposal was dropped", and says so

### Requirement: A question is asked by four roles in their own name
A conductor, the planner, main-level ops and the design agent MAY post a card for a question of their own through Pending You's own tools in their session, under an idempotency key of their own that is no row's, shaped as they see fit. A stage agent, a team's ops, a dispatcher and the operator agent SHALL post none: a stage agent asks its conductor with `crew needs`, the dispatcher asks through the planner.

#### Scenario: A conductor asks
- **WHEN** swb-1-conductor calls `post_request` with the key `ask/swb-1-conductor/hold-the-macs` and three options
- **THEN** the call goes through, and the run record has a `card.post` entry on the conductor with that key and the card's id

#### Scenario: A question with a words answer
- **WHEN** the design agent's question card asks for the user's words in a `text` question
- **THEN** the call goes through: a question's form is its asker's

### Requirement: crew refuses a question card from any other role or under a row's key
crew SHALL refuse a post, change or close from any role but the four, naming the chain of command, and a crew agent's own post, change or close under a row's key or of a row's card, naming the card as crew's; it SHALL refuse nothing else of a question's form.

#### Scenario: A coder asks
- **WHEN** a coder in a crew session calls `post_request`
- **THEN** the call is refused before it reaches Pending You, saying a stage agent asks its conductor with `crew needs`

#### Scenario: A conductor posts its landing card by hand
- **WHEN** swb-1-conductor calls `post_request` with the key `land/y`
- **THEN** the call is refused, saying the landing card is crew's and is raised when the bolt reads proven

### Requirement: A crew agent's Pending You call names only the agent itself
In a crew session, crew SHALL refuse a call to any Pending You tool that names anyone but the agent's `CREW_AGENT` as its caller, before the call runs, in words naming the agent's own name and saying the call would reroute another agent's answers to this session; a call that names no caller SHALL pass, and an area's name SHALL be taken as no caller's.

#### Scenario: Another agent's card read in its name
- **WHEN** swb-1-conductor's session calls `get_request` with the name `swancloud-ops`
- **THEN** the call is refused before it reaches Pending You, naming swb-1-conductor as the session's own name and saying swancloud-ops's answers would wake this session instead

#### Scenario: A whoami under another agent's name
- **WHEN** the planner's session calls `whoami` with `previousName` `swb-1-conductor`
- **THEN** the call is refused, naming the planner's own name, and swb-1-conductor's cards stay with its session

#### Scenario: A call that names no caller
- **WHEN** a conductor's session calls `list_areas`, or `create_area` with the area's name `switchboard-kit`
- **THEN** the name check lets it through: it names no caller

## MODIFIED Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, the thing's and not its version's: `proposal/<n>` for a proposal chain, `n` its first proposal; `batch/<n>` for review batch n; `land/<bolt>` for a bolt proven; `deploy/<env>` for a `manual` environment's open offer; `op/<env>/<n>` for a step that waits on the user; `record/<kit>/<number>` for a record proposed. crew SHALL post the row's card with that key as its idempotency key. A question's card has no row and a key of its asker's own. There SHALL be no review row and no verify row. A batch whose cards were posted under `batch/<n>-<k>` before this change SHALL keep a row for each until its card closes.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2` from before this change, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, until its card closes

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was proven at `abc1234`, a note named a defect, a fix landed on `y` at `def5678` and its verification is green
- **THEN** its landing row's key is still `land/y`, and its card is the one posted at `abc1234`, changed in place

#### Scenario: A unit built again
- **WHEN** unit `u` was constructed at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** no review row or key exists for either head; the unit's revised change is due for the partition's next batch, whose card's key is the batch's

#### Scenario: A verify report saved
- **WHEN** unit `u`'s verify saves its report `verify-u-20261013-1200.md`
- **THEN** the rail has no row for it, and a card keyed `verify/u/20261013-1200` belongs to no row

#### Scenario: A proposal replaced
- **WHEN** proposal 4 is replaced by proposal 5
- **THEN** the rail's row for proposal 5 has the key `proposal/4`, and its card is the chain's

### Requirement: An answer wakes the owner, which acts on the user's word
An answer on a crew card SHALL be acted on by the role whose row it is, woken in its session by the card it adopted, and by no other: the planner applies or rewrites the proposal; the conductor tells main-level ops to land, or starts a fix on a defect note; main-level ops runs the deploy's approval or the step's state; the design agent sets the record's status. crew SHALL then close the card at that act's event.

#### Scenario: A proposal approved from the phone
- **WHEN** the user approves the card for proposal 4 on the phone
- **THEN** the planner is woken, runs `crew plan answer` and `crew plan approve 4`, which closes the card with what was applied, and the rail's proposal row is gone

#### Scenario: Changes asked for on a review card
- **WHEN** the user writes a note on a batch's card asking for changes to unit `x`
- **THEN** the planner's wait returns the note, the conductor runs construct again with its words, and no approval is asked

#### Scenario: Landing approved
- **WHEN** the user approves `land/y` and the conductor's session wakes
- **THEN** the conductor tells main-level ops to land `y` on the user's word, main-level ops lands it, and `crew bolt land` closes the card

### Requirement: An agent never runs Pending You from npm or waits on a hold
An agent crew started SHALL adopt a card crew posted by calling Pending You's `get_request` with the card's id under its own name, as the line crew prints or tells it says, from which the fleet's wake mod adopts the card and wakes the agent's session once the card is answered and the session is idle; it SHALL run no `pendingyou` command, `hold` and `watch` among them, none through `npx`, and wait on no hold. After a fresh start it SHALL read `crew rail` for its open cards and adopt each the same way.

#### Scenario: Restarted with an answered card
- **WHEN** a conductor restarts while the user has answered its landing card
- **THEN** at its start `crew rail` names the card and its id, the conductor adopts it and acts on the answer

### Requirement: A crew agent's card acts are in the run record
Each card crew posts, changes, withdraws or closes, and each a crew agent posts, changes or closes through Pending You's tools, SHALL be an entry in the partition's run record naming the row's object or the asker, the card's id in `Card` and the key in `Key`, crew's read from Pending You's own reply, an agent's from the tool's result; a result crew cannot read SHALL be recorded as unread and listed by the rail. An entry SHALL NOT hold a card's title, summary or other text.

#### Scenario: A card posted and closed
- **WHEN** crew raises `land/y`'s card `req_l1` and later closes it at the landing
- **THEN** the run record has a `card.post` entry on `bolt/y` with that key and `req_l1`, and a `card.close` entry with the same id

#### Scenario: A card posted through crew
- **WHEN** `crew ops offer srv --to abc1234` runs and Pending You answers with the card `req_d1`
- **THEN** the run record has a `card.post` entry on `env/srv` with the key `deploy/srv` and the card `req_d1`, and nothing written on the card

#### Scenario: The user's own sessions
- **WHEN** a Claude session crew did not start posts a Pending You card
- **THEN** nothing is written to crew's run record

#### Scenario: A question posted
- **WHEN** swb-1-conductor's `post_request` under `ask/swb-1-conductor/hold-the-macs` returns `req_q1`
- **THEN** the run record has a `card.post` entry on swb-1-conductor with that key and `req_q1`

### Requirement: The check refuses what it cannot read, and only for crew's sessions
crew's hook SHALL run only in a session with `CREW_AGENT` set, and SHALL refuse a Pending You call when it cannot read the agent's role, the call's key or the partition's rows, naming what it could not read, never letting a call through on a guess; the user's own sessions SHALL be untouched.

#### Scenario: The plan cannot be read
- **WHEN** the hook cannot read the partition's rows to tell whether a key is a row's
- **THEN** the call is refused, naming what could not be read, and nothing is posted

#### Scenario: The user's own session
- **WHEN** a session with no `CREW_AGENT` calls `post_request`
- **THEN** the hook does nothing, and the call goes through as Pending You ships it

#### Scenario: The agent's role cannot be read
- **WHEN** a crew session's `CREW_AGENT` names no role the teams file knows and the agent calls `post_request`
- **THEN** the call is refused, naming the agent, and nothing is posted

### Requirement: The design agent posts a record's card under its record key
A record's card SHALL be raised by crew through `crew record <kit> <number> --proposed`, keyed `record/<kit>/<number>`, where `<kit>` is the name of a kit one of the partition's teams builds and `<number>` the record's four digits, in the design agent's name; the design agent SHALL post none itself, and no agent SHALL post under a record key. A kit that is not the partition's SHALL be refused naming the partition's kits.

#### Scenario: The design agent posts a record's card
- **WHEN** wldn-design runs `crew record atlas-kit 21 --proposed`, and atlas-kit is built by one of wldn's teams
- **THEN** one card keyed `record/atlas-kit/0021` is open in wldn-design's name, and the run record has a `card.post` entry on `record/atlas-kit/0021` with that key

#### Scenario: A kit outside the partition
- **WHEN** wldn-design runs `crew record flywheel-next 3 --proposed`, and no team of wldn builds flywheel-next
- **THEN** the command is refused, naming wldn's kits, and nothing is posted

#### Scenario: Another agent posts under a record key
- **WHEN** wldn-planner or a conductor calls `post_request` with a key `record/atlas-kit/0021`
- **THEN** the call is refused before it reaches Pending You, saying a record's card is crew's

#### Scenario: The design agent posts under any other key
- **WHEN** wldn-design calls `post_request` with the key `proposal/1`
- **THEN** the call is refused, saying a proposal's card is crew's; a key of its own for a question goes through

## REMOVED Requirements

### Requirement: The owner of a row posts its card
**Reason**: crew raises a row's card itself at its event; no agent posts one (record 0031).

### Requirement: No row's card takes another kind
**Reason**: crew builds every row's card; there is no other kind to refuse.

### Requirement: crew refuses a row's card in another form
**Reason**: no agent builds a row's card; crew refuses an agent's call under a row's key instead.

### Requirement: crew refuses a change that takes a row's card out of its form
**Reason**: the same.

### Requirement: crew refuses a batch card in another form
**Reason**: crew builds the batch's card; no agent posts one.

### Requirement: crew checks only a row's card in a crew session
**Reason**: the hook's scope is "The check refuses what it cannot read, and only for crew's sessions" and "A question is asked by four roles in their own name".

### Requirement: crew refuses a crew agent's card under any key but a row's of its own
**Reason**: a question under the asker's own key is allowed; a row's key is refused to agents (record 0031; the user: "My goal isn't to prevent agents from also using pendingyou").

### Requirement: A crew agent's card is posted through crew
**Reason**: `crew card post` goes; crew posts its own cards at their events.

### Requirement: A crew agent's card is changed, closed and read through crew
**Reason**: `crew card change|close` go; `crew card read` is in "A card is closed by crew at the event that ends it" and "An agent never runs Pending You from npm or waits on a hold".

### Requirement: crew names the card a change ends
**Reason**: crew closes the card itself at the event; there is nothing to name to an owner.

### Requirement: A row's card is closed when the row's key changes
**Reason**: a key is the thing's, not its version's; the card is changed in place.
