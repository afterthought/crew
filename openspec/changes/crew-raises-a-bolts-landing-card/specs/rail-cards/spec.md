## MODIFIED Requirements

### Requirement: The landing card is posted once the bolt's verification is green
crew SHALL raise a bolt's landing card once every unit and chore of the bolt has merged, every unit's latest change has been in a batch, sluice's verdict at its head is green and no fix is in flight on it, keyed `land/<bolt>`, as an `approve` of risk high, not reversible, because irreversible, its summary giving the counts, the batches, the verdict and when, and how far main has moved, its face a text artifact "What lands: N units, M chores" naming each one a line, its rationale what follows, and, when sluice's submission at the head has a pull request on GitHub, that pull request as a `url` artifact and among its links; it SHALL ask only for the landing. A note naming a defect SHALL have the conductor start a fix on the bolt, which withdraws the card, and the card SHALL be raised again once the bolt reads proven again.

#### Scenario: Sluice's pull request
- **WHEN** sluice's submission at `y`'s head has pull request #23 on the kit's GitHub
- **THEN** the card links it, titled as sluice's pull request for the landing, on its face and in its details

#### Scenario: No pull request
- **WHEN** the kit's sluice opens no pull request for a submission
- **THEN** the card carries no link, and says nothing of one

#### Scenario: A green bolt
- **WHEN** every unit and chore of bolt `y` has merged, each unit's latest change has been in a batch and sluice is green at `abc1234`
- **THEN** one card keyed `land/y` is open, an approve of risk high, naming the units and chores and the verdict

#### Scenario: A defect noted on the card
- **WHEN** the user answers `land/y` with a note naming a defect and the conductor runs `crew fix` on `y`
- **THEN** the card is withdrawn, "held for a fix: <the note>", and a new card is raised when `y` reads proven again
