## ADDED Requirements

### Requirement: A worktree goes through the kit's remove hooks
crew SHALL remove each worktree it removes through the kit's own worktree tool, run from the kit's main checkout, so the kit's remove hooks run: those before removal with the worktree's files still there, those after it once it is gone. crew SHALL NOT skip the kit's hooks, nor approve them for the user. A kit with no remove hooks SHALL see its worktrees go as before, with no approval asked.

#### Scenario: A kit that tears down what it stood up
- **WHEN** a merged fix's place is removed in a kit whose remove hooks tear down what it stood up for that worktree, approved on that host
- **THEN** the hook that runs before removal finds the place's files, the place is then removed, and the hook that runs after removal runs

#### Scenario: A kit with merge hooks only
- **WHEN** a merged unit's place is removed in a kit whose worktree config has only merge hooks
- **THEN** the place and its branch go as before, and no approval is asked

### Requirement: A remove hook that fails keeps the worktree
A worktree whose removal the kit's worktree tool refuses, because a remove hook that runs before removal failed or because the user has not approved the kit's hooks on that host, SHALL be kept with its branch. Each read of the team SHALL name it with what the tool said failed, never the tool's advice to skip hooks or prompts, and SHALL try it again, removing it once the tool accepts.

#### Scenario: The kit's hook fails
- **WHEN** a merged unit's place is removed and the kit's hook before removal exits non-zero
- **THEN** the place and its branch are kept, and `crew status` of the team names the place and the hook that failed

#### Scenario: The hook is fixed
- **WHEN** the cause of a failed remove hook is cleared
- **THEN** the next `crew status` of the team runs the hook again, removes the place, and decides its branch

#### Scenario: Hooks not yet approved on the host
- **WHEN** a kit has remove hooks the user has not approved on the team's host
- **THEN** no hook runs, the worktree and its branch are kept, and crew names the worktree and says the kit's hooks wait for the user's approval on that host

### Requirement: The branch is crew's to decide, never the worktree tool's
When crew removes a worktree through the kit's worktree tool, the tool SHALL leave the worktree's branch alone, and crew SHALL then keep or remove the branch by its own judgment. When crew cannot tell from the tool that the branch was left alone, it SHALL keep the branch and say so.

#### Scenario: A branch the tool would have kept
- **WHEN** a landed bolt's worktree is removed and the tool would judge its branch unmerged
- **THEN** the branch is kept or removed as crew's own rule says, and crew's message names what became of it

#### Scenario: The tool's answer can't be read
- **WHEN** the tool removes a worktree but crew cannot read what it says of the branch
- **THEN** crew says the worktree is removed and its branch kept, because crew could not tell what became of it
