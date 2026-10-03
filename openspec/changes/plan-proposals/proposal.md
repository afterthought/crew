# Proposal

## Why

The planner writes the plan the moment it decides to. On 2026-10-03 it queued two units within a minute of two signals, with design choices in their intents, and nobody had read either before they were in the plan. The user's judgment is that agents are not reliably good at the placing itself: whether new work is a new bolt, a unit in an existing bolt, or queued, and whether an existing unit should change. Those are the decisions the user wants to see before they take effect, and today the only gate is the review of a unit's OpenSpec change, which comes after the unit has already been named, worded and placed.

This change makes every change the planner makes to the plan a **proposal** that the user approves. It follows Flywheel Next's planner, which writes one proposal, the case for a batch and its units, and creates nothing until the operator approves (`flywheel-next/main/instructions/skills/planner/SKILL.md`). It is step 3 of the findings-to-design work (`openspec/explorations/findings-to-design/proposal.md`, invariants 8, 9, 14 and 15; `roadmap.md`).

## What Changes

- **BREAKING** The planner no longer writes the plan directly. A plan-writing command run by the planner is refused, naming `crew plan propose`.
- **A proposal** is a record in `proposals.rec` on the flywheel's branch of its state repository: the planner's case in a paragraph, and the plan commands it would run, in order (`bolt new`, `bolt order`, `bolt drop`, `unit add`, `unit move`, `unit split`, `unit order`, `unit after`, `unit drop`). Proposals are numbered, and never removed.
- **`crew plan propose <file>`** checks every command against the plan as it stands, in order, and writes the proposal. It tells the conductor of each bolt in flight the proposal touches.
- **`crew plan proposed [<n>]`** lists the open proposals, or prints one as the user would want to read it: the case, then each change in plain words, with a unit's intent beside what it rests on and the goal of the bolt it would join, and who has yet to agree.
- **`crew plan agree <n>`** is the conductor's recorded agreement to a proposal that touches its bolt. Approval is refused without it.
- **`crew plan approve <n>`** applies the proposal's commands, exactly as read, in one commit that also closes the proposal. The user runs it, or an agent runs it on the user's word. If any command no longer applies, nothing changes.
- **`crew plan drop <n> "<reason>"`** closes a proposal unapplied. `crew plan propose --replaces <n>` drops one and writes its successor together.
- **Other agents write the plan only within their own job**, as their briefs already say: a conductor splits, orders and sets dependencies inside the bolt its team holds; the design agent queues units; a dispatcher gives bolts; main-level ops lands them. Any other plan write by an agent is refused. The user at a shell writes freely.
- Every one of these acts is a run-record entry, and each change an approval applies names the proposal it came from.

## Capabilities

### New Capabilities

- `plan-proposals`: how the plan changes: the proposal record, its checks, how it is read, the conductor's agreement, the user's approval, and which agent may write what directly.

### Modified Capabilities

- `main-level`: the planner changes the plan only through approved proposals, and a change to an active bolt is agreed by a recorded act.

## Impact

- `plugin/lib/plan.py`: each plan command split into its checks, its change and its after-effects, so a proposal can check them without writing and an approval can apply several in one commit; `proposals.rec`; the `plan propose|proposed|agree|approve|drop` commands; the caller's role checked on every plan write.
- `plugin/bin/crew`: the `plan` subcommands routed to `plan.py` (it already routes `plan init`).
- `plugin/roles/planner.md` rewritten around proposals; `conductor.md` (agreeing a proposal), `design.md` (queues only), `operator.md` (open proposals are waiting on the user), `dispatcher.md` and `main-ops.md` unchanged in what they may write.
- `README.md`, `plugin/skills/crew/SKILL.md`, the usage header, `tests/`.
- The state repositories: a new file, `proposals.rec`, on each flywheel's branch.
- Depends on `state-repository` (a proposal, the plan and a move change in one commit) and `run-record`.

## Touches

`plugin/lib/plan.py`, `plugin/bin/crew`, `plugin/roles/planner.md`, `plugin/roles/conductor.md`, `plugin/roles/design.md`, `plugin/roles/operator.md`, `plugin/skills/crew/SKILL.md`, `README.md`, `tests/`; `proposals.rec` on each flywheel's branch.
