# Spec Delta

## MODIFIED Requirements

### Requirement: A card carries what the user would read and the row's answers
A proposal's card, a review card and a verify card SHALL each carry the link to the plannotator session its owner started for the card's key: on the proposal's page as `crew plan proposed <n>` prints it, on the unit's change folder, or on the verify report. The card SHALL carry the link in place of the page, the folder's path or the report, and SHALL NOT be posted without it when the owner's session has plannotator. A landing card carries no link. Each card's options SHALL be the row's answers: approve or ask for changes for a proposal or a review, what to fix or merge for a verify report, and approve for a landing. A decision the user makes in the card's session SHALL be acted on by the owner as the card's answer, and the owner SHALL then close the card.

#### Scenario: A review card's options
- **WHEN** the user opens a review card
- **THEN** it offers approval, and a note in the user's own words asks for changes

#### Scenario: A review card's link
- **WHEN** swb-1-conductor posts the card for unit `x` in review at `abc1234`
- **THEN** the card carries the link `crew card session review/x/abc1234` printed, and no folder path

#### Scenario: Answered in the session rather than on the card
- **WHEN** the user annotates the change in the review card's session and sends the annotations
- **THEN** the conductor runs construct again with them, as for a note on the card, and withdraws the card saying it was answered in its session
