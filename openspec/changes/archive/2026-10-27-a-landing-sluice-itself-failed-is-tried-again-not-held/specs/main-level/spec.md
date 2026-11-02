## MODIFIED Requirements

### Requirement: Main-level ops lands bolts by one procedure
The main-level ops SHALL land bolts whose verification is green on the user's word: their send on a kit's landings card, which crew raises in ops's name, the word for every bolt they ticked, in the card's order unless their note moves one; or their words in ops's own pane. It SHALL submit them with one `crew bolt submit <bolt>...` in that order, which queues each in sluice behind the one before and closes each with `crew bolt land` as it lands. It SHALL push nothing, level no host and move no branch by git. A bolt that does not land for its own content, a conflict or a failed check, SHALL be told to its conductor in sluice's words, the rest going on. A bolt whose landing sluice or its host stopped SHALL be reported as a finding outside any bolt and submitted again by the same `crew bolt submit` once what stopped it is cleared, on the word it has, with no new word of the user's. A landing SHALL deploy nothing. Until a kit's deployer records its deploys through crew, the main-level ops SHALL deploy that kit's main only on the user's word for that deploy. A failure after landing SHALL be a fix on main.

#### Scenario: Landing
- **WHEN** the user sends swb-1's bolt ticked on willdan's landings card
- **THEN** the main-level ops runs `crew bolt submit` on it, which lands it through sluice and closes it with `crew bolt land`, and the plan no longer holds the bolt

#### Scenario: Several bolts in order
- **WHEN** the user sends `land/crew` with `y`, `z` and `w` ticked in that order
- **THEN** the main-level ops runs `crew bolt submit y z w` once, as a background command, and sluice lands them in that order

#### Scenario: A note moves the order
- **WHEN** the user sends `land/crew` with `y` and `z` ticked and a note saying `z` goes first
- **THEN** the main-level ops runs `crew bolt submit z y`

#### Scenario: A landing that conflicts
- **WHEN** `crew bolt submit y z` says `y` did not land because it conflicts with main
- **THEN** the main-level ops moves nothing, tells `y`'s conductor and the user sluice's words, and `z` lands all the same

#### Scenario: No word from the planner
- **WHEN** the planner tells the main-level ops that a bolt may land
- **THEN** the main-level ops lands nothing until the user's send on the kit's landings card with the bolt ticked, or the user's words in its pane

#### Scenario: A landing deploys nothing
- **WHEN** a swancloud bolt lands
- **THEN** nothing is deployed by the landing, and main is deployed only by a later act on the user's word for that deploy

#### Scenario: The brief lands bolts together
- **WHEN** main-level ops's brief is read
- **THEN** it says to submit every bolt the user ticked with one `crew bolt submit` in the card's order, and says nothing of landing one bolt at a time

#### Scenario: A landing sluice stopped
- **WHEN** `crew bolt submit y z` says `y` did not land because the host could not run main's checks, nothing of the bolt's
- **THEN** the main-level ops tells no conductor, records what stopped it as a signal and tells the planner, `z` lands all the same, and once the host runs checks again ops runs `crew bolt submit y` on the user's send that still stands, asking the user nothing
