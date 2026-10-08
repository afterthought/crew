# Proposal

## Why

crew takes the first moment a stage's agent goes quiet as the end of the stage. An agent that ends its turn to wait on suites it started, on a merge's checks, or on a question looks exactly like one that has finished, so the conductor is told "settled" with nothing in hand and falls back to reading the agent's pane, once for two hours (ADR 0007, from wldn-ops's findings on brd-1, 2026-10-07). The rule is already written as `teams.4`; crew does not hold to it yet.

## What Changes

- **A stage ends at what it delivers.** Each stage has one deliverable, read in the kit or on the team's host: construct's committed change, code's ticked tasks, verify's report file, merge's commit on the bolt, a fix's commits, ops's proof file. crew records a stage's end once its deliverable exists and its agent has stopped working, never at a quiet pane alone.
- **An agent that can't finish says so through crew.** A new command, `crew needs "<what it needs>"`, run by a stage's agent (or by ops during a proof), ends the stage short. The conductor gets the agent's words from crew: in its wait's answer, or by a tell when it isn't waiting. The words never go in the run record.
- **The wait answers with the outcome.** `crew unit wait <unit>` returns with what was delivered (the change's commit, the ticked head, the report's path, the bolt's commit), or with what the agent needs, or with "stuck": the agent has been quiet for longer than crew's limit (15 minutes by default) with neither a deliverable nor a word, and isn't waiting on background work of its own. A quiet agent still waiting on its suites is not stuck; crew reads that from the agent's own session.
- **The same for a fix and for ops's proof.** `crew fix <team> <name> --wait` waits on a fix the same way. Ops's proof of a bolt becomes a stage crew starts and waits on: `crew prove <team>` asks ops to prove the bolt and owes the proof's end; `crew prove <team> --wait` waits for ops's proof file, which ops now writes once, whole, in the team's reports folder.
- **The run record's `stage.end` names the deliverable** (`Delivered`) and how the stage ended (`Ended`: delivered, short, or stopped when crew ended its agent first). An end nobody waited for is still recorded late, but only once its deliverable exists.
- **The briefs change to match.** The conductor waits for every stage, fix and proof through crew, never reads a pane for an outcome, takes a stuck stage to the user, and answers a stopped-short stage by running it again with the answer as its words. Construct, code, verify and ops say what they need with `crew needs` instead of in a pane nobody watches; ops writes its proof to the reports folder.
- **BREAKING** for a conductor already running: `crew unit wait` no longer returns at the first quiet moment, and its answer reads differently. Each conductor takes the new brief at its next fresh start.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: waiting on a stage returns at its deliverable, its stop-short or its being stuck, for units, fixes and ops's proof; every stage has a deliverable; a stage's agent says what it needs through crew; ops's proof is a stage crew starts and waits on.
- `run-record`: a stage's end is recorded at its deliverable, its stop-short, or when crew ends its agent, never at a quiet pane, and names what was delivered.

## Impact

- `crew unit wait` behaves differently; `crew needs`, `crew fix … --wait` and `crew prove` are new.
- The conductor, construct, coder, verify and ops briefs change; each agent takes them at its next fresh start after the bolt lands and every host has pulled.
- Chores are not in crew yet (`plan.11` is accepted, not built). A chore's stages wait the same way once that kind exists; building it is the chores unit's work.
- The rail's verify row is unchanged.

## Touches

- `plugin/bin/crew` (unit wait, fix --wait, prove, needs, stop, usage header)
- `plugin/lib/plan.py` (the wait, the deliverables, stage ends, the stop-short)
- `plugin/lib/transcript.py` (background work still running in an agent's session)
- `plugin/lib/record.py` (the `Ended` and `Delivered` fields and the descriptor)
- `plugin/lib/crew.py` (the `{{NEEDS}}` brief token)
- `plugin/roles/conductor.md`, `construct.md`, `coder.md`, `verify.md`, `ops.md`
- `plugin/skills/crew/SKILL.md`, `README.md`
- `tests/t-record-team.sh`, `tests/t-amend.sh`, `tests/t-fix.sh`, `tests/t-briefs.sh`, a new `tests/t-stage-ends.sh`, `tests/stubs/herdr` if the stub needs a session transcript
- `docs/architecture/teams.md`, `docs/architecture/_open.md`
