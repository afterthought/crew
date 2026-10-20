## MODIFIED Requirements

### Requirement: Work happens in fixed places
A bolt SHALL be the branch `bolt/<bolt>`, branched from main, with no worktree, and SHALL move only through sluice. A unit SHALL be built on `unit/<unit>`, branched from its bolt and holding its `After` units' work as it stood when its place was made, in `<kit>/places/<unit>`. When a branch of the unit's name was kept by an earlier drop, the unit's place SHALL be made on that branch as it stands, the branch SHALL then track the unit's bolt, and the stage that made the place SHALL say it starts from the kept branch, naming the commit it is at; a chore's place SHALL be made on a kept `chore/<chore>` alike. A unit SHALL merge into its bolt only by a submission through sluice. Its place SHALL be removed once it has merged, as every worktree crew made is once its work is over. Each worktree crew makes SHALL be made ready through its kit's declaration before any agent starts in it, and by no script a kit names for crew. A team's conductor and ops SHALL start in the kit's main checkout, or in the worktree a bolt given before bolts were branches still has.

#### Scenario: A bolt is given
- **WHEN** `crew bolt give swb-1` gives swb-1 the bolt `b`
- **THEN** `bolt/b` is made from the kit's main on swb-1's host, no worktree is made for it, and swb-1's conductor and ops start in the kit's main checkout

#### Scenario: A unit merges
- **WHEN** the merge stage of a verified unit submits it and sluice lands it
- **THEN** `bolt/<bolt>` holds the unit's change in a merge commit sluice made, `places/<unit>` is gone, and the unit's slot is free

#### Scenario: A kit with a crew-prepare script
- **WHEN** crew makes a unit's place in a kit whose main checkout's devenv profile holds a `crew-prepare` script
- **THEN** the script does not run

#### Scenario: A unit added again under a kept branch's name
- **WHEN** `unit/u` was kept when unit `u` was dropped from bolt `a`, and a unit `u` added later to bolt `b` starts construct
- **THEN** `places/u` is made on `unit/u` as it stood, holding the kept commits, `unit/u` tracks `bolt/b`, and the construct's start says the place starts from the kept `unit/u` at its commit

### Requirement: A worktree goes when its work is over
crew SHALL remove each worktree it made, with its branch, once its work is over and no slot holds it: a bolt's once no plan has the bolt; a unit's once its bolt holds its change archived or it has landed, or no plan has it, never while the bolt holds its change open; a chore's once its bolt or main holds its trailer, or no plan has it; a fix's once it has merged into its bolt, its conductor dropped it, or no plan has its bolt. A unit's or chore's branch SHALL go with its place only when `git cherry` finds no commit on it whose patch its bolt lacks, or, once the bolt's branch is gone, whose patch the kit's main as crew reads it now lacks; it SHALL never be judged by which commits are ancestors, since a unit's commits are rebased as they merge. A branch with such commits, or one git cannot compare, SHALL be kept, and the command SHALL name it with the commit it is at, how many commits it holds whose patch its bolt or main lacks, and that it is the user's to keep or delete. A dropped fix's branch SHALL be kept and named when `git cherry` finds commits whose patch its bolt lacks, or cannot compare it with its bolt, and SHALL then be the user's; one holding nothing beyond its bolt SHALL go. Each branch kept SHALL be recorded once, in a run-record entry on the team's host naming the branch, the commit it is at and how many commits it holds of its own. A bolt's branch crew made, which crew marks in the kit's git config when it makes it, SHALL go once no plan has the bolt and no worktree is on it; a deletion git or sluice refuses SHALL keep the branch and name why. It SHALL do this each time it reads a team, for the team's kit checkout, and at once after `crew bolt drop`, `crew unit drop`, `crew chore drop`, `crew unit free`, `crew chore free` or `crew bolt land`.

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
