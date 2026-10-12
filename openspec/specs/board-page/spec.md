# board-page Specification

## Purpose
The board view of crew's page: one partition's flow, read by `crew board`, drawn as the flywheel mockup draws its phases view; and the page's deploys view, each environment's deploys as a timeline.

## Requirements

### Requirement: Operation draws each environment's deploys as records
The board view's Operation lane SHALL draw, under each environment's name, its deploys and the operations waiting on it as the board reads them, each deploy a record stamped with where it stands, and each with its marker; they SHALL be narrowed to a team as the teams on the environment's host.

#### Scenario: An offer waiting on the user
- **WHEN** a deploy of mac-studio is offered and its card is open
- **THEN** Operation shows it under mac-studio, stamped as waiting on the user's word, with its ✓ marker saying the card is open

### Requirement: The deploys view
The page SHALL have a deploys view, one switch from the board and the flow, kept in its address, that draws each environment as a timeline of its deploys over the record's window, oldest first, each with the commit it moved from and to, the user's word on it as its card's answer recorded it (approved by whom and when, waiting, or replaced unanswered), its steps, the suite's checks and its outcome, the bolts it carried with the proposals the lineage joins to each as its release notes, and the after-deploy steps of its commit with their doers and states; then the operations waiting on it. It SHALL be read from the run record alone, and the page SHALL stay one self-contained file.

#### Scenario: What a deploy carried
- **WHEN** the deploy of mac-studio carried bolt b, whose unit came from proposal 3
- **THEN** the deploys view lists b under it with proposal 3 and the first line of its case

#### Scenario: The sequence of words
- **WHEN** one deploy of mac-studio was approved and done and a newer offer waits
- **THEN** the deploys view shows the approved one above the waiting one, each with its word
