## ADDED Requirements

### Requirement: The operator workspace has a board tab
`crew operator up <label>` SHALL also open a `board` tab in the `operator` workspace, after the `rail` tab, showing the partition's board, drawn again each time the rail tab refreshes. When the tab is already there, it SHALL open nothing.

#### Scenario: The tab is opened with the agent
- **WHEN** `crew operator up wldn` starts the operator agent
- **THEN** the `operator` workspace has a `board` tab after `rail`, showing wldn's board

#### Scenario: Run twice
- **WHEN** `crew operator up wldn` runs again
- **THEN** no second `board` tab is opened

#### Scenario: A new entry redraws it
- **WHEN** the user approves a unit from the rail tab's shell
- **THEN** the board tab is drawn again within a few seconds, with that unit's marker gone
