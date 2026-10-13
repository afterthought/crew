## ADDED Requirements

### Requirement: A verify's report says what to do with each finding
A unit's verify SHALL run once, when its tasks are all ticked, and a chore's once its code has committed. Its report SHALL end by marking each finding it raised fix, leave or amend: amend for one that would change what the unit is for, its intent or what its specs say must be true. A chore's report SHALL mark each finding fix or leave.

#### Scenario: A report's last section
- **WHEN** unit `u`'s verify raises a critical finding, a warning and a suggestion
- **THEN** its saved report ends with a line for each, marked fix, leave or amend, and the critical one is not marked leave

### Requirement: A verify's findings are fixed in one round, with no card
The conductor SHALL take a report's marks as they stand, post no card for it and ask the user nothing about it. When the report marks a finding fix, the conductor SHALL run code once more, a fresh agent told the report's path, which fixes every finding marked fix and only those; a finding marked leave SHALL be left. No verify SHALL run after the fix round, and the unit then merges. A fix round that stops short or fails SHALL be a stuck stage, run again or passed over only on the user's word.

#### Scenario: A report with findings to fix
- **WHEN** unit `u`'s verify saves a report that marks two findings fix and one leave
- **THEN** the conductor runs `crew unit run u code "Fix every finding the verify report at <path> marks fix."` with no card posted, the coder fixes those two and not the third, and once that stage delivers the conductor runs the merge with no verify again

#### Scenario: A report with nothing to fix
- **WHEN** unit `u`'s report marks no finding fix or amend
- **THEN** the conductor runs its merge next

#### Scenario: A fix round that stops short
- **WHEN** the coder of `u`'s fix round stops short, saying a finding marked fix needs a task reworded
- **THEN** the conductor tells the user it is stuck, and runs it again or merges `u` only on the user's word

### Requirement: A finding that would change what a unit is for goes to the user
A finding a report marks amend SHALL go to the planner, in the report's words, as the unit's amendment, and the unit SHALL wait to merge until the user answers it: approved, construct runs again; dropped, the unit merges with the finding left.

#### Scenario: An amendment raised by a verify
- **WHEN** unit `u`'s report marks a finding amend
- **THEN** the conductor tells the planner in the report's words and holds `u`'s merge; when the user approves the amendment, construct runs again, and when they drop it, `u` merges with the finding left

### Requirement: A unit fixed after its verify waits to merge
A unit that has delivered its verify, and its fix round when one ran, SHALL wait to merge: a forecast or an amended `After` unit reaches it as a settle stage, and a chore's merge needs its verify once. Construct run again SHALL end the wait, since its change is new.

#### Scenario: A forecast after the fix round
- **WHEN** a forecast against the bolt reaches unit `u`, which delivered its verify and then its fix round, and no stage of it runs
- **THEN** it reaches `u` as a settle stage

### Requirement: A unit's merge archives its change first
A unit's merge stage SHALL archive its change, `openspec archive <unit> --yes` in its place, committed on its branch, before it merges, and crew SHALL read the merge as delivered only once the bolt holds the change archived. A place whose change its merge archived SHALL be read from the archive, its tasks, Touches and planning, so the unit reads as waiting to merge. A chore and a fix have no change to archive.

#### Scenario: Archived and merged
- **WHEN** the merge agent of unit `u` archives `u`'s change, commits it, and merges `unit/u` into `bolt/y`
- **THEN** `bolt/y` holds `openspec/changes/archive/<date>-u`, `u` reads merged, and the merge stage has delivered

#### Scenario: Archived, not yet merged
- **WHEN** `u`'s place holds its change archived and `bolt/y` does not hold `u` yet
- **THEN** `crew bolts` shows `u` in verify, its tasks read from the archive

#### Scenario: An archive openspec refuses
- **WHEN** `openspec archive u --yes` refuses a delta that modifies a requirement a sibling unit adds and has not merged
- **THEN** the merge agent stops, saying so with openspec's words, and nothing is merged

## MODIFIED Requirements

### Requirement: The deliverable of each stage
The deliverables SHALL be: construct, the unit's change committed since the stage began, its planning complete; code, a commit since the stage began with every task ticked at the branch's head; verify, a report for the unit saved in the team's reports folder since the stage began; merge, the bolt holding the unit's change archived, or the fix's commits; a fix's code, a commit on its branch since it began; ops's proof, a proof file for the bolt saved in the team's reports folder since it began.

#### Scenario: Construct
- **WHEN** a construct agent commits its change with its planning complete and stops working
- **THEN** the wait returns saying the change is ready for review, naming the branch's head

#### Scenario: Code with tasks still open
- **WHEN** a code agent stops working with one task of four still open at its branch's head, and has said nothing it needs
- **THEN** the stage has not ended

#### Scenario: Code run again on a ticked change
- **WHEN** code is run with a verify report's path, its one round of fixes, on a unit whose tasks were all ticked before it began
- **THEN** the stage ends only once a commit has been made since it began

#### Scenario: A verify run again
- **WHEN** verify runs again with no commit since the last verify, whose report is still in the folder
- **THEN** that older report is not this run's deliverable, and the stage ends at the report this run saves

#### Scenario: Merge
- **WHEN** a merge agent archives the unit's change, its merge lands the unit on its bolt, and the agent stops working
- **THEN** the wait returns naming the bolt's head that holds the unit

#### Scenario: A change merged open
- **WHEN** a merge agent lands the unit on its bolt with its change not archived
- **THEN** the stage has not ended, and the wait says the bolt holds the change open
