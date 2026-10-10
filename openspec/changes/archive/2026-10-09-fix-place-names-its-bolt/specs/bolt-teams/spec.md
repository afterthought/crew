## MODIFIED Requirements

### Requirement: Fixes during a bolt are built beside its units
`crew fix <team> <name> "<what is wrong>"` SHALL make `fix/<bolt>/<name>` from the team's bolt at `<kit>/places/fix-<bolt>--<name>`. It SHALL start a fresh code agent there in a free slot with the words given. A new fix whose branch or place already exists SHALL be refused, naming the place, and a fix's agent SHALL start only in a worktree on that fix's own branch, made from the team's bolt. `crew fix <team> <name> --merge` SHALL start its merge stage, and the fix SHALL merge into the bolt like a unit. A fix SHALL have no OpenSpec change and no plan record.

#### Scenario: A red suite on the bolt
- **WHEN** the bolt's verification is red after a merge
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
