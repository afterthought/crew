## ADDED Requirements

### Requirement: A row carrying another bolt's work is held
A bolt whose kit's read says it carries another bolt's work that main lacks SHALL be held on its landings row with no box, as a conflict holds one, whatever else holds it, and not marked as taking main first. The row SHALL name each bolt and its landings, and say it lands once main holds that work. No landing card SHALL be raised for it. A bolt whose carried work can't be read SHALL be held the same way, saying why.

#### Scenario: A bolt built on another bolt's landing
- **WHEN** bolt `y`'s branch holds bolt `breadboard-shows-a-deleted-app-as-deleting`'s landing `f5e67f35`, which main lacks
- **THEN** `y`'s row has no box and says "held: carries bolt breadboard-shows-a-deleted-app-as-deleting's work, its landing f5e67f3, which main lacks", and no landing card is raised for it

#### Scenario: Held with a take-main fix in flight
- **WHEN** `y` carries another bolt's work and a take-main fix place is in flight on it
- **THEN** `y`'s row is held for the work it carries, not marked as taking main first

#### Scenario: What it carries can't be read
- **WHEN** the kit's read could not list another bolt's own commits beyond main
- **THEN** `y`'s row has no box and says crew can't tell whether it carries another bolt's work, with why
