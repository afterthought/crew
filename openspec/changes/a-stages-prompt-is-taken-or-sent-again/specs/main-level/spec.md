## ADDED Requirements

### Requirement: A greeting is taken or sent again
A greeting crew sends, to a conductor or to any agent crew starts outside a team, SHALL be sent only once the agent is ready for input, and crew SHALL then read the agent's transcript to see that Claude received it within a short time. When it does not, and the agent sits idle or done, crew SHALL clear what was left typed in the agent's input and send the greeting once more. Exactly one greeting SHALL reach the agent per start.

#### Scenario: A greeting taken at once
- **WHEN** `crew up swb-1` starts the conductor and its transcript shows the greeting received moments after crew sent it
- **THEN** crew says swb-1-conductor was greeted, records one greeting, and sent it once

#### Scenario: A greeting left typed
- **WHEN** crew greets wldn-planner and the planner's transcript shows nothing received within the time, while it sits idle
- **THEN** crew clears the planner's input, sends the greeting once more, and says it was greeted once the transcript shows it

### Requirement: A greeting not taken is reported, with nothing left typed
When the second sending of a greeting is not taken either, crew SHALL leave nothing typed, record no greeting, and say the agent was not greeted, with the `crew tell` that would greet it. When crew cannot read whether the greeting was taken, it SHALL send nothing more and say what it could not read. A greeting that is not delivered SHALL fail nothing else the command does.

#### Scenario: A greeting never taken
- **WHEN** neither sending of wldn-design's greeting shows in its transcript within the time
- **THEN** its input is cleared, crew says wldn-design was not greeted and gives the `crew tell wldn-design "<greeting>"` that would greet it, no greeting is recorded, and `crew main up` goes on with its other agents
