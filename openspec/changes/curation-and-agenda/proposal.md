# Proposal

## Why

Nothing in crew decides what a signal means. The design agent's brief says it curates, and it never has: wldn holds 194 signals and the only two moves ever written are `route` moves the planner wrote on 2026-10-03, within a minute of the signals, because a conductor's brief told it to tell the planner directly. So a finding either skips every judgment and lands in the plan, or sits unread. There is no list of what needs the user's decision, no ritual for deciding it, and no record that ties a decision or a unit back to what was said.

This change adds the missing middle of the flow, and proves the flow end to end. It is step 6 of the findings-to-design work (`openspec/explorations/findings-to-design/proposal.md`, invariants 5 to 13; `roadmap.md`). It follows Flywheel Next's curation: a bounded session that gives every unmoved signal one move, never acts on its own judgment, and delivers in one commit (`flywheel-next/main/openspec/specs/signals/capture-and-curation/spec.md`; its `curator` skill and `move` and `intent-proposal` schemas).

## What Changes

- **Curation is its own pass.** `crew curate <label>` starts a **curator**, a new role on Fable 5.1 at high effort, for one batch: every signal with no standing move, in the flywheel's state and in the blueprints. It runs only on the user's word. The design agent no longer curates.
- **A work order** holds everything the curator reads: the batch's signals, the open agenda items, the plan, where the design is, and the delivery's format.
- **One delivery, one commit.** `crew curate deliver <file>` accepts the curator's moves and new agenda items only when they cover the batch exactly and every target resolves, and writes them all at once.
- **BREAKING** The six moves are Flywheel's words: `attach`, `challenge`, `join`, `answered`, `route`, `drop`. `join` replaces `new-territory`, which no record uses. Every move carries a reason.
- **Two lanes, as agenda items.** `route` puts a signal on a **plan** item, which goes to the planner; `join` puts it on a **design** item, which waits for the user. Items are records in `agenda.rec` on the flywheel's branch, numbered, never removed.
- **`crew agenda`** lists the open items from any host, each with its signals' weight; `crew agenda <n>` shows one with its signals, excerpts and grades. `crew agenda add`, `lane` and `close` are how a person, the planner and the design agent change it.
- **BREAKING** A unit an agent adds names the item it came from (`--item <n>`). The planner turns a plan item into a unit inside a proposal, and approval closes the item. The design agent queues the units a session decides, and closes the item with the decision records and units that cite it. `--signal` remains only for what the user tells the planner directly.
- **BREAKING** A noticing agent captures and tells nobody. The conductor's, ops' and main-level ops' briefs lose "tell the planner in one line".
- **Only the user replaces a move**: `crew signal move … --replace "<why>"` and `crew signal revive <id> "<why>"`. Moves stay append-only; a replacement names the move it replaces.
- Every one of these acts is in the run record, so `crew trace` follows a signal through its move, its item, the proposal or the session, to the unit.

## Capabilities

### New Capabilities

- `curation`: the curator's pass: when it runs, its batch and work order, the moves and their checks, the delivery, the hand that does the same by command, and the replacement of a move.
- `agenda`: the items curation and people put before the planner and the user: the record, how it is read with its weight, how an item changes lane and closes, and how a unit names the item it came from.

### Modified Capabilities

- `main-level`: the design agent works agenda items and does not curate; the planner proposes from plan items; a noticing agent captures and tells nobody; the moves' vocabulary and the one standing move.
- `agent-models`: the curator's model and effort.
- `bolt-plan`: `--signal` is narrowed to the planner's own capture of the user's word.
- `plan-proposals`: a proposal shows the item a unit rests on, and its approval closes the item.
- `operator-agent`: what waits on the user includes the agenda, and the operator starts curation on the user's word.

## Impact

- `plugin/lib/plan.py`: `moves.rec`'s key and enum and the standing-move rule; `agenda.rec`; `crew agenda …`; `crew curate` and its delivery; `--item` on `unit add` and the gate; the proposal page and approval.
- `plugin/bin/crew`: `curate` (a tab in the main level's workspace, as a role is started), `agenda`.
- `plugin/roles/`: a new `curator.md`; `design.md`, `planner.md`, `conductor.md`, `ops.md`, `main-ops.md`, `operator.md` and `construct.md` changed.
- `README.md`, `plugin/skills/crew/SKILL.md`, the usage header, `tests/`.
- The state repositories: `agenda.rec` on each flywheel's branch; `moves.rec` re-keyed.
- The blueprints repos' `signals/README.md`: the six words, the lanes, where moves and items live.
- Depends on `checked-capture`, `plan-proposals`, `state-repository` and `run-record`.

## Touches

`plugin/lib/plan.py`, `plugin/lib/crew.py`, `plugin/bin/crew`, `plugin/bin/crew-role`, `plugin/roles/`, `plugin/skills/crew/SKILL.md`, `README.md`, `tests/`; `agenda.rec` and `moves.rec` on each flywheel's branch; each blueprints repo's `signals/README.md`.
