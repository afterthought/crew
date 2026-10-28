## ADDED Requirements

### Requirement: A left bolt's land line says it would take main first once ticked
A bolt the user left on its kit's landings card, or stopped in their words to main-level ops, whose forecast against main the run record holds in conflict at its present head, SHALL be said on the kit's land row to be left by the user and to take main first once ticked, naming the files, and SHALL NOT be among the bolts the row's tell lands. A left bolt with no such conflict SHALL read as it does today.

#### Scenario: Left and forecast to conflict
- **WHEN** `z` is left on `land/crew`, reads proven, and the run record holds `z` forecast to conflict with main on `README.md` at its present head
- **THEN** crew's row under land says `z` was left by the user and takes main first once ticked, forecast to conflict with main on `README.md`, and its tell names no `z`

#### Scenario: Ticked
- **WHEN** the user ticks `z` and its take-main fix is told
- **THEN** `z`'s line says it takes main first, until its team's take-main fix moves its head
