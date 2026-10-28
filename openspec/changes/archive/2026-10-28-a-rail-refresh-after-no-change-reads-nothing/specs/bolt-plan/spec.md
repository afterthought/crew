## MODIFIED Requirements

### Requirement: A command reads each kit and the plan once
A crew command SHALL read each kit once and fetch the state branch once on each host it runs on, however many steps it has. A step that makes or removes a worktree in a kit SHALL leave the next step to read that kit again. A plan write SHALL start from the tip the command holds and fetch again only when its push is refused. A wait SHALL read afresh each time it looks. The host's follower and `crew events --follow` SHALL check at each look whether what they read has moved, and read again only what has.

#### Scenario: Status with three units in flight
- **WHEN** `crew status <team>` runs for a team with three units in flight
- **THEN** the team's host reads the kit once and fetches the state branch once, and `openspec` is not started

#### Scenario: Running a stage
- **WHEN** `crew unit run <unit> construct` frees finished slots, tidies worktrees, checks the stage and makes the unit's place
- **THEN** the team's host fetches the state branch once and reads the kit once before the place is made

#### Scenario: A write after the plan moved
- **WHEN** another agent's write lands on the state branch after a command fetched it, and the command then writes
- **THEN** the command's push is refused, it fetches the new tip and applies its change there, as any write does

#### Scenario: A wait sees what changes while it waits
- **WHEN** `crew unit wait <unit>` is waiting and the coder ticks the last task
- **THEN** the wait's next look reads the new head and returns with the delivered end

#### Scenario: Nothing is left behind
- **WHEN** a command ends, whether it succeeded or was refused
- **THEN** what it kept for its steps is gone, and the next command reads afresh

#### Scenario: A follower's look after nothing moved
- **WHEN** the host's follower looks again and nothing it read has moved
- **THEN** it reads no kit and fetches no branch at that look
