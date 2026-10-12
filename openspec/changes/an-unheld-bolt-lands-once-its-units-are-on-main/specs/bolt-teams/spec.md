## ADDED Requirements

### Requirement: A bolt no team holds lands once its units are on main
`crew bolt land` SHALL land a bolt no team holds, on the user's word, once its kit's main holds each of its units' changes, open or archived, and each of its chores, read on the host and main checkout of a team of the partition building that kit, recording the landing as any landing; it SHALL be refused for such a bolt with no units or chores, whose kit no team of the partition builds, or while any unit's change is not on main.

#### Scenario: A bolt built outside a team
- **WHEN** the plan holds the bolt `deploys-go-through-crew`, no team holds it, and each of its units' changes is archived on crew's main
- **THEN** `crew bolt land deploys-go-through-crew` removes it and its units from the plan, and the landing's entry names crew and the commit its main holds

#### Scenario: A unit not yet on main
- **WHEN** one unit of a bolt no team holds has no change on its kit's main
- **THEN** `crew bolt land` is refused, naming the unit and its stage
