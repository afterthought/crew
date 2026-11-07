## ADDED Requirements

### Requirement: A bolt carrying another bolt's work is held on its land line
A bolt whose kit's read says it carries another bolt's work that main lacks SHALL NOT be able to land on its kit's land row. Its line SHALL say it is held, naming each bolt whose work it carries and that bolt's landings, and that it lands once main holds that work. It SHALL be left out of the row's answer to ops. Once the kit's read finds nothing carried, the line SHALL say it can land.

#### Scenario: A bolt carrying another bolt's work
- **WHEN** bolt `apex-zones` reads proven and the kit's read says it carries bolt `tenant-environments`'s landing `f5e67f35`
- **THEN** its line says "held: carries bolt tenant-environments's work, its landing f5e67f3, which main lacks", it can't land, and the row offers ops nothing for it

#### Scenario: Main holds the carried work
- **WHEN** the kit's read says `apex-zones` carries nothing
- **THEN** its line says it can land
