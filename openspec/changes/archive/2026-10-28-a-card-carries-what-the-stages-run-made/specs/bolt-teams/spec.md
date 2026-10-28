# Spec Delta

## ADDED Requirements

### Requirement: A stage's made things are read from its place
Until crew runs stages through Flume, what a stage's run recorded as made SHALL be read from `made.jsonl` in the place's own git directory, one line per thing, as the run wrote it. A place with no such file SHALL have made nothing, and its cards SHALL carry no link of its.

#### Scenario: A place that recorded two things
- **WHEN** unit `a`'s place's git directory holds `made.jsonl` with two lines
- **THEN** crew reads both lines, in order, byte for byte

#### Scenario: A place that recorded nothing
- **WHEN** unit `a`'s place has no `made.jsonl`
- **THEN** crew reads nothing made for `a`, and refuses nothing

#### Scenario: The file can't be read
- **WHEN** `made.jsonl` in `a`'s place exists and can't be read
- **THEN** the wait says so on standard error, naming the file, keeps what it copied before, and goes on waiting

### Requirement: The conductor's wait keeps a copy of what each stage made
The conductor's wait SHALL read the place's `made.jsonl` at each look and at the stage's end, and SHALL keep each line it has not kept before, as written, in a copy on the team's host under the unit and the stage that was running when it first saw the line, so the lines outlive the place's tidy. When it keeps a new line for a unit in a batch whose card is open, it SHALL hand that card's change to the partition's main machine. The copies SHALL go when the unit's bolt lands or is dropped.

#### Scenario: A line written while the code stage runs
- **WHEN** the conductor's `crew unit wait a` runs over `a`'s code stage and the code agent appends a line to `made.jsonl`
- **THEN** the wait keeps that line under `a`'s code stage, once, however many looks see it

#### Scenario: A line seen at a later stage
- **WHEN** a line was in `made.jsonl` before the verify stage started and no wait saw it during code
- **THEN** the wait over verify keeps it under the verify stage, the stage that was running when crew first saw it

#### Scenario: The place is tidied
- **WHEN** unit `a` merges and its place is removed
- **THEN** the copy of `a`'s lines is still on the team's host, and batch 7's card still carries them

#### Scenario: The bolt lands
- **WHEN** `crew bolt land y` closes bolt `y`, which holds unit `a`
- **THEN** the copy of `a`'s lines is gone from the team's host
