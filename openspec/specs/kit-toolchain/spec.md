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
