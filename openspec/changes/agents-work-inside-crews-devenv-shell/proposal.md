# Proposal

## Why

A crew agent working in a crew worktree today runs each command it needs crew's tools for wrapped in `devenv shell --`, because CLAUDE.md and the README tell it to (`devenv shell -- tests/run`). The user asked for the opposite: "the whole point is that the agent should be launched inside the shell" (signal `2026-10-08-swancloud-planner-0ca5793d/01-agents-run-inside-the-shell-and-only-affected-tests`). swancloud already works this way: a Claude session in any swancloud checkout enters that checkout's devenv shell at its start, so every command it runs has the shell's tools (swancloud's record 0003, "The shell", and its `.claude/hooks/devenv-shell`). crew should do the same.

## What Changes

- A Claude session that starts in a crew checkout (a unit's or fix's place, a bolt's worktree, crew's main) enters crew's devenv shell before its first command, and every command it runs after that, on start, resume, `/clear` or compaction, runs in that shell. The session sees nothing when this works.
- When the shell can't be entered, the session starts anyway, with one line saying it is not in crew's shell and why, so the agent says so rather than going on as if it were.
- A person who enters a crew worktree from a terminal with direnv enters the same shell, through a tracked `.envrc`.
- `tests/run` refuses to start outside a devenv shell and says how to enter one, so a test never runs with the host's tools in place of the shell's.
- CLAUDE.md, the README and the comments that tell an agent how to run the tests or the bolt's verification say to run them as they are (`tests/run`, `sh .config/hooks/bolt-verify.sh`), never wrapped in `devenv shell --`, and a test holds them to it.
- The rule goes into crew's testing rules, and the testing rules' runner rule says the runner refuses outside the shell.
- devenv's own working files in a worktree are ignored by crew's repository, so entering the shell never leaves a worktree looking changed.

What does not change: the merge gate and the bolt's verification hook in `.config/wt.toml` still enter the shell themselves, since worktrunk runs them for whoever merges and the user's approval is keyed to each command's exact text. Which tests an agent runs (only those its change affects) is the next unit's, `the-suite-runs-as-moon-tasks`. crew's devenv declares the same packages as before (`code.1`); the host's own tools (herdr, wt, openspec, git) stay on the shell's path after the shell's own.

## Capabilities

### New Capabilities

- `dev-shell`: how a Claude session, a person and the test runner in a crew checkout come to be inside crew's devenv shell, and what a session is told when it is not.

### Modified Capabilities

None.

## Impact

- New `.claude/settings.json` (committed) carrying a SessionStart hook, and the hook, `.claude/hooks/devenv-shell`, a standard-library Python script modelled on swancloud's.
- New tracked `.envrc`; `.gitignore` gains devenv's and direnv's working directories.
- `tests/run` gains one check; a new test, `tests/t-dev-shell.sh`, runs the hook against a stand-in devenv and checks the docs.
- `CLAUDE.md` (Tests; Proving and landing a bolt), `README.md`, the comments in `.config/wt.toml` and `.config/hooks/bolt-verify.sh`.
- `docs/architecture/tests.md` (a new rule, `tests.1` amended, its paths), and `core.md`'s table of pages.
- Every crew session's first start in a fresh worktree waits for devenv's first evaluation there (about 20 seconds cold, under a second warm, by `openspec/explorations/command-cost/reading.md`).

## Touches

`.claude/settings.json` (new), `.claude/hooks/devenv-shell` (new), `.envrc` (new), `.gitignore`, `tests/run`, `tests/t-dev-shell.sh` (new), `CLAUDE.md`, `README.md`, `.config/wt.toml` (comment only), `.config/hooks/bolt-verify.sh` (comment only), `docs/architecture/tests.md`, `docs/architecture/core.md`, and `openspec/specs/dev-shell/spec.md` (new, by delta). `CLAUDE.md`'s Tests section and `tests/run` are also edited by `the-suite-runs-as-moon-tasks`.
