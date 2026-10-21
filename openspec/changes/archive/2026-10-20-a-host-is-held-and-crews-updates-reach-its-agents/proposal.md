# Proposal

## Why

The user, 2026-10-20, in the fleet-releases session: "We need to be able to hit the brakes and tell everybody to stop what they're doing so we can do something like upgrade the herder server without messing anybody up", and "We need to be able to push updates out to crew and have it just work. Right now it means stopping every team one by one ... when they find a good point to stop, they do and something restarts them", and "It would also be nice if the mods would show the version of crew that was running". Told the draft, they said "let's implement the new design before starting the teams". It is the graceful shutdown `teams.6` names as not built.

## What Changes

- `crew hold <host>|--all "<why>"` holds each host named: crew starts no agent there until `crew go`, refusing every command that would, and every standing agent up there is told to finish the step it is in and start nothing new. A stage already running ends as it would. `--now` ends every crew agent there at once.
- `crew hold status` says what still works on each host; `crew hold wait` waits until each is quiet and then ends every crew agent there, its panes kept, so herdr can be restarted or the host rebooted.
- `crew go <host>|--all` lifts the hold, brings each standing agent back with its conversation, greeted, or tells one still up to carry on, and runs the consoles' tabs again.
- An agent's start records the crew it loaded and what it was started with. A standing agent whose brief, model, effort or folders changed, or whose loaded part of crew's plugin changed, is due a restart, which crew gives it at its next stop: at the end of its turn (crew's Stop hook), and for one sitting idle, when crew's checkout or the teams file moves (the console's rail tab) or on `crew update`. A conductor restarts fresh; every other standing role resumes its conversation and is told what changed.
- Each agent's band shows the crew it started on, and the version it is restarted on at its next stop once it is due; every band on a held host opens with the hold.

## Capabilities

### New Capabilities

- `host-holds-and-updates`: a host's hold, the restart an update makes due, and the crew an agent's band shows.

## Impact

`plugin/lib/hold.py` (new), `plugin/lib/crew.py` (the hold, `crew_version`, `launch_digest`, `starts`, `update_due`, `due_of`, `agents_here`, `Agents.start`), `plugin/lib/plan.py` (`not_held` on every start), `plugin/lib/board.py` (`here_read`, the bands), `plugin/lib/transcript.py` (`started_commands`), `plugin/lib/record.py` (`host/`), `plugin/bin/crew` and `crew-role`, `plugin/hooks/` (`session-start`, the new `stop`, `hooks.json`); README, the skill, CLAUDE.md, `teams.md`.
