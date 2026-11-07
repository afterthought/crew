## Purpose
What the `crew` command, and `crew-role` beside it, do with what they are given, whatever the command: the rules every command holds to at its entry point, before it reads, records, starts or forwards anything (`code.11`).

## ADDED Requirements

### Requirement: A help flag shows a command's usage and acts on nothing
Every crew command SHALL answer `-h` or `--help` among its own arguments by printing its usage and exiting 0, before it reads the teams file, records, asks, launches, starts, tells or sends anything to another host. Its usage SHALL be the one text its entry point already prints. An argument that is not exactly `-h` or `--help` SHALL be read as it was before.

#### Scenario: A tell's usage
- **WHEN** the design agent runs `crew tell wldn-planner --help`, or `crew tell wldn-planner -h`, where the planner runs as its kind
- **THEN** crew prints `crew tell`'s lines of its usage and exits 0; nothing is asked of the planner, nothing is typed into a pane and no entry is written

#### Scenario: A fix's usage
- **WHEN** ops runs `crew fix tenant-environments tidy --help`, or `crew fix tenant-environments tidy "The banner flickers." -h`
- **THEN** crew prints the usage of `crew fix` and exits 0, and no fix is launched: no request and no entry

#### Scenario: Every command
- **WHEN** any command crew dispatches is run with arguments of its own shape and `--help` or `-h` among them, the internal `_` commands, `crew hold <host> "<why>" --help`, `crew send <partition> "<text>" --help`, `crew main up <label> --help` and `crew revive --help` among them
- **THEN** it prints its usage and exits 0, with no call to herdr, ssh, sluice or any other tool, no agent started, no entry on any host and no write to the state branch; a command `crew` reads itself prints its own lines of `crew`'s usage header, and a command `crew` hands to a Python parser prints that parser's usage

#### Scenario: crew's own usage
- **WHEN** the user runs `crew --help`, `crew -h` or `crew-role wldn planner --help`
- **THEN** each prints its whole usage and exits 0, starting nothing

#### Scenario: A command a Python parser reads
- **WHEN** an agent runs `crew bolt start tenant-environments --help`, or `crew plan approve three --help`, where `three` is no proposal's number
- **THEN** crew prints the usage of `crew bolt start`, or of `crew plan approve`, and exits 0, before it checks for recutils or reads the teams file

#### Scenario: A word that is not the flag
- **WHEN** the design agent runs `crew tell wldn-planner "--help with which table holds tenants"`, where the planner runs as its kind
- **THEN** the words are asked of the planner, as any tell to a role that runs as its kind is
