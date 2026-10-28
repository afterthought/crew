## MODIFIED Requirements

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

### Requirement: The host's follower runs with no tab
`crew _follow` SHALL be the host's follower with no tab, the command a job of the host's runs: once a minute on its clock, and whenever this host's cache of a partition's state branch moves, for every partition with an operator session on the host, it SHALL make the refresh the rail tab's loop makes. crew SHALL run no service of its own for it.

#### Scenario: The host's job follows
- **WHEN** swancloud's job runs `crew _follow` on mac-studio, which holds operator sessions of wldn and swancloud, and no console tab is open
- **THEN** both partitions' board frames, rail frames and agents' views are written each period, the card sessions of closed cards are ended, and due restarts are handed out

## ADDED Requirements

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
The host's follower SHALL learn that a kit's merge queue moved from sluice's overview alone: it SHALL keep one `sluice overview --json --watch` running in each kit whose queue its read shows, on the kit's host, take a line whose document differs from the last, its time aside, as the queue's move, and read the queue from that line. Where no watch can run, because the host's sluice has no watch or the kit's watch ended or could not start, it SHALL ask `sluice overview --json` once on its clock instead, and open an ended watch again at the next tick. crew SHALL read and name no folder of sluice's.

#### Scenario: A merge moves in sluice's queue
- **WHEN** a unit's merge into a bolt of switchboard-kit on the box is queued in sluice, and the kit's overview watch prints a new line
- **THEN** the follower's next refresh, within a few seconds, shows the submission's number on the unit's row, gathers no kit and starts no sluice

#### Scenario: One watch for each kit
- **WHEN** the follower on mac-studio reads two partitions whose bolts are both in switchboard-kit on the box
- **THEN** it keeps one overview watch for switchboard-kit, over one ssh to the box, and a refresh that gathers the kit takes its queue from the watch's line without running sluice again

#### Scenario: A host whose sluice has no watch
- **WHEN** the box's sluice refuses `--watch`
- **THEN** the follower asks the box's kits' overviews once at each tick of its clock, in that tick's one ssh to the box, and not between ticks

#### Scenario: A watch ends
- **WHEN** the ssh holding switchboard-kit's watch drops
- **THEN** the kit's row says its queue can't be read and why until the next tick, which opens the watch again and asks the overview once

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
