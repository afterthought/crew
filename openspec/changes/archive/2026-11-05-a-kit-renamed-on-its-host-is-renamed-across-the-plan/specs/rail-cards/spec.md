## ADDED Requirements

### Requirement: A kit's landings card follows its rename
A card open under `land/<old>`, where a rename of the partition's renamed `<old>` to `<new>`, SHALL be closed by the rail's sweep with the reason that `<old>` is renamed `<new>` and its landings are rows of `land/<new>`. It SHALL never be read as a gone bolt's card. `land/<new>` SHALL be raised for the kit's waiting rows as any row with no card is raised, in main-level ops' name. A decision record's card under `record/<old>/<n>` SHALL be read as `record/<new>/<n>`'s, settled by the record's status under the new kit.

#### Scenario: The landings card of a renamed kit
- **WHEN** madswan-ops holds a card open under `land/flywheel-cloud`, the user renames `flywheel-cloud` to `boomdrive-cloud`, and `you-sign-in-to-staging` waits to land
- **THEN** the sweep closes `land/flywheel-cloud` saying it is renamed `boomdrive-cloud`, and raises `land/boomdrive-cloud` with the bolt's row

#### Scenario: A record's card of a renamed kit
- **WHEN** madswan-design's card under `record/tailrace/0017` is open, `tailrace` has been renamed `timber`, and the design agent runs `crew record timber 17 --accepted`
- **THEN** the sweep closes the card with the record's status
