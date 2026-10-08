## MODIFIED Requirements

### Requirement: A stage's end is recorded when crew sees it
Each `stage.start` entry SHALL be followed by exactly one `stage.end` entry, carrying the stage crew then reads from the kit, the unit's tasks done and total, the head of the unit's or fix's branch, how the stage ended in `Ended`, and, when it delivered, its deliverable as an object in `Delivered`. `Ended` SHALL be `delivered` when the deliverable exists and the agent has stopped working, `short` when the agent said what it needs through crew, and `stopped` when crew ended the stage's agent before either. A wait SHALL record a delivered end when it sees it; a stop-short SHALL be recorded by the command the agent ran; when no wait recorded a delivered end, the next crew command that reads the team SHALL record it, marked as observed late. A stage whose agent has only gone quiet SHALL have no end recorded. Ops's proof SHALL be recorded the same way, on `stage/<bolt>/proof`.

#### Scenario: The conductor waits
- **WHEN** a conductor runs `crew unit wait <unit>` and the construct agent commits its change and stops working
- **THEN** a `stage.end` entry is written with the stage `review`, `Ended: delivered`, the unit branch's head, and `Delivered: unit/<unit>@<head>`

#### Scenario: A verify's report
- **WHEN** a verify stage ends at its report
- **THEN** its `stage.end` entry has `Delivered: report/<the report's file name>`

#### Scenario: Nobody waited
- **WHEN** a stage's agent has delivered and stopped working, no wait ran, and `crew status <team>` is run later
- **THEN** a `stage.end` entry is written then, marked observed late, and a second read writes no second entry

#### Scenario: Quiet with nothing delivered
- **WHEN** a code agent has stopped working with tasks still open, and `crew status <team>` is run
- **THEN** no `stage.end` entry is written

#### Scenario: A stop-short
- **WHEN** a stage's agent runs `crew needs "<what it needs>"`
- **THEN** a `stage.end` entry is written with `Ended: short` and no `Delivered`, and the agent's words appear nowhere in the run record

#### Scenario: A stage run again before it ended
- **WHEN** the conductor runs a unit's code stage again while the previous code stage has neither delivered nor stopped short
- **THEN** the previous stage's `stage.end` is written with `Ended: stopped` before the new stage's start
