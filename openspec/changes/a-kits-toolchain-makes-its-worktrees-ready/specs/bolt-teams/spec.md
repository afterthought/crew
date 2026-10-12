## MODIFIED Requirements

### Requirement: Work happens in fixed places
A bolt SHALL be built on `bolt/<bolt>`, branched from main, in the worktree `<kit>/bolts/<bolt>`. A unit SHALL be built on `unit/<unit>`, branched from its bolt, in `<kit>/places/<unit>`. A unit SHALL merge into its bolt with the kit's merge hooks. Its place SHALL be removed once it has merged, as every worktree crew made is once its work is over. Each worktree crew makes SHALL be made ready by its kit's own toolchain, on the team's host: when it holds `devenv.nix` and `.moon/workspace.yml`, by `moon setup` inside the worktree's own devenv shell, and otherwise by nothing. crew SHALL run no script a kit names for crew, and SHALL read no kit's devenv profile.

#### Scenario: A unit merges
- **WHEN** the merge stage of a verified unit finishes
- **THEN** `bolt/<bolt>` holds the unit's change, `places/<unit>` is gone, and the unit's slot is free

#### Scenario: A kit with devenv and moon
- **WHEN** crew makes a unit's place in a kit whose tree holds `devenv.nix` and `.moon/workspace.yml`
- **THEN** `moon setup` has run inside the place's devenv shell, in the place, before the construct agent starts

#### Scenario: A kit without them
- **WHEN** crew makes a unit's place in a kit whose tree lacks `devenv.nix` or `.moon/workspace.yml`
- **THEN** crew runs nothing in the place, and the construct agent starts

#### Scenario: A setup that fails
- **WHEN** `moon setup` fails in a place crew has just made
- **THEN** the command is refused in the tool's words, naming the place, no agent starts, and running the command again sets the place up

## ADDED Requirements

### Requirement: Every agent crew starts carries its name for sluice
Every agent crew starts SHALL have `SLUICE_AGENT` in its environment, the same as its `CREW_AGENT`, from its start and again when herdr resumes it.

#### Scenario: A stage's agent starts
- **WHEN** crew starts `swb-1-unit-2` for a code stage
- **THEN** its environment holds `CREW_AGENT=swb-1-unit-2` and `SLUICE_AGENT=swb-1-unit-2`

#### Scenario: herdr resumes an agent
- **WHEN** herdr resumes the conductor's session without crew's environment
- **THEN** its commands see `SLUICE_AGENT` back, the same as its `CREW_AGENT`

### Requirement: A bolt's worktree follows its branch in a kit that merges through sluice
In a kit that merges through sluice, crew SHALL bring the bolt's worktree level with `bolt/<bolt>` when a unit's or a fix's merge stage has delivered and before it tells ops to prove the bolt, discarding nothing. When it cannot, crew SHALL change nothing, record it, and tell the conductor what keeps it. A kit that merges with `wt merge` SHALL NOT be touched by it.

#### Scenario: sluice lands a unit
- **WHEN** sluice lands unit a on `bolt/<bolt>`, and crew reads that a's merge stage has delivered
- **THEN** `git status` in `<kit>/bolts/<bolt>` shows nothing staged and nothing changed that the landing brought

#### Scenario: What the worktree held stays
- **WHEN** the bolt's worktree held an untracked file and a local edit to a file the landing did not touch
- **THEN** after crew levels it both are still there

#### Scenario: An edit the landing would overwrite
- **WHEN** the bolt's worktree has a local edit to a file the landing changed
- **THEN** crew changes nothing there, the merge stage still ends, and the conductor is told which file keeps the worktree behind its branch

#### Scenario: A worktree crew can't level
- **WHEN** the bolt's worktree is on another branch, has a rebase or merge in progress, or holds a change staged by hand
- **THEN** crew changes nothing there and tells the conductor which of these keeps it
