# Proposal

## Why

An agent's tool call ends at ten minutes, and sluice's verdict on a submission takes from one to forty-five. wldn's design agent, landing about forty records on a sluice main (2026-10-21), could not block on a submit, so it submitted with `--no-wait` and polled `sluice status main` every minute, searching the listing for landed or failed; a decided submission leaves that listing, so twenty of its pollers never stopped. crew's briefs had a unit's merge, the design agent and the operator run a waiting `wt submit` in the background and wait for it to end, which holds only while the agent keeps that background task and its turn. sluice 0.36.0 adds `sluice wait <n> [--timeout] --json` (sluice ADR 0041): it runs the rounds a waiting submit runs, returns the submission's record however it ends, and exits 0 landed, 1 failed, 2 conflict or refusal, 4 withdrawn, 5 still waiting. sluice's own skill now tells agents to submit with `--no-wait` and loop on it.

## What Changes

- A unit's, chore's or fix's merge command is `sluice submit bolt/<bolt> --no-wait --json`; the coder waits on it with `sluice wait <n> --timeout 9m --json` for as long as it exits 5, ending no turn while it is undecided, and acts on the exit.
- The design agent and the operator submit to a kit's main the same way, and once `sluice wait` exits 0 remove their worktree and branch with `wt remove`, which a waiting `wt submit` did for them.
- No brief reads a submission's outcome from `sluice status <branch>`'s listing.
- crew's own stage wait is unchanged: it reads sluice's overview and `sluice status <n> --json`, and ends a stage at its deliverable, not at the submission.
- A landing stays `crew bolt submit`, which runs a waiting `wt submit main` on the team's host and is run in the background by main-level ops.

## Capabilities

### Modified Capabilities

- `bolt-teams`: a unit's merge is a submission its agent waits on with `sluice wait`.
- `merge-gate`: an agent reads its submission's outcome from `sluice wait`, never from a listing.

## Impact

`plugin/lib/plan.py` (`merge_command`); `plugin/roles/coder.md`, `conductor.md`, `design.md`, `operator.md`; `CLAUDE.md`; `teams.md` (`teams.5`); `tests/stubs/sluice` (`submit --no-wait`, `wait`). Every host needs sluice 0.36.0 or later before this lands, since crew runs live from main.
