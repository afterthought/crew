# Proposal

## Why

crew keeps a partition's plan on a `plan/<label>` branch of its blueprints repo and its curation moves in that repo's `signals/moves.rec` on main. Both are the machinery's own records, rewritten often, and they sit in the design repository: a branch that is no part of the design, and commits on main that land while people and agents work there, so every checkout lags. The findings-to-design work adds more records of the same kind (an agenda, the planner's proposals, an agent's signals, the run record), and a write that must change two of them at once cannot be one commit while they are in different places.

Flywheel Next keeps such records in a state repository that is the machinery's alone, apart from the blueprints. The user asked for the same here: one special repository, not the blueprints, in which several flywheels (a client's, or two people's) are kept separate (`openspec/explorations/findings-to-design/proposal.md`, section 3; the user named it `crew-state` and accepted a branch per flywheel).

## What Changes

- **A state repository per organisation**, named `crew-state` (`WilldanGroup/crew-state` for wldn). Each partition names its own in the teams file as `state`.
- **A branch per flywheel.** A flywheel is one partition's loop, named by its label. Its state is the files on the branch `<label>/main` of its state repository: `plan.rec`, `moves.rec` and the run record under `runs/<host>/`. Later changes add `proposals.rec`, `agenda.rec` and `signals/` beside them.
- **BREAKING** The plan leaves the blueprints. A flywheel has one `plan.rec`, for all its kits, on its branch of the state repository. `plan/<label>` in a blueprints repo is no longer read or written.
- **BREAKING** Moves leave the blueprints. `crew signal move` and the `route` of `crew unit add --signal` append to `moves.rec` on the flywheel's branch. Queuing a unit from a signal becomes one commit, where it was two in two places.
- **`crew state init <label>`** creates the flywheel's branch. Where the partition has `plan/<label>` branches and moves, it adopts them: the plan's history is carried over, and the moves are copied with the commit they came from.
- **One write path.** Every write is the plan's path today, pointed at the flywheel's branch: fetch, apply to the tip, check, push without force, apply again when someone pushed first. A write may change several files and is still one commit. Each commit's message names its run-record entry.
- **The run record is carried.** Every write to the branch also brings `runs/<host>/` on the branch up to what that host has recorded; `crew events --push` does it on request. `crew events` and `crew trace` read the branch first, then ask each host they can reach for what it has not yet carried, so a host that is asleep or rebuilt loses nothing it had carried.
- **BREAKING** `teams.json`: each partition gains `state`. A partition without it is an error naming the fix, never a default.
- Signals themselves stay where they are in this change, in the blueprints' `signals/`. `checked-capture` moves an agent's signals.

## Capabilities

### New Capabilities

- `flywheel-state`: where a flywheel's records live, how they are written, how flywheels in one repository stay separate, and how a flywheel's branch is created and adopted.

### Modified Capabilities

- `bolt-plan`: a flywheel keeps one plan, in its state repository; writes go to the flywheel's branch; a unit queued from a signal and its `route` move are one commit.
- `main-level`: a partition names its state repository; every move is appended to the flywheel's `moves.rec`.
- `run-record`: the record is carried to the state repository, and gathered from there first.

## Impact

- `plugin/lib/plan.py`: where the plan and the moves are read and written, the write path over several files, `crew state init`. `plugin/lib/crew.py`: the teams file's `state`. `plugin/lib/record.py`: carrying and reading from the branch.
- `plugin/bin/crew`: `state init`, `events --push`. The briefs' `{{PLANS}}` and plan paragraphs (`planner.md`, `conductor.md`, `design.md`), `README.md`, `plugin/skills/crew/SKILL.md`, `tests/`.
- swancloud: `state` for each partition in `lib/crew-teams.nix`, published to every host with the teams file; the box's GitHub credential must reach each state repository.
- GitHub: `WilldanGroup/crew-state` and `afterthought/crew-state` created, private and empty; afterwards the `plan/<label>` branches of the blueprints repos deleted.
- The blueprints repos: `signals/README.md` says moves live in the flywheel's state; `signals/moves.rec` and its `.gitattributes` line go.
- Every host must pull crew together: a crew from before this change still writes `plan/<label>`.

## Touches

`plugin/lib/plan.py`, `plugin/lib/crew.py`, `plugin/lib/record.py`, `plugin/bin/crew`, `plugin/roles/planner.md`, `plugin/roles/conductor.md`, `plugin/roles/design.md`, `plugin/skills/crew/SKILL.md`, `README.md`, `tests/`; the state repositories; in each blueprints repo `signals/README.md`, `signals/moves.rec`, `.gitattributes` and the `plan/<label>` branch.
