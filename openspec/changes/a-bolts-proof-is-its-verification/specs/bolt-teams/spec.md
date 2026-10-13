## ADDED Requirements

### Requirement: A bolt's proof is its verification
A bolt SHALL be proven by its verification alone: sluice's verdict on its last landing, green at its head. Nobody SHALL deploy the bolt or work a list from its changes to prove it; ops SHALL prove and deploy nothing. The conductor SHALL offer the bolt for landing once every unit and chore has merged and its verification is green.

#### Scenario: Ready to land
- **WHEN** every unit of a bolt has merged and `crew bolts` shows its verification green
- **THEN** the conductor tells the user the bolt is ready to land and posts its landing card, and no one is asked to prove it

#### Scenario: Not yet green
- **WHEN** every unit of a bolt has merged and its head is no landing of sluice's
- **THEN** the bolt is not offered for landing, and `crew bolts` says what its verification is

## MODIFIED Requirements

### Requirement: The conductor waits for a stage through crew
After starting a unit's stage or a fix, the conductor SHALL wait for it through crew (`crew unit wait <unit>`, `crew chore wait <chore>`, `crew fix <team> <name> --wait`), run as a background command, and SHALL NOT wait on an agent with herdr directly or read a pane to learn an outcome. The wait SHALL run on the team's host and return when the stage has ended, is stuck, or its timeout passes, and say which.

#### Scenario: A stage settles
- **WHEN** a conductor has `crew unit wait <unit>` running, and the unit's verify agent has saved its report and settled
- **THEN** the command returns naming the report's path, and the stage's end is in the run record

#### Scenario: A quiet agent with nothing delivered
- **WHEN** a verify agent ends its turn to wait on suites it started in the background, with no report saved yet
- **THEN** the wait does not return, and returns once the report is saved and the agent has stopped working

#### Scenario: The timeout passes
- **WHEN** the stage has neither ended nor become stuck when the timeout passes
- **THEN** the command returns saying the stage is still running, and whether its agent is working or waiting on work of its own, and no `stage.end` entry is written

### Requirement: The deliverable of each stage
The deliverables SHALL be: construct, the unit's change committed since the stage began, its planning complete; code, a commit since the stage began with every task ticked at the branch's head; verify, a report for the unit saved in the team's reports folder since the stage began; settle, a commit on the unit's branch since it began; merge, the bolt holding the unit's change, the chore's trailer or the fix's commits; a fix's code, and a chore's, a commit on its branch since it began. A line a proof of ops's left in a team's stages file from before SHALL be dropped, owed nothing.

#### Scenario: Construct
- **WHEN** a construct agent commits its change with its planning complete and stops working
- **THEN** the wait returns saying the change is committed, naming the branch's head

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
- **WHEN** a merge agent's `wt submit` lands the unit on its bolt and the agent stops working
- **THEN** the wait returns naming the bolt's head that holds the unit

#### Scenario: A proof from before
- **WHEN** a team's stages file holds a proof line ops's proof left before this change
- **THEN** the team's next read drops it, records no end for it, and owes nothing

## REMOVED Requirements

### Requirement: A bolt is deployed and tested from its branch
**Reason**: Record 0025: a bolt's proof is its verification; ops deploys nothing and works no proof list.
**Migration**: "A bolt's proof is its verification".

### Requirement: Ops's proof of a bolt is a stage crew starts and waits on
**Reason**: Record 0025: `crew prove` and ops's proof report go.
**Migration**: The conductor reads the bolt's verification in `crew bolts`.
