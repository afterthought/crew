## ADDED Requirements

### Requirement: A help flag shows a command's usage and acts on nothing
Every crew command SHALL answer `-h` or `--help` among its own arguments by printing its usage and exiting 0, before it reads the teams file, records, starts, tells or sends anything to another host. Its usage SHALL be the one text its entry point already prints. An argument that is not exactly `-h` or `--help` SHALL be read as it was before.

#### Scenario: A stage's agent asks crew needs for its usage
- **WHEN** the agent of a construct crew owes an end runs `crew needs --help`, or `crew needs -h`
- **THEN** crew prints `crew needs`'s lines of its usage and exits 0; the stage stays begun, no end is recorded, the conductor is told nothing and the agent is not ended

#### Scenario: A fix's usage
- **WHEN** a conductor runs `crew fix swb-1 tidy --help`, or `crew fix swb-1 tidy "The banner flickers." -h`
- **THEN** crew prints the lines of `crew fix` and exits 0, and no fix starts: no place, no branch, no agent and no entry

#### Scenario: A stage's usage
- **WHEN** a conductor runs `crew unit run b code --help`
- **THEN** crew prints the line of `crew unit run` and exits 0, and no stage starts

#### Scenario: Every command
- **WHEN** any command crew dispatches is run with arguments of its own shape and `--help` or `-h` among them, the internal `_` commands, `crew hold <host> "<why>" --help`, `crew tell <agent> "<text>" --help`, `crew up <team> --help` for a team on another host and `crew revive --help` among them
- **THEN** it prints its usage and exits 0, with no call to herdr, ssh, sluice or any other tool, no agent started, no entry on any host and no write to the state branch; a command `crew` reads itself prints its own lines of `crew`'s usage header, and a command `crew` hands to a Python parser prints that parser's usage

#### Scenario: crew's own usage
- **WHEN** the user runs `crew --help`, `crew -h` or `crew-role <team> conductor --help`
- **THEN** each prints its whole usage and exits 0, starting nothing

#### Scenario: A command a Python parser reads
- **WHEN** an agent runs `crew bolt give swb-1 --help`, or `crew plan approve three --help`, where `three` is no proposal's number
- **THEN** crew prints the usage of `crew bolt give`, or of `crew plan approve`, and exits 0, before it checks for recutils or reads the teams file

#### Scenario: A word that is not the flag
- **WHEN** a stage's agent runs `crew needs "--help with which table holds tenants"`
- **THEN** its stage ends short with those words, as any needs does, and its conductor is told them
