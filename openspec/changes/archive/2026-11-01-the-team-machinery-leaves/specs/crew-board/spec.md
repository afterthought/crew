## RENAMED Requirements

- FROM: `### Requirement: The planner's and ops's bands show what a crossed team's places wait on them for`
- TO: `### Requirement: The planner's and ops's bands show what places wait on them for`

## ADDED Requirements

### Requirement: Construction shows a started bolt from the runner's records
The Construction lane SHALL show each started bolt as a ledger of its units, chores and fixes with the stages the runner's records give, its head line naming the host and the stream its work runs in, as the runner that took it reported them, and no slot. The board's JSON SHALL give each such ledger its host and stream.

#### Scenario: A started bolt's ledger
- **WHEN** `x` is started, deneb's runner keeping its kit with the stream `madswan`, `a` at `code 3/7` and `b` waiting on `a`
- **THEN** the board's Construction lane shows `x` on deneb in stream `madswan`, `a` at code 3/7 and `b` waiting on `a`, and no slot line

### Requirement: Construction shows each bolt in flight as a ledger, with no server for a started bolt's work
The Construction lane SHALL show each bolt in flight as a ledger: its head line with its repository and its kit's host, the number and state of its landing while one stands in sluice, and, once every unit and chore of it has merged and sluice is green at its head while not every one has landed, that it waits to land; while the run record has its landing queued and sluice's queue, read, shows no landing of it standing, that its landing is queued, with the number the run record holds; while it is landing again, that, with the submission sluice rejected before it; while sluice's rejection of its landing is at its head, that its landing was rejected and the bolt is open for work, with sluice's words, each state its own (bolt-teams "A landing queued holds its bolt's work"); once it has landed on main and its close was refused, that it landed and was not closed, with the words of its last refused close; each unit in plan order with its stage, its tasks done and total in code or verify, and the number and state of its merge while one stands in sluice; and each fix of the bolt with whether it has merged, and its merge's number and state while one stands. A started bolt's ledger SHALL show no dev server for the bolt or any of its work, whose places are Flume's, until the runner reports a place's addresses. The planner's band SHALL draw each bolt in flight as this ledger, its head line as the lane's, since ordering within a bolt, batches and amendments are the planner's; main-level ops's band SHALL draw the number and state of each landing while one stands in sluice, and the head line of each bolt whose close was refused.

#### Scenario: A unit in code
- **WHEN** unit a of bolt tenant-environments is in code with 1 of 2 tasks ticked, 
- **THEN** tenant-environments' ledger has a line for a saying code 1/2, and names no slot

#### Scenario: A started bolt's work shows no server
- **WHEN** `tenant-environments` is started, and a dev server runs in a worktree of its kit named for it
- **THEN** its ledger shows no URL for the bolt, its units or its fixes, and no note about one

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
- **THEN** `doctor-rows`'s head line, on the lane and in the planner's band, says its landing is queued as #412

#### Scenario: A landing rejected
- **WHEN** the run record has `doctor-rows`'s landing #412 refused at its present head for a conflict on `README.md`
- **THEN** `doctor-rows`'s head line, on the lane and in the planner's band, says its landing #412 was rejected at that head and the bolt is open for work, with sluice's words

#### Scenario: Landing again
- **WHEN** `doctor-rows`, rejected as #412, is queued again as #415, and sluice's queue shows no landing of it standing
- **THEN** its head line says it is landing again as #415, after #412 was rejected

#### Scenario: A close refused
- **WHEN** `doctor-rows` has landed on main and the run record's last `bolt.land` on it since then is refused, saying chore `tidy-rows` has not landed on main
- **THEN** `doctor-rows`'s head line, on the lane and in main-level ops's band, says it landed on main and was not closed, with those words, in the attention gutter

## MODIFIED Requirements

### Requirement: The planner's and ops's bands show what places wait on them for
`board.agent_views` SHALL give the planner's band each launched place that stopped short asking or waits on its caller, with its question or Flume's words, and main-level ops's band each fix of main and each take-main fix in flight with its stage; crew's mod SHALL draw both above the agent's prompt.

#### Scenario: A question in the planner's band
- **WHEN** `a`'s construct stopped short asking "Which partition's rail?"
- **THEN** madswan-planner's view lists `a` with that question, and the mod draws it

#### Scenario: A fix of main in ops's band
- **WHEN** `main--a-test-reads-its-fixture` is in code
- **THEN** madswan-ops's view lists it at code, and the mod draws it

## REMOVED Requirements

### Requirement: The board's JSON lists each partition's teams
**Reason**: Record 0047 move 5, record 0050 part 3: no teams; the page's team control goes with them.
**Migration**: None.

### Requirement: Each object in the board's JSON says whose it is
**Reason**: Record 0047 move 5, record 0050 part 3: no object belongs to a team.
**Migration**: None: an object's partition and kit say whose it is.

### Requirement: Construction shows a crossed team's bolts from the runner's records
**Reason**: Record 0050 part 3: no team is crossed or due, and the board's JSON lists no teams to give a path or stream.
**Migration**: "Construction shows a started bolt from the runner's records", added by this change.

### Requirement: Construction shows each held bolt as a ledger
**Reason**: Record 0047 move 5, record 0050 part 3: no team holds a bolt and no slot holds its work; and a started bolt's places are Flume's, where crew finds no dev server, until the runner reports a place's addresses (the user's ruling of 2026-10-31; `_open.md`).
**Migration**: "Construction shows each bolt in flight as a ledger, with no server for a started bolt's work", added by this change.
