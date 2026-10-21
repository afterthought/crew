# Spec Delta

## MODIFIED Requirements

### Requirement: Partitions are declared in the teams file
`teams.json` SHALL list each partition with a main level. Each entry gives the partition's label (`wldn`, `madswan`, `swancloud`), its swancloud name, its blueprints repos, its state repository (`state`, as `<owner>/<name>`), and the machine and session its main level runs in. The first blueprints repo listed SHALL be the one the partition's signals and elaboration go to by default. A partition with no `state` SHALL be an error naming the field and the machine's configuration as the fix, never a default. A partition's `roles.<role>` MAY name a `session` for a main-level role other than the dispatcher, a session of the main level's machine in the partition, where that role runs; any other session SHALL be an error naming it.

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

## ADDED Requirements

### Requirement: The main level is a workspace in each of its sessions
`crew main up <label>` SHALL open a `<label>` workspace in each session the main level's roles run in, each role's tab in its session's, and start each role there; `crew main down`, `crew main status`, `crew review` and `crew revive` SHALL find each role in its session.

#### Scenario: Design and planner on two accounts
- **WHEN** swancloud's planner runs in `swancloud-2` and the rest of its main level in `swancloud-1`, and `crew main up swancloud` runs
- **THEN** `swancloud-planner` starts in the `swancloud` workspace of `swancloud-2`, and the design agent, ops and the operator in `swancloud-1`'s

### Requirement: A role is never started twice when its session changes
`crew main up` SHALL refuse while a role's agent still runs in a session it no longer stands in, naming it, and `crew main down` SHALL end it there. Panes a state folder recorded in another session than the one its agents run in now SHALL be set aside and said, never taken for that session's.

#### Scenario: A role moved while it runs
- **WHEN** wldn's teams file names a session for its planner while `wldn-planner` still runs in `wldn-2`, and `crew main up wldn` runs
- **THEN** it refuses, naming `wldn-planner`, its session and pane, and that `crew main down wldn` ends it

#### Scenario: Panes recorded in another session
- **WHEN** swancloud's main level moves from `swancloud-2` to `swancloud-1` and a main-level command runs
- **THEN** the panes recorded in `swancloud-2` are set aside and said, and no agent of `swancloud-1` at the same pane id is taken for one of the main level's
