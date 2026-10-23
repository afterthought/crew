## Purpose

The fleet page: every partition in the teams file at once, where it runs, the kits it builds and their mains, its teams and how busy each is, the Claude account each session runs on and what needs attention, each partition's page a link away.

## ADDED Requirements

### Requirement: The fleet page shows every partition at once
`crew page --fleet` SHALL write one page holding every partition in the teams file, in its order, each as a block of its own, from one read of all of them that is the read `crew board` makes. The page SHALL say when that read was made and, for each partition, the commit of its plan it was read at. A host that did not answer, or a plan that could not be read, SHALL be named in its partition's block and in what the command prints, and everything else SHALL still be shown.

#### Scenario: Three partitions
- **WHEN** the teams file holds madswan, swancloud and wldn and `crew page --fleet` is run
- **THEN** the page holds a block for madswan, then swancloud, then wldn, and says as of when and which commit of each plan

#### Scenario: A host that does not answer
- **WHEN** one of wldn's hosts does not answer as the fleet page is made
- **THEN** wldn's block names that host as not answering, the command prints it, and the other partitions and wldn's other hosts are shown in full

### Requirement: Each partition shows where it runs and on which account
A partition's block SHALL name each host its teams and main level run on, one that did not answer marked so, and under each host each herdr session an agent of the partition runs in: the teams in it, its main-level agents in it (design agent, planner, ops, operator) and its dispatcher there, and the Claude account the hosts file gives the session. A session whose entry names no account SHALL say so, never be shown blank. A session no agent of the partition runs in SHALL not be shown.

#### Scenario: Two sessions on two accounts
- **WHEN** swancloud's main level runs in deneb's session swancloud on account madswan and its team crw-6 in deneb's session swancloud-2 on account madswan-2
- **THEN** swancloud's block shows deneb with session swancloud, its design agent, planner, ops and operator, account madswan, and session swancloud-2, crw-6, account madswan-2

#### Scenario: No account named
- **WHEN** a team's session has no account in the hosts file
- **THEN** that session says no account is named for it in the hosts file

### Requirement: Each partition shows its kits and their mains
A partition's block SHALL list each kit its teams build, once, with the teams building it; the last landing on its main in the run record's window, its bolt, the commit main held after it, when and who landed it, or that none is in the window; and what is queued for that main: the bolts of that kit that wait to land, with whether their landing card is open, the bolts of it in construction, and how many bolts of it are planned and units of it are queued.

#### Scenario: A kit with a landing and a bolt waiting
- **WHEN** crew's main last took bolt a at 3f2c1d0 two days ago, bolt b of crew waits to land with its card open, and one unit of crew is queued
- **THEN** crew's line says it last landed a at 3f2c1d0 with when and who landed it, that b waits to land with its card open, and that one unit is queued

#### Scenario: A kit with no landing in the window
- **WHEN** paymaster has had no landing in the run record's window
- **THEN** paymaster's line says no landing is in the window, never a blank

### Requirement: Each partition shows its teams and how busy each is
A partition's block SHALL list each team, in the teams file's order, with its host and session, the bolt it holds with its units' pips, how many have merged and its state, or that it holds none; how many of its slots are at work; and what its conductor waits on: the stages running in its slots, its bolt's landing on the user's word, or nothing.

#### Scenario: A team whose bolt waits to land
- **WHEN** crw-5's bolt has every unit merged and its proof green, and no stage runs
- **THEN** crw-5's line says its bolt waits to land and its conductor waits on the landing, on the user's word

#### Scenario: A team with no bolt
- **WHEN** crw-4 holds no bolt
- **THEN** crw-4's line says it holds no bolt, its slots free and its conductor waiting on nothing

### Requirement: Each team shows what each of its slots is doing
Each of a team's slots SHALL be shown at work on a stage, naming the stage and the unit, chore or fix; holding work with no stage running; or free. A slot SHALL be at work while the run record holds a stage started in it and not yet ended.

#### Scenario: A team at work
- **WHEN** crw-6 holds bolt b, its unit-1 runs the code stage of unit x and unit-2 holds unit y whose verify has ended, and its other slots are free
- **THEN** crw-6's line shows b with its pips, unit-1 at work on code of x, unit-2 holding y with no stage running, two slots free, 1 of 4 slots at work, and that its conductor waits on one stage

### Requirement: Each partition shows what needs attention
A partition's block SHALL show its attention items in the words the board uses for them, and how many of its cards are open, or that nothing needs attention.

#### Scenario: A bolt still in the plan once landed
- **WHEN** a bolt of swancloud has every unit landed and is still in the plan
- **THEN** swancloud's block carries the board's attention line for that bolt

### Requirement: Each partition's page is a link away
Each partition's name on the fleet page SHALL link to that partition's page, and each team to its dock on that page, in the layout of the fleet page's own file: `<label>.html` beside it when the fleet page's file is `index.html`, as the board is served; `<label>/page.html` beside it when its file is `page.html`, crew's own layout. For any other name the partitions SHALL be named and not linked, and the command SHALL say so.

#### Scenario: Served beside the partitions' pages
- **WHEN** `crew page --fleet --out <folder>/index.html` writes the page
- **THEN** wldn's name links to `wldn.html`, and crw-6 to swancloud's page with crw-6's dock open

#### Scenario: A name that says no layout
- **WHEN** `crew page --fleet --out <folder>/fleet.html` writes the page
- **THEN** the partitions are named and not linked, and the command prints a line saying so

### Requirement: The fleet page is written beside the partitions' pages
Written with no `--out`, the fleet page SHALL be `page.html` in crew's state folder, beside each partition's folder.

#### Scenario: Crew's own layout
- **WHEN** `crew page --fleet` is run with no `--out`
- **THEN** it writes `~/.local/state/crew/page.html` and prints that path, and wldn's name links to `wldn/page.html`

### Requirement: The fleet page is one self-contained file that answers nothing
The fleet page SHALL be one file that holds its own data, style and script and fetches nothing, light and dark as the viewer prefers, its blocks side by side on a desktop and stacked under 760 px. Every text it shows from the state SHALL be set as text, never as markup. It SHALL hold no control that answers a card or moves anything, and making it SHALL write nothing to any partition's state.

#### Scenario: Offline
- **WHEN** the fleet page is opened from disk with the network off
- **THEN** every block draws in full and the browser makes no request

#### Scenario: Typed words
- **WHEN** the words of an attention item, a host's error as it was read, hold `</script><b>here</b>`
- **THEN** the page shows those characters as they are, and its data block is not ended by them
