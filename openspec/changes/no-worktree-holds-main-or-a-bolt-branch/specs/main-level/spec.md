## MODIFIED Requirements

### Requirement: Main-level ops lands bolts by one procedure
The main-level ops SHALL land a bolt whose verification is green on the user's word, given by approving the bolt's landing card, which crew raises in the bolt's conductor's name and the conductor passes on with `crew tell`, or said in ops's own pane: it SHALL submit the bolt to main through sluice with `crew bolt submit <bolt>`, which lands it on GitHub's main by a leased push, and run `crew bolt land`. It SHALL push nothing, pull or level no host's checkout, since the fleet's timer moves every host's anchor, and SHALL move no branch by git. A landing that does not land SHALL be told to the bolt's conductor in sluice's words. A landing SHALL deploy nothing. Until a kit's deployer records its deploys through crew, the main-level ops SHALL deploy that kit's main only on the user's word for that deploy. A failure after landing SHALL be a fix on main.

#### Scenario: Landing
- **WHEN** the user approves swb-1's landing card and its conductor tells the main-level ops
- **THEN** the main-level ops runs `crew bolt submit`, then `crew bolt land`, the plan no longer holds the bolt, and the card says every host's folder follows by the timer within minutes

#### Scenario: A landing that conflicts
- **WHEN** `crew bolt submit` fails because the bolt conflicts with main
- **THEN** the main-level ops moves nothing, and tells the bolt's conductor and the user sluice's words

#### Scenario: No word from the planner
- **WHEN** the planner tells the main-level ops that a bolt may land
- **THEN** the main-level ops lands nothing until the user's approval of the landing card, or the user's words in its pane

#### Scenario: A landing deploys nothing
- **WHEN** a swancloud bolt lands
- **THEN** nothing is deployed by the landing, and main is deployed only by a later act on the user's word for that deploy
