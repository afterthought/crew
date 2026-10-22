## MODIFIED Requirements

### Requirement: Work happens in fixed places
A bolt SHALL be the branch `bolt/<bolt>`, made on GitHub from main by sluice at crew's give, with no worktree, and SHALL move only through sluice. A unit SHALL be built on `unit/<unit>`, branched from `origin/bolt/<bolt>` after a fetch, tracking it, and holding its `After` units' work as it stood when its place was made, in `<kit>/places/<unit>`; a bolt made on its host before gives went through sluice SHALL have its places branched from the local `bolt/<bolt>`, tracking it, until it lands. A chore's and a fix's place SHALL be cut the same way. A unit SHALL merge into its bolt only by a submission through sluice. Its place SHALL be removed once it has merged, as every worktree crew made is once its work is over. Each worktree crew makes SHALL be made ready through its kit's declaration before any agent starts in it, and by no script a kit names for crew. A team's conductor and ops SHALL start in the kit's main checkout, a detached anchor at `origin/main` that the fleet's timer moves and nobody edits in, and SHALL read the bolt by ref. No worktree crew makes or starts an agent in SHALL be on `main` or on a bolt branch, except the landing's short-lived worktree.

#### Scenario: A bolt is given
- **WHEN** `crew bolt give swb-1` gives swb-1 the bolt `b`
- **THEN** `bolt/b` is made on GitHub from main by sluice, no worktree is made for it, and swb-1's conductor and ops start in the kit's main checkout, which is detached

#### Scenario: A unit merges
- **WHEN** the merge stage of a verified unit submits it and sluice lands it
- **THEN** `bolt/<bolt>` holds the unit's change in a merge commit sluice made, `places/<unit>` is gone, and the unit's slot is free

#### Scenario: A place is cut from the bolt on GitHub
- **WHEN** crew makes a unit's, chore's or fix's place on a host whose local `bolt/<bolt>` lags the branch on GitHub
- **THEN** the place is cut from `origin/bolt/<bolt>` after a fetch, tracks it, and holds every merge sluice landed there

#### Scenario: A place of a bolt made before
- **WHEN** crew makes a unit's place for a bolt whose branch is on its host only, its tip's policy naming no remote for it
- **THEN** the place is cut from the local `bolt/<bolt>`, tracks it, and nothing is fetched or made on GitHub for it

#### Scenario: The bolt on GitHub cannot be fetched
- **WHEN** crew makes a place for a bolt on GitHub and the fetch fails or GitHub has no `bolt/<bolt>`
- **THEN** no place is made, and crew names the bolt and the fetch's words

#### Scenario: A kit with a crew-prepare script
- **WHEN** crew makes a unit's place in a kit whose main checkout's devenv profile holds a `crew-prepare` script
- **THEN** the script does not run
