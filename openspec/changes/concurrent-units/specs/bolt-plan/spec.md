# Spec Delta

## MODIFIED Requirements

### Requirement: The file's order and dependencies are the plan
A bolt's units SHALL be merged in the order they appear in the file where nothing else orders them, and bolts SHALL be given out in the order they appear. A unit's `After` SHALL name units of the same bolt whose code the unit builds on. The unit's construct SHALL NOT wait on them. Its code SHALL NOT start until each of them has finished construct, its OpenSpec change committed, and it SHALL NOT merge into the bolt until each of them has merged. A unit with no `Bolt` SHALL be queued work.

#### Scenario: A dependency still in construct
- **WHEN** unit B has `After: A`, B's change is committed and A's construct has not committed
- **THEN** B's stage is `waiting`, and crew refuses to start B's code

#### Scenario: A dependency constructed
- **WHEN** unit B has `After: A`, and A's change is committed while A is in code
- **THEN** crew accepts B's code

#### Scenario: Construct does not wait
- **WHEN** unit B has `After: A` and A has no change yet
- **THEN** crew accepts B's construct

#### Scenario: A dependency not yet merged
- **WHEN** unit B has `After: A`, B is verified and A has not merged into the bolt
- **THEN** crew refuses B's merge, naming A

#### Scenario: Queued work
- **WHEN** a unit is added with no bolt
- **THEN** `crew bolts` lists it under the queue of its repo

### Requirement: A unit's stage is read from the kits
crew SHALL derive each unit's stage from its kit on the team's host. The first rule that holds is the unit's stage:

- `landed`: main holds the unit's OpenSpec change, open or archived;
- `merged`: `bolt/<bolt>` holds it;
- `amended`: the plan marks the unit amended, and construct has not been run again;
- `construct`: construct has been run again on an amended unit, and has not yet committed;
- `verify`: every task is ticked;
- `code`: some task is ticked;
- `waiting`: the change's planning is complete, and some unit it comes after has not finished construct;
- `planned`: the change's planning is complete;
- `construct`: the unit's worktree exists;
- `ready`: the unit is in a bolt, with no worktree;
- `queued`: the unit has no bolt.

#### Scenario: A squashed merge
- **WHEN** a unit was merged into its bolt with `wt merge`, and its worktree and branch were removed
- **THEN** its stage is still `merged`, read from the change folder on `bolt/<bolt>`

#### Scenario: Nothing kept by hand
- **WHEN** a coder ticks the last task of a unit's change
- **THEN** `crew bolts` shows the unit in `verify`, and no file was edited to say so

#### Scenario: An amended unit with ticked tasks
- **WHEN** a unit in code is marked amended and construct has been run again and has committed
- **THEN** its stage is `code`, read from its tasks, and no approval is asked

#### Scenario: A constructed unit
- **WHEN** a unit's construct has committed a change whose planning is complete, and no task is ticked
- **THEN** its stage is `planned`, and its code may start once its After units have finished construct

## REMOVED Requirements

### Requirement: The user's approval is a commit
**Reason**: Code no longer waits on the user's review of each unit (record 0014, D5). The user reviews constructed changes in batches, and feedback amends the unit in flight with no re-approval.
**Migration**: `crew unit approve` is removed. `Reviewed-by` commits already on unit branches are left as they are and read by nothing. An amended unit's mark stops counting once its construct has committed again.
