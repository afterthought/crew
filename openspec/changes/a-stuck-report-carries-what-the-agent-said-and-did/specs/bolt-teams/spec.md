## MODIFIED Requirements

### Requirement: The deliverable of each stage
The deliverables SHALL be: construct, the unit's change committed since the stage began, its planning complete; code, a commit since the stage began with every task ticked at the branch's head, or, where the head holds no task list for the unit, as when its change is archived there, a commit since the stage began; verify, a report for the unit saved in the team's reports folder since the stage began; merge, the bolt holding the unit's change archived, or the fix's commits; a fix's code, a commit on its branch since it began. A line a proof of ops's left in a team's stages file from before SHALL be dropped, owed nothing.

#### Scenario: Construct
- **WHEN** a construct agent commits its change with its planning complete and stops working
- **THEN** the wait returns saying the change is committed, naming the branch's head

#### Scenario: Code with tasks still open
- **WHEN** a code agent stops working with one task of four still open at its branch's head, and has said nothing it needs
- **THEN** the stage has not ended

#### Scenario: Code run again on a ticked change
- **WHEN** code is run with a verify report's path, its one round of fixes, on a unit whose tasks were all ticked before it began
- **THEN** the stage ends only once a commit has been made since it began

#### Scenario: Code on a change archived at its head
- **WHEN** a fix round runs on a unit whose change is archived at its branch's head, so no task list stands there, and its agent commits its fix and stops working
- **THEN** the wait returns saying the stage delivered, naming the branch's head and that no task list stands there

#### Scenario: Code with no task list and nothing committed
- **WHEN** a code stage runs on a unit whose branch's head holds no task list, and its agent has committed nothing since the stage began
- **THEN** the stage has not ended, and what it lacks is a commit since it began, never tasks

#### Scenario: A verify run again
- **WHEN** verify runs again with no commit since the last verify, whose report is still in the folder
- **THEN** that older report is not this run's deliverable, and the stage ends at the report this run saves

#### Scenario: Merge
- **WHEN** a merge agent archives the unit's change, its submission lands the unit on its bolt, and the agent stops working
- **THEN** the wait returns naming the bolt's head that holds the unit

#### Scenario: A change merged open
- **WHEN** a merge agent lands the unit on its bolt with its change not archived
- **THEN** the stage has not ended, and the wait says the bolt holds the change open

#### Scenario: A proof from before
- **WHEN** a team's stages file holds a proof line ops's proof left before this change
- **THEN** the team's next read drops it, records no end for it, and owes nothing

### Requirement: A stage quiet too long is reported stuck
A wait SHALL report a stage stuck, naming the stage and its agent, when the agent has not been working for longer than crew's limit (15 minutes unless the wait is given another), with no deliverable, no stop-short, and no background work of its own still running. Before it reports a stage stuck, the wait SHALL read the agent's last words, the last message the agent wrote in its own Claude transcript since the stage began, and the commits on the stage's branch made since the stage began, and the report SHALL carry both: the words quoted with their time, and each commit by its short sha and subject, newest first. Where the agent has written nothing since the stage began, or the branch holds no commit since then, the report SHALL say so; where crew cannot read either, the report SHALL say what it could not read and why, and SHALL NOT stand a guess in its place. A stuck report SHALL end neither the stage nor its agent, and SHALL NOT enter the agent's words in the run record. When crew cannot read whether the agent waits on work of its own, the clock SHALL run and the report SHALL say what could not be read.

#### Scenario: A question left in a pane
- **WHEN** a construct agent asks a question in its pane and stays quiet for longer than the limit, with nothing committed
- **THEN** the wait returns saying the stage is stuck, naming the agent and how long it has been quiet, quoting the question as the agent's last words, and saying the branch holds no commit since the stage began

#### Scenario: Work committed and said, nothing delivered
- **WHEN** a code agent commits two of its four tasks, writes that it stopped because a suite fails twice, and stays quiet past the limit without saying what it needs through crew
- **THEN** the wait's stuck report lists the two commits, newest first, and quotes the agent's message with its time

#### Scenario: A long last message
- **WHEN** the agent's last message is longer than the report carries
- **THEN** the report quotes its opening, cut at a line's end, and says how much more is in the transcript and where

#### Scenario: Words written before the stage began
- **WHEN** the agent's session holds no message written since the stage began
- **THEN** the report says the agent has written nothing since the stage began, and quotes nothing older

#### Scenario: A transcript crew cannot read
- **WHEN** herdr names no session for the agent, or its transcript is missing or not JSON lines
- **THEN** the stuck report still lists the branch's commits, and says crew could not read the agent's last words and why

#### Scenario: Suites still running
- **WHEN** a verify agent has been quiet for longer than the limit while suites it started in the background still run
- **THEN** the stage is not reported stuck

#### Scenario: The agent is gone
- **WHEN** the stage's agent is no longer running and nothing was delivered or said
- **THEN** the wait returns at once saying so, and records nothing

### Requirement: A verify's findings are fixed in one round, with no card
The conductor SHALL take a report's marks as they stand, post no card for it and ask the user nothing about it. When the report marks a finding fix, the conductor SHALL run code once more, a fresh agent told the report's path, which fixes every finding marked fix and only those; a finding marked leave SHALL be left. No verify SHALL run after the fix round, and the unit then merges. A fix round that stops short or fails SHALL be a stuck stage, run again or passed over only on the user's word; one reported stuck SHALL first be read as every stuck report is, and taken to the user only when its words and commits settle nothing.

#### Scenario: A report with findings to fix
- **WHEN** unit `u`'s verify saves a report that marks two findings fix and one leave
- **THEN** the conductor runs `crew unit run u code "Fix every finding the verify report at <path> marks fix."` with no card posted, the coder fixes those two and not the third, and once that stage delivers the conductor runs the merge with no verify again

#### Scenario: A report with nothing to fix
- **WHEN** unit `u`'s report marks no finding fix
- **THEN** the conductor runs its merge next

#### Scenario: A fix round that stops short
- **WHEN** the coder of `u`'s fix round stops short, saying a finding marked fix needs a task reworded
- **THEN** the conductor tells the user it is stuck, and runs it again or merges `u` only on the user's word

## ADDED Requirements

### Requirement: A conductor reads a stuck report before it asks
On a stuck report, the conductor SHALL read the agent's words and the branch's commits the report carries before it asks anyone, and act on what they settle, never reading the agent's pane. Only when they settle nothing SHALL it ask the user, saying what the report carries, and run the stage again or wait again on the user's word.

#### Scenario: The agent's work is done and its next step follows
- **WHEN** a stuck report lists a fix round's commit and quotes the agent saying every finding marked fix is fixed
- **THEN** the conductor runs the unit's merge, and tells the user only what crew refuses of it

#### Scenario: The agent asked in its pane
- **WHEN** a stuck report quotes a construct agent asking which table holds tenants
- **THEN** the conductor gets the answer as for a stop-short, from the design agent first, and runs construct again with it, asking the user only if nobody before them can answer

#### Scenario: The report settles nothing
- **WHEN** a stuck report says the agent has written nothing since the stage began and its branch holds no commit since then
- **THEN** the conductor tells the user which agent and stage is stuck and what the report carries, and runs the stage again or waits again only on the user's word
