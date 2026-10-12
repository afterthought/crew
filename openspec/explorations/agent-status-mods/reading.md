> A reading (2026-10-12): what a Claude Code mod can and cannot do, and a design for showing each crew agent its slice of the board as one; a prototype is on branch `recovery/mods`, and nothing here is decided until the user says so.

# Exploration: each crew agent's status, shown as a Claude Code mod

Asked by the user on 2026-10-12: show, for a team's conductor, what the team is working on, its status and its roadmap, as a mod, in one consistent ASCII form; perhaps the planner, the design agent on its elaborations, and one overview for the operator; only if it is simple.

Read from the mods pages (code.claude.com/docs/en/plugins/mods: overview, create, interface, events, api, test, troubleshoot, admin, reference, gallery), the type declarations Claude Code 2.1.296 writes for a mod, the Pending You mod already loaded on mac-studio (`~/.config/pendingyou/mod`), and crew's `board.py`, `plan.py` and `plugin/bin/crew`.

## What a mod is, and what it can and cannot do

- **What it is.** A plugin whose `hooks/hooks.json` names one JavaScript or TypeScript module (`"modules": ["./x.js"]`). Its `register(on)` hooks events (a tool call, a prompt, a turn, a part of the screen being drawn); each hook can watch, rewrite or answer its event. It runs inside Claude Code's own process, on one worker thread every installed mod shares, with the user's permissions and no sandbox. Claude Code 2.1.287 or later; mac-studio runs 2.1.296.
- **Where it shows.** Only in the terminal and the Desktop app; in `claude -p`, the Agent SDK and the VS Code panel its hooks run and nothing draws.
  - The **band above the prompt** (`AbovePrompt`): always there, shared by every mod, any tree of rows. In fullscreen it gets what is left of half the terminal; a taller tree scrolls under an "n more" row. The user collapses it (ctrl+x ctrl+a) or focuses it (a click, ctrl+x tab).
  - A **pane** (`$.ui.open`): a sidebar in a wide fullscreen terminal, a framed region above the prompt otherwise, tabs when several are open. One the mod opens on its own appears only from 144 columns (110 once the user has opened it); one a command or a button opens appears at any width.
  - **One status line** under the prompt (`$.ui.status`, one per plugin, after the plugin's name), a dim tail on the hint line, a toast, and dim transcript lines Claude does not read (`$.ui.log`).
  - It can restyle or replace what Claude Code draws (the spinner, tool rows, messages, the question dialog), never the permission prompt.
- **What it reads and runs.** Only through the mods API, which `claude plugin validate` lists without running it: files (`$.fs.read`, `write`, `stat`, `list`; 4 MiB a file; no watch), processes (`$.process.run`, no shell, 30 s by default), the network (`$.http.fetch`), environment variables by literal name (`$.env.get`), a JSON store per plugin shared by every session (`$.store`, 4 MiB), the session (`id`, `cwd`, transcript, usage), models (`$.model.complete`, billed to the session's account), and starting a turn or messaging another session (`$.prompt.submit`, `$.session.send`). No Node APIs and no `setTimeout`: timers are `$.clock.every` and `after`.
- **How it refreshes.** A drawing is a snapshot: the hook runs again when its site's props or the terminal's width change, or when the mod calls `$.ui.invalidate`. Nothing redraws on a timer of its own and nothing watches a file, so a mod that shows outside data polls with `$.clock.every`. Redraws are throttled to 10 a second (30 for the band in the terminal) and coalesced.
- **Limits.** A hook's own time is 10 s; 100,000 characters of one tree are drawn; names are 64 characters; a hook that blocks the worker gets its mod unloaded.
- **Interactivity.** Buttons (with a one-key hotkey), text fields and dropdowns, live only while the pane or band has the keyboard; a `/command` the mod registers runs its function at once, with no turn, even while Claude works (`immediate: true`). Elements: `Box`, `Text` (bold, dim, colors, theme keys), `Markdown`, `Code`, `Link`, `Raster` (terminal only), `Svg` (Desktop only).
- **How it ships, and per agent.** A mod is a plugin. crew's plugin is already loaded into every Claude session on mac-studio: swancloud's `claude` wrapper passes `--plugin-dir ~/Code/github_afterthought/crew/main/plugin`. So naming a module in `plugin/hooks/hooks.json` makes crew a mod in every session there, crew agents and the user's own alike. A mod runs in every session that loads its plugin, so per agent means the mod asking who its session is (`CREW_AGENT`, `CREW_LABEL`) and drawing nothing for anyone else; a plugin's `userConfig` is per plugin, not per session. A `--plugin-dir` mod reloads in every running session whenever a file under the folder changes, so a landing reaches every agent at once, and each reload puts a dim line in that session's transcript. Claude Code writes its type declarations into `plugin/.claude-plugin/types/` (with their own `.gitignore`) and adds a `tsconfig.json` to the plugin's folder when it has none, which crew commits so the live checkout stays clean.
- **Cost.** Hooks run in process; nothing forks unless the mod calls `$.process`. A drawing is never sent to Claude, so a mod costs no tokens unless it calls a model or adds to a prompt.
- **Testing.** `claude plugin validate` reads the hooks and calls; `claude plugin test` runs `*.test.ts` files that stub every API call, mount a site on a named surface, and find or press its elements, with no session, sign-in or network.
- **What it cannot do.** Draw where Claude Code draws nothing; read the keyboard outside focus; change the permission prompt; watch a file; redraw faster than the throttle; see another session's screen. Nothing about it is sandboxed.

## What crew already computes

- `crew board` (`board.py`: `board_data`, `board_text`) makes a partition's four lanes from one read (`plan.rail_read` and the signals): Inception (unmoved signals by who captured them, the explorations on each kit's main), Bolt plan (open proposals and whom each waits on, planned bolts, the queue), Construction (each held bolt as a ledger: team, host, state, each unit's stage, tasks, slot and URL, its fixes, and every rail row as a ✓ or ✎ marker), Operation (landed in the last seven days) and attention (!). Every object names the teams it belongs to.
- The read is dear: `crew board --json --label swancloud` took 4.2 s and 2.35 CPU s (1.17 user, 1.18 sys) at load 48, and 14.9 s, 4.3 CPU s at load 40 counting devenv's entry; 29 KB of JSON.
- The rail tab (`crew _rail <label>` in the operator workspace) already runs that read once per partition every 30 s and on each run-record entry (`crew _views`), printing the rail and writing the board's frame, `~/.cache/crew/board/<label>.json`, which the board tab redraws from by its mtime (state.4: a frame is one redraw, not state).
- Live on mac-studio today: swancloud's rail loop has run since 2026-10-08 under a script older than the board tab, so no frame is written (`~/.cache/crew/board` is absent); madswan runs no rail loop. 31 Claude processes run here, several of them resumed bare by herdr (`claude --resume <id>`), which leaves `CREW_AGENT` out of Claude Code's own environment; crew's SessionStart hook keeps it in `~/.local/state/crew/sessions/<id>`.

## Design

**One read, many readers.** The rail tab's refresh, which already reads everything once per partition, also writes every agent's view of the board beside the frame: `~/.cache/crew/board/<label>.agents.json`, holding `read_at`, `stale_after_ms`, the line to add once stale, and `views`, by agent name, each a list of lines of `[text, style]` segments (style bold, dim or none), the board's own segment form. `board.agent_views` decides every view as a function of the board's data and starts no process (code.7), so its cases are in the logic tier (tests.11). The mod decides nothing of crew's: it finds its agent's lines and draws them.

**How the mod knows its agent.** `CREW_AGENT` and `CREW_LABEL`, which `crew-role` sets for every role (teams.6); for a session herdr resumed bare, the session's record under `~/.local/state/crew/sessions/`, found by `$.session.id()`. A session that is neither, or an agent with no view, draws nothing.

**One form, the board's glyphs.** The gutter as the board has it: ✓ an approval waits on the user, ✎ an answer does, ! needs attention, each with its card said at the line's end. A unit is one pip that fills as it goes, and a bolt is its units' pips in plan order:

| pip | stage |
|---|---|
| ○ | queued, waiting, ready: not begun |
| ◔ | amended, construct, planned: being designed |
| ◑ | code |
| ◕ | verify: every task ticked |
| ● | merged or landed |
| ? | unknown: its host did not answer |

**What each agent sees, in the band above its prompt** (from swancloud's board as read at 14:30; bold and dim lost here):

Every bolt's line is led by its product, the repository it builds, so crew's bolts and swancloud's read apart at a glance; in the planner's and the operator's views the team holding it follows, dim, and the teams are listed product by product.

A conductor (`<team>-conductor`): the bolt its team holds as a ledger, the open proposals naming its team (the one waiting on its agreement said so), what is planned and queued next for its kit, and attention for its host, its landed bolt or the plan.

```
  crew  ◕◔○○  curation-and-holds  0 of 4 merged
    ◕  a-queued-unit-can-take-a-signal  verify 3/3  unit-1
    ◔  curate-into-agenda  planned  unit-2
    ○  hold-unit-on-blocking-finding  ready
    ○  chores-beside-units-and-fixes  waiting
  crew  next  signals-arrive-and-curate-unattended  and 5 more planned
  queued  7 in crew
```

The planner: the plan in brief, each team's bolt as its pips, the open proposals and whom each waits on, what comes next by repository, the queue, attention.

```
swancloud plan  3 held  9 planned  10 queued  0 proposals open
  crew  crw-1  ◕◔○○  curation-and-holds  0 of 4 merged
  crew  crw-2  holds no bolt
  crew  crw-3  ●◑  a-crew-agents-questions-reach-the-user-on-cards  1 of 2 merged
  swancloud  swc-1  ●●◔◕○  every-host-reaches-every-other-by-its-tailnet-name  2 of 5 merged
  crew  next  signals-arrive-and-curate-unattended  and 5 more planned
  swancloud  next  pending-you-works-on-every-host  and 2 more planned
  queued  7 in crew, 3 in swancloud
```

The design agent: the signals no move has taken, by who captured them, and the first six explorations on the kits' mains, the rest counted (crew has no elaboration object of its own; the explorations are what the board reads for Inception).

The operator (`<label>-operator-<host>`): the partition's board in brief, a line to each lane, each team's bolt, the last landing, how many rail rows wait on the user (✓ to approve, ✎ to answer), attention.

```
swancloud board  read from mac-studio, macbook-pro
Inception  0 signals not moved  13 explorations
Bolt plan  0 proposals open  9 planned  10 queued
Construction
  crew  crw-1  ◕◔○○  curation-and-holds  0 of 4 merged
  crew  crw-2  holds no bolt
  crew  crw-3  ●◑  a-crew-agents-questions-reach-the-user-on-cards  1 of 2 merged
  swancloud  swc-1  ●●◔◕○  every-host-reaches-every-other-by-its-tailnet-name  2 of 5 merged
Operation  44 landed in seven days  the last a-card-is-whole-and-clean, Mon 08:24
```

Unit agents, team and main-level ops, dispatchers and the reviewer get no view. The band answers nothing, as the board answers nothing: no buttons, no commands.

**Refresh and cost.**
- Producer: the rail tab, as now, every 30 s or on an entry. Making all eight of swancloud's views from the read it already holds took 0.3 ms and 8.6 KB.
- Each agent's mod: a `$.fs.stat` of that file every 5 s (no process), a read and parse of the 8.6 KB only when its time moved, and a redraw of its band. The user's own sessions read their environment and one missing file once, at start.
- The alternative, each agent running `crew board` on a timer, would be about 2.35 CPU s a read: 31 sessions every 30 s is two to three cores held for the same data the rail tab reads once.
- Tokens: none. The band is never sent to Claude.

**When it cannot show.** Views more than 90 s old (three rail periods, the board tab's `STALE`) end with "read at HH:MM; the rail tab on <host> has not refreshed it since". With no views on the host, a crew agent's band says so in one dim line naming `crew operator up <label>` (read.1). An agent on a host other than its partition's rail tab finds no views: today every partition's teams and main level share its host (madswan and swancloud on mac-studio, wldn on chuck-herdr-alpha), so this bites only a partition split across hosts.

**Keeping it true.** A change to what crew models (bolts, units, stages, proposals, explorations and elaborations, cards, rail rows) updates `board.agent_views` and `status.js` in the same change, with their cases (`code.8`, on the user's word). CLAUDE.md's Crew section says so where a team building crew reads it, both files say so at their head, and a logic case reads `status.js` for every key it takes from the views file and fails when the views' shape and the mod part.

**Later, if wanted.** A `/board` command opening a pane with the whole board (the board's own lines, written into the same file), or a unit agent's one line. Neither is needed for what was asked.

## Estimate, and the prototype

About 500 lines in six parts, built on `recovery/mods`:

| part | lines |
|---|---|
| `board.agent_views` and its helpers in `board.py`, and `_views` writing the file; `row`, `gutter`, `stage_of`, `attention_text` lifted out of `board_text` | ~190 |
| logic cases in `tests/py/test_board.py` (14, one pinning every key the mod reads) | ~110 |
| the journey's check that the refresh writes the views (`t-journey-board`) | 3 |
| the mod, `plugin/hooks/status.js`, and `"modules"` in `hooks.json`, `plugin/tsconfig.json` | 95 |
| the mod's cases, `plugin/tests/status.test.ts` (3, `claude plugin test`), and the suite's task `mod` that runs them (`tests/mod`, `tests/moon-tasks`) | ~80 |
| README | 1 paragraph |

`claude plugin validate plugin` passes (hooks `session.start`, `ui.render{component=AbovePrompt}`; calls `$.clock`, `$.env.get`, `$.fs.read`, `$.fs.stat`, `$.session.id`, `$.ui.invalidate`, `$.ui.resolve`; reads `CREW_AGENT`, `CREW_LABEL`, `HOME`). The mod's three cases pass, each failing when the mod draws the wrong view, and run in crew's suite as the task `mod` (`tests.11`'s details: the host's `claude` as a test runner only). The logic tier is 682 passed, and `tests/suite --affected` 20 passed, 0 failed.

The user saw it on a real screen on 2026-10-12 ("That looks great") and asked that each bolt be told apart by its product and team, which every bolt's line now leads with.

## For the user

1. Land it as a bolt? It changes the plugin every session on mac-studio loads, so it reaches every running agent the moment it lands, and each landing that touches `plugin/` afterwards puts one dim reload line in each session's transcript. Recommendation: yes, as a small bolt of its own for a crew team, these two commits as its one unit.
2. After it lands, bring each partition's operator workspace up again (`crew operator up swancloud`, `crew operator up madswan`, and wldn's on the box), so the rail tab runs the loop that writes the frames: today none does. Recommendation: yes, by main-level ops on the landing.
3. Is the pip form right? ○ ◔ ◑ ◕ ● read as a stage at a glance, but they are not ASCII. Recommendation: keep them; the board's own markers are ✓ ✎ already.
4. Anything for unit agents or ops? Recommendation: not yet; add a `/board` pane only if the band proves too small.
