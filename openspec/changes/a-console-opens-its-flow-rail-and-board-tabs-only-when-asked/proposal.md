# Proposal

## Why

The user does not use the console's flow, rail and board tabs now, and asked that crew stop opening them by default while keeping them for when they are wanted again (the user, 2026-10-28, through swancloud-ops: "the console's flow, rail and board tabs are not used now (they may be wanted later, so not opened by default rather than removed)"; signal 2026-10-28-swancloud-planner-29c28e8c/01). The rail tab's loop is also what keeps the board's frame and every agent's band fresh, sweeps card sessions and hands out due restarts, so a tab nobody opens cannot be the only thing that does that work.

The design agent ruled where that work goes (crew 42b5fc1d, `state.4`'s reading of 2026-10-28): one follower on a host serves every partition's tabs there, and crew requires no service for it (`roles.6`). Where the host runs the follower as a job of its own, swancloud's, as it runs the board's word listener (record 0038 point 4), it runs with no tab and writes the rail's text as a frame beside the board's, and the tabs draw the frames when the user opens them. Where no job of the host's runs it, the rail tab's own loop is the follower, as today, so a host never has two followers and never none (record 0047, move 6).

## What Changes

- `crew console up <label>` opens the console workspace with a shell tab alone, crew on its path. It opens the `flow`, `rail` or `board` tab only when the user names it (`crew console up wldn rail`), each opened as it is today. A tab already open is kept by every later `crew console up`, named or not, and a tab whose pane a restart left a bare shell runs its command again, as today. A tab the user closed stays closed.
- The console's own choice: while no host job runs the follower, `crew console up` also opens the rail tab, since that tab is then the host's follower; while one does, it opens nothing the user did not name.
- A new headless follower, `crew _follow`, the command swancloud's host job runs: every 30 seconds and on each run-record entry, for every partition with an operator session on the host, it does what the rail tab's refresh does today (one read, card sessions swept, the board's frame and the agents' views written, due restarts handed out) and also writes the rail's text as a frame of its own.
- One follower per host: whoever follows holds the host's follower lock for as long as it runs and says on it whether it is the host's job or a rail tab. A second follower waits for the lock rather than reading too.
- The rail tab draws the rail frame, as the board tab draws the board's, headed with its age once it is stale. While no one holds the follower lock, the rail tab takes it and follows itself, as today.
- What crew says when there is no frame, or a stale one, names the host's follower rather than the rail tab, in the board tab, in the agents' bands and in crew's mod.
- `crew rail`, `crew board` and `crew events` on the command line, the board's word listener, `crew console down` and the main level's panes are unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `operator-agent`: the console opens with a shell tab alone; its flow, rail and board tabs open when the user names them, kept across later runs; the rail tab opens of itself only while no host job follows.
- `crew-board`: the rail and the board come from the host's one follower, run by a host job with no tab or by the rail tab's loop where no job runs, never two; the rail is written as a frame the rail tab draws.
- `card-sessions`: the sweep of closed cards' sessions happens on each refresh of the host's follower, wherever it runs.

## Impact

- `plugin/lib/plan.py` (`console_cmd`, its parser), `plugin/lib/hold.py` (crew go opens the console as `console_cmd` now takes it), `plugin/lib/board.py` (the follower, the rail frame, the rail tab's drawing, the lock), `plugin/bin/crew` (the `_follow` and `_rail` dispatch, the help).
- `plugin/hooks/status.js`: only its words about who writes the views.
- `plugin/roles/operator.md` and `plugin/skills/crew/SKILL.md`: how the rail tab is opened.
- Tests: logic cases in `tests/py/`, and `tests/t-journey-main.sh` and `tests/t-journey-board.sh` on the stubs; `tests/moon.yml` regenerated.
- swancloud's unit a-host-runs-crews-follower-as-its-own-job runs `crew _follow` as each host's job; this change lands first, and until it does every host keeps following through its rail tab.

## Touches

```
plugin/lib/plan.py
plugin/lib/hold.py
plugin/lib/board.py
plugin/bin/crew
plugin/hooks/status.js
plugin/tests/**
plugin/roles/operator.md
plugin/skills/crew/SKILL.md
README.md
tests/py/**
tests/t-journey-main.sh
tests/t-journey-board.sh
tests/t-briefs.sh
tests/moon.yml
```
