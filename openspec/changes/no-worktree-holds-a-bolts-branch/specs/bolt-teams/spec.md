## MODIFIED Requirements

### Requirement: Work happens in fixed places
A bolt SHALL be built on `bolt/<bolt>`, branched from main, which no worktree SHALL hold; its checkout SHALL be `<kit>/bolts/<bolt>` on `land/<bolt>`, which tracks it. A unit SHALL be built on `unit/<unit>`, branched from the bolt's line, in `<kit>/places/<unit>`, and SHALL merge into the bolt's line with the kit's merge hooks: the bolt's line is `bolt/<bolt>`, or `land/<bolt>` once a fix has carried the bolt onto main. Its place SHALL be removed once it has merged, as every worktree crew made is once its work is over. Each worktree crew makes SHALL be made ready through its kit's declaration before any agent starts in it, and by no script a kit names for crew.

#### Scenario: A unit merges
- **WHEN** the merge stage of a verified unit finishes
- **THEN** `bolt/<bolt>` holds the unit's change, `places/<unit>` is gone, and the unit's slot is free

#### Scenario: A kit with a crew-prepare script
- **WHEN** crew makes a unit's place in a kit whose main checkout's devenv profile holds a `crew-prepare` script
- **THEN** the script does not run

#### Scenario: No worktree on the bolt's branch
- **WHEN** a team holds a bolt and its units are building
- **THEN** `git worktree list` in the kit shows no worktree on `bolt/<bolt>`

### Requirement: Fixes during a bolt are built beside its units
`crew fix <team> <name> "<what is wrong>"` SHALL make `fix/<bolt>/<name>` from the bolt's line at `<kit>/places/fix-<bolt>--<name>`. It SHALL start a fresh code agent there in a free slot with the words given. A new fix whose branch or place already exists SHALL be refused, naming the place, and a fix's agent SHALL start only in a worktree on that fix's own branch, made from the bolt's line. `crew fix <team> <name> --merge` SHALL start its merge stage, and the fix SHALL merge into the bolt's line like a unit, unless the fix carries the bolt onto main, when crew SHALL make the fix's head the head of `land/<bolt>` instead. A fix SHALL have no OpenSpec change and no plan record.

#### Scenario: A red suite on the bolt
- **WHEN** the verification of the bolt's head is red after a merge
- **THEN** the conductor starts a fix on the bolt, before any other unit's code

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
- **WHEN** a fix's branch holds the bolt's commits and a commit of its own beyond them, and the conductor runs `crew fix <team> <name> --merge`
- **THEN** crew starts the fix's merge stage, as for a unit

#### Scenario: A fix after a carry
- **WHEN** a fix has carried the bolt onto main, and the conductor starts another fix on the bolt
- **THEN** the new fix is made from `land/<bolt>`, tracks it, and merges into it with `wt merge`, in a kit on sluice too

### Requirement: A bolt is deployed and tested from its branch
The team's ops SHALL deploy and test from the bolt's checkout, `<kit>/bolts/<bolt>` on `land/<bolt>`, at the head crew last brought it to, into the one shared environment, and SHALL name that head in its proof. It SHALL work the *Proof in dev* lists of the bolt's merged units there. A failure SHALL become a fix on the bolt.

#### Scenario: Proof before landing
- **WHEN** every unit of a bolt has merged
- **THEN** crew brings the checkout level with the bolt, ops deploys it and works each unit's proof list, and the conductor tells the user whether the bolt is ready to land

#### Scenario: A checkout crew could not bring level
- **WHEN** `crew prove` runs while a local edit in the bolt's checkout keeps it behind `bolt/<bolt>`
- **THEN** the proof is refused, naming the file, and no proof starts

### Requirement: A bolt lands on main on the user's word
A proven bolt SHALL be landed by the partition's main-level ops, on the user's approval of its landing card, by one
procedure: from the bolt's checkout it merges `land/<bolt>` into main through the kit's merge hooks, pushes main
without force, and then runs `crew bolt land`; it deploys nothing. The landing SHALL NOT move `bolt/<bolt>`. The bolt's
checkout SHALL then be removed, unless it has uncommitted changes, and the team SHALL hold no bolt. A worktree that is
kept SHALL NOT stop the landing. When the landing's rebase conflicts, main-level ops SHALL abort it so that nothing
lands, and tell the bolt's conductor the commit that conflicted and the files, for the team to carry the bolt onto main
by a fix.

#### Scenario: The bolt lands
- **WHEN** the user approves swb-1's landing card
- **THEN** main holds every unit's change, GitHub's main holds it too, the bolt's records are gone from the plan, and swb-1 can be given its next bolt

#### Scenario: The bolt's worktree has uncommitted changes
- **WHEN** `crew bolt land` runs on a bolt whose checkout has a modified file
- **THEN** the bolt lands and the team holds no bolt, and crew says the checkout is kept with its branch because it has uncommitted changes

#### Scenario: The landing's rebase conflicts
- **WHEN** main-level ops merges a bolt into main and the rebase stops on a conflict
- **THEN** the rebase is aborted, main, `land/<bolt>` and `bolt/<bolt>` are where they were, and the conductor is told the conflicting commit and files and starts a fix that carries the bolt onto main

### Requirement: crew removes only its own worktrees
crew SHALL remove only worktrees directly under `<kit>/bolts/` on a `land/` branch, or on a `bolt/` branch for a bolt given before no worktree held its branch, and directly under `<kit>/places/` on a `unit/` or `fix/` branch, or detached for a verification crew ran. It SHALL never remove the main checkout, a worktree elsewhere, one on another branch, or a locked one, which it names as kept. It SHALL remove nothing when it cannot read every plan the kit's work goes in.

#### Scenario: A worktree made by hand
- **WHEN** a kit checkout has a worktree beside `main` that the user made, on a branch of their own
- **THEN** crew leaves it as it is

#### Scenario: A merge partway through its rebase
- **WHEN** a place is on no branch because its merge stopped partway through a rebase
- **THEN** crew leaves it as it is

#### Scenario: A plan that can't be read
- **WHEN** crew reads a team while the plan of a partition whose teams build the kit cannot be fetched
- **THEN** no worktree is removed, and crew says why

#### Scenario: A bolt's branch with no worktree
- **WHEN** a landed bolt's checkout has been removed and main holds every patch of `bolt/<bolt>`
- **THEN** crew removes `bolt/<bolt>`, and keeps and names it when sluice's hook refuses the delete

### Requirement: A fix that carries the bolt onto main becomes its head
A fix SHALL carry the bolt when the head of `land/<bolt>` is not an ancestor of the fix, the fix holds as many commits beyond the kit's main as `land/<bolt>` does, and, in order, each of the fix's commits is the bolt's commit in the same place replayed: the same message and the same author, its patch the same or changed. `git range-diff` of the two SHALL be printed as the reading and SHALL decide nothing. On `--merge`, crew SHALL then move `land/<bolt>` to the fix's head in the bolt's checkout, end the fix's agent, record the move, and say the old and new heads; `bolt/<bolt>` SHALL NOT move, and no merge or submission SHALL run.

#### Scenario: A fix replays the bolt onto main
- **WHEN** a landing's rebase conflicted, the fix's agent replayed the bolt's three commits onto main resolving one of them, and the conductor runs `crew fix <team> <name> --merge`
- **THEN** `land/<bolt>` is at the fix's head, `bolt/<bolt>` is where it was, the fix reads as merged, its slot and place are freed as after a merge, and crew's output names the old head and new head

#### Scenario: A fix that drops one of the bolt's commits does not carry it
- **WHEN** the fix's branch, on main, holds two of the bolt's three commits and lacks the third
- **THEN** crew does not move `land/<bolt>`, starts the fix's merge stage, and names the bolt's commit that is not in the fix

#### Scenario: A bolt's worktree that is not clean is not moved
- **WHEN** the fix carries the bolt and the bolt's checkout has modified or untracked files git does not ignore, or a rebase or merge in progress
- **THEN** crew moves nothing, starts no merge, names what keeps the checkout from moving, and the refusal is recorded

### Requirement: A carried bolt is checked and proven again
After crew moves `land/<bolt>` to a fix that carries it, crew SHALL verify the new head as after a follow of the bolt, and SHALL say that the bolt must be proven again before it lands. The conductor SHALL ask ops for a new proof and post the bolt's landing card only once that proof is clean.

#### Scenario: The bolt's checks run on the new head
- **WHEN** crew has moved `land/<bolt>` to the fix's head in a kit that declares the checks bolt branches require
- **THEN** a verification of the new head starts, and `crew bolt verify <bolt>` reads that head

#### Scenario: The kit refuses the checks
- **WHEN** the kit declares no checks for bolt branches
- **THEN** `land/<bolt>` is still moved, and crew says no verification runs for the kit, so ops proves the new head without one

#### Scenario: A proof before the move does not land the bolt
- **WHEN** a bolt that ops had proven is carried onto main by a fix
- **THEN** the conductor asks ops to prove it again, and the landing card is posted only after that proof is clean

## ADDED Requirements

### Requirement: The bolt's checkout follows its bolt
Whenever crew reads that `bolt/<bolt>` moved, when a unit's or a fix's merge stage has delivered and in `crew prove`, it SHALL bring the bolt's checkout level by a fast-forward of `land/<bolt>` in the checkout, discarding nothing. When it cannot, crew SHALL change nothing, record it, and tell the conductor what keeps it. Once a fix has carried the bolt, the checkout SHALL follow nothing more.

#### Scenario: sluice lands a unit
- **WHEN** sluice lands unit a on `bolt/<bolt>`, and crew reads that a's merge stage has delivered
- **THEN** `land/<bolt>` is at `bolt/<bolt>`'s head and `git status` in the checkout shows nothing the landing brought

#### Scenario: An edit the move would overwrite
- **WHEN** the bolt's checkout has a local edit to a file the merged unit changed
- **THEN** crew changes nothing there, the merge stage still ends, and the conductor is told which file keeps the checkout behind its bolt

#### Scenario: A checkout crew can't bring level
- **WHEN** the bolt's checkout is on another branch than `land/<bolt>`, or has a rebase or merge in progress
- **THEN** crew changes nothing there and tells the conductor which of these keeps it

#### Scenario: A bolt given before this change
- **WHEN** a bolt's checkout is on `bolt/<bolt>`, made before no worktree held a bolt's branch
- **THEN** crew follows nothing for it, says so once, and the bolt is carried and landed as before
