## MODIFIED Requirements

### Requirement: A unit's stage is read from the kits
crew SHALL derive each unit's stage from its kit on the team's host. The first rule that holds is the unit's stage:

- `landed`: main holds the unit's OpenSpec change, open or archived;
- `merged`: `bolt/<bolt>` holds it archived, as the unit's own merge leaves it;
- `amended`: the plan marks the unit amended, and construct has not been run again;
- `construct`: construct has been run again on an amended unit, and has not yet committed;
- `verify`: every task is ticked;
- `code`: some task is ticked;
- `planned`: the change's planning is complete;
- `construct`: the unit's worktree exists;
- `ready` or `waiting`: neither, depending on whether each of its `After` units has finished construct;
- `queued`: the unit has no bolt.

A unit whose change `bolt/<bolt>` holds open, carried there inside another unit's merge, has not merged: it reads at its own stage, from its worktree, or, once that is gone, from its change as the bolt holds it, its planning complete.

A task, a ticked task and a complete planning mean what OpenSpec means by them. crew SHALL read them from the change's files without the `openspec` command line when the change uses OpenSpec's own spec-driven workflow, and through `openspec` otherwise; on the same worktree both readings SHALL agree.

#### Scenario: A squashed merge
- **WHEN** a unit's commits reached its bolt inside another unit's merge, its change open there with every task ticked, and its worktree and branch were removed
- **THEN** its stage is `verify`, read from the change on `bolt/<bolt>`, and not `merged`

#### Scenario: Merged by its own merge
- **WHEN** a unit's merge archived its change and the bolt holds it archived
- **THEN** its stage is `merged`

#### Scenario: Nothing kept by hand
- **WHEN** a coder ticks the last task of a unit's change
- **THEN** `crew bolts` shows the unit in `verify`, and no file was edited to say so

#### Scenario: An amended unit with ticked tasks
- **WHEN** a unit in code is marked amended and construct has been run again and has committed
- **THEN** its stage is `code`, read from its tasks, and no approval is asked

#### Scenario: A constructed unit
- **WHEN** a unit's construct has committed a change whose planning is complete, and no task is ticked
- **THEN** its stage is `planned`, and its code may start

#### Scenario: A task OpenSpec counts is counted
- **WHEN** a unit's `tasks.md` holds an indented sub-task `  - [ ] 1.1.1 …`, a numbered `1. [ ] …` or a `- [~] …`
- **THEN** crew counts each as a task not done, as `openspec list` does, and the unit stays in `code`

#### Scenario: A link is not a task
- **WHEN** a unit's `tasks.md` holds a bullet `- [design](./design.md)`
- **THEN** crew does not count it, as `openspec list` does not

#### Scenario: Planning complete without specs
- **WHEN** a unit's change declares `skip_specs: true` in its `.openspec.yaml` and has its proposal, design and tasks
- **THEN** its planning is complete, as `openspec status` says, and the unit is in `planned`

#### Scenario: Another workflow
- **WHEN** a unit's change names a workflow other than spec-driven, or its kit redefines spec-driven
- **THEN** crew reads that unit's tasks and planning through `openspec`, and every other unit's from its files

#### Scenario: The readings are held together
- **WHEN** the suite runs
- **THEN** a test reads a set of changes covering every case above both ways, on the same worktrees, and fails on any difference
