# Design

## Context

See proposal.md for why, and for the user's ruling this implements. The current state, after `unit-amendments`, `checked-capture` and `curation-and-agenda`:

- A finding is `crew signal <slug> "<assertion>" --excerpt "<words>"`: a capture and a signal written in one commit on the flywheel's branch, the capture naming the team, bolt and unit the agent was working in. The agent tells nobody.
- A signal is unmoved until a curator's delivery, or a person's hand (`crew signal move`, `crew agenda add`), gives it a standing move. `route` and `join` target an agenda item; `attach`, `challenge`, `answered` and `drop` lead nowhere. The user may replace or revive a move.
- An item closes `planned` (a proposal that adds a unit from it was approved), `decided` with results (decision records, units) or `dropped`.
- The planner changes the plan only by an approved proposal; the design agent queues units with `--item`. A unit added from an item carries `Source: agenda/<n>`.
- A unit in flight can be sent back through construct and review at any stage before merge, and the plan may carry a mark on a unit (`Amended`). The plan holds "what is meant to be built and any hold on it".
- `After` names units of the same bolt. `run_check` refuses construct for a unit whose `After` units have not merged; no other stage checks it.
- The plan, the moves, the agenda, the proposals and an agent's signals are all on one branch, so one commit can change any of them together.

## Goals / Non-Goals

**Goals:**
- A unit cannot merge over an open question about itself, and nobody has to remember that.
- The hold is placed and ended by the same writes that record the finding and settle it, so the plan never disagrees with the agenda.
- The fast path stays fast: the user answers in the conductor's pane and the unit is amended, with no signal and no curation.

**Non-Goals:**
- Stopping a held unit's other stages. The user and the conductor decide whether coding goes on; only completion is gated.
- Starting curation or opening a design session for a blocking signal. Both remain the user's to start; the hold makes the wait visible.
- Holds across bolts. A unit is held by findings in its own bolt's work.

## Decisions

### `Hold` is a mark on the unit, placed with the signal

`Hold` joins the Unit schema's `%allowed`. Its value is `signals/<id>`; a unit may carry several. `crew signal … --blocks <unit>` adds to its checks: the unit is in the plan, in a bolt, not `merged` or `landed`; the caller is the user, or an agent whose team (read from its name) holds that bolt. Its write adds the capture, the signal and the `Hold` in one commit, and the capture gains `blocks: <unit>`. The capture's `blocks` is permanent; the plan's `Hold` is the live state.

*Alternative:* deriving the hold on every read from the signal, its move and its item. Rejected: `crew unit run merge` would need the signals, moves and agenda to decide, and a stored mark that every settling write updates in its own commit cannot be stale, because they share a branch.

### What a hold stops

`run_check` for merge refuses a unit with a `Hold`: "unit <unit> is held by signals/<id>, which is <not yet curated | on the agenda as item <n>, <lane>>: it merges once that is settled, or on the user's word (crew unit release <unit>)". Construct, code and verify are not refused. `crew bolts` prints `held` after the stage, and `--json` carries `holds`.

### How a hold ends

One function, `settle(state, signal)`, is called inside every write that changes a signal's standing move or an item's state, and edits the plan in the same commit:

| The write | Effect on a unit held by the signal |
|---|---|
| a standing move of `attach`, `challenge`, `answered` or `drop` (a delivery, a hand move, a replacement) | `Hold` removed |
| `route` or `join` (to an item), or `revive` | none |
| the signal's item closed `dropped` | `Hold` removed |
| the item closed `decided`, no `unit/` among its results | `Hold` removed |
| the item closed `decided` with units, or `planned` | none yet: see below |
| `crew unit release <unit>` | every `Hold` on the unit removed |

When a hold is removed, the write's `after` tells the unit's conductor: "[crew] The hold on <unit> is lifted: signals/<id> was <settled how>. <the target or the results>." For a direct answer from design, the results are the decision records; the conductor's brief has it amend the unit with them (construct again, `unit-amendments`), or carry on when the answer changes nothing.

### From hold to dependency

When a unit `U` whose sources include `agenda/<n>` is added to or moved into bolt `B`, the write looks at item `n`'s signals: for each whose capture has `blocks: H`, with `H` in `B` and not merged, it removes that `Hold` from `H` and adds `After: U` to `H`. This runs inside `unit add` and `unit move`'s `change`, so within an approval it is part of the approval's commit. `After` requires both units in one bolt, which is why the new unit must go into the held unit's bolt.

`run_check` for merge gains the `After` check construct has: refused while an `After` unit is not `merged` or `landed`, naming it. That is the whole of "has to get merged before the current unit can complete". The existing rule for unstarted units is unchanged.

A proposal is checked for this at propose and again at approve: a `unit add --item <n>` or a `unit move` of a unit sourced from an item that holds `H`, to anywhere but `H`'s bolt, is refused ("item <n> holds unit <H> of bolt <B>: its unit goes into <B>, or the proposal releases <H>") unless an earlier `Do` of the same proposal is `unit release H "<why>"`. The design agent's direct `--item` add to a queue is allowed: the unit is not yet placed, the hold stands, and the planner's placing proposal converts it.

`crew plan proposed <n>` adds, under such a unit: "Unit <H> is held by this item; on approval it comes after <U> and cannot merge before it."

### `crew unit release`

A plan command in three parts. `checks`: the unit carries a `Hold`. `change`: the holds are removed; the reason goes in the commit body. It never touches `After`; removing a dependency is `crew unit after`, which a conductor already has for its own bolt. Role table: the user directly; the unit's conductor directly, on the user's word; the planner inside a proposal.

### What the agents are told

- `conductor.md`, a new section "A finding that blocks a unit": ask the user, in the words of whoever raised it; a small change is construct again with the user's words; when the user says it is big or is for design, `crew signal … --blocks <unit>`, then tell the user the unit is held and that it reaches an item when they have curation run or say to add it to the agenda now (`crew agenda add`, on their word); meanwhile carry on with what the question does not touch, if the user wants; when crew says the hold is lifted, read what settled it and amend the unit if the answer changes it; when a new unit arrives ahead of the held one, build it first.
- `curator.md`: the work order marks a signal that blocks a unit; such a signal is judged like any other, and its item's subject says the unit waits on it.
- `planner.md`: a plan item that holds a unit is proposed promptly and into that unit's bolt.
- `design.md`: an item that holds a unit says so; settle it and close it with the answer, or with the unit that must come first.

`crew agenda` prints `holds unit <H> (<bolt>, <team>)` on an item any of whose signals' captures has `blocks`, while `H` has not merged.

### Entries

`unit.hold` (`On: unit/<H>`, `On: signals/<id>`), in the capture's commit. `unit.release` for a lifted or released hold, with `From` naming the signal and what settled it. A hold turned into a dependency is a `unit.after` entry with `From: signals/<id>` and `From: unit/<U>`.

### What must not break

- A signal recorded without `--blocks` behaves exactly as before.
- A unit with no `Hold` and no `After` merges as before.
- Deliveries, hand moves and closes that touch no blocking signal make the same commits as before.

## Risks / Trade-offs

- [A unit is held for days because nobody runs curation] → the conductor tells the user at the moment of the hold, `crew bolts` and `crew agenda` show it, and the user's hand (`crew agenda add`) or `crew unit release` is one sentence away.
- [The conductor uses `--blocks` where an amendment would do] → the brief puts the user's answer first; the run record shows how often holds end in a direct answer, which is the evidence for tightening the brief.
- [An item yields two units, and only the first reaches the bolt] → each becomes an `After` as it enters the bolt; the hold is gone after the first, and the second, if it matters, is still a dependency once placed.
- [The new unit's bolt is not the held unit's] → refused at propose, with the remedy in the message.
- [A dependency added in flight deadlocks: the new unit comes after the held one in file order] → `After` is a dependency, not an order; crew's cycle check refuses a proposal that would make the new unit depend on the held one.

## Migration Plan

Pull on every host and restart conductors, curators' next runs, planners and design agents for the new briefs. The schema gains an allowed field. As with `Amended`, a crew from before this change cannot read a plan holding `Hold`, so every host pulls before the first blocking signal. Rollback: release any holds, then revert.
