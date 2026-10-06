# Spec Delta

## Purpose

Turns something an agent or the user notices into a capture and a signal that keep the words actually said, say how well crew could check them, and say where they came from, so that whoever judges the signal later is judging the source and not a paraphrase.

## ADDED Requirements

### Requirement: A signal quotes the words that show it
`crew signal <slug> "<what it asserts>"` run by an agent crew started SHALL require an excerpt, given with `--excerpt` or read from a file with `--excerpt-file`: words the agent's session received, from the user or from a tool. The signal SHALL hold the assertion, the excerpt as a quotation, and the excerpt's position. A signal SHALL never be written without an excerpt.

#### Scenario: An aside from the user
- **WHEN** a conductor records what the user said to it, quoting the user's words
- **THEN** the signal holds the conductor's one-sentence assertion and, beneath it, the user's words as they were typed, with the time they were received

#### Scenario: No excerpt
- **WHEN** an agent runs `crew signal` with no excerpt
- **THEN** it is refused, and the message says to quote the words that show the finding

### Requirement: crew grades how well it could check an excerpt
crew SHALL look for the excerpt, whitespace aside, in the transcript of the calling agent's Claude session, and SHALL record one grade on the capture: `verified` when it is in a record the session received, `found` when it is in the transcript in a record crew cannot classify, and `unverified`, with the reason, when crew could not read a transcript. No command SHALL refuse or change its behavior because of a grade; the grade SHALL be shown wherever the excerpt is shown.

#### Scenario: The user's words
- **WHEN** the excerpt is in a message the user typed to the agent
- **THEN** the capture's grade is `verified`, and it says the user asserted it

#### Scenario: A tool's output
- **WHEN** the excerpt is in the output of a command the agent ran
- **THEN** the capture's grade is `verified`, and it says a tool's output showed it

#### Scenario: The transcript's format has changed
- **WHEN** the transcript's lines are JSON, the excerpt is in one, and crew cannot tell that record's kind
- **THEN** the capture is written with the grade `found`

#### Scenario: No transcript
- **WHEN** herdr names no session for the agent, or its transcript cannot be found or parsed
- **THEN** the capture is written with the grade `unverified` and the reason

### Requirement: Only a paraphrase is refused
crew SHALL refuse a signal for its excerpt only when the transcript it reads is the live session's, its last record written within the last 15 minutes, and the excerpt is nowhere in it. When the transcript's last record is older, crew SHALL treat it as possibly another session's and write the capture `unverified`, with the reason. Words the agent itself wrote, and crew's own commands, SHALL NOT count as received.

#### Scenario: The agent's own summary
- **WHEN** an agent gives as its excerpt a sentence the user never typed and no tool printed
- **THEN** the signal is refused, nothing is written, and the message says the words are not in the session's transcript

#### Scenario: crew may be reading another session's transcript
- **WHEN** crew reads a transcript whose last record was written more than 15 minutes ago, such as the one before a `/clear`
- **THEN** the signal is written with the grade `unverified`, never refused, and the reason says how long the transcript has not been written

### Requirement: A capture is one record a session received
A capture made by an agent SHALL be the one transcript record that holds the excerpt. It SHALL name the capturing agent, the host, the Claude session, the record and its time, who asserted it, and the team, bolt and unit the agent was working in. A second signal whose excerpt is in the same record SHALL join that capture as its next signal, and recording the same signal again SHALL write nothing.

#### Scenario: Two findings in one message
- **WHEN** an agent records two signals quoting different sentences of one message from the user
- **THEN** one capture holds both, numbered 01 and 02

#### Scenario: The same signal twice
- **WHEN** an agent runs the same `crew signal` again
- **THEN** nothing is written, and it is told the signal's id

#### Scenario: Where it was noticed
- **WHEN** a stage agent in a unit's slot records a signal
- **THEN** the capture names its team, the bolt the team holds, and that unit

### Requirement: The raw record stays on the host, outside git
crew SHALL copy the transcript record that holds a checked excerpt to a file under `~/.local/state/crew/<label>/raw/` on the capturing host, and the capture SHALL point at it as `<host>:<path>`. Neither the raw record nor the transcript SHALL be written to any repository. Of the source, only the excerpt SHALL enter git.

#### Scenario: Reading the source again
- **WHEN** someone with access to the capturing host follows a capture's `raw` pointer
- **THEN** they read the whole record the excerpt was taken from, though Claude Code has since removed the transcript

#### Scenario: Nothing raw in git
- **WHEN** a capture is written
- **THEN** the commit holds the capture and its signal, and no file holding the rest of the record

### Requirement: An agent's signals live in the flywheel's state
A capture and its signals recorded through `crew signal` SHALL be written, in one commit, to `signals/<capture>/` on the flywheel's branch of its state repository, in the shape the blueprints' `signals/README.md` gives. Signals read from meetings and channels SHALL stay in the partition's first blueprints repo. A signal's id SHALL be unique across both, and crew SHALL look an id up on the flywheel's branch first and in the blueprints after.

#### Scenario: A conductor's finding
- **WHEN** swb-2's conductor records a signal
- **THEN** it is a commit on `wldn/main` of `WilldanGroup/crew-state`, and willdan-blueprints receives no commit

#### Scenario: A meeting's signal
- **WHEN** a command names a signal the daily pass wrote
- **THEN** crew finds it in willdan-blueprints' `signals/`

### Requirement: The user's own note is its own excerpt
`crew signal <slug> "<text>"` run by the user at a shell SHALL write a capture whose source is the user and one signal of kind `ask` unless another kind is given, whose assertion and excerpt are both the text. No transcript SHALL be read.

#### Scenario: A note at a shell
- **WHEN** the user types `crew signal check-templates "Templates should be checked for open security groups" --label wldn`
- **THEN** a capture and one signal hold that sentence as assertion and excerpt, asserted by the user

### Requirement: A signal is read back by its id
`crew signal show <id>` SHALL print, from any host, the signal's kind, who asserted it, its assertion and excerpt, the excerpt's grade, and its capture's provenance: who captured it, where, when, the session and the raw pointer.

#### Scenario: From another host
- **WHEN** `crew signal show <id>` runs on mac-studio for a signal captured on the box
- **THEN** it prints the signal and names the box, the session and the raw record's path there

### Requirement: What crew sends an agent is marked as crew's
A message `crew tell` sends SHALL begin `[crew tell from <sender>]`, and a message crew itself sends an agent (a greeting, a notice of a plan write) SHALL begin `[crew]`. A capture whose excerpt is in such a message SHALL say that agent, or crew, asserted it, and never the user.

#### Scenario: A conductor's message quoted by the planner
- **WHEN** the planner records a signal whose excerpt is in a message `swb-2-conductor` sent it with `crew tell`
- **THEN** the capture says `swb-2-conductor` asserted it

#### Scenario: The user uses crew tell
- **WHEN** the user at a shell runs `crew tell` and the recipient quotes it
- **THEN** the capture says the user asserted it

### Requirement: A capture is in the run record
Recording a signal SHALL leave a `capture` entry naming the signal and the commit that wrote it. A refused signal SHALL leave a refused entry that holds neither the assertion nor the excerpt.

#### Scenario: Tracing from a signal
- **WHEN** `crew trace signals/<id>` runs
- **THEN** its first line is the capture, with the capturing agent, host and session
