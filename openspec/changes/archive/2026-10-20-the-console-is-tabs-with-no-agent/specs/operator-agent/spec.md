# Spec Delta

## REMOVED Requirements

### Requirement: The operator workspace follows the run record
**Reason**: Record 0035: the operator workspace's tabs are the console's, opened with no agent.
**Migration**: `crew console up <label>` opens the `flow` tab ("The console follows the run record").

### Requirement: The operator workspace has a rail tab
**Reason**: Record 0035: the operator workspace's tabs are the console's.
**Migration**: `crew console up <label>` opens the `rail` tab ("The console has a rail tab").

### Requirement: The operator workspace has a board tab
**Reason**: Record 0035: the operator workspace's tabs are the console's.
**Migration**: `crew console up <label>` opens the `board` tab ("The console has a board tab").

## ADDED Requirements

### Requirement: The console follows the run record
`crew console up <label>` SHALL open a `flow` tab in the `console` workspace of the host's `<label>` session that runs `crew events --follow` for the partition, and SHALL start no agent. When the tab is already there it SHALL do nothing. `crew console down <label>` SHALL close the console's tabs.

#### Scenario: The tab is opened with no agent
- **WHEN** `crew console up wldn` runs on mac-studio
- **THEN** the `console` workspace of mac-studio's `wldn` session has a `flow` tab printing wldn's entries as they are written, and no agent is started or greeted

#### Scenario: Run twice
- **WHEN** `crew console up wldn` runs again
- **THEN** no second `flow` tab is opened

### Requirement: The console has a rail tab
`crew console up <label>` SHALL also open a `rail` tab in the `console` workspace, split in two. The upper pane SHALL show `crew rail --label <label>`, printed again every 30 seconds and whenever the partition's run record gains an entry. The lower pane SHALL be a shell with crew on its path. When the tab is already there, it SHALL open nothing.

#### Scenario: The tab is opened
- **WHEN** `crew console up wldn` runs
- **THEN** the `console` workspace has a `rail` tab with wldn's rail above and a shell below in which `crew` runs

#### Scenario: A new entry refreshes the list
- **WHEN** the user approves a unit from the shell below
- **THEN** the list above is printed again within a few seconds, without that unit's review row

#### Scenario: Run twice
- **WHEN** `crew console up wldn` runs again
- **THEN** no second `rail` tab is opened

### Requirement: The console has a board tab
`crew console up <label>` SHALL also open a `board` tab in the `console` workspace, after the `rail` tab, showing the partition's board, drawn again each time the rail tab refreshes. When the tab is already there, it SHALL open nothing.

#### Scenario: The tab is opened
- **WHEN** `crew console up wldn` runs
- **THEN** the `console` workspace has a `board` tab after `rail`, showing wldn's board

#### Scenario: Run twice
- **WHEN** `crew console up wldn` runs again
- **THEN** no second `board` tab is opened

#### Scenario: A new entry redraws it
- **WHEN** the user approves a unit from the rail tab's shell
- **THEN** the board tab is drawn again within a few seconds, with that unit's marker gone

### Requirement: The console's old name opens it and retires the host's operator agent
`crew operator up <label>` SHALL open the console as `crew console up <label>` does, saying it is `crew console up` now. The console's up SHALL end the operator agent the host's operator session held before the operator was a main-level role, `<label>-operator-<host>`, and close the panes crew recorded in its `operator` workspace, once that agent is not working; one working SHALL be left and said.

#### Scenario: The host's timer still runs the old name
- **WHEN** swancloud's timer runs `crew operator up wldn` on mac-studio
- **THEN** the console opens, the command says `crew operator up` is `crew console up` now, and no agent is started
