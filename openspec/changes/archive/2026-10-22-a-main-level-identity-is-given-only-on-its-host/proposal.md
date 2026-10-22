# A main-level agent's identity is given only on its host

## Why

On 2026-10-16 deneb's carried session swancloud-1, then a standby of mac-studio's, came up under its launchd server, and herdr's own session restore replayed its saved panes, among them `claude --resume` of deneb's old main-level sessions. They failed only because `claude` was not yet on deneb's path ("zsh: command not found: claude", signal 2026-10-20-swancloud-operator-mac-studio-d9fcce88/01). Had `claude` been there, each would have come back as swancloud's planner, design agent or ops on a host that was not the main level's: crew's SessionStart hook gives any session it has a record for its name, its `CREW_AGENT` and its pane's name back, and at a compaction its brief, whatever host it runs on. Two copies of one main-level agent would then write to the plan, cards and kits under the same name. swancloud's `herdr.10`, as amended on 2026-10-20, already says a replayed agent pane on a standby is never the main level and that crew refuses it an identity off the teams file's host, by this unit.

The main level has since moved to deneb; mac-studio is now the host whose saved panes and old session records name swancloud's main-level agents. The hazard is the same with the hosts swapped.

## What Changes

- `crew-role` refuses to start a partition's design agent, planner, ops, operator or reviewer on any host but the one the teams file names for that partition's main level, saying which host that is, and starts no Claude. Its `resume` is refused the same way.
- crew's SessionStart hook, for a session herdr resumed whose record names one of those agents, gives its identity back, as today, only on the main level's host. On any other host it gives the session no `CREW_AGENT`, `CREW_LABEL` or `SLUICE_AGENT`, does not rename its pane, gives it no brief at a compaction and leaves its record as it was; instead it tells the session, at each of its starts, that it is no agent of crew's here, which host the main level runs on, and to do nothing of crew's.
- When the hook cannot read the teams file to tell where that main level runs, it gives no identity either, and says why (`read.1`).
- A team's agents and the dispatchers are resumed exactly as today.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `main-level`: a main-level agent's identity is given only on its main level's host, at `crew-role`'s start and at herdr's resume.
- `bolt-teams`: an agent resumed by herdr gets `SLUICE_AGENT` back only where crew gives it an identity.

## Impact

- `plugin/lib/crew.py`: two decisions beside `brief_due` (whether a recorded name is a main level's agent, and what a session off its main level's host is told), and the check in `launch_shell`, `crew-role`'s start.
- `plugin/hooks/session-start`: the off-host path, before the identity is written.
- `plugin/bin/crew-role`: its usage comment says where a main level's role starts.
- `tests/py/test_teams.py`, `tests/t-roles.sh`: the logic tier's cases and the end-to-end ones; `tests/t-session-hook.sh` stays as it is and green, its team agent's resume unchanged.
- `README.md`: the resume paragraph says a main level's agent gets its identity back only on its host.
- No change to what the board or the agents' bands draw (`code.8`).

## Touches

```
README.md
plugin/bin/crew-role
plugin/hooks/session-start
plugin/lib/crew.py
tests/py/test_teams.py
tests/t-roles.sh
```
