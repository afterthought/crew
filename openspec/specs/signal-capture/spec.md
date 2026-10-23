# signal-capture Specification

## Purpose
Turns something an agent, the user or a program notices into a capture and a signal that keep the words actually said, say how well crew could check them, and say where they came from, so that whoever judges the signal later is judging the source and not a paraphrase.

## Requirements

### Requirement: A program's capture lands on the flywheel's branch
A capture a program records, a kit's release adapter's or its deployer's, SHALL land through `crew signal land <capture-dir> --label L`, run on the host that ran the program, on the flywheel's branch of that partition, in one commit, with a `capture` entry naming each signal. crew SHALL refuse, naming the file, a folder holding anything but `capture.md` and its signals; a capture that names no `source`, no `captured_by`, no `event_date` or no raw record on the landing host; a capture that is not read or does not count the signals it holds, at least one; and a signal that does not name itself, its kind and who asserted it, says nothing, quotes no excerpt, or is larger than 8 KiB. A file the branch holds the same SHALL be passed over, one it holds otherwise SHALL refuse the landing, and a capture landed already SHALL write nothing and exit 0.

#### Scenario: A deployer's failed deploy
- **WHEN** swancloud's deployer runs `crew signal land` on mac-studio for its capture of a failed deploy, whose log is banked there
- **THEN** the capture and its signal are one commit on swancloud/main, recorded as a `capture` by swancloud-deployer

#### Scenario: The same capture again
- **WHEN** the deployer offers the same capture again
- **THEN** nothing is written, crew says it is already landed, and the command exits 0

#### Scenario: Raw material in the folder
- **WHEN** the folder holds the step's log beside the capture
- **THEN** the landing is refused, naming the log, and nothing is written

#### Scenario: Landed from another host
- **WHEN** the capture's raw record is on mac-studio and `crew signal land` runs on the box
- **THEN** the landing is refused, saying the capture lands from the host that banked it

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
