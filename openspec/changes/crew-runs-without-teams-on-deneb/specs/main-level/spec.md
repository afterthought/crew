## MODIFIED Requirements

### Requirement: Partitions are declared in the teams file
`teams.json` SHALL list each partition with a main level, and nothing else. Each entry gives the partition's label (`wldn`, `madswan`, `swancloud`), its swancloud name, its blueprints repos, its state repository (`state`, as `<owner>/<name>`), the machine and session its main level runs in, and `flume`, naming each of its five main-level roles, `design`, `planner`, `reviewer`, `ops` and `operator`, as `false` while it stands or as the Flume stream its runs run in on the main level's host. The first blueprints repo listed SHALL be the one the partition's signals and elaboration go to by default. A partition with no `state` or no `flume` SHALL be an error naming the field and the machine's configuration as the fix, never a default, and so SHALL a `flume` that leaves a role out, names another key, or gives a role anything but `false` or a stream's name. crew SHALL read version 5 of the file alone: a file at any other version, or one holding `teams`, SHALL be refused naming swancloud's `lib/crew-teams.nix` as the fix, with nothing done. A partition's `roles.<role>` MAY name a `session` for a main-level role, a session of the main level's machine in the partition, where that role runs while it stands; any other session SHALL be an error naming it.

#### Scenario: clients/willdan
- **WHEN** `teams.json` lists `wldn` as `clients/willdan` with willdan-blueprints and `WilldanGroup/crew-state`, running on the box in `wldn-2`
- **THEN** `crew main up wldn` starts its main level in `wldn-2` on the box, and wldn's plan is read from `wldn/main` of `WilldanGroup/crew-state`

#### Scenario: A partition with no state repository
- **WHEN** a partition's entry has no `state`
- **THEN** crew refuses to load the teams file, naming the partition and the missing field

#### Scenario: The planner in a session of its own
- **WHEN** swancloud's entry names `roles.planner.session` as `swancloud-2`, a session of deneb in partition personal
- **THEN** `swancloud-planner` runs in `swancloud-2` and its other main-level roles in the main level's session

#### Scenario: A session of another partition
- **WHEN** swancloud's `roles.planner.session` names `madswan-1`, a session of partition business
- **THEN** crew refuses to load the teams file, naming the planner, the session and its partition

#### Scenario: A partition with no flume
- **WHEN** a partition's entry has no `flume`
- **THEN** crew refuses to load the teams file, naming the partition, the field and swancloud's `lib/crew-teams.nix`

#### Scenario: A role crew has no kind for
- **WHEN** madswan's `flume` names `dispatcher`, leaves out `operator`, or gives `planner` the value `true`
- **THEN** crew refuses to load the teams file, naming the partition and the role

#### Scenario: The file before version 4
- **WHEN** `teams.json` is at version 3
- **THEN** crew refuses to load it, naming its version and swancloud's `lib/crew-teams.nix`, and does nothing

#### Scenario: The file before version 5
- **WHEN** `teams.json` is at version 4, its `teams` listing a team for each kit
- **THEN** crew refuses to load it, naming its version and swancloud's `lib/crew-teams.nix`, and does nothing

#### Scenario: The box's file at version 2
- **WHEN** `teams.json` is at version 2, its `partitions` and its `teams` as chuck-herdr-alpha's file holds them for wldn's teams
- **THEN** crew refuses to load it, naming its version, that crew reads only version 5, and swancloud's `lib/crew-teams.nix`, and does nothing

#### Scenario: A version-5 file that lists teams
- **WHEN** `teams.json` is at version 5 and holds a `teams` key beside its `partitions`
- **THEN** crew refuses to load it, saying version 5 has no place for teams since crew runs none, naming swancloud's `lib/crew-teams.nix`, and does nothing
