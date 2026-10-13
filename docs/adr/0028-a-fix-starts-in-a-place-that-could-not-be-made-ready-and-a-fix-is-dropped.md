---
number: 28
title: A fix starts in a place that could not be made ready, and a fix is dropped
status: proposed
date: 2026-10-13
decision-makers:
- Chuck Swanberg
---

# A fix starts in a place that could not be made ready, and a fix is dropped

Status: proposed by swancloud-design on 2026-10-13, from two readings wldn's planner recorded; accepted on the user's yes (`briefs.15`).

Deciders: the user, on acceptance. Written by swancloud-design.
Amends: `teams.3`; the details of `plan.9` and `plan.17`; record 0023, point 4, for a fix's place.
Sources: signals 2026-10-13-swancloud-planner-2e24fc2d/01 (a refused fix cannot be closed) and /02 (a bolt with a broken toolchain cannot take main), both asserted by wldn-planner; `plugin/lib/plan.py` `fix_run`, `fix_cmd`, `leftover`, `own_place`, `fix_place`, `make_place`, `reap`, `tidy`, `tidy_over`, `op_unit_drop`; `plugin/lib/kit.py` `readying`, `step_failed`; the `bolt-teams` spec, "Work happens in fixed places", "Fixes during a bolt are built beside its units", "A worktree goes when its work is over"; the `kit-toolchain` delta of `a-kit-declares-its-toolchain-and-tests`, "A toolchain that fails"; record 0023, point 4; `plan.8`, `plan.10`, `teams.5`, `read.4`.

## Context and problem statement

Two readings from wldn on 2026-10-13, both worked around by hand.

**A refused fix cannot be closed.** `crew fix <team> <name> "<words>"` takes a slot, makes the fix's branch and place from the bolt, and makes the place ready through the kit's declaration (`plan.17`). A readying step that fails refuses the start with the place made and the slot given back (`fix_run`), and `crew fix` has start, `--merge` and `--wait`. The fix can't be run again: its place exists and no slot holds it, so the start is refused as a leftover, "name this fix differently" (`leftover`), though crew's own words promised "Running the command again sets it up" (`step_failed`, record 0023 point 4). And it can't be closed: a fix's place and branch go only once it has merged into its bolt or no plan has its bolt (`plan.9`, "A worktree goes when its work is over"), and there is no `crew unit drop` for a fix.

**A bolt with a broken toolchain cannot take main.** Every stage's place is made from the bolt, so when the bolt's own toolchain is broken, its declared toolchain command failing or what it installs unable to run, readying refuses every stage before an agent starts, the fix among them. The one way a bolt takes main is a fix whose agent merges main into its place and submits it to the bolt (`plan.8`, `teams.5`), so the bolt is stuck until someone makes the worktree, merges main and submits by hand.

## Decision drivers

- A bolt is repaired only through a fix ("a defect is a fix, and a new need is a new unit"; `plan.8`: the bolt takes main by a submission from a fix). The repair path must not depend on the bolt being in repair.
- Record 0023, point 4: a worktree is made ready before any agent starts in it, so no agent spends its context on setup, and a command run again after a failure sets it up.
- Like things under the same rule: a unit in flight is dropped by `crew unit drop`, refused only once it has merged; a fix has no plan record, so its end is its slot's and its place's.
- `plan.10`: a branch holding commits the bolt lacks is kept and named when its worktree goes.

## Decision outcome

1. **A fix's agent starts once its place is made, whether or not the place could be made ready.** The step that failed and its last lines go to the agent with the fix's words, so the agent knows what it stands in. A unit's or chore's stage stays refused until its place is ready, as record 0023 point 4 has it: its agent builds on the bolt and is not its repair, and the command run again readies the place again. A fix refused for a place that is not its own, hand-made or made from another bolt, stays refused (`read.4`).
2. **A fix ends by its merge, by `crew fix <team> <name> --drop`, or with its bolt.** The drop is the conductor's, as the fix's start is; it frees the fix's slot, ends its agent when one is up, and its place and branch go as a dropped unit's do, through the kit's worktree tool, the branch kept and named when it holds commits beyond the bolt (`plan.10`). A fix that has merged into its bolt can't be dropped.
3. Until both land, a fix refused at readying stands with its branch and place on the team's host, and is closed by hand; `_open.md` says so.

## Consequences

- A fix is never refused for a place that could not be made ready; the failed readying reaches its agent instead. The agent that merges main into its place and submits gets sluice's verdict on the merged tree, whose declaration sluice reads for its own checkout, so the bolt's checks run on the repaired toolchain.
- A fix a team no longer wants, refused, abandoned or overtaken, leaves the team by one command, and its slot is free for the next.
- `teams.3` is amended, `plan.9` and `plan.17` in their details; the `bolt-teams` spec's "Fixes during a bolt are built beside its units" and "A worktree goes when its work is over" change at the units' archive.

## Considered options

- **Readying never refuses a stage; every agent is told what failed.** Rejected: a unit's agent would start on a bolt it can't build on and spend its stage finding out, which record 0023 point 4 chose against; only the fix's agent is the repair.
- **A flag on the start, `crew fix … --unready`.** Rejected: the conductor would have to know readying will fail before it runs, and the fix's start is the one stage whose agent is the repair, so nothing is gained by asking.
- **A refused fix keeps its slot, and the same command runs it again.** Subsumed by point 1: with it, readying refuses no fix. It would also hold a slot on every refusal, with no agent working.
- **Closing a refused fix by dropping its bolt.** Rejected: it drops the bolt's units with it.
- **Tidy removing a fix's place once no slot holds it.** Rejected: a fix whose slot was freed with commits in its place would lose them (`read.4`, `plan.10`); the drop is a conductor's word, and the branch with commits beyond the bolt is kept.
