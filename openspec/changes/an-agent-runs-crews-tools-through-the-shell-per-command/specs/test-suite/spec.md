## ADDED Requirements

### Requirement: The test runners enter crew's shell themselves
`tests/run` and `tests/suite` SHALL run inside crew's devenv shell. Started outside it, with no `DEVENV_ROOT`, each SHALL run itself again under `devenv shell --` from its own checkout, whichever folder it was started from, and go on there. A shell that sets no `DEVENV_ROOT` SHALL stop it, saying so, rather than have it enter again; a host with no devenv SHALL stop it, saying so, before any test runs.

#### Scenario: Started outside the shell
- **WHEN** `tests/run no-such` is started from another folder with no devenv shell in its environment
- **THEN** devenv is run once, from the checkout, as `devenv shell -- <checkout>/tests/run no-such`, and inside it the run says there is no test `t-no-such`

#### Scenario: The suite started outside the shell
- **WHEN** `tests/suite --no-such` is started the same way
- **THEN** devenv is run once as `devenv shell -- <checkout>/tests/suite --no-such`, and inside it the suite prints its usage and exits 2

#### Scenario: A shell that sets no DEVENV_ROOT
- **WHEN** the shell a runner enters sets no `DEVENV_ROOT`
- **THEN** the runner exits 2, saying devenv shell set no `DEVENV_ROOT`, and devenv was run once

#### Scenario: No devenv on the host
- **WHEN** a runner is started outside the shell on a path with no devenv
- **THEN** it exits 2, saying devenv is not on the host's path, and runs nothing

### Requirement: An agent runs crew's tools through the shell per command
CLAUDE.md SHALL name how an agent runs crew's application tools, through crew's shell per command, `devenv shell -- <command>`; no role brief and no crew skill SHALL name it, since how a kit's tools are run is the kit's CLAUDE.md's to say (`tests.7`).

#### Scenario: The docs are checked
- **WHEN** crew's suite runs
- **THEN** it fails if CLAUDE.md does not hold `devenv shell -- `, or if any role brief or crew skill does

### Requirement: A worktree stays clean of the shell's working files
A crew checkout SHALL carry an `.envrc` that enters crew's devenv shell, for a person whose shell runs direnv, and SHALL ignore devenv's and direnv's working files and the tests' `.venv`, so entering the shell per command never leaves a worktree with untracked files.

#### Scenario: The checkout is checked
- **WHEN** crew's suite runs
- **THEN** it fails unless `.envrc` holds `use devenv` and `.gitignore` holds `.devenv/`, `.direnv/`, `tests/.venv/` and `!.envrc`
