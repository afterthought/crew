# Proposal

## Why

sluice's session, reading crew's side of the branch hint (2026-10-21), asked two things. First, a conductor or ops that keeps running when its team's bolt lands or is dropped still carries the old `SLUICE_BRANCH`, which sluice's Claude Code board reads once at the session's start, so the board names a bolt that is gone until something restarts it. Second, an agent landing docs on a sluice main, wldn's design agent, cleaned up by hand after every landing, about forty times: its brief ran `wt submit main --no-remove` and then had it remove the worktree and delete the branch, though sluice's `wt submit` removes both itself once its record says the head landed. And a unit's place and branch went only at the conductor's next read of its team, not when its merge landed. The user, 2026-10-21, in the fleet-releases session: "what about bolt changes?"

## What Changes

- A start records the branch it carries for sluice (`CREW_BRANCH`), empty after herdr's bare resume, whose process has none.
- When a landing or drop changes the team's bolt, the tidy on the team's host clears the token as before and hands each conductor or ops whose session carries the old branch its restart at its next stop, the restart teams.19 gives an agent an update made due: the conductor fresh, ops with its conversation, each told why. A give already restarts both.
- A unit's, chore's or fix's merge, once its wait sees it delivered, frees the slot and removes the place and branch at once.
- The design agent's and the operator's briefs run `wt submit main`, which removes the worktree and its branch on landing, in place of `--no-remove` and a removal by hand.

## Capabilities

### Modified Capabilities

- `bolt-teams`: a conductor carries its bolt for sluice; a worktree goes when its work is over.

## Impact

`plugin/lib/crew.py` (`starts`, `branch_due`, `branch_now`, `due_of`, `Agents.hint_standing`), `plugin/lib/hold.py` (`renew`), `plugin/lib/plan.py` (`team_tidy`, `after_delivery`, `stage_wait`), `plugin/hooks/session-start`, `plugin/roles/design.md`, `plugin/roles/operator.md`; `teams.md` (`teams.1`, `teams.20`).
