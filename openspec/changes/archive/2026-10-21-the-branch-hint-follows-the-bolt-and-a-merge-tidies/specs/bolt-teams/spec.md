# Spec Delta

## MODIFIED Requirements

### Requirement: A worktree goes when its work is over
crew SHALL remove each worktree it made, with its branch, once its work is over and no slot holds it: a bolt's once no plan has the bolt; a unit's once its bolt holds its change archived or it has landed, or no plan has it, never while the bolt holds its change open; a fix's once it has merged into its bolt, its conductor dropped it, or no plan has its bolt. A dropped fix's branch SHALL be kept and named when `git cherry` finds commits whose patch its bolt lacks, or cannot compare it with its bolt, and SHALL then be the user's; one holding nothing beyond its bolt SHALL go. A bolt's branch crew made, which crew marks in the kit's git config when it makes it, SHALL go once no plan has the bolt and no worktree is on it; a deletion git or sluice refuses SHALL keep the branch and name why. It SHALL do this each time it reads a team, for the team's kit checkout, at once after `crew bolt drop`, `crew unit drop` or `crew bolt land`, and at once when a wait sees a unit's, chore's or fix's merge into its bolt delivered.

#### Scenario: A dropped bolt
- **WHEN** the planner drops a bolt that swb-2 holds
- **THEN** `bolt/<bolt>` is gone from swb-2's host, and so are the places, branches and slots of the bolt's units and fixes

#### Scenario: A leftover from before
- **WHEN** a kit checkout has the worktree of a bolt that no plan has, and a place of a unit that has merged, which no slot holds
- **THEN** the next `crew status` of a team building in that checkout removes both, with their branches

#### Scenario: A bolt branch crew did not make
- **WHEN** a kit checkout has a `bolt/` branch with no mark of crew's, of a bolt no plan has
- **THEN** crew leaves it as it is

#### Scenario: The host does not answer
- **WHEN** a bolt is dropped while its team's host cannot be reached
- **THEN** the plan changes, crew says the host's worktrees were not removed, and the team's next read removes them

#### Scenario: Work dropped with commits of its own
- **WHEN** a removed branch holds commits that neither main nor its bolt has
- **THEN** crew says the commit the branch was at

#### Scenario: A unit carried onto its bolt
- **WHEN** a unit's change is open on its bolt, carried there inside another unit's merge, and the team is read
- **THEN** its worktree, its branch and its slot are kept

#### Scenario: A dropped fix's place with uncommitted changes
- **WHEN** a fix is dropped while its place holds a file nobody committed
- **THEN** its place and branch are kept, and every read names them until the place is clean, when crew removes them

#### Scenario: A merge lands
- **WHEN** the conductor's `crew unit wait a` sees unit `a`'s merge into its bolt delivered, its agent idle
- **THEN** the wait's answer says its slot is free and its place and branch removed, before the conductor reads the team again

### Requirement: A conductor carries its bolt for sluice
A team's conductor and ops that crew starts while the team holds a bolt SHALL have `SLUICE_BRANCH` in its environment set to the bolt's branch, and its herdr pane SHALL carry the token `sluice_branch` with the same value, reported from the source `crew` with no time to live. The token SHALL be reported again when herdr resumes the agent, and cleared when the team's bolt lands or is dropped; a conductor or ops whose session then carries the old branch SHALL be restarted at its next stop, as an agent an update made due is, told why. A unit slot SHALL carry neither.

#### Scenario: A conductor starts on a bolt
- **WHEN** crew starts `swb-1-conductor` in `/workspace/switchboard-kit/main` while team swb-1 holds bolt `b7`
- **THEN** its environment holds `SLUICE_BRANCH=bolt/b7`, and `herdr pane list` shows `"sluice_branch": "bolt/b7"` in its pane's `tokens`

#### Scenario: herdr restarts
- **WHEN** herdr's server restarts and resumes `swb-1-conductor` without crew's environment
- **THEN** its pane's `tokens` hold `"sluice_branch": "bolt/b7"` again

#### Scenario: The bolt lands
- **WHEN** `crew bolt land b7` closes swb-1's bolt
- **THEN** the conductor's and ops's panes carry no `sluice_branch` token, and once each is idle it is restarted without `SLUICE_BRANCH`, the conductor fresh and ops with its conversation, told that its team no longer holds `bolt/b7`

#### Scenario: A unit
- **WHEN** crew starts `swb-1-unit-2` in its own worktree
- **THEN** its environment has no `SLUICE_BRANCH` and its pane no `sluice_branch` token
