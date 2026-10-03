# Spec Delta

## MODIFIED Requirements

### Requirement: The planner plans across bolts
The planner SHALL be the only agent that proposes bolts, the placing of units into bolts, and their splitting, ordering or moving between bolts, and SHALL change the plan only through a proposal the user approves. It SHALL route signals to work. A change to an active bolt SHALL be agreed by that bolt's conductor, with `crew plan agree`, before the proposal can be approved. The planner SHALL NOT start units or drive a team.

#### Scenario: A finding mid-bolt
- **WHEN** swb-1's conductor reports that a unit needs work outside the bolt's goal
- **THEN** the planner proposes queuing that work or adding it to another bolt, and swb-1's bolt keeps its goal

#### Scenario: New work beside a bolt in flight
- **WHEN** the planner judges that new work belongs in the bolt swb-2 holds
- **THEN** it proposes the unit for that bolt, swb-2's conductor agrees or says why not, and the unit is in the bolt only once the user has approved the proposal
