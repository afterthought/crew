## MODIFIED Requirements

### Requirement: Main-level ops lands bolts by one procedure
The main-level ops SHALL land a bolt whose verification is green on the user's word, given by approving the bolt's landing card, which the bolt's conductor posts and passes on with `crew tell`, or said in ops's own pane: it SHALL submit the bolt to main through sluice with `crew bolt submit <bolt>`, push main without force, run `crew bolt land`, and, for crew, bring every host's checkout up to main. It SHALL move no branch by git, and SHALL stop and tell the user when the kit's main is behind GitHub's or GitHub refuses the push. A landing that does not land SHALL be told to the bolt's conductor in sluice's words. A landing SHALL deploy nothing. Until a kit's deployer records its deploys through crew, the main-level ops SHALL deploy that kit's main only on the user's word for that deploy. A failure after landing SHALL be a fix on main.

#### Scenario: Landing
- **WHEN** the user approves swb-1's landing card and its conductor tells the main-level ops
- **THEN** the main-level ops runs `crew bolt submit`, pushes main, runs `crew bolt land`, and the plan no longer holds the bolt

#### Scenario: A landing that conflicts
- **WHEN** `crew bolt submit` fails because the bolt conflicts with main
- **THEN** the main-level ops moves nothing, and tells the bolt's conductor and the user sluice's words

#### Scenario: No word from the planner
- **WHEN** the planner tells the main-level ops that a bolt may land
- **THEN** the main-level ops lands nothing until the user's approval of the landing card, or the user's words in its pane

#### Scenario: A landing deploys nothing
- **WHEN** a swancloud bolt lands
- **THEN** nothing is deployed by the landing, and main is deployed only by a later act on the user's word for that deploy
