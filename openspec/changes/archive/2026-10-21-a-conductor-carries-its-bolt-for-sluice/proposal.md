# Proposal

## Why

Every conductor and ops of a team starts in its kit's main checkout, a detached anchor, or in a bolt's detached worktree, and makes no submission of its own, so sluice's herdr sidebar and Claude Code board show each of them the shared checkout's `N ahead` and none its bolt's queue. sluice now reads the branch an agent works for from a herdr pane token, `sluice_branch`, and from `SLUICE_BRANCH` in the Claude process (sluice's `branch-hint`, ADR 0038). The sluice session that built it handed crew's side over as a spec, and the user, 2026-10-21, in the fleet-releases session: "yes do it".

## What Changes

- A team's conductor and ops, started while the team holds a bolt, have `SLUICE_BRANCH=bolt/<bolt>` from `crew-role`, and their pane the token `sluice_branch=bolt/<bolt>`, reported from crew's source with no time to live and no sequence number.
- herdr keeps no token across its server's restart, so crew's SessionStart hook reports it again when herdr resumes the agent bare, read from the plan as it stands.
- A landing or a drop of the team's bolt clears the token on both panes, through the tidy the write already asks of the team's host; a give restarts both roles, which starts them with the new bolt.
- A unit slot carries neither, and each start in its pane clears the token.

## Capabilities

### Modified Capabilities

- `bolt-teams`: a conductor carries its bolt for sluice.

## Impact

`plugin/lib/crew.py` (`team_bolt`, `hint_branch`, `hint_args`, `hint_agent`, `Agents.hint`, `Agents.hint_standing`, `launch`, `launch_shell`, `crew.py hint`), `plugin/lib/plan.py` (`team_tidy`), `plugin/bin/crew-role`, `plugin/hooks/session-start`; the stubs herdr and claude; `teams.md` (`teams.20`).
