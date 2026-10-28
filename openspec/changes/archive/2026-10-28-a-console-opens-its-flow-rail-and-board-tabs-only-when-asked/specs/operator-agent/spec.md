## ADDED Requirements

### Requirement: The console opens with its shell alone
`crew console up <label> [flow] [rail] [board]` SHALL open the `console` workspace of the host's `<label>` session with a `shell` tab, a shell with crew on its path, and SHALL start no agent. It SHALL open the `flow`, `rail` or `board` tab only when named, or the rail tab while no host job runs the host's follower. A name that is no tab SHALL be refused, naming the three.

#### Scenario: Opened while the host's job follows
- **WHEN** swancloud's job runs `crew _follow` on mac-studio and `crew console up wldn` runs there
- **THEN** wldn's `console` workspace holds the `shell` tab alone, no agent is started or greeted, and the board's frame and wldn's agents' views are still written on every refresh

#### Scenario: Opened while no job follows
- **WHEN** no host job runs the follower on mac-studio and `crew console up wldn` runs there
- **THEN** wldn's `console` workspace holds the `shell` tab and the `rail` tab, whose loop is the host's follower, and no `flow` or `board` tab

#### Scenario: A tab asked for by name
- **WHEN** `crew console up wldn rail` runs while the host's job follows
- **THEN** the `console` workspace has the `rail` tab beside its `shell` tab, as the rail tab requirement says, and no `flow` or `board` tab

#### Scenario: A name that is no tab
- **WHEN** `crew console up wldn page` runs
- **THEN** it is refused, saying the tabs are flow, rail and board, and nothing is opened

### Requirement: The console keeps the tabs it has open
Every later `crew console up <label>`, a tab named or not, SHALL keep each console tab already open, running its command again where a restart left its pane its shell alone, and SHALL not open again a tab the user closed unless it is named, or is the rail tab while no host job runs the follower.

#### Scenario: Run again
- **WHEN** `crew console up wldn` runs again after `crew console up wldn rail`
- **THEN** nothing is opened, run or greeted, and the `rail` tab stays open

#### Scenario: A tab the user closed
- **WHEN** the user closed the `board` tab, and swancloud's timer runs `crew console up wldn`
- **THEN** no `board` tab is opened

#### Scenario: After a restart
- **WHEN** herdr brings the console's `flow` and `rail` tabs back as their shells alone, and `crew console up wldn` runs
- **THEN** each runs its command there again, and no tab is opened

## MODIFIED Requirements

### Requirement: The console follows the run record
`crew console up <label> flow` SHALL open a `flow` tab in the `console` workspace of the host's `<label>` session that runs `crew events --follow` for the partition, and SHALL start no agent. When the tab is already there it SHALL do nothing. `crew console down <label>` SHALL close the console's tabs.

#### Scenario: The tab is opened with no agent
- **WHEN** `crew console up wldn flow` runs on mac-studio
- **THEN** the `console` workspace of mac-studio's `wldn` session has a `flow` tab printing wldn's entries as they are written, and no agent is started or greeted

#### Scenario: Run twice
- **WHEN** `crew console up wldn flow` runs again
- **THEN** no second `flow` tab is opened

#### Scenario: Not asked for
- **WHEN** `crew console up wldn` runs on a host with no `flow` tab open
- **THEN** no `flow` tab is opened

### Requirement: The console has a rail tab
`crew console up <label> rail` SHALL open a `rail` tab in the `console` workspace, split in two, as `crew console up <label>` SHALL while no host job runs the follower. The upper pane SHALL show the rail frame the host's follower writes, `crew rail --label <label>` as of its last read, drawn again whenever the frame changes, and SHALL follow itself while no one does. The lower pane SHALL be a shell with crew on its path. When the tab is already there, it SHALL open nothing.

#### Scenario: The tab is opened
- **WHEN** `crew console up wldn rail` runs
- **THEN** the `console` workspace has a `rail` tab with wldn's rail above and a shell below in which `crew` runs

#### Scenario: A new entry refreshes the list
- **WHEN** the user approves a unit from the shell below
- **THEN** the list above is printed again within a few seconds, without that unit's review row

#### Scenario: Run twice
- **WHEN** `crew console up wldn rail` runs again
- **THEN** no second `rail` tab is opened

#### Scenario: The host's job stops
- **WHEN** the rail tab draws the frames of swancloud's follower job, and that job ends
- **THEN** within one period the rail tab follows itself, and the rail, the board's frame and the agents' views are written again

### Requirement: The console has a board tab
`crew console up <label> board` SHALL open a `board` tab in the `console` workspace, after the `rail` tab when it is there, showing the partition's board, drawn again each time the host's follower writes the board's frame. When the tab is already there, it SHALL open nothing.

#### Scenario: The tab is opened
- **WHEN** `crew console up wldn board` runs
- **THEN** the `console` workspace has a `board` tab showing wldn's board

#### Scenario: Run twice
- **WHEN** `crew console up wldn board` runs again
- **THEN** no second `board` tab is opened

#### Scenario: A new entry redraws it
- **WHEN** the user approves a unit from the rail tab's shell
- **THEN** the board tab is drawn again within a few seconds, with that unit's marker gone
