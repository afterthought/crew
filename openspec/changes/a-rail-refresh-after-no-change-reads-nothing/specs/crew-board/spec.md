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
Before it reads, the host's follower SHALL check whether anything the refresh acts on has moved since its last read: each partition's state branch and blueprints main as this host's caches hold them; each kit's refs, worktrees, places' changes, slots files and sluice's records in the kit's git folder, on every host it reads; each of those hosts' card readings folder, where a reading the user sent back lands; the cards as Pending You answered for them at the clock's last tick; crew's checkout; and the teams file. When nothing has, it SHALL start no read and no process beyond that check, and SHALL write each partition's rail frame, board frame and agents' views again from its last read, as of the check.

#### Scenario: An idle host
- **WHEN** the host's follower on mac-studio refreshes, and nothing it read has moved since its last refresh
- **THEN** it starts no git, no gather and no other process on mac-studio, asks the box only for its kits' check, and writes wldn's frames again from its last read, each saying the time of this refresh

#### Scenario: What it can't check
- **WHEN** the follower cannot read whether a kit on the box has moved, because the box does not answer
- **THEN** it does not take the kit as unmoved: it reads again what rests on the box, and names the box as it does today

#### Scenario: A reading sent back
- **WHEN** the user sends back a batch's reading on mac-studio, and plannotator writes its result into the card's readings folder there, with nothing else moved
- **THEN** the follower's next refresh, within a few seconds, takes mac-studio's readings as moved and sweeps its card sessions there, which is where the reading's owner is told, and gathers no kit and reads no state branch

#### Scenario: A merge moves in sluice's queue
- **WHEN** a unit's merge into a bolt of switchboard-kit on the box goes from queued to testing in sluice, moving sluice's records in the kit's git folder and no ref
- **THEN** the follower's next refresh on its clock takes switchboard-kit on the box as moved and gathers it again, alone

#### Scenario: sluice writes only its logs
- **WHEN** sluice writes its run's logs and progress in switchboard-kit's git folder on the box, and no submission's record moves
- **THEN** the follower takes the kit as unmoved

#### Scenario: A task ticked with nothing committed
- **WHEN** a coder on mac-studio ticks a task in its place's tasks.md and commits nothing
- **THEN** the follower's next refresh on its clock takes the kit as moved and gathers it again

### Requirement: A refresh after a change reads only what moved
When something has moved, the host's follower SHALL read again only what rests on what moved: a moved state tip, that partition's plan, proposals and run record at the new tip; a moved blueprints tip, its signals; a moved kit, that kit alone, on its host. a moved readings folder, that host's card sessions swept and nothing read; cards whose answers moved, the card sweep run and nothing read. What did not move SHALL be taken from the follower's last read, which crew SHALL never read as a fact once what it was read at has moved, and keep in the follower's process alone, writing none of it.

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
