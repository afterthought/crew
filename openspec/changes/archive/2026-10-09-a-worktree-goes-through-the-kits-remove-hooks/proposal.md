# Proposal

## Why

When a unit's or fix's work has merged, or a bolt has landed, crew removes its worktree with plain git. That skips everything the kit's own worktree tool would have run on the way out. switchboard-kit tears down each worktree's ministack and its integration deployment's objects at Frontegg Development in a remove hook, so on 2026-10-09 three of swb-3's fix worktrees went and left all of that standing (signal `2026-10-09-swb-3-ops-401c8aa3/01`). The rule is already amended (`plan.9`); the code still runs `git worktree remove --force` (`_open.md`).

## What Changes

- **Every worktree crew removes goes through the kit's own worktree tool**, `wt remove`, run from the kit's main checkout, so the kit's remove hooks run: the ones before removal with the worktree's files still there, the ones after it once it is gone. A kit with no remove hooks, such as crew's own or swancloud's, sees no difference.
- **A remove hook that fails keeps the worktree, and its branch.** crew names the worktree and the line in which the tool says what failed, on every read of the team, and the first read after the cause is fixed removes it. The tool's own hints to skip the hooks are never passed on.
- **Hooks the user has not approved on that host keep the worktree too.** The kit's hooks run only once the user has approved them on that host, as for its merge hooks; until then crew names the worktree as kept and says that the approval is the user's. crew never approves them itself and never skips them.
- **The branch stays or goes by crew's own judgment, never the tool's.** crew tells the tool to leave the branch alone, then decides it as it does today, which `a-drop-keeps-unmerged-work` turns into `plan.10`'s judgment. Its message about the branch is unchanged.
- **Everything else about when a worktree goes is unchanged**: which worktrees are crew's, what counts as finished, and that uncommitted changes, a lock or an unreadable plan keep one.
- The conductor's and main-level ops' briefs, the README and `crew status`'s usage say this, and the rule's open item goes.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `bolt-teams`: a worktree crew removes goes through the kit's remove hooks, and a failed or unapproved hook keeps it, named.

## Impact

- `plugin/lib/plan.py`: `tidy`, its one removal (`git worktree remove --force`), becomes a `wt remove` run and the reading of what it said.
- `plugin/roles/conductor.md`, `plugin/roles/main-ops.md`, `README.md`, the `crew status` line of `plugin/bin/crew`'s usage header, `docs/architecture/plan.md` (the `plan.9` details' open note), `docs/architecture/_open.md`.
- Tests: `tests/t-tidy.sh` gains the hook cases; the tests whose worktrees go by the tidy (`t-merge`, `t-fix`, `t-bolt`, `t-unit`, `t-unit-free`) now run the real `wt` on kits with no remove hooks.
- Every host crew tidies on needs `wt` on the path its forwarded commands run with; it already does for merges.

## Touches

`plugin/lib/plan.py` (`tidy`, which `a-drop-keeps-unmerged-work` also edits), `plugin/roles/conductor.md`, `plugin/roles/main-ops.md`, `plugin/bin/crew` (usage header only), `README.md` (the Teams paragraph), `docs/architecture/plan.md`, `docs/architecture/_open.md`, `openspec/specs/bolt-teams/spec.md` (by delta), `tests/t-tidy.sh`.
