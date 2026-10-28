## MODIFIED Requirements

### Requirement: The console follows the run record
`crew console up <label> flow` SHALL open a `flow` tab in the `console` workspace of the host's `<label>` session that runs `crew events --follow` for the partition, and SHALL start no agent. When the tab is already there it SHALL do nothing. `crew console down <label>` SHALL close the console's tabs. The tab SHALL show an entry written on this host within a few seconds, and one from another host within a minute.

#### Scenario: The tab is opened with no agent
- **WHEN** `crew console up wldn flow` runs on mac-studio
- **THEN** the `console` workspace of mac-studio's `wldn` session has a `flow` tab printing wldn's entries as they are written, and no agent is started or greeted

#### Scenario: Run twice
- **WHEN** `crew console up wldn flow` runs again
- **THEN** no second `flow` tab is opened

#### Scenario: Not asked for
- **WHEN** `crew console up wldn` runs on a host with no `flow` tab open
- **THEN** no `flow` tab is opened

#### Scenario: An entry from another host
- **WHEN** the `flow` tab runs on mac-studio and a conductor on the box starts a stage
- **THEN** its line appears within a minute, and the tab fetched wldn's branch no more than once a minute meanwhile
