## MODIFIED Requirements

### Requirement: A worktree is made ready through its kit's declaration
When crew makes a unit's, chore's or fix's worktree, on the team's host and before any agent starts there, it SHALL run the declared toolchain command in the worktree and keep what it prints in the worktree's git directory, outside its tree; then, for a moon runner, `moon setup` inside that toolchain. A `"command"` runner SHALL need no setup. A kit that declares nothing SHALL have nothing run. crew SHALL do the same when it finds the worktree already made. A step that fails SHALL refuse a unit's or chore's stage, whose agent builds on the bolt; a fix's agent SHALL start all the same, told what failed, since a fix is how a bolt is repaired (record 0028).

#### Scenario: A kit on moon
- **WHEN** crew makes a unit's place in a kit declaring a toolchain and the moon runner
- **THEN** the toolchain command has run in the place, its output is kept in the place's git directory, and `moon setup` has run in the place with that toolchain sourced, before the construct agent starts

#### Scenario: A toolchain that fails
- **WHEN** the declared toolchain command exits non-zero in a unit's or a chore's new place
- **THEN** the command is refused, naming the place and the step with the tool's last lines, no agent starts, and running the command again sets the place up

#### Scenario: A toolchain that fails in a fix's place
- **WHEN** the declared toolchain command, or the runner's setup, fails in a fix's new place
- **THEN** the fix's agent starts there all the same, told the step that failed and its last lines (bolt-teams, "Fixes during a bolt are built beside its units")

#### Scenario: Nothing declared
- **WHEN** crew makes a place in a kit that declares nothing
- **THEN** nothing runs in the place but git, and the construct agent starts
