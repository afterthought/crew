## MODIFIED Requirements

### Requirement: Units run in slots
A team SHALL have at most `units` units in flight, each held by a slot named `<team>-unit-<n>` with its own pane. A slot SHALL be taken when a unit's first stage starts, and freed when the unit merges into the bolt or is dropped. A slot whose unit or fix has merged into its bolt, or whose work the plan no longer has (a dropped unit, or a fix whose bolt was dropped), SHALL be freed the next time crew reads the team (`crew status`, `crew unit run`, `crew fix`), once the slot's agent is not working.

#### Scenario: Every slot is taken
- **WHEN** the conductor starts a fifth unit on a team with `units = 4`, all four in flight
- **THEN** crew refuses, naming the units the slots hold

#### Scenario: A unit dropped while its stage works
- **WHEN** the planner drops a unit while its slot's agent is working, and that agent later settles
- **THEN** the next `crew status` of the team frees the slot, and the unit's worktree and branch go as for any work that is over

### Requirement: Work happens in fixed places
A bolt SHALL be built on `bolt/<bolt>`, branched from main, in the worktree `<kit>/bolts/<bolt>`. A unit SHALL be built on `unit/<unit>`, branched from its bolt, in `<kit>/places/<unit>`. A unit SHALL merge into its bolt with the kit's merge hooks. Its place SHALL be removed once it has merged, as every worktree crew made is once its work is over.

#### Scenario: A unit merges
- **WHEN** the merge stage of a verified unit finishes
- **THEN** `bolt/<bolt>` holds the unit's change, `places/<unit>` is gone, and the unit's slot is free

### Requirement: A bolt lands on main on the user's word
A proven bolt SHALL be landed by the partition's main-level ops, which merges `bolt/<bolt>` into main through the kit's merge hooks, deploys main, and then runs `crew bolt land`. The bolt's worktree SHALL then be removed, unless it has uncommitted changes, and the team SHALL hold no bolt. A worktree that is kept SHALL NOT stop the landing.

#### Scenario: The bolt lands
- **WHEN** the user says swb-1's bolt may land
- **THEN** main holds every unit's change, the bolt's records are gone from the plan, and swb-1 can be given its next bolt

#### Scenario: The bolt's worktree has uncommitted changes
- **WHEN** `crew bolt land` runs on a bolt whose worktree has a modified file
- **THEN** the bolt lands and the team holds no bolt, and crew says the worktree is kept with its branch because it has uncommitted changes

## ADDED Requirements

### Requirement: A worktree goes when its work is over
crew SHALL remove each worktree it made, with its branch, once its work is over and no slot holds it: a bolt's once no plan has the bolt; a unit's once it has merged into its bolt or landed, or no plan has it; a fix's once it has merged into its bolt, or no plan has its bolt. It SHALL do this each time it reads a team, for the team's kit checkout, and at once after `crew bolt drop`, `crew unit drop` or `crew bolt land`.

#### Scenario: A dropped bolt
- **WHEN** the planner drops a bolt that swb-2 holds
- **THEN** `bolts/<bolt>` and `bolt/<bolt>` are gone from swb-2's host, and so are the places, branches and slots of the bolt's units and fixes

#### Scenario: A leftover from before
- **WHEN** a kit checkout has the worktree of a bolt that no plan has, and a place of a unit that has merged, which no slot holds
- **THEN** the next `crew status` of a team building in that checkout removes both, with their branches

#### Scenario: The host does not answer
- **WHEN** a bolt is dropped while its team's host cannot be reached
- **THEN** the plan changes, crew says the host's worktrees were not removed, and the team's next read removes them

#### Scenario: Work dropped with commits of its own
- **WHEN** a removed branch holds commits that neither main nor its bolt has
- **THEN** crew says the commit the branch was at

### Requirement: Uncommitted changes keep a worktree
A worktree whose work is over SHALL be kept, with its branch, while it has uncommitted changes: modified tracked files, or untracked files git does not ignore. Each read of the team SHALL name it, what its work was and that its changes are the user's to keep or discard, until it is clean, when crew removes it, or gone. Files git ignores SHALL NOT keep a worktree, and go with it.

#### Scenario: A merged unit with a stray file
- **WHEN** a unit has merged into its bolt and its place has an untracked file git does not ignore
- **THEN** the unit's slot is freed, its place and branch are kept, and every `crew status` of the team names the place as kept for its uncommitted changes

#### Scenario: The user clears the changes
- **WHEN** the stray file is removed from a kept place
- **THEN** the next `crew status` of the team removes the place and its branch

#### Scenario: Installed dependencies
- **WHEN** a merged unit's place holds only files git ignores, such as installed dependencies
- **THEN** the place is removed with them

### Requirement: crew removes only its own worktrees
crew SHALL remove only worktrees directly under `<kit>/bolts/` or `<kit>/places/` that are on a `bolt/`, `unit/` or `fix/` branch. It SHALL never remove the main checkout, a worktree elsewhere, one on another branch or on none, or a locked one, which it names as kept. It SHALL remove nothing when it cannot read every plan the kit's work goes in.

#### Scenario: A worktree made by hand
- **WHEN** a kit checkout has a worktree beside `main` that the user made, on a branch of their own
- **THEN** crew leaves it as it is

#### Scenario: A merge partway through its rebase
- **WHEN** a place is on no branch because its merge stopped partway through a rebase
- **THEN** crew leaves it as it is

#### Scenario: A plan that can't be read
- **WHEN** crew reads a team while the plan of a partition whose teams build the kit cannot be fetched
- **THEN** no worktree is removed, and crew says why
