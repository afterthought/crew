---
number: 11
title: After names code the dependent builds on
status: accepted
date: 2026-10-08
decision-makers:
- Chuck Swanberg
- the merge-queue design session
---

# `After` names code the dependent builds on

Deciders: the user, in the merge-queue exploration of 2026-10-08 (`agentplot/blueprints:design/sluice/requirements.md` and the session that wrote it); the design session there.
Sources: `openspec/specs/bolt-plan/spec.md` "The file's order and dependencies are the plan"; `plugin/roles/conductor.md` line 17; Flywheel Next requirement 31 (`agentplot/blueprints:design/flywheel-next/requirements.md`); the sluice statement's clauses on order at landing; AgenticFlict (arXiv 2604.03551) and Xu et al. (arXiv 2607.04697) on conflict rates between agents' changes.

## Context and problem statement

A unit's `After` names units of the same bolt that must merge before it starts. Three different things get called a dependency:

1. The dependent builds on code the dependency writes: a contour, a module, a command, a model, that does not exist until that code exists, and that the dependent's spec has to name.
2. The two units touch the same files.
3. The product wants one before the other.

Only the first needs a start gate. The second usually merges, and a merge queue that tests each entry in the combination it will land in finds what does not before any check runs. The third is build order, which the plan already has: order in the file is build order. A merge queue for agents in worktrees (sluice) lands in order and attributes a conflict to the later entry, so it removes the reason for the second and third, and not for the first.

Could a dependent start earlier, at its dependency's approved spec, or at its verify, when the code exists but the branch still moves?

## Decision drivers

- A dependent's construct writes a spec that cites the contour by name. A spec written before the contour exists invents it, and two agents invent it differently.
- Construction builds only what a written, settled decision records. In crew a unit's code is settled at its merge into the bolt, not before.
- A verify stage may send a unit back to code (`bolt-teams` spec), which rewrites the code a dependent started at verify would already cite.
- Concurrency is bounded by a team's slots. The idle a start gate costs is the dependency's review and verify time, not its build.

## Considered options

1. Start the dependent's code once the dependency's spec is approved, as if the spec were an interface. Assumes a contract exists before the code; for a contour that is discovered in the building, it does not.
2. Start the dependent once the dependency is in verify: its code exists, but its branch still moves and a send-back rewrites it.
3. Keep the start at merge, narrow what `After` means, and make the dependency small.
4. Drop `After` and let the queue find conflicts. Loses the contour dependency, which no conflict detects.

## Decision outcome

Option 3.

1. `After` names a unit whose code the dependent builds on: a contour that exists only once that unit's code exists. It is never set for units that only touch the same files, and never to express product order; order is the file's.
2. The dependent starts only once each `After` unit has merged into the bolt, as the `bolt-plan` spec says. Its construct is the first stage that reads the contour, so nothing of it starts earlier.
3. The lever for concurrency is the plan, not an earlier start: when several units would come after one, the planner carves the contour the others need into a small first unit, so the rest run side by side once it merges.
4. Under a merge queue, landing order within a bolt follows `After`; units with no `After` between them land in any order, and a conflict between them is the later entry's chore, never a reason to add an `After`.

### Consequences

- `plan.13` added in `docs/architecture/plan.md`; the `bolt-plan` spec's "SHALL NOT start until each of them has merged into the bolt" stands as written; `plugin/roles/planner.md` gains the carving sentence; `conductor.md` is unchanged.
- Nothing to build: no check can tell a contour dependency from a shared file, so `roles.3` has nothing to refuse.
- Option 2 may be revisited once verify send-backs are measured rare on a kit.
