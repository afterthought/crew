# crew

Teams of Claude agents, run in herdr.

- `crew.yaml` is every machine and every team, as data.
- `plugin/` is the same for every team: the role briefs (`roles/`), the `crew` command (`bin/`), the builder that turns `crew.yaml` into briefs and settings (`lib/crew.py`), and the skill that teaches an agent to manage teams. It installs as a Claude Code plugin; this repository is its marketplace.

```
plugin/bin/crew status                 every team: state, context use, compactions, age, the change held
plugin/bin/crew up|down|rebuild <team>
plugin/bin/crew restart|resume <team> [role...]
plugin/bin/crew clear   <team> <role>
plugin/bin/crew assign  <team> <coder-n|verifier> <change>
plugin/bin/crew release <team> <coder-n|verifier>
```

A team is one herdr workspace: a `conductor` tab (the conductor and ops), an `explore` tab (the explorer and fable), and a `build` tab that exists only while a coder or the verifier holds a change. A coder builds one whole change in its own worktree with `/opsx:apply`; the verifier runs `/opsx:verify` on it; the merge checks the unit tests; the full suite runs on main afterwards.

A team sits whole on one machine, because a conductor reaches its agents by name and names exist only inside one herdr server. A machine holds many teams.

Needs `herdr`, `jq`, `yq` (mikefarah), `python3`, and in each team's repository `wt` and `openspec`. `devenv.nix` declares the first four.
