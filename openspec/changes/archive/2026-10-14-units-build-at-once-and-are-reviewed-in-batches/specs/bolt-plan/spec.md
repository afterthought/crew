# Spec Delta

## MODIFIED Requirements

### Requirement: The file's order and dependencies are the plan
A bolt's units SHALL be ordered by the file: bolts SHALL be given out in the order they appear, and a unit is ahead of every unit after it in its bolt. A unit's `After` SHALL name units of the same bolt that it builds on, or that a forecast conflict has put it after. The unit's construct SHALL NOT start until each of them has finished construct, its OpenSpec change committed, and SHALL NOT wait for any of them to merge. The unit SHALL NOT merge into the bolt until each of them has merged. A unit with no `Bolt` SHALL be queued work.

#### Scenario: A dependency still in construct
- **WHEN** unit B has `After: A`, and A's construct has not committed
- **THEN** B's stage is `waiting`, and crew refuses to start B's construct

#### Scenario: A dependency constructed
- **WHEN** unit B has `After: A`, and A's change is committed while A is in code
- **THEN** crew accepts B's construct

#### Scenario: A dependency not yet merged
- **WHEN** unit B has `After: A`, B is verified and A has not merged into the bolt
- **THEN** crew refuses B's merge, naming A

#### Scenario: Queued work
- **WHEN** a unit is added with no bolt
- **THEN** `crew bolts` lists it under the queue of its repo

## REMOVED Requirements

### Requirement: The user's approval is a commit
**Reason**: Code no longer waits on the user's review of each unit (record 0014, D5). The user reviews constructed changes in batches, and feedback amends the unit in flight with no re-approval.
**Migration**: `crew unit approve` is removed. `Reviewed-by` commits already on unit branches are left as they are and read by nothing. An amended unit's mark stops counting once its construct has committed again.
