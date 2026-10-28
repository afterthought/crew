---
status: accepted
date: 2026-10-28
decision-makers: the user, swancloud-design
consulted: madswan-design (sluice and Flume), swancloud-planner, swancloud-ops
---

# The fleet's messages: records are the truth, herdr is the one hub, and a session submits and is told

Status: accepted by the user on 2026-10-28, on their card (req_a2bd279a0778447e8e3d, "Approved").

Amended 2026-10-28: the words are now delivered/pending, collect, notice, recipient, stalled (agentplot/sluice record 0070, agentplot/flume record 0014).

Amended 2026-10-28 by record 0049, accepted by the user: pattern 5 adds that a role's work that lands is a Flume place, and a session's start (pattern 4) is a role run's start.

Deciders: the user, in the design agent's pane on 2026-10-28: "we've got this model now where crew sends messages around using tell and that's working okay. We have a sluice Claude Code mod that, I believe, sends messages to the session itself. It's not clear whether agents are supposed to submit and wait in the background or just submit and then let the mod send messages through. We're talking about sluice running as a daemon and sending messages, and crew doing waits. Stepping back, there's a general topology of message sending: client-server versus broadcast versus hub-sub/pub-sub. I don't know that we've actually sat down and defined the patterns that we should be using. We just keep writing fucking code"; and their note to sluice the same day that sluice must stay a simple CLI and nobody is told to set up a daemon. Their words settle what they said; the patterns below are the design agent's, asked on this card.
Amends: `core.md` gains `roles.6`; record 0046 is revised to this record (one delivery per fact: submit and be told, no background wait beside a push); records 0047, 0046, 0044 and 0031 are read under it.
Sources: `roles.4` (every message between agents goes through `crew tell`, marked), `teams.11` (a tell reaches its agent as a prompt or not at all), `teams.15` (a first message is taken or sent again); crew record 0005 and 0031 (cards, the wake); record 0038 (the board's word, a tell in the user's name); `state.4` and `read.5` (state is files, the run record on the branch); sluice record 0068 as revised (a submission's outcome pushed to its submitter through the host's multiplexer, recorded as told, told again at a session's start; nothing of sluice's need run); flume record 0009 (the settle tells each waiter once into its pane and records it; a caller's start asks for untold ends); flume's clause 120 and sluice's README (no process between commands); the sluice Claude Code and herdr plugins as they are on 2026-10-28 (a sidebar following `sluice overview --watch`; no push into a session yet); Claude Code's own ways into a session (a prompt typed into its pane, a hook's text at start or at a prompt, a background command's return).

## Context and problem statement

Messages reach a Claude Code session today by three roads: text typed into its pane by herdr (`crew tell`, a stage's prompt, the board's word), text a hook injects (Pending You's wake mod, crew's session-start hook), and the harness's return of a background command (`crew unit wait`, `sluice wait`). Facts reach it by a fourth: it reads a record. Three tools are now designing pushes of their own, sluice's outcome, Flume's stage end, crew's waits, and record 0046 as proposed lets a session both wait in the background on a submission and be pushed its outcome: one fact, two deliveries, and nobody has written down which pattern the fleet uses. The user asks for the patterns before more code.

## Considered options

1. Records are the truth and are pulled; every push is a point-to-point nudge to one named session through the host's multiplexer, naming the record; one inbox per session; at-least-once delivery deduplicated by the record's told mark and a start-time ask for the untold; submit and be told; no bus and no daemon required (chosen).
2. A message bus (pub/sub) every tool publishes to and every session subscribes to. Rejected: a second source of truth beside the records, a process to keep alive and restart, and a subscriber that missed a message has nothing to read; the user's word against a daemon.
3. Client-server: a sluice or crew server sessions ask for their outcomes. Rejected: sluice and Flume run nothing between commands by design, and polling a server is the load this week measured.
4. Both pushes and background waits, as 0046 first proposed. Rejected: two deliveries of one fact, and two readers of one state (record 0047).

## Decision outcome

Option 1. Six patterns, each named so a record can say which it uses.

1. **Records are the truth, pulled.** Every fact a session may act on lives in a record anyone reads at any time: sluice's submission files, Flume's place and status, a Pending You card, crew's plan and rows, the run record on the branch (`state.4`, `read.5`). A reading, the rail, the board, a conductor's trace, pulls the records on the host's clock, one follower per host (`plan.12`), and is the only broadcast there is.

2. **A message is a nudge that names a record, never a fact to act on blindly.** What a push carries is which record to read: a submission's number, a place and stage, a card's key, a row. A session that receives one reads the record and acts on what it finds; a lost or doubled nudge costs nothing. crew's tells carry words as well, but a tell that reports an event names the record too.

3. **One inbox per session, one hub.** A Claude Code session has one way in: text in its input, typed into its pane or injected by a hook at its start. Every push is therefore point-to-point to one named session, delivered by the host's multiplexer, herdr, the one hub that knows which pane is which session; a sender names the session, never a pane, and herdr finds it. There is no broadcast push: a tool tells the one session that owns the thing, the submitter, the waiter, the card's owner; everyone else reads the record (pattern 1). Across partitions the same hop is `crew send` to the partition's operator, its one door.

4. **At-least-once, deduplicated by the record.** The sender marks the record told, when and to which session (sluice 0068, flume 0009, Pending You's answer), and a session that starts asks each tool for what is untold to it, which is the reconnect; a duplicate is harmless by pattern 2. crew's read-back of a first message (`teams.15`) is the same guarantee for its own tells.

5. **Submit and be told.** An agent submits, launches or posts, and goes on; the outcome reaches it as a nudge in its pane. A blocking wait in a session's background is the session's own choice, for a command that returns in seconds or a host where nothing runs the queue; it is never used beside a push for the same fact on the same host, and on the fleet's hosts, which run sluice for their queues and will run Flume's settles under herdr's watch, no agent background-waits on a submission or a stage. The harness's return of a background command is a session's private tool, not a delivery path for another tool's facts. On a host Flume runs, a role's own work that lands is a place Flume submits, so no session of crew's submits there (record 0049).

6. **No bus, and no daemon any tool requires.** sluice and Flume run nothing between their commands; what runs continuously is herdr and whatever services the fleet itself chooses to run (the fleet's `sluice run`, swancloud's choice). A tool's push is made by the command that decides the fact, the deciding round, the settle, the wake, through the hub, and the tool is as simple with no fleet around it.

What this settles about today's parts: `crew tell` is pattern 3, kept as it is, with the user's own pane never a tell's inbox (the board's word is how the user reaches an agent, record 0038); the sluice sidebar is pattern 1, a reading, and gains no push of its own; sluice's outcome and Flume's stage end are pattern 3 pushes made by sluice's round and Flume's settle, which the fleet's herdr plugins carry into the pane; Pending You's wake is pattern 3 by the mod; `crew unit wait` and `sluice wait` in an agent's background end as the delivery of those facts once the pushes run on a host (record 0047, moves 1 and 3), the background wait kept only as pattern 5 allows.

## Consequences

- `roles.6` is drawn from this record, accepted with it.
- Record 0046 is revised to it: part 5 and part 6 say submit and be told, no background wait beside a push on the same host; part 3's reconnect is pattern 4.
- Records 0047 (the wrapper), 0044 (holds on the row), 0031 (cards) and 0038 (the board's word) name their patterns at their next amendment; a record from here says which pattern each message it adds uses.
- Asked of madswan-design: sluice 0068 and flume 0009 are read as pattern 3 and 4 already; the one ask is that neither tool's push and the same tool's blocking wait are both offered as delivery on one host, the wait following the push where one runs.
- Nothing is queued from this record; the units of 0046 and 0047 carry it.
