## ADDED Requirements

### Requirement: A construct reads every source it is handed, and what each points at
A construct SHALL read each of its unit's sources, and SHALL open what each points at: a page or file it names, an artifact's link, a branch. It SHALL read a page as committed on its repository's main when the stage starts, not the bolt's copy in its own worktree, and a signal with `crew signal show`. A construct run again SHALL read the sources afresh.

#### Scenario: A signal points at a page in another repo
- **WHEN** a unit's sources are a signal and the signal names a page in another repo where the user's design lives
- **THEN** the construct reads the signal with `crew signal show`, opens that page, and cites both

#### Scenario: A record lands after the bolt is cut
- **WHEN** the design agent commits a record on the kit's main after the unit's bolt was cut, and the unit names that record as a source
- **THEN** the unit's construct reads the record as main holds it, not the bolt's older copy in the unit's worktree

### Requirement: A construct stops on a source it cannot open
When a construct cannot open one of its unit's sources, or something a source points at, it SHALL stop through `crew needs`, naming what it could not open and which source named it, and SHALL NOT write the change from the intent in its place.

#### Scenario: A signal names only a conversation's id
- **WHEN** a unit's source is a signal whose words point at a conversation by its id, and nothing names what that conversation made
- **THEN** the construct commits no change and stops through crew, naming the conversation and the signal

### Requirement: A construct builds from its sources where the intent says more or otherwise
Where a unit's intent says more than its sources, or says something they contradict, its construct SHALL write the change from the sources, and its final message SHALL open with the difference: what the intent says, what the sources say instead, and which source. A construct whose intent and sources agree SHALL say nothing of a difference.

#### Scenario: The intent names a measure the sources do not
- **WHEN** a unit's intent names a measure and its sample points, and the design its sources lead to shows a different measure
- **THEN** the change builds the sources' measure, and the construct's final message opens by naming the intent's measure, the sources', and the source

#### Scenario: Intent and sources agree
- **WHEN** a unit's intent names only the outcome its sources describe
- **THEN** the construct writes the change and its final message names no difference
