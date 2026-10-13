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

## ADDED Requirements

### Requirement: Every agent crew starts carries its name for sluice
Every agent crew starts SHALL have `SLUICE_AGENT` in its environment, the same as its `CREW_AGENT`, from its start and again when herdr resumes it.

#### Scenario: A stage's agent starts
- **WHEN** crew starts `swb-1-unit-2` for a code stage
- **THEN** its environment holds `CREW_AGENT=swb-1-unit-2` and `SLUICE_AGENT=swb-1-unit-2`

#### Scenario: herdr resumes an agent
- **WHEN** herdr resumes the conductor's session without crew's environment
- **THEN** its commands see `SLUICE_AGENT` back, the same as its `CREW_AGENT`
