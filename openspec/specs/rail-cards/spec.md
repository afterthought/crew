# rail-cards Specification

## Purpose
Each decision on the rail reaches the user as one Pending You card from the agent that owns it, answered on the Mac or the phone, kept true by crew's own events, and shown on the rail so a stale card is seen at once.

## Requirements

### Requirement: Each rail row has a card key
Each rail row SHALL have one card key, the thing's and not its version's: `proposal/<n>` for a proposal chain, `n` its first proposal; `batch/<n>` for review batch n; `land/<bolt>` for a bolt proven; `deploy/<env>` for a `manual` environment's open offer; `op/<env>/<n>` for a step that waits on the user; `record/<kit>/<number>` for a record proposed. crew SHALL post the row's card with that key as its idempotency key, filled out at its end with `_` to Pending You's eight characters when it is shorter, the same on every post of it, and SHALL record the post under the row's key. A question's card has no row and a key of its asker's own. There SHALL be no review row and no verify row. A batch's row SHALL last until its card closes or the batch waits on nothing (`review-batches`). A batch whose cards were posted under `batch/<n>-<k>` before one card per batch was built SHALL keep a row for each of those keys until its card closes or the units it holds wait on nothing, and SHALL have no `batch/<n>` row.

#### Scenario: A batch of seven
- **WHEN** review batch 3 holds seven changes and no card has been posted for it
- **THEN** the rail has one batch row for it, keyed `batch/3`, holding all seven units

#### Scenario: A key shorter than Pending You takes
- **WHEN** crew raises review batch 7's card, `batch/7` being seven characters, and raises it again after its first post had no answer within a minute
- **THEN** both posts are under `batch/7_`, so Pending You gives the second the card the first made, and the run record holds it under `batch/7`

#### Scenario: A batch posted as two cards before
- **WHEN** the run record holds the planner's posts of batch 2's cards under `batch/2-1` and `batch/2-2` from before one card per batch, and `batch/2-1` has closed
- **THEN** the rail has one row for batch 2, keyed `batch/2-2`, holding its units as before, until its card closes

#### Scenario: An old batch card whose units have landed
- **WHEN** batch 2's cards were posted under `batch/2-1` and `batch/2-2`, neither has closed, and every unit `batch/2-2` holds has landed while one unit of `batch/2-1` has not
- **THEN** the rail has one row for batch 2, keyed `batch/2-1`, and the sweep withdraws `batch/2-2`'s card, saying its units have landed

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
A kit's landings card SHALL never be landed from a key in Herdr's popup. With one row that can land it SHALL be an `approve` of risk high, not reversible, approved by holding the button in the Pending You app, and SHALL NOT carry the `highStakes` flag, which Pending You refuses on an approval. With two or more it SHALL be a list of boxes carrying `highStakes`, which Pending You takes on a list as the same test as risk high.

#### Scenario: Landing from the popup
- **WHEN** the user presses the approve key on a landings card of one row in Herdr's popup
- **THEN** Pending You refuses it as high risk, and the bolt does not land

#### Scenario: A list of three bolts
- **WHEN** crew raises `land/crew` with three rows that can land
- **THEN** the card is one list of three boxes with `highStakes` set, and no `approve` block

### Requirement: An answer wakes the owner, which acts on the user's word
An answer on a crew card SHALL be acted on by the role whose row it is, woken in its session by the card it adopted, and by no other: the planner applies or rewrites the proposal, and reads a batch's answer with `crew card read batch/<n>`; main-level ops lands the bolts the user ticked on a kit's landings card, in the card's order, and passes a note naming a defect in a bolt to that bolt's conductor, who starts a fix on it; main-level ops runs the deploy's approval or the step's state; the design agent sets the record's status. crew SHALL then close the card at that act's event. No process of crew's SHALL wait on a card's answer. Where the role runs as its kind, the host's follower SHALL write an ask of the role for each change Pending You's notice names on a card in the role's name, once per version of the card, reading nothing of the card, and the role's next run SHALL read the card in the role's own name and act on it as the woken session would.

#### Scenario: A proposal approved from the phone
- **WHEN** the user approves the card for proposal 4 on the phone
- **THEN** the planner is woken, runs `crew plan answer` and `crew plan approve 4`, which closes the card with what was applied, and the rail's proposal row is gone

#### Scenario: Changes asked for on a review card
- **WHEN** the user writes a note on a batch's card asking for changes to unit `x`
- **THEN** the planner is woken, `crew card read batch/<n>` prints the note and closes the card, the conductor runs construct again with its words, and no approval is asked

#### Scenario: Landing approved
- **WHEN** the user leaves `a` and `c` ticked on `land/crew`, clears `b`, and sends
- **THEN** swancloud-ops is woken, `crew card read land/crew` prints `a` then `c` and the command that lands them in that order, and no conductor is asked to pass anything on

#### Scenario: A defect noted on a row
- **WHEN** the user's note on `land/crew` names a defect in bolt `b`
- **THEN** swancloud-ops tells `b`'s conductor the note's words, the conductor starts a fix on `b`, and `b`'s row is held for the fix

#### Scenario: A proposal approved while the planner runs as its kind
- **WHEN** madswan's planner runs as its kind, no run of it is live, and the user approves proposal 12's card on the phone
- **THEN** the host's follower, told by Pending You's notice, writes one ask of the planner naming the card's request, and the planner's next run reads the card in madswan-planner's name and runs `crew plan answer` and `crew plan approve 12`

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
crew SHALL keep one landings card for each kit with a proven bolt waiting on its main, keyed `land/<kit>`, in the name of the partition's main-level ops, posted on the partition's main host. A bolt SHALL be a row that can land once every unit and chore of it has merged, every unit's latest change has been in a batch whose card the user has answered, sluice's verdict at its head is green and no fix of it is in flight. Rows SHALL be in the plan's order. The card SHALL ask only for the landing.

#### Scenario: A green bolt
- **WHEN** every unit and chore of bolt `y` of crew has merged, each unit's latest change has been in a batch the user has answered and sluice is green at `abc1234`, and no other bolt of crew can land
- **THEN** one card keyed `land/crew` is open in swancloud-ops's name, an approve of risk high, naming `y`, its units and chores and the verdict

#### Scenario: Sluice's pull request
- **WHEN** sluice's submission at `y`'s head has pull request #23 on the kit's GitHub
- **THEN** `y`'s row links it, titled as sluice's pull request for `y`'s landing, on the card's face and in its details

#### Scenario: No pull request
- **WHEN** the kit's sluice opens no pull request for a submission
- **THEN** the row carries no link, and says nothing of one

#### Scenario: Two green bolts of one kit
- **WHEN** bolts `y` and `z` of crew both read proven, `y` first in the plan
- **THEN** one card keyed `land/crew` is open in swancloud-ops's name, its rows `y` then `z`, and no card is open under `land/y` or `land/z`

#### Scenario: Bolts of two kits
- **WHEN** bolt `y` of crew and bolt `w` of swancloud both read proven
- **THEN** `land/crew` holds `y`, `land/swancloud` holds `w`, and each is its own card

#### Scenario: A row carries what the bolt's card carried
- **WHEN** bolt `y` of swc-1, holding units `a` and `b` read in batch 7 and chore `c`, reads proven at `abc1234`, sluice green there since 10:02 with pull request #23, main moved two landings since `y` was cut
- **THEN** `y`'s row names swc-1-conductor, `a`, `b` and `c (chore)`, batch 7, `abc1234` green since 10:02, two landings, pull request #23 linked, and `y`'s reading's link

#### Scenario: A second bolt is proven while the card waits
- **WHEN** `land/crew` waits on the user with one row, `y`, and bolt `z` of crew reads proven
- **THEN** the card becomes a list of `y` and `z`, posted following the one it replaces since a card's kind does not change in place, with a change note naming `z`

#### Scenario: A row's head moves while the card waits
- **WHEN** `land/crew` waits on the user as a list of `y` and `z`, and a fix's merge moves `z`'s head to `def5678`
- **THEN** the card is changed in place, its note saying `z`'s head is now `def5678`, and `z`'s row carries its reading of `def5678` and, where the kit's policy names a preview, `bolt/z` at `def5678` as what brings it up

#### Scenario: A yes frees the team for its next bolt
- **WHEN** swc-1's bolt `y` is a row of `land/crew`, and the last unit of swc-1's other bolt `z` merges with sluice green at its head, and `d` is the next planned bolt of swc-1's kit
- **THEN** `y`'s row says a yes frees swc-1 for `d`

#### Scenario: A fix in flight holds the card
- **WHEN** bolt `y` would read proven, but `fix/y/gap`, started on `y`, has neither merged nor been dropped
- **THEN** `y` has no box on `land/crew`, its row on the card's face says it is held for `fix/y/gap`, and it has a box again once the fix has merged and `y` reads proven

#### Scenario: A landing row before the bolt reads proven
- **WHEN** every unit of bolt `y` has merged and one unit's latest change has not been in a batch
- **THEN** the rail's landing row for crew names `y`, saying it lands once that unit has been in a batch, and `y` is no row of `land/crew`

#### Scenario: A landing row while a batch card waits on the user
- **WHEN** every unit of bolt `y` has merged, sluice is green at its head, and batch 7, whose card the user has not answered, holds a unit's latest change
- **THEN** the rail's landing row for crew names `y`, saying it lands once you have answered batch 7, and `y` is no row of `land/crew` until the user has answered batch 7's card

#### Scenario: A defect noted on the card
- **WHEN** the user sends `land/crew` with a note naming a defect in `y`, and `y`'s conductor runs `crew fix` on `y` in the note's words
- **THEN** `y` loses its box and its row says "held for a fix: <the note>", and it has a box again once `y` reads proven again

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
When crew changes one of its own cards because its thing changed, it SHALL change the card in place while the card waits on the user. Once the user has answered the card, which Pending You no longer changes, crew SHALL ack it with the change note as its outcome and post the new version as a new card that follows it, in the same owner's name, saying first that the user answered the earlier card, when and with what, and what changed since, as every card that follows one the user answered says it. The run record SHALL hold the answered card's close, with the answer, and the new card's post, both under the row's key.

#### Scenario: A card waiting on the user
- **WHEN** crew changes its card `req_1` under `land/b1`, which waits on the user
- **THEN** `req_1` is changed in place with the change note

#### Scenario: A card the user answered
- **WHEN** crew changes its card `req_1` under `land/b1` after the user has answered it
- **THEN** `req_1` is acked with the change note, and a new card following `req_1` is posted, its summary opening with what the user answered on `req_1` and what changed. The run record has `req_1`'s close, with the answer, and the new card's post under `land/b1`, and `crew card read land/b1` finds the new card

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
- **THEN** the rail's refresh tells the planner to read batch 3, its `crew card read batch/3` prints them, they go to the unit's conductor as the user's words, and the batch's card is closed

#### Scenario: A proposal's card holds the proposal whole
- **WHEN** crew raises the card for proposal 4, which adds two units
- **THEN** the card carries the picture, the text and the case, and no session link

#### Scenario: A landing card links its reading
- **WHEN** crew raises bolt `y`'s landing card
- **THEN** it names the units and chores that land, sluice's verdict and when, and how far main has moved, as before; its details open with the link to `land/y`'s session and say the reading lands nothing; the link is among its links, after which sluice's pull request when it has one; and it is an approval of risk high, the approval being the word to land

#### Scenario: A landing approved without opening its reading
- **WHEN** the user approves `land/y`'s card without opening its session
- **THEN** the conductor tells main-level ops to land `y` as before, and nothing waits on the session

### Requirement: A preview that fails is said on the card and holds nothing
A preview sluice refuses, that crew cannot ask for or read, or whose addresses sluice does not name within twenty seconds of the ask, SHALL be said on its row or line with sluice's or crew's reason, the card changed in place while it waits on the user. A preview whose stack fails to come up after its addresses were listed SHALL change the card in place to say so with the end of what the preview's command printed, its addresses no longer listed; one whose addresses came too late SHALL change the card in place to list them once it is up. A card the user has answered SHALL be left as it is. None of this SHALL hold the landing.

#### Scenario: The host's sluice has no preview command
- **WHEN** swancloud-ops runs `crew card preview land/crew y` and the team's host runs a sluice that refuses `sluice preview`
- **THEN** `land/crew` is changed in place, `y`'s row saying its preview could not be brought up and why, listing no addresses, and `y` keeps its box

#### Scenario: A line naming a branch sluice does not land
- **WHEN** the planner runs `crew card preview batch/7 a/demo` for a line naming `unit/a` at `abc1234`, and sluice refuses since no `[branches]` table names `unit/a`
- **THEN** batch 7's card is changed in place, saying under `a` that `demo` could not be brought up, in sluice's words

#### Scenario: The stack fails to come up
- **WHEN** `y`'s row lists a preview's addresses and the preview's command then exits non-zero
- **THEN** the card is changed in place with a note that `y`'s preview did not come up, the row says so with the last lines of what the command printed and lists no addresses, and `y` keeps its box

#### Scenario: The host is busy when the card is raised
- **WHEN** sluice waits for room on the team's host and names no preview within twenty seconds of the ask, and the preview later comes up
- **THEN** the row says its preview is not there yet, and the card is then changed in place with a note that `y`'s preview is up, listing its addresses

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

### Requirement: A row's card its owner's host can't reach is raised again there
A card belongs to the Pending You sign-in of the host it was posted from, and each row's card is raised and waited on only where its owner runs: a proposal's, a batch's, a deploy's, a step's and a kit's landings card on the partition's main level's host. When the owner's newest card under a row's key was posted from another host and no close ends it, or its last close is as lost to the owner on any host, and no newer card of the owner's is under the key, the rail's next read on the owner's host SHALL post the row's card again there under the row's key, through its kind's raise, its summary opening with the words that say an older copy was lost and to dismiss it in the app, while the row still waits on its card; and the rail SHALL take the new card as the row's. crew SHALL neither ask after nor close the older copy from a host whose sign-in does not reach it. A row that no longer waits SHALL have no card posted again, and the read SHALL say its raise posted none.

#### Scenario: The main level moved to another host
- **WHEN** batch 13's card was posted from mac-studio, the partition's main level now runs on deneb, the user has not answered the batch where crew can read it, and the rail is read on deneb
- **THEN** crew posts batch 13's card again on deneb under `batch/13` in the planner's name, its summary opening "An older copy of this card was lost: dismiss it in the app.", the rail shows the new card's id as the row's, and the read lists the older card as lost and the new one as posted

#### Scenario: A proposal's card left on the host the main level left
- **WHEN** proposal 13's card was posted from mac-studio in the planner's name, proposal 13 is still open, the main level now runs on deneb, and the rail is read on deneb
- **THEN** crew posts proposal 13's card again on deneb under `proposal/13`, in its form, its summary opening with the words that say an older copy was lost, and the rail shows the new card's id as the row's

#### Scenario: A deploy's and a step's card left behind
- **WHEN** `deploy/dev`'s card, or `op/dev/2`'s, was posted from mac-studio in main-level ops's name, the offer or the step still waits on the user among the operations recorded on deneb, and the rail is read on deneb
- **THEN** crew posts that card again on deneb in main-level ops's name, saying an older copy was lost

#### Scenario: A landings card left on the host the main level left
- **WHEN** `land/crew` was posted from mac-studio in swancloud-ops's name, the main level now runs on deneb, bolt `y` of crew still reads proven, and the rail is read on deneb
- **THEN** crew posts the landings card again on deneb under `land/crew`, with `y` as its row, saying an older copy was lost

#### Scenario: Lost to the planner on the host it was posted from
- **WHEN** batch 13's card was recorded lost to the planner on mac-studio, no card was posted under `batch/13` since, and the rail is read on deneb, the main level's host
- **THEN** crew posts batch 13's card on deneb, its summary saying an older copy was lost

#### Scenario: Read on another host
- **WHEN** the rail is read on a host where the row's owner does not run while its card is held on mac-studio
- **THEN** that read posts no card for the row

#### Scenario: The batch no longer waits
- **WHEN** batch 13's card is held on mac-studio and every unit batch 13 holds has landed
- **THEN** no card of batch 13 is posted on deneb

#### Scenario: The proposal no longer waits
- **WHEN** proposal 13's card is held on mac-studio and proposal 13 was approved since
- **THEN** no card of proposal 13 is posted on deneb

### Requirement: A record's card its owner's host can't reach is raised again there
A decision record's card has no rail row and is raised in the design agent's name on the main level's host. When the design agent's newest card under a record's key was posted from another host and no close ends it, or was lost to it on any host, no newer card of the design agent's is under the key, and the record's last status crew recorded is proposed and not settled in the pane, the rail's next read on the main level's host SHALL post the record's card again there under `record/<kit>/<number>`, built from the record as the kit's main holds it, its summary opening with the words that say an older copy was lost.

#### Scenario: A record's card left on the host the main level left
- **WHEN** record 21 in atlas-kit was raised from mac-studio with no alternatives, is still proposed, the main level now runs on deneb, and the rail is read on deneb
- **THEN** crew posts record 21's card again on deneb under `record/atlas-kit/0021` in wldn-design's name, built from the record on atlas-kit's main, its summary opening with the words that say an older copy was lost, and the rail lists the new card under the decision records

#### Scenario: A record settled since
- **WHEN** record 21's card is held on mac-studio and `crew record atlas-kit 21 --accepted` was recorded since
- **THEN** no card of record 21 is posted on deneb

### Requirement: A record raised with alternatives is raised again by its command
`crew record --proposed` SHALL record on its `record.proposed` entry whether the card it raised offered alternatives, keeping none of the file's words. A stranded record card raised with alternatives SHALL NOT be posted again by the rail's read, since crew keeps no copy of the alternatives file: the read SHALL say so, naming `crew record <kit> <number> --proposed --alternatives <file>` for the design agent; and `crew record --proposed`, run while its record's card is stranded so, SHALL post the card saying an older copy was lost.

#### Scenario: A record raised with alternatives
- **WHEN** record 32's card was raised from mac-studio with `--alternatives`, the main level now runs on deneb, and the rail is read on deneb
- **THEN** no card is posted, and the read names `crew record switchboard-kit 32 --proposed --alternatives <file>` for wldn-design

#### Scenario: The command raises it
- **WHEN** wldn-design then runs `crew record switchboard-kit 32 --proposed --alternatives alternatives.md` on deneb
- **THEN** the card is posted on deneb as a choice, its summary opening with the words that say an older copy was lost

### Requirement: A row that can land is a box, ticked as crew proposes
With two to five rows that can land, a landings card SHALL be one list of those rows in order, each ticked as crew proposes, labelled with its place and its bolt, its detail what the row carries, its consequence its forecast; with six or more, lists of five at most, in order, each a question. Clearing a box SHALL leave that bolt waiting. The face SHALL say one send lands the ticked bolts in the order shown and a note may move one.

#### Scenario: Three bolts
- **WHEN** `y`, `z` and `w` of crew read proven in that order
- **THEN** `land/crew` is one list of three ticked boxes, `1. y`, `2. z`, `3. w`, and its summary says the send lands the ticked ones in that order

#### Scenario: Seven bolts
- **WHEN** seven bolts of crew read proven
- **THEN** `land/crew` holds two lists, of four and three, in order, and a change to its rows while it waits withdraws it and posts its new form following it, since Pending You changes no card's questions

### Requirement: The landings card forecasts each row's conflicts
Each row SHALL carry the conflicts crew forecasts when its bolt is merged onto the kit's main and onto each bolt above it on the card, from their merge base, naming the files and the bolt or main each is with, or saying none is forecast. A forecast crew cannot make SHALL be said on its row with why, and SHALL hold nothing. Forecasts SHALL be made again whenever the card is raised or changed, and whenever the kit's main moves while the card is open, against GitHub's main after a fetch and each bolt where it lives.

#### Scenario: Two bolts touch one file
- **WHEN** `y` and `z` of crew are rows in that order, and both change `plugin/lib/plan.py`'s same lines
- **THEN** `z`'s row says it is forecast to conflict with `y` on `plugin/lib/plan.py`, and `y`'s row says no conflict is forecast

#### Scenario: A bolt behind main
- **WHEN** main has landed a change to `README.md` that bolt `y` also changes
- **THEN** `y`'s row says it takes main first, forecast to conflict with main on `README.md`

#### Scenario: A bolt branch crew cannot read
- **WHEN** bolt `y` was made before gives went through sluice and its branch is on no host crew can read it from
- **THEN** `y`'s row says its forecast could not be made and why, and `y` keeps its box

#### Scenario: Main moves under an open card
- **WHEN** `land/crew` is open with `y` as a row forecast against main at `a1b2c3d`, and the rail is read on the main level's host once crew's checkout of the kit reads GitHub's main, as last fetched, at `e4f5a6b`
- **THEN** crew raises `land/crew` again, fetching GitHub's main and forecasting `y` against `e4f5a6b`

#### Scenario: Main has not moved
- **WHEN** `land/crew` is open with its rows forecast against `a1b2c3d`, and the rail is read with GitHub's main still at `a1b2c3d`
- **THEN** the read raises no landings card and fetches nothing for it

### Requirement: A refused landing is held on its row
A bolt whose landing sluice refused for its own content, its submission in conflict or blamed for a check that ran and failed, SHALL be held on its row at that head, with no box, the row saying sluice's words and that it waits for its team's fix, while the bolts after it go on. Once its head moves and it reads proven, it SHALL land on the user's send that ticked it when that send still stands for its work, and SHALL otherwise have a box again. A landing that did not land for any other cause SHALL NOT hold its row.

#### Scenario: The second of three is refused
- **WHEN** the user sends `land/crew` with `y`, `z` and `w` ticked, and sluice refuses `z` for a conflict on `plugin/lib/plan.py`
- **THEN** `y` and `w` land, `z` stays on crew's landing row held, saying sluice's words and that it waits for its team's fix, and the next landings card raised carries `z` held with no box

#### Scenario: A check fails
- **WHEN** sluice blames `z`'s landing for `tests:logic`, which ran and failed
- **THEN** `z` is held on its row with no box, saying sluice's words and that it waits for its team's fix

#### Scenario: The fix merges
- **WHEN** `z`'s team's take-main fix merges into `z` and `z` reads proven at its new head, its own work unchanged since the user's send
- **THEN** `z` has no box on any landings card and lands on that send

#### Scenario: A fix that changes the bolt's work merges
- **WHEN** `z` was refused for a failed check, and its team's fix commits a change and merges, and `z` reads proven at its new head
- **THEN** `z` has a box on `land/crew` again, its note naming the fix's commit

### Requirement: The landings card closes when nothing waits
A landings card the user has answered SHALL be left as it is until every bolt they ticked has landed or been held, then closed naming what landed and where GitHub's main holds it, what was held and why, and what was left; a new card SHALL follow it while rows can land. The close SHALL keep the user's send for each ticked bolt that was held and still stands for its work, saying so. A send ticking none SHALL close it, landing nothing. With no row that can land, no card SHALL be open, and the next proven bolt SHALL raise one, following nothing.

#### Scenario: Everything ticked lands
- **WHEN** the user sent `land/crew` with `y` and `z` ticked and both land
- **THEN** the card is closed saying `y` and `z` landed and where GitHub's main holds them, and no landings card of crew is open

#### Scenario: One left out
- **WHEN** the user sent `land/crew` with `y` ticked and `z` cleared, and `y` lands
- **THEN** the card is closed saying `y` landed and `z` was left, and a new card follows it with `z` as its one row

#### Scenario: The next proven bolt
- **WHEN** no landings card of crew is open and bolt `w` reads proven
- **THEN** `land/crew` is posted with `w` as its one row, following no card

#### Scenario: A ticked bolt held at the close
- **WHEN** the user sent `land/crew` with `y` and `z` ticked, `y` lands and sluice refuses `z`
- **THEN** the card is closed saying `y` landed and `z` was held and why, and that the send stands for `z`: it lands once its team's fix has only taken main in and sluice has proven it, with nothing asked

### Requirement: A bolt's own landing card gives way to its kit's
An open landing card under `land/<bolt>`, in a conductor's name, SHALL be withdrawn by the rail's sweep on the team's host, saying the bolt is now a row of its kit's landings card, and that card SHALL be raised for the bolt. crew SHALL raise no card under `land/<bolt>`. A bolt SHALL NOT be added to the plan under a name that is a kit's of its partition.

#### Scenario: A card from before
- **WHEN** swc-1-conductor holds an open card under `land/y`, raised before this change, and the rail is read on swc-1's host
- **THEN** that card is withdrawn saying `y` is now a row of crew's landings card, and `land/crew` holds `y`

#### Scenario: A bolt named as a kit
- **WHEN** a proposal adds a bolt named `crew` to swancloud's plan, whose teams build the kit crew
- **THEN** its approval is refused, naming the kit, and nothing is written

### Requirement: A ticked bolt's approval stands while its own work is unchanged
The user's send on a kit's landings card SHALL stand for each bolt they ticked, at any later head whose own work is the same as at the head they ticked. A bolt's own work SHALL be the non-merge commits its head holds that GitHub's main does not. A bolt whose send stands SHALL be no row of any later landings card, and SHALL land on that send once it reads proven at its new head, with no card asking for it.

#### Scenario: A refused bolt takes main in
- **WHEN** the user sent `land/crew` with `z` ticked at `abc1234`, sluice refused `z` for a conflict with main, and `z`'s team's take-main fix, resolving the conflict in its merge, merged into `z`, which reads proven at `def5678`
- **THEN** no landings card asks for `z`, and `crew card read land/crew` names `z` among the bolts the user's earlier send lands, with the `crew bolt submit` that lands it

#### Scenario: The head moves by taking main in before the landing
- **WHEN** the user sent `land/crew` with `y` and `z` ticked, `y` is landing, and a take-main fix moves `z`'s head before ops submits it
- **THEN** the card is left as it is, and once `z` reads proven at its new head it lands on the same send

#### Scenario: The host's copy is brought level
- **WHEN** the user ticked `z` at the host copy's head `abc1234`, and the copy is brought level with GitHub's `def5678`, whose merges bring in only main's commits
- **THEN** the send stands for `z` at `def5678`

#### Scenario: Two take-main fixes in a row
- **WHEN** the user ticked `z` at `abc1234`, and two take-main fixes later `z` reads proven at `0a1b2c3`, holding the same commits of its own as at `abc1234`
- **THEN** the send stands for `z` at `0a1b2c3`

### Requirement: A ticked bolt whose own work changed is asked again, saying what changed
A bolt the user ticked whose head now holds commits of its own the ticked head did not, or lacks some it held, SHALL be a row of the next landings card, and that card SHALL say the head the user sent, the head now, and the subjects of the commits gained and lost, five at most, with how many more. A bolt whose own work crew cannot compare SHALL be asked again the same way, the card saying why crew could not tell.

#### Scenario: A fix adds a commit
- **WHEN** the user ticked `z` at `abc1234`, and a fix that commits `fix: keep the lease` merges into `z`, which reads proven at `def5678`
- **THEN** `z` is a row of the card that follows, and its note says `z`'s head is now `def5678`, with work of its own since the user's send at `abc1234`: `fix: keep the lease`

#### Scenario: A take-main fix that also commits a change
- **WHEN** the user ticked `z` at `abc1234`, and its take-main fix merges main and then commits `test: wait for the new lock`
- **THEN** `z` is asked again, the card naming `test: wait for the new lock`

#### Scenario: crew cannot compare the heads
- **WHEN** the user ticked `z` at `abc1234`, `z` reads proven at `def5678`, and GitHub's main cannot be fetched where the kit's forecasts are made
- **THEN** `z` is asked again, and the card says crew could not tell whether `z`'s own work changed since the send, in git's words

### Requirement: A card that follows one the user answered says so first
Every card crew posts that follows a card the user answered SHALL open its summary, and its details, with one paragraph saying that the user answered the earlier card, when the earlier card was posted and by when crew recorded their answer, what they answered, and what has changed since, before anything else the card says, so a card asked again is never read as a repeat. A card the user answered is one the run record shows closed after their answer, declined among them, and one whose follow-on crew withheld (below). What they answered SHALL be the answer crew recorded at the earlier card's close; where the run record holds none, the paragraph SHALL say crew holds no record of what they answered. What changed SHALL be the sentences the event that raised the card gives: a record's new commit; a proposal's rewrite read against the proposal it replaces; a deploy's newer head; a step's place after the card it follows; what the user's send on a kit's landings card landed, held and left, and the bolts proven or moved since.

#### Scenario: A record revised after the user's note
- **WHEN** the user answered record 0019's card `req_1`, posted 2026-10-23 13:10 UTC, with a note, crew recorded it by 14:02 UTC, and the design agent revises the record at `4be21c0`
- **THEN** the card that follows `req_1` opens "You answered the card before this one, posted 2026-10-23 13:10 UTC, by 14:02 UTC: declined, with a note. Since then: revised at 4be21c0", with the commit's subject, before the record's own opening

#### Scenario: A proposal rewritten after the user's note
- **WHEN** the user answered proposal 239's card with a note and the planner rewrites it as proposal 241, which adds unit `x` and no longer adds unit `y`
- **THEN** the card that follows says first what the user answered and that proposal 241 adds `x` and no longer adds `y`

#### Scenario: A deploy offered again after the user declined it
- **WHEN** the user declined deneb's deploy of `ddcf2cb` and the deployer offers deneb `e104bcf`
- **THEN** the new deploy card follows the declined one and opens saying the user declined `ddcf2cb`, when, and that the offer is now `e104bcf`

#### Scenario: The landings card after a send that left a bolt
- **WHEN** the user sent `land/crew` with `y` ticked and `z` cleared, and `y` lands
- **THEN** the card that follows opens saying the user sent the earlier card, when, ticking `y` and leaving `z`, and that `y` landed and `z`, which they left, waits on this card

#### Scenario: An answer crew holds no record of
- **WHEN** a card that follows one the user answered is posted, and the run record's close of the earlier card holds no answer, as a close made before crew recorded answers
- **THEN** its opening says the user answered the earlier card, when, that crew holds no record of what they answered, and what changed since

### Requirement: A follow-on with nothing changed is not posted, the earlier answer standing
A card that follows one the user answered, for which the event that raised it gives nothing changed since the answer, SHALL NOT be posted: crew SHALL record it as a `card.post` under the row's key in its owner's name, refused in crew's own words naming the earlier card and saying its answer stands, with that card's id and the state `stands`, and SHALL refuse nothing of the event. The rail's card line SHALL show those words, and the rail's sweep SHALL NOT raise that row's card again; the next post under the row's key SHALL follow the card whose answer stands and SHALL be posted only when its event gives what changed since.

#### Scenario: A proposal rewritten with nothing changed
- **WHEN** the user answered proposal 239's card and the planner rewrites it as proposal 240 with the same commands and the same case
- **THEN** no card is posted for proposal 240; the run record has a `card.post` under the proposal's key, refused in crew's words naming 239's card and saying its answer stands, state `stands`; and `crew rail` shows the row with those words

#### Scenario: A deploy offered again at the head the user declined
- **WHEN** the user declined deneb's deploy of `ddcf2cb` and the deployer offers deneb `ddcf2cb` again with the same notes and steps
- **THEN** no card is posted, and the decline stands

#### Scenario: The sweep meets a withheld card
- **WHEN** proposal 240's card was withheld and the rail is read on the planner's host
- **THEN** the sweep raises no card for proposal 240's row, and records nothing more

#### Scenario: Something changes after a withheld card
- **WHEN** proposal 240's card was withheld and the planner rewrites it as proposal 242, which adds unit `w`
- **THEN** proposal 242's card is posted following 239's card, opening with what the user answered on it and that proposal 242 adds `w`

### Requirement: The close of an answered card records the answer
When crew closes one of its own cards that the user answered, it SHALL record on the close's entry what they answered as `Answer`, in crew's own words made from names alone: approved or declined; the options they picked, by the bolt, unit or choice each names; done, a failed step, or that they will handle it themselves; and "with a note" when they wrote one, never the note's words (`record.3`). A card answered in a conversation, closed as answered there, SHALL record that it was answered in a pane.

#### Scenario: A landings card sent with ticks
- **WHEN** the user sends `land/crew` with `land:y` ticked, `land:z` cleared and a note, and crew closes it
- **THEN** the close's entry holds `Answer: ticked y, left z, with a note`, and none of the note's words

#### Scenario: A deploy declined
- **WHEN** the user declines deneb's deploy card with the words "not tonight" and crew closes it
- **THEN** the close's entry holds `Answer: declined, with a note`

### Requirement: A row forecast to conflict with main takes main first
A row whose bolt is forecast to conflict with what the kit's main holds, by the card's forecast or by one a conductor's wait recorded at the bolt's present head, SHALL be held with no box, saying it takes main first, the files, and that its team takes main in by a fix. It SHALL NOT be offered to land, and SHALL have a box again once the bolt reads proven at a new head with no conflict forecast. A conflict only with a bolt above it holds nothing. A row whose bolt the user left SHALL NOT be held so: it keeps its box and says it would take main first, as "A row the user left says whether it would take main first" has it.

#### Scenario: Main landed a change the bolt also made
- **WHEN** `y` reads proven and main has landed a change to `openspec/specs/artifact-buckets/spec.md` that `y`'s own archive also changed
- **THEN** `land/crew` holds `y` with no box, saying `y` takes main first, forecast to conflict with main on `openspec/specs/artifact-buckets/spec.md`, and that its team takes main in by a fix

#### Scenario: A wait found it first
- **WHEN** a conductor's wait recorded `y` forecast to conflict with main at `y`'s present head, and the card's own forecast against main could not be made
- **THEN** `y` is still held taking main first, in the recorded files

#### Scenario: Only a bolt above it
- **WHEN** `z` is forecast to conflict with `y`, the row above it, and with nothing on main
- **THEN** `z` keeps its box, its row naming the conflict with `y`

#### Scenario: The fix merges
- **WHEN** `y`'s take-main fix merges and `y` reads proven at its new head with no conflict forecast against main
- **THEN** `y` has its box on `land/crew` again

#### Scenario: A bolt the user left
- **WHEN** the user cleared `z` on their send of `land/crew`, and main then lands a change `z` also makes
- **THEN** `z` keeps its box on the card that follows, unticked, and is not held taking main first

### Requirement: A take-main fix holds its row as taking main first
A fix in flight on a bolt whose words begin "Take main into the bolt" SHALL hold the bolt's row with no box, saying it takes main first and naming the fix and its words.

#### Scenario: The conductor started the fix
- **WHEN** swc-1-conductor starts `take-main-e4f5a6b` on `y` with "Take main into the bolt: it is forecast to conflict on README.md"
- **THEN** `land/crew` holds `y`, saying it takes main first, `take-main-e4f5a6b` taking main in: "Take main into the bolt: it is forecast to conflict on README.md"

### Requirement: A row taking main first changes the card in place
When a row comes to take main first while its card waits on the user, crew SHALL change the card in place saying which bolt takes main first and why, as for any row held, following it instead only when the card's form must change; a card left with no row that can land SHALL be withdrawn saying why.

#### Scenario: One of two
- **WHEN** `land/crew` waits with `y` and `z` as boxes, and main moves so that `z` is forecast to conflict with it
- **THEN** the card is followed by one with `y` as its one box and `z` held taking main first, since a list of two becomes an approval of one

#### Scenario: One of three
- **WHEN** `land/crew` waits with `y`, `z` and `w` as boxes, and main moves so that `w` is forecast to conflict with it
- **THEN** the card is changed in place, its change note saying `w` takes main first and why, `y` and `z` still ticked

### Requirement: A send stands for a ticked bolt taking main in
When the user has sent a landings card with a bolt ticked, and that bolt then takes main first, by a forecast or a take-main fix in flight, crew SHALL keep the send standing for it: the card SHALL be left, and SHALL NOT be closed counting that bolt as held, while it takes main in.

#### Scenario: Ticked, then forecast to conflict
- **WHEN** the user sent `land/crew` with `y` ticked, and before ops submits it main moves so that `y` is forecast to conflict with it
- **THEN** `land/crew` is left as it is, its send still standing for `y`, and `y`'s conductor is told the take-main fix

#### Scenario: Ticked beside one that lands
- **WHEN** the user sent `land/crew` with `y` and `z` ticked, `z` lands, and `y` takes main first
- **THEN** `land/crew` is left as it is while `y` takes main in, and is not closed saying `y` was held

### Requirement: A landing sluice or its host stopped keeps its box
A bolt whose landing did not land for a cause that is not its own content (sluice itself failing, a refusal or answer with no conflict or failed check in sluice's record, checks the host could not run, a withdrawal, or an outcome crew can't tell) SHALL keep its box and the user's word it has. Its row SHALL say what stopped the landing at that head, that it was nothing of the bolt's, and that main-level ops submits it again once that is cleared.

#### Scenario: Checks that never ran
- **WHEN** the user sent `land/crew` with `z` ticked, and sluice's record has `z`'s submission failed with every required check left without a result, the host unable to run them
- **THEN** `z` is not held: `land/crew` is left as the user answered it, `crew card read land/crew` names `z` as still landing on their send, saying what stopped it, with the command that lands it, and no new card asks for `z`

#### Scenario: sluice itself fails
- **WHEN** `crew bolt submit z` ends with sluice exiting 3 and main not holding `z`, and sluice's record of the submission has it neither in conflict nor blamed for a check that ran
- **THEN** `z` keeps its box at that head, and its row says sluice itself failed, in sluice's words, and that ops submits it again once that is cleared

#### Scenario: A new card while it is stopped
- **WHEN** `z`'s landing was stopped and a card of crew's landings follows the one the user answered
- **THEN** the closed card's outcome names `z` as still landing on their send with what stopped it, and the card that follows does not ask for `z` again

#### Scenario: The head moves
- **WHEN** `z`'s landing was stopped at `abc1234` and `z`'s head moves to a new head that reads proven
- **THEN** `z`'s row says nothing of the stop

### Requirement: A bolt the user left stays left until they tick it
A bolt SHALL be left when the user cleared it on their send of its kit's landings card, or when main-level ops recorded the user's words in its pane stopping its landing. It SHALL stay left, shown unticked on each card that follows, until the user ticks it on a later send or ops lands it on the user's words, or until its head moves. crew SHALL move no left bolt's head: it starts no take-main fix for it while it is left.

#### Scenario: Cleared on a send
- **WHEN** the user sends `land/swancloud` with `x` ticked and `builds-reach-the-phone` cleared
- **THEN** `builds-reach-the-phone` is left, and the card that follows shows it unticked

#### Scenario: Left again
- **WHEN** the user sends the card that follows with `builds-reach-the-phone` cleared again
- **THEN** it stays left, unticked on the next card

#### Scenario: Main moves under it many times
- **WHEN** main moves five times while `builds-reach-the-phone` is left, each move conflicting with it
- **THEN** no take-main fix is started for it, its head stays where it was, and it stays left on the card, asked for no more than any other row

#### Scenario: Its head moves
- **WHEN** a fix its conductor started for a defect merges into a left bolt and it reads proven at the new head
- **THEN** it is no longer left, and the card asks for it as a row at its new head

### Requirement: A row the user left says whether it would take main first
Each row of a bolt the user left SHALL be forecast against main whenever the card is raised, as every row is, and SHALL keep its box. When its forecast against main finds a conflict, the row SHALL say it would take main first if ticked, on which files and at which revision of main, and that its team takes main in by a fix once it is ticked, the user's send standing through it; otherwise it SHALL say it lands clean. When the forecast first finds such a conflict at the bolt's head and main's revision while a card waits on the user, crew SHALL change the card in place saying so; the same forecast SHALL NOT change the card again.

#### Scenario: Left, and main conflicts with it
- **WHEN** `z` is left on `land/crew`, waiting on the user, and main moves to `e4f5a6b`, landing a change to `README.md` that `z` also makes
- **THEN** `land/crew` is changed in place, its note saying `z`, which they left, would take main first, forecast to conflict with main on `README.md` at `e4f5a6b`; `z` keeps its box, its row saying it would take main first once ticked; and nothing is told to `z`'s conductor

#### Scenario: Raised again at the same heads
- **WHEN** the card is raised again and neither `z` nor main has moved
- **THEN** the card is not changed for it

#### Scenario: Left and clean
- **WHEN** `z` is left and its forecast against main finds no conflict
- **THEN** its row says no conflict is forecast

### Requirement: Ticking a left bolt that conflicts with main starts its take-main fix
When the user ticks a bolt they had left on a send of its kit's landings card, crew SHALL act on the send when ops reads it: a forecast conflict with what main has landed SHALL hold the bolt's row as taking main first, its conductor SHALL be told the take-main fix then, once, and the user's send SHALL stand for it through the fix. The bolts the read of the send gives ops to land SHALL leave it out, saying it takes main first and that the send stands for it.

#### Scenario: Ticked after being left
- **WHEN** `z` was left on `land/crew` and forecast to conflict with main on `README.md`, and the user sends the card with `z` ticked
- **THEN** `crew card read land/crew` holds `z` taking main first, swc-1-conductor is told `crew fix swc-1 take-main-e4f5a6b "Take main into the bolt: it is forecast to conflict on README.md"`, and the read leaves `z` out of the command that lands, saying it takes main first and that the user's send stands for it

#### Scenario: The fix merges
- **WHEN** `z`'s take-main fix merges and `z` reads proven at its new head
- **THEN** `z` lands on that same send, with nothing asked

#### Scenario: Ticked and clean
- **WHEN** `z` was left, its forecast against main finds no conflict, and the user ticks it
- **THEN** the read gives `z` to land in the command, as any ticked bolt

### Requirement: A bolt stopped in ops's pane is shown as left
A bolt whose landing main-level ops recorded the user's words stopping SHALL be shown on its kit's landings card unticked, as a bolt the user left, at the head it had when the stop was recorded, and SHALL be treated as left until the user ticks it on a send or ops lands it on their words.

#### Scenario: Stopped, then the card is raised
- **WHEN** ops records the user's words stopping `z`'s landing, and `land/crew` is raised
- **THEN** `z`'s row is unticked, the card's note says `z` was stopped on the user's words, and no take-main fix is started for it

#### Scenario: Ticked after a stop
- **WHEN** the user then ticks `z` on a send of `land/crew`
- **THEN** `z` is no longer left, and lands on that send or takes main first as any ticked bolt

### Requirement: A landing row carries what brings its bolt's preview up
Where the kit's policy at a bolt's head declares `[preview]`, the bolt's row on its kit's landings card SHALL carry what brings the preview up, the bolt's branch and its head, and SHALL say that the preview comes up only when the user asks for it on the card and goes when they are done. Where the policy declares none, the row SHALL say "no preview". crew SHALL ask sluice for nothing when it posts or changes the row.

#### Scenario: A kit that declares a preview
- **WHEN** bolt `y` reads proven at head `abc1234` in a kit whose policy at `abc1234` declares `[preview]`
- **THEN** `y`'s row on `land/crew` names `bolt/y` at `abc1234` as what brings its preview up, says to write on the card to bring it up, and sluice on the team's host lists no preview of `abc1234`

#### Scenario: A kit that declares none
- **WHEN** bolt `y` reads proven in a kit whose policy at its head has no `[preview]` table
- **THEN** `y`'s row says "no preview", and sluice is asked for nothing

#### Scenario: The policy can't be read
- **WHEN** the kit's policy at `y`'s head can't be read on the team's host
- **THEN** `y`'s row says its preview can't be told and why, and `y` keeps its box

#### Scenario: Approved without a preview
- **WHEN** the user sends `land/crew` with `y` ticked and never asked for its preview
- **THEN** main-level ops lands `y` as for any ticked row, and no preview of `y` was made

### Requirement: The user asks for a preview by writing on the card
A card that carries a thing that must run SHALL say, in its words, that the user brings it up by writing on the card naming it, and puts it away by writing that they are done. The card's owner, woken by the user's words, SHALL run `crew card preview <key> <thing>` to bring it up and `crew card preview <key> <thing> --done` to release it, `<thing>` a landings row's bolt or a batch line's `<unit>/<name>`. No card SHALL ask the user to run a command.

#### Scenario: The user asks on the landings card
- **WHEN** the user writes "bring up y's preview" on `land/crew` while it waits on them
- **THEN** swancloud-ops is woken, runs `crew card preview land/crew y`, and the card stays open waiting on the user's send

#### Scenario: A thing the card does not carry
- **WHEN** `crew card preview land/crew w` is run and `w` is no row of `land/crew`
- **THEN** crew refuses, naming the rows that carry a preview, and asks sluice for nothing

#### Scenario: Asked by anyone but the owner
- **WHEN** a conductor runs `crew card preview land/crew y`
- **THEN** crew refuses, naming swancloud-ops as the card's owner

### Requirement: A preview asked for from a card is brought up through sluice and listed while it is up
`crew card preview` SHALL bring the thing up with `sluice preview <branch> <revision>` on the host where its kit's work is, as the row or line names them, and SHALL change the card in place listing each address sluice names, under the name sluice gives it, while the preview is up. Asked again while one is up or coming up at the same revision, crew SHALL give it back and make no second.

#### Scenario: Brought up
- **WHEN** swancloud-ops runs `crew card preview land/crew y` with `y`'s row at `abc1234`, and the kit's policy names addresses `web` and `api`
- **THEN** sluice is asked for a preview of `bolt/y` at `abc1234` on `y`'s team's host, and `land/crew` is changed in place, its note saying `y`'s preview is up, `y`'s row listing `web` and `api` with sluice's addresses and saying a preview lands nothing

#### Scenario: Asked twice
- **WHEN** `crew card preview land/crew y` is run again while `y`'s preview of `abc1234` is up
- **THEN** sluice gives back the same preview, and `y`'s row lists the same addresses

### Requirement: A preview is released on the user's done and when its card or row ends
crew SHALL release a preview it brought up from a card when the owner runs `--done` on the user's word, when the card closes, when the bolt lands, is held for a fix or is dropped, and when the row or line that carries it leaves the card; and the card, while it waits, SHALL say it was released. A rail read SHALL release, on each host, a preview crew brought up whose card is closed or whose row is gone. crew SHALL release only a preview it asked for.

#### Scenario: The user is done
- **WHEN** the user writes "done with y's preview" on `land/crew` and swancloud-ops runs `crew card preview land/crew y --done`
- **THEN** `y`'s preview is released on the team's host, and `y`'s row again names `bolt/y` at its head and says to write on the card to bring it up

#### Scenario: The bolt lands with its preview up
- **WHEN** `crew bolt land y` closes `y` while its preview is up
- **THEN** the preview is released on the team's host, and `sluice previews` there no longer lists it

#### Scenario: A fix holds the landing
- **WHEN** a fix started on bolt `y` holds its row while its preview is up
- **THEN** the preview is released, and none is asked when `y` reads proven again

#### Scenario: A preview crew did not ask for
- **WHEN** a person previewed an earlier revision of `bolt/y` themselves, and `y` later lands
- **THEN** crew releases only the preview it brought up, and leaves the person's preview as it is

#### Scenario: A card closed elsewhere
- **WHEN** `land/crew` is closed with no crew command closing it while `y`'s preview is up, and the rail is read
- **THEN** the sweep on `y`'s team's host releases the preview, and says so

### Requirement: A moved head releases the preview of the old one and asks for none
When a merge moves a bolt's head while it is a row of its kit's landings card, crew SHALL change the row in place to name the new head as what brings the preview up, SHALL release a preview it brought up at the old head, and SHALL say so on the row; it SHALL ask for no preview at the new head until the user asks again.

#### Scenario: The head moves with a preview up
- **WHEN** a fix's merge moves bolt `y`'s head from `abc1234` to `def5678` while `y`'s preview of `abc1234` is up
- **THEN** `abc1234`'s preview is released, `y`'s row names `bolt/y` at `def5678` and says its preview of `abc1234` was released as the head moved, and sluice lists no preview of `def5678`

### Requirement: A batch's card carries what each unit's stages recorded as made
A batch's card SHALL carry, under each unit, every line its stages recorded as made, named by the stage that recorded it, each with its name, what it is and its address or its branch and revision, exactly as the run wrote them. crew SHALL make, check and rewrite none of it. A unit whose stages recorded nothing SHALL carry no such line and no word of one.

#### Scenario: A spike recorded by a code stage
- **WHEN** unit `a`'s code stage recorded `{"name": "spike", "kind": "page", "address": "https://example.test/spike"}` and `a` is in batch 7
- **THEN** batch 7's card names, under `a`, the code stage's `spike`, a page, at `https://example.test/spike`, as written

#### Scenario: A thing that must run
- **WHEN** unit `a`'s code stage recorded `{"name": "demo", "kind": "preview", "branch": "bolt/y", "revision": "abc1234"}`
- **THEN** batch 7's card names under `a` the `demo` preview, brought up from `bolt/y` at `abc1234`, says to write on the card to bring it up, and lists no address

#### Scenario: A line crew cannot read as a made thing
- **WHEN** a line of `a`'s is not a JSON object naming a name and what it is
- **THEN** the card carries the line's text as written, saying crew could not read it as a made thing, and the card is raised all the same

#### Scenario: Nothing recorded
- **WHEN** no stage of unit `b` recorded anything as made
- **THEN** batch 7's card says nothing of made things under `b`

### Requirement: A batch's card changes in place as lines are added
When a stage of a unit in a batch whose card waits on the user records a line its card does not yet carry, crew SHALL change that card in place, its note naming the unit and the line's name. A card the user has answered SHALL be left as it is.

#### Scenario: A line added while the card waits
- **WHEN** batch 7's card waits on the user and unit `a`'s code stage, still running, records a page `notes`
- **THEN** batch 7's card is changed in place with a note that `a` recorded `notes`, and carries it under `a`

#### Scenario: A line added after the user answered
- **WHEN** the user has answered batch 7's card and `a`'s stage records another line
- **THEN** batch 7's card is left as it is

### Requirement: A card about a landed revision carries its commit and no preview
A card about a revision that has landed, a deploy's card and the close of a landings card's row that landed, SHALL carry the commit it landed as, and SHALL carry no preview and no word of bringing one up.

#### Scenario: A deploy's card
- **WHEN** main's head `9f8e7d6` is offered to `prod`
- **THEN** `deploy/prod`'s card names `9f8e7d6`, and carries no preview, no branch to bring one up and no word of one

#### Scenario: A landed row
- **WHEN** `y` lands on GitHub's main as `1a2b3c4` and its card closes
- **THEN** the close names `1a2b3c4` as the commit it landed as, and says nothing of a preview
