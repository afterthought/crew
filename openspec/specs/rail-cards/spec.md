# rail-cards Specification

## Purpose
Each decision on the rail reaches the user as one Pending You card from the agent that owns it, answered on the Mac or the phone, kept true by crew's own events, and shown on the rail so a stale card is seen at once.

## Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, the thing's and not its version's: `proposal/<n>` for a proposal chain, `n` its first proposal; `batch/<n>` for review batch n; `land/<bolt>` for a bolt proven; `deploy/<env>` for a `manual` environment's open offer; `op/<env>/<n>` for a step that waits on the user; `record/<kit>/<number>` for a record proposed. crew SHALL post the row's card with that key as its idempotency key, filled out at its end with `_` to Pending You's eight characters when it is shorter, the same on every post of it, and SHALL record the post under the row's key. A question's card has no row and a key of its asker's own. There SHALL be no review row and no verify row. A batch whose cards were posted under `batch/<n>-<k>` before one card per batch was built SHALL keep a row for each of those keys until its card closes, and SHALL have no `batch/<n>` row.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A key shorter than Pending You takes
- **WHEN** crew raises review batch 7's card, `batch/7` being seven characters, and raises it again after its first post had no answer within a minute
- **THEN** both posts are under `batch/7_`, so Pending You gives the second the card the first made, and the run record holds it under `batch/7`

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2` from before one card per batch, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, until its card closes

#### Scenario: A bolt proven again on a new head
- **WHEN** bolt `y` was ready to land at head `abc1234`, a note on its landing card named a defect, and a fix landed on the bolt at `def5678` with its verification green
- **THEN** its landing row's key is still `land/y`, and crew raises a new landing card under it, following the one the fix held

#### Scenario: A unit built again
- **WHEN** unit `u` was constructed at head `abc1234`, and construct runs again and commits `def5678`
- **THEN** no review row or key exists for either head; the unit's revised change is due for the partition's next batch, whose card's key is the batch's

#### Scenario: A verify report saved
- **WHEN** unit `u`'s verify saves its report `verify-u-20261013-1200.md`
- **THEN** the rail has no row for it, and a card keyed `verify/u/20261013-1200` belongs to no row

#### Scenario: A proposal replaced
- **WHEN** proposal 4 is replaced by proposal 5
- **THEN** the rail's row for proposal 5 has the key `proposal/4`, and its card is the chain's

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

### Requirement: Landing is approved only by holding the button
A landing's card SHALL be an `approve` of risk high, not reversible, so it is approved by holding the button in the Pending You app and never with a key in Herdr's popup; it SHALL NOT carry the `highStakes` flag, which Pending You refuses on an approval.

#### Scenario: Landing from the popup
- **WHEN** the user presses the approve key on a landing card in Herdr's popup
- **THEN** Pending You refuses it as high risk, and the bolt does not land

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
Each card crew posts, changes, withdraws or closes, and each a crew agent posts, changes or closes through Pending You's tools, SHALL be an entry in the partition's run record naming the row's object or the asker, the card's id in `Card` and the key in `Key`, crew's read from Pending You's own reply, an agent's from the tool's result; an agent's act whose result names no card SHALL be recorded on the agent with `State: unread`, and `crew rail` SHALL list each such act of the last 14 days with its agent, its act and its time. An entry SHALL NOT hold a card's title, summary or other text.

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

#### Scenario: A question whose reply names no card
- **WHEN** swb-1-conductor's `post_request` under `ask/swb-1-conductor/hold-the-macs` returns a result that names no card
- **THEN** the run record has a `card.post` entry on swb-1-conductor with that key and `State: unread`, and `crew rail` lists it with swb-1-conductor, the act and its time

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
- **WHEN** crew raises the card of srv's first step for the user after swancloud-ops's deploy card for srv
- **THEN** the step's card follows that deploy card, and the phone shows it in that card's thread

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

### Requirement: The check refuses what it cannot read, and only for crew's sessions
crew's hook SHALL run only in a session with `CREW_AGENT` set, and SHALL refuse a card's post, change or close, or an area's making, when it cannot read the agent's partition, the teams file, or crew's record of its cards, the run record on this host that holds the key of the card a change or close names, naming what it could not read and saying to try again later, never letting a call through on a guess. It SHALL read no plan and fetch no state branch. The user's own sessions SHALL be untouched.

#### Scenario: The plan cannot be read
- **WHEN** swb-1-conductor posts a question under `ask/swb-1-conductor/hold-the-macs` while the partition's state branch cannot be fetched
- **THEN** the call goes through: the hook reads no plan, and judges the key by its form alone

#### Scenario: crew's record of its cards cannot be read
- **WHEN** swb-1-conductor calls `cancel_request` for its card `req_q1` and the hook cannot read the partition's run record on this host
- **THEN** the call is refused, "crew could not check this card: <why>. Try it again later.", and nothing is closed

#### Scenario: The user's own session
- **WHEN** a session with no `CREW_AGENT` calls `post_request`
- **THEN** the hook does nothing, and the call goes through as Pending You ships it

#### Scenario: The agent's role cannot be read
- **WHEN** a crew session's `CREW_AGENT` names no role the teams file knows and the agent calls `post_request`
- **THEN** the call is refused, naming the agent and saying only a conductor, the planner, main-level ops and the design agent ask the user on a card, and nothing is posted

### Requirement: crew's card commands refuse what they cannot do, in the words that say why
A card act Pending You refuses SHALL be refused in Pending You's own words and recorded as the act refused, and SHALL refuse nothing of the event it was raised for. When the host is not signed in to Pending You, or Pending You cannot be reached or does not answer within 60 seconds, the act SHALL be recorded as not posted, the command SHALL say so, and the event SHALL stand. A reply that lacks the card's or the area's id SHALL be recorded as unread, never taken as empty.

#### Scenario: Pending You refuses the card
- **WHEN** Pending You refuses a card crew posts with "Approve requests give their risk in approve.risk."
- **THEN** the command says so in those words, the run record has a `card.post` entry with that refusal and no card, and the event it was raised for stands

#### Scenario: The host is not signed in
- **WHEN** the host has no Pending You sign-in and `crew ops offer` runs
- **THEN** the offer is recorded, no card posts, and the command says this computer is not signed in to Pending You

### Requirement: The landing card is posted once the bolt's verification is green
crew SHALL raise a bolt's landing card once every unit and chore of the bolt has merged, every unit's latest change has been in a batch whose card the user has answered, sluice's verdict at its head is green and no fix of it is in flight, none whose place stands that has neither merged nor been dropped, keyed `land/<bolt>`, as an `approve` of risk high, not reversible, because irreversible, its summary giving the counts, the batches, the verdict and when, how far main has moved, and, when its team holds another bolt that is proven too, the team's next planned bolt that a yes frees it for, or that nothing is planned for it; its face a text artifact "What lands: N units, M chores" naming each one a line, its rationale what follows, and, when sluice's submission at the head has a pull request on GitHub, that pull request as a `url` artifact and among its links; it SHALL ask only for the landing. When a merge makes the team's other bolt proven while the card waits on the user, the card SHALL be changed to say what a yes frees. A note naming a defect SHALL have the conductor start a fix on the bolt, which withdraws the card, and the card SHALL be raised again once the bolt reads proven again.

#### Scenario: Sluice's pull request
- **WHEN** sluice's submission at `y`'s head has pull request #23 on the kit's GitHub
- **THEN** the card links it, titled as sluice's pull request for the landing, on its face and in its details

#### Scenario: No pull request
- **WHEN** the kit's sluice opens no pull request for a submission
- **THEN** the card carries no link, and says nothing of one

#### Scenario: A green bolt
- **WHEN** every unit and chore of bolt `y` has merged, each unit's latest change has been in a batch the user has answered and sluice is green at `abc1234`
- **THEN** one card keyed `land/y` is open, an approve of risk high, naming the units and chores and the verdict

#### Scenario: A yes frees the team for its next bolt
- **WHEN** swc-1's card `land/y` waits on the user, and the last unit of swc-1's other bolt `z` merges with sluice green at its head, and `d` is the next planned bolt of swc-1's kit
- **THEN** `land/y` is changed in place, its summary saying a yes frees swc-1 for `d`

#### Scenario: A fix in flight holds the card
- **WHEN** every unit and chore of bolt `y` has merged, each unit's latest change has been in a batch the user has answered and sluice is green at its head, but `fix/y/gap`, started on `y`, has neither merged nor been dropped
- **THEN** no landing card is open for `y`, its rail row says it lands once `fix/y/gap` has merged or been dropped, and the card is raised once it has

#### Scenario: A landing row before the bolt reads proven
- **WHEN** every unit of bolt `y` has merged and one unit's latest change has not been in a batch
- **THEN** the rail shows `y`'s landing row, saying it lands once that unit has been in a batch, and the rail's read raises no card for it

#### Scenario: A landing row while a batch card waits on the user
- **WHEN** every unit of bolt `y` has merged, sluice is green at its head, and batch 7, whose card the user has not answered, holds a unit's latest change
- **THEN** the rail shows `y`'s landing row, saying it lands once you have answered batch 7, and the rail's read raises no card for it until the user has answered batch 7's card

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
A proposal's card SHALL carry its change as an artifact of kind `code` with lang `text`, its lines crew's text of the change, each at most forty characters, so it reads in monospace on a phone without wrapping.

#### Scenario: A proposal's change as text
- **WHEN** crew raises the card for proposal 4, which drops a unit and adds two
- **THEN** the card carries the new and dropped units' paragraphs as Markdown, the uploaded picture, and a `code` artifact of lang `text` holding the change, each line at most forty characters, and no link to a session

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
A deploy's card SHALL be an `approve` of risk high, not reversible, because irreversible, naming the environment and the commit; its summary SHALL count the landings since the environment's last deploy and name the environments before and after it, and its details SHALL hold the landings' subjects. It SHALL follow its environment's last deploy card when the user declined that card, and otherwise no card.

#### Scenario: Three landings since srv's last deploy
- **WHEN** the deployer offers srv `c882cff` with git-cliff's notes for `6aed25c..c882cff` and two steps, and srv runs `6aed25c`
- **THEN** the card's approve block has risk high and reversible false, its summary counts three landings and says the box follows on its own and mac-studio is offered after srv, its face holds the notes as handed and the two steps with their doers, and its details name landings #16, #17 and #18

#### Scenario: A head a landing card put on main
- **WHEN** crew raises srv's deploy card for a head that landing #24's card put on main
- **THEN** the card follows no card, and its details name landing #24

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
Every card crew posts under a row's key after a card of the owner's under that key has closed SHALL take the key with its revision, `<key>:<n>`, as its idempotency key, so Pending You never gives the closed card back. A card still open under the key SHALL keep its own key, so posting it again gives it back, and the run record SHALL hold one post of it: a post Pending You answers with the card this host's record already holds open under the key and owner is that card, printed with the line that adopts it and recorded no second time.

#### Scenario: A card raised again after its last card closed
- **WHEN** crew raises b1's landing card after the user declined the last one under `land/b1`, or follows an answered one with its new version
- **THEN** it is posted under `land/b1:2` as a new card

#### Scenario: A card posted again while it is open
- **WHEN** crew posts its card under `land/b1` again while `req_1` is open there
- **THEN** it is posted under the key its first post took, `land/b1_`, and Pending You gives `req_1` back

#### Scenario: Two rail reads raise a row's card at once
- **WHEN** two rail reads on mac-studio, from two agents' starts, sweep at once, each posts `op/srv/1`'s card, and Pending You gives both `req_1`
- **THEN** the run record holds one `card.post` of `req_1` under `op/srv/1`, written by the read that recorded it first, and the other read prints `req_1` and `call get_request (requestId req_1, name <role>)`

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
A step whose doer is the user SHALL be a `do` card with the step's words, where it is done, each command whole as an action step, what is seen when it worked, and the options Done, Skip and Later. A step an agent runs on its own SHALL have no card. When a deploy ends with more than one step for a card, crew SHALL raise one card at a time: the first following the deploy's card, each next one following the one before, raised when crew closes it. Only another step's open card SHALL hold a step's card back: a step recorded again while its own card is open changes that card, as a row's card changes when its thing changes.

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

### Requirement: crew raises a row's card at its event
crew SHALL build and post each rail row's card itself, from the facts of the event that makes the row, by the command that makes or reads the event, through the fleet's `pendingyou mcp --app claude-code` under the host's sign-in, in the name of the role whose row it is, with the row's key as the card's idempotency key. No crew agent SHALL write, post or close a row's card.

#### Scenario: A proposal accepted into the plan
- **WHEN** the planner runs `crew plan propose <file>` and the proposal is accepted as number 4
- **THEN** one card keyed `proposal/4` is open, asked in the planner's name, built by crew from the plan and the proposal, and the command prints its id and `call get_request (requestId <id>, name <role>)`

#### Scenario: A bolt reads proven at the merge's end
- **WHEN** the merge of bolt `y`'s last unit is recorded, every unit's latest change has been in a batch the user has answered and sluice's verdict at `y`'s head is green
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

### Requirement: A row's card is changed in place when its thing changes
When what a row's card asks changes while it is open, crew SHALL change the one card in place with a change note the user sees, and SHALL post no second card under a new key. A card that asks questions, a proposal's whose rows fill more than one list, SHALL never be changed in place, since Pending You's `update_request` changes no card's questions: while it waits crew SHALL withdraw it with the change note and post its new version following it, under the key's next revision. A rewrite that moves a proposal's card to another form, a hold-to-approve, a choice, one list or lists, read from the replaced proposal's commands, SHALL be followed the same way, since Pending You changes no card's kind in place. A proposal chain's card SHALL be the first proposal's, and the rail's row for the replacing proposal SHALL carry it.

#### Scenario: A proposal rewritten while its card waits
- **WHEN** proposal 4's card, its rows in one list, is open and unanswered, and the planner runs `crew plan propose <file> --replaces 4` and proposal 5 is accepted
- **THEN** the card keyed `proposal/4` is changed in place to proposal 5's, with the change note "Rewritten as proposal 5 after your note", and the rail's row for proposal 5 names it as its card

#### Scenario: A proposal whose rows fill more than one list rewritten while its card waits
- **WHEN** proposal 4's card asks its seven rows as `rows-1` and `rows-2`, is open and unanswered, and the planner runs `crew plan propose <file> --replaces 4` and proposal 5 is accepted
- **THEN** the card is withdrawn, "Rewritten as proposal 5 after your note", and proposal 5's card, asking proposal 5's rows, is posted under `proposal/4:2` following it, since Pending You changes no card's questions in place; the rail's row for proposal 5 names the new card

#### Scenario: A rewrite that moves a proposal's card to another form while it waits
- **WHEN** proposal 4's card asks its seven rows as `rows-1` and `rows-2`, is open and unanswered, and proposal 5, which replaces it, has three rows, one list
- **THEN** the card is withdrawn, "Rewritten as proposal 5 after your note", and proposal 5's one list is posted under `proposal/4:2` following it; so is a hold-to-approve rewritten to a list, or a list to lists

#### Scenario: A merge moves a bolt with an open landing card
- **WHEN** the landing card `land/y` is open and unanswered, and a merge into bolt `y` moves its head to `def5678`
- **THEN** crew changes the card in place, "Its head is now def5678", and posts no second card

#### Scenario: A newer head offered
- **WHEN** `deploy/srv`'s card is open for `abc1234` and the deployer offers `def5678`
- **THEN** the same card is changed to `def5678`, with the change note "Now offering def5678, which includes abc1234"

#### Scenario: A conductor agrees
- **WHEN** `proposal/4`'s card says it waits on crw-2's conductor and that conductor runs `crew plan agree 4`
- **THEN** the card is changed in place, "No longer waits on crw-2-conductor"

#### Scenario: A step recorded again with new words
- **WHEN** `op/srv/1`'s card is open, raised from the deployer's text for its step, and main-level ops records that step again waiting on the user with new words
- **THEN** the same card is changed in place, "Recorded again: its words changed", and the command prints its id and `call get_request (requestId <id>, name <role>)`; recorded again with the words the card shows, the card is not changed and the command prints the same line

#### Scenario: A step's card that changes in kind
- **WHEN** `op/srv/1`'s card, the user's `do`, is open and its step is recorded again with main-level ops its doer, held for the user's word
- **THEN** the card is withdrawn, "Recorded again: its doer and its hold changed", and the step's choice is posted under `op/srv/1:2` following it, since Pending You changes no card's kind in place

### Requirement: A card is closed by crew at the event that ends it
crew SHALL close each of its cards at the event that ends what it asks, with a one-line outcome, and SHALL withdraw a row's card whose row is gone on the next rail read, with the reason. A declined approval SHALL be closed with the user's words when its owner reads it with `crew card read`. The outcome or reason crew sends with a close SHALL be cut to Pending You's 200 characters, and the run record SHALL keep it whole.

#### Scenario: An outcome longer than Pending You takes
- **WHEN** an approval's outcome, naming every unit it added and every one the user left out, runs past 200 characters
- **THEN** the card is acked with the outcome cut to 200 characters, ending with …, and the run record's close holds it whole

#### Scenario: A proposal approved from the phone
- **WHEN** the user approves `proposal/4` on the phone with its new unit `c` unticked, and the planner runs `crew plan answer 4 rows-1 b`
- **THEN** crew applies the proposal with `c` left out and closes the card "Applied: added b. Left out on your word: c.", and the rail's proposal row is gone

#### Scenario: A proposal dropped
- **WHEN** the planner runs `crew plan drop 4 "the user: not this quarter"`
- **THEN** the card is withdrawn with those words

#### Scenario: A bolt landed
- **WHEN** main-level ops runs `crew bolt land y` after the landing's submission
- **THEN** `land/y`'s card is closed "landed on GitHub's main at <its commit>; every host's folder follows by swancloud's timer within minutes"

#### Scenario: A deploy fails
- **WHEN** the deployer records the end of srv's deploy of `abc1234` with its `guests` step failed
- **THEN** `deploy/srv`'s card is closed "The deploy of abc1234 to srv failed at guests; its log: <its log>."

#### Scenario: A step done
- **WHEN** the user answers `op/srv/1` Done and main-level ops runs `crew ops step srv --key <key> --state done`
- **THEN** the card is closed "Done."

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
crew SHALL refuse a post, change or close from any role but the four, naming the chain of command, and a crew agent's own post, change or close under a row's key or of a row's card, naming the card as crew's; it SHALL refuse nothing else of a question's form. A post's key SHALL be judged by its form alone, with or without `:<n>` or the fill of a short key; a change's or a close's, which carries a request id, by the card this host's run record holds under that id, crew's raises and the agents' own posts alike.

#### Scenario: A coder asks
- **WHEN** a coder in a crew session calls `post_request`
- **THEN** the call is refused before it reaches Pending You, saying a stage agent asks its conductor with `crew needs`

#### Scenario: A conductor posts its landing card by hand
- **WHEN** swb-1-conductor calls `post_request` with the key `land/y`
- **THEN** the call is refused, saying the landing card is crew's and is raised when the bolt reads proven

#### Scenario: An agent posts under a row's key as crew sends it
- **WHEN** swb-1-conductor calls `post_request` with the key `land/b1_`, or wldn-planner with `batch/7_` or `batch/7:2`
- **THEN** the call is refused, saying the card is crew's

### Requirement: The planner closes the old batch cards it posted
The planner's close, `cancel_request` or `ack_answer`, of a card under `batch/<n>-<k>`, which it posted itself before a batch was one card and which crew never raises, SHALL pass, and its post or change there SHALL be refused.

#### Scenario: The planner closes an old batch card
- **WHEN** wldn-planner calls `cancel_request` for `req_bat-2`, which this host's run record holds as its own post under `batch/2-1`
- **THEN** the call goes through; a `post_request` or `update_request` of the planner's under `batch/2-1` is refused, saying a batch's card is crew's

### Requirement: A crew agent's Pending You call names only the agent itself
In a crew session, crew SHALL refuse a call to any Pending You tool that names anyone but the agent's `CREW_AGENT` as its caller, before the call runs and before any check of the agent's role or the call's key, which narrows apart from it, in words naming the agent's own name and saying the call would reroute another agent's answers to this session; a call that names no caller SHALL pass, and an area's name SHALL be taken as no caller's.

#### Scenario: Another agent's card read in its name
- **WHEN** swb-1-conductor's session calls `get_request` with the name `swancloud-ops`
- **THEN** the call is refused before it reaches Pending You, naming swb-1-conductor as the session's own name and saying swancloud-ops's answers would wake this session instead

#### Scenario: A whoami under another agent's name
- **WHEN** the planner's session calls `whoami` with `previousName` `swb-1-conductor`
- **THEN** the call is refused, naming the planner's own name, and swb-1-conductor's cards stay with its session

#### Scenario: A question in another agent's name
- **WHEN** the planner, which may ask, calls `post_request` under a key of its own with `session.label` `swb-1-conductor`
- **THEN** the call is refused for its name, though its role and its key would let it through

#### Scenario: A call that names no caller
- **WHEN** a conductor's session calls `list_areas`, or `create_area` with the area's name `switchboard-kit`
- **THEN** the name check lets it through: it names no caller

### Requirement: A deploy waiting at its gate has the user's do card with the gate's link
A step that is the user's whose words are one link alone SHALL be read as a deploy waiting at its gate. Its card, keyed `op/<env>/<n>` and raised by crew in main-level ops's name as every step's card is, SHALL be a `do` asking the user to approve the deploy at its gate, naming the environment and, when the step names one, the commit; its one step and its *where* SHALL be the gate's link, and it SHALL say the approval at the gate is the word to deploy.

#### Scenario: swb-4's break-glass stand at dev's gate
- **WHEN** the step `gate-38612817613` on dev, for the commit `4f2a9c1`, is recorded waiting with doer user and the text `https://github.com/WilldanGroup/switchboard-kit/actions/runs/38612817613`
- **THEN** crew raises the card `op/dev/<n>` in wldn-ops's name, a `do` titled "Approve the deploy of 4f2a9c1 to dev at its gate", its one step and its *where* that link, its summary saying the approval at the gate is the word to deploy and nothing else asks for it, with Done, Skip and Later

#### Scenario: A gate whose step names no commit
- **WHEN** the gate's step is recorded with no commit
- **THEN** its card is titled "Approve the deploy to dev at its gate"

#### Scenario: A gate with a why
- **WHEN** the gate's text is its link followed by a `- why:` line
- **THEN** the card's summary gives the why after saying what waits

#### Scenario: A user's step whose words are more than a link
- **WHEN** a step that is the user's says "Open https://example.com and rotate the key"
- **THEN** it is an after-deploy step, and its card is the user's `do` as before

#### Scenario: An agent's step whose words are a link
- **WHEN** a step whose doer is main-ops, held for the user's word, has a link alone as its words
- **THEN** it is no gate: its card is the choice of when, as for every held step

### Requirement: A card Pending You has ended reads closed to crew
crew SHALL read a card of its own as ended once Pending You reports it `resolved`, `cancelled` or `expired`, recording a resolved card closed and a cancelled or expired one withdrawn, and SHALL send it no change and no close from then on. A change SHALL post the card's next version as a new card under its key's next revision, following the old card if it was resolved and nothing if it was cancelled or expired.

#### Scenario: A card the user dismissed while crew held it open
- **WHEN** crew goes to change or close its card under `land/b1`, and Pending You reports it `cancelled`
- **THEN** crew records the card withdrawn as ended in Pending You already, sends no `update_request`, `ack_answer` or `cancel_request`, and a change posts its new version under `land/b1:2`, following nothing

#### Scenario: A question already ended when its asker is gone
- **WHEN** the rail's read withdraws crw-3-conductor's question after crw-3's team closed, and Pending You reports the question `resolved`
- **THEN** crew records it closed as ended in Pending You already, and sends no `cancel_request`

### Requirement: A post that follows an open card reads it
When crew posts a card that follows a card of the same owner the run record still holds open, it SHALL read that card once the post is made, and SHALL record it closed if Pending You has ended it, as Pending You does for an answered card a new card follows. A read that fails SHALL leave the post standing and the followed card as the record holds it.

#### Scenario: A deploy card picked up by its step's card
- **WHEN** the user has approved `deploy/mac-studio`'s card, its deploy records a step that is the user's, and crew posts `op/mac-studio/1`'s card following the deploy's card, which Pending You then reports `resolved`
- **THEN** the run record holds the deploy's card closed, and the rail shows mac-studio with no open deploy card

#### Scenario: The deploy's end after its card was picked up
- **WHEN** the deployer records the end of that deploy
- **THEN** crew finds no open card under `deploy/mac-studio`, sends Pending You nothing, and records no refused close

#### Scenario: The next offer to that environment
- **WHEN** the deployer then offers mac-studio d35fbf2
- **THEN** crew posts a new card under `deploy/mac-studio`'s next revision, following the card a deploy's card follows when its last one closed, and the user can approve it, as they could deneb's offer of d35fbf2

#### Scenario: A card followed while it still waits
- **WHEN** crew posts a card following one of its own that Pending You still reports `pending` or `answered` after the post
- **THEN** the followed card stays open in the run record, for the event that ends it to close

### Requirement: A card carries what the user reads and the row's answers
A proposal's card SHALL hold the proposal whole, picture, text and case, linking a reading session only when it holds more than fifteen new units. A batch's card SHALL link its one session. A landing's card SHALL link its one session, on what the bolt brings to main, first in its details and among its links, saying the reading lands nothing. A deploy's, a step's and a record's card SHALL link no session: each holds what the user decides from.

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

#### Scenario: A landing card links its reading
- **WHEN** crew raises bolt `y`'s landing card
- **THEN** it names the units and chores that land, sluice's verdict and when, and how far main has moved, as before; its details open with the link to `land/y`'s session and say the reading lands nothing; the link is among its links, after which sluice's pull request when it has one; and it is an approval of risk high, the approval being the word to land

#### Scenario: A landing approved without opening its reading
- **WHEN** the user approves `land/y`'s card without opening its session
- **THEN** the conductor tells main-level ops to land `y` as before, and nothing waits on the session

### Requirement: A landing's card lists the addresses of a preview of its head
When crew raises a bolt's landing card in a kit whose sluice policy, as the bolt's head holds it, declares `[preview]`, it SHALL first ask sluice, on the team's host, for a preview of the bolt's head on the bolt's branch, and SHALL raise the card once sluice has named the preview's addresses, without waiting for the preview's stack to come up. The card SHALL list each address under the name the kit's policy gives it, beside the reading's link, and SHALL say that the preview is coming up, that it lands nothing, and that approving the card is the word to land. A kit whose policy at the head declares no `[preview]` SHALL get no preview, and its card SHALL be as it would be without this requirement. The approval SHALL stay the word to land: nothing about the preview SHALL hold, refuse or delay the card or the landing.

#### Scenario: A kit that declares a preview
- **WHEN** bolt `y` reads proven at head `abc1234` in a kit whose policy at `abc1234` declares `[preview]` with addresses `web` and `api`
- **THEN** sluice is asked for a preview of `bolt/y` at `abc1234` on the team's host, and `land/y`'s card lists `web` and `api` with the addresses sluice named, says the preview is coming up and lands nothing, and is an approval of risk high as before

#### Scenario: A kit that declares none
- **WHEN** bolt `y` reads proven in a kit whose policy at its head has no `[preview]` table
- **THEN** sluice is asked for nothing, and `land/y`'s card carries no preview and no word of one

#### Scenario: Approved without opening the preview
- **WHEN** the user approves `land/y`'s card without opening any of its addresses
- **THEN** the conductor tells main-level ops to land `y` as before, and nothing waits on the preview

#### Scenario: Asked again with nothing changed
- **WHEN** crew raises `land/y`'s card again at the same head, as the rail's sweep does for a card that was lost
- **THEN** sluice gives back the preview crew already asked for, its addresses unchanged, and no second preview is made

### Requirement: A preview that fails is said on the card and holds nothing
A preview sluice refuses, that crew cannot ask for or read, or whose addresses sluice does not name within twenty seconds, SHALL be said on the landing card with sluice's or crew's reason, and the card SHALL be raised all the same. A preview whose stack fails to come up after the card listed its addresses SHALL change the card in place, while it waits on the user, to say so with the end of what the preview's command printed, its addresses no longer listed; one whose addresses came too late for the card's raise SHALL change the card in place to list them once it is up. A card the user has answered SHALL be left as it is. None of this SHALL hold the landing.

#### Scenario: The host's sluice has no preview command
- **WHEN** the team's host runs a sluice that refuses `sluice preview` and bolt `y` reads proven
- **THEN** `land/y`'s card is raised, saying the preview could not be asked and why, and listing no addresses

#### Scenario: The stack fails to come up
- **WHEN** `land/y`'s card lists a preview's addresses and the preview's command then exits non-zero
- **THEN** the card is changed in place with a note that its preview did not come up, says so with the last lines of what the command printed, lists no addresses, and stays an approval the user may give

#### Scenario: The host is busy when the card is raised
- **WHEN** sluice waits for room on the team's host and names no preview within twenty seconds of `land/y`'s raise, and the preview later comes up
- **THEN** the card is raised saying its preview is not there yet, and is then changed in place with a note that its preview is up, listing its addresses

### Requirement: The preview follows the bolt's head and ends with the card
When a merge moves a bolt's head while its landing card is open, crew SHALL release the preview it asked for at the old head and ask for one at the new head, and the card, changed in place for the head, SHALL list the new preview's addresses. When crew closes the landing card, landed, held for a fix or declined, it SHALL release the bolt's preview on the team's host. A rail read SHALL release, on each host, a preview crew asked for whose landing card is closed or whose row is gone. crew SHALL release only a preview it asked for, never one asked for by hand or by another tool.

#### Scenario: The head moves
- **WHEN** a fix's merge moves bolt `y`'s head from `abc1234` to `def5678` while `land/y`'s card waits on the user
- **THEN** `abc1234`'s preview is released, one is asked for at `def5678`, and the card, changed in place, lists `def5678`'s addresses

#### Scenario: The bolt lands
- **WHEN** `crew bolt land y` closes `land/y`'s card
- **THEN** the preview of `y`'s head is released on the team's host, and `sluice previews` there no longer lists it

#### Scenario: A fix holds the landing
- **WHEN** a fix started on bolt `y` withdraws `land/y`'s card
- **THEN** the preview is released, and a new one is asked for when the card is raised again at the bolt's new head

#### Scenario: A preview crew did not ask for
- **WHEN** a person previewed an earlier revision of `bolt/y` themselves, and `land/y`'s card later closes
- **THEN** crew releases the preview of the head it asked for, and leaves the person's preview as it is

#### Scenario: A card closed elsewhere
- **WHEN** `land/y`'s card is closed with no crew command closing it and its row is gone, and the rail is read
- **THEN** the sweep on the team's host releases the preview crew asked for, and says so

### Requirement: A card follows only a card in its owner's name
A card crew posts SHALL follow only a card the run record shows posted in the same owner's name, since Pending You takes `follows` only to a card of the asker's own. When the card its thing would follow is another owner's, it SHALL follow nothing and be posted all the same. A deploy's card SHALL never follow a landing's card; the landings it carries are named on its face.

#### Scenario: A deploy of the head a landing left
- **WHEN** swc-2-conductor's landing card for `the-box-works-in-wldn-prod` is closed, its landing left swancloud's main at `ddcf2cb`, and the deployer offers deneb `ddcf2cb`
- **THEN** crew posts deneb's deploy card in swancloud-ops's name under `deploy/deneb`'s key, following no card, and its face names the landings it carries, the-box-works-in-wldn-prod's among them

#### Scenario: Five environments offered that head
- **WHEN** the deployer offers deneb, mac-studio, macbook-pro, chuck-herdr-alpha and swancloud-srv `ddcf2cb`, as it did from 23:54Z on 2026-10-19
- **THEN** none of the five posts follows swc-2-conductor's card, and none is refused as another agent's

#### Scenario: A newer head after the user declined
- **WHEN** the user declined srv's deploy card `req_d1` and the deployer offers srv a newer head
- **THEN** the new card follows `req_d1`

#### Scenario: A deploy after one that ran
- **WHEN** srv's last deploy card closed with its deploy's outcome and the deployer offers srv a newer head
- **THEN** the new card follows nothing

#### Scenario: A step after its deploy
- **WHEN** swancloud-ops's deploy card for srv was posted and the deploy's first step for the user waits
- **THEN** the step's card follows that deploy card, as before

#### Scenario: A landing raised again on a team that did not post the last one
- **WHEN** bolt b7's last landing card was withdrawn in swb-1-conductor's name and b7 is now held by swb-2, whose conductor raises it again
- **THEN** the new card follows nothing

### Requirement: A row's card that Pending You refused is owed until it posts
A post of a row's card that Pending You refuses SHALL be recorded as a `card.post` on the row's object, under the row's key, in its owner's name, marked refused in Pending You's words, and SHALL refuse nothing of the event it was raised for. The row SHALL stay on the rail, owing its card, with no card open and those words on its card line, until a later post of it is made: by the event raising it again, a deploy's by the next offer of its commit, or by the rail's sweep.

#### Scenario: Pending You refuses a deploy card
- **WHEN** Pending You refuses deneb's deploy card
- **THEN** the run record has a `card.post` on `env/deneb` under `deploy/deneb`, in swancloud-ops's name, marked refused with Pending You's words, `crew rail` shows deneb's row with no card open and those words, and the offer stands

#### Scenario: The next offer of that commit
- **WHEN** deneb's card for `ddcf2cb` was refused and the deployer offers deneb `ddcf2cb` again
- **THEN** crew posts the card, and the rail's card line for `deploy/deneb` names it open, swancloud-ops's
