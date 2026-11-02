# Proposal

## Why

Records 0047 (move 5, amended 2026-10-28 and 2026-10-30) and 0050 settle where crew's teams end and how they get there: when Flume runs a kind's whole state machine, a team's work runs in Flume places with no conductor, team ops or slot, and the fleet moves there one team at a time, behind a per-team setting in `teams.json` that swancloud writes and the user turns on, a team with it off running today's path unchanged (`roles.8`). Flume now runs a change, a chore and a fix through on its own, sending a place back to its code stage on a failed or conflicting submission with sluice's words (flume record 0011), and launches a fix on a base whose own checks went red (flume record 0023). The user settled on 2026-10-31 that a thin runner on each host, `flywheel` from agentplot/flywheel-runner (its record 0001), turns the work crew decides into `flume launch --stream --priority --intent` and carries Flume's ends and status back as records in crew's state repository, and that crew reads Flume only through it.

Nothing in crew yet reads the setting, holds a team back from a new bolt while it finishes its last one on today's path, writes work for a runner, or reads a runner's records. This change is that path: the crossing, one team at a time, with no conversion code. Removing today's path once no team uses it is the sibling `the-team-machinery-leaves`; the roles run as Flume kinds in the sibling `roles-run-as-flume-kinds`.

## What Changes

- `teams.json` gains version 3, where every team names `flume`: `false`, or the name of the Flume stream its work runs in on its host. crew reads version 2 as it does today, every team on today's path, and version 3 with the field required and no default (`code.5`, record 0050 part 2).
- A team's path is read from its setting and the bolts it holds: **today's** while its setting is off; **crossed** while its setting names a stream and it holds no bolt given on today's path; **due** while the two disagree. A team due to cross is given no new bolt; its bolt goes on as given, conductor and all, until it lands or is dropped. That landing or drop crosses it: crew ends its conductor and ops, closes its workspaces and records `team.cross`. A team crosses empty.
- A crossed team's give makes the bolt's branch through sluice as today (`plan.19`), is never refused for the other bolts the team holds (record 0047 move 5 as amended 2026-10-28), starts no agent, and launches the bolt's work whole: one launch request per unit, chore and fix, cut from `bolt/<bolt>`, each carrying its stream, its priority from the plan's order, its intent (the bolt), its recipient (the partition's planner, by address, `roles.7`) and the launches its `After` work must land first.
- crew writes every request for a runner on the flywheel's branch, in `requests.rec`, numbered and append-only, by the same writes as the plan (`state.1`): a launch, a retry with words, a drop, a priority. Each runner writes its answers and Flume's status of each place on a branch of its own, `<label>/runner/<host>` of the partition's state repository, which crew reads and never writes (`state.5`).
- A crossed team's work reads its stage from the runner's records of Flume's status, in `crew bolts`, on the rail and the board and in the agents' bands (`code.8`): launching, waiting on its After work, queued for room, construct, code, verify, needs (with the agent's question), sent back (with sluice's words), submitted, stalled, merged, dropped, refused.
- Plan writes reach a crossed team's places: an added unit or chore is launched; an approved amendment is a retry of construct with the amendment's words, or a fresh launch when its first has not run; a drop drops its place; a reorder of bolts sends the priorities that changed. A move, split or `After` change of work already launched is refused, naming drop and add as the way on.
- `crew answer <work> "<words>"` is the retry that answers a place that stopped short or waits on its caller, the planner's, design's or ops's (record 0047 move 5, flume clause 49).
- `crew fix <team> <name> "<words>"` on a crossed team launches a fix place on the bolt (a review note marked fix among them, flume record 0011). A crossed team's landing that sluice refuses for a conflict with main launches its take-main fix by that read's own act (`plan.8`).
- `crew main fix <kit> <name> "<the failure's words>"` launches a fix of a red main as a fix place on main, its submission held, on the host of a crossed team that builds the kit (record 0047 move 5 as amended 2026-10-30, `state.3`); the kit's landings card carries it as a row, and `crew main fix <kit> <name> --send`, ops's on the user's send, is the retry that submits it. Where no crossed team builds the kit, a red main's fix stays a bolt of one chore.
- A crossed team runs no standing agent and has no slots: `crew up`, `crew unit run`, `crew unit wait` and their kin refuse it, naming where its work runs.
- The dispatcher's, the conductor's, the planner's and main-level ops's briefs, the crew skill, the usage and README say so.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: the teams file's version 3 and its setting; a team's path; a due team given nothing new; the crossing; a crossed team's give, launches, answers and fixes; a crossed team runs no standing agent.
- `flywheel-state`: `requests.rec` on the flywheel's branch, and the runner's branches crew reads.
- `bolt-plan`: a crossed team's work reads its stage from the runner's records; plan writes reach its places.
- `main-level`: a red main's fix is a fix place on main where a crossed team builds the kit.
- `crew-rail`: a crossed team's bolts and a fix of main on the kit's landings row.
- `crew-board`: a crossed team's ledger and the bands from the runner's records.
- `review-batches`: a crossed team's unit enters a batch once its change has landed on its bolt.
- `run-record`: the `team.cross` act and the give's `Path`.

## Impact

- `plugin/lib/crew.py`: `load` reads versions 2 and 3; a team's `flume` setting.
- New `plugin/lib/runner.py`: crew's side of the runner's interface, the requests, the answers and places, and the decisions over them (`code.7`).
- `plugin/lib/plan.py`: the give, the landing and drop's crossing, the plan writes that reach places, `crew answer`, `crew fix` and `crew main fix`, the refusals for a crossed team, `Stages` reading crossed work from the runner, the role table (`may_write`), the state cache's fetch of the runners' branches.
- `plugin/lib/record.py`: the `team.cross` act and the `Path` field.
- `plugin/lib/board.py`, `plugin/hooks/status.js`, `plugin/lib/cards.py` where a landings row is built.
- `plugin/roles/dispatcher.md`, `conductor.md`, `planner.md`, `main-ops.md`; `plugin/skills/crew/SKILL.md`, `plugin/bin/crew`, `README.md`.
- Tests in all three tiers, the mod's cases, two new end-to-end tests, `tests/moon.yml`.
- Depends on, outside this change: the runner's crew implementation (agentplot/flywheel-runner); swancloud's version-3 `teams.json`, Flume's streams on each host and the runner's install; `roles-run-as-flume-kinds` for an end told to a role's address to wake the role. `the-team-machinery-leaves` depends on this change.

## Touches

```
plugin/lib/crew.py
plugin/lib/runner.py
plugin/lib/plan.py
plugin/lib/record.py
plugin/lib/board.py
plugin/lib/cards.py
plugin/hooks/status.js
plugin/roles/dispatcher.md
plugin/roles/conductor.md
plugin/roles/planner.md
plugin/roles/main-ops.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
README.md
tests/py/**
tests/contract/**
tests/t-journey-cross.sh
tests/t-journey-main-fix.sh
tests/t-*.sh
tests/lib.sh
tests/stubs/**
tests/moon.yml
plugin/tests/**
```
