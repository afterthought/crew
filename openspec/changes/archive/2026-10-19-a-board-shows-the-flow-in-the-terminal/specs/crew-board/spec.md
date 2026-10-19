## Purpose

The board of a partition's flow: four lanes, Inception, Bolt plan, Construction and Operation, each object on one line with the rail's decisions as markers on it, read from crew's state and writing nothing, as text in the terminal and as JSON for the page.

## ADDED Requirements

### Requirement: The board prints four lanes in order
`crew board [--label L]` SHALL print, for each partition read (the one named, else the caller's, else every partition), a header naming the partition, the time it was read and the hosts that answered, then four lanes in this order: Inception, Bolt plan, Construction, Operation, then the attention line. Each object SHALL be one line. A lane with nothing in it SHALL say none.

#### Scenario: Nothing in flight
- **WHEN** `crew board --label wldn` runs on a partition whose plan holds no bolt, no queued unit and no open proposal
- **THEN** it prints wldn's header and the four lanes in order, each saying none

#### Scenario: Every partition
- **WHEN** `crew board` runs with no label outside any agent
- **THEN** it prints one board per partition in the teams file, one after another

### Requirement: Inception shows the signals no move has taken and the explorations
The Inception lane SHALL list every signal, on the flywheel's branch or on main of the partition's first blueprints repo, that has no move in `moves.rec`, grouped by who captured it, each group with how many it holds and how old its oldest is, each signal with its kind and its first words. It SHALL then list each exploration folder on main of each kit the partition's teams build, with the first line of its first file.

#### Scenario: A moved signal leaves
- **WHEN** a signal captured by wldn-planner is routed to a unit
- **THEN** the next board no longer lists it, and wldn-planner's group counts one fewer

#### Scenario: An exploration
- **WHEN** the kit's main holds `openspec/explorations/command-cost/reading.md` whose first line says it is a reading
- **THEN** Inception lists `command-cost` with that line

### Requirement: Bolt plan shows the proposals, the planned bolts and the queue
The Bolt plan lane SHALL list each open proposal with its number, who proposed it and the first line of its case; each bolt no team holds, with its repository, its goal and its units with their stages; and the queue, by repository, each unit with its sources.

#### Scenario: A planned bolt
- **WHEN** the plan holds bolt apex-zones with no team and unit zone-one in it
- **THEN** Bolt plan lists apex-zones with its repository and goal, and zone-one under it as ready

### Requirement: Construction shows each held bolt as a ledger
The Construction lane SHALL show each bolt a team holds as a ledger: its head line with its repository, team and host; each unit in plan order with its stage, its tasks done and total in code or verify, the slot holding it and the URL of the dev server running in its worktree; each fix of the bolt with whether it has merged, its slot and its server; and the bolt's own server at the foot.

#### Scenario: A unit in code
- **WHEN** unit a of bolt tenant-environments is in code with 1 of 2 tasks ticked, held by swb-1's unit-1
- **THEN** tenant-environments' ledger has a line for a saying code 1/2 and unit-1

#### Scenario: No server running
- **WHEN** a unit's worktree has no dev server running, or its kit has no dev server naming
- **THEN** its line shows no URL and no note about it

### Requirement: Operation shows the bolts landed in the last seven days
The Operation lane SHALL list each bolt landed in the last seven days, newest first, from the `bolt.land` entries of the partition's run record that were not refused, with when it landed, who landed it and its units.

#### Scenario: A landing
- **WHEN** wldn-ops landed bolt apex-zones two days ago
- **THEN** Operation lists apex-zones with that time, wldn-ops and zone-one

#### Scenario: Past the window
- **WHEN** a bolt landed eight days ago
- **THEN** Operation does not list it

### Requirement: Each rail row is a marker on its object
Every row `crew rail` would list for the partition SHALL appear on the board as a marker on the line of its object, and never as a line of its own: ✓ on a proposal's line for an open proposal, ✓ on a unit's line for a unit in review, ✎ on a unit's line for a verify report the user has not answered, and ✓ on a ledger's head line for a bolt waiting to land. Each marker SHALL say whether that row's card is open and who asked it.

#### Scenario: A unit in review
- **WHEN** unit a is in review and swb-1-conductor has a card open under its key
- **THEN** a's line in its ledger carries ✓ and says the card is open, asked by swb-1-conductor, and no other line names a's review

#### Scenario: A bolt to land
- **WHEN** every unit of tenant-environments has merged and none has landed
- **THEN** its ledger's head line carries ✓ and says whether a card is open for it

### Requirement: The board answers nothing
The board SHALL print no command that answers or moves anything, and SHALL write nothing: no commit, no run-record entry, no file in a kit or a blueprints repo.

#### Scenario: Read only
- **WHEN** `crew board` runs on a partition with a proposal open, a unit in review and a bolt to land
- **THEN** its output holds no `crew plan approve`, `crew unit approve` or `crew tell`, the flywheel's branch has the same tip, and the run record has no new entry

### Requirement: The attention line names what is wrong
The board SHALL end with an attention line, each item marked !, naming each host that did not answer, for its kits or for its run record; each plan or signals home it could not read, with why; and each bolt a team holds whose every unit has landed but which is still in the plan. A ledger whose bolt is in that state SHALL also carry ! on its head line. With nothing to name, the attention line SHALL say none.

#### Scenario: A host down
- **WHEN** the box holding swb-1 does not answer
- **THEN** the attention line names the box and why, and swb-1's ledger shows its units from the plan with their stages unknown

#### Scenario: Landed but still in the plan
- **WHEN** every unit of a held bolt has landed on main and `crew bolt land` has not run
- **THEN** its ledger's head carries ! and the attention line names the bolt as landed and still in the plan

### Requirement: The board prints its lanes as JSON
`crew board --json` SHALL print the same board as JSON: for each partition, its lanes as lists of objects, each object with its partition, its team where it has one, and its markers, each marker with its rail group, its card key, when its row began to wait and its card, and the attention items; and the hosts that did not answer and the plans not read.

#### Scenario: The page's input
- **WHEN** `crew board --label wldn --json` runs while unit a is in review
- **THEN** the JSON's Construction lane holds tenant-environments with team swb-1, and unit a with a marker of group review and its card key

### Requirement: The rail and the board come from one read
When the operator workspace's rail tab refreshes, crew SHALL read the plan, the kits and the run record once for both the rail and the board: the rail tab SHALL print what `crew rail` prints, and the board tab SHALL draw the board from that same read at its own width. When the rail tab's loop has not refreshed the board for more than three of its periods, the board tab SHALL say how old its board is; when it has never written one, the board tab SHALL say so and how to open both tabs afresh.

#### Scenario: One refresh
- **WHEN** the rail tab refreshes for a partition with three units in flight on one host
- **THEN** that host's kits are read once and the state branch fetched once for both tabs

#### Scenario: The loop has stopped
- **WHEN** the rail tab's loop has not run for five minutes
- **THEN** the board tab still shows its last board, headed with how long ago it was read
