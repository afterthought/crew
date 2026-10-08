# Proposal

## Why

Today nothing checks what merges in crew. A unit or fix merging into its bolt, and a bolt landing on crew's main, runs no tests, though main is live on every host the moment it moves. The suite is run by hand before a landing, and the briefs already tell every agent that `wt merge` checks the branch and that the bolt verifies itself after each merge for ops to read: true in switchboard-kit, not in crew. Record 0008 decides that every merge in crew is gated by its suite, and that this gate lands first, at the suite's present cost of about twenty minutes, before the suite is split into parallel moon tasks.

## What Changes

- A merge into a bolt, of a unit or a fix, runs crew's whole suite on the exact tree about to land, after the rebase. When any test fails, the merge is refused and nothing lands; the agent sees which tests failed.
- A bolt's merge onto main runs the same gate, from the bolt's worktree, and is refused the same way.
- After every merge into a bolt, the whole suite runs again on the revision the bolt now holds, in the background, on a copy of that revision that later merges cannot change underneath it. Its outcome (running, green, red with the failing tests, or cut off) is recorded where every worktree on the host can read it, and one command prints it for the bolt's head. That is the bolt's verification, which ops reads and the conductor acts on: red is a fix, before any other unit's code.
- ops can run the verification again on the bolt's head when nothing has merged since.
- The gate and the verification never run the live test, whatever the environment says.
- The coder's and main-level ops's briefs say a merge's checks can outlast a command's time limit, so the merge is run in the background and waited for, never restarted or bypassed.
- CLAUDE.md says how crew's bolt verification is read and that it, green at the bolt's head, is the bolt's proof before landing. `_open.md` keeps only the moon half of `tests.5` as not built.

## Capabilities

### New Capabilities

- `merge-gate`: how crew's own repository checks what merges into a bolt and onto main, and how a bolt's verification after each merge is run and read.

### Modified Capabilities

None. `bolt-teams` already says a unit merges "with the kit's merge hooks" and that a red verification on the bolt is a fix; this change gives crew, as a kit, those hooks.

## Impact

- New `.config/wt.toml` with a pre-merge gate and a post-merge verification; new scripts under `.config/hooks/` that run the verification and print its outcome.
- A new test, `tests/t-merge-gate.sh`, run against a scratch repository with the real `wt` and a stand-in suite.
- `plugin/roles/coder.md` and `plugin/roles/main-ops.md`: one sentence each on running a long merge in the background; `tests/t-briefs.sh` pins both.
- `CLAUDE.md` (Tests; Proving and landing a bolt) and `docs/architecture/_open.md`.
- Every merge in crew takes about twenty minutes more until the moon unit (`the-suite-runs-as-moon-tasks`) makes the suite parallel and replayable.
- Needs, outside the repository: the user approves crew's project hooks once with `wt config approvals add`, on each host that merges in crew, before the first merge that carries this file. worktrunk refuses unapproved hooks in an agent's session, so until then such a merge stops and asks.

## Touches

`.config/wt.toml` (new), `.config/hooks/` (new: the verification and its reader), `tests/t-merge-gate.sh` (new), `tests/t-briefs.sh`, `plugin/roles/coder.md`, `plugin/roles/main-ops.md`, `CLAUDE.md`, `docs/architecture/_open.md`, and `openspec/specs/merge-gate/spec.md` (new, by delta). Every later merge in crew, this unit's own included, runs the gate this change adds.
