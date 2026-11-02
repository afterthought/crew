## ADDED Requirements

### Requirement: A crossed team's bolt waits to land on its kit's row
A crossed team's bolt SHALL be a row of its kit's landings card on the same terms as any bolt, every unit and chore merged and sluice green at its head, its pieces' stages read from the runner's records; its line SHALL name the team's host where another's names a team's slots.

#### Scenario: A crossed bolt proven
- **WHEN** crossed crw-4's `x` has `a`, `b` and `c` merged by the runner's records and sluice green at its head
- **THEN** the rail shows crew's landings row with `x`, crw-4 on deneb, can land

### Requirement: A fix of main waits to land on its kit's row
A fix of the kit's main whose code has delivered and whose submission waits held SHALL be a line of the kit's landings row, `fix main--<name>`, with the first line of its brief, ticked and sent as a bolt is, and naming `crew main fix <kit> <name> --send` as ops's command for it.

#### Scenario: A fix of main waits beside a bolt
- **WHEN** `main--a-test-reads-its-fixture`'s code has delivered and its submission waits held
- **THEN** crew's landings row has a line `fix main--a-test-reads-its-fixture` with the failure's first line, and names its `--send` command
