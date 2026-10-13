## MODIFIED Requirements

### Requirement: Fixes during a bolt are built beside its units
`crew fix <team> <name> "<what is wrong>"` SHALL make `fix/<bolt>/<name>` from the team's bolt at `<kit>/places/fix-<bolt>--<name>`. It SHALL start a fresh code agent there in a free slot with the words given, whether or not the place could be made ready: when a step of its readying failed, the agent SHALL be told the step and its last lines with the fix's words, since a fix is how a bolt is repaired, and the command SHALL say so. A new fix whose branch or place already exists SHALL be refused, naming the place, and a fix's agent SHALL start only in a worktree on that fix's own branch, made from the team's bolt. `crew fix <team> <name> --merge` SHALL start its merge stage, and the fix SHALL merge into the bolt like a unit, by a submission. A fix SHALL have no OpenSpec change and no plan record. A landing that conflicts with main SHALL be taken by a fix whose agent merges main into its place, resolving the conflict, and which merges into the bolt like any fix; nothing of crew's SHALL move the bolt's branch.

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
