## ADDED Requirements

### Requirement: A construct reads its unit's sources from main as they stand when it starts
A construct SHALL read each of its unit's sources as committed on that source's repository's main when the stage starts, and SHALL NOT take a source from its own worktree, which holds the bolt's copy as it was when the bolt was cut. A construct run again SHALL read the sources afresh.

#### Scenario: A record lands after the bolt is cut
- **WHEN** the design agent commits a record on the kit's main after the unit's bolt was cut, and the unit names that record as a source
- **THEN** the unit's construct reads the record as main holds it, not the bolt's older copy in the unit's worktree

#### Scenario: Construct run again after a record changed
- **WHEN** a source of a unit in review is amended on main, and construct runs again on the unit
- **THEN** the new construct reads the amended source

### Requirement: A construct builds from its sources where the intent says more or otherwise
Where a unit's intent says more than its sources, or says something they contradict, its construct SHALL write the change from the sources, and its final message SHALL open with the difference: what the intent says, what the sources say instead, and which source. A construct whose intent and sources agree SHALL say nothing of a difference.

#### Scenario: The intent names a mechanism the record does not
- **WHEN** a unit's intent names a measure and its sample points, and the record its sources name says the page shows a different measure
- **THEN** the change builds the record's measure, and the construct's final message opens by naming the intent's measure, the record's, and the record

#### Scenario: Intent and sources agree
- **WHEN** a unit's intent names only the outcome its sources describe
- **THEN** the construct writes the change and its final message names no difference
