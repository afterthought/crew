# Spec Delta

## MODIFIED Requirements

### Requirement: A unit's intent is amended through crew
`crew unit amend <unit> "<new intent>"` SHALL replace the unit's intent in the plan. A unit that has a worktree SHALL also be marked amended, and once the write has landed its construct SHALL be handed to its team's host, where it SHALL start again in the name of whoever applied the amendment and the conductor SHALL be told from that host what started or why nothing did. The command, run directly or by a proposal's approval, SHALL answer once its write is made and the construct is handed to the host, and SHALL NOT wait on an agent's session coming up or its prompt landing. `crew unit wait <unit>` SHALL wait for a handed construct to start before it waits on the stage, and say why when it did not start; a stage of the unit SHALL be refused while a handed construct starts. A unit that has merged into its bolt or landed SHALL be refused. Run by the planner it SHALL be refused outside a proposal; the user at a shell runs it directly.

#### Scenario: A queued unit
- **WHEN** an amendment to a queued unit's intent is applied
- **THEN** the unit's intent is the new one, and nothing else changes

#### Scenario: A unit in code
- **WHEN** an amendment to a unit in code is applied
- **THEN** the unit's intent is the new one, the unit is marked amended, the command answers once its construct is handed to the team's host, and that host starts construct again and tells the conductor to wait for it

#### Scenario: A team taken down
- **WHEN** an amendment to a unit in verify is applied while its team is down
- **THEN** the unit is marked amended, the start is recorded refused, and the command says construct did not start because the team is down and tells the conductor so

#### Scenario: A wait on a handed construct
- **WHEN** the conductor runs `crew unit wait <unit>` while the construct an amendment handed is starting
- **THEN** the wait waits for it to start and then on its stage, within its timeout; and when it could not start, the wait says why

#### Scenario: A stage while a handed construct starts
- **WHEN** the conductor runs a stage of a unit whose handed construct is starting
- **THEN** crew refuses it, saying the construct is starting and that `crew unit wait <unit>` waits for it

#### Scenario: The unit's stage cannot be read
- **WHEN** an amendment to a unit with a worktree is applied while its team's host does not answer, so the unit's stage cannot be read
- **THEN** the amendment, or the approval holding it, is refused naming the host that did not answer, and nothing is written

#### Scenario: The construct cannot start
- **WHEN** an amendment to a unit in flight is applied once its stage has been read, and its handed construct cannot start because its team's host stops answering before the run reaches it or its team is down
- **THEN** the amendment stands, the unit's stage reads `amended`, the command says why construct did not start, and the conductor, when it can be told, is told why and to run construct once it can, with the card the amendment ended named

#### Scenario: A merged unit
- **WHEN** `crew unit amend` names a unit that has merged into its bolt
- **THEN** it is refused; what is needed is a fix or a new unit
