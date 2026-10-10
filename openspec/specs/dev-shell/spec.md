# dev-shell Specification

## Purpose
TBD - created by archiving change agents-work-inside-crews-devenv-shell. Update Purpose after archive.

## Requirements

### Requirement: A session in a crew checkout works inside crew's devenv shell

A Claude session that starts in a crew checkout SHALL enter that checkout's devenv shell before its first command, at every start (new, resume, `/clear`, compaction), and every command it runs SHALL have the shell's tools first on the path and the host's after them. Entering SHALL print nothing when it succeeds and SHALL never stop the session starting.

#### Scenario: A stage starts in a unit's place

- **WHEN** crew starts a stage's agent in a unit's place in crew
- **THEN** the agent's first command sees `DEVENV_ROOT` naming that place, and `recsel` from the shell's profile

#### Scenario: A resumed session

- **WHEN** herdr resumes a crew agent's session in a crew checkout
- **THEN** its commands run inside that checkout's shell again, and its crew name and partition are still set

#### Scenario: Already inside the shell

- **WHEN** a session is started from a terminal already inside this checkout's devenv shell
- **THEN** the session's environment is not changed

#### Scenario: crew's own start hook

- **WHEN** crew's plugin gives a resumed session its crew name through the same start
- **THEN** the shell's entry keeps that name and adds to it, never replacing it

### Requirement: A session that can't enter the shell is told so

When the shell cannot be entered at a session's start (devenv is missing, fails, or runs past its time), the session SHALL start with its host environment, and SHALL be given one line saying that it is not in crew's devenv shell, that crew's tests and merge gate need it, and that it says so rather than going on without it. The line SHALL NOT tell the session to wrap its commands in `devenv shell --`.

#### Scenario: devenv fails

- **WHEN** devenv exits non-zero at a session's start in a crew checkout
- **THEN** the session starts, its environment is unchanged, and its context holds the one line

### Requirement: No agent wraps a command in devenv shell

CLAUDE.md, the README, the role briefs and crew's skills SHALL tell an agent to run crew's tests and the bolt's verification as they are, `tests/run [name...]` and `sh .config/hooks/bolt-verify.sh`, and SHALL NOT tell it to wrap any command in `devenv shell --`. The merge gate and the bolt's verification hook, which worktrunk runs for whoever merges, SHALL still enter the shell themselves.

#### Scenario: The docs are checked

- **WHEN** crew's suite runs
- **THEN** it fails if CLAUDE.md, README.md, any role brief or any crew skill holds `devenv shell --`

### Requirement: The tests run only inside a devenv shell

`tests/run` SHALL refuse to start, before running any test, when it is not inside a devenv shell, and SHALL say how to enter one: a Claude session in a crew checkout is in it from its start, and a terminal enters it with `devenv shell` or direnv.

#### Scenario: Run from a bare terminal

- **WHEN** `tests/run` is started with no devenv shell in its environment
- **THEN** it exits non-zero, runs no test, and prints how to enter the shell

### Requirement: A person entering a worktree enters the shell

A crew checkout SHALL carry an `.envrc` that enters crew's devenv shell, so a person whose shell runs direnv enters it on changing into the checkout once they have allowed it. devenv's and direnv's working files in a checkout SHALL be ignored by the repository, so entering the shell never leaves a worktree with untracked files.

#### Scenario: A worktree after its first shell

- **WHEN** a session has entered crew's shell in a fresh unit place
- **THEN** `git status --porcelain` in that place prints nothing the session did not write itself
