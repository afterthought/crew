# Design

## Context

See proposal.md for why. How a fix works today (`plugin/bin/crew`, the `fix)` case and the slot helpers):

- `crew fix <team> <name> "<words>"` runs on the team's host (`forward`). It reads the team's bolt (`plan _bolt-of`), then sets `fix=fix/$name` and `path=$KIT_DIR/places/fix-$name`. Neither includes the bolt.
- `slot_of "$fix"` looks for a slot of *this* team holding that name. When none does, `take_slot` takes a free slot and writes `<slot> fix fix/<name> <path>` to the team's `slots` file. The file is per team, so a second team never sees the first team's line.
- `plan _place` runs the `PLACE` script (`plan.py`). It **exits 0 when the path already exists** (`[ -d "$path" ] && exit 0`), and **checks out an existing branch as it is** (`git worktree add "$path" "$branch"`), without branching from this team's bolt. This is how swb-3 was given swb-2's worktree.
- `--merge` looks the slot up by `fix/<name>` and recomputes the path from the name.
- `held_obj` builds the run-record object `fix/<bolt>/<name>` from the branch's upstream. `reap` calls `remove_place`, which also recomputes `places/fix-<name>` and deletes the branch `fix/<name>`.
- `slot_stages` (`plan.py`) reads a fix's stage by matching the slot's name to a branch that `gather.kit` found under `refs/heads/fix/` with its worktree directly in `places/`. `crew bolts` and `crew sites` list fixes by branch and match them to a bolt by upstream.
- The run record already names a fix `fix/<bolt>/<name>` (`record.py` KINDS; `README.md` run record section).
- The swb teams share switchboard-kit's single checkout on chuck-herdr-alpha, so they share its `places/` and its `fix/` branches. Bolt names are unique within a partition's plan (`bolt new` refuses a second bolt of the same name).

## Goals / Non-Goals

**Goals:**
- Two teams' fixes never share a branch or a worktree, whatever the conductors name them.
- crew never starts a fix's agent in a worktree that isn't on that fix's own branch, made from its team's bolt.
- Fixes already in flight when this lands can still be merged and cleaned up.

**Non-Goals:**
- Removing worktrees left behind by dropped bolts or merged units (signal `02-worktrees-outlive-their-work`, a separate piece of work).
- Changing how a conductor brings main into its bolt. It stays a fix, and the conductor still names it.
- Moving a fix in flight when its bolt is given to another team.

## Decisions

### The branch and the place include the bolt

The branch is `fix/<bolt>/<name>`, the same as the run record's object. The place is `<kit>/places/fix-<bolt>--<name>`. The double dash separates the bolt from the name, the same way swancloud's `devurl` separates branch and project, so `places/fix-install-never-instance--bolt-takes-main` reads clearly. The place stays directly under `places/`, where `gather.kit` already looks for it.

Bolt names are unique within a plan, and a bolt is held by one team, so a name is unique per kit checkout once it includes the bolt. A conductor can still reuse a name within its own bolt after the earlier fix has merged and been removed. That is what swb-1 does now.

*Alternatives:* including the team (`fix/<team>/<name>`) does not hold when a bolt moves to another team, and the run record already names fixes by bolt. Checking the name against every team's `slots` file on the host would catch the clash but leave the branch names ambiguous in `crew bolts`, `crew sites` and git, and it says nothing about a branch left behind. Asking conductors to use unique names does not work: the name is obvious and recurs, as the record shows.

### A new fix never adopts what is already there

In `crew fix`, when no slot of the team holds the fix, it is new. Before any slot is taken: if the branch `fix/<bolt>/<name>` exists in the kit, or the place exists, refuse with `fix/<bolt>/<name> already has a place at <path> (or a branch) that no slot of <team> holds: name this fix differently`. Leave a `fix.start` entry with `--refused`. Take no slot.

Before any fix agent starts, new or run again, the place must be the fix's own. `git -C <place> branch --show-current` must be the fix's branch, and that branch's upstream must be `bolt/<the team's bolt>`. Otherwise refuse with `<path> is on <branch>, made from <upstream>, not <fix's branch> from bolt/<bolt>: crew starts a fix only in its own place`. The upstream check catches what the branch name alone cannot: an old `fix/<name>` that two teams already share has the right name for both of them, but it tracks only one team's bolt. So swb-3's slot today is refused.

The check lives in `crew fix`, not in the shared `PLACE` script. `PLACE` is also used for units and bolts, where reusing an existing place across stages is correct and a merge stage may be partway through a rebase with no current branch.

### Lookups use what the slot recorded

A slot's line already records the fix's branch (column 3) and place (column 4). `crew fix` (run again, or `--merge`) finds the team's slot by `fix/<bolt>/<name>` first, then by `fix/<name>`. The second lookup finds a fix started before this change. It then takes the branch and place from that line instead of working them out again. `reap` passes the place it already reads from `plan _slots` to `remove_place`, and `remove_place` deletes the branch it was given. `held_obj` returns the name unchanged when it is already `fix/<bolt>/<name>`, and builds the object from the upstream only for an old `fix/<name>`. With these four changes, old and new fixes both work, and no migration step is needed.

### What the record and the briefs say

Run-record objects stay `fix/<bolt>/<name>`. The `Why` of a fix's entries keeps naming the fix by its own name, `fix(<name>): …`, for old and new fixes alike, so a reader sees the name the conductor gave. The conductor's brief gives the new place and says that a name already in use on its bolt is refused, so it should pick another. The coder's brief says its worktree is on `fix/<bolt>/<name>`.

## Risks / Trade-offs

- [A git branch `fix/<x>` and a branch `fix/<x>/<y>` cannot both exist. An old fix named the same as a bolt blocks that bolt's new fixes] → `PLACE` fails with git's own message, which `crew fix` reports and records as refused. The old branch goes when its fix merges, or by hand. No bolt in today's plans has the same name as a fix.
- [Longer place names and branch names in `crew status` and `crew bolts`] → accepted. `devurl` already shortens long names to one DNS label with a hash.
- [Fixes in flight under the old naming still share a place if they already clashed] → the branch check refuses to start an agent there. The user or ops sorts the existing worktree out by hand, which proof step 3 covers.

## Migration Plan

Land, then pull on every host. Conductors read the new brief at their next fresh start or when told. Fixes in flight keep their old branch and place, and merge and are cleaned up as before through the slot's recorded line. Rollback: revert. A fix started under the new naming is then found only by its recorded slot line, which the old code doesn't read, so merge any such fix, or remove it by hand, before reverting.

## Task notes

**1.1** The `fix)` case in `plugin/bin/crew`: `fix=fix/$BOLT/$name`, `path=$KIT_DIR/places/fix-$BOLT--$name`. Do the slot lookup (new name, then `fix/$name`) before deciding new or held. For a held fix, read `fix` and `path` from the slot's line. The run-record objects (`fix/$BOLT/$name`) stay as they are. The `run_stage` call's `what` argument is the branch (it goes into the `stages` file and `slot_stages` matches on it). Check where `run_stage` builds `Why` from `what` so the `Why` stays `fix(<name>)`. Update the usage header line for `crew fix`.

**1.2** Both refusals happen before `take_slot`, so a refused fix takes no slot. Test with two teams that share the test kit (`team_world` has swb-1 and swb-2 on one kit), each given its own bolt, both running `crew fix <team> bolt-takes-main`. Also test a leftover branch with no slot, a held slot whose place was switched to another branch by hand, and a held old `fix/<name>` whose branch tracks another bolt.

**1.3** `reap` reads `slot kind name stage rest` from `plan _slots`, and the place is the last field of `rest`. `remove_place <kind> <name> <path>`: the worktree at the given path, then `git branch -d <name>` for a fix and `unit/<name>` for a unit. `held_obj`: if `$2` matches `fix/*/*`, echo it. In `stage_ends` (`plan.py`), `name[4:]` becomes the part after the last `/`. Test an old fix by writing a `fix/<name>` slot line and its worktree by hand in the test, the way `t-bolts.sh` makes fixtures, then merging it.

**1.4** `plugin/roles/conductor.md`, the fix paragraph: the place is `places/fix-<bolt>--<name>` on `fix/<bolt>/<name>`, and a name already used on its bolt is refused. `plugin/roles/coder.md`, "A fix": the branch. `README.md`, the Teams section's fix sentence. `tests/t-briefs.sh` and `tests/t-docs.sh` may check these texts. Run them.

## Proof on real work

Once the bolt has landed and every host has pulled:

1. On wldn's box, when two swb teams next bring main into their bolts, `crew status swb-<n>` for each shows `fix/<its bolt>/bolt-takes-main`. `ls switchboard-kit/places` shows two `fix-<bolt>--bolt-takes-main` folders, and `git -C <each> branch --show-current` names its own bolt.
2. `crew bolts` lists each fix under its own bolt only.
3. If the swb-3 slot still holds the old, shared `fix/bolt-takes-main` and its place is still there, running that fix again (`crew fix swb-3 bolt-takes-main "<words>"`) is refused, because the branch tracks `bolt/install-never-instance`. The user then frees the slot by hand.
