# Spec Delta

## ADDED Requirements

### Requirement: The board's JSON lists each partition's teams
`crew board --json` SHALL list, for each partition, its teams in the teams file's order, each with its kit and its host. The board's text SHALL not change.

#### Scenario: The page's team control
- **WHEN** `crew board --label wldn --json` runs
- **THEN** wldn's partition lists each of its teams with its kit and host, in the teams file's order

### Requirement: Each object in the board's JSON says whose it is
Each object in the lanes of `crew board --json` SHALL carry the teams it belongs to: a held bolt or a landing, its team; a signal, the team whose agent captured it; a planned bolt, a queued unit or an exploration, every team building its repository; a proposal, the teams holding its bolts and those building its repositories. An object belonging to no team SHALL carry an empty list.

#### Scenario: A held bolt and the work queued behind it
- **WHEN** swb-1 and swb-2 both build switchboard-kit, swb-1 holds tenant-environments, and unit zone-two of switchboard-kit is queued
- **THEN** the JSON gives tenant-environments the teams `["swb-1"]` and zone-two the teams `["swb-1", "swb-2"]`

#### Scenario: A signal the user wrote
- **WHEN** a signal was captured by the user rather than by an agent of a team
- **THEN** the JSON gives it an empty list of teams

#### Scenario: A proposal for a held bolt
- **WHEN** proposal 4 adds a unit to tenant-environments, which swb-1 holds
- **THEN** the JSON gives proposal 4 the team swb-1
