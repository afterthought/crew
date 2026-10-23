## Why

When crew restarts a standing agent for an update and the agent is slow to exit, the restart gives up and starts nothing, but the `/exit` and Ctrl+C it typed end the agent moments later. The pane is left a bare shell and the agent stays down until someone runs `crew revive`. On deneb on 2026-10-23 swancloud's operator and fwn-1's conductor both stayed down this way for about nine hours (signal 2026-10-23-chuck-mac-studio-8d53f475/01).

## What Changes

- A restart whose agent has not exited when its stop gives up keeps watching the agent, for up to ten minutes, and starts it on crew as it now is the moment it exits: resumed with its conversation and told what changed, a conductor fresh and greeted, as any restart for an update is.
- An agent still running when that watch ends runs on as it was, still due a restart. The restart's log says so, truthfully: it did not exit, it runs on, and the end of its next turn hands it back.
- A restart that gave up leaves a mark naming the session it typed its exit into. A later restart that finds the agent exited, its pane kept and no other start since, starts it without a stop, so an exit later than the watch (an `/exit` that waited behind a turn) still ends with the agent running.
- Nothing else changes about a stop: `stop` still fails rather than lies when the agent did not exit (`teams.2`), and every other caller of it behaves as now.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `host-holds-and-updates`: a due agent's restart ends with the agent running, on the new crew or, when it cannot be ended, as it was; it never leaves the pane a shell.

## Impact

- `plugin/lib/hold.py`: `renew`, a new decision for starting an agent the restart's own exit ended, and the mark under `~/.local/state/crew/renew/`.
- `plugin/lib/crew.py`: `Agents`, a watch for an agent's exit after its stop gave up.
- `tests/py/test_hold.py`, `tests/t-hold.sh`, and the stub herdr (`tests/stubs/herdr`), which learns an agent that is slow to exit.

## Touches

```
plugin/lib/hold.py
plugin/lib/crew.py
tests/py/test_hold.py
tests/t-hold.sh
tests/stubs/herdr
```
