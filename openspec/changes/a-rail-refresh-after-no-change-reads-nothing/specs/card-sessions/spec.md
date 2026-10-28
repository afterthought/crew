## MODIFIED Requirements

### Requirement: A session whose card is closed or whose row is gone is ended on every rail read
Each time `crew rail` runs, and each time the host's follower refreshes after something it read has moved, whether swancloud's job or a rail tab runs it, crew SHALL end, on every host of each partition read, each session it started for a card key whose row is gone, or whose card the run record holds as closed with no card open under the key. A refresh after nothing moved SHALL end sessions only on a host the last refresh could not check. It SHALL end only sessions it recorded, and only a process plannotator lists as serving the recorded document.

#### Scenario: A verify card's session from before
- **WHEN** the session crew started for `verify/x/20261009-1412`, before a verify report had no row, still runs on chuck-herdr-alpha
- **THEN** the next `crew rail`, run on mac-studio, ends that session, since no row has its key, and its link no longer opens

#### Scenario: A proposal approved in the app
- **WHEN** the user approves proposal 4 on its card, the planner runs `crew plan approve 4` but its session lost Pending You's tools before it closed the card
- **THEN** the next rail read ends the session for `proposal/4`, since its row is gone

#### Scenario: A card closed while its row stays
- **WHEN** the planner closed card `proposal/4` with `ack_answer`, its hook could not end the session, and proposal 4 is still open
- **THEN** the next rail read ends that session

#### Scenario: A row with no card yet
- **WHEN** the planner started the session for `proposal/4` and has not yet posted its card
- **THEN** a rail read leaves the session running

#### Scenario: A session crew did not start
- **WHEN** the user runs plannotator by hand on a closed proposal's page on mac-studio
- **THEN** no rail read ends it

#### Scenario: A batch card's sessions on another host
- **WHEN** the planner closed card `batch/3-1` on mac-studio, and the session for its unit `y` still runs on chuck-herdr-alpha
- **THEN** the next rail read ends `y`'s session there

#### Scenario: Swept with no tab open
- **WHEN** the planner closed card `proposal/4` and its session still runs, and the host's follower runs as swancloud's job with no rail tab open
- **THEN** the follower's next refresh ends that session

#### Scenario: A host the last sweep missed
- **WHEN** the follower's last refresh could not check chuck-herdr-alpha's sessions, and nothing has moved since
- **THEN** the next refresh asks chuck-herdr-alpha alone to end its sessions, and asks no other host
