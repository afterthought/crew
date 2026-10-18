---
number: 20
title: A team is free for its next bolt once its current one is proven
status: accepted
date: 2026-10-11
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# A team is free for its next bolt once its current one is proven

Status: accepted by the user on 2026-10-18, on their card.

Deciders: the user, whose words raised it (2026-10-11, in the operator's pane, on the laptop's ssh fix: "No, it can go through fucking approval. It's just that it needs to get the fucking work done. I approved it and you added it to a bolt that's going to end up waiting on six other things."); swancloud-design.

Sources, read on 2026-10-11: the `bolt-teams` spec ("A bolt team builds one bolt at a time"); `teams.1`; `plan.8`; `roles.2`; crew's plan at swancloud/main 8f6e68e; swancloud-ops's and the operator's readings that day.

## Context and problem statement

The user asked for an emergency fix to git over ssh on the laptop. The design ruled it (`names.7`), the planner proposed it as a one-unit bolt first among swancloud's planned (proposal 114), the user approved, and the dispatcher's give was refused: swc-1, the one swancloud team running, holds `mac-studios-doctor-rows-are-green`, whose three units have all merged and which waits on its carrying fix's verification, its landing card, the user's yes and ops's landing. The team's four slots were idle through all of it, and the emergency bolt waited behind a landing it has nothing to do with.

This is the shape, not the day: with one team per kit, every planned bolt waits behind the previous bolt's landing, which is the bolt's proof, a card, the user's yes, the landing itself, and a carrying fix when the rebase conflicts, which it did for swc-1 and crw-2 that same day. A team that has finished building sits until the user and ops have finished landing.

## Decision drivers

- An approved bolt should start when its team has nothing left to build, not when the user has answered an unrelated card.
- The user's yes stays where it is: on the landing (`roles.2`; the user: "it can go through fucking approval").
- No special lane for emergencies: an emergency bolt is a bolt first among the planned, and whatever lets it start lets every bolt start the same way.
- A team's slots stay bounded (`teams.1`) and a landing that conflicts still has the team's fix to carry it (`plan.8`).

## Considered options

1. **A team is free once its bolt is proven**: every unit merged and the bolt's proof green on its head; the landing holds no slot.
2. **A second team per kit**: swc-2 in the teams file, the user's to add; doubles the sessions, and two teams' suites loaded mac-studio to 247 on 2026-10-10 (`tests.9`).
3. **An emergency lane**: a bolt marked urgent may be given to a team that holds one. A special case with its own rules, which the user has turned down elsewhere ("I don't want to have some hard-coded thing just for spikes").
4. **A proven bolt lands without the yes**: ruled out by `roles.2` and the user's words.

## Decision outcome

Option 1.

1. **A team builds one bolt at a time and may hold one more that is proven and waiting to land.** A bolt is proven when every unit of it has merged and its proof is green on its head. From that moment the dispatcher may give the team its next planned bolt, and crew refuses a give only while the team's held bolt has an unmerged unit or a proof not yet green.
2. **The proven bolt keeps of the team only what its landing needs**: a carrying fix when the landing's rebase conflicts (`plan.8`), which takes one of the team's slots like any fix, and the team's ops, who proves it. The conductor serves both bolts; a slot holds a stage of the new bolt or a fix of the old; never more than `units` are in flight (`teams.1`).
3. **The landing changes nothing**: it still runs on the user's yes, by main-level ops, through the kit's hooks (`state.3`, `roles.2`). What changes is that the next bolt's build no longer waits for it.
4. **The rail says what waits**: the proven bolt's row says it waits to land, and its landing card names any bolt waiting behind it, so the user knows what a yes frees.
5. **The second team stays the user's choice**, in the teams file, for throughput, not for unblocking.

Once accepted: the `bolt-teams` spec's purpose reads "builds one bolt at a time and holds at most one more that waits to land" at its next delta; `teams.md` gains the rule; the unit `a-team-is-free-once-its-bolt-is-proven` in crew builds it.

## Consequences

Good: an approved bolt starts as soon as its team has merged what it was building; today's emergency would have started at proposal 114's approval. Bad: a team can hold two bolts' rows on the rail, and a carrying fix for the old competes for slots with the new bolt's stages; the conductor's brief has to say both. Neutral: nothing lands sooner.
