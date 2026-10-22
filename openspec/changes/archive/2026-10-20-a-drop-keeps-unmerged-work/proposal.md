# A drop keeps unmerged work

## Why

Dropping a unit deletes its branch even when the branch holds work nothing else has. Applying proposal 16, crew deleted `unit/srv-tunnels-to-each-publishing-host` with its written change unmerged, though the proposal the user approved said the change was "kept on its branch"; the conductor recreated it by hand (signal `2026-10-07-swancloud-planner-b1ae7de3/01-unit-drop-deletes-unmerged-branch`). It happened again on 2026-10-20: edits the user chose to keep on `unit/curate-into-agenda` were deleted with the branch once its bolt had been dropped (`plan.10` details). Committed work gets less protection than uncommitted work, which already keeps its worktree. Record 0003 decided that a drop keeps a branch holding work the bolt does not.

## What Changes

- When crew removes a unit's or a chore's place, at a drop (`crew unit drop`, `crew chore drop`, `crew bolt drop` for each unit and chore it removes), at `crew unit free`, at the team's read after a merge or a landing, it removes the branch only when the branch holds nothing whose change its bolt lacks, compared by `git cherry` (each commit's patch), never by which commits are ancestors, since a unit's commits are rebased as they merge. When the bolt's branch is gone, the branch is compared with the kit's main as crew reads it now. When git cannot compare them, the branch is kept.
- A branch kept this way is named in what the command prints: the branch, the commit it is at, how many commits it holds whose change the bolt (or main) lacks, and that it is the user's to keep or delete.
- The run record gets one entry for each branch crew keeps, naming the branch, the commit it is at and how many commits it holds of its own. A dropped fix's kept branch gets the same entry.
- A unit or chore added later under the kept branch's name starts from it: its place is made on the kept branch, which then tracks the new unit's bolt, and the stage that made the place says so.
- The README and the planner's role say the same. The `plan.10` details and `_open.md`, which say unit and chore branches are still deleted outright, are the design agent's to amend once this lands (`docs.7`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: "Work happens in fixed places" (a unit or chore whose name has a kept branch is built on it) and "A worktree goes when its work is over" (a unit's or chore's branch is kept when it holds work its bolt or main lacks, named and recorded).

## Impact

- `plugin/lib/plan.py`: `tidy`, `fix_branch_kept` and `fix_branch_gone` become one judgment and one act for every branch a tidy removes; `PLACE` and `make_place` take a kept branch and track the new bolt.
- `plugin/lib/record.py`: a new act, `branch.kept`.
- Tests: `tests/py/test_tidy.py`, `tests/py/test_fix.py`, `tests/contract/test_git.py`, and the journeys whose units' branches hold commits when they are dropped or freed (`tests/t-journey-fix.sh`, `tests/t-journey-land.sh`, `tests/t-journey-plan.sh`).
- Docs: `README.md`, `plugin/roles/planner.md`.

## Touches

```
plugin/lib/plan.py
plugin/lib/record.py
plugin/roles/planner.md
README.md
tests/py/**
tests/contract/**
tests/t-*.sh
tests/moon.yml
```
