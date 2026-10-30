---
status: proposed
date: 2026-10-30
decision-makers: the user, flume-sluice-build (the record)
consulted: swancloud (through its operator, once proposed)
---

# 0052. crew is the control plane: repositories are registered there, and a thin runner on each host keeps their clones and views and launches the plan's work into Flume

Status: proposed to the user on 2026-10-30; accepted only on their yes. Nothing is built from it until the user has used Flume on real work and starts the crew refactor (record 0050 part 4), and each piece then has a plan the user approves first.

Deciders: the user, in flume-sluice-build's session on 2026-10-30. On where repositories are kept: "You're showing the repo config in the host config but is that going to need to be in the repo? I'm thinking that ultimately crew or the flywheel will be where you add and maintain repos." On the shape: "I was thinking that if we start to design around the idea of a flywheel control plane and then a local thin flywheel runner per host, we could start to think about crew as our proxy control plane. We could maybe build that thin runner. I'm wondering if you would be in the control plane, connecting your GitHub repo, and then that would get communicated down to the thin runner." On the repositories themselves: "currently SwanCloud manages partitions and teams, sets up the repos in those partitions, clones them, and sets up a clock that syncs them. It would be nice if there was a clean consistent way to do this. It sounds like Flume wouldn't be responsible. It might be the flywheel or a thin adapter that sets up all the bare repos in its local data directory so they are hidden from the user. There would then be a config somewhere where you could set a location on your host for the projected views of their repos." Then on flume-sluice-build's card (req_ee4687bc6fe249dda876): "Yes, write the record now, for your approval". Their words settle the control plane, the runner and who owns the repositories; the rest is flume-sluice-build's, asked on this record's card.

Amends: record 0047 (its option 4, "Flywheel as the plan", rejected 2026-10-28: the user's words above make a control plane and a runner the plan, with crew standing in as the control plane until there is another; what 0047 keeps for crew and gives each tool stands); record 0050 (unchanged: the freeze and the per-team setting carry crew until the teams leave). Asks of swancloud, once accepted: `herdr.13`, `herdr.14` and `names.3` move to the runner, and the spaces' repository lists in `lib/herdr-hosts.nix` leave the machine's configuration.

Sources: flume v0.3.0 (agentplot/flume 99c66b3, record 0020: streams, pools, the host's `[repos]` table naming a repository's stream, `flume launch --stream --priority --intent`); flume's callers table (planning, ordering and the record of the work are the caller's; a place is made in a repository named by its path); swancloud on `origin/main` 2026-10-30: `lib/views.nix`, `lib/space-clone.nix`, `packages/swancloud-views/views.sh`, `docs/architecture/herdr.md` (`herdr.13`, `herdr.14`), `docs/architecture/core.md` (`names.3`), `docs/architecture/testing.md` (a `sluice run` service per repository holding sluice's records); sluice `core.31` (no policy or document of sluice's asks a host for a daemon; a host's `sluice run` is its own choice).

## Context and problem statement

Today a host's repositories are machine configuration. swancloud declares each host's spaces and every space's repositories in Nix (`lib/herdr-hosts.nix`), `space-clone` clones each into the bare-container layout under the space's folder (`names.3`), and the views timer fetches all of them every two minutes, moves each sluice repository's detached anchor to `origin/<default>` and keeps a detached view of each under `~/Code/views/<space>/<repo>` that it moves only while the view is clean and where the timer last put it (`herdr.13`, `herdr.14`). crew's `teams.json` is written by the same configuration. Adding a repository means a swancloud change and a deploy to every host that should keep it.

Partitions and teams are leaving: Flume's streams, pools and queue take the room and the accounts (flume record 0020), and record 0047's move 5 takes the teams out of crew. Once they go, three questions have no owner: where a repository is registered and which hosts keep it, who keeps its clone and the views the user browses, and who on a host turns the plan's work into Flume launches. Flume's own host file has a `[repos]` table naming a stream per repository, but it is the host's file, and a repository registered there exists on one host only and is cloned by nobody.

## Considered options

1. **A control plane and a thin runner per host.** The control plane holds the registry of repositories and the plan; a small program on each host reads what the control plane wants of it, keeps those repositories' clones and views, and launches the work into Flume. crew is the control plane until a flywheel's own exists. Chosen.
2. **swancloud keeps repositories as it does now**, and crew launches into Flume on each host by ssh. Ruled out: a repository is the user's work, not the machine's, and adding one stays a configuration change and a deploy; the machine's configuration would go on naming spaces after partitions have gone.
3. **Flume owns repositories**, cloning and fetching what its host file names. Ruled out by Flume's own design: it makes places in a repository named by its path, and which repositories exist and where they are kept is the caller's.
4. **Each repository registers itself**, in a file of its own. Ruled out: a repository has to be known before anything clones it, and which hosts keep it, and which stream its work runs in on each, are facts about the hosts, not the repository.

## Decision outcome

Option 1, in six parts.

1. **Repositories are registered in the control plane.** The registry names each repository by its forge address, its default branch, the hosts that keep it and, per host, the stream its work runs in. It is a record in the control plane's state, written through the control plane on the user's word, never by an agent's own act. While crew is the control plane, the registry is a record in crew's state repository, written by a crew command as every write there is (`state.1`), and the user connects a repository there.
2. **A runner on each host keeps the repositories registered to that host.** It reads what the control plane wants of its host by pulling, on its own timer and when told, so no inbound connection reaches a host. For each repository it keeps one bare clone in its own data directory, hidden from the user, fetched on that timer over https through the host's credential helper and after a landing it is told of; and one view under the views' root, a setting of the runner's configuration on the host (`~/Code` where it names none), a worktree of that clone detached at `origin/<default>` and never on a branch. A view is moved only while it holds no uncommitted change and stands where the runner last put it, so a view the user moved stays where they put it (the rule `herdr.14` keeps today, carried whole). A repository dropped from the registry is no longer fetched, and its clone and view are removed only once neither holds work the forge lacks; otherwise they are named and left.
3. **Work reaches Flume through the runner.** The control plane decides what runs: the plan, and the user's order on the rail. The runner on the host turns each launch it is given into `flume launch` in its clone of the repository, always naming `--stream`, `--priority` and `--intent`, so a launch never depends on the host's own file; and it carries Flume's ends and status back to the control plane as records. Flume keeps the room, the queue, the places and the stages (record 0047, what each tool takes); the runner counts nothing and decides nothing about a stage.
4. **swancloud keeps the machine and nothing of the work.** It installs the runner, Flume, sluice and herdr, signs in the accounts, and writes Flume's host file, its pools and streams; it no longer lists repositories, spaces or teams, clones, or runs the views timer. The host file's `[repos]` table stays, as a convenience for a launch by hand, and is never where a repository is registered.
5. **The runner is thin.** It keeps clones and views and relays launches and ends; every decision it carries out is the control plane's or Flume's. When a flywheel's control plane exists, it replaces crew behind the same runner, and the runner does not change.
6. **The order.** Nothing of this is built before the user has used Flume on real work and starts the crew refactor (record 0050 part 4); within the refactor, the registry and the runner come before the teams leave (record 0047 move 5), since move 5 needs something to launch into Flume on each host once no conductor does.

### For the plan to settle

Each of these is answered in the plan the user approves before the runner is built; none of them changes the six parts.

- The runner's name and repository, and whether it is a crew command or a program of its own.
- How a launch and an end travel between the control plane and the runner: records in crew's state repository that the runner pulls (recommended, since crew already writes there and no host takes an inbound connection), or something else.
- Whether views are grouped under the root (today `~/Code/views/<space>/<repo>` with a `<space>.code-workspace`) and by what, once spaces have gone.
- How each host's existing containers move under the runner: adopted where they stand or cloned afresh, with the worktrees and sluice's records they hold kept.
- Who starts a repository's `sluice run` on a host: the runner, beside its clone, or swancloud as now, pointed at the runner's clone (`core.31`: the host's choice either way).

### Consequences

- On the yes, `core.md` gains a rule drawn from parts 1 to 5, and `_open.md` lists the runner and the registry under the refactor, before move 5.
- swancloud is asked, through its operator, to record that `herdr.13`, `herdr.14` and `names.3` move to the runner when the runner is deployed, and that the spaces' repository lists and the views timer leave its configuration then; until then nothing on any host changes.
- Nothing is queued from this record.
