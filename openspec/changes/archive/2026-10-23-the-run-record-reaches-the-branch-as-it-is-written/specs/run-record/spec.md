## ADDED Requirements

### Requirement: Every entry reaches the branch as it is written
Once crew appends an entry to the host's run record, the same command SHALL push it to `runs/<host>/<day>.rec` on the partition's branch of its state repository, as its own commit from that host, by the procedure every write to the branch takes. The commit SHALL change that day's file alone, adding the entry to what the branch holds. Only a host SHALL write its own files, entries SHALL be added and never removed, and pushing an entry the branch holds SHALL change nothing.

#### Scenario: A tell
- **WHEN** an agent on the box tells another agent
- **THEN** before the command returns, `wldn/main` has a commit from the box adding the tell's entry to `runs/chuck-herdr-alpha/<day>.rec`, and no other file

#### Scenario: A plan write
- **WHEN** the planner adds a unit to the queue on mac-studio
- **THEN** the write's commit changes the plan alone, and the next commit on the branch adds its `unit.add` entry, which names the write's commit

#### Scenario: Two hosts at once
- **WHEN** mac-studio and the box each push an entry of wldn at the same moment
- **THEN** both entries are on `wldn/main`, each in its host's file, the one whose push was refused replayed on the new tip

#### Scenario: A host is rebuilt
- **WHEN** a host loses its local run record
- **THEN** every entry it wrote before is still on the branch, and its next entry is added beside them

### Requirement: An entry that did not reach the branch goes with the host's next
When an entry cannot be pushed, crew SHALL say so once on standard error, naming the entry, the branch and why, and the command SHALL do its work and exit as it would have. The entry SHALL stay in the host's file. The host's next push of the partition's record, by its next entry or by `crew events --push`, SHALL first push each of the host's entries the branch lacks, each as its own commit, oldest first. `crew events --push` SHALL say when the branch already holds every entry the host has.

#### Scenario: GitHub out of reach
- **WHEN** a conductor on the box starts a stage while github.com cannot be reached
- **THEN** the stage starts, the command says once that its entry did not reach `wldn/main` and why, and the entry is in the box's file

#### Scenario: The next entry
- **WHEN** the box's next entry of wldn is pushed once github.com answers again
- **THEN** `wldn/main` gains the missed entry's commit, then the new entry's, and nothing is pushed twice

#### Scenario: By hand
- **WHEN** `crew events --push --label wldn` runs on the box after a missed push
- **THEN** each entry the branch lacks is pushed as its own commit, and run again it says there is nothing left to push

#### Scenario: An entry that fails its check
- **WHEN** an entry in the host's file is cut short, so the day's file would fail `recfix --check`
- **THEN** nothing of the record is pushed, the command names the file and why on standard error, and the act it recorded stands

### Requirement: Entries are read from the flywheel's branch alone
`crew events [--label <label>] [--about <object>] [--since <time>] [--json]` and `crew trace <object>` SHALL read the run record from the partition's branch of its state repository, and SHALL ask no host for it. When the branch cannot be read they SHALL say so, naming the branch.

#### Scenario: A host is asleep
- **WHEN** macbook-pro, which wrote entries of wldn and pushed them, does not answer
- **THEN** `crew events --label wldn` prints its entries with the other hosts' in time order, and names no host

#### Scenario: Two hosts
- **WHEN** `crew events --label wldn` runs on mac-studio while wldn's teams run on the box
- **THEN** the box's entries and mac-studio's are printed together in time order, and no ssh is made for them

#### Scenario: One object
- **WHEN** `crew events --about unit/<unit>` runs
- **THEN** only entries naming that unit in `On` or `From` are printed

#### Scenario: The branch cannot be read
- **WHEN** `crew events --label wldn` runs while the state repository cannot be fetched
- **THEN** it names `wldn/main` as not read, and why

## MODIFIED Requirements

### Requirement: Entries can be followed as they are written
`crew events --follow` SHALL print each entry of the partition as it reaches the partition's branch, one line per entry, reading the branch again every five seconds, until it is interrupted. It SHALL ask no host for entries.

#### Scenario: Following a bolt team
- **WHEN** `crew events --follow --label wldn` is running and a conductor starts a stage on the box
- **THEN** that entry's line appears once its commit is on `wldn/main`, without the command being run again

#### Scenario: A host is asleep
- **WHEN** `crew events --follow --label wldn` starts while macbook-pro does not answer
- **THEN** it follows the branch as before, and starts nothing on macbook-pro

## REMOVED Requirements

### Requirement: Entries are gathered from every host
**Reason**: Record 0029 and `read.5`: the run record is read from the flywheel's branch alone, and no host is asked for it.
**Migration**: "Entries are read from the flywheel's branch alone"; every entry is there once written ("Every entry reaches the branch as it is written").

### Requirement: The run record is carried to the state repository
**Reason**: Record 0029: an entry reaches the branch as its own commit when it is written, so a write has nothing left to carry.
**Migration**: "Every entry reaches the branch as it is written" and "An entry that did not reach the branch goes with the host's next"; `crew events --push` pushes what a failed push left.
