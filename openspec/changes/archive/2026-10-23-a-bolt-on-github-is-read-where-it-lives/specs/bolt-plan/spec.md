## ADDED Requirements

### Requirement: A bolt on GitHub is read where it lives
crew SHALL read a bolt at GitHub's copy of its branch, `origin/bolt/<bolt>`, when the host holds that copy and the policy in it names a remote for the bolt, and otherwise at the host's own `bolt/<bolt>`. Its head, verification, the changes and chores it holds, and every stage read from it SHALL come from that ref. crew SHALL never read a bolt on GitHub from the host's own `bolt/<bolt>`, sluice's copy, whether or not sluice has levelled it.

#### Scenario: A merge landed on GitHub while the host's copy stayed behind
- **WHEN** sluice lands a unit's merge and a chore's merge on GitHub's `bolt/b`, the host has fetched it, and the host's own `bolt/b` is still at the commit before them
- **THEN** the unit and the chore read `merged`, the bolt's head is GitHub's, and its verification is the verdict at that head

#### Scenario: A proven bolt whose copy lags
- **WHEN** every unit of a bolt on GitHub has merged and the `Sluice-Result` at GitHub's head starts `passed`, while the host's `bolt/b` is at an earlier landing
- **THEN** the bolt reads proven, and a give to its team is not refused for it

#### Scenario: A bolt kept on its host
- **WHEN** a bolt was made before gives went through sluice, the policy at GitHub's copy of it names no remote for its bolts, and the host's own `bolt/b` holds merges GitHub's copy lacks
- **THEN** the bolt is read at the host's `bolt/b`, those merges counted

#### Scenario: A bolt GitHub's copy of which this host has not got
- **WHEN** the host holds no `origin/bolt/b`
- **THEN** the bolt is read at the host's `bolt/b`, the only copy the host has, and is missing when that is not there either

#### Scenario: A policy crew can't read
- **WHEN** the policy in GitHub's copy of the bolt is not TOML
- **THEN** the bolt's stages read `unknown`, naming the file and the bolt, and nothing is read from the host's `bolt/b`

#### Scenario: A chore's place and a fix beside a bolt on GitHub
- **WHEN** a chore's place holds one commit of its own beyond GitHub's `bolt/b`, and a fix's tip is in GitHub's `bolt/b` but not in the host's
- **THEN** the chore reads `verify` and the fix reads merged

### Requirement: A bolt on GitHub is fetched where a decision rests on it
As main is read (plan.18), crew SHALL read a bolt on GitHub as the host last fetched it on every team read and every refresh of the rail and the board, fetching nothing. `crew bolts`, a give's check that the team's bolts are proven, each look a wait takes at a merge stage, and a give's making of a branch SHALL fetch the kit's origin first. A fetch that fails SHALL be named with git's words, never read past to the host's copy.

#### Scenario: A wait on a merge sees it at once
- **WHEN** `crew chore wait <chore>` waits on a merge, and sluice lands it on GitHub's `bolt/b` without moving the host's `bolt/b` or its tracking ref
- **THEN** the wait's next look fetches, reads the chore in GitHub's `bolt/b`, and returns with the merge delivered at GitHub's head

#### Scenario: crew bolts after a landing elsewhere
- **WHEN** a merge has landed on GitHub's `bolt/b` since the host last fetched, and `crew bolts` runs
- **THEN** it fetches the kit's origin once on the team's host and shows the merged unit as `merged`

#### Scenario: The board does not fetch
- **WHEN** the rail's or the board's refresh reads the team's kit
- **THEN** no fetch is run, and the bolt is read at `origin/bolt/b` as the host last fetched it

#### Scenario: A fetch that fails
- **WHEN** `crew bolts` runs and the fetch of the kit's origin on the team's host fails
- **THEN** the kit's stages read `unknown`, naming that GitHub could not be fetched and git's words, and nothing is read from the host's `bolt/b`

#### Scenario: A give fetches the branch it made
- **WHEN** `crew bolt give` has sluice make `bolt/b` on GitHub
- **THEN** the host holds `origin/bolt/b` at the commit sluice made it at before the give's plan write, and the team's next read reads the bolt there
