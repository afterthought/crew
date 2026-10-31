# Proposal

## Why

Record 0047's move 5 takes the teams out of crew once Flume runs a unit's whole state machine: the conductor, the team's ops, the team, the dispatcher, the slot bound, the give, a team's tells and the fix slot. Record 0050 reaches that move a team at a time: Flume support sits behind a per-team setting in `teams.json`, a team with it off runs today's path unchanged, and the old path leaves crew "in a landing of its own once every team's setting is on" (part 3; `roles.8`). `teams-cross-to-flume-as-their-bolts-land` builds the setting and the path behind it. This change is that landing of its own: once every team has crossed, the old path and the setting itself leave crew whole, so nothing of crew's counts slots, drives a stage, gives a bolt or stands a team agent again.

The user settled the shape around it on 2026-10-31, reading records 0047 (moves 5 and 6), 0050 and 0052:

- crew stays the stand-in control plane until a hosted one replaces it: the plan and its approvals, the cards, the rail, the board and the trace, the roles' briefs, the signals. Nothing new is invested beyond what these changes need.
- A thin runner on each host, in a repository of its own, keeps the clones and views of the repositories its own configuration names, turns the work crew decides into `flume launch --stream --priority --intent`, and carries Flume's ends and status back to crew as records in crew's state repository. crew reads Flume only through the runner. There is no registry of repositories in crew.
- The roles stay, design, planner, reviewer, ops and the operator, with today's handoffs. Only the team machinery leaves: the conductor, team ops, the dispatcher and unit slots.
- A feature branch may hold nested feature branches; Flume has no opinion on a place's base.

## What Changes

- **BREAKING** `teams.json` holds partitions only. Its `teams` list, and the per-team setting with it, leave; the file moves to version 4, after `teams-cross-to-flume-as-their-bolts-land`'s 3, and crew refuses versions 2 and 3, naming the machine's configuration as the fix (`code.5`). A partition's `roles` override names no dispatcher.
- **BREAKING** The team commands leave: `crew list`; `crew status|up|rebuild|close|restart|resume|clear|down <team>`; `crew unit run|wait|free`; `crew chore run|wait|free`; `crew fix`'s slot form, `--merge` and `--wait`; `crew needs`; `crew bolt give`; `crew plan agree`; and the internal `_status`, `_unit-run`, `_unit-wait`, `_fix-run`, `_construct-again`, `_tidy`, `_unit-free`, `_team`, `_dispatch`, `_needs` and `_end-short`. `crew main up` starts no dispatcher, `crew revive` brings back no team agent, and `crew tell` and `crew send` name no team.
- The briefs of the conductor, team ops and the dispatcher leave, and with the unit slots the stage briefs crew gave them, construct, coder and verify: a stage is now a Flume kind's, briefed by the kind and the kit's own files. Every staying brief, the roster and the cards' words name none of them.
- The plan keeps its records and loses the team's part: a bolt is given to no team, so its `Team` field is never written or read; a proposal waits on no conductor's agreement, so `Agreed` is never written; the conductor's and the dispatcher's direct writes leave the role table, and ordering within a bolt is the planner's, by proposal (`roles.1`).
- The three facts a crossed team still gave its bolts get a source with no team: a bolt's work starts by `crew bolt start <bolt>`, the crossed give with no team, which the planner proposes and the user approves; a kit's host, folders and Flume stream come from the runner's own record of what it keeps (one field more asked of the runner's `runner.rec`); `crew fix <bolt> <name> "<words>"` names its bolt, and `crew main fix` its kit alone.
- Every other read crew made through a team takes its fact from where it now lives: a partition's kits from the repositories its plan and its landings name, a partition's hosts from its main level and its kits.
- The run's machinery that lived only for slots and conductors leaves: stage prompts and waits, the stage-end ledger, Touches and overlap notes, forecasts and settles on a conductor's wait, carried units, rebases of dependents, holds and stalls of a team, the team's tidy of places, the slot lent to a fix, the construct handed to a team's host, the branch hint a conductor and ops carried for sluice.
- The views: no slot, conductor, team ops or dispatcher on the rail, the board, the page or any band; `crew board --json` lists no teams and its objects carry no `teams`; a bolt's age runs from the entry that made its branch, not a give; `board.agent_views` and `plugin/hooks/status.js` follow (`code.8`).
- `crew hold` and `crew update` stand down and restart only the main-level roles; the run record gains no slot, stage, fix, give, team or agreement entry, and `crew trace` still reads the ones already on the branch.
- The old path's tests leave; the end-to-end world writes the new teams file; README, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage say all of it together (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: every requirement of a team, its slots, its stages, its fixes, its give, its conductor's waits, its path and crossing and crew's places is removed; what stays is a bolt's branch, its proof and its landing, each read and landed on its kit's host, crew's one worktree a landing's, and the crossed path's launches, answers and fixes, said of a started bolt.
- `main-level`: no dispatcher; the main level's workspace holds its four roles alone; the planner's proposals wait on no conductor; a landing that does not land is held on its row.
- `bolt-plan`: a bolt is created, started, dropped and landed through crew and given to no team; a fix names its bolt and a fix of main its kit; an amendment's construct is handed to no team's host; a conductor hears of no write.
- `plan-proposals`: a bolt in flight changes on the user's approval alone; the other agents' direct writes lose the conductor's and the dispatcher's.
- `operator-agent`: `crew send` reaches a partition's operator by the partition's label alone, and the operator carries to the planner, design or ops.
- `host-holds-and-updates`: a hold and an update reach the main-level roles alone.
- `agent-models`: definitions and overrides for the five standing roles only.
- `chores`: a chore is built as Flume's chore kind, holds no slot, and is written by the planner, design or the user.
- `review-batches`: a batch spans the partition's bolts, reckoned at the rail's sweep on the main-level host; no conductor runs construct again.
- `run-record`: no stage's end is recorded by crew; a landing's age runs from the entry that made the bolt's branch.
- `crew-rail`, `crew-board`, `board-page`, `fleet-page`, `rail-cards`: no team, slot or conductor in a row, a lane, a card or a dock; a question is asked by three roles; the board's JSON lists no teams.
- `kit-toolchain`, `crew-sites`: crew readies no place; sites are listed for each host that keeps a kit.
- `flywheel-state`: a kit's host, its folders there and its work's stream are read from the runners' `runner.rec`; a launch with no stream is refused at a bolt's start.

## Impact

- `plugin/lib/plan.py`, `plugin/lib/runner.py`, `plugin/lib/crew.py`, `plugin/bin/crew`, `plugin/bin/crew-role`, `plugin/lib/hold.py`, `plugin/lib/board.py`, `plugin/lib/cards.py`, `plugin/lib/page.py`, `plugin/lib/gather.py`, `plugin/lib/kit.py`, `plugin/lib/fleet.html`, `plugin/lib/ops.py`, `plugin/lib/record.py`, `plugin/lib/sites.py`, `plugin/lib/transcript.py`, `plugin/hooks/session-start`, `plugin/hooks/stop`, `plugin/hooks/cards`, `plugin/hooks/status.js`.
- `plugin/roles/conductor.md`, `ops.md`, `dispatcher.md`, `construct.md`, `coder.md` and `verify.md` deleted; `design.md`, `planner.md`, `main-ops.md`, `operator.md` and `reviewer.md` edited; `plugin/skills/crew/SKILL.md`, `README.md`.
- Tests in all three tiers and the mod's cases, the end-to-end world in `tests/lib.sh` and `tests/teams.sh`, `tests/moon.yml`.
- Depends on `teams-cross-to-flume-as-their-bolts-land` (the setting and the crossed path, which this change makes the only one), on the runner's record of the repositories its host keeps, with their folders and streams, and on swancloud writing the new teams file in the same deploy as the crew bump that reads it. `roles-run-as-flume-kinds` touches the same launcher, greetings and briefs and builds on none of this change's code, nor this change on its.
- Retires, whole or in part, the rules the design names under *Rules this change retires*; the pages are amended by the design agent after the landing (`docs.7`).

## Touches

```
plugin/lib/plan.py
plugin/lib/runner.py
plugin/lib/crew.py
plugin/lib/hold.py
plugin/lib/board.py
plugin/lib/cards.py
plugin/lib/page.py
plugin/lib/gather.py
plugin/lib/kit.py
plugin/lib/fleet.html
plugin/lib/ops.py
plugin/lib/record.py
plugin/lib/sites.py
plugin/lib/transcript.py
plugin/bin/crew
plugin/bin/crew-role
plugin/hooks/session-start
plugin/hooks/stop
plugin/hooks/cards
plugin/hooks/status.js
plugin/roles/**
plugin/skills/crew/SKILL.md
plugin/tests/**
README.md
tests/py/**
tests/contract/**
tests/t-*.sh
tests/lib.sh
tests/teams.sh
tests/units.sh
tests/stubs/**
tests/moon.yml
```
