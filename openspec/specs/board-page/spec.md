# board-page Specification

## Purpose
The board view of crew's page: one partition's flow, read by `crew board`, drawn as the flywheel mockup draws its phases view; and the page's deploys view, each environment's deploys as a timeline.

## Requirements

### Requirement: Operation draws each environment's deploys as records
The board view's Operation lane SHALL draw, under each environment's name, its deploys and the operations waiting on it as the board reads them, each deploy a record stamped with where it stands, and each with its marker; they SHALL be narrowed to a team as the teams on the environment's host.

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
The Bolt plan lane SHALL show each open proposal as a sheet with its number, who proposed it, the first line of its case and whose agreement it waits on; each planned bolt as a ledger whose units are all queued; and each queued unit as a slip with its repository greyed before its name.

#### Scenario: A queued unit
- **WHEN** unit zone-two of switchboard-kit is in the queue
- **THEN** Bolt plan shows a slip naming zone-two with switchboard-kit greyed before it

### Requirement: Construction shows each held bolt as a ledger with its chain
The Construction lane SHALL show each held bolt as a ledger: its head naming repository, bolt, team and host; its units in plan order as a chain, each marked merged, building or queued, a building unit with its stage, tasks, slot and dev server; its fixes on a row of their own; and its server at the foot.

#### Scenario: A bolt being built
- **WHEN** bolt tenant-environments is held by swb-1 with unit a in code at 1 of 2 tasks and unit b planned
- **THEN** Construction shows tenant-environments as a ledger headed by its repository, swb-1 and its host, with a as a building link of its chain saying code 1/2 and b as a queued link

### Requirement: Operation shows landings as records
The Operation lane SHALL show each bolt landed in the last seven days as a muted record, newest first, with a stamp saying when and by whom it landed, and its team and units.

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
With the board view and the dock, the page SHALL still be one file that holds its own data, style and script and fetches nothing: no font, script, style or image from anywhere. It SHALL hold none of the mockup's sample data. Every text it shows from the state, in the lanes and in a dock, SHALL be set as text, never as markup.

#### Scenario: Offline
- **WHEN** the page is opened from disk with the network off
- **THEN** the board view and the lineage view draw in full and the browser makes no request

#### Scenario: A dock of typed words
- **WHEN** a signal's assertion holds `</script><b>here</b>` and the user opens its dock
- **THEN** the dock shows those characters as they are, and the page's data block is not ended by them

### Requirement: A viewer narrows every lane to one team
The page's header SHALL offer each team of the partition, as the teams file lists them, and all teams. Choosing a team SHALL narrow every lane to the objects the board's read gives as that team's, and a lane left empty SHALL say there is nothing in it for that team. The attention strip SHALL never be narrowed.

#### Scenario: One team
- **WHEN** the user chooses crw-3 on swancloud's page
- **THEN** Construction shows only the bolt crw-3 holds, Inception only the signals crw-3's agents captured, and Bolt plan and Operation only what is crw-3's

#### Scenario: A host down while narrowed
- **WHEN** the user has chosen crw-3 and a host of another team did not answer
- **THEN** the attention strip still names that host

### Requirement: The team chosen survives a reload
The choice of team SHALL survive a reload of the page and a new page written over it: it SHALL be kept in the page's address, and in the browser for that partition when the address names none. A kept team the partition no longer has SHALL be shown as all teams.

#### Scenario: The page is written again
- **WHEN** the user has chosen crw-3 and reloads after the page was written again
- **THEN** the page opens narrowed to crw-3

#### Scenario: Opened from a plain link
- **WHEN** the user chose crw-3 earlier and now opens swancloud's page from a link with no team in it
- **THEN** the page opens narrowed to crw-3

#### Scenario: A team that is gone
- **WHEN** the address names a team the partition no longer has
- **THEN** the page shows all teams

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
A click on an item of the board view, or Enter on it, SHALL open that item's dock: a signal's quote, a proposal's sheet, a planned or held bolt's ledger, a unit's or chore's link in a chain or its queued slip, a fix's row, a landing's record, a deploy's record, a waiting operation's record and a team's pill. Each deploy of the deploys view SHALL open the same dock as its record on the board. Every item the page draws SHALL have a dock.

#### Scenario: A unit being built
- **WHEN** the user clicks unit a in tenant-environments' ledger
- **THEN** a dock opens titled a, saying it is a unit of bolt tenant-environments in code at 1 of 2 tasks, in its slot

#### Scenario: Every item has its dock
- **WHEN** the page is written for a partition with a signal, a proposal, a planned bolt, a held bolt with a unit and a fix, a queued unit, a landing, a deploy and a waiting operation
- **THEN** every one of them carries the key of a dock the page holds, and so does each team of the partition

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
- **WHEN** the user opens the dock of a fix of tenant-environments that has not merged
- **THEN** the dock says it has not merged, names its slot and its server, and links its bolt

### Requirement: A dock links the items it names
Each item a dock names that the page draws SHALL be a link that opens that item's dock in its place, and the dock SHALL keep a trail: its back control SHALL return to the dock it was opened from. An item named that the page does not draw, such as an agenda item, SHALL be named as text.

#### Scenario: From a bolt to its unit and back
- **WHEN** the user opens tenant-environments' dock, follows unit a, then presses back
- **THEN** unit a's dock replaces the bolt's, and back shows the bolt's dock again

### Requirement: The strip names the partition's teams
The strip under the header SHALL name each team of the partition, in the teams file's order, as a pill with its host, after the hosts; it SHALL never be narrowed. A team's dock SHALL show its kits, its host and herdr session, the Claude account that session runs on, the bolts it holds, its landings in the board's window, the signals its agents captured and the environment on its host, each a link where the page draws it.

#### Scenario: A team with no bolt
- **WHEN** crw-4 holds no bolt and the user clicks its pill
- **THEN** crw-4's dock shows its kits, its host and session and its account, and says it holds no bolt

### Requirement: A subscription's dock lists its sessions
The Claude account a team's session runs on SHALL be a link in that team's dock opening the account's dock, which SHALL list the partition's sessions on that account, as the hosts file names them: each team and each main-level agent on it, with its host and session. An account the hosts file does not name for a session SHALL be said not to be named, never shown blank.

#### Scenario: Two teams on one account
- **WHEN** crw-1 and crw-2 run in sessions whose account is madswan-2 and the user opens madswan-2 from crw-1's dock
- **THEN** madswan-2's dock lists crw-1 and crw-2 with their hosts and sessions, and any main-level agent of the partition on it

### Requirement: The dock answers nothing
A dock SHALL hold no control that answers a card or moves anything: it SHALL have no foot, and an item waiting on a decision SHALL carry its marker saying whether its card is open and who asked it, as the board does, the card being answered on the rail.

#### Scenario: A proposal waiting
- **WHEN** proposal 4 is open with its card open and the user opens its dock
- **THEN** the dock carries ✓ saying its card is open and who asked it, and holds no control that approves it

### Requirement: The open dock survives a reload
The dock open SHALL be kept in the page's address beside the team and the view, so a reload, or the page written again over this one, opens the same item's dock. An item the page no longer holds SHALL leave the board shown with no dock open.

#### Scenario: The page is written again
- **WHEN** the user has unit a's dock open and reloads after the page was written again
- **THEN** the page opens with unit a's dock, its details as the new page holds them

#### Scenario: The item is gone
- **WHEN** the address names the dock of a bolt that has since landed and left the board
- **THEN** the page shows the board with no dock open
