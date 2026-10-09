---
number: 14
title: Units build at once and are reviewed in batches
status: accepted
date: 2026-10-09
decision-makers:
- Chuck Swanberg
- the concurrent-units design session
---

# Units build at once and are reviewed in batches

Deciders: the operator, in the operator's ruling of 2026-10-09 (decisions D1 to D8 below); the concurrent-units design session, which wrote this record and the change `concurrent-units`.
Sources: `openspec/specs/bolt-plan/spec.md` "The file's order and dependencies are the plan" and "A unit's stage is read from the kits"; `openspec/specs/bolt-teams/spec.md` "The user reviews every unit before it is coded"; `plugin/roles/conductor.md` line 83 (the building loop's Touches rule); `plugin/roles/construct.md` line 27 (the Touches list); `plugin/lib/plan.py` `run_check` (construct refused while a unit waits on `After`, code refused before approval); record 0011; the sluice statement, `agentplot/blueprints:design/sluice/requirements.md`, on order at landing and conflict attribution.

## Context and problem statement

A bolt's units are built nearly one at a time. Three gates hold them back:

1. **After waits on merge.** A unit with `After` cannot start construct until each After unit has merged into the bolt (record 0011, `plan.13`), so a chain of three units runs end to end: construct, review, code, verify and merge, three times over.
2. **Overlapping Touches serialize building.** The conductor builds two units side by side only when their *Touches* lists do not overlap (`conductor.md` line 83), and "when in doubt, don't". The lists are prose at the end of `proposal.md` (`construct.md` line 27), compared by eye; nothing reads them, and nothing checks them against what the unit changed.
3. **Every unit waits on the user's review before code** (`teams.5`, `bolt-teams` "The user reviews every unit before it is coded"). A unit constructed at night sits in review until the user reads it, and the user reads changes one card at a time.

The user's time is the scarcest thing in a bolt, and a merge queue (sluice) lands units in order and attributes a conflict to the later entry. What the gates protect can be had more cheaply: a dependent needs its dependency's plan, not its merge; an overlap matters only at merge; and the user's view of every change can come in batches, after building has started, with feedback that amends the unit in flight.

## Decision drivers

- Concurrency is bounded by slots, not by the user's reading speed or by the longest chain of `After`.
- A dependent builds on its dependency's contour (record 0011). Once the dependency's change is written, the contour has a name and a shape; the dependent can code against that plan and the work as it stands, and must not land before it.
- A conflict between two units is found most cheaply before either is finished, and is resolved best by an agent that knows both intents.
- The user sees every change before its bolt lands, and what the user says about a change still reaches it while it can be changed.
- Only the user approves (`roles.1`, `roles.2`): feedback in a batch is the user's word, and nothing here lets an agent approve on its own judgment.

## Considered options

1. **Keep the review gate**: code waits for the user's approval of each unit. Keeps the user ahead of every line of code, at the cost of every unit idling between construct and the user's next look; the user reads one change per card and the bolt moves at the user's pace.
2. **Serialize building on Touches overlap**, as the building loop does today. Avoids conflicts by never building overlapping units together; costs the concurrency a merge queue makes safe, and rests on lists nothing reads.
3. **Dependents wait for merge**, record 0011's point 2. The dependent reads the contour as merged code; a chain runs end to end.
4. **Plan, then fan out; dependencies on plans; conflicts forecast; batch review**, the operator's ruling of 2026-10-09.

## Decision outcome

Option 4, as the operator ruled on 2026-10-09:

- **D1 Plan, then fan out.** Once a bolt's plan is approved, every unit's construct runs at once, slots permitting. Construct never waits on `After`; `run_check`'s refusal of construct for a waiting unit goes.
- **D2 Dependencies are on plans, not merges.** A unit whose After units have all finished construct (their OpenSpec change committed) may start code. Its place is made from the bolt's line with each After unit's work taken as it stands; when an After unit merges, the dependent's place is rebased onto the bolt while its agent is idle. A unit never merges before its After units; under sluice the queue's after-entries enforce it. Record 0011's meaning of `After`, code the dependent builds on and never shared files or product order, stands; its point 2, the start at merge, is replaced by this.
- **D3 Overlapping Touches no longer serialize building.** Overlap only orders merging. On each wait or poll of the conductor's, crew dry-runs with `git merge-tree` the merge of each unmerged unit's head with the bolt's line and with the heads of sibling units ahead of it; a predicted conflict is told to the later unit's agent when it is idle, with the paths and the other unit's OpenSpec change. The building loop's "build them one after the other" goes.
- **D4 The later unit resolves.** A conflict, forecast or real, is resolved by the later unit's agent, which is handed the other unit's OpenSpec change and the conflicting paths, so that keeping both intents is informed.
- **D5 No review gate; batch review instead.** Code starts as soon as construct is done and D2 holds; `crew unit approve` and the gate in `teams.5` go. Every N constructed or amended changes, or T hours since the last batch, whichever comes first (a team's setting, 5 and 4 hours by default), a reviewer agent summarizes each change not yet seen: what it does, the decisions it took, its risks, its Touches, and anything the user would likely care about. The batch is one Pending You card with a question per unit, fine or feedback. The card carries each unit's summary and attaches or links its full OpenSpec change, so the user drills in and answers in Pending You itself. Feedback amends the unit in flight through the existing amend path, construct run again with the user's words, and the unit goes on with no re-approval. A unit that has merged is never amended: a defect is a fix, new work a new unit.
- **D6 Landing guard.** A bolt is offered for landing only once every unit's latest change has appeared in a batch; the landing card lists any that have not, and a batch is triggered for them.
- **D7 Merging.** The merge stage becomes `wt submit bolt/<bolt>` when sluice is available; until then `wt merge` stays, one merge at a time as now.
- **D8 Touches is read and checked.** Construct writes Touches as a fenced list of repository paths or globs under a `## Touches` heading in `proposal.md`. crew reads it before code and tells a unit whose Touches overlap a unit in flight, which feeds D3's forecast before any code exists. At verify, `git diff --name-only <bolt>...<unit head>` is compared with the declared list; a path changed and not declared is a verify finding, and the list is corrected.

### Consequences

- **`plan.6`** is amended: an amended unit reads amended, then construct, and is refused code, verify and merge only until construct has committed again; no approval is asked.
- **`plan.13`** is amended: `After` keeps its meaning; the dependent's construct never waits, its code waits on each After unit's construct, and its merge on each After unit's merge.
- **`teams.5`** is amended: the approval gate goes; merge is refused before every After unit has merged; a merge goes through `wt merge bolt/<bolt> --no-squash --no-remove`, or `wt submit bolt/<bolt>` where sluice is available.
- **`briefs.4`** is amended: a change is put before the user in a batch card, not as a review of its own. **`briefs.5`** stands; its last clause covers a batch's feedback to a unit whose construct is still running, which waits until that construct settles.
- **`briefs.9`** is amended: a batch card carries each unit's summary and its whole change in Pending You, with no plannotator session, as the operator ruled; the rule stands for every other card that asks the user to read something.
- **`roles.1` and `roles.2`** stand: only the user approves. A batch's feedback is the user's word; nothing in a batch is an approval an agent can give, and `crew unit approve` leaves the approvals crew does not refuse by caller.
- New rules `teams.12` (Touches is read; overlap and forecast conflicts are told and order only merging), `teams.13` (the later unit resolves a conflict) and `briefs.12` (the batch review and the landing guard).
- The `bolt-plan` and `bolt-teams` specs, and a new `review-batches` spec, change only through `concurrent-units`' deltas (`docs.4`). `conductor.md`, `construct.md`, `verify.md`, a reviewer role, `plan.py` and `plugin/bin/crew` follow in that change. Until it is built, the amended and new rules are accepted and not built (`_open.md`).
- What this record leaves open is listed in `concurrent-units`' design, *Open questions*, and under *Decisions waiting* in `_open.md`.
