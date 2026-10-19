## MODIFIED Requirements

### Requirement: A forecast conflict between two units orders them
When a conflict is forecast between two units that have both not merged, the forecast SHALL reach the later unit, and the later unit's agent SHALL take the earlier unit's work into its place and resolve the conflict there; the forecast alone SHALL NOT give the later unit `After` on the earlier. crew SHALL put the later unit after the earlier one, in the conductor's name, only when the later unit's settle delivers a commit whose branch holds the earlier unit's work, while both are unmerged, and at most once for a pair; a settle that finds nothing to change SHALL order nothing. An `After` crew wrote for a pair whose later unit's settle then stopped short with no commit, and whose branch does not hold the other's work, SHALL be lifted by crew itself, on the conductor's wait that sees that end or on any wait after. An `After` crew wrote for a pair that anyone else lifted SHALL NOT be written again. No proposal or card SHALL ask the user to lift an `After` crew wrote from a forecast.

#### Scenario: Two unmerged units
- **WHEN** a conflict is forecast between A and B, A first, neither merged
- **THEN** the forecast reaches B with A's change, B's agent is told to take A's work into B's place and resolve the conflict there, and the forecast alone gives B no `After`

#### Scenario: The settle takes the other's work
- **WHEN** B, verified and waiting to merge, is forecast to conflict with A, and B's settle delivers a commit that merges A's work into B's place
- **THEN** B gains `After: A` in the conductor's name, and B's merge waits for A's

#### Scenario: The settle finds nothing to change
- **WHEN** B's settle for a forecast against A stops short saying nothing needs to change
- **THEN** B gains no `After`, and B merges without waiting for A

#### Scenario: An order crew wrote is lifted by crew
- **WHEN** B holds `After: A` that crew wrote from a forecast, B's settle for it stopped short with no commit, and B's branch does not hold A's work
- **THEN** the conductor's next wait lifts B's `After: A` in the conductor's name, and no proposal or card is made for it

#### Scenario: An order the user lifted stays lifted
- **WHEN** crew wrote B's `After: A`, the user lifted it by proposal, and a later forecast on new heads finds B and A in conflict again
- **THEN** the forecast reaches B, and crew does not write `After: A` back

#### Scenario: One order for a pair
- **WHEN** crew put B after A on a settle's commit, someone lifted it, and a later settle of B takes A's work again
- **THEN** crew does not write `After: A` again
