# A fix of a landed bolt is swept with it

## Why

On 2026-10-20 `crew status swb-3` showed four slots still holding fixes from two bolts that had landed (`mains-fleet-build-publishes-a-release`, `a-workload-under-a-path-is-known`), read after read, so a free team read as full; the user freed them by hand with `crew unit free <fix branch>` (signal 2026-10-20-swb-3-conductor-aa121565/01 on wldn; signal 2026-10-20-swancloud-planner-e45386c3/01 on swancloud).

Read on the box the same day, the cause is that crew reads a fix only from its place. Each of those fixes had merged into its bolt, and the bolt had landed: GitHub's main holds every fix branch's tip, and each branch had moved past where it was cut. But their places under `places/` were gone, so the team's read found no fix, called each slot's work `none`, and kept the slot. Their branches stayed too, since crew removes a fix's branch only with its place: the kit holds more than forty `fix/` branches whose bolts are long gone. A fix ends by its merge or with its bolt (`teams.3`), and a slot whose fix has merged or landed is freed (`teams.1`); crew's read could not see either once the place had gone.

A second gap waits behind it. Whether a fix has merged is read against the local `bolt/<bolt>` branch only, and a fix's bolt is read from an upstream that begins `bolt/`. Once bolts live on GitHub (`plan.19`) a fix will track `origin/bolt/<bolt>`, and crew would not know its bolt at all.

## What Changes

- A fix reads **landed** once the kit's main holds its tip and it has moved since it was made, as a unit reads landed once main holds its change; one that never moved reads landed once its bolt is in no plan and main holds its tip. A team's read frees its slot then, as for a fix that has merged.
- A fix is read from its branch when its place is gone, so a slot holding it reads merged, landed or dropped all the same, and is freed.
- A team's read removes a fix's branch that no worktree and no slot holds once that fix has merged or landed, or its bolt is in no plan and main holds its tip: the place and branch of a fix go with its bolt. A branch holding anything main and its bolt lack is left as it is.
- A fix's bolt is the one its branch tracks, local `bolt/<bolt>` or GitHub's `origin/bolt/<bolt>`, and whether it has merged is read against that same ref; when that ref is gone, the fix is read from main alone.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: "Units run in slots" frees a slot whose fix has landed with its bolt, read whether or not its place stands; "A worktree goes when its work is over" removes a landed or merged fix's branch with no place, and reads a fix's bolt from either ref it can track.

## Impact

- `plugin/lib/gather.py`: a fix's facts (its bolt, merged, landed) read from its branch, for each fix's place and for each fix branch with none; `fix_merged` reads the bolt at the ref the fix tracks.
- `plugin/lib/plan.py`: `slot_stage` reads a fix's stage from those facts, place or no place; `tidy_over` and `tidy` end a landed fix and remove a fix branch with no place whose work is over; the drop and the merge's end read merged the same way.
- `plugin/lib/crew.py`: `reaped` says a landed slot's work has landed on main.
- Logic cases in `tests/py/test_tidy.py` (and `tests/py/test_slots.py` where the freeing is pinned), contract cases in `tests/contract/test_gather.py`, a journey case in `tests/t-journey-land.sh`.
- No view changes: the board and the bands draw a fix's place as they do now, and `landed` is already a slot stage they draw (`code.8`).
- Every host takes it with crew's main; the next `crew status` of each team frees what it holds of landed bolts and sweeps their branches.

## Touches

```
plugin/lib/gather.py
plugin/lib/plan.py
plugin/lib/crew.py
tests/py/test_tidy.py
tests/py/test_slots.py
tests/py/test_fix.py
tests/contract/test_gather.py
tests/t-journey-land.sh
tests/t-journey-fix.sh
tests/moon.yml
openspec/specs/bolt-teams/spec.md
```
