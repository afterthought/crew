# A unit is merged once its change is archived on the bolt

## Why

crew read a unit merged as soon as its bolt held its change folder, open or archived. In wldn on 2026-10-13 (swb-4, switchboard-kit bolt an-app-like-breadboard-installs-in-the-class), the-deploy-hands-a-stack-its-boundary reached the bolt as copies of its commits inside another unit's merge (8079b54e0); crew read it merged, removed its place and branch (8f52e4927) and never ran its merge stage, so its change stayed open on the bolt and the specs lacked its deltas (signal 2026-10-13-swancloud-planner-45f551aa/01). Record 0027 has a unit's own merge archive its change first, and `teams.17` and `plan.9`, as amended that day, say merged means the bolt holds the change archived.

## What Changes

- **Merged means archived.** A unit reads `merged` only once its bolt holds its change archived. One whose change the bolt holds open, carried there inside another unit's merge, has not merged.
- **A carried unit keeps its place and its merge.** It reads at its own stage, from its place, or, once its place is gone, from its change as the bolt holds it; its slot is not freed and the team's read does not remove its place; `crew status` names it carried by another's merge, its own merge owed, on its slot's line or a line of its own.
- **Its merge archives the change from its own place.** Its merge stage makes its place again from the bolt when it is gone; the merge archives the change there and submits, and delivers once the bolt holds the change archived.
- **The docs say so.** The conductor's and coder's briefs, README, the crew skill and the usage headers.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-plan`: the stage ladder's `merged` is the bolt holding the unit's change archived, and a carried unit reads at its own stage.
- `bolt-teams`: a unit's worktree goes once its bolt holds its change archived; a carried unit keeps its place and slot, is named in the team's status, and its merge makes its place again from the bolt.

## Impact

- `gather.py`: each bolt's read gives the changes it holds archived and the tasks of each it holds open that main does not hold (`opened`, `carried`).
- `plan.py`: `Stages.of`, `slot_stage`, `tidy` and `tidy_over` read merged from the archive; `carried_place`, `carried_units` and `run_check`'s remade place for a merge; `crew.py`'s `holds_said` and `carried_said`.
- Units merged open before record 0027's archive at merge now read at their own stage, their merge owed, in any bolt still in flight: each is merged again through its own merge, which archives its change, before the bolt is offered for landing.

## Touches

```
plugin/lib/gather.py
plugin/lib/plan.py
plugin/lib/crew.py
plugin/roles/conductor.md
plugin/roles/coder.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
README.md
tests/py/test_chores.py
tests/py/test_rail.py
tests/py/test_slots.py
tests/py/test_tidy.py
tests/contract/test_gather.py
tests/t-journey-carried.sh
tests/moon.yml
```
