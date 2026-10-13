# A kit declares its toolchain and tests

## Why

When crew makes a bolt's, unit's or fix's worktree it runs `crew-prepare` from the kit's main checkout's devenv profile: crew reaches into another repository's profile for a script named after crew, which the user called bad design. sluice has settled how a repository says its tools are set up and its checks run: a `[tests]` table in its policy, `.config/sluice.toml`, whose `toolchain` command prints the kit's toolchain and whose `runner` sets up and runs the checks. The user ruled that crew should not assume moon or devenv, and should have the same toolchain and test adapters as sluice, so that flywheel, using sluice's SDK, can later take over crew's steps on the same declaration (record 0023). The file is sluice's for now and becomes `flywheel.toml` when flywheel has it.

## What Changes

- **A kit declares its toolchain and test runner in `.config/sluice.toml`**, with sluice's keys, and crew reads them from the worktree in hand, in one place (`kit.py`'s `DECLARATION`), so the file's rename to `flywheel.toml` is one edit. A kit that declares nothing gets nothing from crew.
- **crew gains a toolchain adapter and a test adapter**, a port of sluice's: the toolchain command runs in the worktree with a cleaned environment and its printed script is kept outside the tree; the moon runner's setup runs `moon setup` inside it, refusing a moon below 2.6; any later command crew runs there sources the script with the `bash` on PATH.
- **A new worktree is made ready by the declaration**: the toolchain step, then the runner's setup, on the team's host, before any agent starts, and again when crew finds the worktree already made. `crew-prepare` is no longer run. **BREAKING** for switchboard-kit, the one kit with a `crew-prepare`; it keeps working, since each of its suite scripts runs `bun install --frozen-lockfile` before it starts, until it writes its declaration and moves its install into its moon config.
- **crew's own toolchain is proto's**: devenv carries proto, jq and recutils; `.prototools` pins moon 2.6.1, Python 3.13.15 (the hosts' minor) and uv; moon's Python toolchain syncs pytest from `tests/pyproject.toml` into `tests/.venv`; crew declares its own toolchain and runner like any kit; its test tasks are tagged `check-full`, beside sluice's `check-fast`, in place of `suite`.
- **Every agent crew starts carries `SLUICE_AGENT`**, its crew name (built).

## Capabilities

### New Capabilities

- `kit-toolchain`: how a kit declares its toolchain and test runner, and how crew's adapters set a worktree up and run commands in it from that declaration.

### Modified Capabilities

- `bolt-teams`: "Work happens in fixed places" makes each worktree ready through its kit's declaration and runs no kit script; a requirement is added for the agent's name for sluice.
- `test-suite`: a requirement is added for crew's own toolchain, which the suite runs on: devenv's system tools, and proto's pins of moon, Python and uv.

## Impact

- `plugin/lib/` (a new module for the adapters; `plan.py`'s `PLACE` and `make_place`), `devenv.nix`, `.prototools`, `.moon/toolchains.yml`, `.config/sluice.toml`, `tests/pyproject.toml`, `tests/uv.lock`, `.gitignore`, `tests/suite`, `tests/moon-tasks` and `tests/moon.yml`, the tests named in the tasks, README and CLAUDE.md.
- switchboard-kit changes in its own repository before this lands on a host its teams use: its declaration, its bun pin in `.prototools`, its moon JavaScript config, and `crew-prepare` gone.
- A kit's agents still start on whatever the session gives them: how agents come to work inside their kit's toolchain is held for an elaboration (`openspec/explorations/agents-in-the-toolchain/reading.md`).
- A bolt's branch in a kit that merges through sluice is held for an elaboration (`openspec/explorations/bolt-branches-under-sluice/reading.md`); the test adapter's run and read wait on it.

## Touches

```
devenv.nix
.prototools
.moon/toolchains.yml
.config/sluice.toml
.gitignore
plugin/lib/kit.py
plugin/lib/plan.py
plugin/hooks/session-start       (built)
plugin/bin/crew-role             (built)
tests/pyproject.toml
tests/uv.lock
tests/suite
tests/moon-tasks
tests/moon.yml
tests/units.sh
tests/stubs/claude               (built)
tests/py/test_kit.py
tests/contract/test_kit.py
tests/t-journey-units.sh
tests/t-roles.sh                 (built)
tests/t-session-hook.sh          (built)
tests/t-suite.sh
tests/t-dev-shell.sh
plugin/bin/crew                  (usage header)
plugin/skills/crew/SKILL.md
docs/architecture/core.md
docs/architecture/plan.md
docs/architecture/tests.md
README.md
CLAUDE.md
```
