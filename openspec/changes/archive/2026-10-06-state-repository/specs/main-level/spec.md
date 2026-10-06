# Spec Delta

## MODIFIED Requirements

### Requirement: Partitions are declared in the teams file
`teams.json` SHALL list each partition with a main level. Each entry gives the partition's label (`wldn`, `madswan`, `swancloud`), its swancloud name, its blueprints repos, its state repository (`state`, as `<owner>/<name>`), and the machine and session its main level runs in. The first blueprints repo listed SHALL be the one the partition's signals and elaboration go to by default. A partition with no `state` SHALL be an error naming the field and the machine's configuration as the fix, never a default.

#### Scenario: clients/willdan
- **WHEN** `teams.json` lists `wldn` as `clients/willdan` with willdan-blueprints and `WilldanGroup/crew-state`, running on the box in `wldn-2`
- **THEN** `crew main up wldn` starts its main level in `wldn-2` on the box, and wldn's plan is read from `wldn/main` of `WilldanGroup/crew-state`

#### Scenario: A partition with no state repository
- **WHEN** a partition's entry has no `state`
- **THEN** crew refuses to load the teams file, naming the partition and the missing field

### Requirement: Every move is written through crew and never merged
Every move SHALL be appended to `moves.rec` on the flywheel's branch of its state repository, through crew: `route` by `crew unit add --signal`, and `attach`, `challenge`, `new-territory`, `answered` and `drop` by `crew signal move <id> <move>`. Each SHALL be fetched over https, applied to the tip of the branch, checked with `recfix --check`, committed, and pushed without force, applied again to the new tip when the push is refused. A signal SHALL have one move; a second is refused.

#### Scenario: Moves from two hosts
- **WHEN** a route is written on the box while curation writes a drop on mac-studio, both through crew
- **THEN** both moves are in `moves.rec`, one after the other, nothing is merged, and the file passes `recfix --check`

#### Scenario: A signal moved twice
- **WHEN** `crew signal move` names a signal that already has its move
- **THEN** it is refused, naming the move it has
