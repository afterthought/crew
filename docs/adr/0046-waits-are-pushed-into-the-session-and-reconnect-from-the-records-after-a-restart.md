---
status: proposed
date: 2026-10-28
decision-makers: the user, swancloud-design
consulted: madswan-design (sluice's and Flume's pieces), swancloud-planner, swancloud-ops
---

# Waits are pushed into the session and reconnect from the records after a restart

Status: proposed to the user on 2026-10-28, as `briefs.15` has it; accepted only on their yes.

Deciders: the user, through swancloud-ops on 2026-10-28 (signal 2026-10-28-swancloud-ops-4f509aa5/01): "If our records already know about sluice submissions, crew units, and chores, then if we restarted a Claude Code session, it should be able to come back up and reconnect with those watchers (either through the mod or through some instruction)", asking for one design of watchers that push into the agent's session instead of per-agent polling waits, each mechanism placed in Flume, sluice or tailrace where it belongs and else in crew as their wrapper, never forced into a tool, Flywheel not being the plan. Their words settle what they said; the record's other words are the design agent's, asked on this card.
Amends: `teams.22` (a wait is the session's own background command, recorded on the row with its submission number where it has one); gains `teams.24`; the briefs on the yes (every wait a background command; `crew card wait` gone); `state.4`'s reading (a wait is never crew's process).
Sources: the signal, with 2026-10-28-swancloud-ops-cc4c8120/01 and swancloud-planner's measurement of 2026-10-28 (one rail refresh forks 609 processes; nine card waits orphaned 33 hours at a tenth of a core each; `crew unit wait` polls every ten seconds, `crew card wait` every five, `sluice wait` polls and drives the queue); crw-6-conductor's signal 2026-10-28-crw-6-conductor-048267dc/01 (two merges stalled in sluice with no waiter); sluice's README (no daemon; a waiting submit drives the queue; every decision written to plain files, so a crash resumes cleanly) and `sluice wait <number>` from any worktree on any host (plan.21's reading with madswan-design, 2026-10-27); Flume's requirements, clauses 43, 46, 119 and 120, and flume's open question "how a caller learns an end (43, 46)"; swancloud's Pending You wake mod (crew record 0005: an answer wakes its owner's session) and `list_pending` at an agent's start (`roles.md`, the briefs); record 0039 (accepted 2026-10-28: the gate host's standing `sluice run` drives every queue); record 0044 and `teams.22` (a hold is crew's wait on the row); `plan.12`'s reading of 2026-10-28 (a refresh re-reads only what moved; one follower per host); crew's plugin hooks (`plugin/hooks/hooks.json`, SessionStart).

## Context and problem statement

An agent waits for three kinds of event: a sluice submission's outcome, a unit's or chore's stage end, and a card's answer. Today each wait is a process polling on the agent's behalf: `crew unit wait` reads the stage every ten seconds, `crew card wait` asks Pending You every five, and `sluice wait` polls sluice's files and drives its rounds besides. Each belongs to the session that started it and to nobody once that session ends: on 2026-10-28 nine batch waits ran orphaned for 33 hours on deneb, and two merges of crw-6's bolt sat passed in sluice with no waiter to land them. After a Claude Code session restarts, by crew, by herdr or by the user, nothing reconnects: the session comes back cold and learns of its submissions, stages and cards only when told. Beside the waits, per-session watchers (fifty sluice sidebar watchers on deneb) and crew's own followers polled the host into that day's meltdown.

The user asks for one design: events pushed into the session, not polled; a restarted session reconnecting to its waits from the records; and each piece living where it belongs.

## Considered options

1. Every wait is one background command of the session's own that blocks until the event and returns, the harness bringing the session back; every wait recorded where the records hold its subject; a session's start reconnecting from those records by crew's SessionStart hook (the mod) and the brief's instruction; sluice's and Flume's pushes theirs, crew the wrapper (chosen).
2. A crew daemon that watches everything and prompts the sessions. Rejected: `state.4` (crew runs no service), the user's word against kludge in crew, and it would be the one process whose crash loses every wait.
3. The waits as they are, polling, given timeouts. Rejected: the polls are the cost, and nothing reconnects.
4. Flywheel's event bus. Rejected by the user: Flywheel is not the plan.

## Decision outcome

Option 1, in seven parts.

1. **A wait is the session's own background command, and the harness is the push.** An agent that waits on anything starts one command in its session's background that blocks until the event and returns; the session is brought back by its harness at the event and polls nothing itself. crew keeps no waiting process of its own: no `crew card wait`, and no wait that outlives the session that started it; a wait whose session ends ends with it, and the session that comes back starts it again. Everything of this part is crew's, the wrapper.

2. **Every wait is recorded where its subject lives.** A merge's or a landing's submission number is on the bolt's row from the moment of the submit; a stage's wait is on the row with what it waits for and since when (`teams.22`); a card is Pending You's record under its key. Nothing a session waits on is kept only in that session's memory. crew's.

3. **A session's start reconnects.** crew's SessionStart hook, in every crew agent's session, reads that agent's open waits from the records, the rows of its bolt (stages running, submissions out, holds), sluice's queue for its submissions and Pending You for its open cards, and gives the agent the list as crew's notice, each with the command that waits on it again; the brief says to start each as a background command before anything else. The greeting of `crew resume` and `crew up` carries the same list. What crew cannot read it names, and starts nothing for (`read.1`). crew's: the hook is its plugin's, the instruction its briefs'.

4. **A card's answer is pushed by Pending You's wake mod**, as today: the answer wakes the owner's session, which acts on it; after a restart `list_pending` at the start reconnects, and the hook's list carries the cards too. crew reads an answer at the owner's act and at the rail's refresh, never by a wait of its own. swancloud's mod, built; crew's reading.

5. **A submission's outcome is sluice's push.** `sluice wait <number>` in the session's background returns at the outcome, and is resumable by number from any worktree on any host, since sluice keeps every decision in plain files. The queue is driven by the gate host's standing `sluice run` (record 0039), so a session's wait watches and need not drive; a submission whose waiter died is landed by the gate host's rounds and found by the next wait. Asked of sluice, madswan's: a wait that drives no rounds where a run drives the branch, and that blocks cheaply between reads on sluice's own event, never a second-by-second poll. sluice's push; crew's recording and re-wait.

6. **A stage's end is Flume's push.** Whoever waits on a stage learns its end with what was delivered (clause 43), through a Flume command that blocks until the end and is resumable by the place's name from Flume's record; Flume polls nothing between its commands (120), settling when an agent goes quiet, when the merge queue answers or when the terminal's watch runs (46, 119). This answers Flume's open question, how a caller learns an end, from the caller's side; madswan-design writes Flume's own record. Until crew launches through Flume, `crew unit wait` and `crew chore wait` take the same shape in crew's wrapper: a background command that blocks until the stage ends, woken by the transcript's growth and by the host's clock no faster than a minute, never a ten-second poll, recorded on the row and started again from it. Flume's; crew's until then.

7. **Nothing watches per session.** A host runs one follower for the rail and the board (`plan.12`'s reading of 2026-10-28) and one sluice sidebar watcher, with backoff when its stream breaks (madswan's side); a Claude session keeps no watcher of its own. Tailrace carries nothing of this today: a deploy's wait is the deployer's, and tailrace's in the same shape when deploys move there.

## Consequences

- `teams.24` is drawn from this record and `teams.22` amended, both marked proposed; on the yes the briefs say every wait is a background command and name no `crew card wait`.
- crew units on the yes: `a-crew-agents-start-lists-its-open-waits-and-starts-each-again` (parts 2 and 3: the hook, the greeting, the rows carrying every submission number) and `a-stage-wait-wakes-on-the-transcript-and-the-clock` (part 6's wrapper, replacing the ten-second poll).
- The planner's three pieces of 2026-10-28, amended on the yes: the rail unit `a-rail-refresh-after-no-change-reads-nothing` stands as part 7; the chore `a-card-wait-ends-with-its-card-or-its-caller` becomes crew starts no card wait, the answer pushed by the wake mod and read at the act, a wait still running ending with its card or its caller (part 4); the unit `a-merge-whose-waiter-ended-is-waited-on-again-by-its-number` becomes the submission's number on the row from the submit and the re-wait started by the session at its start from the row (parts 2, 3 and 5).
- Asked of madswan-design: sluice's wait that does not drive where a run drives and blocks cheaply; Flume's record answering clauses 43 and 46 with a resumable wait by place.
- Nothing is built in Flywheel.
