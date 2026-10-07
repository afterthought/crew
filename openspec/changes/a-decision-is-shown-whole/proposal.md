# Proposal

## Why

The user decides from the thing itself, and today they are shown a pointer to it. At a unit's review the conductor opens only the change's proposal in plannotator, when the user wants all of its files. Agents mention the planner's proposals by number, sometimes with a summary, rarely with the proposal itself, so the user no longer sees the adds, moves and drops the plan would take on. And agents recite commands for the user to answer with, when the user answers in words and the agent runs the command (`docs/adr/0002-what-waits-on-the-user-is-shown-whole-and-read-from-state.md`, "Shown whole").

## What Changes

- **A review is the user's to open.** When a unit's change is written, the conductor tells the user the unit is ready, where its change is, and in two or three plain sentences what it would make true, asks for the answer in words ("approve it, or tell me what to change"), and stops. It no longer opens plannotator. The user opens the whole change, proposal, design, specs and tasks, when they choose to read it.
- **A proposal is shown, never only named.** The planner, a conductor or the operator agent, whenever it puts one of the planner's proposals before the user, shows what `crew plan proposed <n>` prints, in its pane or opened beside it. The number is a reference after the words, never the whole message.
- **An agent recites no answering command.** An agent that puts a review or a proposal before the user asks for the answer in words and runs the command on the user's word, as the briefs already have it.
- **The rendering shows the commands.** Under each change's plain words, `crew plan proposed <n>` prints the command approval will run, so the sequence of adds, moves and drops is visible as it was when the planner wrote the plan directly. Its *Waiting on* section names who it waits on and what each would do, in words, without the answering commands, so an agent showing it whole recites none.
- The conductor's, planner's and operator's briefs say all of this, and the README's description of `crew plan proposed <n>` matches what it prints.

The list of everything waiting on the user (`crew rail`) is the other half of the same decision and is not in this change.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `bolt-teams`: the user's review of a unit is announced in words and opened by the user; the conductor opens nothing and recites no command.
- `plan-proposals`: `crew plan proposed <n>` prints the command approval runs under each change and names who it waits on without commands; any agent that puts a proposal before the user shows it whole and asks for the answer in words.

## Impact

- `plugin/roles/conductor.md`: review with the user; the agreement paragraph of the plan.
- `plugin/roles/planner.md`: showing a proposal, where things stand.
- `plugin/roles/operator.md`: where things stand.
- `plugin/lib/plan.py`: `page()`, the markdown of one proposal.
- `tests/t-briefs.sh`, `tests/t-proposals.sh`: checks for the briefs and the rendering.
- `README.md`: the `crew plan proposed <n>` bullet.
- Each partition's conductors, planner and operator agents take the briefs at their next fresh start, or when told what changed.

## Touches

`plugin/roles/conductor.md`, `plugin/roles/planner.md`, `plugin/roles/operator.md`, `plugin/lib/plan.py` (`page()` only), `tests/t-briefs.sh`, `tests/t-proposals.sh`, `README.md` (the Proposals section), `openspec/specs/bolt-teams/spec.md` (by delta), `openspec/specs/plan-proposals/spec.md` (by delta).
