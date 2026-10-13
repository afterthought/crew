## MODIFIED Requirements

### Requirement: Work happens in fixed places
A bolt SHALL be the branch `bolt/<bolt>`, branched from main, with no worktree, and SHALL move only through sluice. A unit SHALL be built on `unit/<unit>`, branched from its bolt and holding its `After` units' work as it stood when its place was made, in `<kit>/places/<unit>`. A unit SHALL merge into its bolt only by a submission through sluice. Its place SHALL be removed once it has merged, as every worktree crew made is once its work is over. Each worktree crew makes SHALL be made ready through its kit's declaration before any agent starts in it, and by no script a kit names for crew. A team's conductor and ops SHALL start in the kit's main checkout, or in the worktree a bolt given before bolts were branches still has.

#### Scenario: A bolt is given
- **WHEN** `crew bolt give swb-1` gives swb-1 the bolt `b`
- **THEN** `bolt/b` is made from the kit's main on swb-1's host, no worktree is made for it, and swb-1's conductor and ops start in the kit's main checkout

#### Scenario: A unit merges
- **WHEN** the merge stage of a verified unit submits it and sluice lands it
- **THEN** `bolt/<bolt>` holds the unit's change in a merge commit sluice made, `places/<unit>` is gone, and the unit's slot is free

#### Scenario: A kit with a crew-prepare script
- **WHEN** crew makes a unit's place in a kit whose main checkout's devenv profile holds a `crew-prepare` script
- **THEN** the script does not run

### Requirement: A unit is built stage by stage, each by a fresh agent
`crew unit run <unit> <stage>` SHALL start the stage in the unit's slot with a new agent, after ending the one there. The new agent gets that stage's brief and effort, starts in the unit's worktree, and is sent its command. The stages are:

- construct: `/opsx:propose` with the unit's intent and sources;
- code: `/opsx:apply`;
- verify: `/opsx:verify`;
- settle: the coder's brief, with the forecast or amendment that reached a unit waiting to merge;
- merge: a submission to the bolt, `wt submit bolt/<bolt> --no-remove`, which sluice lands only when the checks the kit's policy requires of its bolt branches pass on the bolt with the unit merged.

Code SHALL start as soon as the unit's change is committed, with no review between.

#### Scenario: Construct
- **WHEN** `crew unit run a-tenant-creates-its-environments construct` runs
- **THEN** a fresh agent in `places/a-tenant-creates-its-environments` writes the unit's OpenSpec change from its intent and sources, commits it, and stops

#### Scenario: Code before review
- **WHEN** `crew unit run <unit> code` runs on a unit whose stage is `planned`, whose change no batch has yet held
- **THEN** a fresh code agent starts, and nobody was asked to approve the change

#### Scenario: Code before construct has committed
- **WHEN** `crew unit run <unit> code` runs on a unit in `construct`
- **THEN** it is refused until its change is committed

#### Scenario: Verify before the tasks are done
- **WHEN** `crew unit run <unit> verify` runs on a unit in `code`
- **THEN** it is refused, naming the tasks still open

#### Scenario: Merging
- **WHEN** a verified unit's merge stage runs
- **THEN** its agent is told to run `wt submit bolt/<bolt> --no-remove` in the unit's place, and sluice's verdict decides whether the unit lands on the bolt

### Requirement: Fixes during a bolt are built beside its units
`crew fix <team> <name> "<what is wrong>"` SHALL make `fix/<bolt>/<name>` from the team's bolt at `<kit>/places/fix-<bolt>--<name>`. It SHALL start a fresh code agent there in a free slot with the words given. A new fix whose branch or place already exists SHALL be refused, naming the place, and a fix's agent SHALL start only in a worktree on that fix's own branch, made from the team's bolt. `crew fix <team> <name> --merge` SHALL start its merge stage, and the fix SHALL merge into the bolt like a unit, by a submission. A fix SHALL have no OpenSpec change and no plan record. A landing that conflicts with main SHALL be taken by a fix whose agent merges main into its place, resolving the conflict, and which merges into the bolt like any fix; nothing of crew's SHALL move the bolt's branch.

#### Scenario: A red suite on the bolt
- **WHEN** a unit's or fix's submission to the bolt fails a check the kit's policy requires
- **THEN** nothing lands, the bolt is where it was, and the agent fixes the cause in its own place and submits again

#### Scenario: Two teams name a fix the same
- **WHEN** two teams that build in one kit checkout each start a fix named `bolt-takes-main` on their own bolts
- **THEN** each fix has its own branch made from its own team's bolt, `fix/<bolt>/bolt-takes-main`, in its own place, `places/fix-<bolt>--bolt-takes-main`, and each team's status shows only its own fix

#### Scenario: A fix name already in use on the bolt
- **WHEN** a team starts a fix whose branch or place already exists, and none of its slots holds that fix
- **THEN** crew refuses it, naming the place, takes no slot and starts no agent, and records the refusal

#### Scenario: A fix in flight is run again
- **WHEN** a team starts a fix that one of its slots already holds
- **THEN** the fix's agent starts again in that fix's own place, on its own branch

#### Scenario: A place that is not the fix's own
- **WHEN** a fix's place is on a branch other than the fix's own, or its branch was made from another bolt than the team's
- **THEN** crew refuses to start the fix's agent there, naming the place and the branch or bolt it is on

#### Scenario: A fix that adds commits merges
- **WHEN** a fix's branch holds a commit of its own beyond the bolt, and the conductor runs `crew fix <team> <name> --merge`
- **THEN** crew starts the fix's merge stage, as for a unit, and its agent submits it to the bolt

#### Scenario: A fix takes main into the bolt
- **WHEN** a bolt's landing conflicted with main on `README.md`, a fix's agent merged main into the fix's place resolving it, and the conductor runs `crew fix <team> <name> --merge`
- **THEN** crew starts the fix's merge stage, its agent submits it to the bolt, and once sluice lands it the bolt holds main and the landing can be submitted again

### Requirement: A bolt lands on main on the user's word
A bolt whose verification is green SHALL be landed by the partition's main-level ops, on the user's approval of its landing card, by one procedure: `crew bolt submit <bolt>` submits `bolt/<bolt>` to main through sluice and waits for its outcome, main-level ops pushes main without force, and then runs `crew bolt land`; it deploys nothing. `crew bolt submit` SHALL be refused while the kit's main on its host is behind GitHub's, SHALL submit from a short-lived worktree on the bolt's branch at `<kit>/places/land-<bolt>` on the team's host, in the name of whoever asked, SHALL remove that worktree after, and SHALL bring the kit's main checkout level with what landed. The bolt's branch SHALL then be removed, and the team SHALL hold no bolt. A worktree that is kept SHALL NOT stop the landing. When the submission conflicts with main or fails main's checks, nothing SHALL land and nothing SHALL move, and main-level ops SHALL tell the bolt's conductor sluice's words, for the team to take main into the bolt by a fix.

#### Scenario: The bolt lands
- **WHEN** the user approves swb-1's landing card and main-level ops runs `crew bolt submit <bolt>`
- **THEN** sluice lands the bolt on main as a merge commit, the landing's worktree is gone, the kit's main checkout holds what landed with nothing modified, and after the push and `crew bolt land` GitHub's main holds it too, the bolt's records are gone from the plan, and swb-1 can be given its next bolt

#### Scenario: Main is behind GitHub's
- **WHEN** `crew bolt submit` runs while the kit's main on the team's host lacks a commit GitHub's main has
- **THEN** it is refused, saying how far behind main is, and nothing is submitted

#### Scenario: The landing's rebase conflicts
- **WHEN** the bolt and main changed the same lines and `crew bolt submit` runs
- **THEN** the command fails with sluice's words, main and the bolt's branch are where they were, the landing's worktree is gone, and the conductor is told to take main into the bolt by a fix

#### Scenario: The bolt's worktree has uncommitted changes
- **WHEN** `crew bolt land` runs on a bolt given before bolts were branches, whose worktree has a modified file
- **THEN** the bolt lands and the team holds no bolt, and crew says the worktree is kept with its branch because it has uncommitted changes

### Requirement: A worktree goes when its work is over
crew SHALL remove each worktree it made, with its branch, once its work is over and no slot holds it: a bolt's once no plan has the bolt; a unit's once it has merged into its bolt or landed, or no plan has it; a fix's once it has merged into its bolt, or no plan has its bolt. A bolt's branch crew made, which crew marks in the kit's git config when it makes it, SHALL go once no plan has the bolt and no worktree is on it; a deletion git or sluice refuses SHALL keep the branch and name why. It SHALL do this each time it reads a team, for the team's kit checkout, and at once after `crew bolt drop`, `crew unit drop` or `crew bolt land`.

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

### Requirement: crew removes only its own worktrees
crew SHALL remove only worktrees directly under `<kit>/places/` on a `unit/`, `chore/` or `fix/` branch, and the worktree a bolt given before bolts were branches still has, directly under `<kit>/bolts/` on its `bolt/` branch, and only bolt branches it marked as its own. It SHALL never remove the main checkout, a worktree elsewhere, one on another branch or on none, or a locked one, which it names as kept. It SHALL remove nothing when it cannot read every plan the kit's work goes in.

#### Scenario: A worktree made by hand
- **WHEN** a kit checkout has a worktree beside `main` that the user made, on a branch of their own
- **THEN** crew leaves it as it is

#### Scenario: A merge partway through its rebase
- **WHEN** a place is on no branch because a rebase stopped partway
- **THEN** crew leaves it as it is

#### Scenario: A plan that can't be read
- **WHEN** crew reads a team while the plan of a partition whose teams build the kit cannot be fetched
- **THEN** no worktree is removed, and crew says why

## REMOVED Requirements

### Requirement: A fix that carries the bolt onto main becomes its head
**Reason**: Record 0026 supersedes record 0015: nothing of crew's moves a bolt's branch, and a landing's conflict is taken by a fix that merges main into the bolt and is submitted to it.
**Migration**: The conductor starts a fix whose words begin "Take main into the bolt"; it merges as any fix.

### Requirement: A carried bolt is checked and proven again
**Reason**: No fix carries a bolt any more; every merge into a bolt is a submission sluice checks before it lands, and the bolt's verification is sluice's verdict.
**Migration**: None: a fix that takes main into the bolt lands through sluice, which checks it.
