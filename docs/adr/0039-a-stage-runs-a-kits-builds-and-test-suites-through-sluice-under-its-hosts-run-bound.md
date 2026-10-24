---
number: 39
title: A stage runs a kit's builds and test suites through sluice, under its host's run bound
status: proposed
date: 2026-10-24
decision-makers:
- Chuck Swanberg
---

# A stage runs a kit's builds and test suites through sluice, under its host's run bound

Status: proposed to the user on 2026-10-24, as `briefs.15` has it; accepted only on their yes.

Deciders: the user, on this record's card; written by the design agent from madswan-design's reading of 2026-10-24.
Amends: `briefs.md` (adds `briefs.18`); the coder's, verify's and conductor's words on running a kit's tests.
Sources: swancloud signal 2026-10-24-crw-4-ops-45537fbd/01; madswan-design's tell of 2026-10-24 (the sluice statement's clauses 89 and 91); `sluice exec --help` (0.36.4): "Run the checks this worktree's head affects against a branch, or a command after `--`, under the host's bound"; record 0037 (rejected) and the user's choice of sluice's per-host run bound (sluice clause 71; swancloud's `deneb-runs-three-sluice-checks-at-once`).

## Context and problem statement

On 2026-10-24 deneb's load stood at 130 to 185 on 18 cores while sluice's own runs were bounded per host. The load came from stage agents' cold Rust builds, about 25 rustc each, run directly in their places in agentplot's teams; crew's sluice runs for `a-quiet-agent-that-committed-is-not-stuck` hit their 20-minute timeout three times with no failing test. The user settled test load on sluice's per-host run bound and rejected a bound of crew's own (record 0037). sluice counts a run against its bound only when it runs it: a check, or a command run through `sluice exec <branch> -- <command>`, which waits for room. A build or test run a stage starts directly in its place is counted by nothing and waits for nothing.

## Decision outcome

A stage runs a kit's compile and any tier of its test suite through `sluice exec <its branch> -- <command>`, under its host's run bound and the branch's policy, never directly in its place; what the kit's CLAUDE.md names light enough to run in place, a logic tier that starts no process, a lint, a format, may run there. The briefs say so (`briefs.18`), and sluice's bound stays the one bound: crew keeps no slot or count of its own.

## Considered options

- **Runs directly in the place** (today): counted by nothing; a host overloads beside its capped queue.
- **Every run through `sluice exec`**: a one-second logic test waits behind twenty-minute runs, and a coder's loop stalls.
- **Heavy runs through `sluice exec`, light ones in place** (chosen): the bound covers what loads the host, iteration stays quick.
- **A bound of crew's own** (record 0037): rejected by the user.

## Consequences

- A stage's build or suite waits for room on a loaded host as a check does, and its agent sees the wait.
- Bounded is not cached: in a run sluice starts, `sluice exec`'s included, a compile runs with no shared cache until sluice's record 0049 (proposed, on the user's card) brings a policy-declared compilation cache into sluice's runs; the sccache chores in sluice, tailrace and flywheel-next cover a session's own shell only. The two records read together, this one bounding and 0049 caching, and 0049's unit is the one to place first once both are accepted (madswan-design, 2026-10-24).
- Every kit crew builds already has a sluice policy for its bolt branches (`teams.5`), so `sluice exec` is at hand wherever a stage runs; a kit whose CLAUDE.md names no light checks runs everything through it.
- A crew unit on the yes, `a-stage-runs-builds-and-suites-through-sluice`: the briefs' words and the phrases `tests/t-briefs.sh` pins.
