## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Operation draws each environment's deploys as records
The board view's Operation lane SHALL draw, under each environment's name, its deploys and the operations waiting on it as the board reads them, each deploy a record stamped with where it stands, and each with its marker.

#### Scenario: An offer waiting on the user
- **WHEN** a deploy of mac-studio is offered and its card is open
- **THEN** Operation shows it under mac-studio, stamped as waiting on the user's word, with its ✓ marker saying the card is open

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

## REMOVED Requirements

### Requirement: A viewer narrows every lane to one team
**Reason**: Record 0047 move 5, record 0050 part 3: no teams to narrow to or name.
**Migration**: None.

### Requirement: The team chosen survives a reload
**Reason**: Record 0047 move 5, record 0050 part 3: no teams to narrow to or name.
**Migration**: None.

### Requirement: The strip names the partition's teams
**Reason**: Record 0047 move 5, record 0050 part 3: no teams to narrow to or name.
**Migration**: None.

### Requirement: Construction shows each held bolt as a ledger with its chain
**Reason**: Record 0047 move 5, record 0050 part 3: no team holds a bolt and no slot holds its work; a started bolt's places are Flume's, where crew finds no dev server (the user's ruling of 2026-10-31).
**Migration**: "Construction shows each started bolt as a ledger with its chain", added by this change.

### Requirement: A subscription's dock lists its sessions
**Reason**: Record 0047 move 5, record 0050 part 3: a subscription's dock was opened from a team's dock, and no team is left.
**Migration**: "A subscription's dock lists the main level's sessions on it", added by this change, opened from the fleet page's subscription.
