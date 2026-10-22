## ADDED Requirements

### Requirement: A landing leaves only what main lacks
Once sluice has landed a bolt's submission to main, crew SHALL mark the bolt's branch as landed on the team's host, and every read of the team SHALL then judge the bolt's work against the kit's main as crew reads it now, never against the bolt: each unit's, chore's and fix's branch, as its place goes, and the bolt's own branch, once no plan has the bolt and no worktree is on it. Whether main holds a commit SHALL be judged by its patch, as `git cherry` compares, never by which commits are ancestors. A branch holding no commit whose patch main lacks SHALL go; one holding such a commit, or one git cannot compare with main, SHALL be kept, named with the commit it is at and how many commits it holds whose patch main lacks, recorded once in the run record, and SHALL then be the user's to keep or delete. `crew bolt land` SHALL print what the tidy it asks of the team's host removed and kept, and once that tidy has run the kit SHALL hold nothing of the bolt's work but branches holding work main lacks and worktrees kept for uncommitted changes or a remove hook.

#### Scenario: Everything the bolt left is on main
- **WHEN** a bolt's submission to main has landed, and `crew bolt land` runs while a merged unit's place and a merged fix's place still stand
- **THEN** both places and their branches are removed, the bolt's branch is removed, and the command says the bolt's branch went because main holds every commit of it

#### Scenario: The bolt's branch holds a commit main lacks
- **WHEN** a bolt's submission to main has landed, and its branch then holds a commit main does not, and `crew bolt land` runs
- **THEN** the bolt's branch is kept, the command naming it, the commit it is at and that it holds 1 commit whose patch main lacks, a run-record entry names the branch, and no later read of the team removes it

#### Scenario: A fix of the landed bolt holds work of its own
- **WHEN** a bolt has landed, and a fix made from it, not merged, holds a commit main does not, and its place goes
- **THEN** its place is removed and its branch is kept and named, compared with main

#### Scenario: The team's host did not answer the landing
- **WHEN** `crew bolt land` runs while the team's host cannot be reached, and the team's next read finds the bolt's branch marked landed and holding a commit main lacks
- **THEN** that read keeps the bolt's branch and names it, as the landing's own tidy would have

#### Scenario: Commits main holds under the same hashes
- **WHEN** sluice landed the bolt as a merge commit whose second parent is the bolt's head, and the tidy compares the bolt's branch and its units' branches with main
- **THEN** `git cherry` finds nothing of their own on them, and they go

## MODIFIED Requirements

### Requirement: A worktree goes when its work is over
crew SHALL remove each worktree it made, with its branch, once its work is over and no slot holds it: a bolt's once no plan has the bolt; a unit's once its bolt holds its change archived or it has landed, or no plan has it, never while the bolt holds its change open; a chore's once its bolt or main holds its trailer, or no plan has it; a fix's once it has merged into its bolt, its conductor dropped it, or no plan has its bolt. A unit's or chore's branch SHALL go with its place only when `git cherry` finds no commit on it whose patch its bolt lacks, or, once the bolt has landed or the bolt's branch is gone, whose patch the kit's main as crew reads it now lacks; it SHALL never be judged by which commits are ancestors, since a unit's commits are rebased as they merge. A branch with such commits, or one git cannot compare, SHALL be kept, and the command SHALL name it with the commit it is at, how many commits it holds whose patch its bolt or main lacks, and that it is the user's to keep or delete. A dropped fix's branch SHALL be kept and named when `git cherry` finds commits whose patch its bolt lacks, or cannot compare it with its bolt, and SHALL then be the user's; one holding nothing beyond its bolt SHALL go. A fix's branch whose bolt has landed, or whose bolt's branch is gone, SHALL be judged against the kit's main as a unit's is. Each branch kept SHALL be recorded once, in a run-record entry on the team's host naming the branch, the commit it is at and how many commits it holds of its own. A bolt's branch crew made, which crew marks in the kit's git config when it makes it, SHALL go once no plan has the bolt and no worktree is on it, and a landed bolt's only when `git cherry` finds no commit on it whose patch the kit's main lacks, being otherwise kept, named, recorded and the user's; a deletion git or sluice refuses SHALL keep the branch and name why. It SHALL do this each time it reads a team, for the team's kit checkout, and at once after `crew bolt drop`, `crew unit drop`, `crew chore drop`, `crew unit free`, `crew chore free` or `crew bolt land`.

#### Scenario: A dropped bolt
- **WHEN** the planner drops a bolt that swb-2 holds, none of whose units' or fixes' branches holds a commit of its own
- **THEN** `bolt/<bolt>` is gone from swb-2's host, and so are the places, branches and slots of the bolt's units and fixes

#### Scenario: A dropped bolt whose unit holds a written change
- **WHEN** the planner drops a bolt that swb-2 holds, and one of its units' branches holds the unit's change committed, which the bolt does not
- **THEN** that unit's place and slot are gone and its branch is kept, the drop's output naming it, the commit it is at and that it holds 1 commit whose patch the bolt lacks, and a run-record entry names the branch; the bolt's other places and branches go

#### Scenario: A dropped unit holding nothing of its own
- **WHEN** the planner drops a unit whose branch holds no commit beyond its bolt
- **THEN** its place and its branch are removed, and crew says the commit the branch was at

#### Scenario: Work dropped with commits of its own
- **WHEN** the planner drops a unit whose branch holds its change committed, which neither its bolt nor main has
- **THEN** its place is removed and its slot freed, its branch is kept, and the drop's output names the branch, the commit it is at and how many commits it holds whose patch the bolt lacks

#### Scenario: A unit whose commits reached the bolt rebased
- **WHEN** a unit's branch holds commits whose patches the bolt holds under other hashes, rebased as they merged, and its place goes
- **THEN** its branch is removed, since `git cherry` finds nothing of its own on it

#### Scenario: A unit whose bolt's branch is gone
- **WHEN** a unit's place goes after its bolt's branch was removed, and its branch holds a commit whose patch the kit's main lacks
- **THEN** its branch is kept and named, compared with the kit's main

#### Scenario: A unit of a landed bolt
- **WHEN** a unit's place goes after its bolt has landed, while the bolt's branch still stands, and its branch holds a commit whose patch the bolt holds and main lacks
- **THEN** its branch is kept and named, compared with the kit's main and not with the bolt

#### Scenario: A slot freed by hand
- **WHEN** `crew unit free u` frees a slot holding a unit no longer in its team's bolt, whose branch holds a commit of its own
- **THEN** the slot is freed and the place removed, and `unit/u` is kept and named

#### Scenario: A leftover from before
- **WHEN** a kit checkout has the worktree of a bolt that no plan has, and a place of a unit that has merged, which no slot holds
- **THEN** the next `crew status` of a team building in that checkout removes both, with their branches

#### Scenario: A bolt branch crew did not make
- **WHEN** a kit checkout has a `bolt/` branch with no mark of crew's, of a bolt no plan has
- **THEN** crew leaves it as it is

#### Scenario: The host does not answer
- **WHEN** a bolt is dropped while its team's host cannot be reached
- **THEN** the plan changes, crew says the host's worktrees were not removed, and the team's next read removes them, keeping each branch that holds work of its own

#### Scenario: A unit carried onto its bolt
- **WHEN** a unit's change is open on its bolt, carried there inside another unit's merge, and the team is read
- **THEN** its worktree, its branch and its slot are kept

#### Scenario: A dropped fix's place with uncommitted changes
- **WHEN** a fix is dropped while its place holds a file nobody committed
- **THEN** its place and branch are kept, and every read names them until the place is clean, when crew removes them
