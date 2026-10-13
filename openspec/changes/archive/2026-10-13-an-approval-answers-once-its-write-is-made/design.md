# Design

## Context

See proposal.md for why. An amendment's `after` runs once its plan write has landed; today it runs `crew unit run <unit> construct [--force]` on the team's host through `crew.on_machine` and reads the slot from what that printed, so the approval's command lasts as long as `run_unit_stage` does there: the team's read, the old agent's stop, the new agent's start and the prompt's `send_taken`.

Rules relied on: `plan.15` and `code.9` as amended 2026-10-13, `teams.15` (the start is read on the team's host, taking its time there), `teams.1` (a team taken down starts nothing), `record.1` (a refused start is recorded), `code.3` (a team's command runs on its host as the one asking), `code.7`, `tests.4`, `tests.8`, `tests.12`. Pages whose area this touches: `plan.md`, `core.md`.

## Decisions

### A hand-off entry on the team's host

`crew _construct-again <team> <unit> --by <by> [--force]` is a team command, run as the one asking (`crew_argv`). It refuses at once, recording the refused start and telling the conductor, when the team is down, since that is read from a file. Otherwise it writes `handed/<unit>` in the team's state, `{"by", "log", "at"}`, starts the same entry with `--handed` through `bash crew`, in a session of its own with its output in `handed/<unit>.log` and no descriptor of the command's, so ssh and the asker's shell return as soon as the command does, and answers with the line that names the host, the conductor's word to come and the wait.

### The handed process

The `--handed` process writes its pid into the marker, takes `handed/.lock` so the constructs one approval handed start one at a time, as they did in turn, and runs `run_unit_stage` with its words captured. When the construct starts it removes the marker; when it did not, it writes why into it (a refusal's words, a stop's last line, or an unexpected error, its traceback in the log). Then it tells the conductor what started or why not (`amend_told`, `amend_tell`), as the approval did.

### What a wait and a stage read of it

`handed_state` is a function of the marker, whether its pid is alive and the time: nothing handed; failed, with why; starting while the pid is alive, or for `HAND_NAMED` seconds after the hand-off before the process has named itself; gone otherwise, naming the log. `crew unit wait` polls it once a second while it is starting, within its own timeout, then answers a failure or a gone process in its words, removing the marker, or waits on the stage with what is left of the timeout. `crew unit run` refuses any stage of the unit while it is starting, naming the wait, and removes the marker of one that failed or is gone, since this run is the one that starts it.

## Risks / Trade-offs

- A hand-off whose process never starts is taken as gone after `HAND_NAMED` seconds, a bound in the code rather than in any test (`tests.8`); within it a stage of the unit is refused and a wait waits.
- The approver no longer reads the start: what started reaches the conductor from the team's host, and the approver's command says only that it was handed.
