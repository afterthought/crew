# Spec Delta

## Purpose

The board view of crew's page: one partition's flow, read by `crew board`, drawn as the flywheel mockup draws its phases view. It is the page the user opens to see which bolt plans are waiting and which bolts are being built, narrowed to one team when they want, with every other partition's page one click away.

## ADDED Requirements

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
Every marker the board's read gives SHALL be drawn on its object's form, never as a form of its own: ✓ for an approval (an open proposal, a bolt to land), ✎ for an answer (a verify report not yet answered), ! for attention (a held bolt every unit of which has landed). Each marker SHALL say whether its card is open and who asked it. The board view SHALL hold no button, link or command that answers or moves anything.

#### Scenario: A proposal waiting
- **WHEN** proposal 4 is open and wldn-planner has its card open
- **THEN** proposal 4's sheet carries ✓ and says its card is open, asked by wldn-planner, and nothing on the page approves it

### Requirement: The lanes fit a desktop and a phone, light and dark
On a window 760 px wide or wider, the four lanes SHALL sit side by side, Bolt plan narrowest and Construction widest. Under 760 px they SHALL stack one above the other in the same order, and nothing on the page SHALL run past the window's edge. The page SHALL follow the viewer's light or dark preference with the mockup's colours for each.

#### Scenario: On a phone
- **WHEN** the page is opened 390 px wide
- **THEN** Inception, Bolt plan, Construction and Operation are stacked in that order and the page does not scroll sideways

#### Scenario: In the dark
- **WHEN** the viewer's system prefers dark
- **THEN** the page uses the mockup's dark colours

### Requirement: The page stays one self-contained file
With the board view, the page SHALL still be one file that holds its own data, style and script and fetches nothing: no font, script, style or image from anywhere. It SHALL hold none of the mockup's sample data. Every text it shows from the state SHALL be set as text, never as markup.

#### Scenario: Offline
- **WHEN** the page is opened from disk with the network off
- **THEN** the board view and the lineage view draw in full and the browser makes no request

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
The page's header SHALL name every partition in the teams file, in its order, with the page's own partition marked as current. Each other partition SHALL be a link to that partition's page as crew lays the pages out, `../<label>/page.html` from this page, so that when the pages are served side by side each is one step from the others.

#### Scenario: Three partitions
- **WHEN** the teams file holds madswan, swancloud and wldn and the page is swancloud's
- **THEN** the header shows madswan, swancloud marked as current, and wldn, and madswan links to `../madswan/page.html` and wldn to `../wldn/page.html`
