# A kit's toolchain makes its worktrees ready

## Why

When crew makes a bolt's, unit's or fix's worktree it runs `crew-prepare` from the kit's main checkout's devenv profile: crew reaches into another repository's profile for a script named after crew, which the user called bad design. And only crew's and swancloud's sessions enter their devenv shell, each through its own copy of a repository hook, so crew's agents in every other kit run the host's tools unless they wrap each command in `devenv shell --`. sluice has settled how a repository's tools are split and set up (devenv the system tools, proto through moon the application toolchain, one entry for every launcher), and asks crew for the agent's name in `SLUICE_AGENT` and for a bolt's worktree that does not go stale when sluice moves its branch. Record 0023 decides how crew follows.

## What Changes

- **A new worktree is made ready by the kit's own toolchain.** crew runs `moon setup` in the worktree's devenv shell, on the team's host, when the worktree holds `devenv.nix` and `.moon/workspace.yml`; moon installs what `.prototools` pins, and installs dependencies before the first task that needs them. A kit without both gets nothing from crew. `crew-prepare` is no longer run. **BREAKING** for switchboard-kit, the one kit with a `crew-prepare`: its `bun install` moves into moon's JavaScript toolchain config.
- **Every session in a checkout with a devenv works inside its shell, through crew's plugin.** The SessionStart hook crew's repository carries moves into the plugin, its words any kit's: a session whose checkout has `devenv.nix` at its root enters that shell at every start. crew's agents in every kit and the user's own sessions get the kit's tools from their first command. crew's repository copy goes; swancloud drops its own in its repository.
- **crew's shell runs moon 2.6 and the Python crew runs on.** moon 2.6.1 from moonrepo's release (built), Python pinned to the fleet's 3.13 with pytest, and `MOON_TOOLCHAIN_FORCE_GLOBALS` gone.
- **Every agent crew starts carries `SLUICE_AGENT`**, its crew name (built).
- **A bolt's worktree follows its branch in a kit that merges through sluice**: when a unit's merge stage ends, and before a proof, crew brings the bolt's worktree level with the branch sluice moved.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: "Work happens in fixed places" makes each worktree ready by the kit's toolchain; two requirements are added, the agent's name for sluice and the bolt's worktree following its branch in a kit on sluice.
- `dev-shell`: a session works inside its own checkout's devenv shell, any kit's, entered by crew's plugin; crew's shell runs moon 2.6 and the fleet's Python.

## Impact

- `plugin/lib/plan.py` (`PLACE`, `make_place`, the merge stage's end, `crew prove`), `plugin/hooks/` (a new hook, `hooks.json`), `plugin/bin/crew-role` (built), `devenv.nix`, `tests/suite`, `.claude/` (removed), the tests named in the tasks, README, CLAUDE.md, `plugin/roles/conductor.md` and `ops.md` for the levelled worktree.
- Every Claude session on a host with crew's plugin, in a checkout with `devenv.nix`, waits for its shell at its start.
- switchboard-kit and swancloud each change in their own repository: switchboard moves its install into moon and drops `crew-prepare`; swancloud drops its repository hook.
- No worktree holding a bolt's branch, record 0023's sixth point, is its own change once the user accepts it.

## Touches

```
devenv.nix
.claude/settings.json            (removed)
.claude/hooks/devenv-shell       (moved to plugin/hooks/devenv-shell)
plugin/hooks/devenv-shell
plugin/hooks/hooks.json
plugin/hooks/session-start       (built)
plugin/bin/crew-role             (built)
plugin/lib/plan.py
plugin/roles/conductor.md
plugin/roles/ops.md
tests/suite
tests/units.sh
tests/stubs/claude               (built)
tests/t-dev-shell.sh
tests/t-journey-units.sh
tests/t-sluice.sh
tests/t-roles.sh                 (built)
tests/t-session-hook.sh          (built)
tests/t-briefs.sh
tests/py/
tests/moon.yml
README.md
CLAUDE.md
```
