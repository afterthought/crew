## MODIFIED Requirements

### Requirement: Work happens in fixed places
A bolt SHALL be the branch `bolt/<bolt>`, made on GitHub from `origin/main` by sluice at crew's give, with no worktree, and SHALL move only through sluice. A unit SHALL be built on `unit/<unit>`, branched from `origin/bolt/<bolt>` after a fetch and holding its `After` units' work as it stood when its place was made, in `<kit>/places/<unit>`. A unit SHALL merge into its bolt only by a submission through sluice. Its place SHALL be removed once it has merged, as every worktree crew made is once its work is over. Each worktree crew makes SHALL be made ready through its kit's declaration before any agent starts in it, and by no script a kit names for crew. A team's conductor and ops SHALL start in the kit's main checkout, a detached anchor at `origin/main` that the fleet's timer moves and nobody edits in, and SHALL read the bolt by ref. No worktree crew makes or starts an agent in SHALL be on `main` or on a bolt branch, except the landing's short-lived worktree.

#### Scenario: A bolt is given
- **WHEN** `crew bolt give swb-1` gives swb-1 the bolt `b`
- **THEN** `bolt/b` is made on GitHub from `origin/main` by sluice, no worktree is made for it, and swb-1's conductor and ops start in the kit's main checkout, which is detached

#### Scenario: A unit merges
- **WHEN** the merge stage of a verified unit submits it and sluice lands it
- **THEN** `bolt/<bolt>` holds the unit's change in a merge commit sluice made, `places/<unit>` is gone, and the unit's slot is free

#### Scenario: A place is cut from the bolt on GitHub
- **WHEN** crew makes a unit's place on a host whose local `bolt/<bolt>` lags the branch on GitHub
- **THEN** the place is cut from `origin/bolt/<bolt>` after a fetch, tracking it, and holds every merge sluice landed there

#### Scenario: A kit with a crew-prepare script
- **WHEN** crew makes a unit's place in a kit whose main checkout's devenv profile holds a `crew-prepare` script
- **THEN** the script does not run

### Requirement: A bolt lands on main on the user's word
A bolt whose verification is green SHALL be landed by the partition's main-level ops, on the user's approval of its landing card, by one procedure: `crew bolt submit <bolt>` submits `bolt/<bolt>` to main through sluice and waits for its outcome, and main-level ops then runs `crew bolt land`; it pushes nothing, levels no host and deploys nothing. `crew bolt submit` SHALL submit from a short-lived worktree on the bolt's branch at `<kit>/places/land-<bolt>` on the team's host, in the name of whoever asked, SHALL pass sluice's warning that the worktree holds a queued branch through and stop on nothing of it, SHALL remove that worktree after, SHALL record the landing's head as `origin/main` after a fetch, and SHALL bring the kit's main checkout level only while that checkout is on branch `main`, saying nothing when it is detached. It SHALL NOT be refused for the host's local `main` lagging GitHub's. `crew bolt land` SHALL close the landing card naming the fleet's timer, SHALL ask sluice to delete the bolt's branch and name a refusal, and the team SHALL then hold no bolt. A worktree that is kept SHALL NOT stop the landing. When the submission conflicts with main or fails main's checks, nothing SHALL land and nothing SHALL move, and main-level ops SHALL tell the bolt's conductor sluice's words, for the team to take `origin/main` into the bolt by a fix. While a bolt's landing is queued, `crew unit run` SHALL refuse to start a unit on that bolt, naming the landing.

#### Scenario: The bolt lands
- **WHEN** the user approves swb-1's landing card and main-level ops runs `crew bolt submit <bolt>`
- **THEN** sluice lands the bolt on GitHub's main as a merge commit, the landing's worktree is gone, the landing is recorded at `origin/main`'s head, and after `crew bolt land` the bolt's branch is gone from GitHub, its records are gone from the plan, the card is closed naming the timer, and swb-1 can be given its next bolt

#### Scenario: Main is behind GitHub's
- **WHEN** `crew bolt submit` runs while the kit's local `main` on the team's host lacks a commit GitHub's main has
- **THEN** the submission runs, sluice forms the landing on GitHub's main, and nothing is refused for the lag

#### Scenario: The anchor is detached
- **WHEN** `crew bolt submit` runs on a host whose kit main checkout is detached
- **THEN** the checkout is not touched after the landing, and the command says nothing of levelling

#### Scenario: The landing's rebase conflicts
- **WHEN** the bolt and main changed the same lines and `crew bolt submit` runs
- **THEN** the command fails with sluice's words, main and the bolt's branch are where they were, the landing's worktree is gone, and the conductor is told to take `origin/main` into the bolt by a fix

#### Scenario: A unit during a queued landing
- **WHEN** a conductor runs `crew unit run <unit> construct` for a unit of a bolt whose landing is submitted and not yet landed or refused
- **THEN** it is refused, naming the landing, and no place is made

#### Scenario: The bolt's worktree has uncommitted changes
- **WHEN** `crew bolt land` runs on a bolt given before bolts were branches, whose worktree has a modified file
- **THEN** the bolt lands and the team holds no bolt, and crew says the worktree is kept with its branch because it has uncommitted changes

### Requirement: crew removes only its own worktrees
crew SHALL remove only worktrees directly under `<kit>/places/` on a `unit/`, `chore/` or `fix/` branch, and the worktree a bolt given before bolts were branches still has, directly under `<kit>/bolts/`, and only bolt branches it marked as its own. A `<kit>/bolts/` worktree still on its `bolt/` branch SHALL be detached at the bolt's tip by the next read of the team when it is clean, and named as kept when it is dirty, so that no worktree of crew's holds a bolt branch. It SHALL never remove the main checkout, which is the kit's detached anchor it never moves, a worktree elsewhere, one on another branch, or a locked one, which it names as kept. It SHALL remove nothing when it cannot read every plan the kit's work goes in.

#### Scenario: A legacy bolt worktree on its branch
- **WHEN** a kit checkout has `bolts/b` on `bolt/b` with nothing modified and the team is read
- **THEN** `bolts/b` is detached at `bolt/b`'s tip and crew says so, and it goes through the kit's remove hooks when the bolt is over

#### Scenario: A legacy bolt worktree with changes
- **WHEN** a kit checkout has `bolts/b` on `bolt/b` with a modified file
- **THEN** crew leaves it on the branch and names it as kept for its changes, every read, until it is clean

#### Scenario: A worktree made by hand
- **WHEN** a kit checkout has a worktree beside `main` that the user made, on a branch of their own
- **THEN** crew leaves it as it is

#### Scenario: A merge partway through its rebase
- **WHEN** a place is on no branch because a rebase stopped partway
- **THEN** crew leaves it as it is

#### Scenario: A plan that can't be read
- **WHEN** crew reads a team while the plan of a partition whose teams build the kit cannot be fetched
- **THEN** no worktree is removed, and crew says why
