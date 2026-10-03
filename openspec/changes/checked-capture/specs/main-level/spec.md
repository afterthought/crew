# Spec Delta

## MODIFIED Requirements

### Requirement: Signals reach the plan only through a route
A signal recorded through crew SHALL live on the flywheel's branch of its state repository, and a signal read from a meeting or a channel in the partition's first blueprints repo, both in the signals model that repo's `signals/README.md` gives. A bolt's agents SHALL record a finding outside their bolt as a signal with `crew signal`, quoting the words that show it. A signal SHALL become work only through a `route` move written by `crew unit add --signal`.

#### Scenario: A finding from a bolt
- **WHEN** ops on swb-1 finds a defect in a shared service the bolt does not own
- **THEN** it records a signal on wldn's branch of the state repository, quoting the output that shows the defect, and the planner decides whether to route it
