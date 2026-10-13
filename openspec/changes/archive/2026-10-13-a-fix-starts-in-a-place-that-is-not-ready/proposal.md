# A fix starts in a place that is not ready

## Why

Record 0028, point 1. A fix is how a bolt is repaired: a bolt takes main only by a fix whose agent merges main into its place and submits it to the bolt (`plan.8`, `teams.5`). But every stage's place is made from the bolt, and readying a place refuses the stage when a step fails (`plan.17`), so a bolt whose own toolchain is broken refuses every fix before an agent starts, and main cannot reach it through crew (wldn, 2026-10-13, signal 2026-10-13-swancloud-planner-2e24fc2d/02).

## What Changes

- **A fix's agent starts once its place is made, whether or not the place could be made ready.** The step that failed and its last lines go in its prompt, after the fix's words, on one line; the command says the place is not ready and that the agent starts all the same.
- **A unit's or chore's stage stays refused** until its place is ready, as record 0023 point 4 has it.
- **A place that is not the fix's own stays refused** (`read.4`, `teams.3`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: "Fixes during a bolt are built beside its units" starts a fix's agent in a place that could not be made ready, told what failed.
- `kit-toolchain`: "A worktree is made ready through its kit's declaration" refuses a unit's or chore's stage on a failed step, and not a fix's.

## Impact

- `plugin/lib/plan.py` (`make_place`, `fix_place`, `fix_prompt`, `fix_run`), `plugin/lib/kit.py` (`unready_said`), `tests/py/test_fix.py`, `tests/t-journey-fix.sh`.
- `plugin/bin/crew`'s usage, `README.md`, `docs/architecture/teams.md` (`teams.3`), `docs/architecture/plan.md` (`plan.17`), `docs/architecture/_open.md`.

## Touches

```
plugin/lib/plan.py
plugin/lib/kit.py
tests/py/test_fix.py
tests/t-journey-fix.sh
plugin/bin/crew
README.md
docs/architecture/teams.md
docs/architecture/plan.md
docs/architecture/_open.md
```
