# Spec Delta

## ADDED Requirements

### Requirement: A conductor carries its bolt for sluice
A team's conductor and ops that crew starts while the team holds a bolt SHALL have `SLUICE_BRANCH` in its environment set to the bolt's branch, and its herdr pane SHALL carry the token `sluice_branch` with the same value, reported from the source `crew` with no time to live. The token SHALL be reported again when herdr resumes the agent, and cleared when the team's bolt lands or is dropped. A unit slot SHALL carry neither.

#### Scenario: A conductor starts on a bolt
- **WHEN** crew starts `swb-1-conductor` in `/workspace/switchboard-kit/main` while team swb-1 holds bolt `b7`
- **THEN** its environment holds `SLUICE_BRANCH=bolt/b7`, and `herdr pane list` shows `"sluice_branch": "bolt/b7"` in its pane's `tokens`

#### Scenario: herdr restarts
- **WHEN** herdr's server restarts and resumes `swb-1-conductor` without crew's environment
- **THEN** its pane's `tokens` hold `"sluice_branch": "bolt/b7"` again

#### Scenario: The bolt lands
- **WHEN** `crew bolt land b7` closes swb-1's bolt
- **THEN** the conductor's and ops's panes carry no `sluice_branch` token

#### Scenario: A unit
- **WHEN** crew starts `swb-1-unit-2` in its own worktree
- **THEN** its environment has no `SLUICE_BRANCH` and its pane no `sluice_branch` token
