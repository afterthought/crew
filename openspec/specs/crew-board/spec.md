# crew-board Specification

## Purpose
The board of a partition's flow: four lanes, Inception, Bolt plan, Construction and Operation, each object on one line with the rail's decisions as markers on it, read from crew's state and writing nothing, as text in the terminal and as JSON for the page; and each crew agent's view of it.

## Requirements

### Requirement: Operation shows each environment's deploys and the operations waiting
After the bolts landed in the last seven days, the Operation lane SHALL show each environment's deploys that moved in those seven days or are still open, newest first, each on one line with the commit and the one it comes from, where it stands, whose word it was deployed on and the bolts it carried, or the commit the record can't place when no landing in it left main there; then each operation on that environment whose latest state is waiting, handed or failed. A deploy waiting on the user's word and an operation waiting on the user SHALL carry their rail row's marker. All of it SHALL be read from the run record's `ops.*` entries of the main level's host and its landings, and `crew board --json` SHALL give it as each partition's `environments`.

#### Scenario: A deploy done and a newer one offered
- **WHEN** wldn-ops approved the deploy of mac-studio to a landing's commit, the deployer recorded it done, and a deploy of the next landing's commit is offered
- **THEN** Operation shows the offer first, with ✓, waiting on the user's word and carrying the newer landing's bolt, then the deploy, done, approved by wldn-ops and carrying its bolt

#### Scenario: A deploy whose commit no landing left main at
- **WHEN** a deploy of mac-studio is recorded to a commit no landing in the record left main at
- **THEN** its line says that commit is no landing's commit in the record, and names no bolt

#### Scenario: Operations waiting
- **WHEN** a step after a deploy is handed to the dispatcher and a step on its own waits on the user
- **THEN** Operation shows the first handed to the dispatcher and the second with ✓ and its card, and not a step marked done

### Requirement: Main-level ops's view shows the operations
Main-level ops (`<label>-ops`) SHALL have a view among the agents' views, drawn above its prompt by crew's mod: a head counting the deploys waiting on the user's word, those running and the operations waiting, then, environment by environment, each deploy waiting on the word with its card, each approved and not yet deployed, each running, and each operation step waiting, handed or failed with the deploy it comes after and its doer.

#### Scenario: A deploy offered and a step handed
- **WHEN** a deploy of mac-studio waits on the user's word with wldn-ops's card open, and a step after the last deploy is handed to the dispatcher
- **THEN** wldn-ops's view counts one deploy waiting on the word and one operation, and shows the deploy with ✓ and its card, and the step as handed with the dispatcher as its doer

#### Scenario: A deploy whose card was refused
- **WHEN** a deploy of deneb waits on the user's word and Pending You refused the last post of its card
- **THEN** swancloud-ops's view shows the deploy with ✓ and says it has no card open, its post refused

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
The Construction lane SHALL show each bolt a team holds as a ledger: its head line with its repository, team and host, and, once every unit and chore of it has merged and sluice is green at its head while not every one has landed, that it waits to land; each unit in plan order with its stage, its tasks done and total in code or verify, the slot holding it and the URL of the dev server running in its worktree; each fix of the bolt with whether it has merged, its slot and its server; and the bolt's own server at the foot. A team holding two bolts SHALL have a ledger for each, and its conductor's band SHALL draw both.

#### Scenario: A unit in code
- **WHEN** unit a of bolt tenant-environments is in code with 1 of 2 tasks ticked, held by swb-1's unit-1
- **THEN** tenant-environments' ledger has a line for a saying code 1/2 and unit-1

#### Scenario: No server running
- **WHEN** a unit's worktree has no dev server running, or its kit has no dev server naming
- **THEN** its line shows no URL and no note about it

#### Scenario: A bolt waiting to land beside the one being built
- **WHEN** swc-1 holds `doctor-rows`, every unit merged and sluice green at its head, and `ssh-fix`, with a unit in code
- **THEN** the lane and swc-1-conductor's band each show `doctor-rows`'s head line saying it waits to land, and `ssh-fix`'s ledger beside it

### Requirement: Operation shows the bolts landed in the last seven days
The Operation lane SHALL list each bolt landed in the last seven days, newest first, from the `bolt.land` entries of the partition's run record that were not refused, with when it landed, who landed it and its units.

#### Scenario: A landing
- **WHEN** wldn-ops landed bolt apex-zones two days ago
- **THEN** Operation lists apex-zones with that time, wldn-ops and zone-one

#### Scenario: Past the window
- **WHEN** a bolt landed eight days ago
- **THEN** Operation does not list it

### Requirement: Each rail row is a marker on its object
Every row `crew rail` would list for the partition SHALL appear on the board as a marker on the line of its object, and never as a line of its own: ✓ on a proposal's line for an open proposal, ✓ on a unit's line for a unit in review, ✎ on a unit's line for a verify report the user has not answered, and ✓ on a ledger's head line for a bolt waiting to land. Each marker SHALL say whether that row's card is open and who asked it, and, when none is open and the last post under the row's key was refused, that the row owes its card because Pending You refused its post.

#### Scenario: A unit in review
- **WHEN** unit a is in review and swb-1-conductor has a card open under its key
- **THEN** a's line in its ledger carries ✓ and says the card is open, asked by swb-1-conductor, and no other line names a's review

#### Scenario: A bolt to land
- **WHEN** every unit of tenant-environments has merged and none has landed
- **THEN** its ledger's head line carries ✓ and says whether a card is open for it

#### Scenario: A row whose card post was refused
- **WHEN** a deploy of deneb waits on the user's word, no card is open under `deploy/deneb`, and the last post under that key was refused
- **THEN** its line in Operation carries ✓ and says it has no card open, its post refused, and the JSON's marker carries the refusal's words

### Requirement: The board answers nothing
The board SHALL print no command that answers or moves anything, and SHALL write nothing: no commit, no run-record entry, no file in a kit or a blueprints repo.

#### Scenario: Read only
- **WHEN** `crew board` runs on a partition with a proposal open, a unit in review and a bolt to land
- **THEN** its output holds no `crew plan approve`, `crew unit approve` or `crew tell`, the flywheel's branch has the same tip, and the run record has no new entry

### Requirement: The attention line names what is wrong
The board SHALL end with an attention line, each item marked !, naming each host that did not answer for its kits, never for its run record, which is read from the partition's branch; each plan or signals home it could not read, with why, the branch among them when its run record could not be read; and each bolt a team holds whose every unit has landed but which is still in the plan. A ledger whose bolt is in that state SHALL also carry ! on its head line. With nothing to name, the attention line SHALL say none.

#### Scenario: A host down
- **WHEN** the box holding swb-1 does not answer
- **THEN** the attention line names the box and why, and swb-1's ledger shows its units from the plan with their stages unknown

#### Scenario: An operator host asleep
- **WHEN** macbook-pro, which holds a wldn operator session and runs no team, does not answer
- **THEN** the attention line does not name macbook-pro, and the landings, batches and cards read from `wldn/main` are drawn whole

#### Scenario: Landed but still in the plan
- **WHEN** every unit of a held bolt has landed on main and `crew bolt land` has not run
- **THEN** its ledger's head carries ! and the attention line names the bolt as landed and still in the plan

### Requirement: The board prints its lanes as JSON
`crew board --json` SHALL print the same board as JSON: for each partition, its lanes as lists of objects, each object with its partition, its team where it has one, and its markers, each marker with its rail group, its card key, when its row began to wait, its card, and, when no card is open, the words of Pending You's refusal of the last post under its key, or none, and the attention items; and the hosts that did not answer and the plans not read.

#### Scenario: The page's input
- **WHEN** `crew board --label wldn --json` runs while unit a is in review
- **THEN** the JSON's Construction lane holds tenant-environments with team swb-1, and unit a with a marker of group review and its card key

### Requirement: The rail and the board come from one read
When the host's follower refreshes, crew SHALL read the plan, the kits and the run record once for both the rail and the board: it SHALL write the rail, what `crew rail` prints, as the rail's frame, and the board's data as the board's frame; the rail tab SHALL draw the rail's frame and the board tab SHALL draw the board from that same read at its own width. When the follower has not refreshed a frame for more than three of its periods, its tab SHALL say how old it is; when none was ever written, the tab SHALL say so and that the host's follower writes it.

#### Scenario: One refresh
- **WHEN** the host's follower refreshes for a partition with three units in flight on one host
- **THEN** that host's kits are read once and the state branch fetched once for both frames

#### Scenario: The loop has stopped
- **WHEN** the host's follower has not run for five minutes
- **THEN** the board tab still shows its last board, and the rail tab its last rail, each headed with how long ago it was read

#### Scenario: Never written
- **WHEN** the board tab opens on a host where no follower has written wldn's frame
- **THEN** it says there is no board for wldn yet and that the host's follower writes it

### Requirement: The board's JSON lists each partition's teams
`crew board --json` SHALL list, for each partition, its teams in the teams file's order, each with its kit and its host. The board's text SHALL not change.

#### Scenario: The page's team control
- **WHEN** `crew board --label wldn --json` runs
- **THEN** wldn's partition lists each of its teams with its kit and host, in the teams file's order

### Requirement: Each object in the board's JSON says whose it is
Each object in the lanes of `crew board --json` SHALL carry the teams it belongs to: a held bolt or a landing, its team; a signal, the team whose agent captured it; a planned bolt, a queued unit or an exploration, every team building its repository; a proposal, the teams holding its bolts and those building its repositories. An object belonging to no team SHALL carry an empty list.

#### Scenario: A held bolt and the work queued behind it
- **WHEN** swb-1 and swb-2 both build switchboard-kit, swb-1 holds tenant-environments, and unit zone-two of switchboard-kit is queued
- **THEN** the JSON gives tenant-environments the teams `["swb-1"]` and zone-two the teams `["swb-1", "swb-2"]`

#### Scenario: A signal the user wrote
- **WHEN** a signal was captured by the user rather than by an agent of a team
- **THEN** the JSON gives it an empty list of teams

#### Scenario: A proposal for a held bolt
- **WHEN** proposal 4 adds a unit to tenant-environments, which swb-1 holds
- **THEN** the JSON gives proposal 4 the team swb-1

### Requirement: The host's follower runs with no tab
`crew _follow` SHALL be the host's follower with no tab, the command a job of the host's runs: every 30 seconds and whenever a partition's run record gains an entry, for each partition with an operator session on the host, it SHALL make the refresh the rail tab's loop makes. crew SHALL run no service of its own for it.

#### Scenario: The host's job follows
- **WHEN** swancloud's job runs `crew _follow` on mac-studio, which holds operator sessions of wldn and swancloud, and no console tab is open
- **THEN** both partitions' board frames, rail frames and agents' views are written each period, the card sessions of closed cards are ended, and due restarts are handed out

### Requirement: A host has one follower
Whoever follows on a host, `crew _follow` or a rail tab's loop, SHALL hold the host's follower lock while it follows, saying which it is. A `crew _follow` started while another holds it SHALL wait for it, reading nothing; a rail tab that cannot take it SHALL draw the frames and try again.

#### Scenario: A second follower
- **WHEN** a rail tab's loop holds mac-studio's follower lock and `crew _follow` starts
- **THEN** `crew _follow` reads nothing until the rail tab is closed, and then follows

#### Scenario: The job is followed by a tab
- **WHEN** `crew _follow` holds the lock and the user opens wldn's rail tab
- **THEN** the rail tab draws the follower's frames and reads nothing itself
