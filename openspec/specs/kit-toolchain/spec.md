# kit-toolchain Specification

## Purpose
How a kit declares its toolchain and test runner in sluice's words, and how crew makes a worktree ready from that declaration and runs commands inside it, judging no version of the runner a kit chooses (plan.17, record 0023).

## Requirements

### Requirement: A kit declares its toolchain and test runner in sluice's policy
crew SHALL read a kit's declaration from the `[tests]` table of `.config/sluice.toml` in the worktree in hand, with sluice's keys and meanings: `toolchain`, a command given as a list whose output is shell code that sets the kit's tools up; `runner`, `"moon"` or `"command"`; and `command`, the command a `"command"` runner runs. crew SHALL read nothing else of the file for this. A kit with no file, or no `[tests]` table, SHALL declare nothing.

#### Scenario: A kit that declares both
- **WHEN** a worktree's `.config/sluice.toml` holds `[tests]` with `toolchain = ["devenv", "print-dev-env"]` and `runner = "moon"`
- **THEN** crew reads that toolchain command and the moon runner

#### Scenario: A kit that declares nothing
- **WHEN** a worktree has no `.config/sluice.toml`, or one with no `[tests]` table
- **THEN** crew reads no toolchain and no runner, and says nothing of it

#### Scenario: A declaration crew cannot read
- **WHEN** the file is not TOML, `toolchain` is not a list of strings, `runner` is neither `"moon"` nor `"command"`, or `runner` is `"command"` with no `command`
- **THEN** crew refuses, naming the file and the key

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

### Requirement: A command crew runs in a worktree runs inside its declared toolchain
Every command crew runs in a worktree for its kit's toolchain or runner SHALL run with standard input closed and an environment holding only `PATH`, `HOME`, `USER`, `LOGNAME`, `SHELL`, `TMPDIR`, `LANG`, `TERM`, `PROTO_HOME`, `MOON_HOME` and the `LC_*` variables, as the host has them. After the toolchain command, each SHALL run with the kept toolchain sourced by the `bash` on the PATH, anything the toolchain prints going to standard error.

#### Scenario: A session's environment stays out
- **WHEN** crew makes a place while the command that asked for it runs in another checkout's devenv shell
- **THEN** the place's toolchain command sees no `DEVENV_*`, `GIT_*`, `MOON_*` or `CREW_*` variable

#### Scenario: A toolchain written for a current bash
- **WHEN** the kept toolchain uses bash 4 syntax and the host's `/bin/bash` is 3.2
- **THEN** the setup still runs inside the toolchain

### Requirement: A kit's moon is its own
crew SHALL enforce no floor on the version of moon a kit's toolchain runs: which moon a kit runs is its own, but for sluice's moon runner, which refuses a moon below 2.6 at its run, so a kit runs 2.6 or later before it goes onto sluice. For a moon runner, crew SHALL run `moon --version` inside the toolchain before `moon setup`, and SHALL refuse only output that names no version it can read, naming what was printed; any version it reads SHALL go on to `moon setup`.

#### Scenario: An older moon
- **WHEN** the moon inside a kit's toolchain is 1.41.7, or 2.5.3
- **THEN** crew runs `moon setup` in the place and makes it ready, as for any other version

#### Scenario: A version crew cannot read
- **WHEN** `moon --version` inside a kit's toolchain prints `bash: moon: command not found`, or nothing
- **THEN** crew refuses to make the place ready, naming what was printed
