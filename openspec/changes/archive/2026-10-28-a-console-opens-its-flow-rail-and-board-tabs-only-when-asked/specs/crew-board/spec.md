## ADDED Requirements

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

## MODIFIED Requirements

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
