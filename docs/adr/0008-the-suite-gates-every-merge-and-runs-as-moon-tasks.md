# The suite gates every merge, and runs as moon tasks

- Status: accepted
- Date: 2026-10-07
- Deciders: the user, in an exploration beside swancloud-design ("yes to both", "moon unit after kits-once", "ok" to one task per test file, "let's return all of your recommendations to the crew"); swancloud-design
- Sources: `openspec/explorations/testing-strategy/reading.md` (the exploration's report, with what each fact rests on); `tests/run` line 45; `CLAUDE.md` "Tests" and "Proving and landing a bolt"; `plugin/roles/coder.md` line 25, `conductor.md` line 68, `ops.md` line 22; switchboard-kit's `.config/wt.toml` and `.moon/`; `openspec/explorations/command-cost/reading.md`

## Context and problem statement

crew's 41 tests run serially through `tests/run` in about twenty minutes, nearly all of it crew's own command cost. crew has no merge hooks and no moon, so `wt merge` into a bolt or onto main runs no gate, and the suite is run by hand before a landing. The briefs already assume otherwise: the coder runs `moon run :test --affected`, `wt merge` checks the branch, and the bolt verifies after each merge for ops to read; switchboard-kit has that shape and crew does not.

## Decision outcome

1. **Every merge is gated by the suite.** crew's `.config/wt.toml` runs, inside devenv, a pre-merge gate on a unit's or fix's merge into its bolt and on a bolt's merge onto main, and a post-merge run of the full suite on the bolt, which is the bolt's verification that ops reads, as the briefs already say. A red gate refuses the merge; a red post-merge verification is a fix, before any other unit's code.
2. **The suite runs as moon tasks, one per test file, in parallel.** Each task runs `tests/run <name>`; its inputs are `plugin/**`, `tests/lib.sh`, `tests/stubs/**` and the test file, since every command crosses `plugin/lib/plan.py`; the live test is not a task; a script generates the tasks from `tests/t-*.sh` and fails when a test has none; outputs are shared across worktrees through the git common dir; moon is pinned in devenv. What this buys, stated honestly: the serial twenty minutes become about the longest test plus contention; a tree identical to one already passed, in any worktree or stage, replays for free, so the gate replays the agent's run when the bolt has not moved and the post-merge run replays the gate's; a test-only edit reruns one test. It does not narrow what a change to `plugin/` reruns.
3. **Order.** The gate lands first, at the suite's cost as it is: main is live and merges are one at a time, so a slow gate costs minutes and no gate costs a broken main. The moon tasks follow `a-command-reads-the-kits-once`, which cuts what every task costs. That the tests do not collide when run at once is proven in the moon unit, one parallel run against one serial run.
4. **Kept out.** wtenv (a cached, shared devenv environment across worktrees) is a spike in a scratch worktree with nothing on main; `a-command-reads-the-kits-once` stays as queued; the stale "tests/run exits 0" line in CLAUDE.md is corrected with this record.

### Consequences

- Two units in crew: the gate, then the moon tasks after kits-once.
- The coder's, conductor's and ops's briefs become true for crew without a word changed.

## Considered options

- One moon task for the whole suite: no parallelism, and one failure reruns everything.
- Tasks narrower than `plugin/**`: false cache hits, since every path crosses plan.py.
- No gate until the suite is fast: a live main with no check on what lands, for weeks.
