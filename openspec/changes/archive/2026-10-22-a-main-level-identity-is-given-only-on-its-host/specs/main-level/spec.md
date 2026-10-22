## ADDED Requirements

### Requirement: A main-level role starts only on its main level's host
`crew-role <label> design|planner|ops|operator|reviewer`, fresh or with `resume`, SHALL start its agent only on the host the teams file names for that partition's main level. On any other host it SHALL refuse, naming the agent, the main level's host and this host, and start no Claude.

#### Scenario: The planner started on the standby
- **WHEN** the teams file puts swancloud's main level on deneb and `crew-role swancloud planner` runs on mac-studio
- **THEN** it refuses, saying that swancloud's main level runs on deneb, not mac-studio, and that crew starts `swancloud-planner` only there, and no Claude is started

#### Scenario: On its host
- **WHEN** `crew-role swancloud planner` runs on deneb
- **THEN** the planner starts as it does today

### Requirement: A main-level agent resumed off its host is given no identity
When herdr resumes a session without crew's environment and crew's record of it names a partition's design agent, planner, ops, operator or reviewer, crew SHALL give it its name, identity, pane name and brief back only on the host the teams file names for that main level. On any other host the session SHALL get none of them, its record SHALL be left as it was, and it SHALL be told at each start that it is no agent of crew's there, which host the main level runs on, and to do nothing of crew's.

#### Scenario: A replayed pane on the standby
- **WHEN** the teams file puts swancloud's main level on deneb, and herdr on mac-studio resumes a session whose record there names `swancloud-planner`
- **THEN** its commands see no `CREW_AGENT`, `CREW_LABEL` or `SLUICE_AGENT`, its pane is not named `swancloud-planner`, its record is unchanged, and it is told that swancloud's main level runs on deneb and that it is no agent of crew's on mac-studio

#### Scenario: Compacted on the standby
- **WHEN** that session on mac-studio is compacted
- **THEN** it is given no brief, and is told again that it is no agent of crew's there

#### Scenario: Resumed on its host
- **WHEN** herdr on deneb resumes a session whose record names `swancloud-planner`
- **THEN** it gets its name, identity and pane name back, and its brief at a compaction, as today

#### Scenario: The teams file can't be read
- **WHEN** herdr resumes a session whose record names `swancloud-planner` and crew can't read the teams file
- **THEN** it gets no identity, and is told that crew can't tell where swancloud's main level runs, and why

#### Scenario: A team's agent
- **WHEN** herdr resumes a session whose record names `crw-5-conductor` or `swancloud-dispatch-deneb`
- **THEN** it gets its identity back as today, without the teams file being read for it
