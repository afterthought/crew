# Design

## Context

`gather.kit` gave each bolt the changes it holds, open or archived alike (`gather.changes`), and `Stages.of`, `slot_stage` and the tidy read a unit merged when its name was among them. A unit's commits can reach the bolt without its own merge, as copies inside another unit's merge whose branch took them; crew then read it merged, freed its slot and removed its place and branch, and its merge stage, which archives the change (record 0006, record 0027), never ran. `teams.17` and `plan.9`, amended 2026-10-13, say a unit is merged once its bolt holds its change archived, and that one whose change the bolt holds open keeps its place, reads at its own stage with its merge owed, is named in the team's status, and its merge archives the change from its own place, made again from the bolt when it is gone.

The rules this rests on: `teams.1`, `teams.17`, `plan.9`, `plan.13`, `state.2`, `read.1`, `code.7`, `code.8`, `tests.4`, `tests.11`, `docs.2`. Pages whose area this touches: `plan.md`, `teams.md`, `briefs.md`, `tests.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**
- No unit reads merged, loses its slot or loses its place while its change is open on its bolt.
- A carried unit is visible as such, and its own merge archives its change.

**Non-Goals:**
- Stopping a merge from carrying another unit's change: `a-merge-carries-no-other-units-open-change`.
- `landed`, read from main as before: a bolt is offered for landing only once every unit has merged, so a carried unit holds its bolt back until its merge.

## Decisions

### The bolt's read gives archived and open changes apart

`gather.kit` adds to each bolt `archived`, the changes it holds archived, and `open`, the tasks, `[done, total]`, of each change it holds open that main holds neither open nor archived, read from the bolt's tree (`git show bolt/<b>:openspec/changes/<c>/tasks.md`). Main's own open changes are left out: crew's main has held nineteen open since before archives, and every bolt cut from it holds them; none is a unit of the plan. One `git show` per carried change; there is none on a bolt whose units merged as they should.

### A carried unit reads at its own stage

`Stages.of` reads `merged` from `archived` alone. A unit whose change is in the bolt's `open` is marked `carried` and reads its stage by `place_stage`, from its place when it has one and else from `carried_place`, its tasks as the bolt holds them and its planning complete, so with every task ticked it is in `verify` and its merge may start (`stage_refusal`). `slot_stage` reads the same, and gives `True` as a third value for a carried unit, which `holds_said` names; `team_status` adds a line, `carried_said`, for each carried unit of the team's bolts no slot holds (`carried_units`).

### The tidy waits for the archive

`tidy` hands `tidy_over` the bolt's archived changes, so a unit's place is over once its bolt holds its change archived, landed on main, or out of every plan, never while the bolt holds it open (`plan.9`).

### Its merge makes its place again from the bolt

`run_check` for a merge makes the unit's place again, `unit/<unit>` from the bolt, when its stage was read with no worktree, which only a carried unit's merge can be: the place then holds the change as the bolt does, and the merge stage archives it there and submits, as the coder's brief says, delivering once the bolt holds it archived (`delivered`).

### The stage ladder's delta is written on the built ladder

`bolt-plan`'s *A unit's stage is read from the kits* on main still names review stages that `units-build-at-once-and-are-reviewed-in-batches`, built and open on main, took out; this change's delta is written on that change's ladder, so it holds once that change is archived first, which the archive of the changes open on main does in their order.

## Risks / Trade-offs

- [Bolts in flight whose units merged before the archive at merge was built] → Each reads at its own stage with its merge owed, and the bolt is offered for landing only after each unit's merge archives its change: the rule's intent, at the cost of a merge stage per such unit.
- [A carried unit's change with tasks open on the bolt] → It reads `code` and its merge is refused until its tasks are ticked, run again on its place made from the bolt by its code stage.
