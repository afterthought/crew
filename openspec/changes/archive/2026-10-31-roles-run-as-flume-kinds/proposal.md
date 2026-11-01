# Proposal

## Why

Record 0047's move 6 has no crew role stand: the design agent, the planner, the reviewer, main-level ops and the operator each run on demand, a kind launched on a nudge naming a record, reading the records, acting and ending with its turn, one run at a time per role and partition, the next nudge waiting as a record and the run's start asking for everything untold to the role, so a burst of events is one run (record 0047 move 6, record 0048 pattern 4, record 0049). Today the five stand all day in herdr panes, one set per partition, holding their accounts' context and tokens whether or not anything waits on them, and every handoff to them is a tell typed into a pane that must be up.

The user settled the shape on 2026-10-31, reading records 0047 (moves 5 and 6), 0050 and 0052:

- crew stays the stand-in control plane until a hosted one replaces it: the plan and its approvals, the cards, the rail, board and trace, the roles' briefs, the signals. Nothing new is invested beyond what these changes need.
- A thin runner on each host, in a repository of its own, keeps the clones and views of the repositories its own configuration names, turns the work crew decides into `flume launch --stream --priority --intent`, and carries Flume's ends and status back to crew as records in crew's state repository. crew reads Flume only through the runner. There is no registry of repositories in crew.
- The roles stay, with today's handoffs: design hands solutions to the planner, the planner proposes bolts and changes to them, the user approves. Only the team machinery leaves.
- Each role becomes a kind crew's release carries (`flume launch --kinds`): the role's brief and one stage that reads the records, acts and ends with its turn, launched through the runner when a record names it (an ask from another role or an agent, a card answered, a signal captured, a landing, a tell). Agents doing work make asks of a role, which become such records. Today's standing main-level agents stop once their kind runs.

## What Changes

- crew's release carries a Flume declaration of five kinds, `crew-design`, `crew-planner`, `crew-reviewer`, `crew-ops` and `crew-operator`, each one stage, `turn`, that lands nothing and ends at a turn report, with one prompt beside them (`plugin/flume/`).
- The teams file moves to version 4: every partition's `flume` names each of its five main-level roles `false` while it stands, or the Flume stream its runs run in, as a team's `flume` does in version 3 (`teams-cross-to-flume-as-their-bolts-land`); crew still reads versions 2 and 3, every role standing there. A role moves on the user's word, one at a time, as a team does (`roles.2`, `roles.8`).
- An **ask** is a record on the partition's flywheel branch (`asks.rec`) naming a role: who or what asks, the record it names, and its words. crew writes one wherever it would tell a role that runs as its kind: any `crew tell` to it, crew's own notices to it, `crew send` to the partition's operator, a capture landed through crew (the design agent's), a bolt's landing (the planner's and the design agent's), a card of the role's answered (the follower's card sweep, once per answer), and the user opening the role (`crew role open`). A place the runner's records show waiting on its caller, whose launch request names the role's address as its recipient, is pending for the role the same way: that is how an agent doing work asks a role, by `flume needs`.
- Each role that runs as its kind has a **role record** (`roles.rec`) naming its run's launch: the host, the repository, crew's kinds, the kind, the name, the stream, the priority, the intent, the model and the effort. The runner keeps at most one run of a role, launching it while anything is pending for the role and none stands, and declaring it done once its turn is delivered (the runner's part).
- A run's start, `crew role start`, is the one collector (`roles.7`): it takes everything pending for the role, records the **turn** that took it, and prints the path of the role's brief, filled for its partition as `crew-role` fills it today, and each ask in order. Its end, `crew role end`, records the turn ended and writes the report the stage delivers. What came after the start waits for the next run.
- A run is named as its role's standing agent was, `<label>-<role>`, read from the place crew's launch named, so the plan's role table, the cards' owners and the run record treat it as that role (`roles.1`).
- A role's work that lands, the design agent's records first among it, is a place it launches through the runner with `crew role land`, a `launch` request of Flume's own `chore` kind on the repository's default branch, the role's address its recipient; no role run submits (`roles.7`, record 0048 pattern 5).
- The reviewer is asked a batch by `crew review` and hands its summary back with `crew review delivered`, which records the batch, starts its reading session, raises its card in the planner's name and asks the planner to adopt it; `crew review --wait` refuses for a reviewer that runs as its kind.
- A standing agent of a role that runs as its kind is no longer started: `crew main up` opens no tab for it and ends one still running once it is not working, a standing agent of it is ended at its next stop with no restart, `crew revive` and `crew update` pass it over, and `crew-role` refuses it, naming `crew role open`.
- The views follow (`code.8`): `board.agent_views` and `plugin/hooks/status.js` give a run its band, with what its turn took and what waits for it; the board's attention line names a run that stopped short or was lost, with its place. The rail does not change: an ask waits on a role, not on the user.
- The five briefs say what a turn is: start with `crew role start`, act on what it took, end with `crew role end`, wait in the session on nothing, and ask the user only on a card in the role's own name, never by stopping short.
- README, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage say all of it together (`docs.2`).

Not in this change: launching a team's work, the exchange with the runner, `requests.rec` and the runner's `<label>/runner/<host>` branch, and crew's read of it (`teams-cross-to-flume-as-their-bolts-land`); removing the team machinery (`the-team-machinery-leaves`); the runner itself, which is in its own repository; a bolt's landing moved into Flume.

## Capabilities

### New Capabilities

- `role-runs`: a partition's main-level roles run as Flume kinds crew's release carries, each run launched by the runner while an ask or a place waits on the role, taking everything pending at its start and ending with its turn.

### Modified Capabilities

- `main-level`: the teams file names, for each role, whether it runs as its kind and in which stream; the main level's workspace holds only its standing roles; a tell to a role that runs as its kind is an ask; `crew-role` starts no such role.
- `operator-agent`: the operator may run as its kind; a send to a partition whose operator does is an ask of it.
- `review-batches`: the planner asks the reviewer a batch, and the reviewer's delivery raises the card and asks the planner.
- `rail-cards`: a card's answer reaches a role that runs as its kind as an ask.
- `crew-board`: the agents' views and the attention line show each role that runs as its kind.
- `run-record`: an ask and a turn's begin and end are entries.
- `host-holds-and-updates`: a standing agent of a role that now runs as its kind is ended at its next stop, not restarted.

## Impact

- Code: `plugin/lib/crew.py` (the teams file, `tell`, `launch`, `brief`), `plugin/lib/plan.py` (`agent`, `role`, `main_cmd`, `review_cmd`, `revive_cmd`, `bolt_land`, `signal_land` and the capture writes, the new `role` and `review delivered` commands), a new `plugin/lib/asks.py` for the asks' decisions, `plugin/lib/board.py`, `plugin/lib/hold.py`, `plugin/lib/record.py`, `plugin/hooks/stop`, `plugin/hooks/status.js`, `plugin/bin/crew`, `plugin/bin/crew-role`, the five briefs, and the new `plugin/flume/`.
- State: two new files on every flywheel branch, `asks.rec` and `roles.rec`, written as every write there is (`state.1`).
- The teams file moves to version 4: swancloud's `lib/crew-teams.nix` writes every partition's `flume`, every role `false` until the user moves one, and Flume's host configuration declares each role's stream; crew reads versions 2 to 4, so the deploy and the bump come in either order (record 0050 part 2).
- The runner, `flywheel` from agentplot/flywheel-runner, reads `roles.rec`, `asks.rec` and its turns, launches and keeps one run per role, and records each run's place on its own branch, as design *What this change rests on* lists.
- Tests: logic cases for the asks' decisions, end-to-end journeys for a role's turn on the stubs, the briefs' phrases, the mod's cases.

## Touches

```
plugin/flume/**
plugin/lib/asks.py
plugin/lib/crew.py
plugin/lib/plan.py
plugin/lib/board.py
plugin/lib/hold.py
plugin/lib/record.py
plugin/hooks/stop
plugin/hooks/status.js
plugin/bin/crew
plugin/bin/crew-role
plugin/roles/design.md
plugin/roles/planner.md
plugin/roles/reviewer.md
plugin/roles/main-ops.md
plugin/roles/operator.md
plugin/skills/crew/SKILL.md
plugin/tests/**
README.md
tests/py/**
tests/t-*.sh
tests/lib.sh
tests/moon.yml
tests/stubs/**
```
