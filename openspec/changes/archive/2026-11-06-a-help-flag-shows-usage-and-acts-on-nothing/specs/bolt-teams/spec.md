## MODIFIED Requirements

### Requirement: A stage's agent says what it needs through crew
A stage's agent that cannot finish without something only someone else can give SHALL say so with `crew needs "<what it needs>"`, which ends its stage short. crew SHALL carry the agent's words to the conductor: in the answer of a wait running on the stage, otherwise in a tell marked as from that agent. crew SHALL refuse `crew needs` from anyone but the agent of a stage crew owes an end, and with no words. `crew needs --help` and `crew needs -h` SHALL ask for the command's usage and end no stage (crew-command, "A help flag shows a command's usage and acts on nothing").

#### Scenario: A coder pauses
- **WHEN** a code agent runs `crew needs "a decision on which table holds tenants"` while the conductor waits on its unit
- **THEN** the wait returns saying the stage stopped short, with those words, and the stage's end is recorded

#### Scenario: Nobody is waiting
- **WHEN** a stage's agent runs `crew needs` and no wait is running on its stage
- **THEN** the conductor is told the agent's words, marked as from that agent

#### Scenario: Not a stage's agent
- **WHEN** a conductor, or a slot's agent whose stage has already ended, runs `crew needs "x"`
- **THEN** crew refuses, saying the caller runs no stage crew is waiting on

#### Scenario: The agent reads the command's usage
- **WHEN** the agent of a stage crew owes an end runs `crew needs --help` to read how to use it
- **THEN** crew prints the usage, the stage stays begun and nothing is recorded or told
