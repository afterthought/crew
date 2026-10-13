## REMOVED Requirements

### Requirement: A session in a crew checkout works inside crew's devenv shell
**Reason**: Record 0024: no session is entered into a kit's shell at its start; an agent runs crew's tools through the shell per command, so an edit to the shell's files reaches its next command (`tests.7`).
**Migration**: Run crew's tools as `devenv shell -- <command>` from the checkout, as CLAUDE.md says; `tests/suite`, `tests/run` and the merge hooks enter the shell themselves (`test-suite`).

### Requirement: A session that can't enter the shell is told so
**Reason**: Nothing enters a session into the shell any more (record 0024).
**Migration**: A wrapped command that can't enter the shell fails with devenv's own words; a tool run outside it fails for want of the tool.

### Requirement: No agent wraps a command in devenv shell
**Reason**: Record 0024 reverses it: an agent wraps each command that needs crew's tools.
**Migration**: `test-suite`'s "An agent runs crew's tools through the shell per command": CLAUDE.md names the wrap, and no brief or skill does.

### Requirement: The tests run only inside a devenv shell
**Reason**: The runners enter the shell themselves rather than refusing (record 0024, `tests.1`).
**Migration**: `test-suite`'s "The test runners enter crew's shell themselves".

### Requirement: A person entering a worktree enters the shell
**Reason**: What it holds of a worktree is the suite's to keep, with the rest of what the runners need.
**Migration**: `test-suite`'s "A worktree stays clean of the shell's working files".
