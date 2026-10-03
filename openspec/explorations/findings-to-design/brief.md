# Findings to design

A brief for a clean-room design pass. This brief and the files it names are everything you have: don't rely on any earlier conversation.

**The problem.** Agents and people notice things all the time: a conductor while building, the user in an aside to an agent, a meeting, a Discord channel. crew has to carry each one either straight into the plan, when it is clear enough, or into a design session with the user, when it needs a decision first. It also has to record what happened, so that the user can see the flow for themselves instead of asking an agent to piece it together from transcripts and git logs on two hosts.

**Flywheel Next is the model to align with.** It is the long-run design of this same loop: capture adapters, a capture reader, signals, one standing move per signal, curation as a bounded judgment, intent proposals put to the operator, elaborations that work them, findings from sessions offered on the operator's rail, and a run record of every write. Don't rebuild Flywheel Next in crew. Build the simplest version that keeps Flywheel's shapes and vocabulary wherever they fit, so that running crew this way tests Flywheel's ideas on real work. Where crew needs to differ, say how and why.

## Read first

- **Flywheel Next**, the long-run model:
  - its specs, in `~/Code/github_agentplot/flywheel-next/main/openspec/specs/`: `signals/capture-and-curation/spec.md` and `observability/run-record/spec.md`, then the rest as needed;
  - `instructions/` in the same checkout: the capture-reader and curator agents, the signal, move and intent-proposal schemas, and the curator and planner skills;
  - the design, in `~/Code/github_agentplot/blueprints/main`: `books/flywheel/src/how/the-loop.md`, `design/flywheel-next/models/dispatch/captures.md` and `design/flywheel-next/proposals/console-curation.md`. `design/flywheel-next/` holds more: the requirements, the statechart model, the operation captures.

- **crew** (`~/Code/github_afterthought/crew/main`):
  - `README.md`;
  - `plugin/roles/` (conductor, planner, design, dispatcher, main-ops, operator);
  - `plugin/lib/plan.py` (`crew signal`, `crew signal move`, `crew unit add --signal`) and `plugin/bin/crew`;
  - `openspec/changes/bolt-teams/design.md`.
- **willdan-blueprints** (`~/Code/clients/github_willdan/willdan-blueprints/main`, then `git fetch`):
  - `signals/README.md`, which defines captures, signals, moves and the daily sweep;
  - `signals/moves.rec` and `.claude/skills/signal-capture/`;
  - the capture crew wrote on 2026-10-03, `signals/2026-10-03-swb-2-conductor/` on `origin/main`;
  - `plan.rec` on `origin/plan/wldn`.
- **zoetrope** (`gh repo view furkankly/zoetrope`): its `README.md`, `docs/DESIGN.md` and `docs/DISCOVERY.md`. It draws a Claude Code or Codex transcript as a live flow graph, and it adds new formats as providers.

## Invariants

These must be true. Where you think one is wrong, say so and why. Don't drop it quietly.

### Captures and signals

1. A capture is the raw record of one source event: a meeting, a day of a channel, an exchange with an agent, a finding while building. It keeps the source verbatim, or a pointer that fetches it again, together with its provenance: who, where, when, and which agent session.
2. A signal is extracted from a capture. It is one assertion plus the verbatim excerpt it rests on. No signal exists without the capture it came from and an excerpt.
3. Whoever notices something captures it. Deciding what it means is a separate step, done the same way whatever the source.
4. Raw material that carries names, asides or client detail never enters git; that is the `.raw/` rule. A capture in git still lets anyone with access to its source read that source again.
5. A signal never changes. Its relevance is recorded as a move, which is append-only, one per signal.

### Curation and the two lanes

6. Every signal is curated against the design as it stands, in batches, not one by one as it arrives.
7. Curation puts each signal that should lead somewhere into one of two lanes:
   - **plan-ready:** the planner could write the unit's intent without a decision only the user can make. It goes to the planner, which queues a unit from it.
   - **needs the user:** it raises a design question, a tradeoff, or something to investigate. It goes on the design agenda.
8. Nothing reaches the plan without being curated first, whoever noticed it. The one exception is the user telling the planner directly.
9. The planner makes no design decision while turning a signal into a unit. An intent that needs one goes back to the design lane.

### Design sessions

10. The design agenda is a list the user can open at any time. Each item is a proposed intent or a question, with its signals and their weight.
11. A design session is the user and the design agent working through items on the agenda. It is short, and it can happen at any time.
12. What a session decides is recorded as decision records, intents, and units the design agent queues. Each cites its agenda item and that item's signals. The planner places the units in bolts.
13. The design agent's context holds the user's design work, not batches of curation.

### Plan and bolts

14. A bolt has one goal the user would recognize. Work outside that goal goes to the queue or to another bolt.
15. A bolt may live a long time and collect units found along the way, as long as they serve its goal. Adding a unit to a bolt in flight needs its conductor's agreement.

### Seeing what happened

Flywheel's run record (`observability/run-record`) is the model for these.

16. Every crew action that moves work leaves an event: who did it (agent and session), what, to what, when, on which host, and the commit it wrote, if any. Such actions include:
    - capturing, curating, routing;
    - adding, moving and dropping units;
    - adding, giving, landing and dropping bolts;
    - starting and ending a stage, approving;
    - tell, greet, restart.
17. Events are append-only and durable. They survive restarts, and can be gathered from every host.
18. From the events alone, the user can see, for any bolt, unit or signal, what happened in order, who did it, and what it led to, without asking an agent.
19. What the user looks at is a view over the events. The view can be replaced without changing what crew records. zoetrope is one candidate.
20. An agent's Claude transcript remains the detail behind an event: each event points to the session and time it came from.

## Constraints that hold today

- Agents run crew's commands; the user reads and decides.
- The shared records (`plan.rec`, signals, `moves.rec`) are written only through crew. crew writes them straight to GitHub and replays a write when someone else pushed first, so local checkouts lag behind.
- The user reviews every OpenSpec change in full, in plannotator, before it is built.
- Hosts and accounts:
  - herdr 0.9.3;
  - agents run on several hosts and accounts;
  - a partition's teams run on its box or a Mac, and its main level (design agent, planner, ops, dispatchers) on one of them.
- Determinism and simplicity: add only the complexity the invariants need.

## Where today falls short (2026-10-03)

- **No raw source.** `crew signal` writes a capture and its signals in one step. The capture has no raw source and is marked read as it is written. The signal holds the agent's paraphrase with no excerpt. The user's actual words exist only in the conductor's transcript.
- **The design agent was skipped.** A conductor's brief tells it to tell the planner directly. On 2026-10-03 the planner queued two units from signals within a minute, and wrote design choices into their intents. The design agent never saw them.
- **No agenda, no session, no curation runner.** There is no design agenda and no design-session ritual. The daily sweep extracts signals, but nothing in crew runs curation.
- **No event log.** Working out what happened means reading several agents' transcripts and the git logs on two hosts.

## What to produce

A design proposal for the user to review. Write it to `openspec/explorations/findings-to-design/proposal.md` in crew. Don't write code and don't change any repository.

1. For each invariant, the mechanism that makes it true, or the case for changing the invariant.
2. Who does each step: which agent or job, standing or started for one batch, on which host. Say whether curation belongs to the design agent or to its own pass, and why.
3. The records, meaning capture, signal, agenda and event: their shapes and where each lives.
4. How events are seen:
   - the event schema;
   - where events are written, and how they are gathered;
   - how a view reads them. Compare a zoetrope provider for crew's events, events emitted as Claude-format transcripts so zoetrope reads them unchanged, and any better view you know of.
5. Where the design matches Flywheel Next and where it simplifies, and what running crew this way would show about Flywheel's model.
6. The smallest first step that proves the flow end to end, and the order of the steps after it.
7. The alternatives you considered, and the open questions only the user can answer.
