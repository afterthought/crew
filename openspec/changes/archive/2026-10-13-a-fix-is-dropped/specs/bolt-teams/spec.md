## MODIFIED Requirements

### Requirement: Fixes during a bolt are built beside its units
`crew fix <team> <name> "<what is wrong>"` SHALL make `fix/<bolt>/<name>` from the team's bolt at `<kit>/places/fix-<bolt>--<name>`. It SHALL start a fresh code agent there in a free slot with the words given, whether or not the place could be made ready: when a step of its readying failed, the agent SHALL be told the step and its last lines with the fix's words, since a fix is how a bolt is repaired, and the command SHALL say so. A new fix whose branch or place already exists SHALL be refused, naming the place, and a fix's agent SHALL start only in a worktree on that fix's own branch, made from the team's bolt. `crew fix <team> <name> --merge` SHALL start its merge stage, and the fix SHALL merge into the bolt like a unit, by a submission. `crew fix <team> <name> --drop` SHALL end a fix that is not wanted, whether a slot holds it or only its branch or place stands: its slot SHALL be freed and its agent ended when one is up, a working agent only with `--force`, and its place and branch SHALL go as a dropped unit's do, its branch kept and named when it holds commits whose patch the bolt lacks. A fix that has merged into its bolt SHALL NOT be dropped, and a drop refused SHALL be recorded. A fix SHALL have no OpenSpec change and no plan record. A landing that conflicts with main SHALL be taken by a fix whose agent merges main into its place, resolving the conflict, and which merges into the bolt like any fix; nothing of crew's SHALL move the bolt's branch.

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

#### Scenario: A bolt whose toolchain fails
- **WHEN** a team starts a fix and the bolt's declared toolchain or its runner's setup fails in the fix's new place
- **THEN** the fix's agent starts there, its prompt holding the fix's words, the step that failed and its last lines, and the start is recorded with no refusal

#### Scenario: A fix not wanted is dropped
- **WHEN** the conductor runs `crew fix <team> <name> --drop` on a fix a slot holds, whose agent is idle and whose branch holds nothing beyond the bolt
- **THEN** its slot is freed and its agent ended, its place and branch are removed through the kit's `wt remove`, and the drop is recorded

#### Scenario: A fix whose agent is working
- **WHEN** the conductor drops a fix whose agent is working, without `--force`
- **THEN** crew refuses, saying the agent is working and that `--force` ends it anyway, records the refusal, and frees nothing

#### Scenario: A fix standing with no slot
- **WHEN** a fix's branch and place stand with no slot holding them, the branch holding a commit of its own, and the conductor drops it
- **THEN** its place is removed, and its branch is kept, named with the commit it is at and how many commits of its own it holds

#### Scenario: A merged fix
- **WHEN** the conductor drops a fix that has merged into its bolt
- **THEN** crew refuses, saying it has merged and that a new fix undoes it, and records the refusal

### Requirement: A worktree goes when its work is over
crew SHALL remove each worktree it made, with its branch, once its work is over and no slot holds it: a bolt's once no plan has the bolt; a unit's once it has merged into its bolt or landed, or no plan has it; a fix's once it has merged into its bolt, its conductor dropped it, or no plan has its bolt. A dropped fix's branch SHALL be kept and named when `git cherry` finds commits whose patch its bolt lacks, or cannot compare it with its bolt, and SHALL then be the user's; one holding nothing beyond its bolt SHALL go. A bolt's branch crew made, which crew marks in the kit's git config when it makes it, SHALL go once no plan has the bolt and no worktree is on it; a deletion git or sluice refuses SHALL keep the branch and name why. It SHALL do this each time it reads a team, for the team's kit checkout, and at once after `crew bolt drop`, `crew unit drop` or `crew bolt land`.

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

#### Scenario: A dropped fix's place with uncommitted changes
- **WHEN** a fix is dropped while its place holds a file nobody committed
- **THEN** its place and branch are kept, and every read names them until the place is clean, when crew removes them
