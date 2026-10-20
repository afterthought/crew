# Spec Delta

## ADDED Requirements

### Requirement: A refusal says how a tool's words reach the transcript
When `crew signal` refuses an agent's excerpt, its message SHALL say the words are not in the session's transcript, to quote them as received, and that a background task's output is in the transcript only once the agent has read the output file its task notification names, so to read it and record the signal again. Every brief that records findings SHALL say a refusal means either case.

#### Scenario: A background task's output not yet read
- **WHEN** an agent quotes a line printed by a command it ran in the background, and has not read the task's output file
- **THEN** the signal is refused, nothing is written, and the message names both the words as received and a background task's output that must be read first

#### Scenario: The same words once the output is read
- **WHEN** the agent reads that task's output file in its session and runs the same `crew signal` again
- **THEN** the signal is written with the grade `verified`, asserted by a tool, and the capture names the agent as who recorded it

#### Scenario: The agent's own words
- **WHEN** an agent gives as its excerpt a sentence the user never typed and no tool printed
- **THEN** the signal is refused with the same message

#### Scenario: What the briefs say
- **WHEN** a conductor's, ops's, main-level ops's, the design agent's, the planner's or the operator agent's brief is printed
- **THEN** it says a refusal means the words were reworded or are a background task's output not yet read

### Requirement: A tool's printed words are verified as a tool's
An excerpt that is a tool's output as the session received it, a crew command's own output among them, SHALL be graded `verified` and asserted by a tool, whether the command ran in the foreground or its output was read from a background task's file. The words SHALL match as printed, whitespace aside; words with any other change SHALL be refused.

#### Scenario: A crew command's own line
- **WHEN** a conductor quotes, as printed, a line `crew card wait` printed in its shell
- **THEN** the signal is written `verified`, asserted by a tool

#### Scenario: A background task's output read from its file
- **WHEN** an agent reads a background task's output file and quotes two of its lines together
- **THEN** the signal is written `verified`, asserted by a tool

#### Scenario: A printed line copied with a capital it did not have
- **WHEN** a command printed "no session was started" and the agent quotes "No session was started"
- **THEN** the signal is refused
