# A merge carries no other unit's open change

## Why

In wldn on 2026-10-13 (swb-4), the dependency the-s3-cdn-archetype-lists-what-a-site-with-its-own-api-declares merged its dependent's branch into its own (21770f631), and its merge (8079b54e0) carried the dependent's change onto the bolt open, so the dependent's own merge, which archives its change (record 0027), never ran (signals 2026-10-13-swancloud-planner-51c2c852/01 and 45f551aa/01). The order held (`plan.13`): the dependency merged first, its branch holding the dependent's work as well. `teams.17`, as amended that day, says a unit's or chore's merge is refused before its submission while its branch holds another unit's change open that the bolt does not hold archived, naming the change.

## What Changes

- **A merge that would carry another unit's change is refused.** Before a unit's or chore's merge stage starts, crew reads the changes its branch holds open and refuses it while one is another unit's of the plan that its bolt does not hold archived, naming each.
- **The refusal says what to do.** A unit that comes after the merging one has its work taken out of the branch; any other merges first, its own merge archiving its change, after which the branch's copy is no longer carried.
- **What is not counted.** The unit's own change, which its merge archives; another unit's change its bolt already holds archived, as a dependent's place took it; and a change no unit of the plan has, as the ones main has held open since before archives.
- **The conductor's brief says so.**

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a unit's or chore's merge carries no other unit's open change.

## Impact

- `plan.py`: `merge_carries` reads the branch's open changes on the team's host and the bolt's archived ones as gathered, `carried_in` decides and `carried_refusal` words the refusal; `run_check` and `chore_check` call it for a merge.
- A merge stage now reads one `git ls-tree` more on the team's host.

## Touches

```
plugin/lib/plan.py
plugin/roles/conductor.md
README.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
tests/py/test_stage_rules.py
tests/t-journey-carried.sh
tests/moon.yml
```
