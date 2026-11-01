## MODIFIED Requirements

### Requirement: The planner starts the partition's reviewer
When a batch is due, crew SHALL tell the partition's planner once, and the planner SHALL start the reviewer: a main-level role, run fresh for each batch in its own tab of the main level's workspace, beside the planner, on the main level's host. Where the partition runs its reviewer as its kind, `crew review <label>` SHALL instead write an ask of the reviewer carrying the batch, as the reviewer's first message carries it today, open no tab and start no agent, and `crew review <label> --wait` SHALL refuse, saying the batch's delivery reaches the planner as an ask.

#### Scenario: A batch is due
- **WHEN** a conductor's wait finds a batch due in the wldn partition
- **THEN** wldn-planner is told once, and starts `wldn-reviewer` in the `wldn` workspace

#### Scenario: A reviewer that runs as its kind
- **WHEN** madswan runs its reviewer as its kind and the planner's run runs `crew review madswan`
- **THEN** an ask of the reviewer holds the batch's changes, how to read each and the file to write, no tab is opened, and no reviewer is started by crew

#### Scenario: Waiting on a reviewer that runs as its kind
- **WHEN** madswan runs its reviewer as its kind and `crew review madswan --wait` runs
- **THEN** it refuses, saying the batch's delivery reaches the planner as an ask, and waits on nothing

## ADDED Requirements

### Requirement: A reviewer's run hands its batch back
`crew review delivered [--label L]`, run in the reviewer's run once each batch its turn took has its summary written, SHALL do for each what the planner's wait did once the summary was written: record the batch, start its one reading session, and raise its one card in the planner's name; and SHALL write an ask of the planner naming `batch/<n>` with the line that adopts its card. A batch whose summary file is not written SHALL be refused by name, and the others delivered.

#### Scenario: A batch delivered
- **WHEN** madswan's reviewer run has written batch 21's summary and runs `crew review delivered`
- **THEN** batch 21 is recorded, its reading session started and its card raised in madswan-planner's name, and an ask of the planner names `batch/21` and the `get_request` line that adopts it

#### Scenario: A summary not written
- **WHEN** the reviewer's turn took batches 21 and 22, only 21's summary is written, and it runs `crew review delivered`
- **THEN** batch 21 is delivered, and batch 22 is refused, naming its file
