# board-page Specification

## Purpose
The board view of crew's page: one partition's flow, read by `crew board`, drawn as the flywheel mockup draws its phases view; and the page's deploys view, each environment's deploys as a timeline.

## Requirements

### Requirement: Operation draws each environment's deploys as records
The board view's Operation lane SHALL draw, under each environment's name, its deploys and the operations waiting on it as the board reads them, each deploy a record stamped with where it stands, and each with its marker.

#### Scenario: An offer waiting on the user
- **WHEN** a deploy of mac-studio is offered and its card is open
- **THEN** Operation shows it under mac-studio, stamped as waiting on the user's word, with its ✓ marker saying the card is open

### Requirement: The deploys view
The page SHALL have a deploys view, one switch from the board and the flow, kept in its address, that draws each environment as a timeline of its deploys over the record's window, oldest first, each with the commit it moved from and to, the user's word on it as its card's answer recorded it (approved by whom and when, waiting, or replaced unanswered), its steps, the suite's checks and its outcome, the bolts it carried with the proposals the lineage joins to each as its release notes, and the after-deploy steps of its commit with their doers and states; then the operations waiting on it. It SHALL be read from the run record alone, and the page SHALL stay one self-contained file.

#### Scenario: What a deploy carried
- **WHEN** the deploy of mac-studio carried bolt b, whose unit came from proposal 3
- **THEN** the deploys view lists b under it with proposal 3 and the first line of its case

#### Scenario: The sequence of words
- **WHEN** one deploy of mac-studio was approved and done and a newer offer waits
- **THEN** the deploys view shows the approved one above the waiting one, each with its word

### Requirement: The page opens on the partition's board
`crew page <label>` SHALL embed the board of that one partition, as `crew board --label <label> --json` reads it, and the page SHALL open on a board view of it. The lineage view SHALL be one switch away in the page's header. The board SHALL come from the same read the page is made from, and the page SHALL say when that read was made.

#### Scenario: Opening the page
- **WHEN** the user opens the page `crew page swancloud` wrote
- **THEN** it shows swancloud's board, with the time it was read in its header and a switch to the lineage view

#### Scenario: A host did not answer
- **WHEN** the page is made while a host of the partition does not answer
- **THEN** the board's attention strip names that host, and the bolts on it show their units with their stages unknown

### Requirement: The board view draws four lanes in the mockup's forms
The board view SHALL draw the lanes Inception, Bolt plan, Construction and Operation, in that order, each object in the form the mockup's phases view gives its kind: a signal as a quote, a proposal as a sheet, a queued unit as a slip, a bolt as a ledger and a landed bolt as a record. Bolt plan SHALL be drawn as the hatched gate and Operation marked as observed. No object SHALL carry the name of its lane, and a lane with nothing in it SHALL say so.

#### Scenario: Nothing waiting in the plan
- **WHEN** the partition has no open proposal, no planned bolt and no queued unit
- **THEN** the Bolt plan lane is drawn as the gate and says it holds nothing

### Requirement: Inception shows the unmoved signals and the explorations
The Inception lane SHALL show each unmoved signal as a quote with a left rule, its first words, kind and age, under a counter for who captured it saying how many it holds and how old the oldest is; then each exploration as a row with its kit and first line.

#### Scenario: Two signals from a meeting
- **WHEN** wldn-planner captured two signals nothing has moved, the oldest three days ago
- **THEN** Inception shows a counter for wldn-planner saying 2 and 3 days, and each signal as a quote under it

### Requirement: Bolt plan shows sheets, planned ledgers and slips
The Bolt plan lane SHALL show each open proposal as a sheet with its number, who proposed it and the first line of its case, waiting on the user alone; each planned bolt as a ledger whose units are all queued; and each queued unit as a slip with its repository greyed before its name.

#### Scenario: A queued unit
- **WHEN** unit zone-two of switchboard-kit is in the queue
- **THEN** Bolt plan shows a slip naming zone-two with switchboard-kit greyed before it

### Requirement: Operation shows landings as records
The Operation lane SHALL show each bolt landed in the last seven days as a muted record, newest first, with a stamp saying when and by whom it landed, and its units.

#### Scenario: A landing
- **WHEN** wldn-ops landed bolt apex-zones two days ago
- **THEN** Operation shows apex-zones as a record stamped with that time and wldn-ops

### Requirement: Every decision is a marker on its object
Every marker the board's read gives SHALL be drawn on its object's form, never as a form of its own: ✓ for an approval (an open proposal, a bolt to land), ✎ for an answer (a verify report not yet answered), ! for attention (a held bolt every unit of which has landed). Each marker SHALL say whether its card is open and who asked it, and, when none is open and its last post was refused, that its post was refused, with Pending You's words where the marker is pointed at. The board view SHALL hold no button, link or command that answers or moves anything.

#### Scenario: A proposal waiting
- **WHEN** proposal 4 is open and wldn-planner has its card open
- **THEN** proposal 4's sheet carries ✓ and says its card is open, asked by wldn-planner, and nothing on the page approves it

#### Scenario: A deploy whose card was refused
- **WHEN** a deploy of deneb waits on the user's word and Pending You refused its card's last post
- **THEN** the deploy's marker says it has no card, its post refused, and pointing at it shows Pending You's words

### Requirement: The lanes fit a desktop and a phone, light and dark
On a window 760 px wide or wider, the four lanes SHALL sit side by side, Bolt plan narrowest and Construction widest. Under 760 px they SHALL stack one above the other in the same order, and nothing on the page SHALL run past the window's edge. The page SHALL follow the viewer's light or dark preference with the mockup's colours for each.

#### Scenario: On a phone
- **WHEN** the page is opened 390 px wide
- **THEN** Inception, Bolt plan, Construction and Operation are stacked in that order and the page does not scroll sideways

#### Scenario: In the dark
- **WHEN** the viewer's system prefers dark
- **THEN** the page uses the mockup's dark colours

### Requirement: The page stays one self-contained file
With the board view and the dock, the page SHALL still be one file that holds its own data, style and script and loads nothing: no font, script, style or image from anywhere. The one request it SHALL make is a dock's word, posted to the page's own address when the user sends it. It SHALL hold none of the mockup's sample data. Every text it shows from the state, in the lanes and in a dock, and every answer to a word, SHALL be set as text, never as markup.

#### Scenario: Offline
- **WHEN** the page is opened from disk with the network off
- **THEN** the board view and the lineage view draw in full and the browser makes no request

#### Scenario: A dock of typed words
- **WHEN** a signal's assertion holds `</script><b>here</b>` and the user opens its dock
- **THEN** the dock shows those characters as they are, and the page's data block is not ended by them

#### Scenario: Only the word is posted
- **WHEN** the served page is opened, a dock is opened, and a word is sent
- **THEN** the page's only request is one post to its own address's `word`, carrying the partition, key, agent and text

### Requirement: The header names every partition and links to its page
The page's header SHALL name every partition in the teams file, in its order, with the page's own partition marked as current. Each other partition SHALL be a link to that partition's page in the layout of this page's own file: `<label>.html` beside it when this page's file is named for its partition, `../<label>/` with the same file name when this page's folder is named for its partition, both when both are. When neither names its partition, the other partitions SHALL be named and not linked, and `crew page` SHALL say so. Before the partitions the header SHALL link to the fleet page in the same layout: `index.html` beside a page whose file alone is named for its partition, as the board is served, and `../page.html` from a page written as `page.html` in a folder named for its partition, as crew writes them; a page in any other layout SHALL have no link to the fleet page, since crew cannot tell where the fleet page is.

#### Scenario: Three partitions
- **WHEN** the teams file holds madswan, swancloud and wldn and `crew page swancloud` writes `~/.local/state/crew/swancloud/page.html`
- **THEN** the header links to the fleet page at `../page.html`, then shows madswan, swancloud marked as current, and wldn, and madswan links to `../madswan/page.html` and wldn to `../wldn/page.html`

#### Scenario: Pages written side by side as they are served
- **WHEN** `crew page swancloud --out <folder>/swancloud.html` writes the page, as swancloud's board asks for it
- **THEN** the header links to the fleet page at `index.html`, madswan links to `madswan.html` and wldn to `wldn.html`, so on the board served as `<label>.html` side by side each link opens that partition's page

#### Scenario: A folder and a file both named for the partition
- **WHEN** the page is written to `<folder>/wldn/wldn.html`
- **THEN** madswan links to `../madswan/madswan.html`, and the header has no link to the fleet page

#### Scenario: A page written where its layout names no partition
- **WHEN** `crew page wldn --out <folder>/board.html` writes the page
- **THEN** the header has no link to the fleet page and names madswan and swancloud without linking them, and `crew page` prints a line saying the other partitions are not linked because the page's file and folder are not named for wldn

### Requirement: Every item on the board opens its dock
A click on an item of the board view, or Enter on it, SHALL open that item's dock: a signal's quote, a proposal's sheet, a planned or started bolt's ledger, a unit's or chore's link in a chain or its queued slip, a fix's row, a landing's record, a deploy's record and a waiting operation's record. Each deploy of the deploys view SHALL open the same dock as its record on the board. Every item the page draws SHALL have a dock, and no team SHALL have one.

#### Scenario: A unit being built
- **WHEN** the user clicks unit a in tenant-environments' ledger
- **THEN** a dock opens titled a, saying it is a unit of bolt tenant-environments in code at 1 of 2 tasks, naming no slot

#### Scenario: Every item has its dock
- **WHEN** the page is written for a partition with a signal, a proposal, a planned bolt, a started bolt with a unit and a fix, a queued unit, a landing, a deploy and a waiting operation
- **THEN** every one of them carries the key of a dock the page holds, and no dock is a team's

#### Scenario: A deploy from either view
- **WHEN** the user opens the deploy of mac-studio from the Operation lane, and then from the deploys view
- **THEN** both open the same dock

### Requirement: The dock opens over the board and the board does not move
The dock SHALL be one panel over the right of the board, as the flywheel mockup's dock is: opening and closing it SHALL move, reflow or scroll nothing in the lanes. Esc, the dock's × or a click outside it SHALL close it, and the focus SHALL return to the item it was opened from. Under 760 px the dock SHALL fill the screen with a back control.

#### Scenario: Opened while scrolled
- **WHEN** the user has scrolled the Construction lane and opens a ledger's dock, then presses Esc
- **THEN** the lanes stay where they were throughout, and the dock is gone

#### Scenario: On a phone
- **WHEN** the page is 390 px wide and the user taps a slip
- **THEN** the dock fills the screen with a back control, and back shows the board as it was

### Requirement: A dock holds the item's details as the page's data and lineage hold them
A dock's head SHALL take its item's form, a proposal's a sheet's, a bolt's a ledger's, a queued unit's a slip's, a landing's and a deploy's a record's, with its kind, its name and a line of what it is. Its body SHALL hold the item's facts from the page's data, its markers in the board's own words, each item it is part of or holds, and its history from the run record's entries as `crew trace` walks it, newest last. Nothing in a dock SHALL be read beyond the read the page is made from.

#### Scenario: A signal's history
- **WHEN** the user opens the dock of signal 2026-10-12-x/01, captured by wldn-planner
- **THEN** the dock shows its whole assertion, its kind, who captured it and when, and its entries in the order `crew trace signals/2026-10-12-x/01` prints them

#### Scenario: A deploy's release notes
- **WHEN** the user opens the dock of a deploy of mac-studio that carried bolt b, whose unit came from proposal 3
- **THEN** the dock shows its commits from and to, the user's word on it, its steps and checks, and bolt b with proposal 3 and the first line of its case

#### Scenario: A fix
- **WHEN** the user opens the dock of a fix of tenant-environments that has not merged, at code as the runner's records give it
- **THEN** the dock says it has not merged, names its stage, and links its bolt

### Requirement: A dock links the items it names
Each item a dock names that the page draws SHALL be a link that opens that item's dock in its place, and the dock SHALL keep a trail: its back control SHALL return to the dock it was opened from. An item named that the page does not draw, such as an agenda item, SHALL be named as text.

#### Scenario: From a bolt to its unit and back
- **WHEN** the user opens tenant-environments' dock, follows unit a, then presses back
- **THEN** unit a's dock replaces the bolt's, and back shows the bolt's dock again

### Requirement: The dock answers nothing
A dock SHALL hold no control that answers a card or moves anything: it SHALL have no foot, and an item waiting on a decision SHALL carry its marker saying whether its card is open and who asked it, as the board does, the card being answered on the rail.

#### Scenario: A proposal waiting
- **WHEN** proposal 4 is open with its card open and the user opens its dock
- **THEN** the dock carries ✓ saying its card is open and who asked it, and holds no control that approves it

### Requirement: The open dock survives a reload
The dock open SHALL be kept in the page's address beside the view, so a reload, or the page written again over this one, opens the same item's dock. An item the page no longer holds SHALL leave the board shown with no dock open.

#### Scenario: The page is written again
- **WHEN** the user has unit a's dock open and reloads after the page was written again
- **THEN** the page opens with unit a's dock, its details as the new page holds them

#### Scenario: The item is gone
- **WHEN** the address names the dock of a bolt that has since landed and left the board
- **THEN** the page shows the board with no dock open

### Requirement: Every dock takes a word to its item's agent
Every dock SHALL end with a one-line field for a word to the item's agent, a Send control, and a line naming the agent it goes to and saying that a card is answered on the rail. A word SHALL be at most 1000 characters. A dock opened from a page read from disk SHALL say that a word is sent only from the served board, and SHALL send nothing.

#### Scenario: A unit's dock
- **WHEN** the user opens unit a's dock, a in started bolt tenant-environments
- **THEN** the dock ends with a field and Send, naming the partition's planner as who the word goes to and saying that a card is answered on the rail

#### Scenario: Opened from disk
- **WHEN** the page is opened from a file on disk and the user opens a dock
- **THEN** the dock says a word is sent only from the served board, and its field sends nothing

### Requirement: A word goes to the agent its item's kind names
The agent a dock's word goes to SHALL be decided from the item's kind: a bolt, a unit or chore, a fix, a proposal or a batch to the partition's planner; a signal or a record to its design agent; a landing, a deploy or an operation to its main-level ops; and a subscription or a partition to the partition's operator.

#### Scenario: Each kind's agent
- **WHEN** the page is written for wldn with a bolt in flight with a unit and a fix, a planned bolt, a proposal, a signal, a landing, a deploy, an operation and a subscription
- **THEN** the bolt, unit, fix, planned bolt and proposal go to wldn-planner, the signal to wldn-design, the landing, deploy and operation to wldn-ops, and the subscription to wldn-operator

### Requirement: A word reaches its agent as the user's tell from the board, naming the item
Sending a word SHALL post it, with the partition, the item's key and the agent, to the page's own address, whose listener hands it to `crew tell --board` on its standard input. crew SHALL check it and tell the agent `[crew tell from <user>@board] (on <kind> <name>) <text>`, `<user>` being the user the listener runs as, and record the tell with its length and never its text. On delivery it SHALL print `sent to <agent>` and exit zero.

#### Scenario: A word on a unit
- **WHEN** the listener running as chuck pipes `{"label": "wldn", "key": "unit:a", "to": "swb-1-conductor", "text": "Keep the zone check"}` to `crew tell --board`
- **THEN** swb-1-conductor is prompted with `[crew tell from chuck@board] (on unit a) Keep the zone check`, the command prints `sent to swb-1-conductor`, and the run record holds a tell of 31 characters, the length of what was typed after the mark, and not the words

#### Scenario: The agent reads it as the user's
- **WHEN** the conductor's transcript holds that word and it captures a signal from its words
- **THEN** the signal is asserted by the user

### Requirement: A word crew cannot deliver is said in the tell's words
When the tell itself is refused, its agent not up, waiting on a question in its pane, or on a host that does not answer, `crew tell --board` SHALL type nothing and exit non-zero, saying why on standard error in the tell's own words.

#### Scenario: An agent waiting on a question
- **WHEN** a word for swb-1-conductor is posted while swb-1-conductor waits on a question in its pane
- **THEN** nothing is typed, and the command exits non-zero saying swb-1-conductor is waiting on a question in its pane and nothing was sent

### Requirement: A word not of the board's form is refused
`crew tell --board` SHALL type nothing and exit non-zero, saying why on standard error, when the posted word is not one JSON object holding the partition, key, agent and text as strings; names no partition crew knows; has a key of no kind a dock has; names an agent its item's kind does not go to in that partition; or has a text that is empty, longer than 1000 characters or more than one line.

#### Scenario: An agent the kind does not go to
- **WHEN** a word on `proposal:4` is posted for swb-1-conductor
- **THEN** nothing is typed, and the command exits non-zero saying a word on a proposal goes to wldn-planner

#### Scenario: A word of two lines
- **WHEN** the posted text holds a line break
- **THEN** nothing is typed, and the command exits non-zero saying a word from the board is one line

### Requirement: The dock says what became of the word
After Send the dock SHALL say what the listener answered: on delivery, its words, such as `sent to swb-1-conductor`, and the field emptied; otherwise the listener's words, which are crew's refusal, with the word left in the field. When the listener does not answer, or answers with no words, the dock SHALL say the board's listener did not answer and nothing was sent. Send SHALL be disabled while a word is on its way.

#### Scenario: Delivered
- **WHEN** the user sends a word from unit a's dock and the listener answers 200 with `sent to swb-1-conductor`
- **THEN** the dock says `sent to swb-1-conductor` and the field is empty

#### Scenario: Refused
- **WHEN** the listener answers with crew's words that swb-1-conductor is waiting on a question in its pane
- **THEN** the dock shows those words, and the word stays in the field to send again

#### Scenario: No listener
- **WHEN** the post gets no answer
- **THEN** the dock says the board's listener did not answer and nothing was sent

### Requirement: A word from the board answers nothing
Words that reached an agent only in a tell from `<user>@board` SHALL NOT be taken as the user's words for landing a bolt, answering a batch or settling a record in a pane. crew SHALL refuse each, recording nothing, and say the words came from the board, which answers nothing, and where the user answers instead. The same words typed in the pane, or told from `<user>@<host>`, SHALL still be the user's.

#### Scenario: A landing asked from the board
- **WHEN** the user sends "Land bolt y" from bolt y's landing dock, and swancloud-ops runs `crew bolt submit y --excerpt "Land bolt y"`
- **THEN** nothing is submitted, and the command says the words came from the board, which answers nothing, and the user lands a bolt on its card or in the pane

#### Scenario: A batch answered from the board
- **WHEN** the user sends "Batch 14 is fine" from a dock, and the planner runs `crew card answer batch/14 --excerpt "Batch 14 is fine"`
- **THEN** batch 14 is not answered, and the command says the words came from the board

#### Scenario: Typed in the pane after the board
- **WHEN** the user sent "Batch 14 is fine" from a dock and then typed the same words in the planner's pane
- **THEN** `crew card answer batch/14 --excerpt "Batch 14 is fine"` records batch 14 answered

### Requirement: Construction shows each started bolt as a ledger with its chain
The Construction lane SHALL show each started bolt as a ledger: its head naming repository, bolt, and the host and stream its work runs in, as the runner that took it reported them; its units in plan order as a chain, each marked merged, building or queued, a building unit with its stage and tasks; and its fixes on a row of their own. No ledger SHALL name a team or a slot, nor a dev server until the runner reports a place's addresses.

#### Scenario: A started bolt being built
- **WHEN** bolt tenant-environments is started, the box's runner keeping its kit in stream wldn, with unit a in code at 1 of 2 tasks and unit b planned
- **THEN** Construction shows tenant-environments as a ledger headed by its repository, the box and stream wldn, with a as a building link of its chain saying code 1/2 and b as a queued link, and names no team or slot

### Requirement: A subscription's dock lists the main level's sessions on it
The Claude account a session of the partition's main level runs on SHALL have a dock on the partition's page, opened from the fleet page's subscription by the partition's link, which SHALL list the partition's sessions on that account, as the hosts file names them: each main-level agent on it, with its host and session. A session whose entry names no account SHALL have no such dock.

#### Scenario: One account for three roles
- **WHEN** wldn's design agent, planner and reviewer run in mac-studio's session wldn on account madswan-2, and its ops in session ops on account willdan
- **THEN** madswan-2's dock lists wldn-design, wldn-planner and wldn-reviewer with mac-studio and session wldn, and willdan's lists wldn-ops
