---
status: rejected
date: 2026-10-26
decision-makers: the user, swancloud-design
consulted: madswan-planner, swancloud-planner
---

# A bolt that builds on another bolt is given once that bolt has landed

Status: rejected by the user on 2026-10-27, on their card (req_e437516c9e3f46839dae): "I don't understand where this requirement came from. The whole point of a bolt is that it's something that can be delivered to production independently". `plan.13` and `teams.16` stand unamended: a bolt is planned so that it lands and delivers on its own, so a bolt whose units build on another bolt's unlanded code is mis-planned, the planner's to plan otherwise, in one bolt or after the other has landed, and no `After` between bolts is added.

Deciders: the user, on this record's card; written by the design agent from madswan-planner's finding of 2026-10-26.
Amends: `plan.13` (a bolt's `After`), `teams.16` (the give); the `bolt-plan` spec gains a bolt's `After`.
Sources: madswan signal 2026-10-26-madswan-planner-<see swancloud's 942ec4f8/02>, swancloud's 2026-10-26-swancloud-operator-942ec4f8/02; `plan.8` (a bolt is cut from the kit's main as it stands), `plan.19` (made at the give from `origin/main`), `plan.13` (`After` within one bolt), `roles.1` (the dispatcher gives bolts); records 0011 and 0014 (what `After` is).

## Context and problem statement

A bolt is cut from its kit's main as it stands at the give (`plan.8`, `plan.19`), and `After` orders units within one bolt (`plan.13`); nothing in the plan says a bolt builds on another, so the dispatcher gives the next planned bolt whenever a team is free. flume-the-profiles was given while flume-the-core, whose code every profile unit builds on, still waited to land: its branch was cut from a main without the core, and every construct stopped short for want of what it builds on. The plan knew the order, since the planner placed the profiles after the core, but the file's order is a queue, not a dependency, and two teams drain a kit's queue side by side.

## Decision outcome

A bolt record may name `After`, another bolt of the same kit whose landed code its units build on, written by the planner's proposal (`crew bolt after <bolt> <other>`, a `Do` a proposal may hold) and read by the dispatcher: a give of a bolt whose `After` has not landed on its kit's main is refused, naming the bolt it waits for and where it stands, proven or building, and the dispatcher passes to the next planned bolt the team may take; a bolt's `After` names only a bolt planned or held ahead of it and never one that has landed, which the write drops as met; a proposal that orders a bolt before one it comes after is refused. A unit's `After` stays within its bolt (`plan.13`); what a unit builds on from another bolt is that bolt's landed main, which the give then cuts from. A bolt already given before this lands is not re-cut; its units take main in as `teams.21` has it once the bolt it builds on lands.

## Considered options

1. A bolt's `After`, read at the give (chosen): the plan says the dependency once, where the planner already knows it, and the give honours it.
2. The dispatcher gives a kit's bolts strictly in file order, one at a time. Rejected: independent bolts of one kit build side by side today, and the order would hold them for nothing.
3. Cut the dependent bolt from the other bolt's branch. Rejected: stacked bolts land in order or not at all, a landing of the first rewrites the second's base, and `plan.8` cuts from main alone.
4. Let the constructs wait: a unit whose source is not on main stops short and is run again after the landing. Rejected as the design: it is what happened, a team's slots held by units that can start nothing, and the fix of record 0040 does not reach it, since nothing in the plan put them after anything.

## Consequences

- `plan.13` and `teams.16` gain the clauses, marked proposed.
- A crew unit builds it: the bolt record's `After`, `crew bolt after` and its proposal `Do`, `plan.1`'s checks (same kit, no cycle, not landed), the dispatcher's give refusal naming the bolt waited for, `crew bolts` and the board showing a bolt waiting on another, and the tests.
- The planner names the dependency in the proposal that plans the dependent bolt, as it names a unit's `After`.
