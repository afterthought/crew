## MODIFIED Requirements

### Requirement: The landing card is posted once the bolt's verification is green
crew SHALL raise a bolt's landing card once every unit and chore of the bolt has merged, every unit's latest change has been in a batch whose card the user has answered, sluice's verdict at its head is green and no fix of it is in flight, none whose place stands that has neither merged nor been dropped, keyed `land/<bolt>`, as an `approve` of risk high, not reversible, because irreversible, its summary giving the counts, the batches, the verdict and when, how far main has moved, and, when its team holds another bolt that is proven too, the team's next planned bolt that a yes frees it for, or that nothing is planned for it; its face a text artifact "What lands: N units, M chores" naming each one a line, its rationale what follows, and, when sluice's submission at the head has a pull request on GitHub, that pull request as a `url` artifact and among its links; it SHALL ask only for the landing. When a merge makes the team's other bolt proven while the card waits on the user, the card SHALL be changed to say what a yes frees. A note naming a defect SHALL have the conductor start a fix on the bolt, which withdraws the card, and the card SHALL be raised again once the bolt reads proven again.

#### Scenario: Sluice's pull request
- **WHEN** sluice's submission at `y`'s head has pull request #23 on the kit's GitHub
- **THEN** the card links it, titled as sluice's pull request for the landing, on its face and in its details

#### Scenario: No pull request
- **WHEN** the kit's sluice opens no pull request for a submission
- **THEN** the card carries no link, and says nothing of one

#### Scenario: A green bolt
- **WHEN** every unit and chore of bolt `y` has merged, each unit's latest change has been in a batch the user has answered and sluice is green at `abc1234`
- **THEN** one card keyed `land/y` is open, an approve of risk high, naming the units and chores and the verdict

#### Scenario: A yes frees the team for its next bolt
- **WHEN** swc-1's card `land/y` waits on the user, and the last unit of swc-1's other bolt `z` merges with sluice green at its head, and `d` is the next planned bolt of swc-1's kit
- **THEN** `land/y` is changed in place, its summary saying a yes frees swc-1 for `d`

#### Scenario: A fix in flight holds the card
- **WHEN** every unit and chore of bolt `y` has merged, each unit's latest change has been in a batch the user has answered and sluice is green at its head, but `fix/y/gap`, started on `y`, has neither merged nor been dropped
- **THEN** no landing card is open for `y`, its rail row says it lands once `fix/y/gap` has merged or been dropped, and the card is raised once it has

#### Scenario: A landing row before the bolt reads proven
- **WHEN** every unit of bolt `y` has merged and one unit's latest change has not been in a batch
- **THEN** the rail shows `y`'s landing row, saying it lands once that unit has been in a batch, and the rail's read raises no card for it

#### Scenario: A landing row while a batch card waits on the user
- **WHEN** every unit of bolt `y` has merged, sluice is green at its head, and batch 7, whose card the user has not answered, holds a unit's latest change
- **THEN** the rail shows `y`'s landing row, saying it lands once you have answered batch 7, and the rail's read raises no card for it until the user has answered batch 7's card

#### Scenario: A defect noted on the card
- **WHEN** the user answers `land/y` with a note naming a defect and the conductor runs `crew fix` on `y`
- **THEN** the card is withdrawn, "held for a fix: <the note>", and a new card is raised when `y` reads proven again
