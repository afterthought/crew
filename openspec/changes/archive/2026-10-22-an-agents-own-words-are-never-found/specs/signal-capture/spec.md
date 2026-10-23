## ADDED Requirements

### Requirement: An agent's own words are never found
The excerpt check SHALL search neither the records the agent wrote nor Claude Code's copies of the messages it sent the model, whatever role a copy holds. Words that appear in the live session's transcript only there SHALL be refused as a paraphrase. Words the session received, from the user, a tool or crew, SHALL keep their grade, their asserter and their source record, the original's, though a copy of them is also in the transcript.

#### Scenario: The agent quotes its own earlier reply
- **WHEN** an agent's transcript holds a sentence the agent wrote in an earlier turn, in its own record and again in Claude Code's copy of the message sent to the model, and the agent gives that sentence as its excerpt
- **THEN** the excerpt is refused

#### Scenario: The agent quotes a command it ran
- **WHEN** the agent's excerpt is words that appear only in the input of a tool call it made, in its record and in Claude Code's copy of it
- **THEN** the excerpt is refused

#### Scenario: Words only in a copy
- **WHEN** the excerpt's words are in Claude Code's copy of a message it sent the model and in no other record of the transcript
- **THEN** the excerpt is refused

#### Scenario: The user's words with their copy beside them
- **WHEN** the user typed the words, and Claude Code's copy of that message follows the user's record
- **THEN** the excerpt is `verified`, asserted by the user, and its source is the user's record, with its line number and uuid

#### Scenario: A tool's output with its copy beside it
- **WHEN** a tool printed the words, and Claude Code's copy of the tool's result follows the result's record
- **THEN** the excerpt is `verified`, asserted by a tool, and its source is the result's record
