# Design

## Context

Today, crew (`plugin/bin/crew`, `plugin/lib/crew.py`, `plugin/bin/crew-role`) runs a team as one herdr workspace:
- a conductor, ops and fable standing;
- coders and a verifier that hold one whole OpenSpec change each, on `build/<change>` from `base`, made with `wt switch --create`;
- an explorer started for one command.

Every role starts with `--model 'opus[1m]'` (fable with `fable`) and `--effort xhigh`. A brief is a role template filled from `teams.json`. A fresh stage is `/clear` plus a command (`crew opsx`).

The approved plan is swancloud's `openspec/explorations/bolt-teams/plan.md`. The tracking choice, with its comparison and the checks behind it, is `tracking.md` beside it. swancloud's `herdr-partitions` change gives each partition its sessions, its operator sessions and their windows, publishes each session's partition in `herdr-hosts.json`, writes `teams.json`, puts recutils on every host, and calls `crew operator up <label>` when an operator session starts. See proposal.md for why.

## Goals / Non-Goals

**Goals:**
- One bolt per team, built by units whose every stage is a fresh agent at that stage's effort, reviewed by the user before code.
- A plan anyone in the partition can read and change from the command line while bolts run, with no service and nothing kept by hand.
- A main level per partition, an operator agent per operator session, and `crew sites`.

**Non-Goals:**
- Sessions, windows, catalogs and starting the operator agent with its session. Those are swancloud's `herdr-partitions`.
- The signal capture pipeline (the sweep and its adapters), which stays as it is in each blueprints repo.
- More than one shared environment per kit. Bolts deploy into the one there is.
- A team spanning hosts. A team still sits whole in one session.

## Decisions

### The plan is `plan.rec` on `plan/<label>` in each blueprints repo
This is tracking.md's design, with one change. The branch is named for the partition, `plan/<label>`, rather than `plan`. afterthought/blueprints carries both business's and personal's work, and business also uses agentplot/blueprints for agentplot work. A branch per partition keeps each partition's plan its own in a shared repo, and lets one partition read the plans of several repos.

Everything else follows tracking.md:
- the Bolt and Unit schema, enforced by `recfix --check`;
- file order as build order, and `After` as a hard dependency;
- the write path: fetch over https, apply to the tip, check, commit through a temporary index, push without force, replay on rejection up to five times;
- each stage derived from the kits;
- the approval as an empty `Reviewed-by:` commit.

*Alternatives:* tracking.md's comparison weighs the others, with a JSON file edited by `jq` as runner-up. A single `plan` branch per repo was set aside for the reason above.

### `teams.json` version 2
```json
{ "version": 2,
  "partitions": [
    { "label": "wldn", "partition": "clients/willdan", "blueprints": ["willdan-blueprints"],
      "machine": "chuck-herdr-alpha", "session": "wldn-3" } ],
  "teams": [
    { "name": "swb-1", "system": "Switchboard", "machine": "chuck-herdr-alpha", "session": "wldn-1",
      "units": 4, "repos": ["switchboard-kit", "willdan-blueprints"] } ] }
```
- **A team's partition** is its session's partition in `herdr-hosts.json`, so the team does not repeat it.
- **`repos`** stays `[kit, blueprints]`. swancloud's check that a team's repos are in its session's space keeps working, and crew checks that the second repo is one of the partition's blueprints repos.
- **`units`** replaces `coders`.
- **`base`** goes: a unit's base is its bolt, and a bolt's base is main.

crew refuses version 1 with a message naming the fix, never a guess. *Alternative:* keep reading version 1 alongside 2. Rejected: the briefs and roles change together, so an old file cannot describe a bolt team.

### A unit holds one slot through all its stages, and each stage is a new process
A slot `<team>-unit-<n>` is a pane in `<team> units`. `crew unit run <unit> <stage>` works in four steps:
1. It ends whatever runs in the slot, the way `stop` does today.
2. It starts `crew-role <team> unit-<n> <stage>` there, a new `claude` with that stage's brief, effort and working directory.
3. It names the agent.
4. It sends the stage's prompt.

A new process, not `/clear`, is what lets the effort level and the brief change between stages.

*Alternatives:*
- `/clear` in one long session, as `crew opsx` does today. Rejected: it keeps the first stage's effort and brief.
- A separate role for each stage: the old verifier and explorer. Rejected: it multiplies panes, and the plan asks for a fresh agent per stage, not a different seat.

The explorer and the verifier go. A lookup the conductor needs is asked of the design agent.

### Places are made by crew at fixed paths
`crew bolt give` runs `git worktree add <kit>/bolts/<bolt> -b bolt/<bolt> main`. Construct runs `git worktree add <kit>/places/<unit> -b unit/<unit> bolt/<bolt>`. A fix gets `places/fix-<name>` on `fix/<name>` from the bolt. Each new worktree then runs the kit's `crew-prepare` script, as `assign` does now. These paths are tracking.md's layout. Making them with git directly keeps them from depending on worktrunk's path template, and `wt` still works inside them.

The merge stage runs `wt merge bolt/<bolt> --no-squash --no-remove` from the unit's place, so the kit's merge hooks gate it. crew then removes the place and frees the slot. *Alternative:* `wt switch --create` with a path template set in each kit. Rejected: it would spread the layout across every kit's config.

### Status from the work, read once per host
`crew bolts` reads the plan, then reads the kits on each host holding active bolts, all in one `on_machine` call:
- `git ls-tree` of main and of each `bolt/*` for change folders;
- `git worktree list --porcelain`;
- `openspec list --json` in each place;
- the `Reviewed-by` trailers.

The stage rules are those in the `bolt-plan` spec. `crew status` lists the standing roles and each slot with its unit and stage.

### The main level runs where the teams file says
Each partition entry names the machine and session of its main level. The design agent, the planner and the main-level ops are tabs of one workspace, `<label>`, there. The design agent works in the first blueprints repo's main checkout, with the partition's kits added. The planner and the ops work in the same checkout.

A dispatcher runs on each host that has a team of the partition. It runs in the main level's session when that is on the host, otherwise in the session of the host's first team by name, in a workspace `<label> dispatch`. Deriving the dispatcher's place keeps the teams file to what the user decides.

### Signals are written by path and pushed
A finding becomes a signal file in the partition's first blueprints repo, in the shape its `signals/README.md` gives. A `route` move goes into `signals/moves.rec`. crew commits only those paths on that repo's main and pushes over https, pulling with rebase on a rejected push. `signals/moves.rec merge=union` in `.gitattributes` keeps two hosts' appended moves from conflicting, and its `%key: Signal` lets `recfix` catch a signal moved twice. *Alternative:* keep signals on a branch like the plan. Rejected: the sweep and curation already write them on main.

### One model, an effort per role
`crew.py` names the model once, `claude-opus-5-5[1m]`, and the effort per role in one table: the one in the `agent-models` spec, which is plan.md's table with fix and merge added at code's level. `crew-role` reads both, and no brief names a model.

### The operator agent
`crew operator up <label>` runs on the host itself and works in four steps:
1. It finds the session named `<label>` there.
2. It opens or reuses a workspace `operator` in that session.
3. If no agent is up in its pane, it starts `crew-role` for the operator in the session's folder.
4. It names the agent `<label>-operator-<host>`.

The pane takes its account from the session, through swancloud's account shim. The brief carries the partition's label, its blueprints repos, the dispatchers' hosts and the main level's place. terminal-browser is the tool the brief names for showing a site. swancloud calls the command when the session starts; a crew without it is logged and skipped there.

### `crew sites` uses swancloud's naming, not its own
On each host, crew runs `devurl` in each bolt and place to get its names, and reads the host's portless routes to see which are running. Its naming is never re-implemented, so it cannot drift from `modules/home-devurls.nix`. The URL rule is in the `crew-sites` spec.

### Landing is main-level ops'
The team's ops proves the bolt. The main-level ops merges it into main on the user's word, deploys main, then runs `crew bolt land`. That keeps one agent per partition deciding what reaches main, while each team deploys only from its own bolt.

## Risks / Trade-offs

- [Two teams on one kit share one environment] → bolts deploy one at a time. The dispatcher orders the deploys on its host, and a team waits for the environment rather than overwriting it.
- [A stage restart loses the previous stage's context] → that is the point, and the work is in the change and the commits. The conductor's prompt carries only what the stage cannot read.
- [A push race replays a write that no longer makes sense] → each replay checks its preconditions again and refuses with the commit that changed them.
- [Agents everywhere: an operator agent per operator session, a dispatcher per host] → both run at medium effort and wait idle; an idle agent costs nothing.
- [A breaking `teams.json` before swancloud's deploy] → crew is built on a branch and merged to main only once swancloud's deploy has written version 2 (Migration Plan).
- [recutils missing on a host] → crew checks for `recsel` and names the missing package before any plan command.

## Migration Plan

1. Build this change on a `bolt-teams` branch of crew, in its own worktree. The main checkout, which every session loads, keeps today's crew.
2. In the blueprints repos:
   - create the `plan/<label>` branches with `crew plan init`;
   - add `route` to the `Move` enum and the README;
   - add the `merge=union` line;
   - create afterthought/blueprints, which needs the user's go.
3. swancloud's one deploy writes `teams.json` version 2 and puts recutils on every host.
4. Merge `bolt-teams` into crew's main and pull it on every host that keeps a crew checkout. New sessions load it. Running agents keep their old briefs until they are restarted.
5. Move swb-1: give it its first bolt with `crew bolt give swb-1`, and `crew up swb-1` on the box.

Rollback: revert crew's main to the commit before the merge. `teams.json` version 2 then fails to load with a message, until swancloud is reverted too.

## Open Questions

- Which session each partition's main level runs in is swancloud's to write in `lib/crew-teams.nix`. The example uses `wldn-3` for wldn; madswan's and swancloud's would be `madswan-1` and `swancloud-1`.
