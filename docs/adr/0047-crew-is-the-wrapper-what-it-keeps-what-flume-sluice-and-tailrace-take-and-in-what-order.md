---
status: proposed
date: 2026-10-28
decision-makers: the user, swancloud-design
consulted: madswan-design (Flume, sluice, Tailrace), swancloud-planner, swancloud-ops
---

# crew is the wrapper: what it keeps, what Flume, sluice and Tailrace take, and in what order

Status: proposed to the user on 2026-10-28, as `briefs.15` has it; accepted only on their yes.

Deciders: the user, in the design agent's pane on 2026-10-28, holding record 0046: "I don't want to approve it without knowing two things: that the overall comprehensive design for crew is well understood and that the required changes aren't going to just cause us to start making more and more mistakes because we didn't design it well"; and their standing words: on 2026-10-27, approving record 0044, "I'd rather spend the tokens to build out the correct functionality in Flume, sluice, and Tailrace instead of continuing to make crew more kludgy"; on 2026-10-27, rejecting records 0041 and 0042, "They're all just different Flume kinds ... I feel like this is trying to stomp out fires and not stepping back and thinking about the big-picture design"; on 2026-10-28, through swancloud-ops, that each mechanism is placed in Flume, sluice or Tailrace where it belongs, else in crew as their wrapper, Flywheel not being the plan. Their words settle what they said; the rest of the record is the design agent's, asked on this card.
Amends: `core.md` gains `roles.5`; `_open.md` gains the moves not yet made, one line each; records 0043 to 0046 are read as chapters of this one, 0046 trimmed as this record says.
Sources: agentplot/blueprints `design/flume/requirements.md` (purpose, A.1 to A.13, the callers table with crew's row, S7, the non-goals: "a team's slots, its cap, its bolts, its conductors, its approvals and the conflicts between its units are crew's"); agentplot/flume main on 2026-10-28 (requirements, site and records, no code yet); sluice's README and records 0045 (previews), 0066 (no probe before a run) and 0068 (one driver per host, outcomes pushed); Tailrace's end state for swancloud (agentplot/blueprints `.lavish/tailrace-end-state.html` section 4, the user's decision of 2026-10-26: the push profile first, the deployer retiring after Tailrace's Bolt 6); crew records 0026, 0031, 0036, 0039, 0043, 0044, 0045, 0046; `_open.md`; the user's words above.

## Context and problem statement

crew was built to run bolt teams end to end while the tools around it were still being designed: it makes places, starts and ends stage agents, reads transcripts for stuck and delivered, counts slots, merges and lands through sluice, offers deploys, raises cards and draws the board. Each of those is a mechanism of crew's own. Flume, sluice and Tailrace are now designed, and sluice is built and running, to hold most of them, and the user has said twice that they want the functionality built there, not added to crew. Tonight's records (0043 to 0046) each move one piece, but no page says what crew is at the end, which piece goes where, in what order, and which of crew's stopgaps are worth keeping meanwhile. Without that page each record is a fire put out, and the user is right to withhold a yes until the book exists.

## Considered options

1. crew is the wrapper: it keeps the plan, the give, the readings and the cards for good; every mechanism a tool is designed to hold moves there when that tool holds it, and until then crew changes only by removals, readings and named stopgaps that the move deletes whole (chosen).
2. crew keeps building its own mechanisms, each tool used where convenient. Rejected: the user's words; every mechanism added now is thrown away later and makes the move harder.
3. No change to crew until Flume is built and running. Rejected: Flume has no code yet, and meanwhile teams deadlock on slots and a host melts on waits; the user asked for root-cause fixes today.
4. Flywheel as the plan. Rejected by the user.

## Decision outcome

Option 1.

### What crew keeps for good

crew is the partition's plan and its reading, and the one that asks the user:

- **The plan.** Bolts, units, chores and fixes as records in the state repository; proposals the user approves; the queue; what is given to which team; a bolt shipping alone (record 0042's rejection); a team bound to one bolt (0045). Flume says of itself that planning, ordering, bounding and the record of the work are the caller's.
- **The give and the word.** The dispatcher gives a bolt to a team; a conductor's word starts a stage, holds a stage on an event, merges and submits. Under Flume these are the launch and the retries the callers table gives crew; the words stay crew's.
- **The readings.** The rail, the board, `crew trace`, `crew usage`, the rows' time by holder: what waits on the user, who holds what and since when, read from the records and the tools' own state (`state.4`, read once per refresh on the host's clock).
- **The cards.** The six cards built from facts (0031), a card carrying what a run made (0043), the design agent's records on cards (`briefs.15`), Pending You's wake as the push.
- **The briefs and the signals.** What each agent is told, and the signals' capture and curation.

### What each tool takes

- **Flume** takes the running of work: places and their branches, kinds and stages (a fix, a chore and a unit are kinds), the agent's start and end, prompts, holds on a stage, stuck and lost reads, the settle that moves a place on, what a stage made (flume 0007), the end told to its waiter (flume 0009), tidying. crew launches a place and reads status; it never again reads a transcript for a stage's state, counts slots, or decides a stage is stuck.
- **sluice** takes landing and testing: bolt branches, merges and landings (0026), the gate and its run bound, previews (sluice 0045), the proofs of stages (0039), one driver per host and the outcome pushed to its submitter (sluice 0068). crew records submission numbers on rows, acts on told outcomes, and lands on the user's word.
- **Tailrace** takes releases and deploys: swancloud's deployer retires once Tailrace's push profile holds (the user, 2026-10-26); the offer card, the after-deploy steps and the doctor's rows stay crew's and swancloud's readings.
- **Pending You** carries the cards and wakes the owner.

### The order of the moves

1. **Now, sluice being built and running:** merges and landings through sluice (done); landed read from sluice's record (0044's unit, in flight); stage proofs through `sluice exec` (0039); one driver per host, which swancloud binds as a service, and outcomes pushed and told (sluice 0068, 0046 part 5).
2. **Now, cheap and lasting in crew:** no waiting process of crew's, and a session's start listing its open waits from the records (0046 parts 1 to 4); one follower per host for the rail and board (`plan.12`'s reading); submission numbers on rows.
3. **When Flume's first release runs a kind on a host:** crew launches a unit's, chore's or fix's stages as a Flume place with its stages on hold, and its word is a retry (the callers table, S7); `crew unit wait` is Flume's wait; stuck, lost and delivered are Flume's reads; a team's room is Flume's status (0045 point 5). The slot machinery and the transcript reads leave crew then, whole.
4. **When Tailrace's push profile holds:** the deployer's mechanics leave swancloud; cards and readings stay.

### Stopgaps meanwhile, and the rule for them

A stopgap in crew is allowed only when a team is stuck or a host is burning today, and only as a removal, a reading, or a small change that a move above deletes whole; each is named in the record that calls for it with the move that retires it, and listed in `_open.md` until it leaves. Tonight's: the slot lent to its bolt's fix (0045, leaves at move 3); a held unit's wait on the row (0044, leaves at move 3); submission numbers on rows and the re-wait at a session's start (0046, stays as a reading). Not a stopgap and dropped from 0046: a rewritten stage wait woken by the transcript, which is a new mechanism in crew that move 3 deletes; today's wait stays as it is, ending with its session and started again from the row.

### What could go wrong, and what holds it

- **Stopgaps outliving their reason.** Each is named with the move that retires it and sits in `_open.md`; a move's unit removes them in the same change.
- **Two readers of one fact.** Once Flume runs a place, crew reads only Flume's status for it and never the transcript; once a host binds sluice's driver, no wait of crew's or an agent's runs a round. One owner per fact (`read.1`, `read.2`).
- **Records without the book.** Every record from here says which chapter of this one it is and which move it belongs to; a record that fits none is a question for the user, not a rule.
- **Flume's date.** Flume has requirements and records and no code, so move 3 has no date; the stopgaps are sized for that, and nothing of crew's is removed before the tool that replaces it runs on the host.

## Consequences

- `roles.5` is drawn from this record, marked proposed.
- Record 0046 is revised to this record's reading before its card is asked again: parts 1 to 5 and 7 stand, part 6 names Flume's record 0009 and keeps today's stage wait, ending with its session and restarted from the row.
- `_open.md` gains the four moves and the two stopgaps, each with what retires it.
- Nothing is queued from this record: it orders work the other records call for.
