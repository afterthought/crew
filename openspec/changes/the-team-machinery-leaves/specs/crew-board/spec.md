## MODIFIED Requirements

### Requirement: Construction shows each held bolt as a ledger
The Construction lane SHALL show each bolt in flight as a ledger: its head line with its repository and its kit's host, the number and state of its landing while one stands in sluice, and, once every unit and chore of it has merged and sluice is green at its head while not every one has landed, that it waits to land; while the run record's last `bolt.submit` on the bolt has its landing queued and sluice's queue, read, shows no landing of it standing, that its landing is queued, with the number the run record holds; once it has landed on main and its close was refused, that it landed and was not closed, with the words of its last refused close; each unit in plan order with its stage, its tasks done and total in code or verify, the number and state of its merge while one stands in sluice, and the URL of the dev server running in its place; each fix of the bolt with whether it has merged, its merge's number and state while one stands, and its server; and the bolt's own server at the foot. Main-level ops's band SHALL draw the head line of each bolt whose close was refused.

#### Scenario: A unit in code
- **WHEN** unit a of bolt tenant-environments is in code with 1 of 2 tasks ticked, 
- **THEN** tenant-environments' ledger has a line for a saying code 1/2, and names no slot

#### Scenario: No server running
- **WHEN** a unit's worktree has no dev server running, or its kit has no dev server naming
- **THEN** its line shows no URL and no note about it

#### Scenario: A bolt waiting to land beside the one being built
- **WHEN** `doctor-rows` has every unit merged and sluice green at its head, and `ssh-fix` of the same kit has a unit in code
- **THEN** the lane shows `doctor-rows`'s head line saying it waits to land, and `ssh-fix`'s ledger beside it

#### Scenario: A merge standing in sluice
- **WHEN** unit a of bolt tenant-environments has its merge `#41` under test on `bolt/tenant-environments`
- **THEN** a's line in the lane says `#41 under test`

#### Scenario: A landing standing in sluice
- **WHEN** `doctor-rows`'s landing `#355` is queued on its kit's main
- **THEN** `doctor-rows`'s head line in the lane and in main-level ops's band says `landing #355 queued`

#### Scenario: A queue that can't be read
- **WHEN** sluice's record of the queue could not be read on swb-1's host
- **THEN** tenant-environments' head line says its submissions can't be read, and no line shows a number, though the run record has its landing queued

#### Scenario: A landing recorded queued that sluice no longer has standing
- **WHEN** the run record's last `bolt.submit` on `doctor-rows` is queued as submission 412, and sluice's queue, read on its kit's host, shows no landing of it standing
- **THEN** `doctor-rows`'s head line, on the lane and in main-level ops's band, says its landing is queued as #412

#### Scenario: A close refused
- **WHEN** `doctor-rows` has landed on main and the run record's last `bolt.land` on it since then is refused, saying chore `tidy-rows` has not landed on main
- **THEN** `doctor-rows`'s head line, on the lane and in main-level ops's band, says it landed on main and was not closed, with those words, in the attention gutter

## REMOVED Requirements

### Requirement: The board's JSON lists each partition's teams
**Reason**: Record 0047 move 5, record 0050 part 3: no teams; the page's team control goes with them.
**Migration**: None.

### Requirement: Each object in the board's JSON says whose it is
**Reason**: Record 0047 move 5, record 0050 part 3: no object belongs to a team.
**Migration**: None: an object's partition and kit say whose it is.
