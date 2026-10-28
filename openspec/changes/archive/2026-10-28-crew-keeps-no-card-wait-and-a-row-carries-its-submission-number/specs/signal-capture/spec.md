## MODIFIED Requirements

### Requirement: A tool's printed words are verified as a tool's
An excerpt that is a tool's output as the session received it, a crew command's own output among them, SHALL be graded `verified` and asserted by a tool, whether the command ran in the foreground or its output was read from a background task's file. The words SHALL match as printed, whitespace aside; words with any other change SHALL be refused.

#### Scenario: A crew command's own line
- **WHEN** a conductor quotes, as printed, a line `crew card read` printed in its shell
- **THEN** the signal is written `verified`, asserted by a tool

#### Scenario: A background task's output read from its file
- **WHEN** an agent reads a background task's output file and quotes two of its lines together
- **THEN** the signal is written `verified`, asserted by a tool

#### Scenario: A printed line copied with a capital it did not have
- **WHEN** a command printed "no session was started" and the agent quotes "No session was started"
- **THEN** the signal is refused

