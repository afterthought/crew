---
number: 30
title: A unit stage's proof is a submission to sluice, and crew caps seeding stages until sluice has that run
status: accepted
date: 2026-10-14
decision-makers:
- Chuck Swanberg
---

# A unit stage's proof is a submission to sluice, and crew caps seeding stages until sluice has that run

Status: accepted. The decision is the user's, made in wldn's record 0069 (WilldanGroup/switchboard-kit `docs/adr/0069`, c5e449715, "A heavy run on a machine is started by, or leased from, the machine's sluice", accepted 2026-10-14, "Approved"), whose outcome 1 names crew's change; written into crew's records by swancloud-design the same day from wldn's design's signal. Outcome 4 of that record, crew's stand-in count until sluice has the run, the user declined for crew the same evening through the recovery session ("sluice should handle this going forward. new sluice updates will let us run heavy tests through sluice"): crew holds no cap of its own.

Deciders: the user. Written by swancloud-design.
Adds: `teams.18`.
Sources: signal 2026-10-14-swancloud-planner-48d37a0e/01 (wldn's design, relaying record 0069) and wldn-planner's note through swancloud-planner the same day; record 0069, read on chuck-herdr-alpha at `/workspace/switchboard-kit/main/docs/adr/0069-…`; record 0026 (one merge path, sluice's verdict the bolt's verification); `tests.9`; sluice's records 0012 and 0016 as 0069 reads them.

## Context and problem statement

On the night of 2026-10-13 several agents' worktrees on chuck-herdr-alpha each ran their own integration seed and after-merge verification at once, and the box ran out of memory. Each seed stands an emulator container, a Dagger engine and the containers the stand starts; an image build inside a seed runs Nix for ten minutes. None of those runs passed through sluice: the kit's policy runs one light command, and a unit stage's `ministack-seed` and `suite-integration`, and `post-merge-verify` after a merge, were the stages' own runs, each started by its agent in its place. Eight wldn teams share the box, so no team and no kit can count what runs on it; only crew sees every stage there, and only sluice counts every run.

## Decision drivers

- One party counts the heavy runs on a machine: the one that already counts runs there, sluice (its record 0012), not a second count beside it.
- A count holds no memory; the hold is the executor's, sluice's Linux sandbox once it exists.
- A unit's proof and a landing's verification are checks of a candidate, which is what sluice tests; record 0026 already makes sluice's verdict the bolt's verification.
- Until sluice offers the run, the box must not crash again: a stand-in count that crew alone can hold across every team on a machine.

## Decision outcome

Record 0069's outcomes 1 and 4, as they fall to crew:

1. **A unit stage's integration proof is sluice's run.** The stage submits the unit's branch for a run that tests it against its bolt and lands nothing, reads the outcome, and starts no seed of its own in the place. sluice's bound is then the one cap on the machine and its executor the hold.
2. **crew holds no count of its own.** Every heavy run on a machine is sluice's to start or to lease, and crew caps nothing: the stand-in count record 0069's outcome 4 gave crew until sluice has the run is not built, on the user's word; until sluice has the run, a stage's seed runs in its place as it does today, under the bound sluice's policy gets from wldn-ops's reading.
3. **A seed that is no check**, one a person or an agent runs to look at something, is sluice's heavy slot on the place (record 0069 outcome 2) and nothing of crew's.

## Consequences

- crew's unit stages change: the proof is a submission, not a seed (`a-unit-stages-proof-is-a-submission-to-sluice`), once sluice has a run that tests and does not land, which the user designs with sluice.
- No stand-in count of crew's: `at-most-three-seeding-stages-run-at-once-on-a-machine`, queued 2026-10-14, is dropped by proposal 136 on the user's word.
- `tests.9` stays as it is for crew's own suite.

## Considered options

- **Route the checks to sluice, lease the rest.** Chosen in record 0069: the checks are sluice's runs, the rest takes a heavy slot of the place.
- **Lease alone: the run stays the agent's and takes a heavy slot first.** Rejected there for checks: it recounts beside sluice's own count, and holds no memory.
- **Crew caps seeding stages on a machine, and nothing more.** Rejected, since crew's count holds nothing and sees only its own teams; record 0069 kept it as a stand-in until sluice offers the run, and the user declined even that for crew.
- **A team's or a kit's cap.** Rejected: eight teams share the box, and a team sees only its own slots, a kit only its own places.
