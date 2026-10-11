# Proposal

## Why

On madswan, the user asked the planner for an example measurement page for Flywheel Web, "so I can get an idea of what it was thinking", and pasted the id of the conversation where the measurement pages had been worked out. That conversation ran in a different repo, switchboard-kit: it wrote Flywheel Web's site-design and measurement pages and published the design as artifacts. The signal the planner recorded carried the user's words, so it carried the bare id, and nothing else. The unit made from it named the signal and two of Flywheel Web's pages as its sources. The agent that wrote the unit's change was handed a session id it had no way to open, never saw what that conversation built, and built from the planner's one-line intent instead: unit cycle time, where the user wanted fleet utilization. The user: "You knew what I wanted ... That is not what came out on the other end, so something got lost."

What got lost was the references. Every link of the chain passes on only what it was handed: the agent recording a signal writes down the user's words, the planner names the signal, crew sends the construct the unit's sources, and the construct reads what it is sent. No link is told to turn a pointer (a conversation's id, "the artifact", "the spike") into something the next agent can open, and the construct is not even told how to read a signal: its brief says every source is a page in the blueprints repo, which is not where an agent's signal lives.

Record 0004, as amended on 2026-10-10, already says a unit's sources govern how it is built and that a construct finding the intent saying more builds from the sources and says so (rule `briefs.14`). That only helps once the sources are the real ones.

## What Changes

- **A signal says where the things it points at are.** When the user's words point at something made elsewhere (another conversation, a page or prototype, an artifact, files in another repo, a spike), the agent recording the signal finds it and names it in the signal in a form another agent can open: a repo and path, a branch, an artifact's link. A conversation's id alone is not enough; the signal names what that conversation made.
- **A unit made from a signal carries those things as its sources.** The planner, and the design agent when it queues work, name with `--source` what the signal points at, beside the signal itself, so they reach the construct in its prompt.
- **The construct reads everything it is handed and follows what it points at.** It reads a signal with `crew signal show`, and opens what each source points at. A source, or something one points at, that it cannot open stops it: it asks through crew, naming what it could not open, and never builds from the intent alone.
- **The sources govern where the intent says more or otherwise.** The construct builds from what the sources say, and opens its final message with the difference: what the intent says, what the sources say instead, and which source.
- **A source is read as it stands now.** A page the design agent changes after the bolt was started is read as changed: the construct reads it from the repository's main, not the older copy in its own worktree.
- The briefs say all this, and `tests/t-briefs.sh` holds their phrases. Nothing crew runs changes.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `main-level`: a signal names where the things its words point at are, and a unit made from one names them as sources.
- `bolt-teams`: a construct reads every source it is handed and what each points at, stops when it cannot open one, builds from the sources where the intent says more or otherwise, names the difference first, and reads each source as it stands now on main.

## Impact

- `plugin/lib/crew.py`: the signal-recording instruction every brief that records signals shares (`signal_how`).
- `plugin/roles/planner.md`, `plugin/roles/design.md`: a unit from a signal names what the signal points at.
- `plugin/roles/construct.md`: reading the sources, following them, stopping when one can't be opened, the sources governing, and the opening of the final message.
- `tests/t-briefs.sh`: checks for the new phrases (`tests.6`).
- `docs/architecture/_open.md`: the `briefs.14` entry keeps only the spike, which this change does not build.
- Every agent takes the change at its next fresh start; each construct is a fresh agent, so every team's next construct has it.

## Touches

`plugin/lib/crew.py` and `docs/architecture/_open.md` are shared files. The specs change only through this change's deltas, in its own folder.

```
plugin/lib/crew.py
plugin/roles/construct.md
plugin/roles/planner.md
plugin/roles/design.md
tests/t-briefs.sh
docs/architecture/_open.md
```
