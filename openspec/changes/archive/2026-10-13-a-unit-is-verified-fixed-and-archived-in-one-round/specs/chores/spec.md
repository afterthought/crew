## MODIFIED Requirements

### Requirement: A chore's stage starts only when it may
crew SHALL refuse a chore's code while an `After` has nothing committed to build on, any stage of a merged or landed chore, verify before its place holds a commit of its own beyond the bolt, and merge before its verify has delivered, while a commit of its own lacks the `Chore: <name>` trailer, naming that commit, or while an `After` has not merged. A chore has no construct and no settle: `crew unit run` naming a chore SHALL be refused, naming its kind.

#### Scenario: Construct on a chore
- **WHEN** someone runs `crew unit run bump-biome construct`
- **THEN** it is refused: bump-biome is a chore, which has no construct

#### Scenario: A commit without the trailer
- **WHEN** the conductor runs `crew chore run bump-biome merge` and one commit beyond the bolt lacks `Chore: bump-biome`
- **THEN** the merge is refused, naming that commit

#### Scenario: A merge after the fix round
- **WHEN** the chore's verify delivered its report, and code ran once more on it, fixing what the report marked fix
- **THEN** `crew chore run bump-biome merge` is not refused for want of a verify

### Requirement: A chore is never constructed or reviewed
No batch SHALL hold a chore, the planner SHALL never be told a batch is due for one, and a bolt's landing SHALL never wait on a batch for one. A chore's verify report SHALL be no rail row and have no card, as a unit's has none: its findings marked fix are fixed in one round (`teams.17`).

#### Scenario: A bolt of chores
- **WHEN** every chore of a bolt has merged and the bolt holds no unit
- **THEN** its landing row is offered with no batch due
