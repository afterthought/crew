## ADDED Requirements

### Requirement: A kit's rename is one entry naming both its names
`crew kit rename` SHALL leave one `kit.rename` entry per act, done or refused. The entry SHALL name the kit by its new name, `On: kit/<new>`, and by the name it had, `From: kit/<old>`, with `Repo` its new name and `Count` the number of plan records it renamed. It SHALL hold no text anyone typed. A rename's entry SHALL be read by crew as the partition's record of that rename, and only an entry not refused SHALL rename anything crew reads.

#### Scenario: The entry of a rename
- **WHEN** the user runs `crew kit rename tailrace timber` on madswan's plan, renaming 21 records
- **THEN** madswan's run record holds one `kit.rename` entry with `On: kit/timber`, `From: kit/tailrace`, `Repo: timber` and `Count: 21`, its commit's `Crew-Entry` naming it

#### Scenario: A refused rename renames nothing
- **WHEN** a rename of `tailrace` to `timber` is refused because deneb still keeps `agentplot/tailrace`
- **THEN** its entry is a refusal, and crew still reads `tailrace` as written
