# An approval answers once its write is made

## Why

`plan.15` as amended 2026-10-13 and `code.9`. An approved amendment runs its unit's construct again by the approval's own act, and today the approval's command waits for it over ssh: the old agent ended, the new one's session up, its prompt sent and taken. wldn's `crew plan approve 276` answered 3 min 19 s after its plan write, past the two minutes an agent's shell gives a command, so the planner did not know what had been done and approved the next proposal by hand meanwhile (signal 2026-10-13-swancloud-planner-6eabf8e7/01).

## What Changes

- **The amendment hands its construct to the team's host and answers.** `op_unit_amend`'s `after` runs `crew _construct-again <team> <unit> --by <what amended it> [--force]` there, which writes a marker in the team's state and starts a process of its own that outlives the command; the command answers once that is done.
- **The host's process starts construct again and tells the conductor**, one handed construct at a time on a team: what started, or why nothing did, as the approval's command told it before. A team taken down is said and the conductor told at the hand-off itself, with nothing started.
- **`crew unit wait <unit>` waits for a handed construct to start**, then on its stage, within the same timeout, and says why when it did not start; a stage of the unit run while it starts is refused, naming the wait.
- **A host that does not answer the hand-off** is said, and the conductor told, from the approver's side, as before.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-plan`: "A unit's intent is amended through crew" hands an amended unit's construct to its team's host and answers, with `crew unit wait` waiting for its start.

## Impact

- `plugin/lib/plan.py` (`op_unit_amend`, `construct_again`, `amend_tell`, `HAND_NAMED`, `handed_state`, `construct_handed_state`, `handed_path`, `construct_hand`, `construct_handed`, `unit_run`, `unit_wait`, the `_construct-again` parser and command), `plugin/bin/crew` (`_construct-again`), `plugin/roles/conductor.md`, `README.md`, `docs/architecture/plan.md` (`plan.15`), `docs/architecture/core.md` (`code.9`), `docs/architecture/_open.md`, `tests/py/test_amend.py`, `tests/t-journey-plan.sh`, `tests/t-journey-prompts.sh`.

## Touches

```
plugin/lib/plan.py
plugin/bin/crew
plugin/roles/conductor.md
README.md
docs/architecture/plan.md
docs/architecture/core.md
docs/architecture/_open.md
tests/py/test_amend.py
tests/t-journey-plan.sh
tests/t-journey-prompts.sh
```
