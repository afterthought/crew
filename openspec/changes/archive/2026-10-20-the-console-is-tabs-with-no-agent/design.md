# Design

Rules relied on: `teams.2` (`crew console up` opens the tabs and starts no agent), `read.4` (a tab running anything else is left), `teams.9` (the panes and layout files), `code.8` (the mod's words), `docs.2` (README, skill and usage together). Pages touched: `teams.md`.

1. The console's state is `~/.local/state/crew/<label>-console`, its workspace `console` in the host's operator session; it lists no standing role, so `crew revive` passes it over and swancloud's timer keeps its tabs.
2. `crew operator up` stays as the console's old name for the hosts whose timer still runs it, since crew's main reaches every host within minutes and swancloud's job moves only at each host's deploy; it opens the console and says so.
3. The old operator agent is retired by the console's up, not by hand on each host: its `<label>-operator` state is read, its agent ended unless working, its panes and workspace closed, and the folder kept aside as `<label>-operator.retired-<time>`.
