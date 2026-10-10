## MODIFIED Requirements

### Requirement: A unit's stage is read from the kits
crew SHALL derive each unit's stage from its kit on the team's host. The first rule that holds is the unit's stage:

- `landed`: main holds the unit's OpenSpec change, open or archived;
- `merged`: `bolt/<bolt>` holds it;
- `verify`: every task is ticked;
- `code`: some task is ticked;
- `approved`: the change's planning is complete, and a review has been approved since the bolt;
- `review`: the change's planning is complete, with no approval;
- `construct`: the unit's worktree exists;
- `ready` or `waiting`: neither, depending on its `After` units;
- `queued`: the unit has no bolt.

A task, a ticked task and a complete planning mean what OpenSpec means by them. crew SHALL read them from the change's files without the `openspec` command line when the change uses OpenSpec's own spec-driven workflow, and through `openspec` otherwise; on the same worktree both readings SHALL agree.

#### Scenario: An amended unit with ticked tasks
- **WHEN** a unit in code is marked amended and construct has been run again and has committed
- **THEN** its stage is `review`, though some of its tasks are ticked

#### Scenario: A squashed merge
- **WHEN** a unit was merged into its bolt with `wt merge`, and its worktree and branch were removed
- **THEN** its stage is still `merged`, read from the change folder on `bolt/<bolt>`

#### Scenario: Nothing kept by hand
- **WHEN** a coder ticks the last task of a unit's change
- **THEN** `crew bolts` shows the unit in `verify`, and no file was edited to say so

#### Scenario: A task OpenSpec counts is counted
- **WHEN** a unit's `tasks.md` holds an indented sub-task `  - [ ] 1.1.1 …`, a numbered `1. [ ] …` or a `- [~] …`
- **THEN** crew counts each as a task not done, as `openspec list` does, and the unit stays in `code`

#### Scenario: A link is not a task
- **WHEN** a unit's `tasks.md` holds a bullet `- [design](./design.md)`
- **THEN** crew does not count it, as `openspec list` does not

#### Scenario: Planning complete without specs
- **WHEN** a unit's change declares `skip_specs: true` in its `.openspec.yaml` and has its proposal, design and tasks
- **THEN** its planning is complete, as `openspec status` says, and the unit is in `review`

#### Scenario: Another workflow
- **WHEN** a unit's change names a workflow other than spec-driven, or its kit redefines spec-driven
- **THEN** crew reads that unit's tasks and planning through `openspec`, and every other unit's from its files

#### Scenario: The readings are held together
- **WHEN** the suite runs
- **THEN** a test reads a set of changes covering every case above both ways, on the same worktrees, and fails on any difference

## ADDED Requirements

### Requirement: A command reads each kit and the plan once
A crew command SHALL read each kit once and fetch the state branch once on each host it runs on, however many steps it has. A step that makes or removes a worktree in a kit SHALL leave the next step to read that kit again. A plan write SHALL start from the tip the command holds and fetch again only when its push is refused. A wait, the rail tab's loop and `crew events --follow` SHALL read afresh each time they look.

#### Scenario: Status with three units in flight
- **WHEN** `crew status <team>` runs for a team with three units in flight
- **THEN** the team's host reads the kit once and fetches the state branch once, and `openspec` is not started

#### Scenario: Running a stage
- **WHEN** `crew unit run <unit> construct` frees finished slots, tidies worktrees, checks the stage and makes the unit's place
- **THEN** the team's host fetches the state branch once and reads the kit once before the place is made

#### Scenario: A write after the plan moved
- **WHEN** another agent's write lands on the state branch after a command fetched it, and the command then writes
- **THEN** the command's push is refused, it fetches the new tip and applies its change there, as any write does

#### Scenario: A wait sees what changes while it waits
- **WHEN** `crew unit wait <unit>` is waiting and the coder ticks the last task
- **THEN** the wait's next look reads the new head and returns with the delivered end

#### Scenario: Nothing is left behind
- **WHEN** a command ends, whether it succeeded or was refused
- **THEN** what it kept for its steps is gone, and the next command reads afresh
