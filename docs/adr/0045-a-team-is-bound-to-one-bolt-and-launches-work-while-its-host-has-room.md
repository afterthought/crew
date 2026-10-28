---
status: accepted
date: 2026-10-28
decision-makers: the user, swancloud-design
consulted: madswan-design (Flume's kinds and status), swancloud-planner
---

# A team is bound to one bolt and launches work while its host has room

Status: accepted by the user on 2026-10-28, on their card (req_f2cd7549a2674d88bdd3, "Approved"). Superseded when Flume runs a unit's whole state machine, by record 0047's move 5 as amended 2026-10-28 (accepted on its card): no team is bound to a bolt then, crew launches a bolt's work whole and keeps no slot and no count, the room and the queue Flume's by its callers' priorities (flume record 0010). Status of this mark: accepted with that amendment on 2026-10-28.

Deciders: the user, who settled the picture in their own words on the design agent's card of 2026-10-28 (req_49bc94cf20294abc890e, "Kinds and a team's bound with Flume: does this picture match your thinking?"): "Yes, write it up as one record" and, for the meantime, "Small crew fix now: a slot with no agent running is free to the bolt's fix"; and on 2026-10-27, rejecting records 0041 and 0042: "Honestly what's the difference between a fix, a unit, and a chore? They're all just different Flume kinds. Once we start integrating with Flume, we need to decide: is a team bound to one unit of work or is it able to work on multiple?" and "The whole point of a bolt is that it's something that can be delivered to production independently." Their words settle what they said; the record's other words are the design agent's, asked on this card.
Amends: `teams.1` (what a slot is and what "in flight" counts), `teams.3` (where a fix runs), `teams.16` (what a team is bound to); the open item "What a team holds at once, with Flume's kinds" in `_open.md`, which leaves when this record is accepted.
Sources: agentplot/blueprints `design/flume/requirements.md` (A.1 launches, C.2 the kinds, the callers table, the non-goals: "a team's slots, its cap, its bolts, its conductors, its approvals and the conflicts between its units are crew's"); flume's `_open.md` item on a team's bound; records 0041 and 0042 (rejected 2026-10-27) and 0044 (accepted 2026-10-27); swancloud signals 2026-10-26-swancloud-design-30320788/01, 2026-10-27-swancloud-design-5fad26ee/01, 84ce0b2a/01, 9b29b767/01, 2026-10-26-swancloud-operator-942ec4f8/01, 2026-10-27-crw-6-conductor-a740eccc/01 and 2026-10-28-crw-5-conductor-dbb57c8b/01; `crew status crw-5` and `crw-6` read on 2026-10-28 (four verified chores on crw-5 with no agent running, waiting on one fix with no slot).

## Context and problem statement

crew counts a team's capacity in slots, and a slot holds one piece of work from the moment it is planned until it merges (`teams.1`). A slot whose work is verified and only waiting to merge still counts as full, though no agent runs in it. On 2026-10-27 and 28 two teams deadlocked on exactly that: every slot held verified work waiting on one fix to the bolt, and the fix could get no slot. Record 0041 answered with a fix slot per team; the user declined it as a point solution and asked the bigger question: what a fix, a unit and a chore are, and whether a team is bound to one unit of work or may work on several. A third case is a unit waiting on the outside world (swb-4, 31 hours on a subscription renewal), which held its whole team.

Flume's design leaves the answer to crew: Flume launches one place per ask, runs its stages one agent at a time, and bounds nothing; "a team's slots, its cap, its bolts" are crew's, and whether a team is bound to one unit of work or several is held open in Flume until crew's integration is designed.

## Considered options

1. Slots as today: a place counts against the team from plan to merge, whether or not an agent runs in it.
2. A fix slot beside the unit slots (record 0041). Rejected by the user as a point solution.
3. A team bound to one bolt and to nothing smaller, working as many pieces at once as its host has room for, room counted in agents running, a waiting piece holding none (chosen).
4. No bound at all: every planned piece starts at once. Rejected: the host's seats and CPU, and sluice's run bound, are real limits, and an overloaded host is the meltdown of 2026-10-28.

## Decision outcome

Option 3.

1. **What a fix, a unit and a chore are.** Three shapes of one thing: a piece of work in its own worktree on its own branch, through a list of stages, then merged. A unit writes its change first, then codes, verifies and merges; a chore skips the change; a fix is code and merge on the bolt's own branch, to put the bolt right. In Flume's words they are three kinds in one format, each a list of stages with what every stage must deliver; the only difference between them is the stage list, and none of them is a kind of slot.
2. **A team is bound to one bolt.** A bolt is what ships on its own, so a team holds one bolt at a time (and one more proven and waiting to land, as `teams.16` has it), and is bound to nothing smaller: no count of units, chores or fixes.
3. **Room is the host's, counted in agents running.** Inside its bolt the team works as many pieces at once as its host has room for, of any kind. What bounds that is how many agents the host can run and how many checks sluice runs there, never a slot count. A piece that is waiting, on a merge, on a card, on the outside world, holds no agent and so takes no room. When the host is full, the next piece waits, and a piece that every other piece waits on, a fix to the bolt's branch, goes first: priority, not a reserved slot.
4. **A piece waiting on the outside world holds its team no longer than the planner lets it.** It takes no room. What it can still hold is the bolt's landing, since a bolt lands whole: then the planner moves it to a later bolt and the bolt lands without it. crew's part is to say so: a team whose bolt is held by one waiting piece is a stalled team, raised as record 0044 has it.
5. **What goes where.** Flume runs the work and knows which places have an agent running and which are waiting and on what; sluice tests, lands and bounds a host's checks; Tailrace releases and deploys; crew keeps the plan, the give, the conductor's word that starts a stage, the cards, the board, and how long each piece has waited and on whom. Once crew launches through Flume, crew starts a piece whenever Flume's status says the host has room, and counts no slots.
6. **Until then, the slots stand with one change** (the user's "small crew fix now"): a slot whose agent is not running and whose work waits on a fix of the team's bolt is lent to that fix. The fix's agent runs in it; the waiting work keeps its place, its branch and its stage, and goes on in the same slot once the fix has merged. "In flight" counts agents running, so a team never runs more agents than it has slots.

## Consequences

- `teams.1`, `teams.3` and `teams.16` carry the amendment, accepted 2026-10-28; the open item has left `_open.md`.
- On the yes, one crew chore now: `a-slot-whose-agent-is-not-running-is-lent-to-its-bolts-fix` (point 6), with its cases: every slot holding verified work waiting on the fix; a slot whose agent is running is never lent; the waiting work resumes in its slot after the fix merges.
- A question to Flume's design, through madswan: `flume status` says, per host, how many agents run and whether there is room for one more, in the terms crew launches with; crew's unit that launches while Flume says room is proposed when that integration is designed, never before.
- Records 0041 and 0042 stay rejected; the deadlocks they answered are read against this record.
