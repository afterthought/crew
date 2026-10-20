## MODIFIED Requirements

### Requirement: Units run in slots
A team SHALL have at most `units` units in flight, each held by a slot named `<team>-unit-<n>` with its own pane. A slot SHALL be taken when a unit's first stage starts, and freed when the unit merges into the bolt or is dropped. A slot whose unit or fix has merged into its bolt or landed on main, or whose work the plan no longer has (a dropped unit, or a fix whose bolt was dropped), SHALL be freed the next time crew reads the team (`crew status`, `crew unit run`, `crew fix`), once the slot's agent is not working. A fix SHALL read landed once the kit's main holds its branch's tip and the branch has moved since it was made, or, for one that never moved, once its bolt is in no plan and main holds its tip; a fix SHALL be read from its branch whether or not its place still stands.

#### Scenario: Every slot is taken
- **WHEN** the conductor starts a fifth unit on a team with `units = 4`, all four in flight
- **THEN** crew refuses, naming the units the slots hold

#### Scenario: A unit dropped while its stage works
- **WHEN** the planner drops a unit while its slot's agent is working, and that agent later settles
- **THEN** the next `crew status` of the team frees the slot, and the unit's worktree and branch go as for any work that is over

#### Scenario: A fix whose bolt has landed
- **WHEN** a slot holds a fix that merged into its bolt, the bolt has landed, and the kit's main holds the fix's tip
- **THEN** the next `crew status` of the team reads the fix landed and frees the slot once its agent is not working

#### Scenario: A fix whose place is gone
- **WHEN** a slot holds a fix whose place was removed while its branch stands, and the fix has merged into its bolt or landed with it
- **THEN** the next `crew status` of the team reads it merged or landed from its branch and frees the slot, as it would with its place standing

#### Scenario: A fix just made is not landed
- **WHEN** a fix's branch was cut from its bolt at a commit main already holds, has no commit of its own, and its bolt is still planned
- **THEN** the fix reads in flight, and its slot is kept

### Requirement: A worktree goes when its work is over
crew SHALL remove each worktree it made, with its branch, once its work is over and no slot holds it: a bolt's once no plan has the bolt; a unit's once its bolt holds its change archived or it has landed, or no plan has it, never while the bolt holds its change open; a fix's once it has merged into its bolt or landed on main, its conductor dropped it, or no plan has its bolt. A fix's bolt SHALL be the one its branch tracks, the host's `bolt/<bolt>` or GitHub's `origin/bolt/<bolt>`, and whether it has merged SHALL be read against that same branch; once that branch is gone, whether the fix has landed SHALL be read from the kit's main. A fix's branch that no worktree and no slot holds SHALL go once the fix has merged or landed, or its bolt is in no plan and the kit's main holds its tip; such a branch holding anything its bolt and main lack SHALL be left as it is. A dropped fix's branch SHALL be kept and named when `git cherry` finds commits whose patch its bolt lacks, or cannot compare it with its bolt, and SHALL then be the user's; one holding nothing beyond its bolt SHALL go. A bolt's branch crew made, which crew marks in the kit's git config when it makes it, SHALL go once no plan has the bolt and no worktree is on it; a deletion git or sluice refuses SHALL keep the branch and name why. It SHALL do this each time it reads a team, for the team's kit checkout, and at once after `crew bolt drop`, `crew unit drop` or `crew bolt land`.

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

#### Scenario: A landed fix's place and branch
- **WHEN** a fix's place stands, no slot holds it, and its bolt has landed with the kit's main holding the fix's tip
- **THEN** the next read of a team building in that checkout removes the place and the branch, saying the fix has landed on main

#### Scenario: A landed fix's branch with no place
- **WHEN** a kit checkout holds a `fix/` branch whose place is gone, which no slot holds, whose bolt has landed and been removed, and whose tip the kit's main holds
- **THEN** the next read of a team building in that checkout removes the branch, saying the commit it was at

#### Scenario: A fix branch with work nobody holds
- **WHEN** a `fix/` branch with no place and no slot holds a commit neither its bolt nor the kit's main has, and its bolt is in no plan
- **THEN** crew leaves the branch as it is

#### Scenario: A fix that tracks its bolt on GitHub
- **WHEN** a fix's branch tracks `origin/bolt/<bolt>` and that branch holds the fix's tip
- **THEN** crew reads the fix's bolt as `<bolt>` and the fix as merged, and frees its slot and removes its place and branch as for one tracking the host's `bolt/<bolt>`
