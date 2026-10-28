---
status: proposed
date: 2026-10-27
decision-makers: the user, swancloud-design
consulted: madswan-design (Flume's kinds), wldn-design, swancloud-planner
---

# A card carries what the stage's run made, as Flume gave it

Status: proposed to the user on 2026-10-27, as `briefs.15` has it; accepted only on their yes.

Deciders: the user, on this record's card, who asked for it in their words on 2026-10-26 (swancloud signal 2026-10-26-swancloud-planner-89511ba8/01: "I want to make sure we think about this design more in terms of how Flume ties in. Landing a bolt is one thing but we could possibly have another Flume kind where maybe it was running or created a spike. We want a card that has the link to that spike or maybe there's a preview server that's not done through sluice, although I'm not sure we would want that, really"), and on 2026-10-26 to wldn's planner ("when I'm asked if we should land a bolt, the agents would make sure a sluice preview is running so I could test everything in it"); written by the design agent with madswan-design, who holds Flume's kinds.
Amends: `briefs.13` (what a card carries); record 0031's amendment of 2026-10-26 (the landing's preview) stands as this record's one case and is held no more.
Sources: the two signals; agentplot/blueprints `design/flume/requirements.md` clause 129 at 590acd6, with 23, 43 and C.2 as amended, and flume record 0007 (rule core.23), proposed; sluice's `sluice preview` (a running copy of a revision a branch has landed); switchboard-kit `gates.14` (wldn's practice).

## Context and problem statement

crew's six cards are built from the event's facts and never by an agent (`briefs.13`). The user wants a card that asks about work to carry a link to what the work made: a preview to test before a landing, a spike a kind ran or made. Record 0031's amendment of 2026-10-26 wrote the landing's case, a bolt's row carrying its sluice preview; the user asked that the design be thought through with Flume first, since landing is one kind among those Flume will run.

Flume's side is written (clause 129): a stage's declaration names what it makes besides its deliverable (`makes = ["preview", "spike", …]`); the run records each thing's address as the run knows it, one line per thing, name, what it is and address, at `made.jsonl` in the place's own folder beside flume's held state; flume reads the lines when the stage ends and hands them to whoever waits and to its status, making, checking or rewriting no address of its own; a declared thing with no line is the deliverable not yet made, and the stop check sends the agent back naming it; the lines go with the folder when the place is tidied, so the caller keeps what it was given. A kind that lands makes nothing by landing: what the waiter learns is the commit it landed as, and a preview of a landed revision is the merge queue's, asked of sluice at that commit by whoever wants one.

## Decision outcome

A card crew raises about a stage's work carries the addresses Flume gave at that stage's end, each as the run wrote it, name, what it is and address, and nothing crew made, checked or rewrote; a card raised while the stage runs carries what the run has written so far, and the card changes in place as lines are added. A kit's landings card carries, in each bolt's row, the preview sluice gives at the bolt's head, the bolt branch's landed revision, asked by the conductor's wait when the row is posted or the head moves (`sluice preview bolt/<bolt> <head>`) where the kit's policy names a preview, and "no preview" where it names none; the preview ends with the landing or the bolt's drop, as the policy's release has it. A card about a landed revision carries the commit it landed as and no preview of its own; whoever wants one asks sluice at that commit. Until crew runs stages through Flume, a stage's `made.jsonl` is read where the place is, and a stage that writes none gives its card no link.

## Considered options

1. Cards carry what Flume's runs recorded as made, and the landings row sluice's preview at the bolt's head (chosen): the link is the run's own fact, one shape for every kind, and crew invents none.
2. The landing's preview alone (record 0031's amendment of 2026-10-26, as proposed as a unit). Rejected by the user as one case written before the design: "think about this design more in terms of how Flume ties in".
3. crew makes the links itself, a preview per bolt and a page per spike, from what it knows of the kind. Rejected: crew would name and check addresses the run alone knows, and would have a rule per kind.
4. A preview server not through sluice. Rejected, as the user doubted it: a preview of a revision a branch has landed is sluice's, and a preview of anything else is what a stage makes and records.

## Consequences

- `briefs.13` gains the clause, marked proposed; record 0031's case is unheld.
- A crew unit builds it: the card builders read `made.jsonl` from the stage's place and carry its lines; the conductor's wait brings up the landings row's preview at the bolt's head where the policy names one and the row carries its addresses or says "no preview"; a card changes in place as lines are added; the tests prove each card's facts.
- The unit proposed as 369 is remade from this record once accepted.
