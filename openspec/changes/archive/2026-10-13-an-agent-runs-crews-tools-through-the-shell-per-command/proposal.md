# An agent runs crew's tools through the shell per command

## Why

Record 0024: no session is entered into a kit's shell at its start; an agent runs a kit's application tools through the kit's shell per command, `devenv shell -- <command>`, as the kit's CLAUDE.md names; the kit's own entry points enter the shell themselves; and the host is the container, carrying no application tool on an agent's path. crew still enters every session in a crew checkout into its devenv shell through a SessionStart hook the checkout commits, and its test runners refuse to start outside the shell rather than entering it. With the wrap per command, every entry pays what entering costs, and crew's entry runs `proto install` on each one: 2.8 of a warm entry's 3.2 seconds.

## What Changes

- **crew's session hook goes**: `.claude/hooks/devenv-shell`, its entry in `.claude/settings.json`, `tests/t-dev-shell.sh` and the `dev-shell` spec. No session in a crew checkout is entered into crew's shell at its start (`tests.7`).
- **`tests/suite` and `tests/run` enter crew's shell themselves** when started outside it (`DEVENV_ROOT` unset), running themselves again under `devenv shell --` from their own checkout, rather than refusing (`tests.1`).
- **CLAUDE.md's Tests section names the per-command form**, `devenv shell -- <command>`, and no longer says that no agent wraps; README says the runners enter the shell themselves; no brief or skill names the wrap.
- **crew's shell installs proto's pins only when one is missing** from crew's proto home, so a warm entry costs 0.36 seconds rather than 3.2.
- **What `t-dev-shell` checked that still holds moves**: CLAUDE.md naming the wrap, briefs and skills not, the `.envrc` and `.gitignore` to `t-docs`; crew's moon and Python to the contract tier's `test_toolchain.py`; the runners entering the shell to a new `t-runner`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `dev-shell`: every requirement is removed; the spec goes.
- `test-suite`: requirements are added for the runners entering crew's shell themselves, for running crew's tools through it per command, and for a worktree that stays clean of the shell's working files.

## Impact

- `.claude/`, `tests/run`, `tests/suite`, `devenv.nix`, CLAUDE.md, README, `tests/t-docs.sh`, a new `tests/t-runner.sh` and `tests/contract/test_toolchain.py`, `tests/moon.yml`; `tests.1` and `tests.7` lose their not-built clauses and `_open.md` keeps only swancloud's half.
- `a-kit-declares-its-toolchain-and-tests`, open, puts its toolchain requirement on `test-suite`, since `dev-shell` goes (`docs.3`).
- swancloud's half, its generated SessionStart hook and `~/.bun/bin` on an agent's path, is swancloud's own unit.
- An agent in a crew checkout started before this lands keeps the shell its hook gave it until its next start.

## Touches

```
.claude/hooks/devenv-shell
.claude/settings.json
devenv.nix
tests/run
tests/suite
tests/t-dev-shell.sh
tests/t-docs.sh
tests/t-runner.sh
tests/contract/test_toolchain.py
tests/moon.yml
CLAUDE.md
README.md
openspec/specs/dev-shell/spec.md
openspec/changes/a-kit-declares-its-toolchain-and-tests/
```
