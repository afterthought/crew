# Proposal

## Why

`crew signal` writes a capture and its signal in one step, and the capture is hollow. It has no source: the two signals a conductor recorded on 2026-10-03 hold the agent's paraphrase of something the user said, with no excerpt, and the user's actual words exist only in that conductor's Claude transcript, which the capture does not point at. The capture is one per agent per day, not one per thing that happened. And it is written to the blueprints repo's main, so the user's asides to an agent land in the client's design repository, in commits that arrive while people work there.

A signal is only as good as the excerpt it rests on: curation, the planner and the user all judge it later, and what they must be able to see is what was actually said. This change makes `crew signal` keep the words, check them, and say where they came from. It is step 5 of the findings-to-design work (`openspec/explorations/findings-to-design/proposal.md`, invariants 1 to 4 and "What crew reads of a transcript"; `roadmap.md`). The user decided that an agent's signals live on the flywheel's branch of the state repository, not in the blueprints.

## What Changes

- **BREAKING** `crew signal` run by an agent requires `--excerpt` (or `--excerpt-file`): the words that show the finding, as the agent's session received them, from the user or from a tool.
- **The excerpt is checked** against the agent's own Claude transcript, and the capture records a grade: `verified` (found in a record the session received), `found` (found in the transcript, in a record crew cannot classify) or `unverified` (crew could not read a transcript, with the reason). The signal is **refused only** when the transcript is the live session's, its last record written within 15 minutes, and the excerpt is nowhere in it but in what the agent wrote itself: the paraphrase case. A change in Claude Code's transcript format therefore lowers a grade and never blocks a capture.
- **A capture is one record the session received**: the user's message, or one tool's output. It names the host, the Claude session, the record and its time, who asserted it, and the team, bolt and unit the agent was working in. A second signal from the same record joins the same capture.
- **The raw record is banked** on the capturing host, outside git, and the capture points at it.
- **BREAKING** An agent's captures and signals are written to `signals/` on the flywheel's branch of its state repository, in the shape the blueprints' `signals/README.md` gives. Meeting and channel signals stay in the blueprints, where the daily pass writes them. A signal's id is looked up in the state first and the blueprints after.
- **The user's own note**, `crew signal` at a shell, is its own excerpt.
- **`crew signal show <id>`** prints a signal with its capture's provenance, from any host.
- **`crew tell` marks what it sends** (`[crew tell from <agent>]`, and `[crew]` for crew's own greetings and notices), so words another agent sent are not taken for the user's, by crew or by the agent reading them.

## Capabilities

### New Capabilities

- `signal-capture`: how something noticed becomes a capture and a signal: the excerpt and its check, the capture's provenance and identity, where the records and the raw material live, and how a signal is read back.

### Modified Capabilities

- `main-level`: where signals live, and that a finding is recorded with the words that show it.
- `bolt-plan`: a signal named by `--signal` is looked up in the flywheel's state and in the blueprints.

## Impact

- `plugin/lib/plan.py`: `signal` rewritten (the check, the capture's identity, the write to the state branch), `signal show`, signal lookup in two homes for `signal move` and `unit add --signal`. A small transcript reader, in `plugin/lib/`.
- `plugin/lib/crew.py`: `tell` and `greet` prefix what they send.
- Briefs that record findings: `conductor.md`, `ops.md`, `main-ops.md`, `design.md`, `planner.md`, `operator.md`; and every brief's note on what a `[crew tell from …]` message is.
- `README.md`, `plugin/skills/crew/SKILL.md`, the usage header, `tests/` (fixture transcripts).
- Each host: `~/.local/state/crew/<label>/raw/`.
- The blueprints repos' `signals/README.md`: says where an agent's signals live and documents the capture fields crew writes.
- Depends on `state-repository` and `run-record`.

## Touches

`plugin/lib/plan.py`, `plugin/lib/crew.py`, a new `plugin/lib/transcript.py`, `plugin/bin/crew`, `plugin/roles/`, `plugin/skills/crew/SKILL.md`, `README.md`, `tests/`; `signals/` on each flywheel's branch; each blueprints repo's `signals/README.md`.
