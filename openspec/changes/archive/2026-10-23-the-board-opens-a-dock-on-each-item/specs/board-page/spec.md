## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: The page stays one self-contained file
With the board view and the dock, the page SHALL still be one file that holds its own data, style and script and fetches nothing: no font, script, style or image from anywhere. It SHALL hold none of the mockup's sample data. Every text it shows from the state, in the lanes and in a dock, SHALL be set as text, never as markup.

#### Scenario: Offline
- **WHEN** the page is opened from disk with the network off
- **THEN** the board view and the lineage view draw in full and the browser makes no request

#### Scenario: A dock of typed words
- **WHEN** a signal's assertion holds `</script><b>here</b>` and the user opens its dock
- **THEN** the dock shows those characters as they are, and the page's data block is not ended by them
