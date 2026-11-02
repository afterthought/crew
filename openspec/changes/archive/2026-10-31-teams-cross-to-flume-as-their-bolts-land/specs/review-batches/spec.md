## ADDED Requirements

### Requirement: A crossed team's unit is batched once its change has landed on its bolt
A unit of a crossed team's bolt SHALL become due for review when the runner's records read it merged, its change read archived on GitHub's bolt after a fetch, and SHALL be named in its batch at the commit of the bolt that holds it, its reading opening its archived folder. A note the user marks fix on such a unit SHALL reach its bolt as a fix place, by the planner's `crew fix`.

#### Scenario: Merged, then batched
- **WHEN** crossed crw-4's `a` lands on `bolt/x` at `9f1c2ab`, its change archived there
- **THEN** `a` counts toward the partition's next batch, named `a:crw-4@9f1c2ab`

#### Scenario: Constructed but not landed
- **WHEN** `b`'s construct has delivered and its place is in code
- **THEN** `b` is not yet due for review
