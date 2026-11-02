---
status: accepted
date: 2026-10-28
decision-makers: the user
consulted: the design review of crew, Flume and sluice of 2026-10-28
---

# A role is addressed and woken by Flume, its work lands through a place, and move 3 is skipped

Status: accepted by the user on 2026-10-28, in their design session ("i agree with these changes"), on the recommendations R1, R3, R4 and R5 of a review that read crew records 0045 to 0048, Flume records 0002 to 0011 and sluice records 0056, 0065 and 0068 together and drew them as one picture.

Amended 2026-10-28: the words are now delivered/pending, collect, notice, recipient, stalled (agentplot/sluice record 0070, agentplot/flume record 0014).

Deciders: the user; the shape is the reviewing agent's.
Amends: record 0046 parts 4 and 6, record 0047 moves 3 and 6 and the order, record 0048 pattern 5; `core.md` gains `roles.7`; `_open.md`'s moves.
Sources: record 0047 move 6 (no crew role stands; each is a kind Flume launches on a nudge naming a record); record 0048 patterns 3 to 5; record 0046 part 3 (no SessionStart hook of crew's; a launched role's own start asks); flume records 0011 (a kind runs through on its own), 0012 (a submission read at the settles that follow it; the merge queue removes no place) and 0013 (a waiter may be a role's address; an end untold to it wakes the role); agentplot/blueprints `design/flume/requirements.md` clauses 43, 132, C.7, S38 and the callers table's crew row, as amended at 4074bf9; sluice records 0065 and 0068; `state.4`, `roles.5`, `roles.6`.

## Context and problem statement

Record 0047's move 6 has every role run on demand, but no record said what launches a role when nothing of it is running. Every push in the fleet goes to a live session: Flume tells a waiter's pane, sluice pushes into the submitter's session, and Pending You's wake mod wakes the card owner's session. A planner run that launched a bolt's places has ended by the time its first stage asks a question, so the question, a left place and a landing would stand untold with nothing to start the next planner run. Crew cannot start it, since it runs no service (`state.4`), and Flume decides no next step (Flume core.27).

The review found three smaller things beside it. Record 0046 part 3 dropped crew's SessionStart hook, while its parts 4 and 6, and Flume's record 0009 and rule core.25, still named it. Roles that land work of their own, a design agent's records or a planner's plan, submit from their sessions, and under record 0048 pattern 5 no agent on a fleet host background-waits, so nothing removes their landed worktrees (sluice 0065 makes the driver's re-run wait the one remover). And move 3, launching places with every stage held and each started by a retry, is a mode Flume's first build never needs, since that build carries record 0011.

## Considered options

1. Roles addressed and woken by Flume (Flume record 0013); a role's work that lands launched as a place; the four citations of a hook rewritten; move 3 skipped (chosen).
2. A host job of crew's that polls every tool's untold lists and launches roles. Rejected: a standing poller, against `state.4` and `roles.6`.
3. Keep the planner, ops and design standing until a better answer. Rejected: it keeps the tokens and the bottleneck move 6 removes.

## Decision outcome

Option 1, in four parts.

1. **A role is addressed, and Flume wakes it.** crew names every place's waiter by its role's address, `<partition>/<role>`, never by a session. Each role is a kind crew declares, and the host's configuration names it for the address (`[roles."<partition>/<role>"]` with repository, kind and priority, Flume C.7; binding it on the fleet's hosts is swancloud's). A run of the role takes the address as its session's name, so every push to the role reaches the run that is live. Where none is live, Flume launches one: on its own facts, an end untold to the address, inside the settle; and on a carrier's word, `flume wake <address>`, which Pending You's wake mod sends when the card's owner is a role with no live run. One run of an address is live at a time, and its start asks every tool for what is untold to the role (pattern 4), so a burst of events is one run. Nothing of crew's runs between the events (`state.4`).

2. **A role run's start is the one asker.** Where records 0046 and 0048, Flume record 0009 and Flume rule core.25 name "crew's session-start hook", they mean a role run's start: it asks sluice's one command for untold outcomes, Flume's untold list for the address and `list_pending`, before it acts. No hook of crew's is built.

3. **A role's work that lands goes through a place.** A role with work to land, design records, a plan, a brief, launches it as a place of a landing kind, a chore or a change, and Flume submits it, reads the outcome at its settles and tidies the place (Flume record 0012). So on a fleet host no session of crew's submits, nothing waits in a session's background on a submission, and no landed worktree is left. Sluice 0065's re-run `wt submit` wait stays for a person, and for a host with no Flume.

4. **Move 3 is skipped.** Flume's first build carries record 0011, so crew goes from move 2 straight to move 5 when that build runs a kind on a host. The stopgaps sized for move 3, the slot lent to its bolt's fix (0045) and the held unit's wait on the row (0044), leave at move 5.

### Consequences

- `roles.7` is drawn from this record.
- Record 0046 parts 4 and 6 name a role run's start, not a hook. Record 0047 marks move 3 skipped, names Flume as the launcher in move 6, and moves the stopgaps to move 5. Record 0048 pattern 5 says a role's work that lands is a place. Each carries an amendment line naming this record.
- `_open.md`'s moves follow.
- Units at move 6: each role's kind declared in crew; every launch naming its waiter by address; Pending You's wake mod sending `flume wake` for a role with no live run (swancloud's); the host's `[roles]` table on the fleet's hosts (swancloud's).
- Nothing in crew is built before Flume runs on the host (`roles.5`).
