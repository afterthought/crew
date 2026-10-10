# Design

## Context

See proposal.md for why. Today crew makes and removes worktrees in these places (`plugin/bin/crew`, `plugin/lib/plan.py`):

- **Made.** `bolt_give` makes `<kit>/bolts/<bolt>` on `bolt/<bolt>`. Construct (`plan _run`) makes `<kit>/places/<unit>` on `unit/<unit>`, tracking `bolt/<bolt>`. `crew fix` makes `<kit>/places/fix-<bolt>--<name>` on `fix/<bolt>/<name>`, tracking the bolt. All three go through the `PLACE` script. Every team that builds a kit on a host shares that host's one checkout of it: swb-1 to swb-4 share switchboard-kit on chuck-herdr-alpha, and crew's own checkout on mac-studio has hand-made worktrees (`bolt-teams`, `kickoff`, `checked-capture`, ...) beside `main`.
- **Merged unit or fix.** `reap` runs on every team read (`crew status <team>`, `crew unit run`, `crew fix`). It frees each slot whose work `plan _slots` reads as `merged` or `landed` once its agent is not working, then calls `remove_place`. That runs `git worktree remove` once, without `--force`, and on refusal prints "was kept: it has changes of its own" to stderr. The slot is already free, so nothing tries again. That is what happened to `places/the-real-deploy-finishes-in-the-local-world` (run record: `stage.end … merged` at 02:51:30Z, `slot.free` at 02:52:14Z, and the place still there).
- **Dropped unit.** `op_unit_drop`'s after-step calls `free_slot(remove=True)`, which is `crew _free <team> <unit> --remove` on the team's host. That runs `remove_dropped`: it keeps a worktree with uncommitted changes (`git status --porcelain`), and otherwise removes it and force-deletes the branch, saying the commit the branch was at. A slot whose agent is working is not freed. `crew unit free` frees it later by hand.
- **Dropped bolt.** `op_bolt_drop` changes the plan and has no after-step. Nothing happens on the host: not to the bolt's worktree or branch, nor to its units' or fixes' slots and places. That is what happened to `bolts/one-cfn-lint-pass` (`bolt.give` at 22:25:55Z, `bolt.drop` at 22:28:49Z).
- **Landed bolt.** `bolt_land` writes the plan, then runs `DROP_BOLT` on the host: `git worktree remove "$path" || exit 1`, then `git branch -d`. A refused removal fails the command after the plan has already changed.
- **Requeue.** `op_bolt_drop --requeue` moves the bolt's units to the queue whatever their worktrees. `op_unit_move` refuses to queue a unit that has a worktree ("a queued unit has none").
- `gather.py` lists a checkout's worktrees (`git worktree list --porcelain`) and reads each unit's place, each fix's merged state and each bolt's changes, with git alone. `plan.py` imports nothing from it today but sends its text to hosts.

What git does, from `git help worktree` (git 2.54): `remove` refuses an unclean worktree (untracked files or modified tracked files) **and one with submodules**. `--force` removes both. A locked worktree needs `--force` twice. Ignored files don't make a worktree unclean, and git deletes them with it.

## Goals / Non-Goals

**Goals:**
- One rule decides when any worktree crew made is over. It is applied on every team read and right after the plan writes that end work, so a leftover from any cause, including from before this change, is found again.
- Uncommitted work is never discarded, and a worktree kept for it is named until the user deals with it.
- Nothing crew didn't make is touched.

**Non-Goals:**
- Removing branches left without a worktree. The intent is about worktrees. A branch crew made always goes with its worktree from now on.
- Recording removals in the run record. `slot.free` is already recorded, and the commit a removed branch was at is said in the command's output.
- Stopping a dev server still running from a removed worktree. That is ops' work, and `crew sites` stops listing it.
- Refusing `crew bolt drop` of a bolt with merged units. Its branch goes with the commit said, like a dropped unit's.
- Where a team's conductor and ops sit after their bolt is dropped. They stay in the removed folder until the next `bolt give` restarts them, as after a landing today.

## Decisions

### One tidy, run where the checkout is

A new `plan.py _tidy <team>` runs on the team's host and works on the team's whole kit checkout. It works in this order:

1. **List the checkout's worktrees** (`gather.worktrees`, extended to note `locked`).
2. **Read the slot files** of every team on this host that builds in this checkout.
3. **Read the plans** of every partition whose teams build the kit (`kit_teams` → labels → `plans`).

It lists before it reads, and that order is what makes it safe. The plan always gains a bolt, unit or fix's bolt before crew makes its worktree, and a slot is taken before its place is made. So any worktree in the list was already in a plan, or already held, by the time the plans and slots are read. If any plan can't be read, nothing is removed. Instead it prints one line, `no worktree was removed: <ref> of <repo> could not be read: <why>`.

A worktree is a candidate only when:
- its folder is directly in `<kit dir>/bolts/` and its branch is `bolt/<folder name>`; or
- its folder is directly in `<kit dir>/places/` and its branch is `unit/<folder name>` or starts with `fix/`.

The main checkout, hand-made worktrees and detached ones (a merge stopped partway through a rebase) never match.

A candidate's work is over when:
- **bolt**: no plan has the bolt;
- **unit**: main holds its change (landed), its upstream bolt holds its change (merged), or no plan has the unit;
- **fix**: it has merged into its upstream bolt (the test `gather.kit` already makes, moved into a function both use), or no plan has that bolt. A fix with no upstream is left alone.

A slot holding a worktree, by path or by name, keeps it. Freeing that slot is `reap`'s job.

For each over and unheld candidate:
- **Locked**: kept, with `<path> is kept, and <branch> with it: it is locked`.
- **Uncommitted changes** (`git -C <path> status --porcelain` not empty): kept, with `<path> is kept, and <branch> with it: <its work> is over, and it has uncommitted changes, which are the user's to keep or discard`. `<its work>` is, for example, `unit x has merged into bolt/b` or `bolt b is in no plan`.
- **Otherwise**: `git worktree remove --force <path>`, then `git branch -D <branch>`, printing `<path> and <branch> are removed; the branch was at <short sha>`. That keeps the words `remove_dropped` uses today.

`_tidy` always exits 0. A git failure on one worktree is said and the rest go on.

*Why `--force` after crew's own check:* git's plain `remove` also refuses a worktree with submodules. crew has already checked for uncommitted changes, so `--force` gets past only that. A single `--force` still doesn't remove a locked worktree.

*Why `-D` and the commit said:* a bolt that was dropped, or a unit or fix that was dropped with it, has commits nothing else holds. That is already how `crew unit drop` treats a dropped unit. A merged unit's branch is in its bolt anyway.

*Alternatives:*
- Mending each event (drop, land, merge) on its own would still leave today's leftovers, and anything a missed event leaves. The merged unit on the box was an event that fired and failed.
- Removing with `--force` without the check would discard the user's work, against the user's rule.
- Tidying by team rather than by checkout would never find a dropped bolt's worktree, because the plan no longer ties it to any team.

### reap frees what the plan dropped, then tidies

`slot_stages` gains the stage `dropped`. It is read after `landed` and `merged` have been ruled out, and only when the team's plan was read:
- a unit slot is `dropped` when the plan has no such unit;
- a fix slot is `dropped` when the plan has no bolt its branch tracks.

`reap` frees `dropped` slots as it frees `merged` and `landed` ones, once the agent is not working. It prints `<slot> is free: <name> was dropped from the plan`. While the agent works it prints `<slot> still holds <name>, dropped from the plan: its agent is working; it is freed once that settles`. Then it no longer calls `remove_place`. After its loop it runs `plan _tidy "$TEAM"` once.

A new hidden `crew _tidy <team>` is `load_team; forward; ensure_state; reap`. `remove_place`, `remove_dropped` and `_free --remove` go. `_free` without `--remove` stays, because moves and `free_elsewhere` use it. `crew unit free` keeps its refusals, frees the slot, then runs the tidy.

*Why free the slot when the worktree is kept:* a slot is a place for an agent in flight, and there is none. Holding a slot of four for a stray file would stop the team. The kept worktree is named on every read instead. `crew unit drop` already frees a slot whose worktree it keeps.

### The plan writes that end work tidy at once

`op_unit_drop`, `op_bolt_drop` and `bolt_land` each run `crew _tidy <team>` on the team's host after their write: `crew.on_machine` with `crew_argv`, as `free_slot` does now. They print what it says. If the host doesn't answer, they print `<team>'s host did not answer, so its worktrees for <what> are not removed yet: the team's next read removes them`, and the command still succeeds, because the plan has changed. `op_unit_drop` stops calling `free_slot(remove=True)`. `bolt_land` drops the `DROP_BOLT` script and prints `<bolt> has landed and <team> holds no bolt`, followed by the tidy's lines. `op_bolt_drop` reads the bolt's team before the write, and only a held bolt has a host to tidy.

### Requeue refuses a unit with a worktree

When `--requeue` names a bolt a team holds, `op_bolt_drop` reads the stages of the bolt's units (`stages_for`). For the first unit with a worktree, it refuses with `unit <u> has a worktree at <path>, and a queued unit has none`, the words `op_unit_move` uses. A unit whose stage is `unknown` refuses with `cannot tell unit <u>'s stage: <why>`, as `crew unit drop` does. Inside a proposal, the same check runs at propose and at approve, as for every op.

*Alternative:* removing the requeued units' worktrees would throw away changes, perhaps already approved, that the planner chose to keep for later. Refusing follows the rule crew already has for `unit move`.

## Risks / Trade-offs

- [Teams sharing a checkout (swb-1 to swb-4) each name the same kept worktree on every read, and each conductor could tell the user] → the conductor's brief says to tell the user once, naming the worktree and its work, so the user can see it is the same one.
- [Each team read now fetches the plans of the kit's partitions] → `slot_stages` already fetches the team's plan whenever a unit is in a slot. A small state repository fetches in about a second. Accepted.
- [The commits of a removed branch can be got back only until git prunes them (two weeks by default)] → the commit is printed, and a dropped unit already works this way.
- [A dev server left running from a removed worktree can recreate files at its path] → the folder is then no longer a worktree, so crew never touches it. Ops stops servers for work that is over.
- [A worktree whose folder was deleted by hand still shows in `git worktree list` as prunable] → the tidy skips a candidate whose folder is missing. git prunes such entries itself, and the branch left is a branch-only leftover, outside this change.

## Migration Plan

Land, then pull on every host. The first read of each team after that removes the leftovers in its checkout, including the two on wldn's box, or names them as kept. Conductors, main-level ops and the planner read their new briefs at their next fresh start or when told. Rollback: revert. Worktrees removed meanwhile stay removed, and the commits of their branches were printed.

## Proof on real work

Before this is built, ops reads on wldn's box why git refused `places/the-real-deploy-finishes-in-the-local-world`: `git -C <that place> status --porcelain`, `git -C <switchboard-kit main> worktree list --porcelain` (is it locked?), and whether switchboard-kit has a `.gitmodules`. If the place is clean, submodules are why, and `--force` is what removes it.

Once the bolt has landed and every host has pulled:

1. On wldn's box, `crew status swb-2` removes `bolts/one-cfn-lint-pass` with `bolt/one-cfn-lint-pass`, and `places/the-real-deploy-finishes-in-the-local-world` with its branch. If either has uncommitted changes, crew names it as kept and the user decides. `git -C <switchboard-kit main> worktree list` then lists neither.
2. On mac-studio, `crew status crw-1` leaves crew's hand-made worktrees beside `main` and the bolt crw-1 holds, and removes nothing that is in flight.
3. The next unit that merges on any team has no place left after its conductor's next `crew status`. The next bolt the planner drops has no worktree left on its team's host once the drop returns.

## Task notes

**1.1** `gather.worktrees`: note `locked` (a line `locked` or `locked <reason>`). Move the fix-merged test out of `gather.kit` into a function `fix_merged(main, branch, bolt)` that both use. gather is sent to older hosts, so it keeps to the standard library. `plan.py` can `import gather`, since its own folder is on the path. A candidate whose folder is missing is skipped. Slot files are `~/.local/state/<team>-team/slots` for each team in `fleet["teams"]` whose `machine` is this host and whose `kit.main` is this checkout. Compare candidates with both the slot's name (column 3) and its place (column 4). Messages are as in design.md. Test in a new `tests/t-tidy.sh` (it keeps the `TESTS` first line) with `team_world`, which gives swb-1 and swb-2 one kit:
- a bolt worktree whose bolt is in no plan, removed;
- a merged unit's place that no slot holds, removed;
- a place with an untracked file, kept and named on each read, then removed once the file goes;
- a place with only ignored files, removed;
- a locked worktree, kept;
- a hand-made worktree beside main, and one on `unit/x` outside `places/`, untouched;
- a detached place, untouched;
- an unreadable plan, nothing removed (make the state remote unreachable the way other tests do);
- a held place whose unit is in no plan, untouched.

**1.2** `slot_stages` needs the plan itself, not `marks_of`'s `{}` on failure: read the plan once, and only when it is read does `dropped` apply. For a fix, the bolt is the `bolt` that `kit["fixes"]` gives it. `reap`'s loop matches `merged|landed|dropped`. `crew status` then shows `dropped` in a slot's stage column while its agent works. In `tests/t-unit-free.sh`, the working-agent case now ends with the next `crew status` freeing the slot once the stub says idle. Keep its `crew unit free` cases.

**1.3** In `tests/t-merge.sh`, the merged place still goes on the first idle `crew status`. Add a merged place with a stray file: the slot is freed, the place is kept and named, then removed after the file is removed. `tests/t-fix.sh`: a merged fix's place goes the same way.

**2.1** `op_bolt_drop`: read `team = fleet["teams"].get(b.get("Team"))` before the write. With `--requeue` and a team, check stages as design.md says, outside `change` (the stages read the host), as `op_unit_drop` does. Give the `Op` an `after` that runs `crew _tidy`. In `tests/t-bolt.sh`, give a bolt, construct a unit in it, start a fix on it, then drop the bolt: the bolt's worktree and branch, the unit's place and branch, and the fix's place and branch are gone, and the slots are free. Then check `--requeue` refused for a held bolt with a constructed unit, and allowed for one whose units have no worktree (the existing case).

**2.2** `op_unit_drop`'s after-step and `bolt_land`: as design.md says. In `tests/t-bolt.sh`, land a bolt whose worktree has a modified file: the land succeeds, the plan has no bolt, and the output names the worktree as kept. `tests/t-unit.sh` and `tests/t-unit-free.sh` keep their drop checks, with the messages as they now read.

**3.1** Briefs and docs:
- `plugin/roles/conductor.md`, the paragraph that starts "When the planner drops a unit": the planner may drop a unit or the team's bolt. crew frees the slots and removes the worktrees and branches. A slot whose agent was working is freed by the next `crew status` once it settles. When crew names a worktree as kept for uncommitted changes, tell the user once which worktree it is and what its work was. The changes are the user's to keep or discard, and crew removes the worktree at its first read after they are gone.
- `plugin/roles/main-ops.md` step 5: the bolt's worktree is removed unless it has uncommitted changes, which crew names, and the bolt lands either way.
- `plugin/roles/planner.md`, the drop row or the sentence after the table: `--requeue` is refused while a unit of the bolt has a worktree, so propose dropping that unit, or moving it to another bolt in the same checkout, first.
- `README.md`: the Teams paragraph's sentences on merged and dropped units, and the plan section's `bolt drop`.
- The usage header in `plugin/bin/crew` (`status`, `unit free`) and `plan.py`'s `bolt drop` and `bolt land` lines.

`tests/t-briefs.sh` and `tests/t-docs.sh` check these texts.
