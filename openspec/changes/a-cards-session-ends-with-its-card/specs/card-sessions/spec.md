## ADDED Requirements

### Requirement: A session whose card is closed or whose row is gone is ended on every rail read
Each time `crew rail` runs, and each time the rail tab refreshes, crew SHALL end, on every host of each partition read, each session it started for a card key whose row is gone, or whose card the run record holds as closed with no card open under the key. It SHALL end only sessions it recorded, and only a process plannotator lists as serving the recorded document.

#### Scenario: A landed unit's verify session
- **WHEN** unit `x` has landed, and the session crew started for `verify/x/20261009-1412` still runs on chuck-herdr-alpha
- **THEN** the next `crew rail`, run on mac-studio, ends that session, and its link no longer opens

#### Scenario: A proposal approved in the app
- **WHEN** the user approves proposal 4 on its card, the planner runs `crew plan approve 4` but its session lost Pending You's tools before it closed the card
- **THEN** the next rail read ends the session for `proposal/4`, since its row is gone

#### Scenario: A card closed while its row stays
- **WHEN** the conductor closed card `verify/x/20261009-1412` with `ack_answer`, its hook could not end the session, and the report is still the newest
- **THEN** the next rail read ends that session

#### Scenario: A row with no card yet
- **WHEN** the conductor started the session for `verify/x/20261009-1412` and has not yet posted its card
- **THEN** a rail read leaves the session running

#### Scenario: A session crew did not start
- **WHEN** the user runs plannotator by hand on a closed proposal's page on mac-studio
- **THEN** no rail read ends it

#### Scenario: A batch card's sessions on another host
- **WHEN** the planner closed card `batch/3-1` on mac-studio, and the session for its unit `y` still runs on chuck-herdr-alpha
- **THEN** the next rail read ends `y`'s session there

### Requirement: The rail says which sessions it ended
After its groups and its open cards with no row, `crew rail` SHALL list each session it ended on that read, with its card key, the unit for a batch card's, its partition, its host and whether its card was closed or its row gone, and SHALL name each host whose sessions it could not check, with why. When it ended nothing and checked every host, it SHALL print nothing about sessions.

#### Scenario: Two sessions ended
- **WHEN** a rail read ends the sessions of `proposal/4` and `verify/x/20261009-1412`
- **THEN** the rail lists both, each with its host and why it was ended

#### Scenario: Nothing to end
- **WHEN** every recorded session's row and card are open
- **THEN** the rail says nothing about sessions

### Requirement: A session crew can't judge is kept
A rail read SHALL end no session whose row or card it cannot tell: none on a host that does not answer, which it names; no `verify/<unit>/…` session of a unit whose team's host did not answer; no session for a card closed, and no batch card's, while a host of the partition's run record did not answer; and no session started less than two minutes before its host is checked, which a later read judges.

#### Scenario: The team's host is asleep
- **WHEN** chuck-herdr-alpha does not answer
- **THEN** the rail ends no session there and none for its units' verify keys, names chuck-herdr-alpha as not checked, and ends what it can judge elsewhere

#### Scenario: The record is read in part
- **WHEN** a host of the partition's run record does not answer
- **THEN** the rail ends no session for a card closed and no batch card's session, and still ends a session whose proposal or verify row is gone

#### Scenario: A session just started
- **WHEN** the conductor starts a session for a report written after the rail's read of its kit began
- **THEN** that read leaves it running

## MODIFIED Requirements

### Requirement: The session ends when its card closes
When a crew agent closes or withdraws a card keyed with a row key, the session started for that key on that host SHALL be ended. `crew card end <key>` SHALL end it as well. crew SHALL end only a plannotator process it started for that key, and only while plannotator lists that process as serving that document; a key with no session ends nothing and is not an error. When plannotator's list of sessions cannot be read, crew SHALL end nothing, SHALL keep the key's session as recorded, and SHALL say so, so a later rail read ends it.

#### Scenario: A review card closed after approval
- **WHEN** the conductor approves unit `x` on the card's answer and closes card `review/x/abc1234` with `ack_answer`
- **THEN** the plannotator session for `review/x/abc1234` is no longer running, and its link no longer opens

#### Scenario: A card withdrawn when its row ends
- **WHEN** the planner withdraws card `proposal/4` because proposal 5 replaced it
- **THEN** the session for `proposal/4` is ended

#### Scenario: A process that is not crew's
- **WHEN** the process recorded for a key is no longer a plannotator session on that key's document
- **THEN** crew kills nothing and forgets the key's session

#### Scenario: plannotator's list can't be read
- **WHEN** the planner withdraws card `proposal/4` and `plannotator sessions --json` fails on its host
- **THEN** crew ends nothing, says it could not read plannotator's sessions, and keeps `proposal/4`'s session, which the next rail read ends
