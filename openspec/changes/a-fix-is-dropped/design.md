# Design

## Context

See proposal.md for why and record 0028 for the decision. `fix_run` reads the team (`reap`), then `fix_cmd` decides what `crew fix` acts on from the team's slots file: the slot holding the fix, else the branch and place a new fix of the bolt gets. A slot is freed by `Team.free`, which ends its agent through `Agents.stop`, refused on a working one unless forced. `tidy` removes each worktree crew made whose work is over (`tidy_over`) through the kit's `wt remove`, then deletes its branch with `git branch -D`; a bolt's branch crew made is marked `branch.bolt/<bolt>.crew` in the kit's git config and goes when no plan has the bolt.

Rules relied on: `teams.3` and `plan.9` as amended with record 0028, `plan.10` (a branch with patches its target lacks is kept, by `git cherry`), `teams.2` (a working agent is ended only when forced), `read.4` (crew takes over nothing it did not make), `record.1` (a refusal is recorded), `code.7`, `tests.4`, `tests.12`. Pages whose area this touches: `teams.md`, `plan.md`.

## Decisions

### The drop decides before the team's read, and reads it last

`fix_cmd` decides a drop as it does a merge, before anything changes: refused when the fix has merged into its bolt (`gather.fix_merged`), when no slot, place or branch holds it (`fix_drop_why`), or when its place is not the fix's own (`own_place`, saying crew drops a fix only in its own place); each refusal is recorded as `fix.drop`. A drop skips the read `fix_run` does first for a start or a merge, since that read would free a merged fix's slot and remove its branch, and the refusal must name the merge. `fix_drop` then frees the slot (a working agent refused without `--force`, the refusal recorded), marks the branch, records `fix.drop`, and runs the team's read (`reap`), whose tidy removes what the drop ended.

### A mark in the kit's git config says a fix was dropped

A dropped fix's place can be kept, holding uncommitted changes or refused by a remove hook, and every read must then name it and try again. The drop sets `branch.<fix>.crew dropped` in the kit's git config, as a bolt's branch is marked, which git drops with the branch. `fixes_dropped` reads the marks once per tidy; `tidy_over` counts a marked fix's work over.

### A dropped fix's branch is judged by git cherry

Once a dropped fix's place is removed, or when it had none, `fix_branch_gone` runs `git cherry <bolt> <fix>`: a `+` line is a commit whose patch the bolt lacks. With none the branch is deleted; with some, or when git cannot compare it with its bolt, it is kept, crew names it and the count, and the mark is unset, so the branch is the user's and is not named again. The decision is `fix_branch_kept`, a function of git cherry's exit and words. Every other branch tidy removes keeps its present deletion until `a-drop-keeps-unmerged-work` builds `plan.10` for all of them.

## Risks / Trade-offs

- A fix whose agent merged main into its place holds main's commits beyond the bolt, so its dropped branch is kept and named though the fix wrote nothing of its own; keeping work the user may want is the safer error.
