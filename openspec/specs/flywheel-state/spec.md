# flywheel-state Specification

## Purpose
Keeps each flywheel's own records (its plan, its moves, its run record, and what later capabilities add) in a state repository apart from the design, on a branch of its own, written only through crew, so that several flywheels can share one repository without meeting.

## Requirements

### Requirement: A flywheel's state is one branch of its state repository
Each partition SHALL name one state repository in the teams file, as `state`. The partition's flywheel SHALL keep its state as files on the branch `<label>/main` of that repository. The branch SHALL hold no other flywheel's files and SHALL share no history with another flywheel's branch.

#### Scenario: Willdan's flywheel
- **WHEN** the `wldn` partition names `WilldanGroup/crew-state` as its state repository
- **THEN** its plan, moves and run record are files on the branch `wldn/main` of that repository

#### Scenario: Two flywheels of one organisation
- **WHEN** `madswan` and `swancloud` both name `afterthought/crew-state`
- **THEN** each has its own branch, `madswan/main` and `swancloud/main`, and neither branch holds a commit of the other's

### Requirement: The state is written only through crew, one commit a write
Every write to a flywheel's branch SHALL be made by a crew command. It SHALL fetch the branch over https into crew's own bare cache, apply itself to the tip, check each file it changed, commit without touching any working tree, and push without force. A rejected push SHALL have the write applied again to the new tip, up to five times. A write that changes several files SHALL be one commit.

#### Scenario: Two hosts write at once
- **WHEN** a write from the box and a write from mac-studio reach the same flywheel's branch together
- **THEN** both land, one after the other, and nothing is merged

#### Scenario: A write of two files
- **WHEN** a command changes the plan and appends a move
- **THEN** one commit holds both, and no reader sees the plan change without the move

#### Scenario: A file that fails its check
- **WHEN** a write would leave a recutils file that fails `recfix --check` or crew's rules
- **THEN** nothing is pushed, and the command says which file and why

### Requirement: A commit names its run-record entry
Each commit crew makes on a flywheel's branch SHALL carry, in its message, the id of a run-record entry as a `Crew-Entry:` trailer. A commit that is an act's, such as a plan write, SHALL name the entry that describes it, and that entry SHALL name the commit. A commit that adds an entry to the run record SHALL name the entry it adds, and SHALL change nothing but that entry's day file.

#### Scenario: From a commit to its entry
- **WHEN** a plan write's commit on `wldn/main` is read
- **THEN** its `Crew-Entry` id is the `Id` of one run-record entry, whose `Commit` is that commit

#### Scenario: An entry's own commit
- **WHEN** the commit that follows a plan write on `wldn/main` is read
- **THEN** its `Crew-Entry` id is the `Id` of the entry it adds to `runs/<host>/<day>.rec`, its subject ends with ` (<agent>)`, and it changes no other file

### Requirement: Flywheels in one repository never meet
crew SHALL fetch and push only the branch of the flywheel a command acts for. A write to one flywheel SHALL never be refused, delayed or replayed because another flywheel wrote.

#### Scenario: Two flywheels write at the same moment
- **WHEN** `madswan` and `swancloud` each write their plan at the same moment
- **THEN** each write's first push succeeds

#### Scenario: Reading one flywheel
- **WHEN** a command reads wldn's plan
- **THEN** crew fetches `wldn/main` and no other branch

### Requirement: A flywheel's branch is created, and adopts what it had
`crew state init <label>` SHALL create `<label>/main` in the partition's state repository with an empty plan and an empty moves file. Where a blueprints repo of the partition holds `plan/<label>`, the branch SHALL start from that plan's history, and the moves in the first blueprints repo's `signals/moves.rec` SHALL be copied with the commit they were read at. Run again, it SHALL change nothing.

#### Scenario: Willdan's plan is adopted
- **WHEN** `crew state init wldn` runs while willdan-blueprints holds `plan/wldn` and two moves
- **THEN** `wldn/main` holds the same bolts and units, its history reaches back to the plan's first commit, and `moves.rec` holds both moves

#### Scenario: A partition with two plans
- **WHEN** `crew state init madswan` runs while afterthought/blueprints and agentplot/blueprints each hold `plan/madswan`
- **THEN** `madswan/main` holds one plan with the bolts and units of both, the second plan's records added in one commit that names where they came from

#### Scenario: Two plans share a name
- **WHEN** the two plans being joined both hold a bolt or a unit of the same name
- **THEN** init is refused, naming it, and nothing is written

#### Scenario: Run twice
- **WHEN** `crew state init wldn` runs again
- **THEN** nothing is written, and it says the branch exists and at which commit

### Requirement: A flywheel's state is plain files anyone with access can read
A clone of a flywheel's branch SHALL be recutils files that `recsel` and `recfix` read with no crew command, and each commit's subject SHALL say what the write did and who asked.

#### Scenario: Reading with recutils
- **WHEN** the user clones the branch `wldn/main` and runs `recsel -t Unit plan.rec`
- **THEN** the plan's units are printed

### Requirement: crew asks a host's runner for work by requests on the flywheel's branch
crew SHALL write every request for a host's runner as a record of `requests.rec` on the flywheel's branch: a launch of a place, or a retry, drop or priority of one it launched. Each SHALL be numbered once, appended by a crew command in the commit of the plan write that occasions it, checked by `recfix --check` and crew's own rules, and never changed or removed.

#### Scenario: Never renumbered
- **WHEN** `requests.rec` holds requests 1 to 7 and a drop is written
- **THEN** it is request 8, and requests 1 to 7 are as they were

### Requirement: A launch names everything the runner passes to Flume
A launch of a kit's work SHALL name the work it serves, its repository as the plan names it, its kind, name and base, its priority, intent and recipient, and its brief, and SHALL name no host or stream, a runner whose configuration names its repository taking it, in the stream its host's Flume configuration maps the repository to; a launch of a role's work SHALL also name the host and stream its role runs in. A launch MAY name launches that must land first and a held submission. A retry, drop or priority SHALL name the launch it acts on and no host. crew's rules SHALL refuse a request that lacks what its act needs or names what its act does not take.

#### Scenario: A launch with no stream
- **WHEN** a bolt's start appends a launch of a kit's work naming no `Stream`
- **THEN** it is appended, a runner whose configuration names the kit's repository giving its stream

#### Scenario: A kit's launch naming a host
- **WHEN** a bolt's start would append a launch naming a `Host` or a `Stream`
- **THEN** the write is refused by crew's rules and the branch is unchanged

#### Scenario: A retry of nothing
- **WHEN** a retry would name request 9, which is no launch
- **THEN** the write is refused naming request 9

### Requirement: crew reads each host's runner from that runner's own branch
crew SHALL read a host's runner from `<label>/runner/<host>` of the partition's state repository, fetched with `<label>/main` in one fetch, and SHALL never write it: its `runner.rec` saying a runner serves the partition there, its `answers.rec` where each request stands, and its `places.rec` Flume's status of each place as Flume gave it.

#### Scenario: One fetch
- **WHEN** a command reads the plan and the runners
- **THEN** it fetches the state repository once, `<label>/main` and `<label>/runner/*` together

### Requirement: A runner's branch that can't be read hides only the work no runner crew read has taken
A host whose runner branch recfix refuses, or crew can't read, SHALL hide only the work no runner crew read has taken, which reads unknown, naming that runner; work a runner crew read has taken SHALL read as it stands. A host with no runner branch is no runner, and hides nothing.

#### Scenario: Two hosts, one silent
- **WHEN** `madswan/runner/deneb` holds an answer and a place for request 3, and `madswan/runner/alpha` can't be read
- **THEN** request 3's work reads its stage from deneb's place, and work deneb has not taken reads unknown, naming alpha's runner

### Requirement: A kit's work is taken by a runner whose configuration names its repository
crew SHALL record a kit's work against its repository and look up no kit's host: a runner whose configuration names the repository takes it, under a lease and while its host's stream has room, and launches it there, in the stream its host's Flume configuration maps the repository to. crew SHALL read a launched piece's stage from the runner whose answers hold its launch, launching while none does; where two runners hold it, or none crew read holds it and a runner could not be read, the piece SHALL read unknown, naming them. Where crew must act on or say where a bolt's work runs, its landing, its reads of the bolt and its kit, its reading and preview, the sweep after a landing or a drop, its site row and its ledger's host and stream, it SHALL read what the runner reported for the work it took: the host whose runner took the newest of the bolt's launches taken, and the kit's folder there and the stream its work runs in as Flume's status of that runner's place names them; while no runner has taken any of the bolt's own work, where the runner that took its kit's newest work taken reported the kit. A bolt or kit no runner has reported, or whose newest launch two runners took, SHALL be named as unread, nothing of it landed, and every other bolt read as it stands.

#### Scenario: The runner that took the work
- **WHEN** deneb's runner answers launch 1 of crew's unit `a` on `bolt/x` and carries Flume's status of its place, naming its repository `/w/crew` and its stream `madswan`
- **THEN** `a`'s stage is read from deneb's records, and `x` is read and landed on deneb in `/w/crew`, its ledger saying deneb and `madswan`

#### Scenario: A bolt none of whose own work is taken
- **WHEN** `x` is started and no runner has taken its launches, and deneb's runner took crew's work on another bolt, its place naming `/w/crew`
- **THEN** `x` is read and landed on deneb in `/w/crew`

#### Scenario: Taken by two runners
- **WHEN** deneb's and chuck-herdr-alpha's runners both answer launch 1
- **THEN** its piece reads unknown naming both, and crew can't tell where `x` runs, landing nothing of it

#### Scenario: No runner has reported the kit
- **WHEN** no runner has taken any launch of crew's work
- **THEN** a landing of `x` is refused naming that no runner has reported taking its work, and a piece of it reads launching

### Requirement: What comes before a runner takes a kit's work is done on the main-level host
What crew does on a kit before any runner has taken the work in hand, a start's `sluice branch create` and its read of the kit's policy and its host's sluice, a new unit's or chore's name checked against the kit's main, a bolt never started landed by its close alone, the design agent's records and a proposal's records read in the kit, the board's explorations on the kit's main, and the main level's folders of the partition's kits, SHALL be done in the checkout the partition's main-level host keeps of the kit, as that host's spaces in the hosts file keep it, by its forge address or, for a kit the plan names by its name alone, by that name; it SHALL be refused, naming the host and the kit, where that host keeps none, or keeps two repositories by the kit's name, and nothing SHALL be asked of a runner for it.

#### Scenario: A kit's first bolt is started
- **WHEN** `crew bolt start x` runs for crew's first bolt, no runner has taken any of crew's work, and deneb, madswan's main-level host, keeps `afterthought/crew` at `/d/madswan/crew/main`
- **THEN** sluice makes `bolt/x` from main in `/d/madswan/crew/main` on deneb, the policy there is read, and the start goes on as any start

#### Scenario: A kit the main-level host keeps no checkout of
- **WHEN** `crew bolt start x` runs and deneb's spaces keep no checkout of crew
- **THEN** it is refused naming deneb and crew, the plan is unchanged and no branch is made

#### Scenario: A unit's name and a record
- **WHEN** the planner adds unit `a` to crew and the design agent runs `crew record crew 53 --proposed`
- **THEN** `a`'s name is checked against crew's main, and record 0053 read, in `/d/madswan/crew/main` on deneb

#### Scenario: The main level's kit folders
- **WHEN** madswan's plan names crew and sluice, deneb keeps both and a role of madswan's main level starts there
- **THEN** it may reach deneb's checkouts of crew and sluice, and a kit its plan names that deneb keeps none of is left out
