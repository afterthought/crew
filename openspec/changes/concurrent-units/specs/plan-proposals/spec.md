# Spec Delta

## MODIFIED Requirements

### Requirement: An amendment is read as before and after
For a `unit amend` command, `crew plan proposed <n>` SHALL show the unit's intent as it stands and as it would be, the unit's bolt, team and stage, and what approval sets in motion: for a unit with a worktree, that its conductor runs construct again and the unit goes on from its tasks once that construct has committed, its revised change due for the next batch, with no approval asked.

#### Scenario: An amendment to a unit in code
- **WHEN** proposal N amends the intent of a unit in code in the bolt swb-2 holds
- **THEN** its page shows both intents, that the unit is in code under swb-2, that swb-2's conductor has or has not agreed, and that on approval the unit goes back to construct and then on from its tasks, its revised change in the next batch
