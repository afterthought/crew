# Design

## Context

`overlapping` walked `plan.units_of(bolt)` in the file's order up to the unit, and `forecasts_due` forecast each live unit against the live units before it in the plan's order. `After` (`plan.13`) orders merging, but neither read it, so a dependency listed after its dependent was told the dependent was ahead (signal 2026-10-13-swancloud-planner-51c2c852/01). `teams.12`, amended 2026-10-13, defines ahead as the bolt's merge order, `After` first and the file's order only among units neither comes after.

The rules this rests on: `teams.12`, `teams.13`, `plan.13`, `code.7`, `tests.4`, `tests.11`. Pages whose area this touches: `plan.md`, `teams.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**
- No overlap note or forecast names a unit's dependent as ahead of it, at any depth of `After`.
- Units neither comes after keep the file's order, as today.

**Non-Goals:**
- Changing which units are forecast at all, or how a conflict is resolved (`teams.13`).
- A total order of a bolt: none is needed, and the pairwise rule is not transitive across unrelated units.

## Decisions

### Ahead is decided pair by pair

`ahead(order, after_of, a, b)`: `b` comes after `a` at any depth, else `a` does not come after `b` and is earlier in `order`. `comes_after` walks `After` names, units' and chores' alike (`plan.13`), through the bolt's whole work, so a chain through a merged unit or a chore still counts. A single sorted order was considered: a stable topological sort can put an unrelated unit before a dependent the file lists first, and the rule's file order among unrelated units would then not hold, since the pairwise relation is not transitive (with `d` after `s` and the file `d, x, s`, `s` is ahead of `d`, `d` of `x`, and `x` of `s`). Each pair is decided once, and exactly one of the two is ahead, so each pair is still forecast once.

### The forecasts and the note read the same rule

`overlapping` keeps the units of the bolt that are ahead of the unit; `forecasts_due` compares each live unit with the live units ahead of it, given the bolt's `After` names by the wait (`bolt_order`), and marks a forecast to put the later unit after the earlier only when it does not already come after it at any depth, so a transitive dependent gets no redundant `After` write.

## Risks / Trade-offs

- [Three unrelated units and a dependent can make each unit ahead of another in a ring] → No decision needs a ring-free order: a forecast is a pair, and the `After` a forecast writes goes from the later of a pair to the earlier, which never closes a cycle, since it is written only when the earlier does not come after the later.
