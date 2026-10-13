# Design

## Context

A unit's or chore's merge submits its branch to its bolt through sluice (`teams.5`), and its merge stage archives a unit's own change first (`teams.17`, record 0006). A branch can hold another unit's work: a dependent's place takes its `After` units' heads (`plan.13`), a later unit merges an earlier one's branch to settle a forecast (`teams.13`), and, as wldn's dependency did on 2026-10-13, a unit can merge one it should not. Nothing checked what a merge carried, so a unit's change reached the bolt open inside another's merge, and its own merge never ran. `teams.17`, amended that day, refuses such a merge before its submission.

The rules this rests on: `teams.5`, `teams.13`, `teams.17`, `plan.11`, `plan.13`, `read.1`, `code.7`, `tests.4`, `tests.11`. Pages whose area this touches: `plan.md`, `teams.md`, `briefs.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**
- No unit's change reaches a bolt inside another unit's or a chore's merge.
- The refusal names the change and what the conductor does.

**Non-Goals:**
- What becomes of a unit already carried: `a-unit-is-merged-once-its-change-is-archived-on-the-bolt`.
- Checking the branch again at the submission itself: the merge agent's work in its place is the bolt taken in by a rebase, which carries nothing the bolt lacks.
- A fix's merge: a fix holds no change (`teams.3`).

## Decisions

### What counts as carried

`carried_in(name, units, opened, archived)`: each change the branch holds open (`ls-tree -d openspec/changes/` on `<kind>/<name>`, the archive left out) that is not the merging unit's own, is a unit's of the plan, and that the bolt does not hold archived. Restricting it to the plan's units leaves out the changes a kit's main has held open since before archives, which every branch from it holds (nineteen on crew's main), and which no merge brings anew. A change the bolt holds open, carried there by an earlier merge, still counts: that unit's own merge is owed, and the merge refused here waits for it.

### The refusal says what to do

`carried_refusal` names each change, and splits them by `After` (`comes_after`, at any depth): a unit that comes after the merging one never merges before it (`plan.13`), so its work is taken out of the branch, by a code stage the conductor words; any other merges first, its own merge archiving its change, after which the branch's open copy is no longer carried.

### Where it is checked

`merge_carries`, called by `run_check` for a unit's merge, after its place is made again when it was carried, and by `chore_check` for a chore's, after the trailer check: it reads the branch on the team's host with `kit_git` and the bolt's archived changes from the survey the stage already read, and refuses with `fail` when the kit was not read (`read.1`). The decision is a logic case; the read, the end-to-end journey's.

## Risks / Trade-offs

- [A sibling merged into a later unit to settle a forecast] → The forecast already put the later unit after the earlier (`teams.12`), so its merge waits for the earlier one's, which archives that change on the bolt, and nothing is refused that would not already wait.
