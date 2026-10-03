# Design

## Context

See proposal.md for why. The current state, from `bolt-teams` and `run-record`:

- A partition's plan is `plan.rec`, alone on `plan/<label>` of each blueprints repo the partition names. `plan.py` finds a kit's plan through the blueprints repo of the teams that build it (`plan_for`), and reads every plan of a partition for `crew bolts` (`plans`).
- Moves are `signals/moves.rec` on main of the partition's first blueprints repo. `crew unit add --signal` writes the unit on the plan branch and then the `route` move on main: two commits, in two refs, and the second can fail after the first has landed.
- One write path serves both: `land(repo, ref, path, make)` fetches the ref into crew's bare cache (`~/.cache/crew/git/<owner>/<name>.git`), builds a commit through a temporary index, pushes without force, and applies `make` again to the new tip when the push is refused, up to five times. `write` wraps it for the plan and tells the conductors of bolts it touched.
- The teams file (`~/.config/crew/teams.json`, version 2, written by swancloud's `lib/crew-teams.nix`) lists each partition with `label`, `partition`, `blueprints`, `machine` and `session`.
- The run record is local files, `~/.local/state/crew/<label>/runs/<host>/<date>.rec`, gathered over ssh.

Flywheel Next's layout is the model: one state repository per instance (`<instance>/flywheel-state`), the machinery's alone, `main` the shared line, the run record at `runs/<host>/<date>.rec`, every write a commit that carries its reason (`flywheel-next/main/openspec/specs/state-store/git-only-profile/spec.md`, `instance/bootstrap/spec.md`; `blueprints/main/design/flywheel-next/requirements.md` 203, 218, 219). The user's decisions: the repository is named `crew-state`, one per organisation, and several flywheels in it as branches is accepted, readable by everyone with access to the repository.

## Goals / Non-Goals

**Goals:**
- Every record that is the machinery's and not the design's has one home per flywheel, and one write may change several of them atomically.
- A second flywheel for the same client is a new partition entry and a `crew state init`, with no new repository.
- A flywheel's branch can later become the `main` of a repository of its own with its history, which is Flywheel Next's layout.
- The plan's history survives the move.

**Non-Goals:**
- Hiding one flywheel from another. GitHub grants read per repository. A flywheel that must be private gets its own repository; that day `state` gains a branch part, and this change does not build it.
- Moving signals. They stay in the blueprints' `signals/` here; `checked-capture` moves an agent's.
- One file per object, leases, heartbeats or a tick. crew has no engine, and its writes are applied to the tip again, not rebased.
- Reading old `plan/<label>` branches beside the state. After the rollout there is one place.

## Decisions

### One repository per organisation, one branch per flywheel

The partition entry gains `state: "<owner>/<name>"`. The flywheel's branch is `<label>/main`, an orphan line. `wldn` uses `WilldanGroup/crew-state`; `madswan` and `swancloud` use `afterthought/crew-state` (the user confirms this in the rollout; see Open Questions).

A branch per flywheel gives each its own history, which is that flywheel's audit record. A push to `madswan/main` can never be refused because `swancloud/main` moved, crew's cache fetches one ref, and nothing in one branch names another. Pushed as `main` of a new repository, a branch is exactly a Flywheel Next state repository, so the namespace is an interim and costs nothing to leave.

The name ends in `/main` so that further refs of a flywheel can sit beside it later (`<label>/…`); git refuses a ref whose name is a directory prefix of another, so the flywheel's branch cannot be `<label>` itself.

*Alternatives:* a repository per flywheel from the first day is Flywheel's exact layout, at the cost of a repository to create and grant for every partition. A directory per flywheel on one branch makes every flywheel's pushes contend for one ref and interleaves their histories. Branches of the blueprints repo are today's `plan/<label>`, and are what the user asked to leave.

### The files on the branch

```
<label>/main
  plan.rec                 the plan, as today's file
  moves.rec                the Move record set, as today's signals/moves.rec
  runs/<host>/<date>.rec   the run record, as on each host
```

`plan.rec` keeps its header and schema. Its comment line about sources becomes: "A Source is a path in the flywheel's first blueprints repo, or `<owner>/<name>:<path>` in another." `moves.rec` keeps its descriptor (`%key: Signal`, the six-word enum).

One plan per flywheel, where there was one per blueprints repo: a unit already names its kit (`Repo`), `plan.py` already assumes a kit's name is unique within a partition (`kit_teams`), and a write that touches two kits' work is then one commit. `plan_for` and `plans` collapse to "the flywheel's plan".

### The write path takes several files

`write(fleet, label, change, …)` keeps its shape. What it hands `change` grows from the plan to the flywheel's state at the tip: the plan as today, and a way to read and replace any other file on the branch (`moves.rec` here). The commit holds every file the change replaced. Each replaced recutils file is checked with `recfix --check` before the commit, and the plan with crew's own rules, as today. `land` already accepts several paths.

`crew unit add --signal` becomes one `write`: the unit and the `route` move together. `signal_source`'s checks (the signal exists on the first blueprints repo's main, it has no move, the move passes `recfix`) run inside the change, on each replay. `crew signal move` is a `write` that replaces only `moves.rec`.

The commit message is the subject as today, `<subject> (<agent>)`, the body where there is one, and a trailer `Crew-Entry: <id>`. The entry id is made before the commit and written to the host's run record after the push, with the commit's sha.

`crew signal` (a finding) still lands on the blueprints repo's main by path, unchanged, until `checked-capture`.

### `crew state init <label>`

1. Fetch `<label>/main` from the state repository. If it exists, print its commit and stop.
2. If the partition's first blueprints repo has `plan/<label>`: fetch it into the cache and push that commit to the state repository as `<label>/main`. The plan's history is now the branch's.
3. Otherwise make an orphan commit holding `plan.rec` with its header and no records.
4. If a second blueprints repo has `plan/<label>`: one commit appends its Bolt and Unit records to `plan.rec`, in their order, after the first's. A `Source` that was a bare path in the second repo becomes `<owner>/<name>:<path>`. A bolt or unit name both plans hold refuses the whole init before anything is pushed. The message names the repository and commit the records came from.
5. One commit adds `moves.rec`: the descriptor, and every Move record of the first blueprints repo's `signals/moves.rec` on main, with that commit in the message. With no such file, the descriptor alone.

Each step is its own push with the previous step's commit as the expected tip, so a run that stops partway is finished by running it again: every step first checks whether the branch already shows its result. The steps emit `state.init` entries.

Pushing a blueprints commit into the state repository copies only that branch's objects, which are `plan.rec` blobs; nothing of the design goes with it.

*Alternative:* start the branch empty and copy the plan as a file. Rejected: the plan's history since 2026-10-02 is the only record of what was planned when, and one push keeps it.

### The run record on the branch

`write` adds the host's uncarried entries to the same commit. For each local file of the flywheel newer than the last carry (a marker file, `~/.local/state/crew/<label>/runs/.carried`, holds the newest carried `Id`), the branch's `runs/<host>/<date>.rec` becomes the union by `Id` of what the branch has and what the host has, in `Id` order. A host only ever writes under its own name, so two hosts never change the same file and a replay never conflicts on content. The marker is advanced after the push.

`crew events --push` is a `write` with no other change; it does nothing when there is nothing to carry.

The entry for the write in hand is appended after the push, so it rides with the host's next write. `crew events` closes that gap: it reads the branch, then asks each reachable host for entries whose `Id` is newer than the branch's newest for that host. A host that does not answer contributes what it had carried.

`crew events --follow` still tails the hosts; the branch is not polled.

### Reading

Every read of the plan or the moves fetches `<label>/main` into the cache of the state repository and reads at that tip, as today's reads fetch `plan/<label>`. `crew bolts` prints `<label>/main <sha>  <state repository>` where it printed `plan/<label> <sha>  <blueprints repo>`. Its JSON keeps its shape with one plan per partition.

### The teams file

`crew.py` reads `state` on each partition and refuses a file where one is missing: "partition wldn names no state repository (`state`): regenerate teams.json from the machine's configuration." The file stays version 2; the field is required. A team's `repos` are unchanged.

### What must not break

- `crew bolts`, `crew status` and `crew sites` print what they did, but for the plan's header line.
- A conductor still hears the subject of a write to its bolt, and dispatchers of a bolt added, landed or dropped.
- `crew bolt give`, `crew unit run`, approvals and the kits' worktrees are untouched: only where the plan is read from changes.
- The tests' bare remote gains a second bare repository for the state.

## Risks / Trade-offs

- [A host still on the old crew writes `plan/<label>` after the move] → the rollout pulls crew on every host before any agent is started again, and deletes the `plan/<label>` branches, so an old crew fails loudly ("no plan/<label> yet") and cannot write.
- [The box's GitHub credential cannot reach the state repository] → an outside task, checked before the rollout with a `git ls-remote` from the box.
- [Every flywheel in a repository is readable by everyone with access to it] → accepted by the user. A private flywheel gets a repository of its own.
- [The run record makes the branch's history long] → entries ride in commits that were being made anyway, plus explicit `--push` commits; no commit is made per entry.
- [A partition's kits in two organisations share one plan] → that is today's assumption that kit names are unique within a partition, now stated. Init refuses a collision.
- [`moves.rec` leaves the blueprints, where `signals/README.md` and the daily pass's skill mention it] → the blueprints' README is edited in the rollout; the daily pass never wrote moves.

## Migration Plan

1. Build on a `state-repository` branch of crew. Main keeps today's crew.
2. Outside crew: create the state repositories; confirm the box can reach them; swancloud's deploy writes `state` for every partition.
3. With every team idle (no plan write in flight), run `crew state init` for `wldn`, `madswan` and `swancloud` from the branch's checkout.
4. Merge to crew's main and pull on every host. Restart the standing agents so their briefs name the state.
5. Check `crew bolts` shows the same bolts, units and stages as before. Then delete `plan/<label>` in each blueprints repo and remove `signals/moves.rec` there, with the README edit.

Rollback, before step 5: revert crew's main; the old branches are untouched since step 3, less any write made after it, which is copied back by hand from the state branch's log. After step 5, restore `plan/<label>` by pushing the state branch's plan commits back.

## Open Questions

- Which organisation holds madswan's and swancloud's state. `afterthought/crew-state` is assumed; the user confirms it when creating the repositories. Nothing in crew depends on the answer but the teams file's value.
