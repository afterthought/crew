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
The Construction lane SHALL show each bolt a team holds as a ledger: its head line with its repository, team and host, the number and state of its landing while one stands in sluice, and, once every unit and chore of it has merged and sluice is green at its head while not every one has landed, that it waits to land; while the run record's last `bolt.submit` on the bolt has its landing queued and sluice's queue, read, shows no landing of it standing, that its landing is queued, with the number the run record holds; once it has landed on main and its close was refused, that it landed and was not closed, with the words of its last refused close; each unit in plan order with its stage, its tasks done and total in code or verify, the number and state of its merge while one stands in sluice, the slot holding it and the URL of the dev server running in its worktree; each fix of the bolt with whether it has merged, its merge's number and state while one stands, its slot and its server; and the bolt's own server at the foot. A team holding two bolts SHALL have a ledger for each, and its conductor's band SHALL draw both. Main-level ops's band SHALL draw the head line of each bolt whose close was refused.

#### Scenario: A unit in code
- **WHEN** unit a of bolt tenant-environments is in code with 1 of 2 tasks ticked, held by swb-1's unit-1
- **THEN** tenant-environments' ledger has a line for a saying code 1/2 and unit-1

#### Scenario: No server running
- **WHEN** a unit's worktree has no dev server running, or its kit has no dev server naming
- **THEN** its line shows no URL and no note about it

#### Scenario: A bolt waiting to land beside the one being built
- **WHEN** swc-1 holds `doctor-rows`, every unit merged and sluice green at its head, and `ssh-fix`, with a unit in code
- **THEN** the lane and swc-1-conductor's band each show `doctor-rows`'s head line saying it waits to land, and `ssh-fix`'s ledger beside it

#### Scenario: A merge standing in sluice
- **WHEN** unit a of bolt tenant-environments has its merge `#41` under test on `bolt/tenant-environments`
- **THEN** a's line in the lane and in swb-1-conductor's band says `#41 under test`

#### Scenario: A landing standing in sluice
- **WHEN** `doctor-rows`'s landing `#355` is queued on its kit's main
- **THEN** `doctor-rows`'s head line in the lane, in swc-1-conductor's band and in main-level ops's says `landing #355 queued`

#### Scenario: A queue that can't be read
- **WHEN** sluice's record of the queue could not be read on swb-1's host
- **THEN** tenant-environments' head line says its submissions can't be read, and no line shows a number, though the run record has its landing queued

#### Scenario: A landing recorded queued that sluice no longer has standing
- **WHEN** the run record's last `bolt.submit` on `doctor-rows` is queued as submission 412, and sluice's queue, read on swc-1's host, shows no landing of it standing
- **THEN** `doctor-rows`'s head line, on the lane and in swc-1-conductor's band, says its landing is queued as #412

#### Scenario: A close refused
- **WHEN** `doctor-rows` has landed on main and the run record's last `bolt.land` on it since then is refused, saying chore `tidy-rows` has not landed on main
- **THEN** `doctor-rows`'s head line, on the lane, in swc-1-conductor's band and in main-level ops's band, says it landed on main and was not closed, with those words, in the attention gutter

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
When the host's follower refreshes, crew SHALL read the plan, the kits and the run record once for both the rail and the board, and once for every partition with an operator session on the host, each kit read once however many of those partitions it serves: it SHALL write each partition's rail, what `crew rail` prints, as that partition's rail frame, and its board's data as its board frame; the rail tab SHALL draw the rail's frame and the board tab SHALL draw the board from that same read at its own width. When the follower has not refreshed a frame for more than three of its periods, its tab SHALL say how old it is; when none was ever written, the tab SHALL say so and that the host's follower writes it.

#### Scenario: One refresh
- **WHEN** the host's follower refreshes for a partition with three units in flight on one host
- **THEN** that host's kits are read once and the state branch fetched once for both frames

#### Scenario: Two partitions on one host
- **WHEN** the host's follower on mac-studio, which holds operator sessions of wldn and swancloud, makes its first refresh, and both partitions' teams build kits on the box
- **THEN** the box's kits are gathered once for both partitions, and wldn's and swancloud's rail frames, board frames and agents' views are each written from that one read

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
`crew _follow` SHALL be the host's follower with no tab, the command a job of the host's runs: once a minute on its clock, and whenever this host's cache of a partition's state branch moves, for every partition with an operator session on the host, it SHALL make the refresh the rail tab's loop makes. crew SHALL run no service of its own for it.

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

### Requirement: A refresh after nothing moved reads nothing
Before it reads, the host's follower SHALL check whether anything the refresh acts on has moved since its last read: each partition's state branch and blueprints main as this host's caches hold them; each kit's refs, worktrees, places' changes and slots files, on every host it reads; each kit's queue, as sluice's overview last printed it; each of those hosts' card readings folder, where a reading the user sent back lands; the cards as Pending You answered for them at the clock's last tick; crew's checkout; and the teams file. When nothing has, it SHALL start no read and no process beyond that check and, at a tick of its clock, the clock's own fetches and reads, and SHALL write each partition's rail frame, board frame and agents' views again from its last read, as of the check.

#### Scenario: An idle host
- **WHEN** the host's follower on mac-studio refreshes, and nothing it read has moved since its last refresh
- **THEN** beyond its clock's fetch and its reads of what no stamp sees, it starts no git, no gather, no sluice and no other process on mac-studio, asks the box only for its kits' check, and writes wldn's frames again from its last read, each saying the time of this refresh

#### Scenario: What it can't check
- **WHEN** the follower cannot read whether a kit on the box has moved, because the box does not answer
- **THEN** it does not take the kit as unmoved: it reads again what rests on the box, and names the box as it does today

#### Scenario: A reading sent back
- **WHEN** the user sends back a batch's reading on mac-studio, and plannotator writes its result into the card's readings folder there, with nothing else moved
- **THEN** the follower's next refresh, within a few seconds, takes mac-studio's readings as moved and sweeps its card sessions there, which is where the reading's owner is told, and gathers no kit and reads no state branch

#### Scenario: sluice's folder moves
- **WHEN** sluice writes its records and logs in switchboard-kit's git folder on the box, and its overview prints no new line
- **THEN** the follower takes the kit as unmoved, having read nothing of that folder

#### Scenario: A task ticked with nothing committed
- **WHEN** a coder on mac-studio ticks a task in its place's tasks.md and commits nothing
- **THEN** the follower's next refresh on its clock takes the kit as moved and gathers it again

### Requirement: A refresh after a change reads only what moved
When something has moved, the host's follower SHALL read again only what rests on what moved: a moved state tip, that partition's plan, proposals and run record at the new tip; a moved blueprints tip, its signals; a moved kit, that kit alone, on its host; a kit's queue moved, that kit's rows' submissions from the overview's new line and nothing gathered; a moved readings folder, that host's card sessions swept and nothing read; cards whose answers moved, the card sweep run and nothing read. What did not move SHALL be taken from the follower's last read, which crew SHALL never read as a fact once what it was read at has moved, and keep in the follower's process alone, writing none of it.

#### Scenario: The plan moved and no kit did
- **WHEN** the user approves a proposal on mac-studio, moving wldn's state branch there, and no kit has moved
- **THEN** the follower's refresh fetches nothing, reads wldn's plan and run record once at the new tip, and gathers no kit

#### Scenario: One kit moved
- **WHEN** a coder commits in a place of switchboard-kit on the box, and nothing else has moved
- **THEN** the follower's next refresh gathers switchboard-kit on the box alone, and reads no state branch again

### Requirement: The follower fetches on a one-minute clock
The host's follower SHALL fetch each partition's state branch and blueprints main once a minute on its own clock, never faster, and SHALL never fetch because an entry arrived. Between its clock's ticks it SHALL look at this host's caches with no process, refreshing within a few seconds when a write on this host moves one; it SHALL start no `crew events --follow` to wake on.

#### Scenario: An entry from another host
- **WHEN** a conductor on the box starts a stage, and wldn's branch gains its entry
- **THEN** mac-studio's follower shows it at its clock's next fetch, within a minute, and fetched nothing in between

#### Scenario: An entry written on this host
- **WHEN** the user approves a unit from the rail tab's shell on mac-studio
- **THEN** the follower refreshes within a few seconds, without fetching

### Requirement: The follower asks Pending You about cards on its clock
The host's follower SHALL ask Pending You about the cards its sweep acts on only at its clock's tick, in one bridge, and in none when there is no card to ask about. Its sweeps between ticks SHALL judge the cards as that tick last answered.

#### Scenario: A card lost between ticks
- **WHEN** Pending You no longer finds wldn's card for proposal 4, whose row is still on the rail, and nothing else moves
- **THEN** the follower asks Pending You nothing until its clock's next tick, and at that tick takes the cards as moved and its card sweep posts the card again

#### Scenario: No card to ask about
- **WHEN** the follower's clock ticks and its last read names no card its sweep would act on
- **THEN** it starts no Pending You bridge at that tick

### Requirement: The follower follows each kit's queue through sluice's overview
The host's follower SHALL learn that a kit's merge queue moved from sluice's overview alone. It SHALL keep one `sluice overview --json --watch` running in each kit whose queue its read shows, on the kit's host, take a line whose document differs from the last (its time aside) as the queue's move, and read the queue from that line. Where no watch can run, because the host's sluice has no watch or the kit's watch ended or could not start, it SHALL ask `sluice overview --json` once on its clock instead, and open an ended watch again at the next tick. A gather of a kit SHALL read the decided submissions of the kit's held bolts from sluice's record with `sluice status <branch> --all --json`, for each held bolt's branch and for the kit's main, and SHALL run no overview of its own while a watch's line gives the queue. Between gathers, a submission that has left the queue SHALL count as it last stood until the line that no longer holds it. crew SHALL read and name no folder of sluice's.

#### Scenario: A merge moves in sluice's queue
- **WHEN** a unit's merge into a bolt of switchboard-kit on the box is queued in sluice, and the kit's overview watch prints a new line
- **THEN** the follower's next refresh, within a few seconds, shows the submission's number on the unit's row, gathers no kit and starts no sluice

#### Scenario: One watch for each kit
- **WHEN** the follower on mac-studio reads two partitions whose bolts are both in switchboard-kit on the box
- **THEN** it keeps one overview watch for switchboard-kit, over one ssh to the box, and a refresh that gathers the kit takes its queue from the watch's line, running no overview of its own and asking sluice only for its held bolts' records

#### Scenario: A host whose sluice has no watch
- **WHEN** the box's sluice refuses `--watch`
- **THEN** the follower asks the box's kits' overviews once at each tick of its clock, in that tick's one ssh to the box, and not between ticks

#### Scenario: A watch ends
- **WHEN** the ssh holding switchboard-kit's watch drops
- **THEN** the kit's row says its queue can't be read and why until the next tick, which opens the watch again and asks the overview once

#### Scenario: A held bolt's decided merges
- **WHEN** the follower gathers switchboard-kit while bolt `b`, held by swb-1, has had two merges decided and one standing
- **THEN** the gather reads `b`'s branch's and main's records from sluice once each, and `b`'s line counts all three merges' time in the gate

### Requirement: What no stamp sees is read on the follower's clock
At each tick of its clock, the host's follower SHALL read again each host's dev servers as portless lists them, and herdr's listing of each card's asker its card sweep acts on, and SHALL take a change in either as moved, drawing the frames again and sweeping the cards with it, with nothing gathered. At every refresh, whether or not anything moved, it SHALL work out from the run record's times and the time now whether a batch is due by hours, and tell the partition's planner once when one is.

#### Scenario: A dev server started by hand
- **WHEN** a dev server is started by hand on the box, and nothing else moves
- **THEN** the board shows it after the follower's next tick, within a minute, and no kit is gathered

#### Scenario: An asker's agent gone
- **WHEN** the agent that asked a question on a card leaves its pane, and nothing else moves
- **THEN** at the follower's next tick herdr's listing shows the pane empty, and the card sweep withdraws the question, naming the asker

#### Scenario: A batch made due by the hours
- **WHEN** wldn's last batch was delivered as many hours ago as its setting, one change is due, and nothing moves
- **THEN** the follower's next refresh tells wldn's planner the batch is due, reading nothing to find it, and the refresh after reads the entry and tells nothing again

### Requirement: A held bolt's head line shows its age and who held its time
Each held bolt's head line SHALL show, in the Construction lane, in the board's JSON and in every agent's band that draws it, the bolt's age since its newest give and the minutes of that age each holder held, leaving out a holder that held none. It SHALL also show who holds the bolt now and since when; for a hold, what the hold is for. Once nobody has held the bolt for five minutes, the line SHALL say it is stalled. When the give, the stages or the submissions can't be read, the line SHALL say the age or the split can't be told and why, and SHALL never show a guessed share. No card SHALL be raised and no one told because of a bolt's age.

#### Scenario: The bands
- **WHEN** the follower writes swb-1-conductor's view and the planner's
- **THEN** each draws `b`'s head line with its age, its shares and who holds it now, as the lane does

#### Scenario: Stalled
- **WHEN** nothing of `b` has run, stood in sluice, had a card open or been held for seven minutes
- **THEN** those seven minutes are nobody's, and the line says `b` is stalled since they began

#### Scenario: Nobody for a moment
- **WHEN** a stage of `b` ended two minutes ago and nothing has started since
- **THEN** the line says nobody holds `b` since then, and does not say it is stalled

#### Scenario: A give that can't be read
- **WHEN** the run record holds no give of `b` in the days the board reads
- **THEN** `b`'s head line says its age can't be told and why, and shows no share

### Requirement: Each minute of a bolt's life goes to one holder
Each minute of a held bolt's life SHALL go to exactly one holder, the first of these that applies:

1. the team, while a stage of the bolt's units, chores or fixes runs other than a merge;
2. the kit, while one of the bolt's submissions (a merge into its branch, or its landing on its kit's main) is under test in sluice;
3. the team, while a merge stage of the bolt's runs or one of its submissions stands in sluice not under test;
4. the user, while a card of the bolt's is open;
5. a hold, while one is recorded on the bolt;
6. nobody.

A submission whose start of checks sluice's record does not give SHALL be counted under test for its whole stay.

#### Scenario: A team at work
- **WHEN** bolt `b` was given to swb-1 three hours ago, a code stage ran for two hours, a batch card holding its unit was open for forty minutes with nothing running, and nothing held it for twenty minutes
- **THEN** `b`'s head line in the lane says `3h 00m`, team `2h 00m`, user `40m`, nobody `20m`, and names no kit or hold share

#### Scenario: A merge under test
- **WHEN** unit `a`'s merge `#41` into `bolt/b` stood queued for five minutes and then under test for twelve, while `a`'s merge stage ran throughout and no other stage ran
- **THEN** the five minutes are the team's and the twelve the kit's, and while `#41` is under test the line says the kit holds `b` since the start of its checks

#### Scenario: A stage beside a merge under test
- **WHEN** unit `c`'s code stage runs while unit `a`'s merge `#41` is under test
- **THEN** those minutes are the team's

#### Scenario: A decided merge whose checks' start is not kept
- **WHEN** sluice's record of `#41`, landed, gives when it was submitted and when it was decided but not when its checks began
- **THEN** its whole stay, from submitted to decided, is the kit's

### Requirement: Each holder is read from what crew already keeps
Every holder of a bolt's time SHALL be read from what crew already keeps, and nothing SHALL be recorded to make the reading:

- **Stages**: the run record's stage starts and ends for the bolt's work since the give.
- **Submissions**: sluice's record of each submission of the bolt: when it was submitted, when its checks began, and when it was decided.
- **Cards**: the run record's card posts and closes. A card is the bolt's when:
  - it is under the bolt's own key, `land/<bolt>`;
  - it is a batch's card holding work of the bolt's;
  - it is a proposal's card whose changes name the bolt or its work;
  - it is the kit's landings card, counted from the end of the bolt's last merge;
  - it is a question an agent of the bolt's team asked the user while the team held the bolt;
  - or its post names the bolt or its work.
- **Holds**: the run record's hold of the team's host, from its hold to its go.

#### Scenario: The user's card
- **WHEN** every unit of `b` has merged, nothing runs, and its kit's landings card has been open for an hour
- **THEN** that hour is the user's, and the line says the user holds `b` since the card's post, naming its key

#### Scenario: A question from the team
- **WHEN** swb-4's unit stopped short and swb-4-conductor's question to the user is open, with nothing of its bolt running
- **THEN** the minutes since its post are the user's

#### Scenario: A held host
- **WHEN** nothing of `b` runs and no card of it is open, while its team's host was held by the user at 14:02 and not yet let go
- **THEN** the minutes since 14:02 are the hold's, and the line says `b` is held since 14:02 because its host is held, naming who held it
