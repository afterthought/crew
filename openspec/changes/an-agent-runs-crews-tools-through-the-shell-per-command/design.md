# Design

## Context

See proposal.md for why and record 0024 for the decision; this is how. What shapes it:

- **crew's hook** (`.claude/hooks/devenv-shell`, run by `.claude/settings.json` at every SessionStart) entered the checkout's devenv shell and appended what it set to `CLAUDE_ENV_FILE`. `tests/t-dev-shell.sh` tested it with a stand-in devenv, and also held checks that are not the hook's: `tests/run` refusing outside the shell, no doc naming the wrap, the `.envrc` and `.gitignore`, and crew's moon and Python.
- **The runners** (`tests/run`, `tests/suite`) refuse with exit 2 when `DEVENV_ROOT` is unset. worktrunk's merge hooks (`.config/wt.toml`) already enter the shell themselves, `devenv shell -- ...`.
- **Entering crew's shell** (`devenv.nix`'s `enterShell`) links moon's archives, sets crew's own `PROTO_HOME` and `MOON_HOME` in the git common dir, runs `proto install --config-mode upwards` and activates proto's tools. Read on mac-studio, 2026-10-13, ten warm entries of `devenv shell -- true` each: a median of 3.21 seconds at a load of 15 with `proto install` on every entry, 0.37 seconds with it removed; `proto install` alone, with every pin installed, 1.4 seconds of wall and 1.2 of CPU.
- **proto's layout** (proto 0.63.1): a tool's version lives at `<PROTO_HOME>/tools/<tool>/<version>/`, read in crew's own home: `moon/2.6.1`, `python/3.13.15`, `uv/0.13.0`. `.prototools` pins each as `<tool> = "<version>"`, one a line, above any `[section]`.
- **devenv shell** keeps the caller's environment and sets `DEVENV_ROOT` to the checkout it entered (read 2026-10-13).

Rules relied on: `tests.1` and `tests.7` as amended with record 0024 (built here), `tests.10` (the tasks' inputs follow the tests), `tests.11` (the toolchain checks are the contract tier's: moon and Python run for real), `tests.12`, `code.1` (crew's toolchain), `docs.3` (the open toolchain change's delta moves), `docs.4` (the spec goes through this delta), `docs.6`. Pages whose area this touches: `tests.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**
- No session in a crew checkout is entered into crew's shell by anything crew carries.
- An agent runs crew's tools as CLAUDE.md says, and crew's runners work from any shell.
- A wrapped command costs a warm entry, not an install.

**Non-Goals:**
- swancloud's generated hook and the host's path: swancloud's unit.
- A kit-neutral per-command runner in crew (record 0024: not added).

## Decisions

### The runners enter the shell themselves

Each of `tests/run` and `tests/suite`, with `DEVENV_ROOT` unset, runs itself again as `devenv shell -- <its own path> <args>` from its own checkout's root, with `CREW_TESTS_ENTERING` set; inside, with `DEVENV_ROOT` set, it unsets that and goes on as before. A shell that comes back without `DEVENV_ROOT` while `CREW_TESTS_ENTERING` is set refuses, saying so, so the runner never loops; a host with no devenv refuses, saying so. The check stays `DEVENV_ROOT` unset, as record 0024 has it: a runner started inside another checkout's shell runs there, as it did.

### Proto's pins installed only when one is missing

`enterShell` reads `.prototools` line by line, skipping blank lines and comments and stopping at the first `[section]`, and runs `proto install --config-mode upwards` once, only when a pin's version folder is missing from the proto home; otherwise it activates at once. A fresh clone, its proto home empty, installs every pin at its first entry (read 2026-10-13: a clone's first entry installed moon, Python and uv, 24 seconds, evaluation included). Readying a worktree sources the printed shell the same way (record 0023, point 4), so a pin a rebase bumps is installed at the next entry or readying. A version folder an interrupted install left half made reads as installed; proto's own install is what repairs it, run by hand.

### Where t-dev-shell's checks go

- CLAUDE.md names `devenv shell -- `, and no brief or skill does; the `.envrc` enters devenv; `.gitignore` ignores `.devenv/`, `.direnv/` and `tests/.venv/` and keeps `.envrc`: `tests/t-docs.sh`, which already holds the docs.
- moon 2.6 or later, proto's under crew's own home, at or above sluice's floor (`kit.MOON_FLOOR`); the tests on Python 3.13 with pytest: `tests/contract/test_toolchain.py`.
- The runners entering the shell: `tests/t-runner.sh`, with a stand-in devenv first on the path that logs where it ran and what, and sets `DEVENV_ROOT` unless told not to.

### The specs

`dev-shell` loses every requirement: a session entered at its start, the line a session that can't enter is given and "no agent wraps" go with record 0024; "the tests run only inside a devenv shell" and "a person entering a worktree enters the shell" become `test-suite`'s, as the runners entering the shell and a worktree that stays clean. `a-kit-declares-its-toolchain-and-tests`, open, adds its toolchain requirement to `test-suite`.

## Risks / Trade-offs

- A warm entry still costs about a third of a second per wrapped command; the gate and the runners pay it once a run.
- An agent that forgets the wrap runs no moon at all once swancloud takes `~/.bun/bin` off its path; until then it may run the host's moon 1.41.7, which cannot run crew's suite and fails loudly.
