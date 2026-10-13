---
number: 27
title: A unit's verify is fixed in one round by a fresh coder, and its change archived at its merge, with no card
status: proposed
date: 2026-10-13
decision-makers:
- Chuck Swanberg
---

# A unit's verify is fixed in one round by a fresh coder, and its change archived at its merge, with no card

Status: proposed to the user on 2026-10-13, as `briefs.15` has it; accepted only on their yes.

Deciders: the user, in the recovery session of 2026-10-13, whose words below are the decision; the defaults under *Decision outcome* were chosen in the main session, and are the user's to change. Written by the recovery's verify workstream.
Amends: `briefs.2`, `briefs.13`, `teams.5` and `teams.14`, and adds `teams.17`; record 0002, its verify row; record 0005, its verify card; record 0007, the merge's deliverable and the verify row's consequence. Builds record 0006's first point, the queued unit `a-merged-change-is-archived`.
Sources: `plugin/roles/conductor.md` (*Running the stages*, *Cards*, the building loop's step 3 and the chore's paragraph), `verify.md`, `coder.md`; OpenSpec's verify skill, `.claude/skills/openspec-verify-change/SKILL.md` (its report's CRITICAL "Must fix before archive", WARNING "Should fix" and SUGGESTION "Nice to fix", each with a recommendation); `plan.py` `rail_rows`, `stage_refusal`, `chore_refusal`, `verified`, `reach_way`, `card_refusal`, `delivered`; `plugin/hooks/cards` (`FORMS`); the `rail-cards`, `crew-rail` and `bolt-teams` specs, and the `chores` spec of `chores-beside-units-and-fixes`.

## Context and problem statement

Once a unit's code has delivered every task ticked, its conductor runs verify, reads the report, tells the user what it would do about each finding, and posts a verify card, keyed `verify/<unit>/<stamp>`, a `choice` or a `multi` of its options; the unit waits on the user. The answer runs code with the findings the user chose, or merge. A chore's verify goes the same way, and crew refuses a chore's merge until verify has run since its last code, so a fix to a chore calls for another verify and another card. The rail lists the report as a row until a commit or the merge ends it.

Record 0006 has a unit's change archived by its merge stage, first thing, so the bolt's specs say what its code does. Nothing builds it: no brief, prompt or check archives a change, and changes reach main open, fourteen of them at fd0d3d8 (`_open.md`).

## Decision drivers

- The user takes the recommendation almost every time, so the card and the wait cost a round trip for nothing.
- One standard round, simple to start with; a loop is later work.
- Every stage a fresh agent (`teams.2`).
- What changes what a unit is for stays the user's, by the amendment's path (`plan.15`).

## Decision outcome

The user, in the recovery session of 2026-10-13: "Right now we run after construction, then run verify, and then prompt the operator if they want to apply the verify fixes. I think we should instead go with the recommendations because 99 times out of 100 I'm just agreeing with whatever was recommended to me. I think having a new coding agent fix the verification and then move to archive is probably the way to go. Later we might want to do that in a loop but I think if we just did one round of verify, fixed if necessary, and then archived, that would be a pretty simple standard process to start with."

1. **Verify runs once**, when a unit's tasks are all ticked, or a chore's code has committed, as today. Its report ends by saying, of each finding it raised, fix, leave or amend: amend for a finding that would change what the unit is for, its intent or what its specs say must be true.
2. **One fix round, by a fresh coder.** When the report marks a finding fix, the conductor runs code once more: a fresh agent, told the report's path, fixes every finding the report marks fix and only those. No verify runs after it.
3. **The change is archived at the merge** (record 0006). A unit's merge stage first runs `openspec archive <unit> --yes` in the unit's place, committed on its branch, then merges; the merge has delivered once the bolt holds the change archived. A chore has no change, and merges as it does.
4. **No card and no wait on the user.** The verify card, its row on the rail and its form go. crew refuses a chore's merge until its verify has delivered once, never again since a fix round; a unit that has delivered its verify, and its fix round when one ran, waits to merge, where a forecast reaches it as a settle (`teams.14`).

**Defaults, chosen in the main session, which the user may change:**
- A finding the report marks leave is left; the report keeps it.
- A finding marked amend is no fix: the conductor tells the planner in the report's words, the planner proposes the unit's amendment (`plan.15`), and the unit waits to merge until the user answers it. Approved, construct runs again and the unit goes on from its tasks, a round of its own; dropped, it merges with the finding left. A chore has no intent to amend: its report marks each finding fix or leave.
- A fix round that stops short or fails is a stuck stage, told to the user as one is today; it runs again, or the unit merges without it, only on the user's word.
- One round only; a loop is later work.

### Consequences

- `briefs.2`, `briefs.13`, `teams.5` and `teams.14` say the above, and `teams.17` is new, each marked with this record and proposed until the user's yes. Records 0002, 0005 and 0007 name this record where they list the verify row, the verify card and the merge's deliverable.
- One unit in crew, `a-unit-is-verified-fixed-and-archived-in-one-round`, which builds record 0006's first point and so the queued `a-merged-change-is-archived`: `conductor.md`'s table, building loop and chore paragraph; `verify.md`'s report; `coder.md`'s fix round and its merge's archive; crew's rail, card keys, card hook, board and stage starts without the verify row and card; `chore_refusal`, `verified` and the merge's deliverable; the `rail-cards`, `crew-rail`, `bolt-teams` and `chores` specs through deltas.
- A verify card open when that unit lands matches no row: the rail names it with its owner, who closes it, as any card whose row is gone.

## Considered options

- **The card, as today**: the user decides each verify, and agrees almost every time.
- **No card, the conductor choosing the findings to fix**: the conductor writes no design (`briefs.1`), and the report's author is the one that read the change against its code.
- **An archive stage between verify and merge, run by the fixing coder**: "fix the verification and then move to archive" read as one agent's work; a stage with nothing to do but the archive when nothing is to fix, where record 0006 has the merge archive first.
- **One round, the report's recommendations fixed by a fresh coder, the change archived at its merge** (chosen).
- **A loop of verify and fix until the report is clean**: the user's "later".
