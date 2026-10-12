## MODIFIED Requirements

### Requirement: Work happens in fixed places
A bolt SHALL be built on `bolt/<bolt>`, branched from main, in the worktree `<kit>/bolts/<bolt>`. A unit SHALL be built on `unit/<unit>`, branched from its bolt, in `<kit>/places/<unit>`. A unit SHALL merge into its bolt with the kit's merge hooks. Its place SHALL be removed once it has merged, as every worktree crew made is once its work is over. Each worktree crew makes SHALL be made ready through its kit's declaration before any agent starts in it, and by no script a kit names for crew.

#### Scenario: A unit merges
- **WHEN** the merge stage of a verified unit finishes
- **THEN** `bolt/<bolt>` holds the unit's change, `places/<unit>` is gone, and the unit's slot is free

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
