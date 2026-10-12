# Tasks

## 1. crew's shell

- [x] 1.1 crew's devenv carries moon 2.6.1 from moonrepo's release for each platform, hashes pinned, as sluice's does, and `tests/suite t-suite t-merge-gate logic contract` ends with "0 failed" (dc1e6ce; `code.1`, `tests.5`).
- [ ] 1.2 crew's devenv carries Python 3.13 with pytest and no `MOON_TOOLCHAIN_FORCE_GLOBALS`, `tests/suite` keeps only `MOON_CONCURRENCY` from the caller's `MOON_*`, and `tests/suite --affected` ends with "0 failed" (design: *crew's shell*; Task notes 1.2; `code.1`).

## 2. A new worktree is made ready by its kit's toolchain

- [ ] 2.1 `setup_of` decides from whether a worktree holds `devenv.nix` and `.moon/workspace.yml`, with its logic cases, and `tests/suite logic` ends with "0 failed" (design: *A new worktree is set up by moon in its own shell*; Task notes 2.1; `code.7`, `tests.11`).
- [ ] 2.2 `make_place` runs `devenv shell -- moon setup` in the worktree when `setup_of` says so, on new and existing worktrees, refusing in the tool's words when it fails, and runs no `crew-prepare`; `t-journey-units` shows the setup after give and construct, none for a kit without the files, and a failed setup refused and set up on a second run, and `tests/suite journey-units journey-plan` ends with "0 failed" (Task notes 2.2; `read.1`, `teams.9`, `tests.4`).

## 3. Every session enters its checkout's shell through crew's plugin

- [ ] 3.1 The SessionStart hook is `plugin/hooks/devenv-shell`, run by the plugin's `hooks.json`, entering the shell of the checkout holding the project directory when it has `devenv.nix` and leaving every other session and a subagent's alone; `.claude/settings.json` and `.claude/hooks/` are gone; `t-dev-shell` proves each case, and `tests/suite dev-shell session-hook` ends with "0 failed" (design: *The session's shell is entered by crew's plugin*; Task notes 3.1; `tests.4`, `tests.10`).
- [ ] 3.2 CLAUDE.md and README say the shell is entered by crew's plugin in every checkout with a `devenv.nix`, and `tests/suite --affected` ends with "0 failed" (Task notes 3.2; `docs.2`).

## 4. What sluice asks of crew

- [x] 4.1 Every agent crew starts carries `SLUICE_AGENT`, the same as `CREW_AGENT`, at its start and on a herdr resume, `teams.6` says so, and `tests/suite roles session-hook` ends with "0 failed" (4bdc6d0; `teams.6`, `tests.4`).
- [ ] 4.2 In a kit that merges through sluice, crew brings the bolt's worktree level with its branch after a merge stage delivers and before a proof, by `levelling` and `git read-tree -m -u`, refusing and telling the conductor when it can't; the logic, contract and `t-sluice` cases and the briefs' phrase pass, and `tests/suite --affected` ends with "0 failed" (design: *A bolt's worktree follows its branch in a kit on sluice*; Task notes 4.2; `code.6`, `code.7`, `roles.3`, `teams.5`, `tests.6`).
