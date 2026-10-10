## MODIFIED Requirements

### Requirement: The conductor waits for a stage through crew
After starting a unit's stage, a fix or ops's proof, the conductor SHALL wait for it through crew (`crew unit wait <unit>`, `crew fix <team> <name> --wait`, `crew prove <team> --wait`), run as a background command, and SHALL NOT wait on an agent with herdr directly or read a pane to learn an outcome. The wait SHALL run on the team's host and return when the stage has ended, is stuck, or its timeout passes, and say which.

#### Scenario: A stage settles
- **WHEN** a conductor has `crew unit wait <unit>` running, and the unit's verify agent has saved its report and settled
- **THEN** the command returns naming the report's path, and the stage's end is in the run record

#### Scenario: A quiet agent with nothing delivered
- **WHEN** a verify agent ends its turn to wait on suites it started in the background, with no report saved yet
- **THEN** the wait does not return, and returns once the report is saved and the agent has stopped working

#### Scenario: The timeout passes
- **WHEN** the stage has neither ended nor become stuck when the timeout passes
- **THEN** the command returns saying the stage is still running, and whether its agent is working or waiting on work of its own, and no `stage.end` entry is written

## ADDED Requirements

### Requirement: A stage ends at its deliverable
Each stage SHALL have one deliverable, read in the kit or on the team's host and never kept by hand. A stage SHALL end when its deliverable exists and its agent has stopped working, or when its agent stops short through crew, and SHALL NOT end because its agent has gone quiet.

#### Scenario: Delivered while still working
- **WHEN** a code agent's last task is committed and the agent is still writing its summary
- **THEN** the stage ends once the agent stops working, so the next stage never starts over a working agent

### Requirement: The deliverable of each stage
The deliverables SHALL be: construct, the unit's change committed since the stage began, its planning complete; code, a commit since the stage began with every task ticked at the branch's head; verify, a report for the unit saved in the team's reports folder since the stage began; merge, the bolt holding the unit's change or the fix's commits; a fix's code, a commit on its branch since it began; ops's proof, a proof file for the bolt saved in the team's reports folder since it began.

#### Scenario: Construct
- **WHEN** a construct agent commits its change with its planning complete and stops working
- **THEN** the wait returns saying the change is ready for review, naming the branch's head

#### Scenario: Code with tasks still open
- **WHEN** a code agent stops working with one task of four still open at its branch's head, and has said nothing it needs
- **THEN** the stage has not ended

#### Scenario: Code run again on a ticked change
- **WHEN** code is run with findings from a verify on a unit whose tasks were all ticked before it began
- **THEN** the stage ends only once a commit has been made since it began

#### Scenario: A verify run again
- **WHEN** verify runs again with no commit since the last verify, whose report is still in the folder
- **THEN** that older report is not this run's deliverable, and the stage ends at the report this run saves

#### Scenario: Merge
- **WHEN** a merge agent's `wt merge` lands the unit on its bolt and the agent stops working
- **THEN** the wait returns naming the bolt's head that holds the unit

### Requirement: A stage's agent says what it needs through crew
A stage's agent that cannot finish without something only someone else can give SHALL say so with `crew needs "<what it needs>"`, which ends its stage short. crew SHALL carry the agent's words to the conductor: in the answer of a wait running on the stage, otherwise in a tell marked as from that agent. crew SHALL refuse `crew needs` from anyone but the agent of a stage crew owes an end, and with no words.

#### Scenario: A coder pauses
- **WHEN** a code agent runs `crew needs "a decision on which table holds tenants"` while the conductor waits on its unit
- **THEN** the wait returns saying the stage stopped short, with those words, and the stage's end is recorded

#### Scenario: Nobody is waiting
- **WHEN** a stage's agent runs `crew needs` and no wait is running on its stage
- **THEN** the conductor is told the agent's words, marked as from that agent

#### Scenario: Not a stage's agent
- **WHEN** a conductor, or a slot's agent whose stage has already ended, runs `crew needs "x"`
- **THEN** crew refuses, saying the caller runs no stage crew is waiting on

### Requirement: A stage quiet too long is reported stuck
A wait SHALL report a stage stuck, naming the stage and its agent, when the agent has not been working for longer than crew's limit (15 minutes unless the wait is given another), with no deliverable, no stop-short, and no background work of its own still running. A stuck report SHALL end neither the stage nor its agent. When crew cannot read whether the agent waits on work of its own, the clock SHALL run and the report SHALL say what could not be read.

#### Scenario: A question left in a pane
- **WHEN** a construct agent asks a question in its pane and stays quiet for longer than the limit, with nothing committed
- **THEN** the wait returns saying the stage is stuck, naming the agent and how long it has been quiet

#### Scenario: Suites still running
- **WHEN** a verify agent has been quiet for longer than the limit while suites it started in the background still run
- **THEN** the stage is not reported stuck

#### Scenario: The agent is gone
- **WHEN** the stage's agent is no longer running and nothing was delivered or said
- **THEN** the wait returns at once saying so, and records nothing

### Requirement: Ops's proof of a bolt is a stage crew starts and waits on
`crew prove <team> ["<words>"]` SHALL ask the team's ops to deploy the bolt and work the *Proof in dev* list of each of its units, in a tell marked as from the caller, and SHALL record the proof's start and owe its end like a stage. Ops SHALL write its results once, whole, to `proof-<bolt>-<YYYYMMDD-HHMM>.md` in the team's reports folder; that file is the proof's deliverable. `crew prove` SHALL be refused when the team holds no bolt or its ops is not up.

#### Scenario: Proof before landing
- **WHEN** every unit of a bolt has merged, the conductor runs `crew prove swb-1` and then `crew prove swb-1 --wait`
- **THEN** ops is asked to prove the bolt, and the wait returns with the proof file's path once ops has written it and stopped working

#### Scenario: Ops needs the user's word
- **WHEN** ops, during a proof, runs `crew needs "the user's word to deploy over swb-2's bolt"`
- **THEN** the proof ends short, and the conductor learns it with ops's words
