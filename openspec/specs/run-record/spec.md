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
An entry's `On` fields SHALL name each object the act touched, and its `From` fields each object the act came from, as typed names: `unit/<unit>`, `chore/<chore>`, `bolt/<bolt>`, `queue/<kit>`, `signals/<id>`, `team/<team>`, `agent/<name>`, `stage/<unit or chore>/<stage>`, `fix/<bolt>/<name>`.

#### Scenario: A unit queued from a signal
- **WHEN** a unit is added with `--signal <id>`
- **THEN** the `unit.add` entry has `On: unit/<unit>` and `From: signals/<id>`, and the route move's entry has `On: signals/<id>` and `On: unit/<unit>`

#### Scenario: A stage
- **WHEN** a unit's code stage starts in slot 2 of swb-1
- **THEN** the entry has `On: stage/<unit>/code`, `On: unit/<unit>` and `On: agent/swb-1-unit-2`

#### Scenario: A chore's stage
- **WHEN** a chore's verify starts in slot 1 of swb-1
- **THEN** the entry has `On: stage/<chore>/verify`, `On: chore/<chore>` and `On: agent/swb-1-unit-1`

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

### Requirement: Entries can be followed as they are written
`crew events --follow` SHALL print each entry of the partition as it reaches the partition's branch, one line per entry, until it is interrupted. It SHALL read the branch as this host's cache holds it, read it again only when the cache's tip moves, and read again only the run-record files whose content changed. The branch SHALL be fetched once a minute, never faster: by the host's follower for a partition it follows, else by the follow itself. It SHALL ask no host for entries.

#### Scenario: Following a bolt team
- **WHEN** `crew events --follow --label wldn` is running and a conductor starts a stage on the box
- **THEN** that entry's line appears once its commit is on `wldn/main` and this host has fetched it, within a minute, without the command being run again

#### Scenario: A host is asleep
- **WHEN** `crew events --follow --label wldn` starts while macbook-pro does not answer
- **THEN** it follows the branch as before, and starts nothing on macbook-pro

#### Scenario: Nothing moves
- **WHEN** `crew events --follow --label wldn` runs on a host where no follower follows wldn, and nothing reaches wldn's branch
- **THEN** it fetches the branch once a minute and starts no other process

#### Scenario: The host's follower fetches
- **WHEN** `crew events --follow --label wldn` runs on mac-studio while mac-studio's follower follows wldn
- **THEN** the follow fetches nothing itself, and prints each entry once the follower's fetch, or a write on mac-studio, has moved the cache

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
Each `stage.start` entry SHALL be followed by exactly one `stage.end` entry, carrying the stage crew then reads from the kit, the unit's tasks done and total, the head of the unit's or fix's branch, how the stage ended in `Ended`, and, when it delivered, its deliverable as an object in `Delivered`. `Ended` SHALL be `delivered` when the deliverable exists and the agent has stopped working, `short` when the agent said what it needs through crew, and `stopped` when crew ended the stage's agent before either. A wait SHALL record a delivered end when it sees it; a stop-short SHALL be recorded by the command the agent ran; when no wait recorded a delivered end, the next crew command that reads the team SHALL record it, marked as observed late. A stage whose agent has only gone quiet SHALL have no end recorded. Ops's proof SHALL be recorded the same way, on `stage/<bolt>/proof`.

#### Scenario: The conductor waits
- **WHEN** a conductor runs `crew unit wait <unit>` and the construct agent commits its change and stops working
- **THEN** a `stage.end` entry is written with the stage `review`, `Ended: delivered`, the unit branch's head, and `Delivered: unit/<unit>@<head>`

#### Scenario: A verify's report
- **WHEN** a verify stage ends at its report
- **THEN** its `stage.end` entry has `Delivered: report/<the report's file name>`

#### Scenario: Nobody waited
- **WHEN** a stage's agent has delivered and stopped working, no wait ran, and `crew status <team>` is run later
- **THEN** a `stage.end` entry is written then, marked observed late, and a second read writes no second entry

#### Scenario: Quiet with nothing delivered
- **WHEN** a code agent has stopped working with tasks still open, and `crew status <team>` is run
- **THEN** no `stage.end` entry is written

#### Scenario: A stop-short
- **WHEN** a stage's agent runs `crew needs "<what it needs>"`
- **THEN** a `stage.end` entry is written with `Ended: short` and no `Delivered`, and the agent's words appear nowhere in the run record

#### Scenario: A stage run again before it ended
- **WHEN** the conductor runs a unit's code stage again while the previous code stage has neither delivered nor stopped short
- **THEN** the previous stage's `stage.end` is written with `Ended: stopped` before the new stage's start

### Requirement: A send is one entry in the receiving partition's record
Each `crew send` that reaches its operator SHALL append one entry, act `send`, to the run record of the partition it was sent to, on the host the command ran on. Its `By` SHALL be the sender, its `On` the operator, `agent/<label>-operator`, and the team, `team/<team>`, when a team was named; its `Why` SHALL be `send <team or partition>`; and its `Chars` the length of the text. It SHALL hold no part of the text, and no separate tell entry SHALL be written for it. A send that types nothing SHALL write no entry, as a tell that types nothing writes none.

#### Scenario: A send to a team
- **WHEN** `crw-5-unit-1` sends 46 characters to `swb-1`, a team of wldn
- **THEN** wldn's run record gains one entry: act `send`, `By: crw-5-unit-1`, `On: agent/wldn-operator`, `On: team/swb-1`, `Why: send swb-1`, `Chars: 46`, and the text appears nowhere in it

#### Scenario: A send that is refused
- **WHEN** a send fails because `wldn-operator` is not up
- **THEN** no entry is written

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

### Requirement: A bolt's landing entry records its time by holder
Every `bolt.land` entry crew writes for a bolt a team held SHALL record two things: the bolt's age, in whole minutes, from its newest give to its landing, as `Age`; and the minutes of that age each holder held, as `Split`, in the order team, kit, user, hold, nobody, each named with its minutes, `team 130, kit 12, user 40, hold 0, nobody 3`. The split SHALL be made by the same rule the board's head line uses. The landing SHALL be the moment sluice's record says the bolt's landing submission was decided, or the entry's own time when no submission of the bolt landed. When the give or sluice's record of the bolt's submissions can't be read, the entry SHALL carry neither field, and the landing SHALL go on as it does today.

#### Scenario: A bolt lands
- **WHEN** main-level ops closes the landing of `b`, given 6h 10m before sluice landed it, with team 3h 20m, kit 25m, user 2h 05m, hold 0 and nobody 20m
- **THEN** its `bolt.land` entry holds `Age: 370` and `Split: team 200, kit 25, user 125, hold 0, nobody 20`

#### Scenario: sluice's record can't be read at the landing
- **WHEN** `sluice status` fails on the team's host as `b`'s landing is recorded
- **THEN** the `bolt.land` entry is written without `Age` and `Split`, and the landing is closed as it is today
