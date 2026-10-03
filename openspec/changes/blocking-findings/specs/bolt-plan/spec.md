# Spec Delta

## MODIFIED Requirements

### Requirement: The file's order and dependencies are the plan
A bolt's units SHALL be built in the order they appear in the file, and bolts SHALL be given out in the order they appear. A unit's `After` SHALL name units of the same bolt. The unit SHALL NOT start until each of them has merged into the bolt, and a unit that had already started when it gained the dependency SHALL NOT merge until each has. A unit with no `Bolt` SHALL be queued work.

#### Scenario: A dependency not yet merged
- **WHEN** unit B has `After: A` and A is in code
- **THEN** B's stage is `waiting`, and crew refuses to start B

#### Scenario: Queued work
- **WHEN** a unit is added with no bolt
- **THEN** `crew bolts` lists it under the queue of its repo

#### Scenario: A dependency gained in flight
- **WHEN** unit B is in code and gains `After: C`, a unit added to the bolt because of a finding in B
- **THEN** B's code and verify stages may run, and `crew unit run B merge` is refused until C has merged into the bolt
