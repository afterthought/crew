# crew

Teams of Claude agents, run in herdr.

- `plugin/` is the same for every team: the role briefs (`roles/`), the `crew` command (`bin/`), and the skill that teaches an agent to manage teams. It installs as a Claude Code plugin; this repository is its marketplace.
- `teams/<org>/<team>/` is one team: `team.sh` (the system, its repositories, its machine and herdr session, its agents' names) and four short fragments the briefs pull in.
- `machines/<hostname>.sh` says where each org folder and this repository are on that machine, and how to reach it.

```
plugin/bin/crew status                 every team: state, context use, compactions, age
plugin/bin/crew up|down <team>
plugin/bin/crew restart <team> [role...]
plugin/bin/crew resume  <team> [role...]
plugin/bin/crew clear   <team> <role>
```

A team sits whole on one machine, because a conductor reaches its agents by name and names exist only inside one herdr server. A machine holds many teams.
