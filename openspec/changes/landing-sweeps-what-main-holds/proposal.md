# A landing sweeps what main holds

## Why

After a bolt lands, crew can delete work main never received, and can leave behind work main already holds. The bolt's branch is deleted once no plan has the bolt, whatever it holds; a unit's, chore's or fix's branch is compared with the bolt rather than with main, so work that reached the bolt after its landing was formed is deleted with it (signal `2026-10-07-swancloud-planner-a46c6cb9/01-landing-leaves-bolt-branch-and-fix-worktree`, where `bolt/tunnels-keep-the-reach` and `places/fix-bolt-onto-main` stood redundant after the landing). Record 0003 decided that a landing sweeps everything of the bolt's work that main holds, and keeps, named, only what main lacks.

## What Changes

- The landing's submission marks the bolt's branch as landed in the kit's git config, on the team's host, once sluice has landed it, so every later read of the team knows the bolt landed, whether or not its host answered `crew bolt land`.
- Once its bolt has landed, a unit's, chore's or fix's branch is compared with the kit's main as crew reads it now, never with the bolt, by `git cherry` (each commit's patch), never by which commits are ancestors. Its branch goes with its place when main holds every commit's patch, and is kept and named, the user's to keep or delete, when it holds a commit main lacks. A fix whose bolt's branch is gone is compared with main as a unit's is.
- A landed bolt's branch goes only when `git cherry` finds no commit on it whose patch main lacks; otherwise it is kept and named with the commit it is at and how many commits main lacks, crew's mark taken off so it is the user's, and one run-record entry names it.
- `crew bolt land` prints each of these lines, from the tidy it asks of the team's host: what went, and each branch kept with why. Once it has run, the kit holds nothing of the bolt's work but branches holding work main lacks, and worktrees kept for uncommitted changes or a failed remove hook, as today.
- README's sentence on worktrees going and main-level ops's landing step say the same.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: "A worktree goes when its work is over" (once a bolt has landed, its work's branches and its own branch are judged against main) and a new requirement, "A landing leaves only what main lacks".

## Impact

- `plugin/lib/plan.py`: `LANDING` sets the landed mark; the tidy reads it and judges a landed bolt's work and its branch against main through the judgment `a-drop-keeps-unmerged-work` builds (`branch_target`, `branch_kept`, `branch_gone`), and `bolt_branch_over` gives way to that judgment for a landed bolt.
- Tests: `tests/py/test_tidy.py`, `tests/py/test_landing.py`, `tests/contract/test_git.py`, `tests/t-journey-land.sh`, and `tests/t-briefs.sh` if it pins main-ops's landing words.
- Docs: `README.md`, `plugin/roles/main-ops.md`.

## Touches

```
plugin/lib/plan.py
plugin/roles/main-ops.md
README.md
tests/py/**
tests/contract/**
tests/t-journey-land.sh
tests/t-briefs.sh
tests/moon.yml
```
