## ADDED Requirements

### Requirement: A conductor carries a stage's design questions together
When a stage stops short on design questions, its conductor SHALL send the questions that are linked (from one stage, or from units of its bolt about the same thing) to the design agent in one message, in the words of whoever asked. When the design agent asks for a reading before it rules, the conductor SHALL get it from its team's ops and send it back with the questions. The conductor SHALL bring the answer back to the stage verbatim, with the documentation or reading it names. When the planner says it holds corrections to a unit whose construct is running, the conductor SHALL tell the planner when that construct settles.

#### Scenario: A construct stops with several questions
- **WHEN** a unit's construct stops short, naming three design questions about the same service
- **THEN** the conductor sends all three to the design agent in one message, and the construct gets the answer back verbatim, with the reading it names

#### Scenario: The design agent needs a reading
- **WHEN** the design agent answers that it needs the live policy before it can rule
- **THEN** the conductor asks its team's ops for that reading, and sends it to the design agent with the questions it was for

#### Scenario: The planner is holding corrections
- **WHEN** the planner has said it holds corrections to a unit, and that unit's construct settles
- **THEN** the conductor tells the planner, which then proposes the one amendment
