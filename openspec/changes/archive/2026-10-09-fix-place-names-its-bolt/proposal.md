# Proposal

## Why

Two teams that build bolts in the same kit checkout can end up working on one fix. On wldn's box, swb-2 (bolt `install-never-instance`) started a fix named `bolt-takes-main` at 17:29:23Z on 2026-10-06, and swb-3 (bolt `the-local-world-finishes-the-real-deploy`) started its own fix of the same name 28 seconds later. Both slots then held `fix/bolt-takes-main`, there was one `places/fix-bolt-takes-main`, and swb-3's code agent was started in swb-2's worktree, on a branch made from swb-2's bolt. Merged from there, swb-3's fix would have carried swb-2's bolt into swb-3's (signal `2026-10-06-swancloud-planner-dc4c1137/01-fix-places-collide-across-bolts`).

Two things together make this happen:

- **A fix's place and branch carry no bolt.** `crew fix <team> <name>` makes the branch `fix/<name>` at `<kit>/places/fix-<name>`. Every team that builds in that kit on that host shares one `places/` folder and one set of branches, and swb-1 to swb-4 all build in switchboard-kit on chuck-herdr-alpha. A unit is safe because the plan refuses a second unit of the same name. A fix has no plan record, so nothing checks its name against anyone else's.
- **crew adopts whatever is already there.** When the place exists, crew uses it as it is, whatever branch it is on. When the branch exists, crew checks it out rather than making a new one from the team's bolt. So the second team got no error, only the first team's work.

The two teams chose the same name because it is the obvious name for routine work. Every time main moves, a conductor brings main into its bolt as a fix, and the conductors call that fix `bolt-takes-main`. The run record shows the name used by swb-1, swb-2, swb-3 and swb-4. swb-1 had already started adding its own suffixes (`-again`, `-c11d672c`, `-proc34`) to avoid clashing with itself. Asking conductors to choose unique names would not be enough. The name has to be made unique by crew.

## What Changes

- **A fix is named within its bolt.** `crew fix <team> <name>` makes the branch `fix/<bolt>/<name>` at `<kit>/places/fix-<bolt>--<name>`, from the team's bolt. The conductor still types only `<name>`. Its run-record object, `fix/<bolt>/<name>`, is unchanged, and the branch now has the same name. Two teams' fixes can share a name and still get different places and branches.
- **crew never starts a fix in a place that isn't its own.** A new fix whose branch or place already exists is refused, with the place named, and the conductor picks another name. A fix in flight that is run again keeps its own place, as it does today. Its agent is started only in a worktree on its own branch, made from its team's bolt. This also stops a fix that two teams already share under the old naming.
- **What a slot records is used.** Merging a fix, freeing its slot and removing its place all work from the place and branch the slot recorded when the fix started, not from a path recomputed from the name. So a fix started before this change, under the old naming, can still be merged and cleaned up with `crew fix <team> <name> --merge`.
- The conductor's and the coder's briefs, `README.md`, the usage header and the `bolt-teams` spec give a fix's new place and branch.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `bolt-teams`: a fix's branch and place include its bolt, and a new fix is refused when its place or branch already exists.

## Impact

- `plugin/bin/crew`: the `fix` command (names, the refusal, the merge's lookup), `held_obj`, `reap` and `remove_place` (the recorded place), the usage header.
- `plugin/lib/plan.py`: `stage_ends`'s fix branch and the `Why` it writes, only where they assume `fix/<name>`.
- `plugin/roles/conductor.md`, `plugin/roles/coder.md`, `README.md`.
- `tests/t-fix.sh`, `tests/t-units-ws.sh`, `tests/t-record-team.sh`, `tests/t-bolts.sh`, `tests/t-sites.sh`.

## Touches

`plugin/bin/crew`, `plugin/lib/plan.py`, `plugin/roles/conductor.md`, `plugin/roles/coder.md`, `README.md`, `openspec/specs/bolt-teams/spec.md` (by delta), `tests/t-fix.sh`, `tests/t-units-ws.sh`, `tests/t-record-team.sh`, `tests/t-bolts.sh`, `tests/t-sites.sh`.
