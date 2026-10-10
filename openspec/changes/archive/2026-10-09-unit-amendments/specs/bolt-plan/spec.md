# Spec Delta

## ADDED Requirements

### Requirement: A unit's intent is amended through crew
`crew unit amend <unit> "<new intent>"` SHALL replace the unit's intent in the plan. A unit that has a worktree SHALL also be marked amended, and its bolt's conductor told to run construct again. A unit that has merged into its bolt or landed SHALL be refused. Run by the planner it SHALL be refused outside a proposal; the user at a shell runs it directly.

#### Scenario: A queued unit
- **WHEN** an amendment to a queued unit's intent is applied
- **THEN** the unit's intent is the new one, and nothing else changes

#### Scenario: A unit in code
- **WHEN** an amendment to a unit in code is applied
- **THEN** the unit's intent is the new one, the unit is marked amended, and its conductor is told to run construct again

#### Scenario: A merged unit
- **WHEN** `crew unit amend` names a unit that has merged into its bolt
- **THEN** it is refused; what is needed is a fix or a new unit

## MODIFIED Requirements

### Requirement: A unit's stage is read from the kits
crew SHALL derive each unit's stage from its kit on the team's host. The first rule that holds is the unit's stage:

- `landed`: main holds the unit's OpenSpec change, open or archived;
- `merged`: `bolt/<bolt>` holds it;
- `amended`: the plan marks the unit amended, and construct has not been run again;
- `construct`: construct has been run again on an amended unit, and has not yet committed;
- `review`: an amended unit's construct has committed, and the user has not approved it again;
- `verify`: every task is ticked;
- `code`: some task is ticked;
- `approved`: the change's planning is complete, and a review has been approved since the bolt;
- `review`: the change's planning is complete, with no approval;
- `construct`: the unit's worktree exists;
- `ready` or `waiting`: neither, depending on its `After` units;
- `queued`: the unit has no bolt.

#### Scenario: A squashed merge
- **WHEN** a unit was merged into its bolt with `wt merge`, and its worktree and branch were removed
- **THEN** its stage is still `merged`, read from the change folder on `bolt/<bolt>`

#### Scenario: Nothing kept by hand
- **WHEN** a coder ticks the last task of a unit's change
- **THEN** `crew bolts` shows the unit in `verify`, and no file was edited to say so

#### Scenario: An amended unit with ticked tasks
- **WHEN** a unit in code is marked amended and construct has been run again and has committed
- **THEN** its stage is `review`, though some of its tasks are ticked

### Requirement: The user's approval is a commit
`crew unit approve <unit>` SHALL record the review as an empty commit on `unit/<unit>` with a `Reviewed-by:` trailer naming the user. It SHALL refuse a unit whose change's planning is not complete. Approving a unit that is marked amended SHALL also clear the mark in the plan, after which the unit's stage is read from its tasks again.

#### Scenario: The approval travels with the work
- **WHEN** an approved unit is rebased onto a newer bolt tip
- **THEN** its approval commit comes with it, and its stage stays `approved`

#### Scenario: An amended unit is approved again
- **WHEN** the user approves an amended unit whose rewritten change is in review
- **THEN** a new approval commit is on `unit/<unit>`, the plan no longer marks the unit amended, and its stage is `code` if any task is ticked, else `approved`

#### Scenario: Approving before construct has run again
- **WHEN** `crew unit approve` names a unit whose stage is `amended`
- **THEN** it is refused, saying construct has not been run again
