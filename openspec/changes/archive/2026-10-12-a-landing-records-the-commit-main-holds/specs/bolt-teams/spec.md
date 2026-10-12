## ADDED Requirements

### Requirement: A landing records the commit main holds
`crew bolt land` SHALL record, in its `bolt.land` entry of the run record, the kit the bolt landed on and the commit that kit's main holds on the team's host once the bolt has landed, and SHALL be refused when it can't read that commit.

#### Scenario: The landing's commit
- **WHEN** main-level ops has merged swb-1's bolt into switchboard-kit's main, pushed it, and runs `crew bolt land`
- **THEN** the landing's entry names switchboard-kit and the commit its main holds, and crew says the bolt has landed at that commit
