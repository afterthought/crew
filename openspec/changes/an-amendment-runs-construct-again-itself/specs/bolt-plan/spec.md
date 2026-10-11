# Spec Delta

## MODIFIED Requirements

### Requirement: A unit's intent is amended through crew
`crew unit amend <unit> "<new intent>"` SHALL replace the unit's intent in the plan. A unit that has a worktree SHALL also be marked amended, and once the plan's write has landed, the amendment itself SHALL run the unit's construct again on its team's host, in the name of whoever applied it, the user or the approver of the proposal holding it, and SHALL tell the unit's conductor what started or why nothing did. A unit that has merged into its bolt or landed SHALL be refused. Run by the planner it SHALL be refused outside a proposal; the user at a shell runs it directly.

#### Scenario: A queued unit
- **WHEN** an amendment to a queued unit's intent is applied
- **THEN** the unit's intent is the new one, and nothing else changes

#### Scenario: A unit in code
- **WHEN** an amendment to a unit in code is applied
- **THEN** the unit's intent is the new one, the unit is marked amended, a fresh construct agent starts in the unit's slot on its team's host within the same command, and its conductor is told that construct runs again and to wait for it

#### Scenario: The construct cannot start
- **WHEN** an amendment to a unit in flight is applied while its team's host does not answer, its team is not up, or the agent in its slot is still working
- **THEN** the amendment stands, the unit's stage reads `amended`, the command says why construct did not start, and the conductor, when it can be told, is told why and to run construct once it can, with the card the amendment ended named

#### Scenario: A merged unit
- **WHEN** `crew unit amend` names a unit that has merged into its bolt
- **THEN** it is refused; what is needed is a fix or a new unit
