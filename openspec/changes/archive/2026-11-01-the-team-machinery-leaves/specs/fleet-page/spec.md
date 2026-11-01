## ADDED Requirements

### Requirement: Each partition shows where its main level runs and on which account
A partition's block SHALL name each host the board asked for it, its main level's and its runners', one that did not answer marked so, and its main level's host, marked not asked where the board did not ask it; and under each host each herdr session an agent of the partition runs in: its main-level agents in it (design agent, planner, ops, operator), and the Claude account the hosts file gives the session. A session whose entry names no account SHALL say so, never be shown blank. A session no agent of the partition runs in SHALL not be shown, and no team SHALL be named.

#### Scenario: Two sessions of one main level
- **WHEN** swancloud's design agent, planner and ops run in deneb's session swancloud on account madswan, and its operator in deneb's session swancloud-3, which names no account
- **THEN** swancloud's block shows deneb with session swancloud, its design agent, planner and ops, account madswan, and session swancloud-3, its operator, saying no account is named for it in the hosts file

#### Scenario: A runner's host
- **WHEN** wldn's runner on chuck-herdr-alpha takes its work and its main level runs on mac-studio, which the board did not ask
- **THEN** wldn's block shows chuck-herdr-alpha answered with no session under it, and mac-studio not asked with session wldn and its main-level agents

### Requirement: Each partition shows the kits its plan and landings name, and their mains
A partition's block SHALL list each of its kits, the repositories its plan and its landings name, once; the last landing on its main in the run record's window, its bolt, the commit main held after it, when and who landed it, or that none is in the window; and what is queued for that main: the bolts of that kit that wait to land, with whether their landing card is open, the bolts of it in construction, and how many bolts of it are planned and units of it are queued. No kit SHALL name a team that builds it.

#### Scenario: A kit with a landing and a bolt waiting
- **WHEN** crew's main last took bolt a at 3f2c1d0 two days ago, bolt w of crew waits to land with its card open, and one unit of crew is queued
- **THEN** crew's line says it last landed a at 3f2c1d0 with when and who landed it, that w waits to land with its card open, and that one unit is queued, and names no team

#### Scenario: A kit with no landing in the window
- **WHEN** swancloud has had no landing in the run record's window
- **THEN** swancloud's line says no landing is in the window, never a blank

### Requirement: Each partition's page is a link away, and a subscription's dock on it
Each partition's name on the fleet page SHALL link to that partition's page, and each partition a subscription names to that page with the subscription's dock open, in the layout of the fleet page's own file: `<label>.html` beside it when the fleet page's file is `index.html`, as the board is served; `<label>/page.html` beside it when its file is `page.html`, crew's own layout. For any other name the partitions SHALL be named and not linked, and the command SHALL say so.

#### Scenario: Served beside the partitions' pages
- **WHEN** `crew page --fleet --out <folder>/index.html` writes the page
- **THEN** wldn's name links to `wldn.html`, and swancloud under the madswan subscription to swancloud's page with madswan's dock open

#### Scenario: A name that says no layout
- **WHEN** `crew page --fleet --out <folder>/fleet.html` writes the page
- **THEN** the partitions are named and not linked, and the command prints a line saying so

### Requirement: A subscription shows the main levels' sessions and partitions on it beside its use
A subscription SHALL list each session the hosts file gives its account, by host, with crew's agents in it, the main levels' roles, and SHALL name the partitions whose agents run in those sessions. A session no crew agent runs in SHALL be listed as running none. Nothing SHALL be computed from the use and the work together, and no team or slot SHALL be named.

#### Scenario: Two main levels on one subscription
- **WHEN** madswan's main level runs in deneb's session madswan and swancloud's design agent, planner and ops in deneb's session swancloud, both on account madswan
- **THEN** madswan lists deneb's sessions madswan, with madswan's design agent, planner, ops and operator, and swancloud, with swancloud's design agent, planner and ops, and names the partitions madswan and swancloud

#### Scenario: A main-level session that runs nothing
- **WHEN** deneb's session agentplot-2 is on account madswan and no agent of any partition runs there
- **THEN** madswan lists deneb's agentplot-2 as running no crew agent

## REMOVED Requirements

### Requirement: Each partition shows its teams and how busy each is
**Reason**: Record 0047 move 5, record 0050 part 3: no teams.
**Migration**: None: a partition's work shows on its own page.

### Requirement: Each team shows what each of its slots is doing
**Reason**: Record 0047 move 5, record 0050 part 3: no slots.
**Migration**: None.

### Requirement: Each partition shows where it runs and on which account
**Reason**: Record 0047 move 5, record 0050 part 3: no team or dispatcher runs in a session, so a block names its main level's sessions alone.
**Migration**: "Each partition shows where its main level runs and on which account", added by this change.

### Requirement: Each partition shows its kits and their mains
**Reason**: Record 0047 move 5, record 0050 part 3: no team builds a kit; a partition's kits are the repositories its plan and its landings name (design Decision 3).
**Migration**: "Each partition shows the kits its plan and landings name, and their mains", added by this change.

### Requirement: Each partition's page is a link away
**Reason**: Record 0047 move 5, record 0050 part 3: no team has a dock to link to.
**Migration**: "Each partition's page is a link away, and a subscription's dock on it", added by this change.

### Requirement: A subscription shows the sessions and partitions on it beside its use
**Reason**: Record 0047 move 5, record 0050 part 3: no team's slots or conductor's wait to show.
**Migration**: "A subscription shows the main levels' sessions and partitions on it beside its use", added by this change.
