---
status: proposed
date: 2026-10-27
decision-makers: the user, swancloud-design
consulted: madswan-design (Flume's kinds), wldn-design, swancloud-planner
---

# A card carries what the stage's run made, as Flume gave it

Status: proposed to the user on 2026-10-27, as `briefs.15` has it, and revised on 2026-10-28 on their note of 2026-10-27 ("I need the design from Flume put in front of me before we lock in this ADR"): Flume's design is set out below in plain words, and the landing's preview now follows it, brought up on the user's ask and never held while a card sits; accepted only on their yes.

Deciders: the user, on this record's card, who asked for it in their words on 2026-10-26 (swancloud signal 2026-10-26-swancloud-planner-89511ba8/01: "I want to make sure we think about this design more in terms of how Flume ties in. Landing a bolt is one thing but we could possibly have another Flume kind where maybe it was running or created a spike. We want a card that has the link to that spike or maybe there's a preview server that's not done through sluice, although I'm not sure we would want that, really"), and on 2026-10-26 to wldn's planner ("when I'm asked if we should land a bolt, the agents would make sure a sluice preview is running so I could test everything in it"); written by the design agent with madswan-design, who holds Flume's kinds.
Amends: `briefs.13` (what a card carries); record 0031's amendment of 2026-10-26 (the landing's preview) is this record's one case, as revised here: the row carries what brings the preview up, and the preview comes up on the user's ask; it is held no more.
Sources: the two signals; agentplot/blueprints `design/flume/requirements.md` clause 129 at 590acd6, with 23, 43 and C.2 as amended, and flume record 0007 (rule core.23), accepted by the user on 2026-10-27 on its card after a revision on their note; sluice's `sluice preview` (a running copy of a revision a branch has landed); switchboard-kit `gates.14` (wldn's practice).

## Context and problem statement

crew's six cards are built from the event's facts and never by an agent (`briefs.13`). The user wants a card that asks about work to carry a link to what the work made: a preview to test before a landing, a spike a kind ran or made. Record 0031's amendment of 2026-10-26 wrote the landing's case, a bolt's row carrying its sluice preview; the user asked that the design be thought through with Flume first, since landing is one kind among those Flume will run.

Flume's side is written (clause 129): a stage's declaration names what it makes besides its deliverable (`makes = ["preview", "spike", …]`); the run records each thing's address as the run knows it, one line per thing, name, what it is and address, at `made.jsonl` in the place's own folder beside flume's held state; flume reads the lines when the stage ends and hands them to whoever waits and to its status, making, checking or rewriting no address of its own; a declared thing with no line is the deliverable not yet made, and the stop check sends the agent back naming it; the lines go with the folder when the place is tidied, so the caller keeps what it was given. A kind that lands makes nothing by landing: what the waiter learns is the commit it landed as, and a preview of a landed revision is the merge queue's, asked of sluice at that commit by whoever wants one.

## Flume's design behind this record, in plain words

The user asked to read Flume's side before deciding. It is two documents, both settled on madswan's side: clause 129 of Flume's requirements (agentplot/blueprints `design/flume/requirements.md`, with clauses 23 and 43) and flume record 0007, which the user accepted on 2026-10-27 after asking on its first card "How does this work? What process is driving this loose preview? Is it Flume or is it Crew? What if the preview needs to be started? ... being able to toggle the server on and off?". Together they say:

1. **A kind says what each stage makes.** Besides its deliverable (a head or a report), a stage may be declared to make things a person will want to open: a preview, a spike, a page, a report kept elsewhere (clause 23, clause 129, `makes = [...]`).
2. **The agent that made a thing writes its address.** The stage's run records each made thing in one file in the place's own folder, one line per thing: its name, what it is, and its address as the run knows it. Flume fills that path into the prompt as `{{made}}`. A thing the run made without declaring it may be written there too.
3. **Flume carries the lines as written and invents nothing.** When the stage ends, Flume reads the file and hands the lines to whoever waits on the stage and to its status (clause 43). It makes, checks or rewrites no address of its own.
4. **A declared thing with no line means the stage is not done.** When the agent goes quiet with a declared thing unrecorded, the stop check sends it back naming the thing, as it does for a missing deliverable.
5. **The lines go with the place.** When the place is tidied the file goes with it, so a caller that wants the addresses afterwards keeps its own copy, as it keeps a report.
6. **A thing that must run is never a loose server.** A server an agent started is nobody's once the stage ends: nothing holds it, nothing restarts it, the host's next restart ends it, and a card pointing at it for days holds a dead link. So a running thing is recorded as what brings it up, the branch and revision, and a stage starts no server that outlives its place. The merge queue already owns a running copy of a revision: `sluice preview <branch> <revision>` brings one up from a landed revision and hands back its addresses, `sluice release` ends it, and asking twice gives the same one back. Whoever shows the card brings the preview up when the person opens it and releases it when they are done. That is the toggle the user asked for: sluice's on and off, pressed by the caller, with no daemon of Flume's.
7. **A landing makes nothing by landing.** Whoever waits on a submission learns the commit it landed as. A preview of a landed revision is the merge queue's to make, asked at that commit by whoever wants one.

Flume's rule core.23 is drawn from record 0007: what a stage made is read from the line its run wrote and carried as written, a durable thing by its address and a running thing by the branch and revision that bring it up.

## Decision outcome

A card crew raises about a stage's work carries what Flume gave at that stage's end, each line as the run wrote it, name, what it is and address, and nothing crew made, checked or rewrote; a card raised while the stage runs carries what the run has written so far, and the card changes in place as lines are added. A thing that must run is carried as what brings it up, the branch and revision, never as a server's address: crew brings it up when the user asks for it from the card, through sluice's preview, carries the addresses sluice hands back on the card while it is up, and releases it when the user says they are done or when the card closes. A kit's landings card carries, in each bolt's row, what brings the bolt's preview up, the bolt branch and its head, where the kit's policy names a preview, and "no preview" where it names none; the preview is brought up on the user's ask from the row and released when they are done, when the bolt lands or when it is dropped, and is never held while the card sits; when the head moves, the row says so and a preview up at the old head is released. A card about a landed revision carries the commit it landed as and no preview of its own; whoever wants one asks sluice at that commit. Until crew runs stages through Flume, a stage's `made.jsonl` is read where the place is, and a stage that writes none gives its card no link.

## Considered options

1. Cards carry what Flume's runs recorded as made, a running thing as what brings it up, and the landings row the bolt branch and head with the preview brought up on the user's ask (chosen): the link is the run's own fact, one shape for every kind, crew invents none, and no server is held for a card that sits (flume record 0007).
2. The landing's preview alone (record 0031's amendment of 2026-10-26, as proposed as a unit). Rejected by the user as one case written before the design: "think about this design more in terms of how Flume ties in".
3. crew makes the links itself, a preview per bolt and a page per spike, from what it knows of the kind. Rejected: crew would name and check addresses the run alone knows, and would have a rule per kind.
4. A preview server not through sluice. Rejected, as the user doubted it: a preview of a revision a branch has landed is sluice's, and a preview of anything else is what a stage makes and records.
5. The landings row's preview held by the conductor's wait from the moment the row is posted until the landing (this record's first draft). Rejected with flume record 0007: a card may sit for days, and a preview held that long is a loose server on a loaded host; the user asked for a toggle, and sluice's preview and release are it.

## Consequences

- `briefs.13` gains the clause, marked proposed; record 0031's case is unheld.
- A crew unit builds it: the card builders read `made.jsonl` from the stage's place and carry its lines; a landings row carries the bolt branch and head and an ask to bring the preview up where the policy names one, crew brings it up through sluice's preview on that ask and releases it on the user's done, at the landing or the drop, the row carrying sluice's addresses while it is up; a card changes in place as lines are added and as a preview comes up or goes; the tests prove each card's facts.
- The unit proposed as 369 is remade from this record once accepted.
