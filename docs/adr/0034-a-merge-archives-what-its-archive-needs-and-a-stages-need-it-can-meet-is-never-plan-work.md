---
number: 34
title: A merge archives what its archive needs, and a stage's need it can meet itself is never plan work
status: proposed
date: 2026-10-19
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# A merge archives what its archive needs, and a stage's need it can meet itself is never plan work

Status: proposed to the user on 2026-10-19, as `briefs.15` has it; accepted only on their yes. Record 0033 rules the slot; this record rules the two faults ahead of it.

Deciders: the user, on awb-1's deadlock (2026-10-19, in awb-1's pane: "why the fuck would you do that? can we get that root cause fixed", signal 2026-10-19-awb-1-conductor-5eafeeda/01 on wldn/main of WilldanGroup/crew-state, relayed by swancloud-planner as 2026-10-19-swancloud-planner-1e0507a1/01); swancloud-design.
Amends: `teams.4`, `teams.17`.
Sources, read on 2026-10-19: both signals; `teams.4`, `teams.5`, `teams.17` as amended by record 0027, `plan.5`, `plan.11`; `plugin/roles/conductor.md` on crew's main at 6010fce (the planner line, step 4 of the building loop, *When a stage stops short*); the open changes on crew's main at 6010fce, twelve, six with every task ticked (`a-board-shows-the-flow-in-the-terminal`, `a-stage-builds-from-its-sources-over-its-intent`, `a-stages-prompt-is-taken-or-sent-again`, `an-amendment-runs-construct-again-itself`, `page-of-the-flow`, `the-page-shows-the-board`), left open by merges before record 0027; `openspec archive --help` (validation against the specs, `--skip-specs`).

## Context and problem statement

awb-1's unit `the-production-class-account-is-seeded` reached its merge, which archives the unit's change first (`teams.17`). The archive needed five changes the bolt holds open with every task ticked, left by merges before record 0027, whose requirements the unit's deltas build on. The merge stopped short and named them. The conductor's brief says what changes the bolt is the planner's and that a bolt that can't land without new work says so; the conductor read the five archives as new work, the planner proposed them as a chore marked `--unblocks` ahead of the unit (`plan.5`, proposal 409), the user approved, and the chore could not start because the waiting unit held the team's one slot (record 0033). Three faults in a row: a merge that stops for something its own stage can do, a conductor that sends a stage's need to the plan, and a slot held by a wait. The user asks for the root cause fixed, not the slot alone.

## Decision drivers

- A merge's deliverable is its change archived into the bolt (`teams.17`): what that archive needs on the unit's own branch is the merge's own work.
- The plan holds what the bolt builds; a stage's need is not a change to that (`plan.5` places work the bolt needs to land, not work a stage left undone).
- A stale open change on main is housekeeping, not a unit or a chore, and not a reason a bolt waits for the user.
- A merge is not asked to carry what its unit has no part in: archiving an unrelated change's deltas into the bolt in a unit's merge puts spec changes nobody in the bolt built on into its landing, and a validation failure in one of them would stop a merge that is not its own.

## Considered options

1. **The merge archives what its archive needs; the conductor keeps a stage's need in the stage.** Each fully ticked change the bolt holds open that the unit's change builds on is archived on the unit's branch before its own, oldest first; a conductor answers a stopped stage with what to do and runs it again; the planner hears only of work that changes what the bolt builds.
2. **The merge archives every fully ticked change the bolt holds open.** Clears main's leftovers by the next merge in each kit, at the cost of a merge carrying changes its unit has no part in, and of one bad delta stopping another unit's merge.
3. **Archive chores**, as proposal 409 did: plan work for housekeeping, a card for the user, and record 0033's deadlock on a small team.
4. **The merge skips the specs** (`openspec archive --skip-specs`) when the archive fails: the bolt's specs stop saying what its code does, which record 0027 ended.

## Decision outcome

Option 1.

1. **A merge archives what its own archive needs.** Before archiving the unit's change, the merge stage archives, on the unit's branch and oldest first, each change the bolt holds open whose every task is ticked and whose requirements the unit's change builds on, one commit each; then its own. It stops short for no archive it can make. It stops short, naming the change, only for one it cannot make: a change not fully ticked, or a unit of the plan not yet merged, which `teams.17` already refuses.
2. **A stage's need that the stage can meet is the stage's.** When a stage stops short for something its own agent can do in its own place, an archive, a rebase onto the bolt, a tidy of its branch, the conductor runs the stage again with the word to do it (`teams.4`). The planner is told only of work that changes what the bolt builds: a unit added, changed or moved, or work the bolt cannot land without that no stage of it can do. crew refuses a chore or a unit proposed as a stage's prerequisite the same way it refuses the planner's `--unblocks` on a unit placed elsewhere.
3. **Main's leftovers are housekeeping.** A change open on a kit's main with every task ticked and nothing building on it is main-level ops's to archive on main through sluice, one commit each, on its own read, with no unit, no chore and no card. A bolt's merge archives one only when its own change builds on it.
4. **Nothing else changes.** `teams.17`'s refusal of a merge whose branch holds another plan unit's change open stands; record 0033's slot yield stands beside this; `plan.5` still places work a bolt needs to land, when that work is building, not archiving.

Once accepted: `teams.4` and `teams.17` read as amended below; the unit the planner proposed beside record 0033's, `a-merge-archives-what-its-specs-need-itself` on proposal 159, builds it in crew, the conductor brief's building loop and *When a stage stops short* with it, this record its source; swancloud-ops archives the six on crew's main.

## Consequences

Good: a merge whose archive needs an earlier change makes it and goes on; no conductor turns a stage's leftover into a proposal, a card and a slot; main's open changes stop accumulating a chore each. Bad: a merge commit can carry an earlier change's archive beside its own, which its landing's reader sees as two archives in one merge. Neutral: a change nothing builds on stays open until ops reads main; nothing lands sooner.
