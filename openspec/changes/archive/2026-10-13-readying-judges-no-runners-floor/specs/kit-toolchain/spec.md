## ADDED Requirements

### Requirement: A kit's moon is its own
Which moon a kit's toolchain runs SHALL be the kit's own choice: crew SHALL judge no version of it, nor take any as sluice's to require. For a moon runner, crew SHALL run `moon --version` inside the toolchain before `moon setup`, and SHALL refuse only output that names no version it can read, naming what was printed; any version it reads SHALL go on to `moon setup`.

#### Scenario: An older moon
- **WHEN** the moon inside a kit's toolchain is 1.41.7, or 2.5.3
- **THEN** crew runs `moon setup` in the place and makes it ready, as for any other version

#### Scenario: A version crew cannot read
- **WHEN** `moon --version` inside a kit's toolchain prints `bash: moon: command not found`, or nothing
- **THEN** crew refuses to make the place ready, naming what was printed

## REMOVED Requirements

### Requirement: The moon runner needs moon 2.6
**Reason**: The user, 2026-10-13: "The version of Moon is decided by every kit repo. It's not enforced by Sluice and it's not enforced by crew. It has to do with certain features the project may or may not want to take advantage of, but Sluice does not require Moon 2.6".
**Migration**: "A kit's moon is its own": a kit that wants a moon's features pins that moon in its own toolchain.
