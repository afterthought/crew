# Proposal

## Why

When an agent reports how tests, checks or a bolt's proof went, it folds the results into sentences, and the user has to read every line carefully to be sure nothing failed. The user asked for a bulleted pass/fail list with a green check or red cross on each line, as standard behaviour for every agent that reports results (signal `2026-10-07-swancloud-design-c8f7c4bd/01-test-results-are-a-glyph-list`). The rule is already written as `briefs.7`; no brief carries it yet.

## What Changes

- Every role that reports test, check or proof results (the conductor, ops, main-level ops, construct, coder and verify) puts them first, before any prose, as one bullet per suite, check or proof:
  - ✅ passed, with its counts where the tool gave them;
  - ❌ failed, with how many failed and one line on why;
  - ⏳ not yet run, or still running.
- A result is never said only in a sentence ("they all passed"), and several suites are never folded into one bullet.
- The same list is used wherever the results go: the agent's reply, a file it writes them to, or a message to another agent that passes them on. An agent passing on another's results passes its list on as it is.
- The rule is written once, as one section crew builds and every one of the six briefs carries, so the six cannot drift apart.
- The brief tests pin the section in each of the six briefs, and check it reads the same in all of them.
- `briefs.7` stops being listed as accepted but not built.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a requirement that the team's conductor, ops, construct, coder and verify report results as the glyph list.
- `main-level`: a requirement that the partition's main-level ops reports a landing's checks and main's deploy as the glyph list.

## Impact

- The six briefs gain one section, filled by crew when each role starts; nothing an agent runs changes.
- Takes effect for each agent at its next fresh start after the bolt lands and every host has pulled.

## Touches

- `plugin/lib/crew.py` (the brief tokens for teams and main levels)
- `plugin/roles/conductor.md`, `ops.md`, `main-ops.md`, `construct.md`, `coder.md`, `verify.md`
- `tests/t-briefs.sh`
- `docs/architecture/briefs.md`, `docs/architecture/_open.md`
