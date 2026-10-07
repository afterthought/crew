# A drop keeps unmerged work

- Status: accepted
- Date: 2026-10-07
- Deciders: swancloud-design, on swc-1-conductor's finding (signal `2026-10-07-swancloud-planner-b1ae7de3/01-unit-drop-deletes-unmerged-branch`)
- Sources: `openspec/specs/bolt-teams/spec.md` ("Units run in slots"), `README.md` (a unit dropped from the plan), `plugin/lib/plan.py` (`unit drop`); proposal 16 on `swancloud/main`

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

Option 1. `crew unit drop`, `crew bolt drop` for each unit it removes, and `crew unit free` remove the worktree and free the slot as they do today, and remove the branch only when it holds no commit the bolt does not. A branch with unmerged commits is kept, and the command says so, naming the branch and how many commits it holds beyond the bolt; the run-record entry carries the branch as an object it left. A kept branch is the user's: to delete, or to build from again, and a unit added later under the kept branch's name starts from that branch rather than a fresh one. `crew bolts` does not list kept branches; `git branch --list 'unit/*'` in the kit does.

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
