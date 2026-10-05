# Tasks

## 1. The teams file

- [x] 1.1 `crew.py` loads `state` (`<owner>/<name>`) on every partition and refuses a file where one lacks it, naming the partition, the field and the machine's configuration as the fix. Add `state` to the test fixtures. Verify with a fixture missing the field, and one with a malformed value.
- [x] 1.2 The harness gains a bare repository for each fixture partition's state, reached as the blueprints remote is. Verify `tests/run` passes with the existing tests pointed at it.

## 2. The write path on the flywheel's branch

- [x] 2.1 `write` targets `<label>/main` of the partition's state repository and hands its change the state at the tip: the plan, and reading and replacing any other file. The commit holds every replaced file; each recutils file is checked with `recfix --check`, the plan with crew's rules. Verify with a test whose change replaces `plan.rec` and `moves.rec`: one commit, both files, and a failing file pushes nothing and names the file.
- [x] 2.2 The commit message ends with `Crew-Entry: <id>`, and the entry written after the push carries that id and the commit. Verify a commit's trailer matches one entry whose `Commit` is that sha.
- [x] 2.3 A flywheel's command fetches and pushes only its own branch. Verify with two fixture partitions sharing one state repository: simultaneous writes both succeed on the first push, and the stub git log shows no fetch of the other's ref.

## 3. `crew state init`

- [x] 3.1 `crew state init <label>`: an existing branch is reported with its commit and nothing written; with no `plan/<label>` anywhere, an orphan commit with an empty `plan.rec`; then `moves.rec` with its descriptor. Verify against the bare remotes that both files pass `recfix --check` and a second run writes nothing.
- [x] 3.2 Adoption: `plan/<label>` of the first blueprints repo is pushed as the branch, so its history is the branch's; a second blueprints repo's plan is appended in one commit naming its source, bare `Source` paths becoming `<owner>/<name>:<path>`; a shared bolt or unit name refuses the init before any push; the first blueprints repo's `signals/moves.rec` records are copied with the commit they were read at. Verify with fixture remotes: the branch's log reaches the plan's first commit, the joined plan holds both sets in order, and the collision case writes nothing.
- [x] 3.3 A run that stops between steps is finished by running it again. Verify by failing the push of the moves step once and rerunning.

## 4. The plan and the moves, read and written there

- [x] 4.1 `plan.py` reads one plan per flywheel from the state branch: `plans`, `locate`, `plan_for` and every command's read. `crew bolts` prints `<label>/main <sha>  <state repository>`; its JSON has one plan per partition. Verify the existing `bolt-plan` tests pass against the state remote, and a fixture partition with kits under two blueprints repos lists them in one plan.
- [x] 4.2 `crew unit add --signal` writes the unit and its `route` move in one commit on the flywheel's branch, its checks rerun on each replay; `crew signal move` appends to the branch's `moves.rec`. Verify that a signal already moved refuses the add with the plan unchanged, and that a route from one host and a drop from another both land.
- [x] 4.3 `plan.rec`'s header says a Source is a path in the flywheel's first blueprints repo or `<owner>/<name>:<path>`. Briefs: `planner.md`, `conductor.md` and `design.md` say the plan and the moves are on the flywheel's branch of its state repository and are written only through crew; `design.md` drops its instruction to pull the blueprints checkout because crew writes moves there. Verify every brief prints for the `wldn` fixture with no unfilled token and no mention of `plan/<label>`.
- [x] 4.4 `README.md` ("The plan" and "Signals" sections, and a "State" section with the layout and `crew state init`), `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew`. Verify every command in the README appears in `crew`'s usage.

## 5. The run record on the branch

- [x] 5.1 Each `write` adds the host's uncarried entries to its commit: the branch's `runs/<host>/<date>.rec` becomes the union by `Id` of the branch's and the host's, and the `.carried` marker advances after the push. Verify a tell's entry reaches the branch with the next plan write, and that carrying twice changes nothing.
- [x] 5.2 `crew events --push` carries with no other change, and makes no commit when there is nothing to carry. Verify both.
- [x] 5.3 `crew events` and `crew trace` read the branch, then each reachable host's entries newer than the branch's newest for that host; an unreachable host is named and shown as far as it had carried. Verify with a simulated host made unreachable after a push: its carried entries are printed.
- [x] 5.4 A host whose local run record was removed after carrying keeps its entries on the branch and adds new ones beside them. Verify with a scratch home wiped between two writes.

## 6. Outside crew

- [x] 6.1 GitHub, with the user's go: create `WilldanGroup/crew-state` and `afterthought/crew-state`, private and empty, readable and writable by the accounts and tokens that today write the blueprints repos' `plan/<label>` branches. Verify `git ls-remote https://github.com/<owner>/crew-state.git` succeeds from mac-studio and from the box.
- [x] 6.2 A decision for the user: confirm `afterthought/crew-state` holds both `madswan` and `swancloud`, knowing madswan's agentplot work is then planned there too.
- [x] 6.3 (Done in swancloud's code, commit 73533a5; waits for the deploy of mac-studio, macbook-pro and the box.) swancloud: `lib/crew-teams.nix` gives every partition a `state`, and the teams file published to each host (`lib/herdr-published.nix`) carries it; the box's GitHub token helper covers the state repositories. Verify `jq '.partitions[].state' ~/.config/crew/teams.json` prints one repository per partition on each host after the deploy.
- [ ] 6.4 The blueprints repos (willdan-blueprints, afterthought/blueprints, agentplot/blueprints), each as a reviewed commit: `signals/README.md` says moves and the plan live in the flywheel's state repository and are written only through crew; `signals/moves.rec` and the `signals/moves.rec merge=union` line in `.gitattributes` are removed. Verify the README names no file the repo no longer has.

## 7. Rollout and proof on real work

- [x] 7.1 With every team idle, run `crew state init wldn`, `madswan` and `swancloud` from the change's branch. Verify `git log` of `wldn/main` reaches "plan: start plan/wldn" of 2026-10-02, and its `moves.rec` holds the two `route` moves of 2026-10-03.
- [x] 7.2 Merge to crew's main, pull on mac-studio, macbook-pro and the box, and restart each partition's main level and teams. Verify `crew bolts --label wldn` on mac-studio and on the box lists the same bolts, units and stages as before the move, under the header `wldn/main`.
- [ ] 7.3 Make one real plan write on each host (for example an order change the planner would make anyway) and one `crew signal move`. Verify each is one commit on `wldn/main` with a `Crew-Entry` trailer and the conductor heard the subject. Then run `crew events --push` on the box, make the box unreachable from mac-studio, and verify `crew trace` of the unit on mac-studio still shows the box's entries.
- [ ] 7.4 With the user's go, delete `plan/wldn`, `plan/madswan` and `plan/swancloud` from the blueprints repos and land task 6.4's commits. Verify `crew bolts` still answers for all three partitions, and a clone of `wldn/main` reads with `recsel -t Unit plan.rec`.
