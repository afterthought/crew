## ADDED Requirements

### Requirement: A deploy is approved and recorded through crew
A kit's deployer SHALL ask crew for each deploy of a `manual` environment with `crew deploy offer`, and the user's word
for it SHALL be holding the card of the rail row the offer makes, which main-level ops posts and records with
`crew deploy approve`. `crew deploy word` SHALL give the commit the word is for until that deploy's end is recorded.
Every deploy's start, steps and end, and every after-deploy step's state, SHALL be an entry of the run record of the
host where the partition's main level runs, and every `crew deploy` command SHALL run there.

#### Scenario: A deploy offered and approved
- **WHEN** the deployer offers mac-studio a deploy of main's head and the user holds its card
- **THEN** main-level ops runs `crew deploy approve`, the row leaves the rail, and `crew deploy word mac-studio` prints the commit until the deploy's end is recorded

#### Scenario: An approval for another commit
- **WHEN** `crew deploy approve` names a commit other than the open offer's
- **THEN** it is refused, recorded as refused, and no word is given

#### Scenario: A user's after-deploy step
- **WHEN** the deployer records a step whose doer is the user as waiting
- **THEN** the rail shows it under deploys until it is recorded done or declined, and `crew deploy steps` gives its latest state
