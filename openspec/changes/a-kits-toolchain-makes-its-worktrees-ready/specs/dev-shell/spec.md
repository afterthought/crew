## RENAMED Requirements

- FROM: `### Requirement: A session in a crew checkout works inside crew's devenv shell`
- TO: `### Requirement: A session works inside its checkout's devenv shell`

## MODIFIED Requirements

### Requirement: A session works inside its checkout's devenv shell
A Claude session that starts in a git checkout with `devenv.nix` at its root, crew's or any kit's, SHALL enter that checkout's devenv shell before its first command, at every start (new, resume, `/clear`, compaction), through crew's plugin, and every command it runs SHALL have the shell's tools first on the path and the host's after them. Entering SHALL print nothing when it succeeds and SHALL never stop the session starting. A session in no checkout, or in a checkout without `devenv.nix`, SHALL be left as it started.

#### Scenario: A stage starts in a unit's place
- **WHEN** crew starts a stage's agent in a unit's place in a kit with `devenv.nix`
- **THEN** the agent's first command sees `DEVENV_ROOT` naming that place, and the tools of that place's shell

#### Scenario: A session below the checkout's root
- **WHEN** a session starts in a folder inside a checkout whose root holds `devenv.nix`
- **THEN** its commands run inside the shell of the checkout's root

#### Scenario: A checkout without devenv
- **WHEN** a session starts in a checkout with no `devenv.nix`, or in a folder in no checkout
- **THEN** the session's environment is not changed and devenv is not run

#### Scenario: A resumed session
- **WHEN** herdr resumes a crew agent's session in a checkout with `devenv.nix`
- **THEN** its commands run inside that checkout's shell again, and its crew name and partition are still set

#### Scenario: Already inside the shell
- **WHEN** a session is started from a terminal already inside its checkout's devenv shell
- **THEN** the session's environment is not changed

#### Scenario: crew's own start hook
- **WHEN** crew's plugin gives a resumed session its crew name through the same start
- **THEN** the shell's entry keeps that name and adds to it, never replacing it

### Requirement: A session that can't enter the shell is told so
When the shell cannot be entered at a session's start (devenv is missing, fails, or runs past its time), the session SHALL start with its host environment, and SHALL be given one line saying that it is not in its checkout's devenv shell, that the checkout's tests and merge gate need it, and that it says so rather than going on without it. The line SHALL NOT tell the session to wrap its commands in `devenv shell --`.

#### Scenario: devenv fails
- **WHEN** devenv exits non-zero at a session's start in a checkout with `devenv.nix`
- **THEN** the session starts, its environment is unchanged, and its context holds the one line

## ADDED Requirements

### Requirement: crew's shell runs the moon sluice pins and the Python crew runs on
crew's devenv shell SHALL carry moon at the version sluice's moon profile needs, 2.6 or later, and Python at the minor the fleet's hosts run crew on, with pytest. moon SHALL run the shell's own tools, with no toolchain of moon's configured in crew.

#### Scenario: The tests' Python
- **WHEN** crew's logic tier runs inside crew's shell
- **THEN** `python3` there is the minor the fleet runs crew on, and pytest imports

#### Scenario: moon's version
- **WHEN** `moon --version` runs inside crew's shell
- **THEN** it prints moon 2.6 or later
