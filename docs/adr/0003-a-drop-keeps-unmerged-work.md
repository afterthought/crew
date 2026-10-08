---
number: 3
title: A drop keeps unmerged work
status: accepted
date: 2026-10-07
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# A drop keeps unmerged work

Date: 2026-10-07; extended to landing the same day.
Deciders: swancloud-design, on swc-1-conductor's finding (signal `2026-10-07-swancloud-planner-b1ae7de3/01-unit-drop-deletes-unmerged-branch`).
Sources: `openspec/specs/bolt-teams/spec.md` ("Units run in slots"), `README.md` (a unit dropped from the plan), `plugin/lib/plan.py` (`unit drop`); proposal 16 on `swancloud/main`.

## Context and problem statement

`crew unit drop` frees the unit's slot and removes its worktree and branch at once, unless its stage is still working or its worktree has uncommitted changes. Applying proposal 16, which re-planned `srv-tunnels-to-each-publishing-host` under another name and said "its change kept on its branch", crew deleted the branch with its constructed change unmerged; the conductor recreated it by hand. Committed work got less protection than uncommitted work.

Should a drop keep a branch that holds work the bolt does not?

## Decision drivers

- Nothing a person or an agent committed is lost by a plan write: the plan holds intent, and a drop is a change of intent, not of the kit.
- Branches that hold nothing are noise; `crew bolts` and gather read `unit/*` and `fix/*` branches.
- The user approves a proposal from its words; "kept on its branch" has to be true when they read it.

## Considered options

1. A drop removes the worktree and the slot, and keeps the branch when it holds commits the bolt does not; a branch with nothing beyond the bolt's tip is removed.
2. A drop keeps every branch.
3. A drop removes every branch, as today, and refuses when the branch holds unmerged commits, as it refuses uncommitted changes.

## Decision outcome

Option 1. `crew unit drop`, `crew bolt drop` for each unit it removes, and `crew unit free` remove the worktree and free the slot as they do today, and remove the branch only when it holds no commit the bolt does not. A branch with unmerged commits is kept, and the command says so, naming the branch and how many commits it holds beyond the bolt; the run-record entry carries the branch as an object it left. Whether the bolt, or main, "holds" a commit is judged by its patch, not its ancestry (`git cherry`): a unit's merge into its bolt and a bolt's landing on main both rebase, so a merged commit's hash is not on the branch it merged into, while its patch is. A commit whose patch changed on the way, in a conflict resolved during the rebase, reads as unmerged, and its branch is kept: the safe side (crw-1's conductor, 2026-10-07, signal `2026-10-07-swancloud-planner-c9179e59/01-kept-branches-compared-by-patch`).

A kept branch is the user's: to delete, or to build from again, and a unit added later under the kept branch's name starts from that branch rather than a fresh one. `crew bolts` does not list kept branches; `git branch --list 'unit/*'` in the kit does.

A bolt drop sweeps its team's host as `unit drop` does, and that is built (b09f8d0, 82734e4, in worktrees-go-with-their-work): each unit's worktree is removed and its slot freed, and this record's rule for branches applies to each, so a branch with unmerged commits is kept and named. On 2026-10-07 the user dropped a proposal that would have re-stated this as new work ("seems like a waste; we just do that manual cleanup"); the sweep itself was already in the code, and only the keeping of unmerged branches is still to build, in `a-drop-keeps-unmerged-work`. With `--requeue`, each unit keeps its branch, since its work is still planned, and loses its worktree and slot; a unit still working, or with uncommitted changes, is left for `crew unit free`.

The same rule holds at landing (2026-10-07, on ops's finding that `bolt/tunnels-keep-the-reach` and `places/fix-bolt-onto-main` were left after the bolt landed). `crew bolt land` sweeps what the bolt's work left in the kit that main now holds: the bolt's worktree and branch, and each merged unit's and fix's place and branch. A fix or unit branch with commits main does not hold keeps its branch, its worktree removed, and the command names it. After a landing, the kit holds nothing of the bolt but what main does not.

### Consequences

- The `bolt-teams` spec's slot requirement and the README's sentence on a dropped unit are amended by the change that builds this.
- Proposal 16's words become true for the next such drop; the branch recreated by hand on 2026-10-07 stands.

## Pros and cons of the options

### Option 1: keep what is unmerged

- Good: no committed work is lost; nothing kept that holds nothing; the proposal's words hold.
- Bad: a kept branch can be forgotten; it is visible only in git.

### Option 2: keep every branch

- Good: simplest rule.
- Bad: empty `unit/*` branches accumulate and gather reads them.

### Option 3: refuse the drop

- Good: nothing is ever kept behind the user's back.
- Bad: a drop the user approved in a proposal fails at the end, after the plan has been read as approved; dropping would need a force flag, and forcing is where work is lost.
