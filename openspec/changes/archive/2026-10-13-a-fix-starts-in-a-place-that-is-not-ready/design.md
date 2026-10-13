# Design

## Context

See proposal.md for why and record 0028 for the decision. `make_place` makes a worktree with git on the team's host, then runs the kit's readying steps there (`kit.readying`: the declared toolchain, moon's version, `moon setup`), refusing the command on the first that fails with `kit.step_failed`'s words. `fix_place` calls it for a fix, then refuses a place that is not on the fix's own branch made from the bolt (`own_place`). `fix_run` starts the fix's code stage with the prompt `Fix: <words>`.

Rules relied on: `teams.3` and `plan.17` as amended with record 0028, `read.4` (a place not the fix's own stays refused), `code.7` (what the agent is told is a function of facts), `teams.15` (the prompt is taken or sent again, as any stage's), `tests.4`, `tests.12`. Pages whose area this touches: `teams.md`, `plan.md`.

## Decisions

### make_place says what failed instead of refusing, for a fix

`make_place` takes `unready`: with it, the first readying step that fails stops the readying and its words are returned rather than raised; without it, as for a unit's and a chore's place, it refuses as before. It returns nothing once the place is ready. `fix_place` passes `unready`, and still refuses a place that is not the fix's own.

### What the agent is told

`kit.unready_said(place, why)` puts the step's words on one line, lines joined by " / ", since they go in a prompt: the place could not be made ready, so the kit's tools may not run in it, the step and its last lines, and that repairing it may be part of the fix. `plan.fix_prompt(words, place, unready)` is the prompt: `Fix: <words>`, then those words when the place is not ready. The command prints the place's first line of what failed and that the agent starts on the fix all the same. The fix's start is recorded as any start, with no refusal.

## Risks / Trade-offs

- A fix's agent may start where nothing of the kit's runs; it is told so, and the fix is its repair. sluice's run on the fix's submission reads the merged tree's own declaration, so the bolt's checks run on the repaired toolchain.
