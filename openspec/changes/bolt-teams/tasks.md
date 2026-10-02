# Tasks

## 1. The teams file and the agent definitions

- [x] 1.1 A small test harness, `tests/run`, that gives each test a scratch `HOME` holding fixture `teams.json` and `herdr-hosts.json` files, a bare git remote, and stub `herdr` and `ssh` commands that record their calls. Verify `tests/run` passes with no tests.
- [x] 1.2 Add `recutils` to `devenv.nix`, and have every plan command check for `recsel` first and name the missing package. Verify `recsel --version` resolves in the devenv, and a test with `recsel` off `PATH` gets the message.
- [x] 1.3 `crew.py` loads `teams.json` version 2:
  - partitions with their label, partition, blueprints repos and main-level place;
  - teams with `units` and `[kit, blueprints]`;
  - a team's partition taken from its session in `herdr-hosts.json`;
  - optional `roles` overrides on a team or a partition;
  - errors for version 1, a missing field, or a blueprints repo outside the partition.

  Verify with fixtures in `tests/`.
- [x] 1.4 Each role in `plugin/roles/` becomes an agent definition: frontmatter `name`, `description`, `model` and `effort` from the `agent-models` table (`claude-fable-5-1` for the design agent and the planner, `claude-opus-5-5[1m]` for the rest), with the brief as its body. `crew-role` reads the definition, applies a `roles` override from `teams.json`, and starts `claude --model … --effort … --append-system-prompt <filled brief>`. An override naming an unknown role or effort level is refused. Verify a test prints each role's launch arguments, with and without an override.

## 2. The plan

- [x] 2.1 A plan module beside `crew.py`. It reads `plan.rec` from `origin/plan/<label>` of a blueprints repo over https. `crew plan init <blueprints> <label>` creates the orphan branch with the schema header from `tracking.md`. Verify against the bare test remote: `recfix --check` passes on the initialized file.
- [x] 2.2 The write path:
  - fetch, apply to the tip;
  - check with `recfix --check` and crew's rules (the bolt exists in the same repo, `After` stays inside the bolt with no cycle, the unit name is free in the kit);
  - commit through a temporary index;
  - push without force, replaying up to five times on rejection.

  Verify with a test where two writes race: both land in order, and a write whose unit was dropped is refused, naming the commit.
- [x] 2.3 `crew bolt new|give|order|drop|land`, with `give` making `bolt/<bolt>` and `<kit>/bolts/<bolt>` on the team's host, and its refusals. Verify each refusal in the `bolt-plan` spec's scenarios with tests.
- [x] 2.4 `crew unit add|split|order|after|move|drop|approve`. A move rebases a unit that has a worktree. The approval is an empty `Reviewed-by:` commit. Verify each scenario of the `bolt-plan` spec with tests, including the approval surviving a rebase.
- [x] 2.5 Derive each unit's stage from the kits in one `on_machine` call per host, and add `crew bolts [<bolt>] [--json]` with an unreachable host shown as unknown. Verify with a fixture kit holding a unit at each stage, and a squashed merge still reading `merged`.
- [x] 2.6 `crew unit add … --signal <id>`: the unit's source is the signal, and a `route` move is committed by path on blueprints main and pushed. Verify against the test remote that `moves.rec` gains the move and passes `recfix --check`.
- [x] 2.7 Tell a bolt's conductor the subject of any plan write by someone else that touches its active bolt. Verify the stub `herdr` records the prompt to the conductor and none for the conductor's own write.

## 3. Bolt teams

- [x] 3.1 `crew up|down|rebuild|close|restart|resume` act on the conductor and ops only, in a workspace `<team>` with a `conductor` tab and a `git` tab (gitgui in the kit and the blueprints repo). Remove fable, the explorer, the verifier, `assign`, `release` and `opsx`. Verify with the stub `herdr` that `crew up` creates one workspace with those two tabs and starts two agents.
- [x] 3.2 Unit slots, and `crew unit run <unit> construct|code|verify|merge`:
  - a free slot is taken, refused when all `units` are in flight;
  - construct makes `places/<unit>` on `unit/<unit>` from the bolt and runs the kit's `crew-prepare`;
  - each stage ends the slot's agent and starts a new one with the stage's brief and effort, then sends its prompt;
  - code is refused before approval, and verify before every task is ticked.

  Verify each refusal and the launch arguments with the stubs.
- [x] 3.3 The merge stage runs `wt merge bolt/<bolt> --no-squash --no-remove` from the place. When the bolt holds the change, crew removes the place and frees the slot. Verify in a scratch kit that a merged unit reads `merged` and its slot is free.
- [x] 3.4 `crew fix <team> <name> "<what is wrong>"` makes `places/fix-<name>` on `fix/<name>` from the bolt, starts a code agent in a free slot, and merges like a unit. Verify with the stubs and a scratch kit.
- [x] 3.5 `<team> units` workspace: created with the first unit or fix in flight, one tiled pane per slot, closed when the last one frees. `crew status` lists the standing roles and each slot's unit and stage. Verify with the stub `herdr`.
- [ ] 3.6 Briefs:
  - `conductor.md` and `ops.md` rewritten for a bolt team;
  - `construct.md`, `verify.md`, and `coder.md` for code, merge and fix;
  - `fable.md`, `explorer.md` and `verifier.md` removed.

  The conductor's brief:
  - takes units through review with the user;
  - asks design questions of the design agent;
  - records findings outside its bolt as signals;
  - never edits the plan except through crew, and gives up its "no tracking files" rule only for the plan.

  Verify `crew.py brief swb-1 <role>` prints every role with no unfilled token.

## 4. The main level

- [ ] 4.1 `crew main up|down|status <label>`: the `<label>` workspace with `design`, `planner` and `ops` tabs in the main level's session, and a dispatcher in `<label> dispatch` on each host with a team of the partition, placed as design.md says. Verify with the stubs for a partition with teams on two hosts.
- [ ] 4.2 Briefs `design.md` (elaboration on main, curation's five moves, answering conductors, queuing work), `planner.md` (the only writer of bolts and placements, routing signals, agreeing changes with conductors), `dispatcher.md` (giving bolts, starting and stopping teams, watching accounts) and `main-ops.md` (landing and deploying main). Verify each prints for the `wldn` fixture with no unfilled token.
- [ ] 4.3 A finding written as a signal in the partition's first blueprints repo, by path on main, pushed with a rebase on rejection. Verify against the test remote with two hosts appending moves under `merge=union`.

## 5. The operator agent and sites

- [ ] 5.1 `crew operator up <label>` on the host itself: the `operator` workspace in the session named `<label>`, the agent `<label>-operator-<host>` started in the session's folder, nothing done when it is already up, and a non-zero exit naming a missing session or partition. Verify by running it twice with the stub `herdr`.
- [ ] 5.2 `operator.md`: where things stand from `crew bolts`, `crew status` and `crew sites`; requests carried to the planner, the design agent, a dispatcher or a conductor; sites opened in terminal-browser, or the Mac URL given on a box. Verify it prints for the `wldn` fixture.
- [ ] 5.3 `crew sites [<label>] [--json]`: each host's bolts, places and fixes, names from `devurl` run in each worktree, running servers from the host's portless routes, the URL rule of the `crew-sites` spec, and unreachable hosts named. Verify on mac-studio with a scratch kit whose place runs `devurl-serve`.

## 6. Documents and the blueprints repos

- [ ] 6.1 Update `README.md`, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew` to the commands above. Verify every command in the README appears in `crew`'s usage, and none that was removed.
- [ ] 6.2 In willdan-blueprints and agentplot/blueprints:
  - add `route` to the `Move` enum in `signals/moves.rec`, and to the README's move table;
  - change the README's line that work reaches the tracker only through an intent;
  - add `signals/moves.rec merge=union` to `.gitattributes`.

  Verify `recfix --check signals/moves.rec` passes in each.

## 7. Rollout

- [ ] 7.1 After swancloud's deploy writes `teams.json` version 2:
  - run `crew plan init` for each partition's blueprints repos, once afterthought/blueprints exists with the user's go;
  - merge `bolt-teams` into crew's main, and pull it on the box.

  Verify `crew bolts` answers for `wldn`, `madswan` and `swancloud`.
- [ ] 7.2 `crew main up` for each partition, and `crew operator up` in each operator session. Verify each agent is listed in its workspace.
- [ ] 7.3 Move swb-1: plan its first bolt with the planner, `crew bolt give swb-1`, `crew up swb-1` on the box. Verify `crew bolts` shows the bolt active on `chuck-herdr-alpha`.
