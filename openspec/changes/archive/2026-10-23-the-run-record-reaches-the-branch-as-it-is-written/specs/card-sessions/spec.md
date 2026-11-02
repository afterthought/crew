## MODIFIED Requirements

### Requirement: A session crew can't judge is kept
A rail read SHALL end no session whose row or card it cannot tell: none on a host that does not answer, which it names; no session for a card closed, and no batch card's, while the partition's run record cannot be read from its branch; and no session started less than two minutes before its host is checked, which a later read judges. A host that does not answer SHALL keep only the sessions on it: a card it posted or closed SHALL be judged from the branch like any other.

#### Scenario: The team's host is asleep
- **WHEN** chuck-herdr-alpha does not answer
- **THEN** the rail ends no session there, names chuck-herdr-alpha as not checked, and ends what it can judge elsewhere

#### Scenario: The record is read in part
- **WHEN** the partition's branch cannot be read
- **THEN** the rail ends no session for a card closed and no batch card's session, and still ends a session whose proposal's row is gone

#### Scenario: The host that closed a card is asleep
- **WHEN** a card the planner closed on macbook-pro is on `wldn/main` as closed, its session runs on mac-studio, and macbook-pro does not answer
- **THEN** the rail ends that session on mac-studio, its card read as closed

#### Scenario: A session just started
- **WHEN** the planner starts a session for a proposal opened after the rail's read began
- **THEN** that read leaves it running
