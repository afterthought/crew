---
number: 22
title: A decision is tested as a function of facts, a tool by a contract, and the command's wiring end to end
status: accepted
date: 2026-10-12
decision-makers:
- Chuck Swanberg
---

# A decision is tested as a function of facts, a tool by a contract, and the command's wiring end to end

Deciders: the user, who asked on 2026-10-12 for "fast tests that tested the state machine logic without hitting the real services and then … dedicated tests that proved how the services were expected to work", after record 0021's trims left a full suite at about five minutes; the recovery session, which measured what follows.
Amends: record 0008, its decision that the suite is one moon task per bash test file; record 0021, whose inputs rule now holds for the end-to-end tier.
Sources: the per-test measurement of 2026-10-12 on mac-studio (each test's CPU from the rusage of its own run, five at a time, every team down); `plugin/lib/plan.py`; `plugin/bin/crew`; `tests/`; the session's design as agreed with the user the same day.

## Context and problem statement

Every crew test is a bash file that builds simulated hosts, git repositories and a stub herdr, ssh and claude, then runs the real `crew` command and reads what the stubs logged. A check of one decision, whether verify names a path the unit did not declare, whether a card is refused, which stage comes next, costs a whole team world and every process the command starts on the way: about 2,000 launches for a heavy test, so each test keeps about a core busy for its whole run. Record 0021 bounded how many run at once and which ones rerun; it could not make one cheaper. Measured on 2026-10-12, the 63 tests take 1,740 s of CPU, a median of 22 s each, 83% of their wall time spent on a core; the ten costliest take 742 s of it, 43%: `t-fix` 161 s, `t-stage-ends` 95, `t-unit-run` 75, `t-batches` 73, `t-after` 61, `t-record-team` 60, `t-amend` 59, `t-unit-free` 55, `t-proposals` 53, `t-card-sweep` 51.

The cost is not in the decisions. `plan.py` is 6,000 lines, 246 functions, with about ninety places that call git, ssh, herdr or an agent, mixed into the decisions they feed; `plugin/bin/crew` holds decisions too, such as refusing a stage whose agent is working. So a decision can only be reached through the command, and the command only through its tools.

## Decision outcome

1. **Three tiers.**
   - **Logic** (`tests/py/`, pytest, in-process): a decision of crew's called on plain facts, its result checked. It starts no process: the tier's fixture makes every `subprocess` call raise. Facts are built by `tests/py/facts.py`, so a case reads as the spec's scenario: a bolt, its units and stages, an agent working.
   - **Contract** (`tests/contract/`, pytest): git, recutils and worktrunk run for real in a scratch directory, each case pinning one behaviour crew's code assumes and naming the function or rule that assumes it: a first-parent log, a `merge-tree` forecast, a plan record read after a write, `wt merge` on a branch holding merges.
   - **End to end** (`tests/t-*.sh`, as today): about ten tests that run the `crew` command on the stubs and prove its wiring, from the bash through `plan.py` to the stub agent.
   Nothing in the suite calls a real agent, posts a real card or reaches another host; `t-sites-live` stays as it is, outside the suite.
2. **A decision is a function of facts.** crew's commands read, decide, then act: the decision is a function of plain data that calls no tool, and the read and the act around it stay thin, proved by the contract and end-to-end tiers. Decisions are pulled out one at a time as their tests convert, never by rewriting `plan.py` at once; a decision in `plugin/bin/crew`'s bash moves to Python when its test converts (`core` rule `code.7`).
3. **What runs when.** A coder's edit runs the logic tier, in seconds. Every merge gate, into a bolt and onto main, runs all three; onto main with nothing replayed (record 0021). The suite is moon tasks: one for the logic tier, one for the contract tier, one per end-to-end file, each with its inputs.
4. **How a test converts.** The costliest first, by CPU, measured before and after. Each of a bash test's cases goes to the lowest tier that can check it: a decision to logic, a tool's behaviour to contract, the command's wiring kept end to end, one case per command at most. The bash case a lower tier now checks is deleted in the same commit. A fix lands with its reproducing case at the lowest tier that can hold it (`tests.4`).

### Consequences

- The edit loop is the logic tier; the gate is the logic and contract tiers and about ten end-to-end tests. The aim is record 0021's: a full suite's CPU at a third or less of 1,922 s, and three crew teams' gates at once with the host under its cores.
- `plan.py` and `plugin/bin/crew` change shape as decisions come out; each extraction keeps the command's behaviour, proved by the end-to-end test of that command and the logic cases of the decision.
- A stub stays the end-to-end tier's stand-in for herdr, ssh, claude and plannotator; when a fix depends on how one behaves, the stub changes to behave the same, as now.
- pytest is a development dependency in devenv; crew's own Python still imports nothing outside the standard library (`code.1`).

## Considered options

- Keep every test end to end and trim further (record 0021's path): bounded by the processes each crew call starts, which no trim removes.
- Patch `subprocess` or `kit_git` inside the end-to-end tests: tests that pin call sequences rather than decisions, broken by every refactor.
- A native or Rust helper for the plan's read and write path: cheaper calls, but the tests would still make every call; record 0021's step 1.7 stays a go/no-go after this.
- A live tier against real herdr, claude, Pending You and plannotator: costs tokens and posts real cards; the user ruled it out on 2026-10-12 ("I don't understand why we would be running live contract tests now").
