# Proposal

## Why

Every merge in crew now waits about twenty minutes for its gate, because crew's tests run one after another, and the bolt's verification after the merge runs the same twenty minutes again on a tree the gate has just passed. While they work, agents run that whole suite by hand too, since CLAUDE.md tells them to run `tests/run`. Record 0008 decides the second half of the testing strategy: the suite runs as one moon task per test file, in parallel, a test whose inputs already passed is replayed rather than run again, and the user asked that a coder or verify run only the tests its change affects, leaving the whole suite to the merge gate.

## What Changes

- crew's tests run as moon tasks, one per test file, side by side. One command, `tests/suite`, runs them all, or the ones named, or only those a change affects, and prints a line for each test, a summary, and the output of each failure, as `tests/run` does today; every test runs even when one fails.
- A test whose inputs are identical to a run that already passed on the same host, in any worktree or stage, is replayed from moon's cache in a moment instead of run again. So the merge gate replays what the coder already ran when the bolt hasn't moved, the bolt's verification replays what the gate passed, and an edit to one test file reruns only that test. A change to `plugin/` still reruns every test, since every command goes through `plan.py`.
- The tasks are generated from `tests/t-*.sh` by a script. The suite refuses to run when a test has no task, or when a test reads a file of crew's that its task doesn't list as an input, so a stale replay can't hide a change. The live test is not a task.
- The merge gate and the bolt's verification run `tests/suite` in place of `tests/run`. The verification's frozen copy of the bolt's head becomes a one-commit git repository, because moon caches nothing in a directory that isn't one.
- The tests are proven not to collide when run at once: one full parallel run and one serial run, both green, and any test that fails only in parallel is fixed.
- CLAUDE.md, and the coder's, verify's and construct's briefs, say an agent runs only the tests its change affects (`tests/suite --affected`, or tests it names), never the whole suite by hand: that is the merge gate's.
- moon joins crew's devenv, and its task archives are shared by every worktree through the git common dir. `code.1` is amended to allow it, as record 0008 decides.

## Capabilities

### New Capabilities

- `test-suite`: how crew's own tests are run: as parallel moon tasks replayed on an identical tree, kept in step with the test files, and which of them an agent runs while it works.

### Modified Capabilities

None. The `merge-gate` capability (from `a-merge-is-gated-by-the-suite`, not yet archived into `openspec/specs/`) still holds as written: its gate and verification run the whole suite through `tests/run`, now one test per task.

## Impact

- New: `.moon/workspace.yml`, `tests/moon.yml` (generated), `tests/moon-tasks` (the generator and its check), `tests/suite`, `tests/t-suite.sh`.
- `devenv.nix` gains moon, the shared-archive link and `MOON_TOOLCHAIN_FORCE_GLOBALS`; `.gitignore` gains `.moon/cache/`.
- `.config/wt.toml` (the gate's command) and `.config/hooks/bolt-verify.sh` (the copy and the command it runs); `tests/t-merge-gate.sh` follows them.
- The tests that read files outside the common inputs say so in their opening comment; any test that collides in parallel is fixed.
- `CLAUDE.md`, `README.md`, `plugin/roles/coder.md`, `verify.md`, `construct.md`, `tests/t-briefs.sh`; `docs/architecture/core.md` (`code.1`), `tests.md` (`tests.5`), `_open.md`.
- Every host that merges in crew needs the user's `wt config approvals add` again, since the gate's command changes; until then a merge there stops and asks.
- Each host's first shell after this lands waits for devenv to evaluate again (about twenty seconds).

## Touches

`.moon/` (new), `tests/moon.yml` (new), `tests/moon-tasks` (new), `tests/suite` (new), `tests/t-suite.sh` (new), `tests/t-merge-gate.sh`, `tests/t-briefs.sh`, the opening comments of `tests/t-dev-shell.sh`, `tests/t-docs.sh`, `tests/t-merge-gate.sh` and `tests/t-sites.sh`, any other `tests/t-*.sh` found to collide in parallel, `devenv.nix`, `.gitignore`, `.config/wt.toml`, `.config/hooks/bolt-verify.sh`, `CLAUDE.md`, `README.md`, `plugin/roles/coder.md`, `plugin/roles/verify.md`, `plugin/roles/construct.md`, `docs/architecture/core.md`, `docs/architecture/tests.md`, `docs/architecture/_open.md`, and `openspec/specs/test-suite/spec.md` (new, by delta). Every merge in crew, this unit's own included, runs the gate this change edits.
