# Spec Delta

## MODIFIED Requirements

### Requirement: An amendment is read as before and after
For a `unit amend` command, `crew plan proposed <n>` SHALL show the unit's intent as it stands and as it would be, the unit's bolt, team and stage, and what approval sets in motion: for a unit with a worktree, that construct runs again at once in its team's slot and the unit returns to the user's review.

#### Scenario: An amendment to a unit in code
- **WHEN** proposal N amends the intent of a unit in code in the bolt swb-2 holds
- **THEN** its page shows both intents, that the unit is in code under swb-2, that swb-2's conductor has or has not agreed, and that on approval construct runs again at once in swb-2's slot and the unit returns to review
