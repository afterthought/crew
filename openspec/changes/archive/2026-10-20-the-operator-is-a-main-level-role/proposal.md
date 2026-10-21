# Proposal

## Why

The operator agent ran once per host and partition, `<label>-operator-<host>`, in an operator session of its own. After swancloud moved both main levels and deneb's teams into deneb's work sessions, those operator sessions held nothing but an agent that only carries. Record 0035, accepted by the user on 2026-10-20 ("we need to make the console change first"), makes the operator one main-level role per partition, the partition's one door.

## What Changes

- `<label>-operator` is a main-level role: `crew main up` starts it beside the design agent, the planner and ops, one tab of the `<label>` workspace, greeted as they are; `crew main down` ends it; `crew revive` brings it back as it does them.
- Every brief names the operator as the partition's door, `<label>-operator`; a conductor that waits on the user with no card tells it.
- No host's operator agent is started apart from it: `crew operator up` no longer starts an agent (the console change).
- The board's view for an operator is `<label>-operator`'s.

## Capabilities

### Modified Capabilities

- `operator-agent`: the operator is a main-level role, started and ended with the main level.
- `main-level`: the main level holds four standing roles.

## Impact

`plugin/lib/crew.py` (`MAIN_STANDING`, `place_of_agent`, `label_of_agent`, `standing_greeting`, `launch`, `team_tokens`, `main_tokens`), `plugin/lib/plan.py` (`main_cmd`, `role`, `where_of`), `plugin/lib/board.py` (`agent_views`), `plugin/roles/operator.md`, `plugin/roles/conductor.md`; README, the skill, the usage.
