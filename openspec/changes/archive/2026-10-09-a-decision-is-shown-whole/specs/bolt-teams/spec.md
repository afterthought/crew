## MODIFIED Requirements

### Requirement: The user reviews every unit before it is coded
When a unit's construct stage finishes, the conductor SHALL tell the user the unit is ready for review: which unit, the folder its change is in, and in two or three plain sentences what it would make true. It SHALL ask for the answer in words and stop. It SHALL NOT open the change in plannotator or any other viewer, and SHALL NOT recite a command for the user to answer with: the user opens the whole change when they choose to read it. Code SHALL wait for `crew unit approve`, which the user runs or asks an agent to run. What the user wants changed SHALL go back to a fresh construct stage.

#### Scenario: A unit is ready for review
- **WHEN** a unit's construct agent has committed its change
- **THEN** the conductor tells the user the unit is ready, where its change is and what it would make true, asks them to approve it or say what to change, and opens nothing

#### Scenario: The user approves in words
- **WHEN** the user tells the conductor to approve a unit in review
- **THEN** the conductor runs `crew unit approve` for it, and code may start

#### Scenario: Changes asked for
- **WHEN** the user asks for a change to a unit in review
- **THEN** the conductor runs construct again with the user's words, and the unit returns to review
