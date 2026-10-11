---
number: 17
title: Token spend is read from crew's sessions and Claude's transcripts, by team, role, agent and model
status: accepted
date: 2026-10-11
decision-makers:
- Chuck Swanberg
- swancloud-design
---

# Token spend is read from crew's sessions and Claude's transcripts, by team, role, agent and model

Deciders: the user (2026-10-10, through madswan-design, signal 2026-10-10-madswan-design-7e66130f/01 on madswan/main: an audit of Claude Code token spend by team, agent type and role); swancloud-design.
Sources: madswan-design's reading of 2026-10-10: `~/.local/state/crew/sessions/<session id>` carries each session's `CREW_AGENT` and `CREW_LABEL`; each transcript under `~/.claude/projects/*/<session id>.jsonl` carries per-message usage (input, output, cache creation and cache read tokens, model); 525 of 535 registered sessions on mac-studio have a transcript; ccusage is not installed and groups by project folder with no session tags. `core.md` state.4 (a view reads and never writes), read.3 (a read across hosts names each that does not answer), code.1 (the standard library only).

## Context and problem statement

The user wants to know what the teams spend: tokens by partition, team, role (unit agents, conductors, design, ops, planners), agent and model, over a window, weighted by kind, since cache reads are most of it and cost least. Nothing reports it. ccusage would need installing and cannot tell a conductor from a coder. crew already holds the join between a session and its agent, and Claude writes the usage into every transcript.

## Decision outcome

`crew usage [--label L] [--since <date>] [--by partition|team|role|agent|model]` is a read-only view: it joins crew's session registry on each host where the partition's agents run with the transcripts' usage, sums tokens by kind (input, output, cache creation, cache read) and by model, groups as asked, and prints a table with a line per group and a total; it names any host it could not read and any session it could not find a transcript for, and writes nothing (`state.4`). Dollars are a weighting the kit supplies as a table of rates per model and kind, printed when given and absent otherwise; crew ships no price list. The same join is what a page or a collector reads; `--json` gives it to them.

### Consequences

- One unit in crew, `crew-usage-sums-tokens-by-team-role-and-agent`.
- madswan's flywheel-web collector reads `crew usage --json` rather than the transcripts itself.
- The board's Operation lane may carry a spend line later; this record does not decide it.
