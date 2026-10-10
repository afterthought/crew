# Proposal

## Why

Worktrees crew makes stay behind after the work they were made for is over (signal `2026-10-06-swancloud-planner-dc4c1137/02-worktrees-outlive-their-work`). On wldn's box, two are still in switchboard-kit's checkout:

- `bolts/one-cfn-lint-pass`. The dispatcher gave that bolt to swb-2 at 22:25:55Z on 2026-10-05, which made the worktree. The planner dropped it three minutes later. **Dropping a bolt never touches the team's host.** It changes the plan and nothing else, so the bolt's worktree, its branch and any slots of the team stay.
- `places/the-real-deploy-finishes-in-the-local-world`. Its unit merged into its bolt at 02:51:30Z on 2026-10-06, and its slot was freed at 02:52:14Z. So crew did try to remove the worktree, and git refused. **crew gives up after one try.** When git refuses, crew prints "was kept: it has changes of its own" once, to whoever read the team. Nothing holds the place any more, so nothing ever tries again.

Two more gaps let the same thing happen:

- **Landing a bolt can fail halfway.** When git refuses to remove the bolt's worktree, `crew bolt land` fails after it has already taken the bolt out of the plan. The worktree stays, and nothing comes back for it.
- **Requeuing a bolt leaves units in a state crew forbids.** `crew bolt drop --requeue` puts a unit that has a worktree into the queue, but `crew unit move` refuses that, because a queued unit has no worktree.

The user's rule: dropping a bolt or merging a unit removes its worktree, unless the worktree holds uncommitted changes.

## What Changes

- **Every worktree crew made goes when its work is over.** This covers:
  - a bolt's worktree, once the plan no longer has the bolt (landed or dropped);
  - a unit's, once it has merged into its bolt or landed, or the plan no longer has it;
  - a fix's, once it has merged into its bolt, or the plan no longer has its bolt.

  Each goes with its branch. When the branch holds commits that neither main nor its bolt has, crew says the commit it was at, so the work can be got back.
- **One rule, checked every time crew reads a team.** `crew status <team>`, `crew unit run` and `crew fix` already free a merged unit's slot. They now also remove every leftover worktree in the team's kit checkout, whatever left it there. That covers worktrees from before this change too, including the two on the box.
- **Removal happens at once.** `crew bolt drop`, `crew unit drop` and `crew bolt land` apply the same rule on the team's host right after they change the plan. When that host doesn't answer, the team's next read does it.
- **Uncommitted changes keep a worktree, and crew keeps saying so.** A worktree with modified files, or with untracked files that git doesn't ignore, is kept with its branch. Every read of the team names it as the user's to keep or discard, until it is clean (then crew removes it) or gone. Ignored files, such as installed dependencies and `.devenv`, never keep a worktree. Landing a bolt whose worktree is kept still lands.
- **Slots whose work the plan no longer has are freed by themselves.** A unit dropped while its stage agent was working, or a fix whose bolt was dropped, is freed by the next read of its team once its agent settles, the same way a merged unit's slot is. `crew unit free` still works for the user.
- **crew touches only its own worktrees.** It removes only worktrees directly under `<kit>/bolts/` or `<kit>/places/` that are on a branch crew names (`bolt/`, `unit/` or `fix/`). It never removes the main checkout, a worktree made by hand, a detached one (a merge stopped partway through its rebase), or a locked one. It removes nothing when it can't read every plan the kit's work goes in.
- **`crew bolt drop --requeue` refuses a unit that has a worktree**, in the same words `crew unit move` uses: a queued unit has none. The planner first drops that unit, or moves it to another bolt in the same checkout.
- The conductor's, main-level ops' and planner's briefs, the README and the usage text say all of this.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `bolt-teams`: when a slot is freed, when a worktree crew made is removed, what keeps one, and that a landing finishes even when the bolt's worktree is kept.
- `bolt-plan`: dropping a bolt removes its worktrees, and `--requeue` refuses a unit that has a worktree.

## Impact

- `plugin/bin/crew`: `reap` (it frees dropped work as well as merged work, then removes leftovers), a new hidden `_tidy <team>`, `remove_place`, `remove_dropped` and `_free --remove` (all replaced by the one rule), `unit_free`, and the usage header.
- `plugin/lib/plan.py`: a `_tidy` subcommand (the leftover rule), `slot_stages` (a `dropped` stage), `op_bolt_drop` (the requeue refusal and its after-step), `op_unit_drop`'s after-step, `bolt_land` (the `DROP_BOLT` script goes), and the usage lines for `bolt drop` and `bolt land`.
- `plugin/roles/conductor.md`, `plugin/roles/main-ops.md`, `plugin/roles/planner.md`, `README.md`.
- Tests: `tests/t-bolt.sh`, `tests/t-merge.sh`, `tests/t-unit.sh`, `tests/t-unit-free.sh`, `tests/t-fix.sh`, and a new `tests/t-tidy.sh`.

## Touches

`plugin/bin/crew`, `plugin/lib/plan.py`, `plugin/roles/conductor.md`, `plugin/roles/main-ops.md`, `plugin/roles/planner.md`, `README.md`, `openspec/specs/bolt-teams/spec.md` (by delta), `openspec/specs/bolt-plan/spec.md` (by delta), `tests/t-bolt.sh`, `tests/t-merge.sh`, `tests/t-unit.sh`, `tests/t-unit-free.sh`, `tests/t-fix.sh`, `tests/t-tidy.sh` (new).
