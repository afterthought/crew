# run-record Specification

## Purpose
Keeps a record of every act of crew's that moves work, written where the act happened, so that a person can read what happened to a bolt, a unit or a signal, who did it and what it led to, without asking an agent.

## Requirements

### Requirement: Every command that moves work leaves an entry
Every crew command that changes the plan, a signal or its move, a unit's approval or stage, a fix, or an agent's or a team's sessions, and every `crew tell`, SHALL append one entry for each such act to the run record of the partition it acts for, after the act is done. A command that only reads SHALL append nothing. An entry SHALL give its id, the time in UTC, the host crew ran on, who asked, the act, and the objects it acted on.

#### Scenario: A plan write
- **WHEN** the planner adds a unit to the queue
- **THEN** the run record gains one entry whose act is `unit.add`, naming the unit and the queue it went to

#### Scenario: A command that does several things
- **WHEN** `crew bolt give swb-1` writes the plan, restarts the team's conductor and ops, and greets the conductor
- **THEN** the run record gains an entry for the give, one for each restart and one for the greeting

#### Scenario: A command that only reads
- **WHEN** `crew bolts`, `crew status` or `crew sites` runs
- **THEN** no entry is written

### Requirement: An entry names who asked and the session behind it
An entry's `By` SHALL be the name of the agent crew started that ran the command, else `<user>@<host>`. Its `Session` SHALL be the host and the Claude session id herdr reports for that agent when the command runs, and SHALL be absent for the user at a shell or when herdr reports none. A command crew runs again on another host SHALL carry both there, so the entry names the one who asked and not the host that did the work.

#### Scenario: A conductor's command
- **WHEN** `swb-2-conductor` on the box starts a unit's construct stage
- **THEN** the entry's `By` is `swb-2-conductor` and its `Session` is the box and that conductor's Claude session id

#### Scenario: The user at a shell
- **WHEN** the user runs `crew unit approve` in a terminal on mac-studio
- **THEN** the entry's `By` is `chuck@mac-studio` and it has no `Session`

#### Scenario: A command run on another host
- **WHEN** the operator agent on mac-studio runs `crew unit run` for a team on the box
- **THEN** the entry is written on the box, its `Host` is the box, and its `By` and `Session` name the operator agent and its session on mac-studio

### Requirement: An entry names the commit it wrote
When the act wrote a commit, its entry SHALL name it as `<owner>/<name>@<sha>`: the plan's commit for a plan write, the signals repo's for a signal or a move, the kit's for an approval. An act that wrote no commit SHALL carry none.

#### Scenario: An approval
- **WHEN** `crew unit approve` records the review on `unit/<unit>`
- **THEN** the entry names the kit and that commit

#### Scenario: A tell
- **WHEN** `crew tell` prompts an agent
- **THEN** the entry carries no commit

### Requirement: An entry names what it acted on and what that came from
An entry's `On` fields SHALL name each object the act touched, and its `From` fields each object the act came from, as typed names: `unit/<unit>`, `bolt/<bolt>`, `queue/<kit>`, `signals/<id>`, `team/<team>`, `agent/<name>`, `stage/<unit>/<stage>`, `fix/<bolt>/<name>`.

#### Scenario: A unit queued from a signal
- **WHEN** a unit is added with `--signal <id>`
- **THEN** the `unit.add` entry has `On: unit/<unit>` and `From: signals/<id>`, and the route move's entry has `On: signals/<id>` and `On: unit/<unit>`

#### Scenario: A stage
- **WHEN** a unit's code stage starts in slot 2 of swb-1
- **THEN** the entry has `On: stage/<unit>/code`, `On: unit/<unit>` and `On: agent/swb-1-unit-2`

### Requirement: A refusal is an entry
When crew refuses a command that would have moved work, it SHALL append an entry with the act refused, the objects named and crew's reason in `Refused`.

#### Scenario: Code before review
- **WHEN** `crew unit run <unit> code` is refused because the unit is in review
- **THEN** the run record gains an entry with act `stage.start`, `On: unit/<unit>`, and the refusal's words in `Refused`

### Requirement: An entry holds no text anyone typed
An entry's `Why` SHALL be the subject crew itself composes from the names of things. An entry SHALL NOT hold the text of a tell, the words given to a stage, an intent, a goal, a reason or an excerpt. A tell's entry SHALL record the sender, the recipient and the length of the text.

#### Scenario: A tell
- **WHEN** a conductor tells the design agent a question in the user's words
- **THEN** the entry names both agents and the number of characters sent, and the question appears nowhere in the run record

### Requirement: The run record is files on the host, appended and never rewritten
Entries SHALL be recutils records in `~/.local/state/crew/<label>/runs/<host>/<date>.rec` on the host where the command ran, one file per UTC day, each append one write. crew SHALL never rewrite or remove an entry. A failed append SHALL be reported on standard error and SHALL NOT change the command's result or exit status.

#### Scenario: After a restart
- **WHEN** a host restarts
- **THEN** every entry written before it is still in its file

#### Scenario: The record cannot be written
- **WHEN** the run record's directory cannot be written
- **THEN** the command does its work and exits as it would have, with one line on standard error saying the entry was not recorded

#### Scenario: Read with recutils alone
- **WHEN** `recsel -e "On = 'unit/<unit>'"` is run over a host's run-record files
- **THEN** it prints that unit's entries, with no crew command involved

### Requirement: Entries are gathered from every host
`crew events [--label <label>] [--about <object>] [--since <time>] [--json]` SHALL read the run record on the flywheel's branch of its state repository, then ask every host where the partition's teams, main level and operator sessions run, one call per host, for the entries it has not yet carried, and print them all in time order. A host that does not answer SHALL be named, and its entries shown as far as it had carried them.

#### Scenario: Two hosts
- **WHEN** `crew events --label wldn` runs on mac-studio while wldn's teams run on the box
- **THEN** the box's entries and mac-studio's are printed together in time order

#### Scenario: A host is asleep
- **WHEN** a Mac holding entries does not answer
- **THEN** the entries it had carried are printed with the other hosts', and the Mac is named as not answering

#### Scenario: One object
- **WHEN** `crew events --about unit/<unit>` runs
- **THEN** only entries naming that unit in `On` or `From` are printed

### Requirement: Entries can be followed as they are written
`crew events --follow` SHALL print each entry of the partition, from every host it can reach, as it is appended, one line per entry, until it is interrupted.

#### Scenario: Following a bolt team
- **WHEN** `crew events --follow --label wldn` is running and a conductor starts a stage on the box
- **THEN** that entry's line appears without the command being run again

### Requirement: One object's history is read from the entries alone
`crew trace <object>` SHALL print, in time order, every entry that names the object, and every entry of the objects it came from and the objects that came from it, each line giving the time, the act, who asked, the host, the commit, and the session to open. It SHALL read only the run record. An object no entry names SHALL be reported as such with a non-zero exit.

#### Scenario: A unit from a signal
- **WHEN** `crew trace unit/<unit>` runs for a unit queued from a signal and since merged
- **THEN** it prints the signal's capture, its route, the unit's add, each stage's start and end, the approval and the merge, in order

#### Scenario: A signal
- **WHEN** `crew trace signals/<id>` runs
- **THEN** it prints the same chain, starting from the signal

#### Scenario: Nothing recorded
- **WHEN** `crew trace unit/<unit>` names a unit no entry mentions
- **THEN** it says so and exits non-zero

### Requirement: A stage's end is recorded when crew sees it
Each `stage.start` entry SHALL be followed by exactly one `stage.end` entry, carrying the stage crew then reads from the kit, the unit's tasks done and total, and the head of the unit's branch. `crew unit wait <unit>` SHALL wait until the unit's stage agent is no longer working and then record it. When no wait recorded it, the next crew command that reads the team SHALL record it, marked as observed late.

#### Scenario: The conductor waits
- **WHEN** a conductor runs `crew unit wait <unit>` and the construct agent settles
- **THEN** a `stage.end` entry is written with the stage `review` and the unit branch's head

#### Scenario: Nobody waited
- **WHEN** a stage's agent has settled, no wait ran, and `crew status <team>` is run later
- **THEN** a `stage.end` entry is written then, marked observed late, and a second read writes no second entry

### Requirement: The run record is carried to the state repository
Every write crew makes to a flywheel's branch SHALL, in the same commit, bring `runs/<host>/` on the branch up to the entries that host has recorded for the flywheel. `crew events --push` SHALL do the same on request with no other change. Only a host SHALL write its own files there, entries SHALL be added and never removed, and carrying the same entries twice SHALL change nothing.

#### Scenario: A tell, then a plan write
- **WHEN** an agent on the box tells another agent and later writes the plan
- **THEN** the plan write's commit also adds the tell's entry to `runs/chuck-herdr-alpha/` on the branch

#### Scenario: The newest entry
- **WHEN** a plan write has just landed
- **THEN** its own entry, which names that commit, is on the host and reaches the branch with the host's next write or `crew events --push`

#### Scenario: A host is rebuilt
- **WHEN** a host loses its local run record after carrying it
- **THEN** the entries it had carried are still on the branch, and its next carry adds its new entries beside them
