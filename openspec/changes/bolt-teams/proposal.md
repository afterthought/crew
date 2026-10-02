# Proposal

## Why

A crew team today builds whole OpenSpec changes one after another on main, with fable designing beside it. Nothing gathers the changes into a body of work that is deployed and tested before it lands, nothing plans across teams, and work found mid-build has nowhere to go but the user's head. The bolt-teams plan (swancloud `openspec/explorations/bolt-teams/plan.md`, with `tracking.md` beside it) moves the swb-1 team onto the Willdan box as the first **bolt team**, and every partition gets a main level that plans the bolts and an operator agent that works for the user. swancloud's companion change `herdr-partitions` gives these their sessions and windows; this change is crew's half.

## What Changes

- **BREAKING** A team builds **bolts**. A bolt is a body of work on branch `bolt/<bolt>` with its worktree at `<kit>/bolts/<bolt>`, built from **units**. A unit is one OpenSpec change on `unit/<unit>` at `<kit>/places/<unit>`, built stage by stage: construct, the user's review, code, verify, then merge into the bolt. Each stage is a fresh agent. The bolt is deployed and tested from its branch, then landed on main.
- **BREAKING** A team's standing roles are its conductor and ops. Fable, the explorer and the verifier go. A team's units in flight run in slots, as many as the team's `units`.
- **The plan.** Each partition keeps one recutils `plan.rec` per blueprints repo, on that repo's `plan/<label>` branch. It holds only intent: bolts and units. Every stage is read from the kits. `crew bolts`, `crew bolt …` and `crew unit …` read and write it, with no service and no merges. A team gets its next bolt with `crew bolt give`, with no edit and no deploy.
- **herdr workspaces per team:** `<team>` for the standing roles and `<team> units` for the units in flight. A session holds several teams.
- **The main level, per partition:**
  - a design agent, which elaborates on main and curates signals;
  - a planner, which plans across the partition's bolts with their conductors;
  - a dispatcher on each host where the partition's bolts run, which allocates that host's work;
  - ops, which lands bolts and deploys main.

  Signals stay in the partition's blueprints repo. Queuing work from a signal is a new `route` move.
- **The operator agent** stands in each operator session. It is started with `crew operator up <label>` and works for the user. It finds what is running with `crew sites` and opens it in terminal-browser.
- **`crew sites`:** every host's bolts and units, with the URL of each running dev server.
- **Agents:** each role is an agent definition, `plugin/roles/<role>.md` in Claude Code's agent format, whose frontmatter sets its model and effort: Opus 5.5 at the effort per role, to start. The teams file can override either for a team or for a partition's main level. The design agent replaces fable.
- **BREAKING** `teams.json` becomes version 2. It gains the partitions and their main levels, `units` replaces `coders`, and `base` goes. swancloud's `lib/crew-teams.nix` follows in its `herdr-partitions` change.

## Capabilities

### New Capabilities

- `bolt-plan`: the plan of bolts and units per partition, the commands that read and write it, and the stage of each unit derived from the kits.
- `bolt-teams`: a team's standing roles, its unit slots and stages, its worktrees, how a bolt is given, deployed, tested and landed, and the team's herdr workspaces.
- `main-level`: a partition's design agent, planner, dispatchers and ops, where they run, and how signals reach the plan.
- `operator-agent`: the standing agent in an operator session, how it is started, and what it does for the user.
- `crew-sites`: the listing of every host's bolts, units and running dev servers, with the URL to open each from.
- `agent-models`: each role's agent definition, the model and effort it sets, and the teams file's overrides.

### Modified Capabilities

(none)

## Impact

- `plugin/bin/crew`, `plugin/bin/crew-role`, `plugin/lib/crew.py`; a new plan module beside `crew.py`
- `plugin/roles/`, each role now an agent definition:
  - `conductor.md`, `ops.md` and `coder.md` rewritten;
  - `construct.md`, `verify.md`, `design.md`, `planner.md`, `dispatcher.md`, `main-ops.md` and `operator.md` added;
  - `fable.md`, `explorer.md` and `verifier.md` removed.
- `plugin/skills/crew/SKILL.md`, `README.md`, `devenv.nix` (recutils)
- The blueprints repos (willdan-blueprints, agentplot/blueprints, a new afterthought/blueprints):
  - a `plan/<label>` branch;
  - the `route` move in `signals/moves.rec` and its README;
  - `signals/moves.rec merge=union` in `.gitattributes`.
- swancloud: `lib/crew-teams.nix` in the version 2 shape, and recutils on every host (its `herdr-partitions` change).
- Running teams keep their sessions until restarted: a brief is read at launch. apk-1 takes the bolt model the next time it is rebuilt.

## Touches

`plugin/bin/crew`, `plugin/bin/crew-role`, `plugin/lib/`, `plugin/roles/`, `plugin/skills/crew/SKILL.md`, `README.md`, `devenv.nix`; in each blueprints repo `signals/moves.rec`, `signals/README.md`, `.gitattributes` and the `plan/<label>` branch.
